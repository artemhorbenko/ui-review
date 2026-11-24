# Results

Scores 1-5: **E** evidence (every finding traces to a measurement or screenshot), **L** location (selectors and marks point at the right element), **P** plan specific and implementable, **R** report renders on desktop, tablet and phone, **H** hands-off file works for an agent.

| Date | Version | Scenario | Product | E | L | P | R | H | What broke |
|---|---|---|---|---|---|---|---|---|---|
| 2026-11-24 | 1.0.0 | demo-fixture (skip questions) | Tallyo demo site | 5 | 4 | 4 | 5 | 4 | Playwright's mobile emulation zoomed the overflowing page out to 1,096 px and hid the sideways scroll; inspect_ui.py now keeps the layout viewport at the given width. Current → target table squeezed the property column on tablets; it now stacks below 1000 px. HTML tags in the hands-off Markdown were swallowed as HTML; they are now wrapped in code spans. |
