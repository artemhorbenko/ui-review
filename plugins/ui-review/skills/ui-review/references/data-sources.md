# Inputs and data sources

Check what this session can actually reach before gathering: search the tool list (ToolSearch or similar) for each source below. Never assume a connector exists, and never fill a gap with invented values. Use every source read-only.

## Status

| Status | When |
|---|---|
| `ok` | Connected and used, a value you measured yourself (computed styles, `inspect_ui.py`), or the owner's own answer, file or screenshot. |
| `demo` | A sample, a partial export, a value read off a compressed screenshot (colours from a JPEG are approximate), a Figma frame that may not match production. |
| `no` | Not connected; connected but returning an error or "no access"; a page you could not open (login wall, bot block). Try a failing call once more; if it fails again, mark `no` and move on. |

Confidence in the report is the average of ok = 1, demo = 0.6, no = 0, so list only sources that matter for this interface.

## What to look for and what to ask it

### Browser (the main source)
- **Tools:** Claude in Chrome, the built-in browser, a cloud browser, or Playwright from the shell (`scripts/inspect_ui.py`).
- **Do:** open each key screen at **desktop 1280×800** and **phone 390×844** (add **tablet 820×1180** for apps used on tablets). Walk the main task end to end. Take a screenshot of every screen in every viewport and give it an id (`home-desktop`). Hover and focus the primary controls; tab through the page once with the keyboard; resize to 360 px once.
- **Measure, don't eyeball:** read computed styles (colour, background, font size, line height, padding, radius, size) for every element you flag. With a shell, `python scripts/inspect_ui.py URL --sel name=css ...` does this and also runs the automatic checks below. With a browser tool only, read the same values with a small script (`getComputedStyle`, `getBoundingClientRect`).
- **Don't:** submit real forms, payments, sign-ups or messages. Fill fields to see validation, then leave.
- **Fallback:** the owner's screenshots or a screen recording; mark measured values from them `demo`.
- **Feeds:** all lenses.

### Automatic checks (with a shell)
- **Tool:** `scripts/inspect_ui.py` (Playwright). Per viewport it reports:
  - text contrast pairs that pass WCAG AA, with the failing ones (text, selector, ratio, needed ratio, colours);
  - touch targets under 24×24 px (WCAG 2.5.8 minimum) and under 44×44 px (comfortable) on touch viewports;
  - text under 12 px; images without `alt`; form fields without an accessible name; sideways scroll; missing `lang`;
  - for each `--sel`, the element's box as % of the screenshot (for marks) and its computed styles (for current values).
- **Other tools if present:** axe-core, Lighthouse (accessibility and CLS), Pa11y. Record their version and the page.
- **Know the limits:** contrast over images and gradients cannot be computed (reported as `unknown`); automatic checks find maybe a third of accessibility problems; keyboard and screen-reader checks stay manual.
- **Feeds:** colour, accessibility, responsive, typography, forms.

### Design source and tokens
- **Tools:** a Figma connector (Dev Mode variables, styles), Storybook, the repo's CSS variables / Tailwind config / theme file, a design-system site.
- **Queries:** colour, type, spacing, radius and shadow tokens with their values; the components for buttons, inputs, cards; which screens exist in design but differ in production.
- **Watch for:** production values that match no token (hard-coded); two tokens with the same value; tokens named by colour instead of role.
- **Fallback:** derive the de-facto palette and scale from computed styles on 3-5 screens and say they are inferred.
- **Feeds:** design-system consistency, colour, typography, layout. Record useful ones in `tokens` in `audit.json`; target values should name a token when one exists.

### Behaviour analytics
- **Tools:** Microsoft Clarity, Hotjar, FullStory, PostHog, GA4 (events), Amplitude, Mixpanel.
- **Queries, last 30-90 days:** rage clicks and dead clicks by element; scroll depth on key pages; form-field drop-off; error events; device split (how much traffic is phone).
- **Fallback:** heatmap or dashboard screenshots with the date range visible.
- **Polluted data:** own team's sessions, bots (0-second sessions), one campaign spike.
- **Feeds:** hierarchy, forms, states, responsive; Impact scores.

### User feedback
- **Tools:** Intercom, Zendesk, app store reviews, survey tools, usability-test notes.
- **Queries:** tickets and reviews that mention a screen, a button or "can't find"; 2-3 short quotes.
- **Fallback:** the owner's summary ("people keep asking where the export is").
- **Feeds:** navigation, microcopy, heuristics; Confidence scores.

### Performance and stability
- **Tools:** PageSpeed Insights / Lighthouse, CrUX, Sentry, Web Vitals in analytics.
- **Queries:** CLS and INP on key pages, JavaScript errors on the main task.
- **Feeds:** states and feedback, responsive.

## Recording values

For every value you use, keep where it came from: the screen id, viewport, selector and the tool. A KPI or check with a number must name its source (`src` in `audit.json`), and that source must not be marked `no`. Values in `change.cur` must be measured (computed style or a tool), not guessed from a screenshot, unless the source is marked `demo`.
