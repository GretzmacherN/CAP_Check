import inspect, subprocess, difflib
from pathlib import Path
import nbformat
from cap.paths import get_paths
import cap.provenance as prov

paths = get_paths()
root = paths.root
print(inspect.getsource(prov.notebook_source_sha256))

ex = sorted((paths.run_root / "01_preprocessing" / "executed_notebooks").glob("001_*.ipynb"))[0]
nb_ex = nbformat.read(ex, as_version=4)
nb_ex.cells = [c for c in nb_ex.cells if "injected-parameters" not in c.metadata.get("tags", [])]
ref_code = [c.source for c in nb_ex.cells if c.cell_type == "code"]
ref_all = [(c.cell_type, c.source) for c in nb_ex.cells]
print(f"\nReference: {ex.name} | code cells: {len(ref_code)} | all cells: {len(ref_all)}")

def load_git(commit, rel):
    r = subprocess.run(["git", "show", f"{commit}:{rel}"], cwd=root, capture_output=True)
    return nbformat.reads(r.stdout.decode("utf-8"), as_version=4) if r.returncode == 0 else None

cands = {
    "working notebooks/001_Preprocessing.ipynb": paths.root / "notebooks" / "001_Preprocessing.ipynb",
    "working notebooks/001_Papermill.ipynb": paths.root / "notebooks" / "001_Papermill.ipynb",
    "archive notebooks_with_outputs/001_Papermill.ipynb": paths.run_root / "notebooks_with_outputs" / "001_Papermill.ipynb",
}
for label, p in cands.items():
    cands[label] = nbformat.read(p, as_version=4) if p.is_file() else None
commit = "9124e1a68191f01af7ef225c1e00ac7396d98c4f"
cands[f"git {commit[:8]} notebooks/001_Papermill.ipynb"] = load_git(commit, "notebooks/001_Papermill.ipynb")
cands[f"git {commit[:8]} notebooks/001_Preprocessing.ipynb"] = load_git(commit, "notebooks/001_Preprocessing.ipynb")

for label, nb in cands.items():
    print(f"\n== {label}")
    if nb is None:
        print("  not found"); continue
    code = [c.source for c in nb.cells if c.cell_type == "code"]
    allc = [(c.cell_type, c.source) for c in nb.cells]
    print(f"  code cells: {len(code)} | all cells: {len(allc)}")
    print(f"  code cells identical to executed copy: {code == ref_code}")
    print(f"  all cells identical to executed copy: {allc == ref_all}")
    if code != ref_code:
        for i, (a, b) in enumerate(zip(ref_code, code)):
            if a != b:
                print(f"  first differing code cell: {i}")
                d = list(difflib.unified_diff(a.splitlines(), b.splitlines(),
                                              "executed", label, lineterm="", n=1))
                print("\n".join("    " + l for l in d[:30]))
                break
        else:
            print("  code cell counts differ or one is a prefix of the other")
