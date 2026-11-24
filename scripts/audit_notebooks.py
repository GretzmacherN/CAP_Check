import csv, json, subprocess, tempfile
from pathlib import Path
from cap.paths import get_paths
from cap.provenance import notebook_source_sha256

paths = get_paths()
root, run = paths.root, paths.run_root

def hash_bytes(data):
    with tempfile.NamedTemporaryFile(suffix=".ipynb", delete=False) as t:
        t.write(data); name = t.name
    try:
        return notebook_source_sha256(Path(name))
    finally:
        Path(name).unlink(missing_ok=True)

def committed(commit, rel):
    r = subprocess.run(["git", "show", f"{commit}:{rel}"], cwd=root, capture_output=True)
    return r.stdout if r.returncode == 0 else None

rows = []
for d in sorted(x for x in run.iterdir() if x.is_dir() and x.name[:2].isdigit()):
    pf = d / "run_provenance.json"
    if not pf.is_file():
        continue
    p = json.loads(pf.read_text(encoding="utf-8"))
    nb = p.get("notebook") or {}
    rel, recorded = nb.get("path", ""), nb.get("source_sha256", "")
    working = notebook_source_sha256(root / rel) if rel and (root / rel).is_file() else None
    blob = committed(p["git_commit"], rel) if rel else None
    at_commit = hash_bytes(blob) if blob is not None else None
    rows.append({
        "stage": d.name,
        "run_commit": p["git_commit"][:8],
        "git_dirty": p["git_dirty"],
        "recorded_matches_run_commit": at_commit == recorded,
        "recorded_matches_working_copy": working == recorded,
        "dirty_entries": " | ".join(p["git_status_porcelain"]),
    })

out = paths.root / "run_records" / paths.run_id / "notebook_audit.csv"
out.parent.mkdir(parents=True, exist_ok=True)
with out.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
for r in rows:
    print(r["stage"], "| run commit:", r["run_commit"], "| matches run commit:",
          r["recorded_matches_run_commit"], "| matches working copy:",
          r["recorded_matches_working_copy"])
    if r["dirty_entries"]:
        print("    dirty:", r["dirty_entries"])
print("Written:", out)
