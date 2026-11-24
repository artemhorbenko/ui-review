---
name: ui-review
description: Review the user interface of a website, web app, SaaS screen, landing page, mobile app screenshots or Figma frames through 12 UI lenses - visual hierarchy, layout and spacing, typography, colour and contrast, usability heuristics, navigation, forms, states and feedback, accessibility (WCAG), responsive and touch, microcopy, design-system consistency - and deliver a visual report with annotated screenshots plus a hands-off task file for AI agents with selectors and current vs target values. Use when someone asks to review, critique or audit a UI, a design, a screen or a page's look and usability, check accessibility or contrast, or asks what to fix in the interface.
---

# UI Review

Look at an interface through 12 UI lenses and return a short, prioritized list of fixes in two forms from one `audit.json`: a visual report for people (with annotated screenshots) and a hands-off brief for whoever implements it, often another AI agent (with page, viewport, selector and current → target values for every task).

Respond in the user's language, and write the report in it too.

Files next to this SKILL.md (read each when its step comes, not up front):
- `references/data-sources.md` - which tools to look for, what to measure, fallbacks (steps 0-1).
- `references/lenses.md` - the 12 lenses, their checks, icon and group ids, severity and UI maturity (step 2).
- `references/report-spec.md` and `references/audit.schema.json` - the report's sections and the shape of its data (step 4).
- `assets/report-template.html` - the report page; it renders everything from one JSON block. `assets/example-audit.json` (Ukrainian) and `assets/example-audit.en.json` are full examples (fictional invoicing app "Tallyo", with real screenshots in `assets/demo/`).
- `scripts/inspect_ui.py` - screenshots, element boxes for marks, computed styles and automatic checks (contrast, touch targets, labels, alt, small text, sideways scroll) (step 1).
- `scripts/validate_audit.py`, `scripts/build_report.py`, `scripts/check_report.py` - data check, page build, render check (steps 4-5).
- `scripts/build_handoff.py` - the same audit as `handoff.md` + `tasks.json` for an AI agent or developer. Example: `assets/example-handoff.en.md`.

## 0. Check which sources are connected

Before gathering, look at the tools this session actually has (search the tool list / ToolSearch; never assume): a browser, a shell with Playwright, a Figma or design-token source, behaviour analytics (Clarity, Hotjar), feedback. `references/data-sources.md` lists what to look for and the fallbacks. Build a source list with a status for each: `ok` (connected and used, or measured by you), `demo` (sample, partial, or values read off a screenshot), `no` (not connected, or failing, or behind a login you could not pass).

Use every source read-only. If an important source is missing, say which one in one line and continue; never fill the gap with invented values. The list goes into the report's data block, and each `no` lowers confidence.

## 0.5 Ask the requester (every question skippable)

First look for saved context: a `ui-review-context.md`, a design-system doc, or a previous `audit.json` in the project or attached by the user. Read it and ask only about what it does not cover. With a previous `audit.json`, say in the report what changed since then: which tasks were done, which checks moved.

Then ask one short round of up to 4 questions. Use a multiple-choice question tool when available (AskUserQuestion or similar), and give every question a "Skip" option; otherwise ask in plain text and say they can skip any. Never block: if the person skips or does not answer, state the assumption you take and continue.

Pick the questions that change the review most:
- **Which screens and which task matter most** (sign-up, checkout, the dashboard people open daily)?
- **Devices**: mostly phone, desktop, or both; any tablet or in-app webview?
- **Design system and constraints**: tokens, a component library, a Figma file, brand colours that cannot change, a framework (Tailwind, MUI, WordPress theme).
- **What is already known**: complaints, support tickets, test results, things already tried.

Record each answer in the sources list as `ok` ("from the owner"), and list all questions with their answers in the report; a skipped one shows "Skipped" plus the assumption taken.

## 1. Gather the material (before judging anything)

- **Live UI**: open each key screen at desktop 1280×800 and phone 390×844 (tablet 820×1180 if relevant) and walk the main task. Give every screenshot an id (`signup-phone`). Hover and focus the main controls, tab through once, look at empty, error and loading states where you can reach them without sending anything real. Do not submit real forms, payments or messages.
- **With a shell**: `python scripts/inspect_ui.py URL --name home --sel cta=".hero .btn-primary" --sel email="#email" --out ./shots`. It saves a JPEG per viewport, prints each selector's box as % of the screenshot (use it for marks) and its computed styles (use them as current values), and runs the automatic checks; their pass counts feed `checks`. Run it once per key screen.
- **Without a shell**: take screenshots with the browser tool and read values with `getComputedStyle` / `getBoundingClientRect`. Estimate mark boxes in % from the screenshot and keep them generous.
- **Screenshots or Figma only**: say so in sources; colours read off a compressed image are approximate (`demo`), and nothing about hover, focus or keyboard can be observed.
- **Context**: design tokens, the owner's answers; for anything still unknown, state the assumption.

Write down the main task as a route of screens. Mark where you measured and where you are guessing. Name the **UI maturity** level from evidence (Broken, Usable, Consistent, Polished, Delightful) and say what blocks the next one.

## 2. Apply the lenses

Read `references/lenses.md` and go through all 12 lenses in 5 groups: look (hierarchy, layout and spacing, typography, colour and contrast), use (usability heuristics, navigation, forms, states and feedback), reach (accessibility, responsive and touch), words (microcopy and trust), system (design-system consistency). For each lens write 1-3 findings tied to something you saw or measured, and score it 0-100. Cite the WCAG criterion or Nielsen heuristic a finding rests on.

## 3. Prioritize

Collect all findings into one table:

| # | Issue | Lens | Evidence | Severity | Impact | Confidence | Ease | ICE | Type |

- Severity 1-4 (cosmetic, minor, major, critical) says how bad it is; ICE (Impact × Confidence × Ease, each 1-10) says what to do first. A severity-4 issue gets Impact ≥ 8.
- Type = **fix** (`opt`, make the current UI right) or **rethink** (`ex`, a different pattern or layout that needs a test).
- Label each finding **observed** (seen or measured) or **hypothesis** (needs a test, e.g. "users miss the export button").
- For every task record **where**: page or URL, viewport, CSS selector or screenshot id; and **change**: property, current value (measured), target value, the token to use. A task with no exact selector still names the screen and the shot.
- Put each issue on a screenshot as a mark (box in %, number = issue id). One issue can have marks on several shots.
- For the top 3, compare at least 2 alternative solutions, write the experiment with its risk type (value, usability, viability, feasibility) and a success threshold, and run a short pre-mortem: "it shipped and nothing improved - why?"; put the answer into the plan.
- Group repeated instances (14 small buttons) into one task with a list of selectors, not 14 tasks.

## 4. Output: two files from one audit.json

Read `references/report-spec.md`. Write the review as one `audit.json` that follows `references/audit.schema.json` (start from `assets/example-audit.en.json`): language, the report's own text (headlines that state their point), KPIs, checks, maturity, 12 lens scores, screens, shots with marks, issues with a `detail` entry each (with `where` and `change`), `plans` for the top 3, tokens, start answers, sources and the glossary. You write data only; the template draws every chart, table, mark and label and computes ICE, the health index, quick wins and confidence.

**1) Report for people.**
- **With a shell:** `python scripts/build_report.py audit.json report.html`. It runs `validate_audit.py` first and refuses to build on errors (an issue without evidence or `where`, ICE outside 1-10, a number with no source, a mark pointing at a missing issue, a top-3 fix without alternatives or pre-mortem), and embeds screenshot files as data URIs. Fix the data, not the template.
- **Without a shell** (Claude app without code execution): copy `assets/report-template.html`, set `<html lang>` and `<title>`, and replace the content of its `<script type="application/json" id="audit">` block with your JSON. Write `<\/` instead of `</` inside strings. Leave `src` out of shots you cannot embed: the template draws the marks on a placeholder frame. Check the rules from `validate_audit.py` yourself.

Interface labels come from the template's `UI` dictionary chosen by `<html lang>` (`uk`, `en`). Save `audit.json` next to the report: the next run compares against it. Deliver one self-contained HTML page: publish it as an artifact when an artifact tool exists, otherwise send the .html file.

**2) Hands-off for AI agents.** `python scripts/build_handoff.py audit.json handoff.md --json tasks.json`. It holds context, sources, design tokens, rules for the implementer and every issue as a task, ordered by ICE with dependencies first: evidence, where (page, viewport, selector, screenshot mark), current → target values, steps, acceptance criteria, how to verify, risks. Add `accept`, `depends` and `verify` to `detail` entries and top-level `rules` when the defaults are not specific enough. Without a shell, write the same structure by hand. Deliver it next to the report as files (not an artifact), together with the screenshots it references, and say in one line what it is for.

In chat, reply with 3-5 summary bullets, the link or files, and one line on what was checked.

## 5. Check before delivering

Never deliver a report you have not checked.

1. **Facts.** Every number in the text, KPIs, checks, `why` and `change.cur` must trace to a source in `sources`, a tool result or the owner's answers, and the arithmetic must hold. In Claude Code, give this check to a separate subagent that has not seen your reasoning: pass it `audit.json`, the `inspect_ui.py` output and the screenshots, and ask it to list every value it cannot trace and every mark that does not sit on the element it names. Elsewhere, do the pass yourself. Fix or remove what does not trace.
2. **Marks.** Open each screenshot with its marks (the built report, or look at the image and the boxes): every box must cover the element its issue is about.
3. **Script.** `node --check` on the template's main script if you edited anything beyond the JSON.
4. **Render**, when Python and a Chromium-based browser are available (`pip install playwright`, `playwright install chromium`): `python scripts/check_report.py report.html --out ./report-check`. It opens the page as desktop (1280px), tablet (820px, touch) and phone (390px, touch) and fails on page or console errors, sideways scroll, empty charts, KPIs or checks, broken screenshots or marks outside them, overlapping labels, tooltips that do not open on hover or tap or do not close on a second tap, table cells not wrapped in one `.cv`, filters that break the table. It saves screenshots, including dark mode.
5. **Look at the screenshots** it saved: overlapping labels, marks off target, cut-off badges, poor dark-theme contrast.
6. **Fix and re-check**, at most twice. If something still fails, say what in one line.
7. **No headless browser:** open the published page with any browser tool at desktop and narrow width and check the same list by looking. If no browser tool exists, say plainly which visual checks were not done.

## Rules
- Every finding must point to evidence (a screenshot, a measured value, a selector, the owner's words) or be clearly marked as a hypothesis.
- Measure, don't eyeball: current values come from computed styles or a tool, not from guessing pixels.
- Target values name a design token when one exists; do not invent a new colour or size when the system already has one.
- Prefer fewer, sharper fixes over long lists; group repeated instances.
- Separate fixes from rethinks; a healthy plan has mostly the first.
- Do not recommend dark patterns (fake urgency, confirmshaming, pre-checked consent, hidden costs, disguised ads) even if they would raise conversion; flag existing ones.
- Never invent evidence: no made-up analytics, user quotes, test results or testimonials, in findings or in suggested copy.
- When a fix changes copy (buttons, errors, headings), give 2 alternative wordings with a one-line reason each.
- If a check could not be run, show it with "no data" (`v: null`) instead of a number, and lower confidence.
- Lens scores are judgments: base each on findings, and be consistent (below 40 = big problems, 40-60 = partial, above 60 = solid).
