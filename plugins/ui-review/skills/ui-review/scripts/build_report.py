#!/usr/bin/env python3
"""Turn a ui-review audit.json into a finished report page.

Usage: python build_report.py audit.json report.html [--template path] [--force] [--no-embed]

Validates the data first (see validate_audit.py) and stops on errors unless
--force is given. Screenshot files named in shots[].src (relative to
audit.json) are embedded as data URIs so the page stays one file; pass
--no-embed to keep the paths. Then puts the JSON into the template's
<script type="application/json" id="audit"> block, sets <html lang> and
<title>, and writes the page. Standard library only.
"""
import argparse
import base64
import copy
import json
import mimetypes
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from validate_audit import validate  # noqa: E402

BLOCK = re.compile(r'(<script type="application/json" id="audit">\n?)(.*?)(\n?</script>)', re.S)
BIG = 400 * 1024


def embed_shots(audit, base):
    audit = copy.deepcopy(audit)
    notes = []
    for s in audit.get("shots") or []:
        src = s.get("src")
        if not src or src.startswith(("data:", "http://", "https://")):
            continue
        path = src if os.path.isabs(src) else os.path.join(base, src)
        if not os.path.exists(path):
            notes.append(f"shot '{s.get('id')}': file not found ({src}); a placeholder frame is drawn")
            s.pop("src")
            continue
        raw = open(path, "rb").read()
        if len(raw) > BIG:
            notes.append(f"shot '{s.get('id')}' is {len(raw) // 1024} KB; save it as JPEG ≤ 1280px wide to keep the page light")
        mime = mimetypes.guess_type(path)[0] or "image/png"
        s["src"] = f"data:{mime};base64," + base64.b64encode(raw).decode()
    return audit, notes


def build(audit, template):
    blob = json.dumps(audit, ensure_ascii=False, indent=1)
    blob = blob.replace("</", "<\\/").replace("<!--", "<\\!--")
    if not BLOCK.search(template):
        raise ValueError("the template has no <script type=\"application/json\" id=\"audit\"> block")
    page = BLOCK.sub(lambda m: m.group(1) + blob + m.group(3), template, count=1)
    lang = audit.get("lang", "en")
    page = re.sub(r'<html lang="[^"]*"', f'<html lang="{lang}"', page, count=1)
    title = audit.get("title")
    if title:
        safe = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        page = re.sub(r"<title>.*?</title>", lambda m: f"<title>{safe}</title>", page, count=1, flags=re.S)
    return page


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audit")
    ap.add_argument("out")
    ap.add_argument("--template", default=os.path.join(HERE, "..", "assets", "report-template.html"))
    ap.add_argument("--force", action="store_true", help="write the page even if validation finds errors")
    ap.add_argument("--no-embed", action="store_true", help="keep screenshot paths instead of embedding the images")
    a = ap.parse_args()

    with open(a.audit, encoding="utf-8") as f:
        audit = json.load(f)
    err, warn = validate(audit)
    for w in warn:
        print("[WARN] ", w)
    for e in err:
        print("[ERROR]", e)
    if err and not a.force:
        print(f"Not built: {len(err)} error(s). Fix them or pass --force.")
        return 1
    if not a.no_embed:
        audit, notes = embed_shots(audit, os.path.dirname(os.path.abspath(a.audit)))
        for n in notes:
            print("[WARN] ", n)
    with open(a.template, encoding="utf-8") as f:
        page = build(audit, f.read())
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"Written {a.out} ({len(page) // 1024} KB). Next: python {os.path.join(HERE, 'check_report.py')} {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
