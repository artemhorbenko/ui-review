# Hands-off: UI review: Tallyo (demo)

Implementation brief generated from the UI review. Work top to bottom: tasks are ordered by ICE, and a task always comes after the ones it depends on. Each task says where the change happens (page, viewport, selector, screenshot mark) and what the values are now and should become. Treat "hypothesis" tasks as experiments: test before building fully.

## Context

- **Main finding:** Keyboard focus is invisible on all 32 controls, and the phone page scrolls sideways
- The landing page looks tidy at 1280 px but breaks down at the edges: focus rings are removed, grey text fails contrast, a late promo bar shifts the page, and below 1280 the feature strip pushes the page to 1,096 px wide. Most fixes are one-line CSS changes.
- **UI maturity:** Usable. Usable at 1280 for a mouse user. Not yet Consistent: four button shapes, eleven font sizes, eleven off-scale spacing values, and the layout breaks at 768 and 360.
- **Confidence:** 65%

### Owner answers and assumptions

- Which pages matter most? (skipped): Skipped. Assumption: home and pricing
- Devices / dark mode (skipped): Skipped. Assumption: phone and desktop equally; no dark mode
- Design system and brand (skipped): Skipped. Assumption: infer tokens from CSS; brand blue #3156d3
- What is already known (skipped): Skipped. Assumption: nothing

### Sources

- [ok] inspect_ui.py — home at 3 widths, pricing at 1280
- [ok] Page CSS and DOM — read
- [demo] Design tokens — inferred from CSS
- [no] Behaviour analytics — not connected

Missing, so lower confidence: Behaviour analytics.

### Design tokens

| Token | Value | Use |
|---|---|---|
| `color.primary` | `#3156d3` | buttons, links, focus ring |
| `color.text` | `#1d2433` | headings, body |
| `color.text-muted` | `#6b7280` | secondary text (proposed, 4.83:1) |
| `color.surface` | `#f6f7fb` | cards |
| `radius.md` | `8px` | buttons, inputs (proposed) |
| `space.*` | `4 / 8 / 12 / 16 / 24 / 40px` | padding, gaps (proposed) |
| `font.size.*` | `12 / 14 / 16 / 20 / 28 / 44px` | type scale (proposed) |

### Screenshots

- `home-1280` — Home · 1280×800 · index.html · `demo/home-1280.jpg` · marks: 2, 3, 1, 7, 9, 16
- `home-768` — Home · 768×1024 · index.html · `demo/home-768.jpg` · marks: 4, 12, 10, 10
- `home-360` — Home · 360×780 · index.html · `demo/home-360.jpg` · marks: 5, 3, 13, 6, 14
- `pricing-1280` — Pricing · 1280×800 · pricing.html · `demo/pricing-1280.jpg` · marks: 11, 2, 8, 10

## Rules for the implementer

- Use the design tokens listed here; do not hard-code new colours, sizes or spacing values.
- Change only the elements named under Where; check that the same component elsewhere does not break.
- Verify at every viewport listed (1280×800, 768×1024 and 360×780 unless stated) and in dark mode if the product has one.
- Keep text contrast ≥ 4.5:1 (large text ≥ 3:1), touch targets ≥ 24×24 px (aim for 44×44), visible focus on every control.
- Do not submit real forms, payments or messages while testing.
- Record before/after screenshots and measured values for each task.
- When a task is a hypothesis, run the cheapest test first and stop if the threshold is not met.

## Suggested order

| # | ID | Task | Severity | ICE | Type | Evidence |
|---|---|---|---|---|---|---|
| 1 | T01 | Bring back the keyboard focus ring (0 of 32 stops show focus) (top 3) | 4 critical | 648 | fix | observed |
| 2 | T02 | Raise grey text to AA: 16 of 39 text elements fail at 1280 (top 3) | 3 major | 576 | fix | observed |
| 3 | T04 | Stop the sideways scroll below 1280: the feature strip makes the page 1,096–1,117 px wide (top 3) | 3 major | 567 | fix | observed |
| 4 | T05 | Reserve space for the promo bar: it lands at ≈ 750 ms and shifts the page (CLS 0.137 at 360) | 3 major | 432 | fix | observed |
| 5 | T03 | One primary action: the pulsing orange “Book a demo” outweighs “Get started free” | 3 major | 392 | fix | observed |
| 6 | T06 | Respect reduced motion: the demo button pulses forever, even with reduce set | 2 minor | 324 | fix | observed |
| 7 | T07 | Use one icon style: outline, filled and emoji icons sit side by side | 2 minor | 288 | fix | observed |
| 8 | T13 | Enlarge phone tap targets: 9 of 17 are under 24 px, the menu button is 32 px | 2 minor | 288 | fix | observed |
| 9 | T12 | Give 768 px its own layout: the hero keeps two columns and the H1 runs to 4 lines | 2 minor | 280 | fix | observed |
| 10 | T10 | One button shape instead of four radii (4, 6, 12, 999 px) | 2 minor | 252 | fix | observed |
| 11 | T11 | Bring the oranges back into the palette (#e8572a, #d2471d are not brand colours) | 2 minor | 196 | fix | observed |
| 12 | T08 | Cut the type scale from 11 sizes to 6 and lift text under 12 px | 2 minor | 192 | fix | observed |
| 13 | T14 | Show a 2-line max on the hero subtitle at 360 (5 lines now) | 1 cosmetic | 168 | fix | observed |
| 14 | T09 | Put spacing on a 4 px scale (11 of 18 values are off it) | 1 cosmetic | 144 | fix | observed |
| 15 | T16 | Test a single-column hero: one CTA, sign-up card below | 2 minor | 120 | rethink | hypothesis |
| 16 | T15 | Decide on dark mode: none today, light colours are hard-coded | 1 cosmetic | 36 | rethink | hypothesis |

## Tasks

### 1. T01 — Bring back the keyboard focus ring (0 of 32 stops show focus)

- Lens: Colour and contrast · Severity: 4 critical · ICE 648 = 8×9×9 · Type: fix · observed
- Effort: ≈15 minutes

**Evidence.** style.css has \*:focus { outline: none } and nothing in its place. A Tab walk at 1280 found 0 of 23 stops on home and 0 of 9 on pricing with any visible change (WCAG 2.4.7). Keyboard users cannot see where they are.

**Hypothesis.** If focus is visible again, keyboard users can see where they are and finish sign-up, because every control shows a ring when tabbed to.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| All pages · style.css | all | `*:focus` | home-1280 (demo/home-1280.jpg), mark 1 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `outline on :focus-visible` | none | 2px solid #3156d3, offset 2px | `color.primary` |

**Steps:**

1. Delete \*:focus { outline: none }.
2. Add :focus-visible { outline: 2px solid var(--color-primary); outline-offset: 2px }.
3. Rerun inspect_ui.py: focus visible must be 23 of 23 and 9 of 9.

**Acceptance criteria:**

- [ ] outline on :focus-visible is 2px solid #3156d3, offset 2px (color.primary) at every viewport
- [ ] 32 of 32 stops show focus
- [ ] Metric: Keyboard stops with a visible focus: 32 of 32 (now 0)

**How to verify:** Delete one CSS rule, add :focus-visible, rerun inspect_ui.py (≈15 min)

**Risk / guardrail:** Mouse users see no ring with :focus-visible, so their view does not change.

**Alternatives rejected:**

- Box-shadow ring: also valid; outline chosen because it survives Windows high-contrast mode.
- Underline links on focus only: not enough for buttons and inputs.

**Pre-mortem:** It shipped and focus was still invisible on the blue Submit button, because the ring was the same blue. Use outline-offset so the ring sits on the white around it.


### 2. T02 — Raise grey text to AA: 16 of 39 text elements fail at 1280

- Lens: Colour and contrast · Severity: 3 major · ICE 576 = 8×9×8 · Type: fix · observed
- Effort: ≈1 hour

**Evidence.** 16 of 39 text elements at 1280 fail WCAG AA (1.4.3): the hero subtitle #a3a9b4 on white = 2.36:1, “No card needed” and the feature strip #8d94a1 = 3.05:1, the Terms links #a3a9b4 on #f6f7fb = 2.21:1, footer links 2.36:1. On pricing “/mo per seat” is 2.36:1 and the VAT note #b8bec9 is 1.87:1.

**Hypothesis.** If secondary text uses #6b7280 instead of the three pale greys, the subtitle and small print become readable for low-vision visitors and in sunlight.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home · index.html | all | `.sub, .proof, .strip span, .terms a, footer a` | home-1280 (demo/home-1280.jpg), mark 2 |
| Pricing · pricing.html | all | `.price small, .vat` | pricing-1280 (demo/pricing-1280.jpg), mark 2 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `color (.sub, .terms a, footer a, .price small)` | #a3a9b4 (2.36:1) | #6b7280 (4.83:1) | `color.text-muted` |
| `color (.proof, .strip)` | #8d94a1 (3.05:1) | #6b7280 | `color.text-muted` |
| `color (.vat)` | #b8bec9 (1.87:1) | #6b7280 | `color.text-muted` |

**Steps:**

1. Add --color-text-muted: #6b7280.
2. Replace #a3a9b4, #8d94a1 and #b8bec9 for text with it; keep pale greys for borders only.
3. Rerun inspect_ui.py at 3 widths; only the demo button (#3) may still fail.

**Acceptance criteria:**

- [ ] color (.sub, .terms a, footer a, .price small) is #6b7280 (4.83:1) (color.text-muted) at every viewport
- [ ] color (.proof, .strip) is #6b7280 (color.text-muted) at every viewport
- [ ] color (.vat) is #6b7280 (color.text-muted) at every viewport
- [ ] 0 text elements below AA on the 4 screenshots
- [ ] Metric: Text passing AA at 1280: 39 of 39 (now 23)

**How to verify:** Swap the greys in style.css and rerun inspect_ui.py at 3 widths

**Risk / guardrail:** Heavier look; keep hierarchy with size and weight, not paler grey.

**Alternatives rejected:**

- Darken only the subtitle: leaves 15 failures.
- A darker #5d6472 (5.95:1): kept in reserve for new surfaces.

**Pre-mortem:** The check still failed because greys were hard-coded in six places and two were missed. Search style.css for every hex value first.


### 3. T04 — Stop the sideways scroll below 1280: the feature strip makes the page 1,096–1,117 px wide

- Lens: Responsive · Severity: 3 major · ICE 567 = 7×9×9 · Type: fix · observed
- Effort: ≈20 minutes

**Evidence.** The feature strip is five 200 px items in a non-wrapping flex row with overflow: visible. At 768 the page becomes 1,117 px wide and at 360 1,096 px; the browser offers sideways scroll and phones may zoom the page out (WCAG 1.4.10 Reflow).

**Hypothesis.** If the strip wraps instead of overflowing, phones and tablets stop scrolling sideways and the browser stops zooming the page out.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home, feature strip · index.html | 768, 360 | `.strip` | home-768 (demo/home-768.jpg), mark 4 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `document width` | 1,117px at 768; 1,096px at 360 | equal to the viewport | — |
| `.strip / .strip span` | no wrap; span width 200px, flex none | flex-wrap: wrap; gap 8px 16px; span width auto | — |

**Steps:**

1. Set .strip { flex-wrap: wrap; gap: 8px 16px } and drop the fixed width on .strip span.
2. Rerun inspect_ui.py at 360, 768 and 1280: no SIDEWAYS SCROLL line.

**Acceptance criteria:**

- [ ] document width is equal to the viewport at 768, 360
- [ ] .strip / .strip span is flex-wrap: wrap; gap 8px 16px; span width auto at 768, 360
- [ ] No sideways scroll at 360, 390, 768 and 820
- [ ] Metric: Page width equals viewport at 360 and 768

**How to verify:** Add flex-wrap to .strip and rerun inspect_ui.py at 360/768

**Risk / guardrail:** The strip becomes 2–3 lines on phones.

**Alternatives rejected:**

- Hide the strip below 768: loses content.
- Horizontal scroller with snap: fine, but a hidden overflow on a key selling point.

**Pre-mortem:** The strip was fixed but the 5-item nav overflowed at 768 next. Rerun the check at every width, not only the one in the ticket.


### 4. T05 — Reserve space for the promo bar: it lands at ≈ 750 ms and shifts the page (CLS 0.137 at 360)

- Lens: Perceived performance · Severity: 3 major · ICE 432 = 6×9×8 · Type: fix · observed
- Effort: ≈30 minutes

**Evidence.** A promo bar (“New: recurring invoices for retainers”) is inserted by script ≈ 750 ms after load at the top of the page, 88 px tall (107 px at 360). Everything below jumps down: CLS 0.068 at 1280, 0.085 at 768 and 0.137 at 360 (above the 0.1 limit). The shifted nodes are main, header.top and the sign-up button.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home · index.html | all | `.promo (inserted by the inline script)` | home-360 (demo/home-360.jpg), mark 5 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `promo bar` | inserted at ≈ 750 ms, pushes content | rendered in the HTML, or a reserved 88px slot (min-height) from first paint | — |
| `CLS at 360` | 0.137 | ≤ 0.1 | — |

**Steps:**

1. Render the promo in the HTML, or reserve its height with a placeholder of the same size.
2. Rerun inspect_ui.py: CLS ≤ 0.1 at all widths.

**Acceptance criteria:**

- [ ] promo bar is rendered in the HTML, or a reserved 88px slot (min-height) from first paint at every viewport
- [ ] CLS at 360 is ≤ 0.1 at every viewport
- [ ] Metric: CLS ≤ 0.1 at 360, 768, 1280

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** None.


### 5. T03 — One primary action: the pulsing orange “Book a demo” outweighs “Get started free”

- Lens: CTA prominence · Severity: 3 major · ICE 392 = 7×7×8 · Type: fix · observed
- Effort: ≈1 hour

**Evidence.** Two filled buttons of the same size sit side by side - “Get started free” (#3156d3, 180×46) and “Book a demo” (#e8572a, 153×46) - and the sign-up card adds a third filled “Submit”. The orange one wins the eye: it is the only warm colour on the page and it pulses (#6). Its white text is 3.6:1. At 360 the two stack and the form drops below the fold.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home, hero · index.html | all | `.ctas .btn-demo` | home-1280 (demo/home-1280.jpg), mark 3 |
| Home, hero · index.html | 360 | `.ctas` | home-360 (demo/home-360.jpg), mark 3 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `background (.btn-demo)` | #e8572a | transparent | — |
| `color / border (.btn-demo)` | #ffffff on #e8572a (3.6:1) | #3156d3 text, 1px #3156d3 border (6.17:1) | `color.primary` |

**Steps:**

1. Make “Book a demo” a secondary outline button.
2. Keep “Get started free” as the only filled button in the hero.
3. 5-second test with 5 people: what would you click first?

**Acceptance criteria:**

- [ ] background (.btn-demo) is transparent at every viewport, 360
- [ ] color / border (.btn-demo) is #3156d3 text, 1px #3156d3 border (6.17:1) (color.primary) at every viewport, 360
- [ ] Metric: First clicks on the primary action (5-second / first-click test)

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** Demo requests may drop; watch them for 2 weeks.


### 6. T06 — Respect reduced motion: the demo button pulses forever, even with reduce set

- Lens: Motion · Severity: 2 minor · ICE 324 = 4×9×9 · Type: fix · observed
- Effort: ≈10 minutes
- Depends on: T03

**Evidence.** “Book a demo” runs an infinite 1.6 s box-shadow pulse. There are no prefers-reduced-motion rules, and with reduce emulated the animation still runs (1 running animation).

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home, hero · index.html | all | `.btn-demo` | home-360 (demo/home-360.jpg), mark 6 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `animation (.btn-demo)` | pulse 1.6s infinite | none, or 2 iterations and none under prefers-reduced-motion: reduce | — |

**Steps:**

1. Remove the infinite pulse, or limit it to 2 runs.
2. Add @media (prefers-reduced-motion: reduce) { \* { animation: none !important; transition: none !important } } as a safety net.

**Acceptance criteria:**

- [ ] animation (.btn-demo) is none, or 2 iterations and none under prefers-reduced-motion: reduce at every viewport
- [ ] Metric: 0 running animations with reduced motion

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** None.


### 7. T07 — Use one icon style: outline, filled and emoji icons sit side by side

- Lens: Imagery and icons · Severity: 2 minor · ICE 288 = 4×9×8 · Type: fix · observed
- Effort: ≈1 hour

**Evidence.** The three feature icons mix styles: an outline clock (1.6 stroke), a filled bell and a 📋 emoji. The feature strip uses ★ characters and pricing a 🔥 emoji. Four icon languages on two pages.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home, features · index.html | all | `.ficon` | home-1280 (demo/home-1280.jpg), mark 7 |
| Pricing · pricing.html | all | `#timer` | — |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `icon style` | outline + filled + emoji | one outline set, 24px, 1.6 stroke, color.primary | — |

**Steps:**

1. Pick one outline icon set (the clock already matches).
2. Replace the bell, the emoji and the ★ characters with icons from that set.

**Acceptance criteria:**

- [ ] icon style is one outline set, 24px, 1.6 stroke, color.primary at every viewport
- [ ] Metric: Icon styles in use: 1

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** None.


### 8. T13 — Enlarge phone tap targets: 9 of 17 are under 24 px, the menu button is 32 px

- Lens: Responsive · Severity: 2 minor · ICE 288 = 4×9×8 · Type: fix · observed
- Effort: ≈30 minutes

**Evidence.** At 360, 9 of 17 tap targets are under 24 px (WCAG 2.5.8): four social links 18×18 and five footer links 14 px high. The menu button is 32×32; only 2 of 17 reach 44×44.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home · index.html | 360 | `.social a, footer a, .burger` | home-360 (demo/home-360.jpg), mark 13 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `size (.social a, .burger)` | 18×18 / 32×32px | 44×44px | — |
| `footer a height` | 14px | ≥ 24px | — |

**Steps:**

1. Make .social a and .burger 44×44 with the icon centred.
2. Pad footer links to 24 px tall.

**Acceptance criteria:**

- [ ] size (.social a, .burger) is 44×44px at 360
- [ ] footer a height is ≥ 24px at 360
- [ ] Metric: Tap targets ≥ 24 px at 360: 17 of 17

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** Footer grows ≈ 30 px.


### 9. T12 — Give 768 px its own layout: the hero keeps two columns and the H1 runs to 4 lines

- Lens: Layout and grid · Severity: 2 minor · ICE 280 = 5×8×7 · Type: fix · observed
- Effort: ≈1 hour

**Evidence.** At 768 the hero keeps the desktop two-column layout (the breakpoint is 700 px): the 46 px H1 wraps to 4 lines in a 352 px column (199 px tall) while the card sits beside it. The nav shows all 5 items.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home · index.html | 768 | `.hero, .hero h1` | home-768 (demo/home-768.jpg), mark 12 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `hero layout at 701–1024px` | two columns, H1 46px | one column, H1 36px | — |

**Steps:**

1. Move the single-column breakpoint to 1024 px, or scale the H1 with clamp(32px, 5vw, 46px).
2. Check 768 and 820.

**Acceptance criteria:**

- [ ] hero layout at 701–1024px is one column, H1 36px at 768
- [ ] Metric: H1 ≤ 3 lines at 768

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** None.


### 10. T10 — One button shape instead of four radii (4, 6, 12, 999 px)

- Lens: Design system · Severity: 2 minor · ICE 252 = 4×9×7 · Type: fix · observed
- Effort: ≈30 minutes

**Evidence.** Buttons use four corner radii: 12 px (Get started), 999 px (Book a demo), 4 px (Submit, Log in) and 6 px (pricing Choose). Four shapes read as four components.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home + pricing · index.html, pricing.html | all | `.btn, .menu .login` | home-768 (demo/home-768.jpg), mark 10 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `border-radius (buttons)` | 4 / 6 / 12 / 999px | 8px | `radius.md` |

**Steps:**

1. Add radius.md (8px) and use it on every button.
2. Remove per-button overrides.

**Acceptance criteria:**

- [ ] border-radius (buttons) is 8px (radius.md) at every viewport
- [ ] Metric: Button radii in use: 1

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** None.


### 11. T11 — Bring the oranges back into the palette (#e8572a, #d2471d are not brand colours)

- Lens: Brand coherence · Severity: 2 minor · ICE 196 = 4×7×7 · Type: fix · observed
- Effort: ≈1 hour
- Depends on: T02

**Evidence.** The brand palette is blue (#3156d3) and navy (#1d2433), yet two unrelated oranges appear: the demo button #e8572a and the pricing countdown #d2471d on #fff1ec (4.09:1). Five greys are used for text.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Pricing · pricing.html | all | `#timer` | pricing-1280 (demo/pricing-1280.jpg), mark 11 |
| Home · index.html | all | `.btn-demo` | — |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `accent colours` | #e8572a, #d2471d | brand blue for actions; one warning colour token if needed | `color.primary` |
| `text greys` | 5 (#4a5263 #6b7280 #8d94a1 #a3a9b4 #b8bec9) | 2 (color.text, color.text-muted) | — |

**Steps:**

1. Replace the oranges with brand colours (see #3).
2. Merge the text greys into two tokens (see #2).

**Acceptance criteria:**

- [ ] accent colours is brand blue for actions; one warning colour token if needed (color.primary) at every viewport
- [ ] text greys is 2 (color.text, color.text-muted) at every viewport
- [ ] Metric: Off-palette colours: 0

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** None.


### 12. T08 — Cut the type scale from 11 sizes to 6 and lift text under 12 px

- Lens: Typography scale · Severity: 2 minor · ICE 192 = 4×8×6 · Type: fix · observed
- Effort: ≈2 hours

**Evidence.** Eleven distinct font sizes on home (10, 11, 12, 13, 14, 15, 17, 20, 22, 28, 46 px), with 13 and 14 px used side by side for similar text. 8 text elements per width are under 12 px (social labels 10 px, footer links 11 px); body text is 14 px with line-height 1.3.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home, pricing · index.html | all | `body, footer, .social a, .vat` | pricing-1280 (demo/pricing-1280.jpg), mark 8 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `font sizes` | 11 sizes, 10–46px | 6 steps: 12 / 14 / 16 / 20 / 28 / 44px | `font.size.*` |
| `body` | 14px / 1.3 | 16px / 1.5 | `font.size.md` |
| `footer, .vat, .social a` | 10–11px | 12px minimum | — |

**Steps:**

1. Define 6 size tokens and map every font-size to the nearest.
2. Set body to 16px/1.5.

**Acceptance criteria:**

- [ ] font sizes is 6 steps: 12 / 14 / 16 / 20 / 28 / 44px (font.size.\*) at every viewport
- [ ] body of `body, footer, .social a, .vat` is 16px / 1.5 (font.size.md) at every viewport
- [ ] footer, .vat, .social a is 12px minimum at every viewport
- [ ] Metric: Distinct font sizes ≤ 6; text under 12 px: 0

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** Longer page on phones.


### 13. T14 — Show a 2-line max on the hero subtitle at 360 (5 lines now)

- Lens: Visual hierarchy · Severity: 1 cosmetic · ICE 168 = 3×7×8 · Type: fix · observed
- Effort: ≈30 minutes

**Evidence.** At 360 the hero subtitle runs 5 lines (123 px) in pale grey between the H1 and the buttons, pushing the primary button to 60% of the screen.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home · index.html | 360 | `.sub` | home-360 (demo/home-360.jpg), mark 14 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `subtitle length at 360` | 5 lines | ≤ 3 lines (shorter copy or 15px) | — |

**Steps:**

1. Shorten the subtitle on small screens or drop it to 15 px.
2. Check the primary button lands in the top half at 360.

**Acceptance criteria:**

- [ ] subtitle length at 360 is ≤ 3 lines (shorter copy or 15px) at 360
- [ ] Metric: Primary button within the top 55% at 360

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** Copy change: agree with whoever owns the text.


### 14. T09 — Put spacing on a 4 px scale (11 of 18 values are off it)

- Lens: Spacing rhythm · Severity: 1 cosmetic · ICE 144 = 3×8×6 · Type: fix · observed
- Effort: ≈2 hours
- Depends on: T10

**Evidence.** Paddings, margins and gaps take 18 distinct values; 11 are off a 4 px scale: 6, 7, 10, 11, 13, 14, 18, 22, 26, 34, 37 px (e.g. header 13px 37px, card 26px 22px, strip 18px 37px).

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home · index.html | all | `.top, .card, .strip, .features` | home-1280 (demo/home-1280.jpg), mark 9 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `spacing values` | 11 of 18 off-scale | 4 / 8 / 12 / 16 / 24 / 40px | `space.*` |

**Steps:**

1. Add spacing tokens.
2. Replace off-scale values; one page padding (40px at 1280, 16px at 360).

**Acceptance criteria:**

- [ ] spacing values is 4 / 8 / 12 / 16 / 24 / 40px (space.\*) at every viewport
- [ ] Metric: Off-scale spacing values: 0

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** Small shifts; compare screenshots.


### 15. T16 — Test a single-column hero: one CTA, sign-up card below

- Lens: Visual hierarchy · Severity: 2 minor · ICE 120 = 6×4×5 · Type: rethink · hypothesis
- Effort: ≈2 days
- Depends on: T03

**Evidence.** The hero offers three ways in (two buttons and a form). A single-column hero with one CTA and the sign-up card below might lift starts; there is no behaviour data, so this is a hypothesis.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home · index.html | all | `.hero` | home-1280 (demo/home-1280.jpg), mark 16 |

**Steps:**

1. Add click tracking on the three entry points.
2. Run an A/B test for 2 weeks: current vs single-column hero.

**Acceptance criteria:**

- [ ] Metric: Sign-up starts per 100 visits

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** Card below the fold may lose sign-ups from returning visitors.


### 16. T15 — Decide on dark mode: none today, light colours are hard-coded

- Lens: Dark mode · Severity: 1 cosmetic · ICE 36 = 3×4×3 · Type: rethink · hypothesis
- Effort: ≈1 day if built
- Depends on: T02, T11

**Evidence.** No prefers-color-scheme rules and no color-scheme meta: the page is light only, with colours hard-coded. Nothing breaks; whether users want a dark landing page is unknown.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| All pages · style.css | all | `:root` | — |

**Steps:**

1. Move colours to tokens first (#2, #11).
2. Decide with product whether a dark theme is worth it for an app the landing leads into.

**Acceptance criteria:**

- [ ] Metric: Decision recorded

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** Doubles visual QA.

## Glossary

- **WCAG** (accessibility standard): Web Content Accessibility Guidelines. Level AA is the usual legal target. Numbers like 1.4.3 are its success criteria.
- **AA** (the usual WCAG level): Contrast: normal text 4.5:1, large text 3:1, icons and focus rings 3:1. #a3a9b4 on white is 2.36:1.
- **ICE** (priority score): Impact × Confidence × Ease, each 1–10.
- **CTA** (call to action): The primary button; here “Get started free”.
- **CLS** (cumulative layout shift): How much visible content jumps while loading. ≤ 0.1 is good; the demo reaches 0.137 at 360.
- **Tap targets** (what a finger can hit): WCAG 2.5.8 asks ≥ 24×24 px; 44×44 px is comfortable.
- **focus** (where the keyboard is): The element that receives keys; a visible ring shows keyboard users where they are (WCAG 2.4.7).
- **token** (named design value): A named colour, size or spacing (color.text-muted = #6b7280) instead of a hard-coded value.
- **tokens** (named design values): Named colours, sizes and spacing used instead of hard-coded values.
- **inspect_ui.py** (measurement script): Part of this skill: screenshots at 3 widths, computed styles, contrast, scale, tap targets, dark and reduced-motion emulation, CLS and a focus walk.
- **5-second test** (quick hierarchy test): Show the screen for 5 seconds and ask what it was about and what to click.
- **pre-mortem** (failure analysis in advance): Imagine the fix shipped and nothing improved, then explain why.
- **A/B test** (comparison test): Half the visitors see the new version, half the old.
- **Reflow** (no sideways scroll): WCAG 1.4.10: content fits a 320 px wide viewport without scrolling in two directions.
