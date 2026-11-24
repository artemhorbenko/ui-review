# The 12 UI lenses

Go through every lens for every screen you captured. For each lens write 1-3 findings tied to something you actually saw (a screenshot region, a measured value, a selector), and score the lens 0-100: below 40 = big problems, 40-60 = partial, above 60 = solid. Scores are judgments; base each on findings and be consistent across screens.

Each lens has an icon id (`i`) and a group id (`g`) used in `audit.json`.

## Group `look` - Can people see what matters?

| Lens | `i` | The question | What to check |
|---|---|---|---|
| **Visual hierarchy** | `hier` | Does the eye land on the most important thing first? | One primary action per screen; heading sizes step down clearly; squint test (blur the screenshot: what stays visible?); competing CTAs of equal weight; F/Z reading pattern on content pages. |
| **Layout and spacing** | `grid` | Is there a consistent grid and spacing rhythm? | Spacing values on a scale (4/8 px or the product's tokens); alignment to one grid; related things closer than unrelated (proximity); line length 45-90 characters; crowding or dead space. |
| **Typography** | `type` | Is text easy to read at every size? | Body text ≥ 16 px on phone (≥ 14 px for dense UI); line height 1.4-1.6 for body; 2-3 sizes per screen, not 7; weights that mean something; truncation and wrapping of long words (and Cyrillic/German strings). |
| **Colour and contrast** | `color` | Does colour carry meaning, and can everyone read it? | WCAG 2.2 AA: text 4.5:1, large text (≥ 24 px, or ≥ 18.66 px bold) 3:1, UI parts and focus rings 3:1; one accent used for one meaning; status not shown by colour alone; dark mode. |

## Group `use` - Can people get the job done?

| Lens | `i` | The question | What to check |
|---|---|---|---|
| **Usability heuristics** | `heur` | Does the UI follow Nielsen's 10 heuristics? | Visibility of system status, match with the real world, user control (undo, cancel), consistency, error prevention, recognition over recall, flexibility, minimalism, error recovery, help. Name the heuristic in the finding. |
| **Navigation and IA** | `nav` | Do people know where they are and where to go? | Current page shown in nav; labels in users' words; depth of key tasks (clicks to the core action); back and breadcrumbs; search; nothing important only in a hover menu. |
| **Forms and input** | `form` | Can people fill it in without errors? | Visible labels (not placeholder-only); correct input types and `autocomplete`; inline validation after the field, not on every keystroke; error text that says how to fix; required/optional marked; one column. |
| **States and feedback** | `state` | Does every action get a clear response? | Hover, focus, active, disabled states; loading and skeletons; empty states that say what to do next; error and success messages; layout shift (CLS) when content loads. |

## Group `reach` - Does it work for everyone, everywhere?

| Lens | `i` | The question | What to check |
|---|---|---|---|
| **Accessibility** | `a11y` | Can people with disabilities use it? | Keyboard path and visible focus; landmarks and heading order; alt text; accessible names for icon buttons; `lang`; zoom to 200% without loss; reduced motion. Cite the WCAG success criterion (e.g. 1.4.3, 2.4.7, 2.5.8). |
| **Responsive and touch** | `resp` | Does it hold up on a phone and a tablet? | No sideways scroll at 360-390 px; touch targets ≥ 24×24 px (WCAG 2.5.8) and ideally ≥ 44×44 px; sticky elements that eat the screen; tables and long words; thumb reach for the primary action. |

## Group `words` - Do the words help?

| Lens | `i` | The question | What to check |
|---|---|---|---|
| **Microcopy and trust** | `copy` | Do labels, buttons and messages say what happens next, honestly? | Buttons as verbs with an object ("Create invoice", not "Submit"); error text in plain words; consistent terms; no fake urgency, confirmshaming, pre-checked consent or hidden costs (dark patterns); real proof, no invented testimonials. |

## Group `system` - Is it built from one system?

| Lens | `i` | The question | What to check |
|---|---|---|---|
| **Design-system consistency** | `sys` | Are the same things made the same way? | Count variants: button styles, radii, shadows, greys, font sizes, spacing values; hard-coded values instead of tokens; the same component behaving differently on two screens. Record the token each fix should use. |

## Supporting concepts

- **Severity** (Nielsen, 1-4): 1 cosmetic, 2 minor, 3 major (slows or confuses most users), 4 critical (blocks a task or excludes a group of users). Severity says how bad the problem is; ICE says what to do first.
- **UI maturity** (for the header strip, 0-4): Broken (a key task cannot be done) -> Usable (tasks work, with friction) -> Consistent (one system, few variants) -> Polished (states, details, accessibility) -> Delightful (motion, personality, anticipation). Name the current level from evidence, and say what blocks the next one. Polishing animations on a Broken product is itself a finding.
- **Squint test, 5-second test, first-click test**: cheap tests for hierarchy; use them as the "cheapest test" in plans.
- **Gestalt** proximity, similarity, alignment; **Fitts's law** (big and near = fast); **Hick's law** (more choices = slower); **Jakob's law** (people expect your UI to work like the others they use).
- **HEART** (Google) for choosing UI metrics: happiness, engagement, adoption, retention, task success.

If specialized skills or tools are installed (an accessibility audit, a design-system linter, a Figma connector), name them as the next step for a deep dive instead of duplicating their work.

## Weighting

Weight lenses by what the product is: forms and states matter most in a SaaS app; hierarchy, copy and responsive in a landing page; navigation and typography in a content site; accessibility always (it is a legal requirement in many markets: EAA in the EU since June 2025, ADA in the US). A severity-4 finding gets Impact 8 or more, so it lands near the top of the ICE ranking; `validate_audit.py` warns when it does not.
