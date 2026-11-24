#!/usr/bin/env python3
"""Screenshot a page, measure elements and run automatic UI checks.

Usage:
    python inspect_ui.py URL [--name home] [--out ./shots]
                         [--vp desktop=1280x800 --vp phone=390x844 ...]
                         [--sel cta=".hero .btn" --sel email="#email" ...]
                         [--full] [--dark] [--wait 1200] [--browser /path/to/chrome]

For each viewport it saves <name>-<viewport>.jpg and prints, and writes to
<name>-inspect.json:
  - for each --sel: how many elements match, the first one's box as % of the
    screenshot (ready for a mark in audit.json) and its computed styles and
    text contrast (ready for change.cur);
  - checks: text contrast (WCAG AA 4.5:1, large text 3:1), touch targets
    (24x24 px minimum, WCAG 2.5.8; 44x44 px comfortable), text under 12 px,
    images without alt, form fields without an accessible name, sideways
    scroll, missing <html lang>, and on desktop viewports a keyboard walk
    (Tab up to --tabs times) counting stops with a visible focus change;
    failing items come with a selector.
  - a ready-made "checks" array for audit.json (pass counts against targets).

Viewports narrower than 900px get touch input. The layout viewport is kept at
the given width (no mobile zoom-out), so content that overflows shows up as
sideways scroll instead of being shrunk to fit. The page is
only loaded and read: nothing is clicked, typed or submitted.
Contrast over background images or gradients cannot be computed and is
counted as "unknown", not as a pass.

Needs: pip install playwright && playwright install chromium
"""
import argparse
import json
import pathlib
import re
import shutil
import sys

PROBE = r"""
({sels, full}) => {
  const vw = innerWidth, vh = innerHeight;
  const docW = Math.max(document.documentElement.scrollWidth, vw), docH = Math.max(document.documentElement.scrollHeight, vh);
  const W = full ? docW : vw, H = full ? docH : vh;
  const parse = c => { const m = c && c.match(/rgba?\(([^)]+)\)/); if (!m) return null; const p = m[1].split(/[ ,\/]+/).filter(Boolean).map(Number); return {r:p[0], g:p[1], b:p[2], a: p.length > 3 ? p[3] : 1}; };
  const hex = c => c ? '#' + [c.r, c.g, c.b].map(v => Math.round(v).toString(16).padStart(2, '0')).join('') + (c.a < 1 ? Math.round(c.a * 255).toString(16).padStart(2, '0') : '') : null;
  const blend = (top, bot) => ({r: top.r * top.a + bot.r * (1 - top.a), g: top.g * top.a + bot.g * (1 - top.a), b: top.b * top.a + bot.b * (1 - top.a), a: 1});
  const lum = c => { const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); }; return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const bgOf = el => {
    const layers = [];
    for (let e = el; e; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') return null;
      const c = parse(cs.backgroundColor);
      if (c && c.a > 0) { layers.push(c); if (c.a >= 1) break; }
    }
    let base = {r: 255, g: 255, b: 255, a: 1};
    for (let i = layers.length - 1; i >= 0; i--) base = blend(layers[i], base);
    return base;
  };
  const visible = el => { const r = el.getBoundingClientRect(), cs = getComputedStyle(el); return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && parseFloat(cs.opacity) > 0.05; };
  const path = el => {
    if (el.id) return '#' + CSS.escape(el.id);
    const parts = [];
    for (let e = el, i = 0; e && e !== document.body && i < 3; e = e.parentElement, i++) {
      if (e.id) { parts.unshift('#' + CSS.escape(e.id)); break; }
      const cls = [...e.classList].filter(c => !/^(is-|has-|js-)/.test(c)).slice(0, 2).map(c => '.' + CSS.escape(c)).join('');
      parts.unshift(e.tagName.toLowerCase() + cls);
    }
    return parts.join(' > ');
  };
  const box = el => { const r = el.getBoundingClientRect(); const ox = full ? scrollX : 0, oy = full ? scrollY : 0;
    const x = (r.left + ox) / W * 100, y = (r.top + oy) / H * 100, w = r.width / W * 100, h = r.height / H * 100;
    const inView = full || (r.bottom > 0 && r.top < vh && r.right > 0 && r.left < vw);
    const cl = v => Math.round(Math.max(0, Math.min(100, v)) * 10) / 10;
    return {x: cl(x), y: cl(y), w: cl(Math.min(w, 100 - Math.max(0, x))), h: cl(Math.min(h, 100 - Math.max(0, y))), px: {x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height)}, inView};
  };
  const ownText = el => [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.nodeValue).join(' ').replace(/\s+/g, ' ').trim();
  const contrastOf = el => {
    const cs = getComputedStyle(el), fg = parse(cs.color), bg = bgOf(el);
    if (!fg || !bg) return {unknown: true, fg: hex(fg)};
    const f = fg.a < 1 ? blend(fg, bg) : fg, size = parseFloat(cs.fontSize), weight = parseInt(cs.fontWeight) || 400;
    const large = size >= 24 || (size >= 18.66 && weight >= 700);
    const r = Math.round(ratio(f, bg) * 100) / 100;
    return {ratio: r, need: large ? 3 : 4.5, pass: r >= (large ? 3 : 4.5), fg: hex(fg), bg: hex(bg), size, weight, large};
  };

  // contrast
  const textEls = [...document.querySelectorAll('body *')].filter(el => !['SCRIPT', 'STYLE', 'NOSCRIPT', 'SVG', 'OPTION'].includes(el.tagName) && ownText(el).length > 1 && visible(el));
  const contrast = {total: 0, pass: 0, unknown: 0, fails: []}, seenC = new Set();
  const small = {total: 0, fails: []};
  for (const el of textEls) {
    const c = contrastOf(el);
    contrast.total++;
    if (c.unknown) { contrast.unknown++; continue; }
    if (c.pass) contrast.pass++;
    else { const k = c.fg + c.bg + c.size; if (!seenC.has(k) && contrast.fails.length < 15) { seenC.add(k); contrast.fails.push({text: ownText(el).slice(0, 60), sel: path(el), ratio: c.ratio, need: c.need, fg: c.fg, bg: c.bg, size: c.size + 'px'}); } }
  }
  for (const el of textEls) {
    const size = parseFloat(getComputedStyle(el).fontSize);
    small.total++;
    if (size < 12) { small.n = (small.n || 0) + 1; if (small.fails.length < 15) small.fails.push({text: ownText(el).slice(0, 60), sel: path(el), size: size + 'px'}); }
  }
  small.pass = small.total - (small.n || 0);

  // touch targets
  const tSel = 'a[href], button, input:not([type=hidden]), select, textarea, summary, [role=button], [role=link], [role=tab], [role=checkbox], [onclick]';
  const targets = {total: 0, pass24: 0, pass44: 0, fails24: [], fails44: []};
  for (const el of document.querySelectorAll(tSel)) {
    if (!visible(el)) continue;
    if (el.tagName === 'A' && el.parentElement && ownText(el.parentElement).length > 0) continue; // inline link in text: WCAG 2.5.8 exception
    const r = el.getBoundingClientRect(), w = Math.round(r.width), h = Math.round(r.height);
    targets.total++;
    const item = {text: (el.innerText || el.getAttribute('aria-label') || el.value || el.name || '').trim().slice(0, 40), sel: path(el), size: w + '×' + h};
    if (w >= 24 && h >= 24) targets.pass24++; else if (targets.fails24.length < 15) targets.fails24.push(item);
    if (w >= 44 && h >= 44) targets.pass44++; else if (targets.fails44.length < 15) targets.fails44.push(item);
  }

  // images and labels
  const imgs = [...document.querySelectorAll('img')].filter(visible);
  const alt = {total: imgs.length, pass: imgs.filter(i => i.hasAttribute('alt')).length, fails: imgs.filter(i => !i.hasAttribute('alt')).slice(0, 15).map(i => ({sel: path(i), src: (i.currentSrc || i.src).split('/').pop().slice(0, 60)}))};
  const fields = [...document.querySelectorAll('input:not([type=hidden]):not([type=submit]):not([type=button]):not([type=reset]):not([type=image]), select, textarea')].filter(visible);
  const named = el => el.getAttribute('aria-label') || el.getAttribute('aria-labelledby') || el.getAttribute('title') || (el.id && document.querySelector('label[for="' + CSS.escape(el.id) + '"]')) || el.closest('label');
  const labels = {total: fields.length, pass: fields.filter(named).length, fails: fields.filter(f => !named(f)).slice(0, 15).map(f => ({sel: path(f), type: f.type || f.tagName.toLowerCase(), placeholder: f.placeholder || ''}))};

  // requested elements
  const elements = {};
  for (const [name, sel] of Object.entries(sels)) {
    let list = [];
    try { list = [...document.querySelectorAll(sel)]; } catch (e) { elements[name] = {sel, error: String(e)}; continue; }
    const el = list.find(visible) || list[0];
    if (!el) { elements[name] = {sel, count: 0}; continue; }
    const cs = getComputedStyle(el);
    elements[name] = {sel, count: list.length, box: box(el), text: (el.innerText || '').trim().slice(0, 80),
      styles: {color: hex(parse(cs.color)), background: hex(parse(cs.backgroundColor)), effectiveBackground: hex(bgOf(el)), fontFamily: cs.fontFamily.split(',')[0].replace(/["']/g, ''), fontSize: cs.fontSize, fontWeight: cs.fontWeight, lineHeight: cs.lineHeight, letterSpacing: cs.letterSpacing,
        padding: cs.padding, margin: cs.margin, gap: cs.gap, borderRadius: cs.borderRadius, border: cs.borderTopWidth + ' ' + cs.borderTopStyle + ' ' + hex(parse(cs.borderTopColor)), boxShadow: cs.boxShadow, width: Math.round(el.getBoundingClientRect().width) + 'px', height: Math.round(el.getBoundingClientRect().height) + 'px', outline: cs.outlineStyle + ' ' + cs.outlineWidth},
      contrast: contrastOf(el)};
  }
  return {viewport: vw + 'x' + vh, shot: {w: W, h: H, full}, lang: document.documentElement.lang || '', title: document.title,
    hscroll: document.documentElement.scrollWidth > vw + 1 ? document.documentElement.scrollWidth : 0,
    checks: {contrast, targets, small, alt, labels}, elements};
}
"""


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
    agg = {}
    for vp, r in results.items():
        c = r["checks"]
        rows = [("Text contrast ≥ AA", c["contrast"]["pass"], c["contrast"]["total"] - c["contrast"]["unknown"], 100),
                ("Form fields with a label", c["labels"]["pass"], c["labels"]["total"], 100),
                ("Images with alt", c["alt"]["pass"], c["alt"]["total"], 100),
                ("Text ≥ 12 px", c["small"]["pass"], c["small"]["total"], 100)]
        if c.get("focus"):
            rows.append(("Visible keyboard focus", c["focus"]["pass"], c["focus"]["total"], 100))
        if r["touch"]:
            rows.insert(1, ("Touch targets ≥ 24 px", c["targets"]["pass24"], c["targets"]["total"], 100))
            rows.insert(2, ("Touch targets ≥ 44 px", c["targets"]["pass44"], c["targets"]["total"], 90))
        for l, v, b, t in rows:
            if b:
                agg.setdefault(l, []).append((vp, v, b, t))
    out = []
    for l, lst in agg.items():
        v, b = sum(x[1] for x in lst), sum(x[2] for x in lst)
        out.append({"l": l, "v": v, "b": b, "t": lst[0][3], "sub": ", ".join(x[0] for x in lst), "src": "inspect_ui.py"})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument("--name", default="page")
    ap.add_argument("--out", default="shots")
    ap.add_argument("--vp", action="append", help="NAME=WIDTHxHEIGHT; default desktop=1280x800 and phone=390x844")
    ap.add_argument("--sel", action="append", help="NAME=CSS selector to measure and box")
    ap.add_argument("--full", action="store_true", help="full-page screenshot (boxes relative to the whole page)")
    ap.add_argument("--dark", action="store_true", help="emulate prefers-color-scheme: dark")
    ap.add_argument("--wait", type=int, default=1200, help="ms to wait after load")
    ap.add_argument("--tabs", type=int, default=30, help="Tab presses for the keyboard focus check (desktop viewports)")
    ap.add_argument("--quality", type=int, default=72, help="JPEG quality")
    ap.add_argument("--browser", help="path to Chrome/Chromium if Playwright's own is not installed")
    a = ap.parse_args()

    vps = parse_pairs(a.vp or ["desktop=1280x800", "phone=390x844"], "vp")
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
            ctx = browser.new_context(viewport={"width": w, "height": h}, has_touch=touch,
                                      device_scale_factor=1, color_scheme="dark" if a.dark else "light")
            page = ctx.new_page()
            try:
                page.goto(url, wait_until="networkidle", timeout=45000)
            except Exception:
                page.goto(url, wait_until="load", timeout=45000)
            page.wait_for_timeout(a.wait)
            r = page.evaluate(PROBE, {"sels": sels, "full": a.full})
            r["checks"]["focus"] = None if touch else focus_walk(page, a.tabs)
            file = out / f"{a.name}-{name}.jpg"
            page.screenshot(path=str(file), type="jpeg", quality=a.quality, full_page=a.full)
            r.update(file=str(file), touch=touch)
            results[name] = r
            ctx.close()
        browser.close()

    report = {"url": a.url, "viewports": results, "suggested_checks": summary_checks(results)}
    jf = out / f"{a.name}-inspect.json"
    jf.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    for name, r in results.items():
        c = r["checks"]
        print(f"[{name} {r['viewport']}] {r['file']}  shot {r['shot']['w']}×{r['shot']['h']}" + ("  SIDEWAYS SCROLL " + str(r["hscroll"]) + "px" if r["hscroll"] else "") + ("" if r["lang"] else "  no <html lang>"))
        print(f"  contrast {c['contrast']['pass']}/{c['contrast']['total'] - c['contrast']['unknown']} pass (unknown {c['contrast']['unknown']})"
              + (f"; targets ≥24px {c['targets']['pass24']}/{c['targets']['total']}, ≥44px {c['targets']['pass44']}/{c['targets']['total']}" if r["touch"] else "")
              + (f"; focus visible {c['focus']['pass']}/{c['focus']['total']}" if c.get("focus") else "")
              + f"; labels {c['labels']['pass']}/{c['labels']['total']}; alt {c['alt']['pass']}/{c['alt']['total']}; text<12px {c['small']['total'] - c['small']['pass']}")
        for f in c["contrast"]["fails"][:5]:
            print(f"    contrast {f['ratio']}:1 (needs {f['need']}) {f['fg']} on {f['bg']} {f['size']} '{f['text']}' {f['sel']}")
        for k, e in r["elements"].items():
            if e.get("count"):
                b = e["box"]
                print(f"  {k}: x{b['x']} y{b['y']} w{b['w']} h{b['h']}%{'' if b['inView'] else ' (out of view)'}  {e['styles']['fontSize']} {e['styles']['color']} on {e['styles']['effectiveBackground']}  {e['styles']['width']}×{e['styles']['height']}  radius {e['styles']['borderRadius']}")
            else:
                print(f"  {k}: no match for {e.get('sel')}" + (f" ({e['error']})" if e.get("error") else ""))
    print(f"details: {jf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
