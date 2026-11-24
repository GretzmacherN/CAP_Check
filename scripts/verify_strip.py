import json, subprocess, tempfile
from pathlib import Path
from cap.paths import get_paths
from cap.provenance import notebook_source_sha256

paths = get_paths()
root = paths.root
arch = paths.run_root / "notebooks_with_outputs"

def norm(src):
    return "".join(src) if isinstance(src, list) else (src or "")

def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

def cells(d):
    return [(c.get("cell_type"), norm(c.get("source"))) for c in d.get("cells", [])]

def top(d):
    return (d.get("nbformat"), d.get("nbformat_minor"),
            d.get("metadata", {}).get("kernelspec", {}).get("name"))

def head_blob(rel):
    r = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=root, capture_output=True)
    if r.returncode != 0:
        return None
    with tempfile.NamedTemporaryFile(suffix=".ipynb", delete=False) as t:
        t.write(r.stdout); name = t.name
    try:
        return Path(name)
    finally:
        pass

for s in sorted(d.name for d in paths.run_root.iterdir()
                if d.is_dir() and d.name[:2].isdigit()):
    pf = paths.stage_dir(s) / "run_provenance.json"
    if not pf.is_file():
        continue
    prov = json.loads(pf.read_text(encoding="utf-8"))
    rel = prov["notebook"]["path"]
    rec = prov["notebook"]["source_sha256"]
    work = root / rel
    archived = arch / Path(rel).name
    head = head_blob(rel)

    print(f"\n== {s}")
    print(f"  recorded == archive: {notebook_source_sha256(archived) == rec if archived.is_file() else 'no archive'}")
    print(f"  recorded == working: {notebook_source_sha256(work) == rec}")
    print(f"  recorded == HEAD:    {notebook_source_sha256(head) == rec if head else 'not in HEAD'}")
    if archived.is_file():
        a, w = load(archived), load(work)
        print(f"  top-level archive: {top(a)} | working: {top(w)}")
        print(f"  cells identical archive vs working: {cells(a) == cells(w)}")
