# Status

Living state of the work. Update at the end of every session. Public repo: no real site names, client data or private links here.

**Version:** 1.1.0 (2026-11-24)

## Done recently

- 1.1.0: scope narrowed to UI; 13 lenses in 5 groups; every page measured at 360, 768 and 1280 px.
- `scripts/probe.js`: one measuring probe for Playwright and browser tools (whole-page contrast, type/colour/radius/spacing scale, tap targets, unnamed icon links, dark-mode and reduced-motion rules, animations, CLS, LCP, fixed bars).
- Browser-only path: exact widths via a same-origin iframe when the browser window cannot be resized.
- Report template: new lens icons and groups; nested screenshot marks stay clickable.
- New fictional demo (Tallyo) with screenshots at three widths; English example audit and hands-off.
- First real run: public B2B SaaS marketing site, 4 pages × 3 widths, via browser only. See `evals/results.md`.
- Repo docs: `CLAUDE.md`, `STATUS.md`.

## In progress

- Nothing open in this repo.

## Next

1. Maintainer: share the EN demo artifact publicly, and create tags v1.0.0–v1.1.0 and a GitHub Release (the session cannot push tags or change artifact sharing).
2. Test in Claude Code desktop and in the Claude app (upload the ZIP).
3. Run trigger evals from `evals/trigger-evals.json` with the skill-creator skill.
4. Reduce contrast false positives in `probe.js` (visually hidden labels, layered backgrounds) and make LCP inside an iframe report "lead" automatically.
5. Test on a product with a real dark mode, a web app behind sign-in (read-only) and mobile-app screenshots only.
6. Optional Ukrainian demo built from the same fixture.

## Open questions

- Which real site becomes the public case study (owner consent needed)?
- Move the shared report core into its own repo once 2–3 sibling skills exist?
- Should `inspect_ui.py` also capture a design-token file (Figma variables, CSS custom properties) as a source?

## Links

- Public demo: EN https://claude.ai/artifact/NwoSocJV55ttWHtgK6VZAc (fictional "Tallyo"; sharing pending, see Next 1)
- Roadmap and ideas: kept in the maintainer's private plan doc.
