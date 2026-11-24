import difflib, json, subprocess
from cap.paths import get_paths

paths = get_paths()
rel = "notebooks/000_Raw_Data_And_Cohort.ipynb"
prov = json.loads((paths.stage_dir("00_cohort") / "run_provenance.json").read_text(encoding="utf-8"))
commit = prov["git_commit"]

import nbformat, tempfile
from pathlib import Path

blob = subprocess.run(["git", "show", f"{commit}:{rel}"], cwd=paths.root,
                      capture_output=True, check=True).stdout
with tempfile.NamedTemporaryFile(suffix=".ipynb", delete=False) as t:
    t.write(blob); tmp = Path(t.name)
old_nb = nbformat.read(tmp, as_version=4)
tmp.unlink()
new_nb = nbformat.read(paths.root / rel, as_version=4)

def export(nb):
    out = []
    for i, c in enumerate(nb.cells):
        out.append(f"### cell {i} [{c.cell_type}]")
        out.extend(c.source.splitlines())
    return out

diff = list(difflib.unified_diff(export(old_nb), export(new_nb),
                                 f"{commit[:8]} (run commit)", "working copy", lineterm=""))
diffs = paths.run_root / "executed_notebooks" / "diffs"
diffs.mkdir(parents=True, exist_ok=True)
out = diffs / "00_cohort.diff.txt"
if out.exists():
    raise FileExistsError(out)
out.write_text("\n".join(diff) + "\n", encoding="utf-8")
print(f"Written: {out}")
print("\n".join(l for l in diff if l[:1] in "+-" and l[:2] not in ("++", "--")))
