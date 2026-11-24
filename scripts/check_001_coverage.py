import csv
from cap.paths import get_paths
import nbformat

paths = get_paths()
ex_dir = paths.run_root / "01_preprocessing" / "executed_notebooks"
files = sorted(ex_dir.glob("001_*.ipynb"))

nb = nbformat.read(files[0], as_version=4)
print(f"Injected parameters in {files[0].name}:")
for c in nb.cells:
    if "injected-parameters" in c.metadata.get("tags", []):
        print(c.source)

ran = {f.name[len("001_"):-len(".ipynb")] for f in files}
with (paths.root / "config" / "cohort_release_2026-11-13.csv").open(encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))

included = {r["sample_id"] for r in rows if r["include"] == "True"}
included_with_files = {r["sample_id"] for r in rows
                       if r["include"] == "True" and r["files_present"] == "True"}

print(f"\nCohort rows: {len(rows)} | include=True: {len(included)} "
      f"| include=True and files present: {len(included_with_files)}")
print(f"Executed copies: {len(ran)}")
print("Included with files but not executed:", sorted(included_with_files - ran))
print("Executed but not included:", sorted(ran - included))
