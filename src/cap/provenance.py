"""Checksum verification and reproducible run metadata for CAP."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cap.paths import ProjectPaths


def sha256_file(path: Path, block_size: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(block_size), b""):
            digest.update(block)
    return digest.hexdigest()


def notebook_source_sha256(path: Path) -> str:
    """Hash ordered notebook cell sources, excluding outputs and execution counts."""
    with Path(path).open(encoding="utf-8") as handle:
        notebook = json.load(handle)

    cells = []
    for cell in notebook.get("cells", []):
        metadata = cell.get("metadata", {}) or {}
        cell_record: dict[str, Any] = {
            "cell_type": cell.get("cell_type"),
            "source": cell.get("source", ""),
        }
        if "tags" in metadata:
            cell_record["tags"] = metadata["tags"]
        if "attachments" in cell:
            cell_record["attachments"] = cell["attachments"]
        cells.append(cell_record)

    payload = {
        "nbformat": notebook.get("nbformat"),
        "nbformat_minor": notebook.get("nbformat_minor"),
        "kernelspec": notebook.get("metadata", {}).get("kernelspec", {}),
        "cells": cells,
    }
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _python_package_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for distribution in importlib.metadata.distributions():
        name = distribution.metadata.get("Name")
        if name:
            versions[name] = distribution.version
    return dict(sorted(versions.items(), key=lambda item: item[0].casefold()))


def _r_environment_versions() -> dict[str, Any]:
    executable = shutil.which("Rscript")
    if executable is None and os.environ.get("R_HOME"):
        r_home = Path(os.environ["R_HOME"])
        candidates = (
            r_home / "bin" / "Rscript.exe",
            r_home / "bin" / "x64" / "Rscript.exe",
            r_home / "bin" / "Rscript",
        )
        executable = next((str(path) for path in candidates if path.is_file()), None)
    if executable is None:
        return {"available": False}

    expression = (
        'cat(R.version.string, "\\n"); '
        'packages <- installed.packages()[, c("Package", "Version")]; '
        'write.table(packages, sep="\\t", quote=FALSE, '
        'row.names=FALSE, col.names=FALSE)'
    )
    try:
        output = subprocess.check_output(
            [executable, "--vanilla", "-e", expression],
            text=True,
            stderr=subprocess.STDOUT,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        return {"available": True, "collection_error": str(error)}

    lines = [line for line in output.splitlines() if line.strip()]
    package_versions: dict[str, str] = {}
    for line in lines[1:]:
        fields = line.split("\t", maxsplit=1)
        if len(fields) == 2:
            package_versions[fields[0]] = fields[1]
    return {
        "available": True,
        "version": lines[0] if lines else None,
        "packages": dict(sorted(package_versions.items())),
    }


def validate_frozen_inputs(paths: ProjectPaths) -> None:
    manifest_path = paths.manifest_dir / "frozen_inputs.json"
    with manifest_path.open(encoding="utf-8") as handle:
        manifest = json.load(handle)

    mismatches: list[str] = []
    for filename, record in manifest.items():
        file_path = paths.frozen_dir / filename
        paths.require_file(file_path, f"frozen input {filename}")
        observed = sha256_file(file_path)
        expected = record["sha256"]
        if observed != expected:
            mismatches.append(f"{filename}: expected {expected}, observed {observed}")

    if mismatches:
        raise ValueError("Frozen input checksum mismatch:\n" + "\n".join(mismatches))


def write_run_provenance(
    paths: ProjectPaths,
    stage_dir: Path,
    *,
    notebook_path: Path | None = None,
    input_checksums: Mapping[str, str] | None = None,
) -> Path:
    """Write run metadata; explicit notebook/input arguments enrich new call sites."""
    root = paths.root.resolve()
    git_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True
    ).strip()
    git_status = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        text=True,
    ).splitlines()

    notebook_record: dict[str, str] | None = None
    if notebook_path is not None:
        notebook_path = Path(notebook_path).resolve()
        if not notebook_path.is_file():
            raise FileNotFoundError(f"Notebook source not found: {notebook_path}")
        try:
            relative_notebook = notebook_path.relative_to(root).as_posix()
        except ValueError as error:
            raise ValueError("Notebook source must be inside the repository root.") from error
        notebook_record = {
            "path": relative_notebook,
            "file_sha256_at_provenance_write": sha256_file(notebook_path),
            "source_sha256": notebook_source_sha256(notebook_path),
            "source_hash_scope": (
                "ordered cell types and source text, cell tags, attachments, and kernelspec; "
                "excludes outputs and execution counts"
            ),
        }

    checksum_map = dict(sorted((input_checksums or {}).items()))
    checksum_path = Path(stage_dir) / "input_checksums.json"
    checksum_file_sha256 = None
    if checksum_path.is_file():
        with checksum_path.open(encoding="utf-8") as handle:
            saved_checksums = json.load(handle)
        if input_checksums is not None and saved_checksums != checksum_map:
            raise ValueError("input_checksums.json does not match the supplied input checksums.")
        checksum_file_sha256 = sha256_file(checksum_path)

    missing_fields = []
    if notebook_path is None:
        missing_fields.append("notebook")
    if input_checksums is None:
        missing_fields.append("input_checksums")

    payload = {
        "run_id": paths.run_id,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "repository_root": str(paths.root),
        "data_root": str(paths.data_root),
        "git_commit": git_commit,
        "git_dirty": bool(git_status),
        "git_status_porcelain": git_status,
        "notebook": notebook_record,
        "input_checksums": checksum_map,
        "input_checksums_file_sha256": checksum_file_sha256,
        "provenance_completeness": {
            "complete": not missing_fields,
            "missing_fields": missing_fields,
        },
        "versions": {
            "python": sys.version,
            "platform": platform.platform(),
            "python_packages": _python_package_versions(),
            "R": _r_environment_versions(),
        },
    }
    destination = Path(stage_dir) / "run_provenance.json"
    destination.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return destination
