#!/usr/bin/env python3
"""Check a ui-review audit.json before it becomes a report and a hands-off file.

Usage: python validate_audit.py audit.json

Errors (exit 1) break the report or the skill's rules; warnings (exit 0)
are worth a look. Standard library only.
"""
import json
import re
import sys

ICONS = {"hier", "grid", "type", "color", "heur", "nav", "form", "state", "a11y", "resp", "copy", "sys"}
GROUPS = {"look", "use", "reach", "words", "system"}
LANGS = {"uk", "en"}
STATUSES = {"ok", "demo", "no"}
TOKENS = re.compile(r"\{(health|qw|n|conf|crit)\}")
TEXT_KEYS = ["headline", "lead", "lensesH", "matrixH", "opsH", "nextH", "planH", "dataH"]


def ice(o):
    return o.get("I", 0) * o.get("C", 0) * o.get("E", 0)


def validate(a):
    err, warn = [], []
    E, W = err.append, warn.append

    if not isinstance(a, dict):
        return ["the file is not a JSON object"], []

    if a.get("lang") not in LANGS:
        W(f"lang '{a.get('lang')}' has no interface dictionary; labels fall back to English (add an entry to UI in the template)")

    text = a.get("text") or {}
    keys = TEXT_KEYS + (["shotsH"] if a.get("shots") else []) + (["screensH"] if a.get("screens") else [])
    for k in keys:
        if not str(text.get(k, "")).strip():
            E(f"text.{k} is missing: every section needs a heading that states its point")
    if "<" in json.dumps(text, ensure_ascii=False):
        W("text contains '<': HTML is shown as plain text; use [[...]] to highlight words")

    sources = a.get("sources") or []
    names = {s.get("name") for s in sources}
    status = {s.get("name"): s.get("status") for s in sources}

    def check_src(path, src):
        if not src:
            E(f"{path} has a number but no src: name the source it came from")
        elif src not in names:
            E(f"{path}.src '{src}' is not in sources")
        elif status.get(src) == "no":
            E(f"{path} cites '{src}', which is marked as not available")

    # lenses
    lenses = a.get("lenses") or []
    if len(lenses) != 12:
        W(f"{len(lenses)} lenses instead of 12")
    seen_i = set()
    for i, l in enumerate(lenses):
        p = f"lenses[{i}]"
        if l.get("i") not in ICONS:
            E(f"{p}.i '{l.get('i')}' is not a lens id ({', '.join(sorted(ICONS))})")
        elif l["i"] in seen_i:
            W(f"{p}.i '{l['i']}' is used twice")
        seen_i.add(l.get("i"))
        if l.get("g") not in GROUPS:
            E(f"{p}.g '{l.get('g')}' is not a group ({', '.join(sorted(GROUPS))})")
        s = l.get("s")
        if not isinstance(s, (int, float)) or not 0 <= s <= 100:
            E(f"{p}.s must be a number 0-100")
        if not l.get("k"):
            E(f"{p}.k (short name) is missing")

    # header picture
    checks, funnel = a.get("checks"), a.get("funnel")
    if checks and funnel:
        E("use either checks or funnel, not both")
    for i, c in enumerate(checks or []):
        p = f"checks[{i}]"
        if not c.get("l"):
            E(f"{p}.l is missing")
        if not isinstance(c.get("t"), (int, float)):
            E(f"{p}.t (target %) must be a number")
        v, b = c.get("v"), c.get("b")
        if v is not None:
            if not isinstance(v, (int, float)) or not isinstance(b, (int, float)) or b <= 0:
                E(f"{p} has v but no positive base b")
            elif v > b:
                E(f"{p}.v ({v}) is larger than b ({b})")
            check_src(p, c.get("src"))
    if funnel:
        if len(funnel) < 2:
            E("funnel needs a base step and at least one more")
        for i, f in enumerate(funnel):
            n = f.get("n")
            if n is not None and (not isinstance(n, (int, float)) or n < 0):
                E(f"funnel[{i}].n must be a number or null (no data)")
    if not checks and not funnel:
        W("no checks or funnel: the header has no picture")
    if checks and all(c.get("v") is None for c in checks) and not any(s.get("status") == "no" for s in sources):
        W("no check has a value but no source is marked 'no': say which tool was missing")

    m = a.get("maturity")
    if m is not None and (not isinstance(m.get("cur"), int) or not 0 <= m["cur"] <= 4):
        E("maturity.cur must be 0-4 (Broken, Usable, Consistent, Polished, Delightful)")

    shot_ids = {}
    for i, s in enumerate(a.get("shots") or []):
        p = f"shots[{i}]"
        if not s.get("id"):
            E(f"{p}.id is missing")
            continue
        if s["id"] in shot_ids:
            E(f"{p}.id '{s['id']}' is used twice")
        shot_ids[s["id"]] = s
        for k in ("w", "h"):
            if not isinstance(s.get(k), (int, float)) or s[k] <= 0:
                E(f"{p}.{k} must be the image size in px (sets the aspect ratio)")
        if not s.get("src"):
            W(f"{p} '{s['id']}' has no src: the report shows a placeholder frame with the marks")
        for j, mk in enumerate(s.get("marks") or []):
            q = f"{p}.marks[{j}]"
            for k in ("x", "y", "w", "h"):
                v = mk.get(k)
                if not isinstance(v, (int, float)) or not 0 <= v <= 100:
                    E(f"{q}.{k} must be 0-100 (% of the image)")
            if all(isinstance(mk.get(k), (int, float)) for k in ("x", "y", "w", "h")):
                if mk["x"] + mk["w"] > 100.5 or mk["y"] + mk["h"] > 100.5:
                    E(f"{q} runs outside the image (x+w or y+h > 100)")
                if mk["w"] < 0.5 or mk["h"] < 0.3:
                    W(f"{q} is very small; make the box cover the whole element")

    for i, r in enumerate(a.get("screens") or []):
        if r.get("st") not in ("ok", "warn", "bad"):
            E(f"screens[{i}].st must be ok, warn or bad")
        if r.get("shot") and r["shot"] not in shot_ids:
            E(f"screens[{i}].shot '{r['shot']}' is not a shot id")

    # opportunities
    ops = a.get("ops") or []
    if not ops:
        E("ops is empty")
    detail = a.get("detail") or {}
    marked = set()
    for s in shot_ids.values():
        for mk in s.get("marks") or []:
            n = mk.get("n")
            if not isinstance(n, int) or not 1 <= n <= len(ops):
                E(f"a mark on shot '{s['id']}' points to issue {n}, which does not exist")
            marked.add(n)
    for i, o in enumerate(ops):
        p, oid = f"ops[{i}] (#{i + 1})", i + 1
        for k in ("I", "C", "E"):
            v = o.get(k)
            if not isinstance(v, int) or not 1 <= v <= 10:
                E(f"{p}.{k} must be a whole number 1-10")
        sev = o.get("sev")
        if not isinstance(sev, int) or not 1 <= sev <= 4:
            E(f"{p}.sev must be 1-4 (cosmetic, minor, major, critical)")
        elif sev == 4 and isinstance(o.get("I"), int) and o["I"] < 8:
            W(f"{p} is critical (sev 4) but has impact {o['I']}: critical issues should have impact 8+")
        if o.get("x") not in ("opt", "ex"):
            E(f"{p}.x must be opt (fix) or ex (rethink)")
        if o.get("ev") not in ("obs", "hyp"):
            E(f"{p}.ev must be obs (observed) or hyp (hypothesis)")
        if o.get("l") not in ICONS:
            E(f"{p}.l '{o.get('l')}' is not a lens id")
        if not o.get("t") or not o.get("ln"):
            E(f"{p} needs t (title) and ln (lens label)")
        if o.get("ev") == "hyp" and isinstance(o.get("C"), int) and o["C"] > 7:
            W(f"{p} is a hypothesis with confidence {o['C']}: confidence above 7 needs evidence")
        if shot_ids and oid not in marked:
            W(f"{p} has no mark on any screenshot")
        d = detail.get(str(oid))
        if not d:
            E(f"{p} has no detail[\"{oid}\"]: every issue needs its evidence, location and steps")
            continue
        if not str(d.get("why", "")).strip():
            E(f"detail[\"{oid}\"].why is empty: every finding must point to evidence")
        if len(d.get("steps") or []) < 2:
            E(f"detail[\"{oid}\"].steps needs at least 2 concrete steps")
        for k in ("metric", "effort", "risk"):
            if not str(d.get(k, "")).strip():
                E(f"detail[\"{oid}\"].{k} is missing")
        where = d.get("where") or []
        if not where:
            E(f"detail[\"{oid}\"].where is missing: name the page or URL, viewport, and selector or screenshot")
        for j, w in enumerate(where):
            q = f"detail[\"{oid}\"].where[{j}]"
            if not (w.get("page") or w.get("url")):
                E(f"{q} needs page or url")
            if not w.get("vp"):
                E(f"{q} needs vp (viewport, e.g. 390×844 or 'all')")
            if not (w.get("sel") or w.get("shot")):
                E(f"{q} needs sel (CSS selector) or shot (screenshot id)")
            if w.get("shot") and w["shot"] not in shot_ids:
                E(f"{q}.shot '{w['shot']}' is not a shot id")
        ch = d.get("change")
        if not ch and o.get("x") == "opt" and o.get("ev") == "obs":
            W(f"detail[\"{oid}\"] has no change list: give current vs target values for an observed fix")
        for j, c in enumerate(ch or []):
            q = f"detail[\"{oid}\"].change[{j}]"
            for k in ("prop", "cur", "tgt"):
                if not str(c.get(k, "")).strip():
                    E(f"{q}.{k} is missing")
            if str(c.get("cur", "")).strip() == str(c.get("tgt", "")).strip() and c.get("cur"):
                W(f"{q}: current and target are the same")
        for dep in d.get("depends") or []:
            if not re.fullmatch(r"T\d{2,}", str(dep)) or not 1 <= int(str(dep)[1:]) <= len(ops):
                E(f"detail[\"{oid}\"].depends '{dep}' is not a task id (T01..T{len(ops):02d})")
    for k in detail:
        if not k.isdigit() or not 1 <= int(k) <= len(ops):
            E(f"detail[\"{k}\"] does not match any issue")

    ranked = sorted(range(1, len(ops) + 1), key=lambda j: (-ice(ops[j - 1]), j))
    for oid in ranked[:3]:
        pl = (a.get("plans") or {}).get(str(oid))
        if not pl or not all(str(pl.get(k, "")).strip() for k in ("h", "m", "t")):
            E(f"top-3 issue #{oid} needs plans[\"{oid}\"] with h (hypothesis), m (metric), t (cheapest test)")
        d = detail.get(str(oid)) or {}
        for k in ("alt", "rtype", "thr", "pm"):
            if not d.get(k):
                E(f"top-3 issue #{oid} needs detail.{k} (alternatives, risk type, threshold, pre-mortem)")

    if not sources:
        E("sources is empty: list what was used and what was missing")
    for i, s in enumerate(sources):
        if s.get("status") not in STATUSES:
            E(f"sources[{i}].status must be ok, demo or no")
    for i, k in enumerate(a.get("kpis") or []):
        v = str(k.get("v", ""))
        if not TOKENS.search(v) and re.search(r"\d", v):
            check_src(f"kpis[{i}] '{v}'", k.get("src"))

    for i, q in enumerate(a.get("answers") or []):
        if not q.get("q") or not q.get("a"):
            E(f"answers[{i}] needs q and a (for a skipped question, a = the assumption taken)")
    for i, t in enumerate(a.get("tokens") or []):
        if not t.get("name") or not t.get("value"):
            E(f"tokens[{i}] needs name and value")

    gl = a.get("glossary") or {}
    for k, v in gl.items():
        if not v.get("g") or not v.get("d"):
            E(f"glossary['{k}'] needs g (short gloss) and d (definition)")
    if not gl:
        W("glossary is empty: terms will have no tooltips")
    return err, warn


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    with open(sys.argv[1], encoding="utf-8") as f:
        try:
            a = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERROR] not valid JSON: {e}")
            return 1
    err, warn = validate(a)
    for e in err:
        print("[ERROR]", e)
    for w in warn:
        print("[WARN] ", w)
    print("OK" if not err else f"{len(err)} error(s)")
    return 1 if err else 0


if __name__ == "__main__":
    sys.exit(main())
