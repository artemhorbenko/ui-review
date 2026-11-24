#!/usr/bin/env python3
"""Render-check a ui-review report in a headless browser.

Usage:
    python check_report.py report.html [--out ./report-check] [--browser /path/to/chrome]

Opens the page as desktop (1280px), tablet (820px, touch) and phone (390px, touch),
runs the checks from SKILL.md step 5 (including screenshots, marks and the
plan's where/current-target blocks), saves screenshots and prints a summary.
Exit code 0 = all checks passed, 1 = something failed, 2 = could not run.

Needs: pip install playwright && playwright install chromium
(or pass --browser with the path to an installed Chrome/Chromium).
"""
import argparse
import asyncio
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

VIEWS = [
    ("desktop", dict(viewport={"width": 1280, "height": 900})),
    ("tablet", dict(viewport={"width": 820, "height": 1100}, is_mobile=True, has_touch=True)),
    ("phone", dict(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True, device_scale_factor=2)),
]

# Returns a dict of simple facts about the rendered page.
PROBE = """() => {
  const q = s => document.querySelector(s);
  const svgKids = s => { const e = q(s + ' svg'); return e ? e.childElementCount : 0; };
  const cells = [...document.querySelectorAll('#tbody td')];
  return {
    scrollWidth: document.documentElement.scrollWidth,
    width: innerWidth,
    radar: svgKids('#radar'),
    matrix: svgKids('#mx'),
    checkRows: document.querySelectorAll('#checks .step').length,
    shots: document.querySelectorAll('.shot').length,
    brokenImgs: [...document.querySelectorAll('.frame img')].filter(i => i.complete && !i.naturalWidth).length,
    marks: document.querySelectorAll('.mbox').length,
    marksOut: [...document.querySelectorAll('.mbox')].filter(m => { const f = m.closest('.frame').getBoundingClientRect(), r = m.getBoundingClientRect(); return r.left < f.left - 1 || r.top < f.top - 1 || r.right > f.right + 1 || r.bottom > f.bottom + 1 || r.width < 2 || r.height < 2; }).length,
    planWhere: document.querySelectorAll('#planList .where').length,
    ctBad: [...document.querySelectorAll('.ct td')].filter(td => !(td.children.length === 1 && td.firstElementChild.classList.contains('cv'))).length,
    kpis: [...document.querySelectorAll('#kpis .num')].filter(n => n.textContent.trim()).length,
    rows: document.querySelectorAll('#tbody tr').length,
    badCells: cells.filter(td => !(td.children.length === 1 && td.firstElementChild.classList.contains('cv'))).length,
    tableTerms: document.querySelectorAll('#tbody .t').length,
    terms: document.querySelectorAll('.t').length,
    overflows: [...document.querySelectorAll('.step .lab, .step .lab small, .kpi small, .kpi .num, .stop p, .stop h3, .card h3, .shot figcaption')].filter(e => e.offsetParent && e.scrollWidth > e.clientWidth + 2).length,
    overlaps: [...document.querySelectorAll('#checks .track, .kpi, .stop')].reduce((n, box) => {
      const kids = [...box.querySelectorAll('span, small, b, .note, .ndl')].filter(e => e.offsetParent && e.textContent.trim());
      for (let i = 0; i < kids.length; i++) for (let j = i + 1; j < kids.length; j++) {
        if (kids[i].contains(kids[j]) || kids[j].contains(kids[i])) continue;
        const a = kids[i].getBoundingClientRect(), b = kids[j].getBoundingClientRect();
        if (a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1) n++;
      }
      return n;
    }, 0),
  };
}"""

TIP_VISIBLE = "() => getComputedStyle(document.getElementById('tip') || document.body).display !== 'none' && !!document.getElementById('tip')"


def script_check(html: str) -> str | None:
    """Return an error string if the last <script> does not parse (needs node)."""
    node = shutil.which("node")
    if not node or "<script>" not in html:
        return None
    src = html[html.rindex("<script>") + 8: html.rindex("</script>")]
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(src)
    r = subprocess.run([node, "--check", f.name], capture_output=True, text=True)
    return None if r.returncode == 0 else r.stderr.strip().splitlines()[-1]


async def check_view(browser, url, name, ctx_args, out):
    fails, notes = [], []
    ctx = await browser.new_context(**ctx_args)
    page = await ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    page.on("console", lambda m: errors.append(f"console: {m.text}") if m.type == "error" else None)
    await page.goto(url)
    await page.wait_for_timeout(1500)
    await page.evaluate("() => Promise.all([...document.images].map(i => { i.loading = 'eager'; return i.complete ? 0 : new Promise(r => { i.onload = i.onerror = r; setTimeout(r, 3000); }); }))")
    p = await page.evaluate(PROBE)

    if p["scrollWidth"] > p["width"] + 1:
        fails.append(f"sideways scroll: page is {p['scrollWidth']}px wide in a {p['width']}px viewport")
    for key, label in [("radar", "radar chart"), ("matrix", "impact-effort matrix")]:
        if not p[key]:
            fails.append(f"{label} is empty")
    if not p["checkRows"]:
        fails.append("checks / funnel block is empty")
    if p["brokenImgs"]:
        fails.append(f"{p['brokenImgs']} screenshots did not load (check shots[].src)")
    if p["marksOut"]:
        fails.append(f"{p['marksOut']} marks fall outside their screenshot or have no size")
    if p["shots"] and not p["marks"]:
        notes.append("screenshots have no marks")
    if p["ctBad"]:
        fails.append(f"{p['ctBad']} current-target cells are not wrapped in one .cv")
    if not p["planWhere"]:
        fails.append("no 'where' block in the plan: tasks need page, viewport and selector")
    if not p["kpis"]:
        fails.append("KPI row has no numbers")
    if not p["rows"]:
        fails.append("opportunities table is empty")
    if p["badCells"]:
        fails.append(f"{p['badCells']} table cells are not wrapped in one .cv (breaks the phone layout)")
    if p["overflows"]:
        fails.append(f"{p['overflows']} labels overflow their box (text runs into the next column)")
    if p["overlaps"]:
        fails.append(f"{p['overlaps']} overlapping text labels in the funnel, KPIs or journey")
    if not p["terms"]:
        notes.append("no tooltip terms found (.t)")

    await page.screenshot(path=str(out / f"{name}-top.png"))

    # Tooltip: hover on desktop, tap (and second tap closes) on touch.
    term = await page.query_selector("#ops .t") or await page.query_selector(".t")
    if term:
        await term.scroll_into_view_if_needed()
        await page.wait_for_timeout(200)
        if name == "desktop":
            await term.hover()
        else:
            await term.tap()
        await page.wait_for_timeout(250)
        if not await page.evaluate(TIP_VISIBLE):
            fails.append("tooltip does not open on " + ("hover" if name == "desktop" else "tap"))
        else:
            await page.screenshot(path=str(out / f"{name}-tooltip.png"))
            if name != "desktop":
                await term.tap()
                await page.wait_for_timeout(250)
                if await page.evaluate(TIP_VISIBLE):
                    fails.append("tooltip does not close on a second tap")

    # Filters: each chip re-renders the table; cells and tooltips must survive.
    chips = await page.query_selector_all("#ops .chip[data-f]")
    for chip in chips:
        f = await chip.get_attribute("data-f")
        await chip.click()
        await page.wait_for_timeout(200)
        p2 = await page.evaluate(PROBE)
        if p2["rows"] == 0 and f == "all":
            fails.append("filter 'all' leaves the table empty")
        if p2["badCells"]:
            fails.append(f"after filter '{f}' table cells lose their .cv wrapper")
        if p["tableTerms"] and p2["rows"] and p2["tableTerms"] == 0 and f == "all":
            fails.append("tooltips disappear from the table after filtering")
    if chips:
        await chips[0].click()
        await page.wait_for_timeout(200)

    # A mark links to its plan entry and opens it.
    mark = await page.query_selector(".mbox")
    if mark:
        href = await mark.get_attribute("href")
        await mark.scroll_into_view_if_needed()
        await mark.click()
        await page.wait_for_timeout(300)
        if not await page.evaluate(f"() => !!document.querySelector('{href}') && document.querySelector('{href}').open"):
            fails.append(f"clicking mark {href} does not open its plan entry")

    for sel, label in [("#shots", "shots"), ("#ops", "table"), ("#plan", "plan")]:
        if await page.query_selector(sel):
            await page.evaluate(f"document.querySelector('{sel}').scrollIntoView()")
            await page.wait_for_timeout(200)
            await page.screenshot(path=str(out / f"{name}-{label}.png"))

    if name == "phone":
        await page.emulate_media(color_scheme="dark")
        await page.evaluate("scrollTo(0,0)")
        await page.wait_for_timeout(300)
        await page.screenshot(path=str(out / "phone-dark.png"))

    fails += errors
    await ctx.close()
    return {"view": name, "ok": not fails, "fails": fails, "notes": notes, "facts": p}


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--out", default="report-check")
    ap.add_argument("--browser", help="path to Chrome/Chromium if Playwright's own is not installed")
    a = ap.parse_args()

    path = pathlib.Path(a.report).resolve()
    if not path.exists():
        print(f"not found: {path}")
        return 2
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    results = []
    err = script_check(path.read_text(encoding="utf-8"))
    if err:
        results.append({"view": "script", "ok": False, "fails": [f"script does not parse: {err}"]})

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("playwright is not installed: pip install playwright && playwright install chromium")
        return 2

    async with async_playwright() as pw:
        launch = {"args": ["--no-sandbox"]}
        exe = a.browser or next((shutil.which(b) for b in ("google-chrome", "chromium", "chromium-browser") if shutil.which(b)), None)
        try:
            browser = await pw.chromium.launch(**launch)
        except Exception:
            if not exe:
                print("no browser: run `playwright install chromium` or pass --browser")
                return 2
            browser = await pw.chromium.launch(executable_path=exe, **launch)
        for name, ctx_args in VIEWS:
            results.append(await check_view(browser, path.as_uri(), name, ctx_args, out))
        await browser.close()

    ok = all(r["ok"] for r in results)
    for r in results:
        status = "PASS" if r["ok"] else "FAIL"
        print(f"[{status}] {r['view']}")
        for f in r.get("fails", []):
            print(f"   - {f}")
        for n in r.get("notes", []):
            print(f"   note: {n}")
    print(f"screenshots: {out.resolve()}")
    (out / "result.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
