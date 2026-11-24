# The 13 UI lenses

Scope: what the interface looks like and how its surface behaves. Task flows, forms, navigation logic and copy belong to **ux-review**; strategy, growth and business model to **product-lens-audit**. If you find something outside the scope, note it in one line in `text.dataP` and point to the other skill instead of making it an issue.

Go through every lens for every screen you captured at 360, 768 and 1280 px. For each lens write 1-3 findings tied to something you saw or measured (a screenshot region, a computed value, a selector), and score the lens 0-100: below 40 = big problems, 40-60 = partial, above 60 = solid. Scores are judgments; base each on findings and keep them consistent across screens.

Each lens has an id (`i`) and a group id (`g`) used in `audit.json`.

## Group `look` - Does the eye go where it should?

| Lens | `i` | The question | What to measure or check |
|---|---|---|---|
| **Visual hierarchy** | `hier` | Does the eye land on the most important thing first? | Heading sizes step down clearly (ratio between levels); one dominant element per screen; squint test (blur the screenshot: what stays?); competing elements of equal weight. |
| **CTA prominence** | `cta` | Is the primary action the most visible control, everywhere? | Size, colour, contrast and position of the primary button vs others; one filled primary per view; above the fold at 360 and 1280; label contrast ≥ 4.5:1 (or ≥ 3:1 for large text). |
| **Imagery and icons** | `img` | Do images and icons look like one set and earn their place? | One icon style (stroke vs filled, weight, size grid); image quality and crop at each width; decorative vs meaningful images (`alt=""` vs real alt); icons with ≥ 3:1 contrast (WCAG 1.4.11). |

## Group `structure` - Is there an underlying order?

| Lens | `i` | The question | What to measure or check |
|---|---|---|---|
| **Layout and grid** | `grid` | Do things sit on a consistent grid? | Content width and margins at each width; columns and gutters; edges that line up between sections; line length 45-90 characters. |
| **Spacing rhythm** | `space` | Do paddings, gaps and margins follow one scale? | Distinct spacing values (from computed styles) and how many fall on a 4/8 px scale; vertical rhythm between sections; proximity (related things closer). |
| **Typography scale** | `type` | Is there a clear, limited type scale? | Distinct font sizes and weights in use; ratio between steps; body ≥ 16 px on phones; line height 1.4-1.6 for body; nothing under 12 px. |

## Group `colour` - Does colour work and stay on-brand?

| Lens | `i` | The question | What to measure or check |
|---|---|---|---|
| **Colour and contrast** | `color` | Can everyone read it? | WCAG 2.2 AA: text 4.5:1, large text 3:1, UI parts and icons 3:1; text over images and gradients (measure the worst spot); status not by colour alone. |
| **Dark mode** | `dark` | If the product follows the system theme, does the dark version hold up? | `prefers-color-scheme` rules present; screenshot with dark emulated; contrast and images in dark. If there is no dark mode, say so and score what exists honestly (a light-only marketing site can score 60+ when nothing breaks under forced dark modes). |
| **Brand coherence** | `brand` | Does every screen look like the same brand? | Palette in use vs brand colours (count off-palette colours); logo use; one type family set; illustration and photo style consistent across pages. |

## Group `system` - Is it built from one system?

| Lens | `i` | The question | What to measure or check |
|---|---|---|---|
| **Consistency with its design system** | `sys` | Are the same things made the same way? | Count variants: button styles, radii, shadows, greys, font sizes; the same component looking different on two pages; values that match no token. Record the token each fix should use. |

## Group `behave` - Does it hold up across widths and over time?

| Lens | `i` | The question | What to measure or check |
|---|---|---|---|
| **Responsive behaviour** | `resp` | Does it work at 360, 768 and 1280 px? | No sideways scroll; nothing clipped or overlapped; tap targets ≥ 24×24 px (WCAG 2.5.8), ideally 44×44; fixed headers and banners as a share of the screen; images and tables at each width. |
| **Motion** | `motion` | Does motion help, and can it be turned off? | Autoplay carousels and looping animations; `prefers-reduced-motion` rules present; durations (150-400 ms for UI); nothing flashes more than 3 times a second. |
| **Perceived performance** | `perf` | Does the page feel stable and fast? | Cumulative layout shift (CLS ≤ 0.1), largest contentful paint (LCP ≤ 2.5 s, measured on your connection - say so), skeletons or loading states, images with width/height, fonts that swap without jumping. |

## Supporting concepts

- **Severity** (Nielsen, 1-4): 1 cosmetic, 2 minor, 3 major (hurts most users or one group badly), 4 critical (content cannot be read or used). Severity says how bad; ICE says what to do first. A severity-4 issue gets Impact 8 or more.
- **UI maturity** (header strip, 0-4): Broken (content unreadable or unusable at some width) -> Usable -> Consistent (one system, few variants) -> Polished (states, motion, dark, details) -> Delightful. Name the level from evidence and say what blocks the next one.
- **Squint test, 5-second test**: cheap hierarchy tests; good "cheapest test" entries in plans.
- **Gestalt** proximity, similarity, alignment; **Fitts's law** (big and near = fast to hit); **modular scale** (type sizes in a steady ratio such as 1.25).

## Weighting

Weight by what the product is: CTA prominence, hierarchy and imagery matter most on marketing pages; spacing, type scale and consistency in apps and dashboards; responsive everywhere. Contrast failures on text people need are at least severity 3.
