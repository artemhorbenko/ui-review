#!/usr/bin/env python3
"""Screenshot a page at 360, 768 and 1280 px, measure it and run UI checks.

Usage:
    python inspect_ui.py URL [--name home] [--out ./shots]
                         [--vp desktop=1280x800 --vp tablet=768x1024 --vp phone=360x780]
                         [--sel cta=".hero .btn" --sel h1="h1" ...]
                         [--full] [--wait 1500] [--browser /path/to/chrome]

For each viewport it saves <name>-<viewport>.jpg and writes <name>-inspect.json
with what scripts/probe.js measures (the same probe can be pasted into a
browser tool when there is no shell):
  - for each --sel: match count, box as % of the screenshot (ready for a mark
    in audit.json), computed styles (ready for change.cur) and text contrast;
  - checks: text contrast over the whole page (WCAG AA), tap targets (24 px
    minimum, WCAG 2.5.8; 44 px comfortable), text under 12 px, images without
    alt, icon-only links and buttons without a name, sideways scroll;
  - scale: distinct font sizes, weights, families, text and background
    colours, radii, spacing values and how many sit on a 4 px scale;
  - css: prefers-color-scheme and prefers-reduced-motion rules;
  - motion: running and infinite animations; perf: CLS and LCP (on your
    connection), with the elements that shifted;
  - fixed bars: how much of the screen sticky headers and banners take.
On the widest viewport it also emulates dark mode (and saves a -dark.jpg when
the page changes), emulates reduced motion, and tabs through the page to count
stops with a visible focus. A ready "checks" array for audit.json is included.

Viewports narrower than 900 px get touch input; the layout viewport stays at
the given width, so overflow shows up as sideways scroll. The page is only
loaded and read: nothing is clicked, typed or submitted.

Needs: pip install playwright && playwright install chromium
"""
import argparse
import json
import pathlib
import re
import shutil
import sys

HERE = pathlib.Path(__file__).resolve().parent
PROBE = (HERE / "probe.js").read_text(encoding="utf-8")
PROBE = PROBE[PROBE.index("async ("):].rstrip().rstrip(";")
LOOK = "() => { const b = getComputedStyle(document.body), h = getComputedStyle(document.documentElement); return [b.backgroundColor, h.backgroundColor, b.color].join('|'); }"

FOCUS_STYLE = """el => { const cs = getComputedStyle(el); return [cs.outlineStyle, cs.outlineWidth, cs.outlineColor, cs.boxShadow, cs.borderColor, cs.backgroundColor, cs.textDecorationLine, cs.color].join('|'); }"""


def focus_walk(page, tabs):
    """Tab through the page and count stops whose look changes on focus."""
    res = {"total": 0, "pass": 0, "fails": []}
    seen = set()
    page.evaluate("() => { document.activeElement && document.activeElement.blur(); scrollTo(0, 0); }")
    for _ in range(tabs):
        page.keyboard.press("Tab")
        info = page.evaluate("""() => { const el = document.activeElement; if (!el || el === document.body) return null;
            const r = el.getBoundingClientRect(); const id = el.tagName + '|' + Math.round(r.left + scrollX) + '|' + Math.round(r.top + scrollY);
            const path = el.id ? '#' + el.id : el.tagName.toLowerCase() + [...el.classList].slice(0, 2).map(c => '.' + c).join('');
            return {id, path, text: (el.innerText || el.getAttribute('aria-label') || el.placeholder || '').trim().slice(0, 40)}; }""")
        if not info or info["id"] in seen:
            if info is None:
                continue
            break
        seen.add(info["id"])
        on = page.evaluate(f"() => ({FOCUS_STYLE})(document.activeElement)")
        off = page.evaluate(f"() => {{ const el = document.activeElement; el.blur(); return ({FOCUS_STYLE})(el); }}")
        res["total"] += 1
        if on != off:
            res["pass"] += 1
        elif len(res["fails"]) < 15:
            res["fails"].append({"sel": info["path"], "text": info["text"]})
    return res


def parse_pairs(items, what):
    out = {}
    for it in items or []:
        if "=" not in it:
            sys.exit(f"--{what} needs NAME=VALUE, got '{it}'")
        k, v = it.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def summary_checks(results):
    """Suggest a checks array for audit.json from all viewports."""
    rows = {}
    def add(label, v, b, t, vp):
        if b:
            r = rows.setdefault(label, [0, 0, t, []])
            r[0] += v; r[1] += b; r[3].append(vp)
    for vp, r in results.items():
        c = r["checks"]
        add("Text contrast ≥ WCAG AA", c["contrast"]["pass"], c["contrast"]["total"] - c["contrast"]["unknown"], 100, vp)
        add("Icon-only controls with a name", c["iconNames"]["pass"], c["iconNames"]["total"], 100, vp)
        add("Text ≥ 12 px", c["small"]["pass"], c["small"]["total"], 100, vp)
        if r["touch"]:
            add("Tap targets ≥ 24 px", c["targets"]["pass24"], c["targets"]["total"], 100, vp)
            add("Tap targets ≥ 44 px", c["targets"]["pass44"], c["targets"]["total"], 90, vp)
        if c.get("focus"):
            add("Visible keyboard focus", c["focus"]["pass"], c["focus"]["total"], 100, vp)
    return [{"l": l, "v": v, "b": b, "t": t, "sub": ", ".join(vps), "src": "inspect_ui.py"} for l, (v, b, t, vps) in rows.items()]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--name", default="page")
    ap.add_argument("--out", default="shots")
    ap.add_argument("--vp", action="append", help="NAME=WIDTHxHEIGHT; default desktop=1280x800, tablet=768x1024, phone=360x780")
    ap.add_argument("--sel", action="append", help="NAME=CSS selector to measure and box")
    ap.add_argument("--full", action="store_true", help="full-page screenshots (boxes relative to the whole page)")
    ap.add_argument("--wait", type=int, default=1500, help="ms to wait after load")
    ap.add_argument("--tabs", type=int, default=40, help="Tab presses for the keyboard focus check")
    ap.add_argument("--quality", type=int, default=72, help="JPEG quality")
    ap.add_argument("--no-scan", action="store_true", help="measure contrast only in the first screen (faster)")
    ap.add_argument("--browser", help="path to Chrome/Chromium if Playwright's own is not installed")
    a = ap.parse_args()

    vps = parse_pairs(a.vp or ["desktop=1280x800", "tablet=768x1024", "phone=360x780"], "vp")
    sels = parse_pairs(a.sel, "sel")
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    url = a.url
    if re.match(r"^[./~]|^[A-Za-z]:\\", url) or pathlib.Path(url).exists():
        url = pathlib.Path(url).expanduser().resolve().as_uri()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright is not installed: pip install playwright && playwright install chromium")
        return 2

    results = {}
    widest = max(vps, key=lambda k: int(vps[k].lower().split("x")[0]))
    with sync_playwright() as pw:
        launch = {"args": ["--no-sandbox"]}
        exe = a.browser or next((shutil.which(b) for b in ("google-chrome", "chromium", "chromium-browser") if shutil.which(b)), None)
        try:
            browser = pw.chromium.launch(**launch)
        except Exception:
            if not exe:
                print("no browser: run `playwright install chromium` or pass --browser")
                return 2
            browser = pw.chromium.launch(executable_path=exe, **launch)
        for name, size in vps.items():
            w, h = (int(x) for x in size.lower().split("x"))
            touch = w < 900
            ctx = browser.new_context(viewport={"width": w, "height": h}, has_touch=touch, device_scale_factor=1, color_scheme="light")
            page = ctx.new_page()
            try:
                page.goto(url, wait_until="networkidle", timeout=45000)
            except Exception:
                page.goto(url, wait_until="load", timeout=45000)
            page.wait_for_timeout(a.wait)
            r = page.evaluate(PROBE, {"sels": sels, "full": a.full, "scan": not a.no_scan})
            file = out / f"{a.name}-{name}.jpg"
            page.screenshot(path=str(file), type="jpeg", quality=a.quality, full_page=a.full)
            r.update(file=str(file), touch=touch)
            if name == widest:
                r["checks"]["focus"] = focus_walk(page, a.tabs)
                page.evaluate("() => scrollTo(0, 0)")
                light = page.evaluate(LOOK)
                page.emulate_media(color_scheme="dark")
                page.wait_for_timeout(400)
                dark = page.evaluate(LOOK)
                r["dark"] = {"changes": light != dark, "light": light, "dark": dark}
                if light != dark:
                    df = out / f"{a.name}-{name}-dark.jpg"
                    page.screenshot(path=str(df), type="jpeg", quality=a.quality)
                    r["dark"]["file"] = str(df)
                page.emulate_media(color_scheme="light", reduced_motion="reduce")
                page.reload()
                page.wait_for_timeout(a.wait)
                r["motion"]["runningWithReducedMotion"] = page.evaluate("() => document.getAnimations ? document.getAnimations().filter(a => a.playState === 'running').length : null")
            results[name] = r
            ctx.close()
        browser.close()

    report = {"url": a.url, "viewports": results, "suggested_checks": summary_checks(results)}
    jf = out / f"{a.name}-inspect.json"
    jf.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    for name, r in results.items():
        c, s = r["checks"], r["scale"]
        print(f"[{name} {r['viewport']}] {r['file']}" + (f"  SIDEWAYS SCROLL {r['hscroll']}px" if r["hscroll"] else "") + ("" if r["lang"] else "  no <html lang>"))
        print(f"  contrast {c['contrast']['pass']}/{c['contrast']['total'] - c['contrast']['unknown']} pass (unknown {c['contrast']['unknown']})"
              + (f"; targets ≥24px {c['targets']['pass24']}/{c['targets']['total']}, ≥44px {c['targets']['pass44']}/{c['targets']['total']}" if r["touch"] else "")
              + (f"; focus visible {c['focus']['pass']}/{c['focus']['total']}" if c.get("focus") else "")
              + f"; unnamed icon controls {c['iconNames']['total'] - c['iconNames']['pass']}/{c['iconNames']['total']}; alt {c['alt']['pass']}/{c['alt']['total']}; text<12px {c['small']['total'] - c['small']['pass']}")
        print(f"  scale: {s['fontSizes']['distinct']} font sizes, {s['textColours']['distinct']} text colours, {s['radii']['distinct']} radii, spacing {s['spacing']['onScale4']}/{s['spacing']['distinct']} on 4px scale; fixed bars {r['fixed']['topPx']}px ({r['fixed']['topShare']}%)")
        p = r["perf"]
        print(f"  perf: CLS {p.get('cls')} LCP {(p.get('lcp') or {}).get('ms')}ms; motion: {r['motion']['running']} running, {r['motion']['infinite']} infinite; css: dark rules {r['css']['darkRules']}, reduced-motion rules {r['css']['reducedMotionRules']} (unreadable sheets {r['css']['unreadable']})")
        if r.get("dark"):
            print(f"  dark mode: {'changes' if r['dark']['changes'] else 'no change'}; animations with reduced motion: {r['motion'].get('runningWithReducedMotion')}")
        for f in c["contrast"]["fails"][:5]:
            print(f"    contrast {f['ratio']}:1 (needs {f['need']}) {f['fg']} on {f['bg']} {f['size']} '{f['text']}' {f['sel']}")
        for k, e in r["elements"].items():
            if e.get("count"):
                b, st = e["box"], e["styles"]
                print(f"  {k}: x{b['x']} y{b['y']} w{b['w']} h{b['h']}%{'' if b['inView'] else ' (out of view)'}  {st['fontSize']} {st['color']} on {st['background']}  {st['width']}×{st['height']}  radius {st['borderRadius']}")
            else:
                print(f"  {k}: no match for {e.get('sel')}" + (f" ({e['error']})" if e.get("error") else ""))
    print(f"details: {jf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
