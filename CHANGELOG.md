# Changelog

## 1.1.0 - 2026-11-24

Scope and evidence reworked to match the spec: UI only, measured at three widths.

- **13 UI lenses in 5 groups** replace the 12 mixed ones: visual hierarchy, CTA prominence, imagery and icons (look); layout and grid, spacing rhythm, typography scale (structure); colour and contrast, dark mode, brand coherence (colour); design-system consistency (system); responsive behaviour, motion, perceived performance (behave). Forms, navigation, microcopy and heuristics moved out to ux-review; out-of-scope observations get one line with a pointer.
- **Three widths, always:** 360, 768 and 1280 px. `validate_audit.py` warns when a width is missing.
- **`scripts/probe.js`**, one measuring probe for Playwright and for browser tools: computed styles and boxes, contrast over the whole page (paint-stack background, so overlays and pseudo-elements count), type / colour / radius / spacing scale, tap targets, icon-only links without a name, `prefers-color-scheme` and `prefers-reduced-motion` rules, running and infinite animations, CLS and LCP, fixed bars as a share of the screen.
- **`inspect_ui.py`** now runs the probe at 360/768/1280, emulates dark mode (saves a -dark screenshot when the page changes) and reduced motion, and keeps the Tab walk for visible focus.
- **Browser-only path documented:** exact widths via a same-origin iframe when the window cannot be resized.
- **Fact check** is the last step of the process, after the render check.
- Report: new lens icons and groups; a large mark no longer blocks clicks on smaller marks inside it (badges are the click targets, smaller boxes sit on top); `check_report.py` clicks the badge.
- New demo: the Tallyo fixture gained a late promo bar (layout shift), an infinite pulse that ignores reduced motion and mixed icon styles; English example audit, hands-off and screenshots at three widths. The Ukrainian example was dropped; the Ukrainian interface labels stay.

## 1.0.0 - 2026-11-24

First public release: 12 UI lenses, annotated screenshots, `inspect_ui.py`, report and hands-off from one `audit.json`, same design and process as product-lens-audit 1.3.0.
