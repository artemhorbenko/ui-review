# ui-review — notes for Claude and contributors

Start every session by reading this file and STATUS.md, then continue from Next. End every session by updating STATUS.md and committing.

A public Claude skill (Claude Code plugin + Claude app skill ZIP) that reviews the visual interface of a site or app through 13 UI lenses at 360, 768 and 1280 px, and outputs two files from one `audit.json`: a visual HTML report with annotated screenshots for people, and a hands-off brief (`handoff.md` + `tasks.json`) for AI agents with page, viewport, selector, screenshot mark and current → target values. Scope is UI only: flows belong to `ux-review`, strategy to `product-lens-audit`.

## Layout

```
.claude-plugin/marketplace.json        this repo is a plugin marketplace
plugins/ui-review/                     the only folder that ships to users
  .claude-plugin/plugin.json
  skills/ui-review/
    SKILL.md                           the process Claude follows
    references/                        lenses, data sources, report spec, audit.schema.json
    assets/                            report-template.html, example audit + hands-off, demo/ screenshots
    scripts/                           probe.js, inspect_ui, validate_audit, build_report, build_handoff, check_report
evals/                                 scenarios, trigger prompts, results log (anonymised), demo-site fixture
docs/                                  README screenshots
ui-review-skill.zip                    Claude app upload, rebuilt on every skill change
CLAUDE.md, STATUS.md, CHANGELOG.md     repo docs; never move them into plugins/
```

## Rules

- Respond to the maintainer in Ukrainian; code, docs and commits in English.
- Never invent numbers. Every size, colour, ratio and count comes from `probe.js` / computed styles; missing data shows as "no data" and lowers confidence.
- Review only the production domain the user names; ignore other subdomains (staging, old A/B-test sites) unless the user confirms they are live.
- Real reviews stay private (artifacts or local files). Nothing in this repo may name a real reviewed site, client data or private links; log runs in `evals/results.md` anonymised.
- Public demos use fictional products only (the "Tallyo" fixture in `evals/fixtures/demo-site/`).
- Claude writes only `audit.json`; the template and scripts render everything. Change the template, not the data, when layout breaks.
- Keep `SKILL.md` short; details go to `references/`.
- Use data sources read-only. The probe only loads and reads pages; never submit real forms, sign up, pay or send messages.

## Build and check

```
S=plugins/ui-review/skills/ui-review
(cd evals/fixtures/demo-site && python -m http.server 8765 &)       # fixture must be served over http
python $S/scripts/inspect_ui.py http://localhost:8765/index.html --name home --out shots
python $S/scripts/validate_audit.py audit.json
python $S/scripts/build_report.py audit.json report.html
python $S/scripts/build_handoff.py audit.json handoff.md --json tasks.json
python $S/scripts/check_report.py report.html --out ./report-check   # needs playwright + Chromium
```

Before committing a template or script change, run validate, build_report, build_handoff and check_report on `assets/example-audit.en.json` (also with `"lang": "uk"`), and check that a deliberately broken input fails. Regenerate `assets/example-handoff.en.md` when `build_handoff.py` changes.

## Release

1. Bump the version in `.claude-plugin/marketplace.json` and `plugins/ui-review/.claude-plugin/plugin.json`.
2. Add a section to `CHANGELOG.md` (user-facing changes only).
3. Rebuild the ZIP: `rm -f ui-review-skill.zip && cd plugins/ui-review/skills && zip -qr -X ../../../ui-review-skill.zip ui-review -x '*/__pycache__/*'`
4. `claude plugin validate .`
5. Commit, push; tags and GitHub releases are created by the maintainer.

## Related repos

Same report core and design: `product-lens-audit` (source of the shared core), `seo-audit`, `qa-audit`, `ux-review`, `competitor-teardown` (all under github.com/artemhorbenko). Shared core changes are made in product-lens-audit first, then copied here; never edit the sibling repos from this one.
