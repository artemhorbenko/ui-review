# Hands-off: UI review: Tallyo (demo)

Implementation brief generated from the UI review. Work top to bottom: tasks are ordered by ICE, and a task always comes after the ones it depends on. Each task says where the change happens (page, viewport, selector, screenshot mark) and what the values are now and should become. Treat "hypothesis" tasks as experiments: test before building fully.

## Context

- **Main finding:** Neither sign-up field has a label, and the password shows as plain text
- The page looks tidy, but the one task that matters, signing up, fails screen-reader and keyboard users and exposes the password on screen. Fix the form and the invisible focus first; the contrast and phone fixes are cheap and come next.
- **UI maturity:** Usable. The pages look consistent at a glance, so the UI is Usable for a mouse user with good eyesight. It cannot be called Consistent until the form and keyboard basics work for everyone and the four button shapes become one.
- **Confidence:** 66%

### Owner answers and assumptions

- Which screens and task matter most?: Landing sign-up, then pricing
- Devices (skipped): Skipped. Assumption: about half the visits are on phones, so both viewports were checked
- Design system and constraints: No published tokens; keep the brand blue #3156d3
- What is already known (skipped): Skipped. Assumption: no user tests or complaints collected yet

### Sources

- [ok] Browser walk-through (desktop + phone) — done
- [ok] inspect_ui.py (automatic checks) — 3 screenshots
- [ok] Page CSS and DOM — read
- [ok] Owner's answers (2 of 4) — 2 skipped
- [demo] Design tokens — inferred from CSS
- [no] Behaviour analytics (Clarity / Hotjar) — not connected
- [no] User feedback / tests — none

Missing, so lower confidence: Behaviour analytics (Clarity / Hotjar), User feedback / tests.

### Design tokens

| Token | Value | Use |
|---|---|---|
| `color.primary` | `#3156d3` | buttons, links, focus ring |
| `color.text` | `#1d2433` | headings, body |
| `color.text-muted` | `#6b7280` | secondary text (4.83:1) |
| `color.surface` | `#f6f7fb` | cards |
| `radius.md` | `8px` | buttons, inputs (proposed) |
| `radius.lg` | `12px` | cards (proposed) |
| `space scale` | `4 / 8 / 12 / 16 / 24 / 40px` | padding, gaps (proposed) |

### Screenshots

- `home-desktop` — Home · desktop 1280×800 · index.html · `demo/home-desktop.jpg` · marks: 1, 2, 3, 5, 6, 8, 11
- `home-phone` — Home · phone 390×844 · index.html · `demo/home-phone.jpg` · marks: 14, 1, 3, 4, 6, 9
- `pricing-desktop` — Pricing · desktop 1280×800 · pricing.html · `demo/pricing-desktop.jpg` · marks: 7, 2, 10, 12, 13

## Rules for the implementer

- Use the design tokens listed here; do not hard-code new colours, sizes or spacing values.
- Change only the elements named under Where; check that the same component elsewhere does not break.
- Verify at every viewport listed (desktop 1280×800, phone 390×844 unless stated) and in dark mode if the product has one.
- Keep text contrast ≥ 4.5:1 (large text ≥ 3:1), touch targets ≥ 24×24 px (aim for 44×44), visible focus on every control.
- Do not submit real forms, payments or messages while testing.
- Record before/after screenshots and measured values for each task.
- When a task is a hypothesis, run the cheapest test first and stop if the threshold is not met.

## Suggested order

| # | ID | Task | Severity | ICE | Type | Evidence |
|---|---|---|---|---|---|---|
| 1 | T01 | Give the sign-up fields visible labels and the right types (the password shows as plain text) (top 3) | 4 critical | 729 | fix | observed |
| 2 | T05 | Bring back the keyboard focus ring (0 of 31 stops show focus) and add the page language (top 3) | 4 critical | 648 | fix | observed |
| 3 | T02 | Raise text contrast: 37 of 97 text elements fail WCAG AA (top 3) | 3 major | 576 | fix | observed |
| 4 | T04 | Stop the phone page scrolling sideways (feature strip is 1,096 px wide) | 3 major | 567 | fix | observed |
| 5 | T07 | Remove the pricing countdown that restarts on every page load | 3 major | 540 | fix | observed |
| 6 | T06 | Enlarge phone tap targets (9 of 17 under 24 px) and name the menu button | 3 major | 432 | fix | observed |
| 7 | T03 | One primary action: "Get started" and "Book a demo" compete with the form | 3 major | 336 | fix | observed |
| 8 | T12 | Lift small text: footer, social and VAT note at 10–11 px, body 14 px / 1.3 | 2 minor | 288 | fix | observed |
| 9 | T08 | Replace "Submit" with a label that says what happens | 2 minor | 280 | fix | observed |
| 10 | T10 | One button shape instead of four corner radii (4, 6, 12, 999 px) | 2 minor | 252 | fix | observed |
| 11 | T13 | Show the current page in the navigation | 1 cosmetic | 216 | fix | observed |
| 12 | T09 | Show a response after sign-up: validation, loading and success states | 3 major | 210 | fix | hypothesis |
| 13 | T11 | Put spacing on an 8-point scale (13, 18, 22, 26, 37 px today) | 1 cosmetic | 144 | fix | observed |
| 14 | T14 | Test an email-first sign-up (password on the next step) | 2 minor | 140 | rethink | hypothesis |

## Tasks

### 1. T01 — Give the sign-up fields visible labels and the right types (the password shows as plain text)

- Lens: Forms · A11y · Severity: 4 critical · ICE 729 = 9×9×9 · Type: fix · observed
- Effort: ≈1 hour

**Evidence.** Both fields use only a placeholder ("Email", "Password") and no label: the automatic check found 0 of 2 fields with an accessible name (WCAG 1.3.1, 3.3.2, 4.1.2). Both are type="text", so the password is shown on screen and phones show a text keyboard instead of an email one. The placeholder disappears as soon as people type.

**Hypothesis.** If both fields get visible labels and the right input types, screen-reader users can sign up and nobody sees their password on screen, because the fields will be announced and masked.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home, sign-up · index.html | all | `#email` | home-desktop (demo/home-desktop.jpg), mark 1 |
| Home, sign-up · index.html | all | `#password` | home-phone (demo/home-phone.jpg), mark 1 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `label` | none (placeholder only) | `<label for="email">`Work email`</label>` and `<label for="password">`Password`</label>`, visible above each field | — |
| `type (#email)` | text | email, autocomplete="email" | — |
| `type (#password)` | text | password, autocomplete="new-password" | — |
| `placeholder color` | #b8bec9 | remove the placeholder, or #6b7280 if kept as a hint | `color.text-muted` |

**Steps:**

1. Add a visible `<label>` above each input in index.html and link it with for/id.
2. Change #email to type="email" autocomplete="email" and #password to type="password" autocomplete="new-password".
3. Style labels in .card: 14px/1.4, color.text, 6px gap to the field.
4. Run inspect_ui.py on the home page (labels must be 2 of 2) and check once with a screen reader.

**Acceptance criteria:**

- [ ] `#email` and `#password` each have a visible label linked by for/id (inspect_ui.py: labels 2 of 2)
- [ ] `#password` is type="password" and the typed text is masked
- [ ] `#email` is type="email" with autocomplete="email"; the phone shows the email keyboard
- [ ] Form still fits the first screen at 1280×800

**How to verify:** Fix in a branch, run inspect_ui.py and VoiceOver/NVDA once (≈30 min)

**Risk / guardrail:** The card gets ≈40 px taller; check that the form still fits the first desktop screen (it ends at 52% of 800 px now).

**Alternatives rejected:**

- Floating labels inside the field: rejected, they shrink to tiny text and often fail contrast.
- aria-label only: rejected, it fixes screen readers but sighted users still lose the hint after typing.

**Pre-mortem:** It shipped and nothing improved for screen-reader users because the visible label was added but not linked (for/id mismatch). The acceptance check runs the automatic label test, not just a visual look.


### 2. T05 — Bring back the keyboard focus ring (0 of 31 stops show focus) and add the page language

- Lens: Accessibility · Severity: 4 critical · ICE 648 = 8×9×9 · Type: fix · observed
- Effort: ≈30 minutes

**Evidence.** style.css has \*:focus { outline: none } and no replacement: tabbing through home and pricing gave 0 of 31 stops with any visible change (WCAG 2.4.7). Keyboard users cannot see where they are. The page also has no `<html lang>`, so screen readers guess the language (3.1.1).

**Hypothesis.** If focus is visible again, keyboard users can see where they are and finish sign-up, because every control will show a ring when tabbed to.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| All pages · style.css | desktop 1280×800 | `*:focus` | home-desktop (demo/home-desktop.jpg), mark 5 |
| All pages · index.html, pricing.html | all | `html` | — |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `outline on :focus-visible` | none | 2px solid #3156d3, offset 2px | `color.primary` |
| `html lang` | missing | en | — |

**Steps:**

1. Delete \*:focus { outline: none }.
2. Add :focus-visible { outline: 2px solid var(--color-primary); outline-offset: 2px } for links, buttons and inputs.
3. Add lang="en" to `<html>` on every page.
4. Rerun inspect_ui.py: focus visible must be 31 of 31.

**Acceptance criteria:**

- [ ] outline on :focus-visible is 2px solid #3156d3, offset 2px (color.primary) at desktop 1280×800, every viewport
- [ ] html lang is en at desktop 1280×800, every viewport
- [ ] 31 of 31 stops show focus; a keyboard-only sign-up run-through succeeds
- [ ] Metric: Keyboard stops with a visible focus: 31 of 31 (now 0)

**How to verify:** Tab through home and pricing after the change; rerun the focus check

**Risk / guardrail:** Mouse users see no ring with :focus-visible, so the look for them does not change.

**Alternatives rejected:**

- Box-shadow focus ring: equally valid; chosen outline because it survives Windows high-contrast mode.
- Underline links on focus only: rejected, not enough for buttons and inputs.

**Pre-mortem:** It shipped and focus was still invisible on the blue Submit button because the ring was the same blue as the button. Use outline-offset so the ring sits on the white page around it.


### 3. T02 — Raise text contrast: 37 of 97 text elements fail WCAG AA

- Lens: Colour and contrast · Severity: 3 major · ICE 576 = 8×9×8 · Type: fix · observed
- Effort: ≈1 hour

**Evidence.** inspect_ui.py found 37 of 97 text elements below WCAG AA (1.4.3). The worst: the hero subtitle #a3a9b4 on white = 2.36:1, the Terms/Privacy links #a3a9b4 on #f6f7fb = 2.21:1, "/mo per seat" 2.36:1, the VAT note #b8bec9 = 1.87:1, the feature strip and "No card needed" #8d94a1 = 3.05:1. All need 4.5:1.

**Hypothesis.** If secondary text uses #6b7280 instead of #a3a9b4, the subtitle and legal text become readable for low-vision users and in sunlight, without changing the look much.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home · index.html | all | `.sub, .proof, .strip span, .terms a, footer a` | home-desktop (demo/home-desktop.jpg), mark 2 |
| Pricing · pricing.html | all | `.price small, .vat` | pricing-desktop (demo/pricing-desktop.jpg), mark 2 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `color (.sub, .terms a, footer a, .price small)` | #a3a9b4 (2.36:1) | #6b7280 (4.83:1 on white, 4.52:1 on #f6f7fb) | `color.text-muted` |
| `color (.proof, .strip)` | #8d94a1 (3.05:1) | #6b7280 | `color.text-muted` |
| `color (.vat)` | #b8bec9 (1.87:1) | #6b7280 | `color.text-muted` |

**Steps:**

1. Add a muted-text token (--color-text-muted: #6b7280) to style.css.
2. Replace #a3a9b4, #8d94a1 and #b8bec9 for text with the token; keep the lighter greys only for borders and decoration.
3. Rerun inspect_ui.py on home (desktop, phone) and pricing; the contrast fails list should be empty except the CTA handled in #3.

**Acceptance criteria:**

- [ ] color (.sub, .terms a, footer a, .price small) is #6b7280 (4.83:1 on white, 4.52:1 on #f6f7fb) (color.text-muted) at every viewport
- [ ] color (.proof, .strip) is #6b7280 (color.text-muted) at every viewport
- [ ] color (.vat) is #6b7280 (color.text-muted) at every viewport
- [ ] 0 text elements below AA on the 3 checked screens (excluding text over images)
- [ ] Metric: Text elements passing AA: 60 of 97 now, target 97 of 97

**How to verify:** Swap the two greys in style.css and rerun inspect_ui.py on 3 screens

**Risk / guardrail:** The page looks a little heavier; keep the hierarchy by size and weight, not by paler grey.

**Alternatives rejected:**

- Darken only the subtitle: rejected, leaves 30+ failing elements in the footer, strip and pricing.
- Switch to a darker brand grey #5d6472 (5.95:1): kept as an option if #6b7280 fails on new surfaces.

**Pre-mortem:** It shipped and the check still failed because the greys were hard-coded in 6 places and two were missed. Search style.css for every hex value first and replace them through the token.


### 4. T04 — Stop the phone page scrolling sideways (feature strip is 1,096 px wide)

- Lens: Responsive · Severity: 3 major · ICE 567 = 7×9×9 · Type: fix · observed
- Effort: ≈20 minutes

**Evidence.** At 390 px the page is 1,096 px wide: the feature strip uses five fixed 200 px items in a flex row with overflow: visible, so the whole page scrolls sideways and the browser can zoom out (WCAG 1.4.10 Reflow).

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home, feature strip · index.html | 390×844 | `.strip` | home-phone (demo/home-phone.jpg), mark 4 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `document width at 390 px` | 1096px | 390px (no sideways scroll) | — |
| `.strip span width` | 200px (flex: none) | auto; .strip flex-wrap: wrap | — |

**Steps:**

1. Set .strip { flex-wrap: wrap; gap: 8px 16px } and remove the fixed width from .strip span.
2. Check at 360, 390 and 820 px that nothing else overflows (inspect_ui.py prints SIDEWAYS SCROLL if it does).

**Acceptance criteria:**

- [ ] document width at 390 px is 390px (no sideways scroll) at 390×844
- [ ] .strip span width is auto; .strip flex-wrap: wrap at 390×844
- [ ] Metric: Page width at 390 px equals 390 px

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** None worth noting; the strip becomes two or three lines on phones.


### 5. T07 — Remove the pricing countdown that restarts on every page load

- Lens: Microcopy and trust · Severity: 3 major · ICE 540 = 6×9×10 · Type: fix · observed
- Effort: ≈15 minutes

**Evidence.** The "Launch offer ends in 09:59" badge on pricing restarts from 10 minutes on every load: it is false urgency, a dark pattern that erodes trust and may break consumer-protection rules. Its text is also 4.09:1 on #fff1ec, below AA.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Pricing · pricing.html | all | `#timer` | pricing-desktop (demo/pricing-desktop.jpg), mark 7 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `#timer` | countdown from 10:00 on every load | removed, or a real end date ("Launch price until 31 Jan") | — |

**Steps:**

1. Remove the countdown script and the badge.
2. If there is a real launch price, show its real end date as plain text in color.text-muted.

**Acceptance criteria:**

- [ ] #timer is removed, or a real end date ("Launch price until 31 Jan") at every viewport
- [ ] Metric: No fake urgency on the page; plan choice rate watched for 2 weeks

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** A small drop in urgency-driven clicks, worth the trust.

**Copy variants:**

- "Launch price until 31 January": true and still gives a reason to act.
- "Prices locked for a year when you sign up now": a real benefit instead of a clock.


### 6. T06 — Enlarge phone tap targets (9 of 17 under 24 px) and name the menu button

- Lens: Responsive · A11y · Severity: 3 major · ICE 432 = 6×9×8 · Type: fix · observed
- Effort: ≈1 hour

**Evidence.** On the phone 9 of 17 tap targets are under the 24×24 px minimum (WCAG 2.5.8): the 4 social icons are 18×18 and the 5 footer links 14 px high. Only 2 of 17 reach the comfortable 44×44. The menu button is 32×32 and has no accessible name (it reads as "☰").

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home, footer · index.html | 390×844 | `.social a, footer a` | home-desktop (demo/home-desktop.jpg), mark 6 |
| Home, header · index.html | 390×844 | `.burger` | home-phone (demo/home-phone.jpg), mark 6 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `size (.social a)` | 18×18 px | 44×44 px (icon stays 18 px) | — |
| `height (footer a)` | 14 px | ≥ 24 px (padding 5px 4px), ideally 44 px | — |
| `size (.burger)` | 32×32 px | 44×44 px | — |
| `aria-label (.burger)` | none | Menu (and aria-expanded) | — |

**Steps:**

1. Give .social a and .burger width/height 44px with the icon centred.
2. Add padding to footer links so each is at least 24 px high and 8 px apart.
3. Add aria-label="Menu" and aria-expanded to the burger button.
4. Rerun inspect_ui.py at 390×844: targets ≥ 24 px must be 17 of 17.

**Acceptance criteria:**

- [ ] size (.social a) is 44×44 px (icon stays 18 px) at 390×844
- [ ] height (footer a) is ≥ 24 px (padding 5px 4px), ideally 44 px at 390×844
- [ ] size (.burger) is 44×44 px at 390×844
- [ ] aria-label (.burger) is Menu (and aria-expanded) at 390×844
- [ ] Metric: Phone tap targets ≥ 24 px: 17 of 17 (now 8); ≥ 44 px: at least 90%

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** The footer grows by ≈30 px; fine.


### 7. T03 — One primary action: "Get started" and "Book a demo" compete with the form

- Lens: Visual hierarchy · Severity: 3 major · ICE 336 = 7×6×8 · Type: fix · observed
- Effort: ≈2 hours

**Evidence.** The hero has two filled buttons of the same size (Get started free 180×46, Book a demo 153×46) and the form beside it has a third filled button ("Submit"). The orange demo button draws the eye most (Hick's law, visual weight) and its white text is only 3.6:1 on #e8572a. On the phone both buttons sit side by side above the form.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home, hero · index.html | all | `.ctas .btn-demo` | home-desktop (demo/home-desktop.jpg), mark 3 |
| Home, hero · index.html | 390×844 | `.ctas` | home-phone (demo/home-phone.jpg), mark 3 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `background (.btn-demo)` | #e8572a | transparent | — |
| `color / border (.btn-demo)` | #ffffff on #e8572a (3.6:1) | #3156d3 text, 1px #3156d3 border (6.17:1) | `color.primary` |
| `href (.btn-primary)` | #signup | #signup and move focus to #email | — |

**Steps:**

1. Make "Book a demo" a secondary (outline) button in color.primary.
2. Keep "Get started free" as the one filled button; on click, move focus to the email field.
3. On phone, stack the two buttons full width with the primary first.
4. Run a 5-second test with 5 people: what would you click first?

**Acceptance criteria:**

- [ ] background (.btn-demo) is transparent at every viewport, 390×844
- [ ] color / border (.btn-demo) is #3156d3 text, 1px #3156d3 border (6.17:1) (color.primary) at every viewport, 390×844
- [ ] href (.btn-primary) is #signup and move focus to #email at every viewport, 390×844
- [ ] Metric: Share of first clicks on the primary action (5-second / first-click test)

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** Demo requests may drop; track them separately for 2 weeks.

**Copy variants:**

- "Start free — no card": puts the cost answer into the button.
- "Create my first invoice": names the outcome rather than the account.


### 8. T12 — Lift small text: footer, social and VAT note at 10–11 px, body 14 px / 1.3

- Lens: Typography · Severity: 2 minor · ICE 288 = 4×8×9 · Type: fix · observed
- Effort: ≈30 minutes

**Evidence.** 17 of 97 text elements across the 3 screenshots are under 12 px: social labels 10px, footer links and © 11px, the pricing VAT note 11px. Body text on the phone is 14px with line-height 1.3 (18.2px), tight for paragraphs.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Pricing · pricing.html | all | `.vat` | pricing-desktop (demo/pricing-desktop.jpg), mark 12 |
| Home · index.html | 390×844 | `footer, .social a, .features p` | — |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `font-size (footer, .vat)` | 11px | 13px | `font.size.sm` |
| `font-size (body on phone)` | 14px | 16px | `font.size.md` |
| `line-height (body)` | 1.3 (18.2px) | 1.5 | — |

**Steps:**

1. Set body to 16px/1.5 below 700 px and 15px/1.5 above.
2. Raise footer, social and VAT text to 13px.

**Acceptance criteria:**

- [ ] font-size (footer, .vat) is 13px (font.size.sm) at every viewport, 390×844
- [ ] font-size (body on phone) is 16px (font.size.md) at every viewport, 390×844
- [ ] line-height (body) is 1.5 at every viewport, 390×844
- [ ] Metric: Text under 12 px: 0 (now 17 of 97 across the 3 screenshots)

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** Longer pages on phones; acceptable.


### 9. T08 — Replace "Submit" with a label that says what happens

- Lens: Microcopy · Severity: 2 minor · ICE 280 = 4×7×10 · Type: fix · observed
- Effort: ≈5 minutes

**Evidence.** The sign-up button says "Submit", which says nothing about the result (Nielsen: match between system and real world). It sits under "Create your account".

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home, sign-up · index.html | all | `#signup .btn` | home-desktop (demo/home-desktop.jpg), mark 8 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `button text` | Submit | Create free account | — |

**Steps:**

1. Change the button text.
2. Use the same verb in the success message ("Account created").

**Acceptance criteria:**

- [ ] button text is Create free account at every viewport
- [ ] Metric: Button names the outcome; first-click test on the form

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** None.

**Copy variants:**

- "Create free account": repeats the heading and the price promise.
- "Start invoicing": names what people came for.


### 10. T10 — One button shape instead of four corner radii (4, 6, 12, 999 px)

- Lens: Design system · Severity: 2 minor · ICE 252 = 4×9×7 · Type: fix · observed
- Effort: ≈1 hour

**Evidence.** Computed border-radius across buttons: 12px (Get started), 999px (Book a demo), 4px (Submit, Log in), 6px (pricing Choose); cards add 8, 12 and 16px. Four button shapes on two pages read as four different components.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home + Pricing · index.html, pricing.html | all | `.btn, .menu .login` | pricing-desktop (demo/pricing-desktop.jpg), mark 10 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `border-radius (buttons)` | 4px / 6px / 12px / 999px | 8px | `radius.md` |
| `border-radius (cards)` | 8px / 12px / 16px | 12px | `radius.lg` |

**Steps:**

1. Add radius tokens (radius.md 8px, radius.lg 12px) and use them in .btn, .login, .card, .plan.
2. Remove per-button radius overrides.

**Acceptance criteria:**

- [ ] border-radius (buttons) is 8px (radius.md) at every viewport
- [ ] border-radius (cards) is 12px (radius.lg) at every viewport
- [ ] Metric: Distinct button radii on the site: 1 (now 4)

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** None; check the popular plan still stands out by its border, not its radius.


### 11. T13 — Show the current page in the navigation

- Lens: Navigation · Severity: 1 cosmetic · ICE 216 = 3×8×9 · Type: fix · observed
- Effort: ≈20 minutes

**Evidence.** On pricing.html the "Pricing" link looks the same as the others: nothing marks the current page and there is no aria-current (heuristic: visibility of system status).

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Pricing, header · pricing.html | desktop 1280×800 | `.menu a[href="pricing.html"]` | pricing-desktop (demo/pricing-desktop.jpg), mark 13 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `current link` | #4a5263, no marker | color.text + 2px underline, aria-current="page" | `color.text` |

**Steps:**

1. Add aria-current="page" to the active link on each page.
2. Style [aria-current=page] with color.text and a 2px underline.

**Acceptance criteria:**

- [ ] current link is color.text + 2px underline, aria-current="page" (color.text) at desktop 1280×800
- [ ] Metric: Every page marks its nav item

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** None.


### 12. T09 — Show a response after sign-up: validation, loading and success states

- Lens: States and feedback · Severity: 3 major · ICE 210 = 7×5×6 · Type: fix · hypothesis
- Effort: ≈1 day
- Depends on: T01

**Evidence.** The form has no validation messages, no loading or disabled state on the button and no success message in the markup; the submit handler returns false. We did not submit it, so what users see after the click is a hypothesis: most likely nothing.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home, sign-up · index.html | all | `#signup` | home-phone (demo/home-phone.jpg), mark 9 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `error message` | none | inline text under the field, linked with aria-describedby, after blur | — |
| `button while sending` | no state | disabled + "Creating account…" | — |
| `success` | none | redirect to onboarding or a confirmation message | — |

**Steps:**

1. Submit the form once on a staging copy with a test email and record what happens.
2. Add inline errors for an invalid email and a short password, shown after the field loses focus.
3. Disable the button and change its text while the request runs; show success or a clear error.

**Acceptance criteria:**

- [ ] error message is inline text under the field, linked with aria-describedby, after blur at every viewport
- [ ] button while sending is disabled + "Creating account…" at every viewport
- [ ] success of `#signup` is redirect to onboarding or a confirmation message at every viewport
- [ ] Metric: Every submit attempt ends in a visible success or a specific error

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** Over-eager validation (on every keystroke) annoys people; validate on blur and on submit.


### 13. T11 — Put spacing on an 8-point scale (13, 18, 22, 26, 37 px today)

- Lens: Layout and spacing · Severity: 1 cosmetic · ICE 144 = 3×8×6 · Type: fix · observed
- Effort: ≈2 hours

**Evidence.** Computed paddings and gaps: header 13px 37px, card 26px 22px, strip 18px 37px, feature gap 22px, hero gap 48px. None share a scale, so edges do not line up between sections.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home · index.html | desktop 1280×800 | `.top, .card, .strip, .features` | home-desktop (demo/home-desktop.jpg), mark 11 |

**Current → target:**

| Property | Current | Target | Token |
|---|---|---|---|
| `padding (.top)` | 13px 37px | 12px 40px | `space.3 / space.10` |
| `padding (.card)` | 26px 22px | 24px | `space.6` |
| `padding (.strip)` | 18px 37px | 16px 40px | `space.4 / space.10` |
| `gap (.features)` | 22px | 24px | `space.6` |

**Steps:**

1. Add a 4/8-based spacing scale as tokens.
2. Replace off-scale values; use one horizontal page padding (40px desktop, 16px phone).

**Acceptance criteria:**

- [ ] padding (.top) is 12px 40px (space.3 / space.10) at desktop 1280×800
- [ ] padding (.card) is 24px (space.6) at desktop 1280×800
- [ ] padding (.strip) is 16px 40px (space.4 / space.10) at desktop 1280×800
- [ ] gap (.features) is 24px (space.6) at desktop 1280×800
- [ ] Metric: Off-scale spacing values in style.css: 0

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** Small layout shifts; compare before/after screenshots.


### 14. T14 — Test an email-first sign-up (password on the next step)

- Lens: Forms · Heuristics · Severity: 2 minor · ICE 140 = 7×4×5 · Type: rethink · hypothesis
- Effort: ≈3 days
- Depends on: T01, T09

**Evidence.** Asking for email and password at once on the landing is a common drop-off point; an email-first step can lower the effort of starting. We have no form analytics, so this is a hypothesis to test after #1 and #9.

**Where:**

| Page | Viewport | Selector | Screenshot |
|---|---|---|---|
| Home, sign-up · index.html | all | `#signup` | home-phone (demo/home-phone.jpg), mark 14 |

**Steps:**

1. Add form-start and submit events to measure today's drop-off first.
2. Build an email-only first step behind a flag; password and name on step 2.
3. Run an A/B test for 2 weeks or until each variant has 300 sign-up starts.

**Acceptance criteria:**

- [ ] Metric: Completed sign-ups per form start

**How to verify:** Open the page at each viewport listed under Where, take a screenshot of the same area, compare with the original mark, and re-run the measurement (scripts/inspect_ui.py --sel) for every property in Current → target.

**Risk / guardrail:** Two steps can feel longer; keep step 2 on the same page without reload.

## Glossary

- **WCAG** (accessibility standard): Web Content Accessibility Guidelines. Level AA is the usual legal target in the EU (EAA) and the US. Numbers like 1.4.3 are its success criteria.
- **AA** (the usual WCAG level): For contrast: normal text needs 4.5:1, large text (24 px, or 18.66 px bold) 3:1. #a3a9b4 on white is 2.36:1.
- **ICE** (priority score): Impact × Confidence × Ease, each 1–10. The bigger the product, the sooner to do it.
- **inspect_ui.py** (measurement script): Part of this skill: opens the page at each viewport, saves screenshots, reads computed styles and runs the contrast, tap-target, label, focus and small-text checks.
- **tap target** (area you can touch): The clickable size of a link or button. WCAG 2.5.8 asks for at least 24×24 px; 44×44 px is comfortable for a thumb.
- **Tap targets** (areas you can touch): The clickable size of links and buttons. WCAG 2.5.8 asks for at least 24×24 px; 44×44 px is comfortable for a thumb.
- **focus** (where the keyboard is): The element that receives the keyboard. A visible focus ring shows keyboard users where they are (WCAG 2.4.7).
- **screen reader** (software that reads the UI aloud): VoiceOver, NVDA, TalkBack. It reads labels, roles and states; a field with only a placeholder is often announced as just "edit text".
- **CTA** (call to action): The button that asks for the main action, here "Get started free".
- **Hick's law** (more choices, slower choice): The time to decide grows with the number of options of equal weight; two filled buttons plus a form make three.
- **dark pattern** (manipulative design): A UI trick that pushes people against their interest: fake urgency, confirmshaming, pre-checked consent, hidden costs.
- **token** (named design value): A named colour, size or spacing (color.text-muted = #6b7280) used instead of a hard-coded value, so one change updates the whole UI.
- **tokens** (named design values): Named colours, sizes and spacing used instead of hard-coded values.
- **5-second test** (quick hierarchy test): Show the screen for 5 seconds and ask what it was about and what to click. Shows whether the hierarchy works.
- **pre-mortem** (failure analysis in advance): Imagine the fix shipped and nothing improved, and explain why. The reasons become checks you add up front.
- **A/B test** (comparison test): Half of the visitors see the new version, half the old; the difference shows the effect.
- **aria-current** (current-page marker): An attribute that tells screen readers which link is the current page; also a hook for styling it.
- **Nielsen** (usability heuristics): Jakob Nielsen's 10 usability heuristics and 0–4 severity scale, the standard checklist for UI reviews.
