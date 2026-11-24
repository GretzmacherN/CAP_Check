import nbformat
from cap.paths import get_paths

paths = get_paths()
targets = [
    ("notebooks/000_Raw_Data_And_Cohort.ipynb", 1),
    ("notebooks/003b_Meta_Programmes.ipynb", 3),
    ("notebooks/002_Celltype_ID.ipynb", 272),
]
for rel, idx in targets:
    nb = nbformat.read(paths.root / rel, as_version=4)
    c = nb.cells[idx]
    print(f"===== {rel} | index {idx} | {c.cell_type} | execution_count={c.get('execution_count')}")
    print(c.source)
    print()
