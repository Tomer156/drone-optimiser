---
name: Drone Optimiser
description: A dense single-screen tool that sizes a quadcopter from bench data and says whether the mission is achievable.
colors:
  ink: "#16181A"
  body: "#55534E"
  mut: "#5F5D57"
  dim: "#6A6761"
  quiet: "#D6D2CA"
  page: "#E8E7E5"
  card: "#FFFFFF"
  line: "#E7E4DF"
  fit-good: "#2E9E63"
  fit-med: "#B8801A"
  fit-bad: "#BE4230"
  fit-good-text: "#247C4E"
  fit-med-text: "#926515"
  ink-dark: "#F2F1EE"
  body-dark: "#C6C3BD"
  mut-dark: "#96938C"
  page-dark: "#101215"
  card-dark: "#1B1E22"
  fit-good-dark: "#5BC58C"
  fit-med-dark: "#D6A63A"
  fit-bad-dark: "#E0715C"
typography:
  display:
    fontFamily: "Spline Sans Mono, Spline Mono Fallback, monospace"
    fontSize: "34px"
    fontWeight: 400
    lineHeight: 1
    letterSpacing: "-0.04em"
  figure:
    fontFamily: "Spline Sans Mono, Spline Mono Fallback, monospace"
    fontSize: "26px"
    fontWeight: 400
    lineHeight: 1
    letterSpacing: "-0.04em"
  reading:
    fontFamily: "Instrument Sans, Instrument Fallback, sans-serif"
    fontSize: "16px"
    fontWeight: 600
    letterSpacing: "-0.015em"
  brand:
    fontFamily: "Instrument Sans, Instrument Fallback, sans-serif"
    fontSize: "15px"
    fontWeight: 600
    letterSpacing: "-0.015em"
  data:
    fontFamily: "Spline Sans Mono, Spline Mono Fallback, monospace"
    fontSize: "16px"
    fontWeight: 400
    letterSpacing: "-0.02em"
  title:
    fontFamily: "Instrument Sans, Instrument Fallback, sans-serif"
    fontSize: "13px"
    fontWeight: 600
    letterSpacing: "-0.005em"
  body:
    fontFamily: "Instrument Sans, Instrument Fallback, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Instrument Sans, Instrument Fallback, sans-serif"
    fontSize: "11px"
    fontWeight: 400
  micro:
    fontFamily: "Instrument Sans, Instrument Fallback, sans-serif"
    fontSize: "10px"
    fontWeight: 400
    letterSpacing: "0.1em"
  nano:
    fontFamily: "Spline Sans Mono, Spline Mono Fallback, monospace"
    fontSize: "9px"
    fontWeight: 500
rounded:
  sm: "6px"
  md: "8px"
  lg: "12px"
spacing:
  hair: "2px"
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "20px"
components:
  card:
    backgroundColor: "{colors.card}"
    rounded: "{rounded.lg}"
    padding: "14px 16px"
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.card}"
    rounded: "{rounded.sm}"
    padding: "10px"
    typography: "{typography.body}"
  chip:
    textColor: "{colors.label}"
    rounded: "{rounded.sm}"
    padding: "7px 4px"
    typography: "{typography.label}"
  tooltip:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.card}"
    rounded: "{rounded.md}"
    padding: "9px 11px"
    typography: "{typography.label}"
---

# Design System: Drone Optimiser

## Overview

**Creative North Star: "The Bench Sheet"**

This is an instrument, not a page. It reads like a lab worksheet a technician keeps open beside the test rig: everything on one screen, numbers in a monospace column so they align down the page, prose only where a number needs explaining. Density is the point. A user comparing 318 motor/prop/voltage combinations against 221 packs should never scroll to compare two figures.

The visual world came from a Claude Design comp and is settled. Instrument Sans carries the interface, Spline Sans Mono carries every measured value, and the surface is warm off-white paper rather than clinical grey. Colour is almost entirely absent: a three-tone fit palette (good / marginal / bad) is the only chroma, and it appears on values and status dots, never on whole cards.

Two modes share one layout. Auto hides every parts list and speaks in plain language; Pro exposes the catalogue, the checks and the calculation chain. The same panels occupy the same places in both.

**Key Characteristics:**
- One screen, no scrolling in the results area at the supported window sizes
- Monospace for every measured value; sans for every label
- Colour reserved for fit status; the rest is a warm grey ramp
- Panels are flat cards on a tinted page, never nested
- Dark mode is a real second theme with its own ramps, not an inversion

## Colors

A near-monochrome warm grey system with a single three-tone status palette.

### Primary
- **Ink** (`#16181A`): headings, primary values, the Optimise button, tooltip backgrounds. In dark mode it flips to **Paper Ink** (`#F2F1EE`).

### Secondary
- **Fit Good** (`#2E9E63`): passing status dots, donut arcs, slider track zones. Its text variant **Fit Good Text** (`#247C4E`) is used wherever the tone lands on type.
- **Fit Marginal** (`#B8801A`) / text variant (`#926515`).
- **Fit Bad** (`#BE4230`): already AA as text, so it has no separate variant.

### Neutral
- **Page** (`#E8E7E5`) / **Card** (`#FFFFFF`): the two surfaces, separated by 1.24:1. That ratio is the only thing distinguishing a card from the page, since the system has no shadows and no card borders. Dark mode: `#101215` / `#1B1E22`.
- **Body** (`#55534E`), **Muted** (`#5F5D57`), **Dim** (`#6A6761`): the text ramp, in that order of prominence.
- **Quiet** (`#D6D2CA`): pending status dots and inactive slider track.
- **Line** (`#E7E4DF`): dividers and card edges.

### Named Rules

**The Two-Palette Rule.** Every colour is declared per theme. Nothing is inverted, filtered, or reused across themes. The mass donut ramp had one shared definition and its darkest tone rendered at 1.06:1 on the dark card, invisible. Both ramps are separate and spaced for separation between neighbours (16-20 dL* per step, worst neighbouring pair 1.63:1 light and 1.70:1 dark). Donut segments are judged against each other rather than the card, so the far step is allowed to sit under the 3:1 an isolated graphic would need.40:1), and every step clears 3:1 against its own card.

**The Text Variant Rule.** The fit palette exists twice: saturated for dots, arcs and track gradients (which need 3:1), and one step darker for anything that is type (which needs 4.5:1). Never put the graphics tone on text.

**The Status-Only Rule.** Colour means fit. It never means category, decoration, or emphasis. Mass categories are told apart by a grey ramp plus a legend, not by hue.

## Typography

**Interface Font:** Instrument Sans (with a metric-matched local fallback)
**Data Font:** Spline Sans Mono (with a metric-matched local fallback)
**Notation Font:** Georgia italic, used only in the Pro calculation chain

**Character:** A neutral grotesque for the interface and a mono for every number, so figures align in columns and change without reflowing. The mono is the voice of measurement; the sans never states a measured value.

### Hierarchy
- **Display** (400, 34px, -0.04em, mono): the verdict. Flight time, and the motor efficiency figure beside it. There is one class of display figure and both charts use it.
- **Figure** (400, 26px, mono): the take-off mass total in the donut.
- **Brand** (600, 15px, -0.015em): the app name only.
- **Title** (600, 13px): card headings.
- **Body** (400, 12px, 1.5): prose, control labels, buttons.
- **Label** (400/600, 11px): secondary labels, chips, comparison row names.
- **Micro** (400/600, 10px, 0.1em when uppercase): metadata, axis ticks, column headers, step names.
- **Nano** (500, 9px, mono): step badges and diagram dimension labels.

### Named Rules

**The Nine-Step Rule.** Nine sizes, no more: 34 / 26 / 16 / 15 / 13 / 12 / 11 / 10 / 9. Half-pixel steps (10.5, 11.5, 12.5) are not a hierarchy, they are noise. Pick the nearest existing step.

**The Measured-Value Rule.** If it is a number that came from the physics or the database, it is mono. If it is a word, it is sans.

**The Dark Compensation Rule.** Dark mode adds `letter-spacing: .004em` at the body level. Light strokes on a dark ground bloom and close up the counters at 10-11px.

## Layout

Three regions, fixed: a **288px sidebar** (the wizard, its own scroll), a **results area**, and a **268px rail** inside it. The results area holds two equal columns plus the rail.

Row order in the results area, which is settled and should not be reshuffled:

1. Motor efficiency | Flight time (equal peers, same height, same plot area)
2. Required vs selected | Design flags
3. Selected components (Auto) / Checks (Pro), full width
4. Rail, right: Take-off mass, Layout, Contribute

**Spacing scale:** 2 / 4 / 8 / 12 / 16 / 20. 12px is the gap between cards and the default gap inside them; 8px groups rows within a card; 16-20px separates a card's distinct blocks. Card padding is 14px 16px, one step tighter (12px 16px) in the rail.

### Named Rules

**The Supported-Window Rule.** The No-Scroll Rule holds at **1152x700 and above**, which is where
it has been measured. Below that the results column is too narrow to keep Required-vs-selected and
Design flags side by side; the row wraps, the section doubles in height, and the results area
scrolls. At 1024x768 that is 352 px of overflow. This is a width limit, not a height one, and the
honest fix is a reflow for narrow windows rather than more squeezing. The sidebar rail scrolls
below about 780 px of height and says so with a fade.

**The No-Scroll Rule.** The results area does not scroll. It is verified at **1280×860 and above, and 1440×900**, in both modes, with zero overflow. Below roughly 1280×820 the content genuinely exceeds the window and it scrolls; that is the honest outcome, not a target to defeat by shrinking content further.

**The Level-Bottoms Rule.** The last card in the results column ends level with the last card in the rail. This is not achievable with flex: the charts would have to grow into a height that their own growth defines, and that feedback loop is what previously made them overshoot the region and paint over the panels below. `syncChartHeight()` computes it instead: `chart height = region inner height − (the column's other cards + their gaps)`, clamped 200-620px, with one shrink-only corrective pass. It runs on every render and whenever the available height changes.

**The Charts-Absorb Rule.** Leftover vertical space goes to the two charts and nothing else. Every other panel sits at its content height. Taller plots are the only thing on this screen that improves with height; everything else would just gain padding.

**The Paired-Charts Rule.** The two charts stay side by side. Their wrappers use a 240px basis so they do not stack until roughly a 1100px window; stacked, they double the height they contribute and force a scroll.

**The Mass-Outranks-Layout Rule.** In the rail, Take-off mass is always taller than Layout. It is not left to leftover space: the donut has a 148px floor, which puts the mass card structurally above the layout card at any window size.

## Elevation & Depth

Flat. There are no shadows on cards. Depth comes entirely from tonal layering: a tinted page (`#F1F0ED`) with white cards on it, and dividers at `#E7E4DF`. The only shadow in the system is on the shared tooltip (`0 4px 14px rgba(0,0,0,.16)`), because it floats above content and needs to read as a separate plane.

### Named Rules

**The Flat-Card Rule.** Cards are distinguished by fill and radius, never by shadow or border. Do not add elevation to make a panel feel important; move it or resize it instead.

## Shapes

One radius family: **12px** for cards and dialogs, **8px** for tooltips and popovers, **6px** for buttons, chips, badges, inputs and selects. Three sub-tokens exist and are deliberate: **99px** for the mode pill, **5px** for the logo mark, **2px** for slider tracks and scrollbar thumbs. Nothing else. Status dots are 5-7px circles. The donut is an 11-unit stroke on a 140-unit viewBox, with rounded caps on segments large enough to take them.

The frame diagram is a square X-quad schematic drawn at 1:1 or below, never scaled above its authored size, with `vector-effect="non-scaling-stroke"` on every element so weights hold at any size and its dimension labels rendered as HTML overlays so they stay 10px regardless of the drawing's scale.

## Components

### Buttons
- **Shape:** 6px radius, 10px padding, 12px body type at weight 500.
- **Primary:** ink fill, card-coloured text. Hover shifts to `inkHover` (`#000000` light, `#FFFFFF` dark).
- **Secondary:** card fill with a `grid2` border; hover darkens the border to ink.
- **Busy state:** the Optimise button paints "Comparing 0%" through to "Comparing 100%" with `aria-busy`, sets `disabled` so a second click cannot queue a second sweep, and announces the result through a polite live region. The sweep blocks the main thread for **about 2.5 s** on a cold load (321 motor/prop/voltage entries x 221 packs = 70,941 candidates, ~103,000 bench interpolations). A warm repeat with unchanged inputs is near-instant because the interpolation is memoised.

### Chips
- Flight style, optimise goal, mode toggle. 6px radius, 11px label, 7px 4px padding.
- Selected chips take the `chip` surface with ink text; unselected are transparent with muted text.

### Cards
- 12px radius, flat fill, 14px 16px padding (12px 16px in the rail), 12px internal gap.
- Card titles are 13px/600, top-left, first element in the card.

### Inputs
- Sliders: 4px track, 13px thumb with a 1.5px ink border. The track carries a fit-coloured gradient showing where in the range the build passes.
- Selects and text inputs: 6px radius, 1px `fld-bd` border, 12px type.
- Focus: a 2px `fld-fg` outline at 2px offset, on `:focus-visible` only.

### Tooltip (signature)
One tooltip for the entire app, via a `data-tip` attribute and a single CSS rule. Ink background, card-coloured text, 8px radius, 9px 11px padding, 11px/1.5 type, 240px max width, and it appears on keyboard focus as well as hover. `data-tip-end` anchors it to the right edge for the rail so it cannot run off screen.

### Named Rules

**The One Tooltip Rule.** There is exactly one tooltip mechanism. Native `title` attributes cannot be styled to match, and a second hand-built popover drifts. Every hint uses `data-tip`. An icon-only control that loses its `title` must gain an `aria-label`.

**The No-Formulas-In-Tooltips Rule.** Tooltips explain in plain language what a number means and what to do about it. Formulas live in the Pro calculation chain, nowhere else.

## Do's and Don'ts

### Do:
- **Do** put leftover vertical space into the charts, and nothing else.
- **Do** compute a height in JS when the value depends on sibling content. Flex cannot size an element against a container that its own size defines.
- **Do** give every colour a per-theme value and check it against its own card: 4.5:1 for text, 3:1 for graphics.
- **Do** keep both chart cards identical in height, plot area and figure size. They are peers.
- **Do** state a measured value in mono and its label in sans.
- **Do** use the nine type steps and the six spacing steps. Snap to the nearest.
- **Do** write advisories in Auto mode about things Auto can actually change: the target, the altitude, the flight style, the mass sliders.

### Don't:
- **Don't** use em dashes in any user-facing text.
- **Don't** reshuffle the panel order. It has been set deliberately and changing it cascades into every height calculation.
- **Don't** give a card `flex-grow` to make it match a neighbour's height once it is no longer beside that neighbour. Two leftover `flex: 1 1 auto` declarations from an earlier arrangement caused the charts to lose their slack.
- **Don't** count a `display: none` sibling when computing gaps. The components card and the checks card are siblings with one hidden per mode, and CSS lays no gap against a hidden item.
- **Don't** reach for a `ResizeObserver` in `componentDidMount`. The template has not rendered, so it attaches to nothing, and the runtime swaps nodes on re-render.
- **Don't** scale an SVG's text with the drawing. Dimension labels belong outside the SVG so they hold their size.
- **Don't** add a shadow to a card, or a coloured left border to a panel.
- **Don't** put a formula in a tooltip.

## The Two-Filenames Rule

`pro-7f3k9.html` is a byte-identical copy of `index.html`. There is one source; only the name it is
served under differs. The page reads its own filename at boot (`window.__PRO_BUILD`) and, on the
`pro-` name, starts in Pro mode with no sign-up gate and injects a `noindex` meta.

**Any change to `index.html` must be followed by `cp index.html pro-7f3k9.html`.** A diff between
the two files is always a mistake.

Share links never carry the Pro filename. `buildLink()` writes `<dir>/index.html?b=<payload>` and
forces `mode: 'auto'` into the payload, so a recipient lands on the public page with the build
populated, whoever generated the link. The old `#b=` form is still parsed so links already sent
keep working.

## The Visible-Pro Rule

The Auto/Pro toggle stays on the public page, and so does the gate behind it. Clicking Pro opens
the sign-up dialog, which links to the Typeform and leaves the visitor in Auto; it never grants
Pro. Pro itself lives only at `pro-7f3k9.html`.

This is deliberate. The toggle is not a broken control that fails to switch modes: it is how a
visitor finds out Pro exists at all, and the route into signing up for it. Do not remove it on the
grounds that it "never succeeds" — succeeding is not its job.
