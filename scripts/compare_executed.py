import json, tempfile, difflib
from pathlib import Path
import nbformat
from cap.paths import get_paths
from cap.provenance import notebook_source_sha256

paths = get_paths()
exec_dir = paths.run_root / "executed_notebooks"

def hash_nb(nb):
    with tempfile.NamedTemporaryFile(suffix=".ipynb", delete=False) as t:
        name = t.name
    nbformat.write(nb, name)
    try:
        return notebook_source_sha256(Path(name))
    finally:
        Path(name).unlink(missing_ok=True)

stages = ["00_cohort", "01_preprocessing", "02_cell_annotation",
          "03b_meta_programmes", "03d_normal_tissue_protein"]

for s in stages:
    p = json.loads((paths.stage_dir(s) / "run_provenance.json").read_text(encoding="utf-8"))
    rel = p["notebook"]["path"]
    recorded = p["notebook"]["source_sha256"]
    print(f"\n===== {s} ({rel})")
    ex = exec_dir / Path(rel).name
    if not ex.is_file():
        print("  no executed notebook found at", ex); continue
    nb_exec = nbformat.read(ex, as_version=4)
    nb_exec.cells = [c for c in nb_exec.cells
                     if "injected-parameters" not in c.metadata.get("tags", [])]
    nb_work = nbformat.read(paths.root / rel, as_version=4)
    print("  executed (minus injected cell) hash == recorded:", hash_nb(nb_exec) == recorded)
    print("  working copy hash == recorded:", hash_nb(nb_work) == recorded)
    ce = [c.source for c in nb_exec.cells if c.cell_type == "code"]
    cw = [c.source for c in nb_work.cells if c.cell_type == "code"]
    print(f"  code cells: executed={len(ce)} working={len(cw)}")
    if ce == cw:
        print("  code cells identical, same order")
        continue
    same_set = sorted(ce) == sorted(cw)
    print("  same cells, different order:", same_set)
    diff = list(difflib.unified_diff(
        "\n".join(f"#CELL {i}\n{x}" for i, x in enumerate(ce)).splitlines(),
        "\n".join(f"#CELL {i}\n{x}" for i, x in enumerate(cw)).splitlines(),
        "executed", "working", lineterm="", n=1))
    for line in diff[:80]:
        print("  ", line)
    if len(diff) > 80:
        print("   ... truncated,", len(diff) - 80, "more lines")
