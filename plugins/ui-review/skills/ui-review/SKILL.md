---
name: ui-review
description: Review the visual interface of a website, web app, landing page, mobile app screenshots or Figma frames through 13 UI lenses - visual hierarchy, CTA prominence, imagery and icons, layout and grid, spacing rhythm, typography scale, colour and contrast (WCAG), dark mode, brand coherence, design-system consistency, responsive behaviour at 360/768/1280, motion, perceived performance - with measured values and annotated screenshots, and deliver a visual report plus a hands-off task file for AI agents (selectors, viewports, current vs target values). Use when someone asks to review, critique or audit a UI or a page's look, check contrast, consistency, type or spacing, or asks what to fix visually. Task flows go to ux-review, strategy to product-lens-audit.
---

# UI Review

Look at an interface through 13 UI lenses and return a short, prioritized list of fixes in two forms from one `audit.json`: a visual report for people (with annotated screenshots) and a hands-off brief for whoever implements it, often another AI agent (with page, viewport, selector and current → target values for every task).

**Scope.** What the interface looks like and how its surface behaves. Task flows, forms logic, navigation structure and copy belong to **ux-review**; strategy, growth and business model to **product-lens-audit**. When you notice something outside the scope, mention it in one line in the data section and name the other skill; do not make it an issue.

Respond in the user's language; write the report in the language they ask for (default: theirs).

Files next to this SKILL.md (read each when its step comes, not up front):
- `references/data-sources.md` - which tools to look for, what to measure, fallbacks (steps 0-1).
- `references/lenses.md` - the 13 lenses, what to measure for each, group ids, severity and UI maturity (step 2).
- `references/report-spec.md` and `references/audit.schema.json` - the report's sections and the shape of its data (step 4).
- `assets/report-template.html` - the report page; it renders everything from one JSON block. `assets/example-audit.en.json` is a full example (fictional invoicing app "Tallyo", real screenshots in `assets/demo/`); `assets/example-handoff.en.md` is the hands-off built from it.
- `scripts/probe.js` - the measuring probe: computed styles, element boxes, contrast over the whole page, type/colour/radius/spacing scale, tap targets, dark-mode and reduced-motion rules, running animations, CLS and LCP. Paste it into a browser tool's JavaScript runner when there is no shell.
- `scripts/inspect_ui.py` - runs the probe with Playwright at 360, 768 and 1280 px, saves screenshots, emulates dark mode and reduced motion, and tabs through the page for visible focus (step 1).
- `scripts/validate_audit.py`, `scripts/build_report.py`, `scripts/check_report.py`, `scripts/build_handoff.py` - data check, page build, render check, hands-off (steps 4-5).

## 0. Check which sources are connected

Before gathering, look at the tools this session actually has (search the tool list / ToolSearch; never assume): a shell with Playwright that can reach the site, a browser tool, a Figma or design-token source, behaviour analytics. `references/data-sources.md` lists what to look for and the fallbacks. Build a source list with a status for each: `ok` (connected and used, or measured by you), `demo` (sample, partial, or values read off a screenshot), `no` (not connected, failing, or behind a login).

Use every source read-only. If an important source is missing, say which one in one line and continue; never fill the gap with invented values. Each `no` lowers confidence.

## 0.5 Ask the requester (every question skippable)

First look for saved context: a `ui-review-context.md`, a design-system doc, or a previous `audit.json`. Ask only about what it does not cover; with a previous `audit.json`, say in the report which tasks were done and how each check moved.

Then ask one short round of up to 4 questions with a multiple-choice question tool when available (AskUserQuestion or similar), each with a "Skip" option; otherwise in plain text. Never block: on a skip or no answer, state the assumption and continue.
- **Which pages or screens** matter most?
- **Devices**: mostly phone, desktop or both; does the product have a dark mode?
- **Design system and brand**: tokens, a component library, Figma, brand colours that cannot change.
- **What is already known**: complaints, a redesign in progress, things already tried.

Record answers in `answers` and in sources as `ok`; a skipped one shows "Skipped" plus the assumption.

## 1. Gather the material (before judging anything)

- **Three widths, always:** 360, 768 and 1280 px. Screenshot the first screen of every key page at each width, plus any section a finding is about. Give every screenshot an id (`pricing-768`). Do not submit forms, sign up, pay or send anything.
- **With a shell that reaches the site:** `python scripts/inspect_ui.py URL --name home --sel cta=".hero .btn" --sel h1="h1" --out ./shots` per page. It prints each selector's box as % of the screenshot (use it for marks) and its computed styles (use them as current values), and writes everything else to `<name>-inspect.json`.
- **With a browser tool only:** paste `scripts/probe.js` into its JavaScript runner and call it with your selectors: `(<probe>)({sels: {cta: '.hero .btn'}})`. If the browser window cannot be resized to exact widths, load the page in a same-origin `<iframe>` of the exact size (write it into a tab on the same site) and run the probe in `iframe.contentWindow`; screenshot the iframe. Check visible focus by tabbing, and dark mode by looking at the `css.darkRules` count and, if possible, an emulated dark screenshot.
- **Screenshots or Figma only:** say so in sources; colours read off images are approximate (`demo`); motion, focus, CLS and dark mode cannot be observed.
- **Measure, never guess:** every font size, colour, contrast ratio, spacing value, size and CLS number in the report comes from computed styles or a tool result. A value you only see in a screenshot is marked as approximate.

Write down the main screens as a route. Name the **UI maturity** level from evidence and what blocks the next one.

## 2. Apply the lenses

Read `references/lenses.md` and go through all 13 lenses in 5 groups: look (hierarchy, CTA prominence, imagery and icons), structure (layout and grid, spacing rhythm, typography scale), colour (colour and contrast, dark mode, brand coherence), system (design-system consistency), behave (responsive, motion, perceived performance). For each lens write 1-3 findings tied to something you saw or measured, cite the WCAG criterion where one applies, and score it 0-100.

## 3. Prioritize

- One table of findings with severity 1-4, Impact, Confidence, Ease (1-10), ICE = I × C × E, type **fix** (`opt`) or **rethink** (`ex`), and **observed** or **hypothesis**.
- For every task: **where** (page or URL, viewport, CSS selector or screenshot id) and **change** (property, measured current value, target value, token).
- Put each issue on its screenshot as a mark (box in %, number = issue id). One issue can have marks on several shots. Group repeated instances (14 small buttons) into one task with their selectors.
- For the top 3: compare at least 2 alternatives, write the experiment with risk type and a success threshold, and run a pre-mortem ("it shipped and nothing improved - why?"); put the answer into the plan.

## 4. Output: two files from one audit.json

Read `references/report-spec.md`. Write the review as one `audit.json` following `references/audit.schema.json` (start from `assets/example-audit.en.json`). You write data only; the template draws every chart, table, mark and label and computes ICE, health, quick wins and confidence.

**1) Report for people.** With a shell: `python scripts/build_report.py audit.json report.html` - it validates first, refuses to build on errors, and embeds the screenshots. Without a shell: copy `assets/report-template.html`, set `<html lang>` and `<title>`, replace the JSON in `<script type="application/json" id="audit">` (write `<\/` for `</`); shots without `src` draw their marks on a placeholder frame. Publish it as an artifact when an artifact tool exists (private by default), otherwise send the .html file. Save `audit.json` next to it.

**2) Hands-off for AI agents.** `python scripts/build_handoff.py audit.json handoff.md --json tasks.json`: context, sources, design tokens, rules, and every issue as a task ordered by ICE with dependencies first - evidence, where, current → target, steps, acceptance criteria, how to verify, risks. Add `accept`, `depends`, `verify` and top-level `rules` when the defaults are not specific enough. Deliver `handoff.md`, `tasks.json` and the screenshots as files.

## 5. Check before delivering

1. **Validate:** `validate_audit.py` must pass (it also warns when 360, 768 or 1280 is missing).
2. **Render:** `python scripts/check_report.py report.html --out ./report-check` (desktop 1280, tablet 820 touch, phone 390 touch): page errors, sideways scroll, empty charts, broken screenshots, marks outside their image, marks that do not open their plan entry, overlapping labels, tooltips on hover and tap, phone table cells. Look at the screenshots it saves, dark mode included. Fix and re-check at most twice. Without a headless browser, open the published page with a browser tool at wide and narrow widths.
3. **Fact check, last:** every number in the text, KPIs, checks, `why` and `change.cur` must trace to a probe or tool result, and the arithmetic must hold (sums of pass counts, shares, ratios). Every mark must sit on the element its issue names. In Claude Code, give this to a separate subagent that has not seen your reasoning: pass it `audit.json`, the probe/inspect output and the screenshots, and ask for every value it cannot trace and every mark that misses. Elsewhere, do it yourself, number by number. Fix or remove what does not trace, then rebuild both outputs.

In chat, reply with 3-5 summary bullets, the link and files, and one line on what was checked.

## Rules
- Every finding points to evidence (screenshot, measured value, selector) or is marked as a hypothesis.
- Measure, don't eyeball. Say when a number depends on your connection (LCP) or on an emulation.
- Target values name a design token when one exists; do not invent a colour or size when the system has one.
- Fewer, sharper fixes; group repeated instances; mostly fixes, a few rethinks.
- Stay in scope: flows to ux-review, strategy to product-lens-audit.
- Do not recommend dark patterns; never invent analytics, quotes or results.
- A check that could not run shows "no data" (`v: null`), never a guessed number.
- Lens scores are judgments based on findings: below 40 = big problems, 40-60 = partial, above 60 = solid.
