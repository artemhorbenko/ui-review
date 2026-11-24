# Evals

- `evals.json` - end-to-end scenarios: what the run must do (`expectations`) and must not do (`forbidden`). Run each in a fresh session with the plugin installed, then grade the result against the lists.
- `trigger-evals.json` - prompts that should and should not start the skill. With the skill-creator skill installed, ask it to run trigger evals on `plugins/ui-review/skills/ui-review` with this file; it can also tune the description.
- `fixtures/demo-site/` - the fictional "Tallyo" pages with deliberate UI problems. The demo report and hands-off file in `assets/` were made from it (served over http so stylesheets are readable), so it doubles as a regression test: a run on it should find the same problems with the same numbers.
- `results.md` - one row per run.

Every report must also pass the automatic checks:

```
S=plugins/ui-review/skills/ui-review
python $S/scripts/validate_audit.py audit.json
python $S/scripts/check_report.py report.html
```

Reproduce the demo measurements:

```
(cd evals/fixtures/demo-site && python -m http.server 8765 &)
python $S/scripts/inspect_ui.py http://localhost:8765/index.html --name home --out shots
python $S/scripts/inspect_ui.py http://localhost:8765/pricing.html --name pricing --vp desktop=1280x800 --out shots
```

Real sites stay private: record the scenario and the scores here, not the site's data.
