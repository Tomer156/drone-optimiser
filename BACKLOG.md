# Backlog

Known issues, stowed rather than fixed. Each one has been measured, not guessed. Ordered by
severity, with the evidence that established it so nobody has to re-derive it.

## Blocking / major

**Pro gate modal is not a dialog.** No `role="dialog"`, no `aria-modal`, focus is never moved into
it, no focus trap, and Escape does not close it — and it is the only route into Pro mode.
*Deferred at the user's request; revisit with whatever replaces the fake signup.*

**Tooltips are mouse-only.** 15 of 19 `data-tip` hosts are non-focusable `div`s, so the
plain-language explanations (including all six Required-vs-selected reasons) never reach a keyboard
user. The CSS already supports `:focus-visible`; the markup does not.
*Fix:* move `data-tip` onto the already-focusable element for the comparison rows and frame stats,
and add `tabindex="0"` only to the two chart headers. Two new tab stops instead of fifteen.

## Accessibility

**No toggle state is exposed.** Zero `aria-selected` and zero `aria-expanded` in the document. The
four flight-style chips, three goal chips and six collapsible step headers signal state through
background colour alone. (`aria-pressed` now exists on the Tooltips button only.)

**`role="tablist"` contains zero `role="tab"`.** The Results / Electronics / Calc chain group is
announced as a tab list with no tabs and no selected item. Either make the roles real or drop them.

**Slider tracks are 4 px tall.** Ten range inputs render at 243×4 against the WCAG 2.5.8 minimum
target of 24×24. The thumb is 13×13 with no padded hit area.

**13 decorative SVGs** are neither `role="img"` with a label nor `aria-hidden="true"`.

**Text cannot be resized.** Every size is an inline `px` value inside a `100vh; overflow:hidden`
shell, so OS text scaling and browser minimum-font-size have no effect. Page zoom is the only
route, and below ~1024px the comparison columns overprint.

## Design

**The slider fit-gradient is invisible and unexplained.** Adjacent zones measure **1.06:1**
(good vs med), 1.07:1 (good vs bad) and 1.12:1 (med vs bad) on a 4 px track, against DESIGN.md's
own 3:1 rule for graphics, with no legend anywhere. Forty physics evaluations per track and nine
tracks per render are spent producing a signal nobody can decode.
*Fix:* use the saturated `PAL` values at reduced alpha instead of the pastel `TINT` set, raise the
track, and add one tooltip explaining what the colours mean.

**Fit green is not rationed.** The Status-Only Rule is honoured — colour only ever means fit — but
in a passing build 14 separate elements carry the good tone at once, so "everything green" stops
reading as a signal. Consider restricting saturated green to the dots and leaving passing numbers
in ink.

**No responsive design.** One `@media` in the file and it is `@media print` inside the vendored
runtime. At 1024px the charts stack and axis labels clip; at 375px the sidebar takes 77% of the
width and the results column collapses.

**`prefers-color-scheme` and `prefers-reduced-motion` are never read.** Theme is not carried in the
share link either, so a shared build always opens in light with the donut animating.

**Empty tooltip guard.** Rows whose reason resolves to an empty string still carry `data-tip=""`.
The `:not([data-tip=""])` guard is in place, but new call sites should omit the attribute rather
than rely on it.

## Data

**One entry still mixes voltages.** `XING2 3110 900KV | 10.0x5.0x3` spans 24.91 V to 21.86 V. This
is sag within a single sweep, not two tests, so it is correctly left as one curve — recorded here
only so it is not "fixed" by mistake.

**Three AOS entries duplicate throttle values** at the same voltage (30,30,40,40 …), i.e. two runs
of the same test merged. Thrusts are close, so the curve shows small steps rather than a drop, and
the x-sort keeps it monotonic.

**One prop string has an unrecorded pitch.** `4.9x?x3` renders with a literal `?` mid-string. A
trailing unknown blade count is stripped; a mid-string unknown is not.

## Performance

**The arithmetic prune earns nothing.** The thrust/weight gate before the full evaluation removes
**644 of 70,941** candidates (1%). Real speedups have to come from narrowing the pack set per
motor, which changes which candidates are considered and so needs a deliberate decision.

**Yield primitive matters more than slice size.** `setTimeout(0)` measured **up to 1,004 ms** per
yield in an embedded/background view, which turned a ~2.5 s sweep into 20 s. The sweep uses a
`MessageChannel` post instead (**0.07 ms** measured). Do not switch it back to `setTimeout` or
`requestAnimationFrame` — the latter stops entirely in a hidden view.

**Progress is painted directly to the DOM, not through state.** A `setState` per slice cost ~100
full re-renders, each re-running `calc()` and repainting nine slider gradients. The label and bar
are written by hand and restored explicitly when the sweep ends.
