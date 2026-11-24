import json
from pathlib import Path
import nbformat
from cap.paths import get_paths

paths = get_paths()
stages = ["00_cohort", "02_cell_annotation", "03b_meta_programmes", "03d_normal_tissue_protein"]

for s in stages:
    p = json.loads((paths.stage_dir(s) / "run_provenance.json").read_text(encoding="utf-8"))
    rel = p["notebook"]["path"]
    nb = nbformat.read(paths.root / rel, as_version=4)
    code = [(i, c) for i, c in enumerate(nb.cells) if c.cell_type == "code"]
    counts = [(i, c.get("execution_count")) for i, c in code]
    ran = [(i, n) for i, n in counts if n is not None]
    unrun = [i for i, n in counts if n is None]
    seq = [n for _, n in ran]
    print(f"\n===== {s} ({rel})")
    print(f"  code cells: {len(code)} | executed: {len(ran)} | never executed: {len(unrun)}")
    print(f"  cells never executed (notebook index): {unrun[:40]}")
    print(f"  execution counts follow cell order: {seq == sorted(seq)}")
    if seq != sorted(seq):
        breaks = [(i, n) for (i, n), (_, m) in zip(ran, ran[1:]) if m < n]
        print(f"  out-of-order at (index, count): {breaks[:20]}")
    print(f"  cells with saved outputs: {sum(1 for _, c in code if c.get('outputs'))}")
