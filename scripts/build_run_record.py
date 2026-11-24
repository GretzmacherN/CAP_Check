import csv, hashlib, json, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path
from cap.paths import get_paths

paths = get_paths()
root, run_root = paths.root, paths.run_root
record = root / "run_records" / paths.run_id
if record.exists():
    raise FileExistsError(f"Record already exists: {record}")
record.mkdir(parents=True)

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                      capture_output=True, text=True, check=True).stdout.strip()
stages = sorted(d for d in run_root.iterdir() if d.is_dir() and d.name[:2].isdigit())

fields = ["stage", "has_provenance", "run_id_matches", "git_commit", "git_dirty",
          "complete", "notebook", "notebook_source_sha256", "n_dirty_entries"]
rows = []
for d in stages:
    pf = d / "run_provenance.json"
    if not pf.is_file():
        rows.append({"stage": d.name, "has_provenance": False}); continue
    p = json.loads(pf.read_text(encoding="utf-8"))
    nb = p.get("notebook") or {}
    rows.append({
        "stage": d.name, "has_provenance": True,
        "run_id_matches": p["run_id"] == paths.run_id,
        "git_commit": p["git_commit"], "git_dirty": p["git_dirty"],
        "complete": p["provenance_completeness"]["complete"],
        "notebook": nb.get("path", ""),
        "notebook_source_sha256": nb.get("source_sha256", ""),
        "n_dirty_entries": len(p["git_status_porcelain"]),
    })
    target = record / d.name
    target.mkdir()
    for name in ("run_provenance.json", "input_checksums.json"):
        if (d / name).is_file():
            shutil.copy2(d / name, target / name)

with (record / "stage_summary.csv").open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)

files = []
for f in sorted(run_root.rglob("*")):
    if f.is_file():
        files.append({"path": f.relative_to(run_root).as_posix(),
                      "bytes": f.stat().st_size, "sha256": sha256(f)})
(record / "output_manifest.json").write_text(
    json.dumps(files, indent=2) + "\n", encoding="utf-8")

(record / "run_record.json").write_text(json.dumps({
    "run_id": paths.run_id,
    "created_utc": datetime.now(timezone.utc).isoformat(),
    "record_built_on_commit": head,
    "n_stages": len(stages),
    "n_files_hashed": len(files),
}, indent=2) + "\n", encoding="utf-8")

print(f"Record written to {record}")
for r in rows:
    print(r)
