import nbformat
from cap.paths import get_paths

paths = get_paths()
run = paths.run_root

print("=== 02: export cells")
nb = nbformat.read(paths.root / "notebooks" / "002_Celltype_ID.ipynb", as_version=4)
for i, c in enumerate(nb.cells):
    if c.cell_type == "code" and ("cell_metadata.csv" in c.source or "barcode_table.csv" in c.source):
        lines = [l.strip() for l in c.source.splitlines() if "csv" in l]
        print(f"  index {i} | execution_count={c.get('execution_count')} | {lines}")
for name in ["cell_metadata.csv", "barcode_table.csv"]:
    hits = [str(p.relative_to(run)) for p in run.rglob(name)]
    print(f"  file {name}: {hits or 'not found'}")

print("\n=== 03d: moved cells and their dependencies")
nb = nbformat.read(paths.root / "notebooks" / "003d_Normal_Tissue_Protein.ipynb", as_version=4)
keys = ["gene_order = [", "def load_hpa", "hpa_summary = ", "load_hpa(data_file)",
        "score_hpa(abundance)", 'hpa_summary["rank"]']
for i, c in enumerate(nb.cells):
    if c.cell_type != "code":
        continue
    for k in keys:
        if k in c.source:
            print(f"  index {i} | execution_count={c.get('execution_count')} | {k}")
