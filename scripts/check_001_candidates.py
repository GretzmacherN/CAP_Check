import json, tempfile
from pathlib import Path
import nbformat
from cap.paths import get_paths
from cap.provenance import notebook_source_sha256

paths = get_paths()
rec = json.loads((paths.stage_dir("01_preprocessing") / "run_provenance.json")
                 .read_text(encoding="utf-8"))["notebook"]["source_sha256"]
print("recorded:", rec)

def h(nb):
    with tempfile.NamedTemporaryFile(suffix=".ipynb", delete=False) as t:
        name = t.name
    nbformat.write(nb, name)
    try:
        return notebook_source_sha256(Path(name))
    finally:
        Path(name).unlink(missing_ok=True)

def strip(nb):
    nb.cells = [c for c in nb.cells if "injected-parameters" not in c.metadata.get("tags", [])]
    return nb

candidates = [
    paths.root / "notebooks" / "001_Preprocessing.ipynb",
    paths.root / "notebooks" / "001_Papermill.ipynb",
    paths.run_root / "notebooks_with_outputs" / "001_Papermill.ipynb",
]
print("\nWorking-tree candidates:")
for c in candidates:
    if c.is_file():
        print(f"  {c.parent.name}\\{c.name}: matches recorded = {h(strip(nbformat.read(c, as_version=4))) == rec}")

ex = sorted((paths.run_root / "01_preprocessing" / "executed_notebooks").glob("001_*.ipynb"))
hashes = {f.name: h(strip(nbformat.read(f, as_version=4))) for f in ex}
print(f"\nExecuted per-sample copies: {len(ex)}")
print(f"  distinct code hashes: {len(set(hashes.values()))}")
print(f"  matching recorded: {sum(v == rec for v in hashes.values())}")
for name, v in list(hashes.items())[:5]:
    print(f"  {name}: {v[:12]}")
