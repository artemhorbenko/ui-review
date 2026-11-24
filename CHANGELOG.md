# Changelog

## 1.0.0 - 2026-11-24

First public release. Built on the approach of [product-lens-audit](https://github.com/artemhorbenko/product-lens-audit) 1.3.0: one `audit.json`, two outputs.

- 12 UI lenses in 5 groups (look, use, reach, words, system), Nielsen severity 1-4, UI maturity strip (Broken → Delightful).
- Process: sources check (ok / demo / no) → up to 4 skippable questions → gather at desktop and phone width → findings labelled observed or hypothesis with annotated screenshots → severity and ICE → top 3 with alternatives, success threshold and pre-mortem → report and hands-off file → render check.
- `scripts/inspect_ui.py` (Playwright): screenshots per viewport, element boxes as % of the screenshot (for marks), computed styles (for current values), and automatic checks: WCAG AA text contrast, labelled form fields, visible keyboard focus (Tab walk), tap targets ≥ 24 / 44 px, text < 12 px, images without alt, sideways scroll, missing `lang`. Prints a ready `checks` array.
- Report template (same design as product-lens-audit): measured checks against targets, annotated screenshots with numbered marks that link to their fix, screen route, issues table with severity and a "severe" filter, plan entries with **Where** and a **Current → target** table with colour swatches and tokens, design tokens in the data block. Screenshots are embedded by `build_report.py`; without them the marks are drawn on a placeholder frame.
- `scripts/validate_audit.py`: every issue needs evidence and a `where` (page or URL, viewport, selector or shot); marks must point at real issues and stay inside the image; numbers need sources; the top 3 need alternatives and a pre-mortem.
- `scripts/build_handoff.py`: `handoff.md` + `tasks.json` with design tokens, screenshot list, rules for the implementer, and per task: where, current → target, steps, acceptance criteria (generated from the change list when not given), how to verify; ordered by ICE, dependencies first.
- `scripts/check_report.py`: also fails on broken screenshots, marks outside their image, missing where blocks, unwrapped current-target cells, and a mark that does not open its plan entry.
- Demo: fictional "Tallyo" pages with deliberate problems (`evals/fixtures/demo-site/`), real screenshots and measurements, examples in Ukrainian and English, hands-off example.
- `ui-review-skill.zip` in the repo root for uploading to the Claude app (rebuild it whenever the skill folder changes).
