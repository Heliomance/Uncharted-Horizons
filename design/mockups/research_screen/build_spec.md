# Research screen: final build spec (Uncharted Horizons, Unciv styling)

## 0. Basis

**Concept chosen.** The base is the Focus Ledger, which scored highest on all three lenses (7.5 / 7.5 / 7.5). Ideas grafted from the other two concepts:
- From Direction A:
  - The status bodies: Unciv's own state fills, a solid/dashed/dotted border ladder, a glyph on every revealed status, and a distinct shape for Moment passed (a radius-4 "window").
  - A compact funding header frozen at the top left.
  - Select, describe, act in the bottom bar, with a full action matrix.
  - Consistent Endeavour figures (5,340 Insight; 3,415 = 5 × 683 = 64%).
  - The confirmation popup for switching away from an Endeavour.
- From the Focus Board:
  - The content corrections, including the declared lands.
  - RC03 as Not yet reachable, and QP09/QP10 at turn 231.
  - The rule that the Endeavour price is built only from true multipliers.
  - The status-phrase table.
  - Ability state folded into the funding description.

**Every must_fix is applied:**
- MS02 is shown as "Nanotechnology".
- The queue advances on revealed rows only.
- The FTL prototype is never named here.
- No "since turn N" anywhere.
- The state corrections are applied and the fold re-measured.
- The Endeavour total excludes Truth multipliers and detour margins.
- Not yet reachable has its own chip and count.
- The lands are declared.
- Every focus is visible at once.
- Revealed rows show conjecture, never effects.
- W19 text is static.
- Action buttons are 290 px wide.
- Amber no longer means two things.
- A focus run that wraps keeps its label column.
- The list hint is shortened to 197 px.
- DejaVu Sans is embedded.
- The phone artboard is landscape at 600 virtual px, with 44-px targets.

**How it was measured.** I built a static measurement prototype in Chromium with DejaVu Sans and the corrected data. Every geometry figure below comes from it. It is a measuring aid only, not the build.

**Decisions taken (stated, not reopened):**
- The candidate discovery model: occurrence windows, and an idea occurring does not reveal it.
- Glimpses work as now.
- Status 4 is worded "Its moment passed — only an Endeavour is certain".
- No odds, no hidden meter fractions, no window lengths or closing times.
- No tiers on revealed rows. Rare and Unique are marked on owned rows only.
- No per-focus spread figures: only the funded share and the total spread.
- Unknown breakthroughs leave no trace.
- One funding target at a time: a focus, or an Endeavour in the slot.
- A focus queue exists (R51).
- The FTL screen is separate, reached by a button (R134).

## 1. Global rules

**Artboard and units**
- 1440 × 810 Unciv virtual px: the Large size, 800-px virtual height at 16:9.
- Body and every surface are #000033.

**Font**
- Embed a Latin subset of DejaVu Sans as an inline `@font-face` in `<helmet><style>`:
  - family name "DejaVu Sans UH";
  - source `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf`.
- Subset command: `pyftsubset … --unicodes="U+0020-007E,U+00A0-00FF,U+2013,U+2014,U+2018,U+2019,U+201C,U+201D,U+2022,U+2026,U+2190-2193,U+2605,U+2713,U+2717,U+25BE,U+00D7,U+2212" --flavor=woff2 --layout-features='kern,liga'`.
  - That gives 21,412 bytes, or 28,552 characters of base64. A test subset is at `/tmp/claude-0/-home-user-Uncharted-Horizons/ffab2c8f-97b2-5cca-83ad-f0d7b939b828/scratchpad/final_spec/dv.woff2`.
- Stack: `'DejaVu Sans UH','DejaVu Sans',sans-serif`. Never list Verdana.
- One weight, regular. No bold, no italic.
- Sizes are only 14 px (names, tags, body) and 18 px (labels, titles, buttons). Nothing is smaller.

**Template and code**
- Only one `<style>` block is allowed, in `<helmet>`. It holds:
  - the `@font-face`;
  - the scrollbar knob: `::-webkit-scrollbar{width:10px}`, thumb #334D80 with radius 5, transparent track; plus `scrollbar-color:#334D80 transparent`;
  - `:hover` and `:focus-visible` rules on the fixed class names `uh-chip`, `uh-btn` and `uh-row`.
- Everything else is inline style.
- Every clickable element is a real `<button>`.
- Glyphs are inline stroke SVG chosen with `<sc-if>`.
- No emoji. No script-built DOM.

**Contrast and colour**
- Text contrast is at least 4.5:1 everywhere. The lowest is 5.18:1, the past-era band label.
- Every status differs by fill lightness, border pattern, shape and glyph, and is named in text. Hue never works alone.

## 2. Palette

Hex values come from the style extraction unless marked NEW. Contrast is WCAG.

**From the extraction**

| Hex | Role | Contrast / note |
|---|---|---|
| #000033 | background; studying and badge text | white on it 20.04 |
| #FFD700 | Owned fill | — |
| #4893AF | Being studied fill; funded focus row and pill; under-study badge; funded run-label rule | navy on it 5.79 |
| #0E5C56 | Awaiting fill; queued focus rows; current-era band header; era pill | white on it 7.82 |
| #111111 | Moment passed fill; future-era band; popup | #B3B3B3 on it 9.01; white on it 18.88 |
| #B3B3B3 | chip borders; secondary text on navy; segment counts | 9.56 on navy; 6.70 on #252B3E |
| #334D80 | buttons; Endeavour body; FTL tag; dividers; scroll knob; run-label rule | white on it 8.35 |
| #252B3E | inactive segments; disabled buttons; Superseded and Path not taken tags | white on it 14.06 |
| #65DC72 | button hover, text #404040 (5.94); met mark ✓ | 11.48 on navy |
| #409955 | button pressed | text #000033 there (navy on #409955 is 5.6; Unciv's white is 3.56, a transient state) |
| #FFAF00 / #782E10 | past-era band header and label | 5.18 |
| #7F3200 | Rare tag, white text | 8.90 |
| #3F1046 | Unique tag, white text (Unciv's Medieval era icon colour) | 15.28 |
| rgba(0,64,133,0.75) | queue-order disc, white numeral | 12.71 over navy; 9.63 over the #0E5C56 row |
| #FF0000 | unmet mark ✗ (Unciv Color.RED) | 5.01 |
| #3A98DB | keyboard focus ring, 2 px (Unciv skin selection colour) | 6.5 non-text |
| #19263F | 1-px edges of dividers | — |

**NEW colours**

| Hex | Role | Contrast / justification |
|---|---|---|
| #6B4300 | owned name (Unciv's #9A6210 darkened); Dead end tag fill, with #FFD700 text | 6.17 on #FFD700, where Unciv's own value is 3.63 |
| #9C9CB4 | Path not taken name and glyph | 7.47 on navy; a faded light-on-navy that the extraction lacks |
| #6A6A8C | Path not taken dashed border | 3.87, decorative |
| #FFFFFF | text; New tag fill, with navy text (20.04) | — |

**Fill lightness ladder**
- Owned 0.699, then being studied 0.253, then awaiting 0.084, then Moment passed 0.006 (charcoal window), then Not yet reachable and Path not taken (no fill).
- The Endeavour body #334D80 is 0.076, close to awaiting. It is told apart by its solid 2-px white border, its pyramid glyph, the word tag "Endeavour 64%" and its own section.

## 3. Layout at 1440 × 810

Coordinates are x, y, w × h. Vertical dividers are 3 px: #19263F, #334D80, #19263F.

### 3.1 Left column

The column is 0,0 252 × 810, full height. The vertical divider sits at x 252–255 and runs full height.

**Funding header**
- A `<button>` at 8,4 236 × 76. Clicking it selects "funding".
- Row 1 (y 4–28): a 16-px flask glyph in white at x 11, then "853 Insight a turn" at 18 px white at x 30 (160 px wide).
- Row 2 (y 30–58), the funding pill, 236 × 28, radius 14:
  - Focus funded: fill #4893AF, 1.5 px #B3B3B3 border, navy 14-px text.
    - A 16-px radio-on glyph at x 13: a 1.5 px navy ring with a 7-px navy dot.
    - "Quantum Physics" at x 35.
    - "80% · 683" right-aligned, padding-right 8.
  - Endeavour (A3): fill #334D80, 2 px #FFFFFF border, white text.
    - Line at y 32–49: the 16-px pyramid disc glyph, "Superconductivity", and "64%" right-aligned.
    - Below it, a 4-px bar from x 29 to the inner right edge: track rgba(255,255,255,.25), white fill to 64%, and 1-px #000033 ticks at 25%, 50% and 75%.
  - FTL prototype (spec only): the same body with "FTL prototype" and "38%". It never names the drive or its hypothesis.
- Row 3 (y 60–80): a 236 × 20 pill, radius 10, 1 px dashed #B3B3B3, no fill, 14-px #B3B3B3 text.
  - "Spread to other foci" at x 18.
  - "20% · 171" right-aligned.
  - It is unchanged during an Endeavour.
- Before Specialization of Labor (spec only), the rows read "50% · …".
- A one-off push (R53, spec only) appends " · +N push" to row 1.

**Focus list**
- At 8,84, 236 wide. It is `role="radiogroup"` labelled "Fund a focus".
- 33 rows, each 20 tall with a 1-px gap (pitch 21), radius 10. They end at y 777. Thirty-four foci would end at y 798, so the list never scrolls on desktop.
- Order is alphabetical:
  Aeronautics, Animal Husbandry, Chemistry, Computing, Construction, Electricity, Electronics, Energy Systems, Farming, Fire, Foraging, Genetics, Materials Science, Mathematics, Mechanics, Medicine, Metallurgy, Mining, Nuclear Physics, Observation, Optics, Philosophy and the Arts, Quantum Physics, Relativity & Cosmology, Rocketry, Seafaring, Social Organization, Stonework, Textiles & Materials, Thermodynamics, Trade, Warfare, Water Management.
- Row anatomy (padding 0 4 0 3), left to right:
  - A radio `<button role="radio" aria-checked>`, 22 × 20, holding a 14-px circle with a 1.5-px ring.
  - The name `<button>`: 14 px, flex 1, left-aligned, line-height 20. It ellipsises only as a guard; the measured worst case is 217 of 236 px.
  - Optional items pushed right, each with margin-left 4:
    - the pyramid glyph (16 px), on the focus holding the Endeavour;
    - a "New" tag: 15 tall, radius 7.5, padding 0 5, #FFFFFF fill, navy 14-px text;
    - the under-study badge: min-width 18, height 15, radius 7.5, #4893AF, navy 14-px numeral, padding 0 4. On the funded row it adds a 1-px #000033 ring.
    - the queue disc: 16-px circle, rgba(0,64,133,.75), 1.5 px #FFFFFF border, white 14-px numeral.
- Row states:

| State | Fill | Text | Radio |
|---|---|---|---|
| Plain | none | #FFFFFF | #B3B3B3 ring |
| Funded | #4893AF | #000033 | #000033 ring with a 6-px #000033 dot |
| Queued | #0E5C56 | #FFFFFF | plain ring, plus the queue disc |
| Holds the Endeavour | as plain | as plain | plain, plus the pyramid glyph |

  - Selected: add `box-shadow: inset 0 0 0 2px #FFFFFF`.
  - Hover, on unfilled rows only: #252B3E.
- Hint at 11,786, shown only while the list ends above y 780: a 14-px radio glyph in #B3B3B3, then "funds · right-click queues" at 14 px #B3B3B3 (197 px in all).

### 3.2 Top row of the board

**Status filter**
- At 271,8, height 30. Five segments, each a `<button aria-pressed>`, gap 4, single choice. Pressing the pressed one clears it; none pressed means all are shown.
- Segment style: 30 tall, radius 15, padding 0 11, 14 px. Content is the status glyph, 6 px, the label, 6 px, and the count.
  - Inactive: #252B3E, count #B3B3B3.
  - Pressed: #334D80, `inset 0 0 0 1.5px #FFFFFF`, count #FFFFFF.
- Measured x and width at turn 226:

| Segment | x | Width |
|---|---|---|
| Being studied 26 | 271 | 164 |
| Awaiting the idea 6 | 439 | 179 |
| Not yet reachable 2 | 622 | 182 |
| Moment passed 24 | 808 | 177 |
| Owned 191 | 989 | 124 |

  The segments end at x 1113.
- Counts are the rows of that status in the current view: the whole board, or one focus in the focus view.

**Era pill**
- A `<button>`, right-aligned to x 1424, at 1162,11 262 × 24.
- 1 px #FFFFFF border, #0E5C56 fill, padding 0 10, 14 px white.
- Text: "Modern era · 5 of 6 toward Atomic". At turn 231: "Atomic era · 2 of 4 toward Space".

### 3.3 Board

**Scroll pane**
- 271,46, 1163 wide, padding-right 10, `overflow-y:auto`. The content width is 1143 (x 271–1414).
- The native 10-px knob sits at x 1424–1434. In A1 it measures 211 px (640 / 1942).
- The viewport is y 46–686 (640 px).
- Scrolling is vertical only; nothing scrolls sideways.

**Section**
- `margin-bottom:4px`.
- Header: a `<button aria-expanded>`, `display:flex;align-items:center;height:24px;margin-bottom:2px`. Clicking it collapses or expands the section, and the count stays visible. It contains:
  - the status glyph;
  - the title, 18 px white, margin-left 8;
  - the count, 18 px #B3B3B3, margin-left 8;
  - a chevron, 10-px stroke #B3B3B3, margin-left 6: ▾ open, ▸ collapsed;
  - the reason, 14 px #B3B3B3, margin-left 14.
- Body: `display:flex;flex-wrap:wrap;gap:3px 12px;align-items:flex-start`.

**Focus run (hanging indent)**
- Container: `display:flex;align-items:flex-start;max-width:100%`.
- Label: a `<button>` that selects the focus. `flex:none;height:22px;line-height:22px;padding:0 6px 0 7px;border-left:2px solid #334D80;color:#B3B3B3;14px`.
  - Funded focus: text #FFFFFF, border-left #4893AF.
  - Selected focus: text #FFFFFF, `box-shadow:inset 0 0 0 1px #FFFFFF`.
- Chips: `display:flex;flex-wrap:wrap;gap:3px 4px;min-width:0`.
- A run longer than a line takes a whole line and wraps under its first chip, so a continuation line never lacks its focus.

**Order**
- Runs are alphabetical by focus.
- In live sections, chips are ordered by era, then name.
- In owned bands, chips are ordered by discovery turn, with Paths not taken last.
- The pitch is 25 px per line: 22-px chips and a 3-px gap.

**Sections, top to bottom**
1. "Grand Endeavour" (only while one runs; A3). One inline line, 24 px: the glyph, the title, the Electricity run with its single chip, then the reason "takes the funded share until it is complete".
2. "Being studied". Reason: "each takes a share of its focus’s Insight every turn".
3. "Awaiting the idea". Reason: "gets no Insight until the idea occurs — it still may".
4. "Not yet reachable". Reason: "a prerequisite must be discovered first".
5. "Moment passed". Reason: "Its moment passed — only an Endeavour is certain".
6. "Owned" with its count. Reason: "newest era first · 2 paths not taken · 1 unique · 2 rare · 2 superseded · 1 dead end".
   - Then one band per era, newest first. Each band header is a `<button aria-expanded>`: `width:100%;height:24px;border:1px solid #FFFFFF;padding-left:10px;font 18px;margin:6px 0 5px`, followed by " · N" at 14 px with margin-left 8.
   - Band colours, relative to the current era:

| Era | Fill | Label |
|---|---|---|
| Past | #FFAF00 | #782E10 |
| Current | #0E5C56 | #FFFFFF |
| Later | #111111 | #FFFFFF |

   - Band label: "<Era> era · <owned count>".
   - Each band holds focus runs of gold chips, with no era tags.

**Measured positions in A1 (turn 226)**

| Section | y | Lines |
|---|---|---|
| Being studied | 46–294 | 9 |
| Awaiting the idea | 298–371 | 2 |
| Not yet reachable | 375–423 | 1 |
| Moment passed | 427–650 | 8 |
| Owned header (fold cue) | 654–678 | — |

- The fold is at y 686, so every revealed row is visible at open.
- Board content height is 1,942.
- Owned bands at turn 226: Space 1, Atomic 4, Modern 31, Early Modern 40, Medieval 27, Classical 19, Ancient 38 (plus the 2 paths not taken), Primitive 31.

**Measured positions in A3 (turn 231)**

| Section | y | Lines |
|---|---|---|
| Grand Endeavour | 46–70 | 1 |
| Being studied | 74–297 | 8 |
| Awaiting the idea | 301–374 | 2 |
| Not yet reachable | 378–426 | 1 |
| Moment passed | 430–653 | 8 |
| Owned header | 657–681 | — |

**Focus view (A4)**
- Header line at y 46, 30 px tall, then 4 px. It contains:
  - a radio (16-px drawn, a real funding radio);
  - "Energy Systems" at 18 px;
  - "6 here · 3 reached from other foci" at 14 px #B3B3B3;
  - a right-aligned "× All foci" `<button>`: 30 tall, radius 15, #334D80, 14 px white, padding 0 11.
- The same sections follow, but rows are drawn as cards:
  - 565 × 50, two per line, gaps 8 (vertical) and 12 (horizontal);
  - the same body styles as the chips, with radius 15 (Moment passed keeps radius 4);
  - padding 0 10;
  - line 1 (20 px): glyph, name, era tag (live rows only) and tags;
  - line 2 (18 px): a 14-px summary in the body's text colour, ellipsised.
- Summaries: revealed rows show their conjecture; owned rows show their objects in Unciv words; rows reached from another focus add "home: <focus>". Measured: the last card ends at y 657.

### 3.4 Bottom bar

- Divider: 255,686 1185 × 3 (#334D80 with #19263F edges). Bar: y 689–810, 121 px, Unciv's 15% cap.
- "Close" `<button>`: 265,697 90 × 50. Esc and Back trigger it.
- "Faster than light" `<button>`: 265,753 180 × 50. Label 147 px. It opens the FTL screen and exists only once RC01 is owned.
- Description pane: 455,689 675 × 121, padding 8 10, so text spans x 465–1120. It scrolls inside itself with the 10-px knob. A click on it, or F1, opens the Civilopedia.
  - Title line (24 tall): the status glyph; the name at 18 px white, margin-left 7; the meta at 14 px #B3B3B3, margin-left 10, reading "<Focus> · <Era> era".
    - If the row is New, add a New tag.
    - Dual-path rows append " · also reached by <foci>" only if the whole title line stays within 655 px; otherwise that note becomes the last body line.
    - The worst measured title is 558 px.
  - Body: up to 4 visible lines at 14 px, line-height 19, `white-space:nowrap`. Every scripted line is at most 650 px; all were measured.
- Primary action: 1140,697 290 × 50. Secondary action: 1140,753 290 × 50.
  - Unciv TextButton: radius 20, padding 0 13 0 12, 18-px line-height 20, an optional second line at 14 px with line-height 16.
  - States: up #334D80; hover #65DC72 with text #404040; pressed #409955 with text #000033; disabled #252B3E with white text.
  - A hidden button is removed with `sc-if`.

**Deviation.** The bottom bar spans the board only (x 255–1440), because the focus list runs full height. The description body is 14 px; Unciv uses 18. The title stays at 18 px.

## 4. Status encoding

**Chip base:** `display:inline-flex;align-items:center;height:22px;box-sizing:border-box;font-size:14px;white-space:nowrap;cursor:pointer`, class `uh-chip`. Hover turns the border #FFFFFF. Glyph then name has a 5-px gap.

| # | Status | Body |
|---|---|---|
| 1 | Owned | `background:#FFD700;border:1.5px solid #B3B3B3;border-radius:11px;color:#6B4300;padding:0 9px`. No glyph. Owned rows sit only in history bands. |
| 2 | Being studied | `background:#4893AF;border:1.5px solid #B3B3B3;border-radius:11px;color:#000033;padding:0 8px 0 2px`. Glyph G-STUDY. No progress mark of any kind. |
| 3 | Awaiting the idea (revealed, not yet occurred) | `background:#0E5C56;border:1.5px dashed #FFFFFF;border-radius:11px;color:#FFFFFF;padding:0 8px 0 3px`. Glyph G-SEED. |
| 3b | Not yet reachable (revealed, prerequisites not all discovered; R69) | `background:transparent;border:1.5px dashed #B3B3B3;border-radius:11px;color:#FFFFFF;padding:0 8px 0 3px`. Glyph G-LOCK. |
| 4 | Moment passed (window closed) | `background:#111111;border:1.5px dotted #B3B3B3;border-radius:4px;color:#B3B3B3;padding:0 8px 0 3px`. Glyph G-SHUTTER. |
| 5 | Path not taken (Competing Solutions lock-out) | `background:transparent;border:1.5px dashed #6A6A8C;border-radius:11px;color:#9C9CB4;padding:0 3px`. Glyph G-FORK and the tag "Path not taken". It lives only in its era band. |
| 6 | Grand Endeavour target (overrides 2–5) | `background:#334D80;border:2px solid #FFFFFF;border-radius:11px;color:#FFFFFF;padding:0 3px 0 2px`. Glyph G-PYRAMID, era tag, and the tag "Endeavour 64%". |

**Status labels everywhere:** "Owned", "Being studied", "Awaiting the idea", "Not yet reachable", "Moment passed", "Path not taken", "Grand Endeavour". The long form of status 4 is "Its moment passed — only an Endeavour is certain".

**Spec-only variants (shown in A6 only):**
- Set-aside Endeavour: the base body plus the tag "Set aside · 40%" (#4893AF fill, navy text).
- Known dead end (a revealed rival theory reported against): the base body plus the tag "Dead end".
- Closed for good by a negative prerequisite: the Path-not-taken body, a G-NOENTRY glyph, and the tag "Closed: Writing came first".
- Unique claimed by a rival: the Path-not-taken body, a G-STAR-OUTLINE glyph, and the tag "Claimed by another civilisation".

**Era tag (live chips and live cards):** `display:inline-flex;align-items:center;height:17px;padding:0 4px;margin-left:6px;font-size:14px;box-shadow:inset 0 0 0 1px currentColor`. It is neutral, in the chip's own text colour, with no hue.
- Text: Prim, Anc, Class, Med, E.Mod, Mod, Atom, Space.
- There is no "»" mark. "Ahead of its time" appears only in the Endeavour price note.

**Word tags:** `display:inline-flex;align-items:center;height:17px;border-radius:8.5px;padding:0 6px;margin-left:6px;font-size:14px`.

| Tag | Fill | Text |
|---|---|---|
| New | #FFFFFF | #000033 |
| Rare | #7F3200 | #FFFFFF |
| ★ Unique | #3F1046 | #FFFFFF |
| Dead end | #6B4300 | #FFD700 |
| Superseded | #252B3E | #FFFFFF |
| FTL | #334D80 | #FFFFFF |
| Path not taken | #252B3E | #FFFFFF |
| Endeavour 64% | #FFFFFF | #000033 |
| 75% · traded / 50% · stolen (spec) | #252B3E | #FFFFFF |

**Overlays**
- Selected: add `;outline:2px solid #FFFFFF;outline-offset:2px`.
- Prerequisite of the selection, for shown rows only (R93): add `;outline:1.5px dashed #FFFFFF;outline-offset:2px`.
- Keyboard focus: `outline:2px solid #3A98DB`.

**Glyphs (inline SVG)**
- G-FLASK (Insight, currentColor), viewBox 0 0 14:
  `<path d="M5 1.5h4M5.8 1.5v4L2.2 11.6c-.4.7.1 1.4.9 1.4h7.8c.8 0 1.3-.7.9-1.4L8.2 5.5v-4" fill="none" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/><path d="M3.6 9.5h6.8"/>`
- G-STUDY, 16 px: `<circle cx="8" cy="8" r="7.5" fill="#FFFFFF"/>` with G-FLASK at `translate(2.3 2.1) scale(.82)`, stroke #000033, width 1.7.
- G-PYRAMID, 16 px: `<circle cx="8" cy="8" r="7.5" fill="#FFFFFF"/><path d="M3.6 11.3h8.8L8 4.2z" fill="none" stroke="#000033" stroke-width="1.4" stroke-linejoin="round"/><path d="M5.4 8.4h5.2" stroke="#000033" stroke-width="1.1"/>`
- G-SEED, 14 px, white: `<circle cx="7" cy="7" r="5.2" fill="none" stroke-width="1.5" stroke-dasharray="2.2 1.6"/><circle cx="7" cy="7" r="1.6" fill/>`
- G-LOCK, 14 px, white: `<rect x="2.75" y="6.25" width="8.5" height="6.25" rx="1.2" fill="none" stroke-width="1.5"/><path d="M4.8 6.25V4.5a2.2 2.2 0 0 1 4.4 0v1.75" fill="none" stroke-width="1.5"/>`
- G-SHUTTER, 14 px, #B3B3B3: `<rect x="2.25" y="2.25" width="9.5" height="9.5" rx="1.5" fill="none" stroke-width="1.5"/><path d="M2.5 5.6h9M2.5 8.4h9" stroke-width="1.3"/>`
- G-FORK, 14 px, #9C9CB4: `<path d="M3 12.5V8.3L7 5V1.5M7 5l4.5 3.6" fill="none" stroke-width="1.5" stroke-linecap="round"/><path d="M8.6 10.9l2.6-3" stroke-width="1.5" stroke-linecap="round"/>`
- G-OWNED (legend only), 14 px: `<rect x="1.5" y="3.5" width="11" height="7" rx="3.5" fill="#FFD700" stroke="#B3B3B3"/>`
- In section headers and segments, G-SEED and G-LOCK are white and G-SHUTTER is #B3B3B3.
- Move-up and move-down chevrons: `M3 9l4-4 4 4` and `M3 5l4 4 4-4`, stroke 1.6, white.

## 5. Funding and queue

**Fund with one click (R48).** Clicking a radio funds that focus immediately; switching costs nothing.
- The funded target shows in three agreeing places: the blue list row with its filled radio, the funding pill, and the white run label with a blue rule on the board.
- Selecting a focus (a name in the list, a run label, or the focus-view header) offers "Fund <focus>" as the primary action, which is Unciv's select-then-act path.
- Double-clicking a focus name funds it and closes the screen.

**Queue (R51)**
- Right-click or long-press a focus row to append it to the queue, or remove it if queued.
- With a focus selected, the secondary action is "Add to queue" or "Remove from queue".
- For a queued focus, the description title line carries two 24 × 24 round `<button>`s (#334D80, white chevrons) at x 1064 and x 1094, y 697. Their aria-labels are "Move <focus> up the queue" and "Move <focus> down the queue".
- The funded focus counts as 1, so discs start at 2.
- The rule is stated in the funding and focus descriptions: the queue moves on when the funded focus has no revealed work under study. It counts revealed rows only. There is no stall indicator and no "exhausted" mark.

**Committing an Endeavour**
- Confirmation popup (spec only):
  - Title: "Begin a Grand Endeavour?"
  - Body: "Begin a Grand Endeavour on Superconductivity? It takes the funded share, 683 a turn, for about 8 turns: 5,340 Insight in all. It cannot fail. Quantum Physics goes back to the head of the queue."
  - Buttons: [Begin Grand Endeavour] [Cancel].
- The previously funded focus goes back to the head of the queue.
- While the Endeavour runs:
  - no radio is on;
  - the focus holding the target gets the pyramid glyph;
  - the funding pill becomes the Endeavour pill;
  - the spread row is unchanged.

**Switching away from an Endeavour (R52 with the critic's fix; artboard A3b)**
- Clicking any radio, or "Fund X", opens a popup (§10, A3b): "Fund Quantum Physics instead?" / "The Superconductivity Endeavour stops at 64%. Its progress then decays slowly, and you can resume it later." / [Fund Quantum Physics] [Keep the Endeavour].
- Committing a different Endeavour while one runs:
  - the button reads "Replace the Endeavour";
  - the popup body reads "Replace the Endeavour on Superconductivity? It stops at 64%; its progress decays slowly, and you can resume it later.";
  - buttons: [Begin Grand Endeavour] [Keep the Endeavour].

**Under-study badge.** It counts the revealed rows under study that funding this focus advances, including dual-path reach (R85).
- Turn 226: Aeronautics 2, Chemistry 2, Computing 1, Electronics 1, Energy Systems 4, Farming 2, Materials Science 1, Medicine 2, Mining 2, Nuclear Physics 1, Observation 1, Optics 1, Philosophy and the Arts 2, Quantum Physics 2, Relativity & Cosmology 1, Rocketry 1, Textiles & Materials 1, Trade 1, Water Management 1.
- Turn 231: the same, except Construction 1 is added, Philosophy and the Arts is 1, and Quantum Physics has none.
- Queue: at turn 226, 2 Energy Systems and 3 Medicine. At turn 231, 2 Quantum Physics, 3 Energy Systems and 4 Medicine.

## 6. Selection, description and actions

**Selection model.** `sel = {kind: row | focus | funding | era, id}`. Only one thing is selected at a time.
- On opening, the funded focus is selected, as Unciv selects the current tech.
- Clicking a chip or card selects the row. The board does not move.
- Clicking a focus name or run label selects the focus and switches the board to the focus view.
- "× All foci" returns to the overview and selects the funded focus.
- Section headers and era bands only collapse and expand. The era pill selects "era".

**Description rules (R70, R77–R82)**
- L1, revealed rows: "<Source>. <status sentence>".
  - Sources: "Glimpsed by our scholars", "Revealed by <theory>", "Seen in use by another civilisation", "Learned of from another civilisation".
  - Being studied rows carry no source.
- L1, owned rows: "Discovered on turn N." followed by the effects in Unciv words (R80: object names, "Shows X on the map", "Opens the X focus").
- Prerequisites, by name:
  - "Needs ✓ A + ✓ B — all discovered.", with ✓ in #65DC72 and ✗ in #FF0000;
  - unmet parts read "✗ Laser (under study in Optics)";
  - tokens are shown as met by the owned provider;
  - environmental conditions read like "✓ Desert in your lands".
- Revealed rows end with a conjecture in #B3B3B3, in curly quotes: one sentence, at most 80 characters, no effects, no numbers, no FTL text, no forward references.
- Owned rows end with flavour in #B3B3B3.
- Fallback conjecture for a revealed row with none written: "“Our scholars believe <name> may be within reach.”"

**Action matrix (primary / secondary)**

| Selection | Primary | Secondary |
|---|---|---|
| Owned row | disabled "Discovered" | "Open the FTL screen", only on FTL-tagged rows; otherwise hidden |
| Being studied row | "Fund <its focus>", or disabled "Funded" | "Begin Grand Endeavour" / "<price> Insight · about N turns" |
| Awaiting row | "Experiment" / "300 Gold" (illustrative) | "Begin Grand Endeavour" / "<price>…" |
| Not yet reachable row | "Fund <focus where the missing prerequisite is under study>" | disabled "Grand Endeavour" / "needs <missing> first" |
| Moment passed row | "Synthesis" / "once this era · unused" (or disabled "Synthesis" / "used this era") | "Begin Grand Endeavour" / "<price>…" |
| Path not taken row | disabled "Never developed" | hidden |
| Endeavour target | disabled "Endeavour under way" / "64%" | "Stop the Endeavour" (confirm: "Stop the Endeavour? Its progress decays slowly; you can resume it later.") |
| Focus | "Fund <focus>" or disabled "Funded" | "Add to queue" / "Remove from queue" |
| Focus, while an Endeavour runs | "Fund <focus>" / "sets the Endeavour aside" (opens the popup) | as above |
| Funding header | disabled "Funded: Quantum Physics" | hidden |
| Era | hidden | hidden |

- While an Endeavour runs, every other "Begin Grand Endeavour" reads "Replace the Endeavour".
- The Endeavour is always the secondary action (R111).

**Example texts.** Each example gives the title line, then body lines. All are measured at 650 px or less.

A1, Superconductivity (EL11), Moment passed:
- Title: [G-SHUTTER] "Superconductivity", meta "Electricity · Atomic era".
- "Glimpsed by our scholars. Its moment passed — only an Endeavour is certain."
- "Needs ✓ Refrigeration + ✓ Electromagnetism — all discovered."
- "As an Endeavour: 5,340 Insight, twice today’s price, falling as development catches up."
- "“Cooled far enough, some metals might carry a current with no loss at all.”"
- Actions: [Synthesis | once this era · unused] and [Begin Grand Endeavour | 5,340 Insight · about 8 turns].

A3, Superconductivity, Endeavour target:
- Title: [G-PYRAMID] "Superconductivity", meta "Electricity · Atomic era · Grand Endeavour".
- "64% complete — 3,415 of 5,340 Insight; about 3 more turns at 683 a turn. It cannot fail."
- "It takes the funded share; the 20% spread still reaches your other foci."
- "Milestones at 25%, 50% and 75% may bring spin-offs. Committed on turn 226."
- "Stopping it lets its progress decay slowly; you can resume it later." (#B3B3B3)

Biomass Power Plant (ES03-W), Being studied:
- Meta: "Energy Systems · Modern era · also reached by Farming".
- "Being studied in Energy Systems: it takes a share of that focus’s Insight every turn."
- "Competes with Coal Power Plant (under study): if that comes first, this is never developed."
- "Needs ✓ Turbine Design + ✓ Wood Gas Production + ✓ Selective Breeding."
- "“Wood and crops might fire a cleaner, weaker plant.”"
- Actions: [Fund Energy Systems] and [Begin Grand Endeavour | 2,447 Insight · about 4 turns].

Standard Model Completion (QP06), Being studied in the funded focus (phone A5):
- "Being studied in Quantum Physics, which you fund: it takes Insight every turn."
- "Needs ✓ Quantum Field Theory + ✓ Particle Accelerator — all discovered."
- "“A complete list of the particles and forces may be within our grasp.”"
- Actions: [Funded] (disabled) and [Begin Grand Endeavour | 5,340 Insight · about 8 turns].

Phage Therapy (MD20), Awaiting the idea:
- "Revealed by Germ Theory. Awaiting the idea: no Insight, however hard Medicine is funded."
- "Needs ✓ Germ Theory + ✓ Telescope — all discovered."
- "Competes with Antibiotics, under study: if Antibiotics comes first, this is never developed."
- "“Viruses that prey on bacteria might be bred to fight infection.”"
- Actions: [Experiment | 300 Gold] and [Begin Grand Endeavour | 2,447 Insight · about 4 turns].

Gravitational Waves Detection (RC03), Not yet reachable:
- "Revealed by General Relativity. Not yet reachable: a prerequisite must be discovered first."
- "Needs ✓ General Relativity + ✗ Laser (under study in Optics) + ✓ Precision Machining."
- "It cannot be a Grand Endeavour until Laser is discovered."
- "“If space itself can ripple, a fine enough instrument might hear it.”"
- Actions: [Fund Optics] and disabled [Grand Endeavour | needs Laser first].

Rigid Airship (AE13), Not yet reachable:
- "Seen in use by another civilisation. Not yet reachable: a prerequisite must come first."
- "Needs ✗ Dirigible/Airship (under study in Aeronautics) + ✓ Aluminium Extraction."
- "It cannot be a Grand Endeavour until Dirigible/Airship is discovered."
- "“A frame of light metal around great gas cells could cross an ocean.”"
- Actions: [Fund Aeronautics] and disabled [Grand Endeavour | needs Dirigible/Airship first].

Camel Domestication (AH05), Moment passed, with an environmental prerequisite:
- "Glimpsed by our scholars. Its moment passed — only an Endeavour is certain."
- "Needs ✓ Animal Behavior Study + ✓ Desert in your lands — all met."
- "As an Endeavour: 37 Insight, twice today’s price; about 1 turn at 683 a turn."
- "“The desert beast that stores its water might carry our goods.”"

Corbel Arch/Vault (CO05), Path not taken:
- "Glimpsed by our scholars. Path not taken: Arch Construction was discovered first,"
- "so Corbel Arch/Vault will never be developed — a thing glimpsed and let slip."
- "“Stones stepped inward, course by course, until they meet.”"

Polymer Science (CH11), Owned:
- "Discovered on turn 223. Infantry (unit); +15% Production when building land units."
- "Opens the Materials Science focus."
- "Needs ✓ Organic Chemistry + ✓ Petrochemistry."
- "Mass-produced uniforms and kit: nylon is a polymer."

Caloric Theory (TH09), Owned, Dead end:
- "Discovered on turn 187. Dead end — Mechanical Equivalent of Heat reported:"
- "heat is motion, not a fluid. What stands: +1 Production from every Steam Works."
- "Needs ✓ Steam Engine + ✓ Natural Philosophy."
- "Heat as a weightless fluid — wrong in our world."

Nitrate Fertiliser (FA16), Owned, Superseded:
- "Superseded by Catalysis (turn 203): its +1 Food from Farms passed to the Haber process."
- "Needs ✓ Saltpeter Mining + ✓ Crop Rotation."
- "Before 1913 the world’s fields were fed from Chilean nitrate and Peruvian guano."

General Relativity (RC02), Owned, FTL:
- "Discovered on turn 186. No buildings, units or bonuses of its own."
- "Needs ✓ Special Relativity + ✓ Non-Euclidean Geometry."
- "This bore on the question of how to exceed the speed of light."
- Secondary action: [Open the FTL screen].

Rice Paddy Mastery (WM09), Owned, Unique: its body adds "Unique to your civilisation: it cannot be traded or stolen, and never diffuses."

Energy Systems, focus (A4):
- Title: radio glyph, "Energy Systems", meta "not funded · queued 2nd", then the Move up and Move down buttons.
- "Under study here: Coal Power Plant, Biomass Power Plant, Tidal Power, Biomass/Biogas."
- "Tends to help with power and production. Modifiers: +5% Natural Philosophy (all foci)."
- "Queued 2nd: funding moves here when Quantum Physics has no revealed work under study."
- "Switching loses nothing: every row keeps its progress." (#B3B3B3)
- Actions: [Fund Energy Systems] and [Remove from queue].

Funding header (6 lines; the pane scrolls and shows its knob):
- Title: "Insight", meta "853 a turn, equal to your science".
- "80% (683) goes to the funded focus, since Specialization of Labor; before it, 50%."
- "The other 20% (171) spreads to foci with work under study. Switching loses nothing."
- "Queue: 2 Energy Systems, 3 Medicine. It moves on when the funded focus has no revealed"
- "work under study. Diffusion: after the press (Printing Press)."
- "Theories reveal their applications (Scientific Method)."
- "Abilities: Experiment (Scientific Method) · Synthesis (Dialectical Thinking), unused this era."
- At turn 231, line 3 reads "When the Endeavour ends, funding goes to the first queued focus with revealed work under study."

Era pill:
- Title: "Modern era", meta "entered by count".
- "You enter an era when you hold enough breakthroughs from it or later."
- "Atomic needs 6 from the Atomic era or later: you hold 5."
- "Modern rows: 31 owned · 12 being studied · 4 awaiting the idea"
- "1 not yet reachable · 8 moment passed. Synthesis: once in each era, unused."

**Other focus descriptions follow the A4 pattern.**
- Insight modifiers (R57, R58), with the declared lands:
  - River start +20%: Farming, Trade, Construction.
  - Volcanic region +20%: Metallurgy, Chemistry.
  - Earthquake-prone +25%: Construction.
  - Diverse lands +20%: Farming, Medicine, Foraging.
  - Natural Philosophy +5%: all foci.
  - Botanical Classification +10%: Farming, Medicine.
  - Quantum Electrodynamics +10%: Electronics.
  - Special Relativity +10%: Nuclear Physics.
- W19 placeholder text ("Tends to help with …"). It is static, names no breakthrough, never mentions FTL, and is mechanism-open.

| Focus | Tends to help with | Focus | Tends to help with |
|---|---|---|---|
| Aeronautics | air units and sight | Animal Husbandry | mounted units and food |
| Chemistry | materials, fuels and medicines | Computing | science and administration |
| Construction | buildings and defences | Electricity | power and communication |
| Electronics | detection and devices | Energy Systems | power and production |
| Farming | food and growth | Fire | production and early weapons |
| Foraging | food and medicine | Genetics | health and food |
| Materials Science | production and protection | Mathematics | science and engineering |
| Mechanics | production and machines | Medicine | health and growth |
| Metallurgy | weapons, armour and production | Mining | resources and production |
| Nuclear Physics | power and weapons | Observation | science and knowing the land |
| Optics | sight and instruments | Philosophy and the Arts | culture, faith and learning |
| Quantum Physics | science and instruments | Relativity & Cosmology | science and trade |
| Rocketry | launches and missiles | Seafaring | ships and sea trade |
| Social Organization | government and specialists | Stonework | building and tools |
| Textiles & Materials | trade goods and equipment | Thermodynamics | engines and power |
| Trade | gold and trade routes | Warfare | military units and tactics |
| Water Management | food and water power | | |

## 7. Other controls and keyboard

- Status segments filter by single choice. The Owned segment shows only the history.
- Section headers and era bands are collapse toggles.
- "Faster than light" opens the FTL screen.
- Close, Esc and Back close the screen.
- Enter performs the primary action. F1, or a click on the description, opens the Civilopedia.

**ARIA**
- Chips: "<name> — <status label> — <focus>, <era> era", plus tags.
- Radios: "Fund <focus>", with aria-checked.

## 8. Data

### Corrected state

The source is `/home/user/Uncharted-Horizons/design/mockups/research_screen/late_game_state.json`. The corrections are coded in `/tmp/claude-0/-home-user-Uncharted-Horizons/ffab2c8f-97b2-5cca-83ad-f0d7b939b828/scratchpad/final_spec/data.py`. The mockup must label them as corrections.
- Rename the focus "Philosophy And The Arts" to "Philosophy and the Arts". Rename MS02 to "Nanotechnology".
- Paths not taken:
  - CO05 Corbel Arch/Vault: "Arch Construction came first".
  - WA08 Chariot Warfare: "Cavalry Tactics came first".
- Superseded: FA16 (by Catalysis, turn 203) and WM11 (by Railway Network, turn 198).
- Persists (plain owned rows with a note in the description): TH08 Stirling Engine Mastery and CH09-W Bio-Organic Synthesis.
- Owned dead end: TH09 Caloric Theory. Mechanical Equivalent of Heat reported, and Turbine Design is owned.
- Added rows:
  - MD20 Phage Therapy (Medicine, Modern, Awaiting): revealed by Germ Theory; competes with Antibiotics.
  - ES05 Oil Power Plant (Energy Systems, Modern, Awaiting): revealed by Turbine Design.
  - RK09 Ion Drive (Rocketry, Space, Awaiting): revealed by Quantum Electrodynamics.
  - RC03 Gravitational Waves Detection (Relativity & Cosmology, Atomic, Not yet reachable): revealed by General Relativity; needs Laser.
  - AE13 Rigid Airship (Aeronautics, Modern, Not yet reachable): seen in use by another civilisation; needs Dirigible/Airship.
- At turn 231:
  - QP09 String Theory Validation and QP10 Loop Quantum Gravity are Awaiting, revealed by Quantum Gravity Theory, tagged New, and shown side by side with no ordering cue.
  - Geodesic Structures is Being studied (New).
  - Information Theory, Standard Model Completion and Quantum Gravity Theory are owned (New).
  - EL11 is the Endeavour target.
- Declared lands: a river-valley start in a volcanic, earthquake-prone region, with desert and tropical forest in its lands. This makes AH05, AH06, CO07, S05, WA13, WM09 and WM11 legitimate.
- New tags: at turn 226, PH14 (discovered) and SF12 (moment passed). The Materials Science focus is New until it is first selected. "New" means changed since the screen was last opened.
- FTL tags: RC01, RC02, MA13 and QP02 (proposals); QP08 is added at turn 231.

### Counts

| Status | Turn 226 | Turn 231 |
|---|---|---|
| Owned | 191 | 194 |
| Being studied | 26 | 24 |
| Awaiting the idea | 6 | 7 |
| Not yet reachable | 2 | 2 |
| Moment passed | 24 | 23 |
| Path not taken | 2 | 2 |
| Endeavour | — | 1 |
| Total | 251 | 253 |

### Era by count

- Turn 226: 5 owned from the Atomic era or later, so "Modern era · 5 of 6 toward Atomic".
- Turn 231: 8, so Atomic is entered. Space holds 2, so "2 of 4 toward Space".

### Endeavour prices (illustrative, true multipliers only)

- Price = 2 × era price × per-city multiplier 1.2864 × 4^(eras ahead of development 5.7).
- Era prices are from `design/simulator/power/era_prices.json`.
- Prices at turn 226:

| Era | Price (Insight) |
|---|---|
| Primitive | 12 |
| Ancient | 37 |
| Classical | 168 |
| Medieval | 371 |
| Early Modern | 1,130 |
| Modern | 2,447 |
| Atomic | 5,340 |
| Space | 21,827 |

- Turns = round(price / 683), at least 1.
- The price is fixed at commitment.
- It never includes World-Truth multipliers, detour margins, tier promotion or price cuts. Multipliers below 1 act as head starts.

### Mapping into the template (`renderVals`)

**Files**
- `research_screen.dc.html`: A1–A4, chosen by the prop `view` (a1, a2, a3, a3b or a4; default a1). Use `this.state.view ?? this.props.view` so a preview can switch it.
- `research_screen_phone.dc.html`: A5.
- `research_screen_key.dc.html`: A6.
- The script embeds the corrected rows as JSON. Fields:
  - id; n (name); f (focus); era; s (status: owned, studying, waiting, unreach, closed, not_taken, endeavour); t (discovery turn, owned rows);
  - tags[]; src (source); req (`[name, met, note]`); conj (conjecture); fx (effects); flav (flavour); lines (optional explicit description lines).

**State**
- sel, focusView, filter, collapsed{}, funded, queue[], endeavour {id, pct, paid, price, turn}, popup, phase (t226 or t231).

**What `renderVals` returns** (every hole is a dotted lookup):
- `fund`: {onClick, isFocus, isEndeavour, name, right, barFill (a style string), insight, spread}.
- `foci[]`: {name, rowStyle, radioStyle, radioOn, aria, onFund, onSelect, onQueue (contextmenu), showPyramid, showNew, showBadge, badge, badgeStyle, showQueue, queueNo}, and `showHint`.
- `segs[]`: {label, count, style, countStyle, pressed ("true"/"false"), g:{studying, waiting, unreach, closed, owned}, onClick}; `era`: {text, onClick}.
- `board`: {overview, focusHead:{show, name, summary, radioStyle, onFund, onBack}, endeavour:{show, runs}, sections[]:{show, title, count, why, chevron, expanded, onToggle, g:{…}, runs[]:{label, labelStyle, onSelect, chips[]}, cards[]}, owned:{show, count, why, expanded, onToggle, bands[]:{label, count, style, expanded, onToggle, runs[], cards[]}}}.
- `chip`: {name, style, g:{studying, waiting, unreach, closed, notTaken, endeavour}, era:{show, text}, tags[]:{text, style}, aria, onClick}. A card is the same, plus `line2`.
- `bar`: {show, g:{…}, title, meta, tags[], lines[]:{style, parts[]:{text, style}}, move:{show, onUp, onDown}, primary:{show, l1, l2, showL2, disabled, style, onClick}, secondary:{…}}.
- `popup`: {show, title, body, ok:{label, onClick}, cancel:{label, onClick}}.

## 9. Hidden-information rules

**Unknown rows and counts**
- Nothing is drawn for Unknown rows. Counts cover shown rows only.
- Only the 33 entered foci are listed: no Space Engineering, and no Quintessic Physics, which the state's `foci` list wrongly includes.

**Funding, meters and windows**
- No per-focus Insight, spread or flow anywhere.
- No meter, percentage, turns or "since" on rows under study.
- No window length or closing turn.
- No tier on any revealed row.
- No per-row "held open while funded" text (W16).

**Text stripped from every string**
- FQ codes and percentages, world labels, and Germ-exclusive / FOSSIL_FUELS_ABSENT / ENHANCED_SPRINGS phrases.
- "cost ×2.5" (NP12, TH15).
- "airship chain" and confidence-ladder text.
- "Competing Solution" metadata, and merge or W18 notes.
- FTL text:
  - QP08's "critical node for Warp, Wormhole and Hyperspace";
  - RC04's "decides Wormhole FTL";
  - RC03's "fires the FTL report";
  - QP05's "prerequisite for the FTL paths";
  - RC02's "prerequisite for all FTL theories";
  - QP06's "hosts an FTL condition";
  - QP09/QP10's "Hosts …".
- Forward references: EL11's "Prerequisite for Fusion (NP04) and some FTL paths", RK09's "prerequisite for Asteroid Prospecting", and similar.

**Prerequisites rendered from the world-derived ruleset**
- OP07 reads "✓ Lens Grinding + ✓ Quantum Mechanics Formalism".
- RC04 reads "✓ Quantum Field Theory".
- CP13 reads "✓ Vacuum Tube" (MC14 is Unknown).
- MD06 reads "✓ Germ Theory", since the validated condition has resolved.

**Competition, theories and hidden state**
- "Competes with" appears only when both rows are revealed (ES03-W/ES03, MD20/MD06). CP13 shows nothing.
- A dead end is shown only after its report.
- No airship confidence, trust stockpile or Edison/Tesla state.
- No rival names, no diffusion countdowns, no development figure.

**FTL**
- Only the button, the FTL tag, and the line "This bore on the question of how to exceed the speed of light."
- The prototype in the slot is unnamed.

## 10. Artboards

**A1 "Research — turn 226"** (1440 × 810)
- Overview, scrolled to the top.
- Quantum Physics funded; queue 2 Energy Systems, 3 Medicine.
- Superconductivity selected, with the texts and actions in §6.
- Every revealed row is visible, ending at y 650. The fold cue at y 654 is "Owned 191".

**A2 "Research — whole board, turn 226"** (1440 × 2000)
- The board is unclipped: content from y 46 to 1988, 251 rows.
- The left column and top row are as in A1, with navy below y 810. There is no bottom bar.
- Superconductivity stays selected. Refrigeration (Modern band) and Electromagnetism (Early Modern band) carry the dashed prerequisite outline.
- It shows:
  - both ghosts (Ancient band);
  - Superseded on Industrial Canal Network and Nitrate Fertiliser;
  - Dead end on Caloric Theory;
  - Rare on Ornithopter and Greek Alchemical Tradition;
  - ★ Unique on Rice Paddy Mastery;
  - FTL on Special Relativity, General Relativity, Topology and Quantum Mechanics Formalism;
  - New on The Enlightenment and Ironclad.

**A3 "Grand Endeavour — turn 231"** (1440 × 810)
- The Endeavour pill shows "Superconductivity 64%" with its bar and ticks; the spread row is unchanged.
- No radio is on. Electricity carries the pyramid glyph.
- Discs: 2 Quantum Physics, 3 Energy Systems, 4 Medicine.
- The Grand Endeavour section is inline at the top.
- Atomic is the current era (teal band); Modern is past (amber band).
- New tags on Geodesic Structures, String Theory Validation, Loop Quantum Gravity, and the three newly owned rows.
- Superconductivity is selected; texts as in §6.

**A3b "Switching away from the Endeavour"** (1440 × 810)
- A3 with a scrim of rgba(0,0,0,0.5).
- Popup at 410,305, 620 × 200: #111111 fill, 1.5 px #B3B3B3 border, radius 15, padding 24.
  - Title, 18 px: "Fund Quantum Physics instead?"
  - Body, 18 px over 2 lines: "The Superconductivity Endeavour stops at 64%. Its progress then decays slowly, and you can resume it later."
  - Buttons, right-aligned at the bottom, gap 12: [Fund Quantum Physics] (250 × 50) and [Keep the Endeavour] (250 × 50).

**A4 "Choosing a focus — turn 226"** (1440 × 810)
- Energy Systems is selected: the list row has the white inset ring, and the board is in focus view.
  - Being studied (4 cards): Coal Power Plant, Biomass Power Plant, Tidal Power, Biomass/Biogas ("also via Chemistry, Farming").
  - Awaiting (1): Oil Power Plant.
  - Moment passed (1): Geothermal Power.
  - Owned (3), each in its era band:
    - Stirling Engine Mastery: "Stirling Works (building) · persists · home: Thermodynamics".
    - Windmill: "home: Mechanics".
    - Water Mill: "home: Water Management".
- Segment counts read 4, 1, 0, 3.
- The bottom bar is as in §6.

**A5 "Research — phone, turn 226"** (1300 × 600, Unciv Small at 19.5:9, landscape)
- Left column, 300 wide:
  - funding header 284 × 76;
  - list pane at y 84–507 with rows 44 tall (radius 22, radio 20 drawn in a 44 × 44 hit area), scrolled by 616 px so Mechanics through Relativity & Cosmology are visible and Quantum Physics is at y 436.
- Divider at x 300.
- Top row at 315,6:
  - five glyph-and-count segments, 36 tall, radius 18;
  - the era pill, 28 tall;
  - "Faster than light" at 170 × 40.
- Board at 315,52, 973 × 455:
  - chips 36 tall (radius 18; Moment passed radius 6);
  - run labels with line-height 36;
  - gaps 8 × 8; runs 14 apart; section headers 30;
  - Being studied takes 10 lines (464 px), so the board scrolls.
- Bottom bar at y 510–600, with a divider at 507:
  - Close 100 × 50 at 10,530;
  - description at 120,510, 660 × 90 (title plus 3 lines);
  - [Funded] (disabled) at 790,530, 240 × 50;
  - [Begin Grand Endeavour | 5,340 Insight · about 8 turns] at 1050,530, 240 × 50.
- Standard Model Completion is selected; texts as in §6.
- Long-press queues a focus.

**A6 "Status key"** (1440 × 810)
- Title "Status key", 18 px, at 24,16. Two columns at x 24 and x 744, rows at a 44-px pitch from y 56. Each row has the example at 1×, then the label at 18 px and a sentence at 14 px #B3B3B3, at x + 330.
- Column A:

| Label | Sentence |
|---|---|
| Owned | Discovered: its effects are yours. |
| Being studied | Its idea occurred: it takes a share of its focus’s Insight every turn. |
| Awaiting the idea | Revealed, not yet occurred: no Insight until the idea occurs. |
| Not yet reachable | Revealed; a prerequisite must be discovered first. |
| Moment passed | Its moment passed — only an Endeavour is certain. |
| Path not taken | A rival solution came first; never developed. |
| Grand Endeavour | Being completed by an Endeavour; it cannot fail. |
| Set aside | An Endeavour you stopped; its progress decays slowly. |
| Dead end | A theory reported against; only its consolation remains. |
| Closed for good | A negative prerequisite closed it. |
| Claimed by another civilisation | A Unique that another civilisation discovered first. |

- Column B:
  - the tags: Rare, ★ Unique, Superseded, Dead end, FTL, New, 75% · traded, 50% · stolen;
  - the overlays: Selected, Prerequisite of the selection;
  - the focus-row states: plain, funded, queued 2, selected, holds the Endeavour, New.

## 11. Open questions this mockup answers by choice

Numbers are the order of the 42 questions in `requirements.json`.

- **Q1–Q4:** as decided.
- **Q5:** nothing hints that a lost idea "may yet return".
- **Q6:** four later-era Moment-passed rows are kept (EL11, GN02, MA11, TH15). Under the era-hold clock they could not exist, and the A1 example would move to Radar or Ironclad.
- **Q7:** no W16 text on rows. TH15 is closed while its focus was unfunded.
- **Q8:** totals only.
- **Q9:** nothing is shown on rows under study.
- **Q10:** a price appears only as the Endeavour price of eligible rows.
- **Q11:** nothing about windows.
- **Q12:** Rare and Unique on owned rows only.
- **Q13:** no murmurs.
- **Q14:** the queue counts revealed rows only.
- **Q15:** exhausted foci are listed, fundable, and never marked.
- **Q16:** 2× only.
- **Q17:** rows under study are Endeavour-eligible.
- **Q19:** a Path not taken cannot be committed. "Competes with" appears only when both rows are revealed.
- **Q20:** Not yet reachable, Path not taken and Endeavour are statuses. Dead end, Superseded, Rare, Unique, FTL, New and traded/stolen are tags. Persists is a note.
- **Q21:** Experiment acts on Awaiting rows and Synthesis on Moment-passed rows, with no size of effect.
- **Q22:** Not yet reachable is its own status, naming its missing prerequisites. No placeholders.
- **Q23:** head starts.
- **Q24:** only entered foci are listed.
- **Q25:** W19 text is static and never mentions FTL.
- **Q26:** the FTL tag and its single line only.
- **Q27:** a prototype in the slot is unnamed, and switching away is confirmed. Prototypes and hypotheses are not listed.
- **Q28:** diffusion appears only as a source phrase.
- **Q29:** the era pill shows the era entered by count. "Ahead of its time" appears only in the price note, from development.
- **Q30:** the screen records breakthroughs and reports only.
- **Q31:** each row appears once under its home focus, with cross-references; badges count reach.
- **Q32:** IDs are never shown.
- **Q34:** price = 2 × era price × row multiplier × per-city multiplier × prematurity premium.
- **Q35:** no guidance.
- **Q36:** no codex here.
- **Q37:** the phone is landscape at Small.
- **Q38:** the world is atomic, known since Systematic Element Analysis.

**Also chosen here:**
- Committing an Endeavour returns the funded focus to the head of the queue.
- "New" means changed since the screen was last opened.
- Endeavour commitment is confirmed with a popup.
- Experiment costs 300 Gold (illustrative), and the per-city multiplier is 1.2864 (illustrative).

## 12. Requirements left out on purpose

- **R46, R55, R56** (per-focus Insight): would leak hidden occurrence.
- **R61:** does not apply in the late game.
- **R62** (murmurs): awaits translation to the new model.
- **R75** (codex).
- **R76** (claimed by a rival), **R73** (negative prerequisite), **R109** (set-aside Endeavour) and **R132** (traded or stolen): in the A6 key and the spec only.
- **R53** (push): spec only.
- **R87–R90** (leading line, serendipity, chains, propulsion tags).
- **R100** (Reveals lists).
- **R114, R115** (airship tiers, guidance).
- **R129:** only TH09's report is shown.
- **R131** (diffusion countdowns).
- **R145** (timeline): the era bands serve as the known-tree list.
- **Unciv's prerequisite connector lines:** replaced by dashed outlines on shown prerequisites and the ✓/✗ list. Positions in a flow layout are unknown, and 58% of the links cross foci.

## 13. Deviations from Unciv, and risks

**Deviations**
- Text colours on gold and blue are changed, because Unciv's pairs are 3.63 and 3.46:1.
- The funding header, status filter, focus list and queue widgets are additions.
- A board scrollbar is visible.
- The bottom bar spans the board only.
- The description body is 14 px.
- There are no era columns or connector lines.
- Era tags sit inside chips.

**Risks**
- **The height budget is exact.** The live rows end 36 px above the fold. More reveals (for example a Determinist Institute) push Moment passed below the fold. The fallback is to fold Moment-passed rows from two or more eras back into one expandable run, "12 from before the Early Modern era ›", counting shown rows only.
- **Badges add up to 29 while 26 rows are under study.** This is because of dual-path reach, and the focus description explains it.
- **"New" on a closed row reveals the turn it closed.**
- **The era pill and the price premium can disagree** at turn 231.
- **Selection re-renders reset scroll in `preview.py`.** In `componentDidMount`, set only the phone list's scroll position. If the runtime forbids that, use `margin-top:-616px` on the static frame.

## 14. Verification

- Render each artboard: `python3 design/mockups/research_screen/preview.py <file> <out.png> --size WxH`, with `--full` for A2.
- Check:
  - the live sections end by y 655 in A1 and A3;
  - the list ends by y 798 with 34 foci;
  - every description line has `scrollWidth` of 655 or less;
  - every button label fits 265 px.
- Measurement aids are in `/tmp/claude-0/-home-user-Uncharted-Horizons/ffab2c8f-97b2-5cca-83ad-f0d7b939b828/scratchpad/final_spec/`:
  - scripts: `data.py`, `proto.py`, `shot.py`, `phone.py`, `texts.py`;
  - renders: `proto_a1.png`, `proto_a2.png`, `proto_a3.png`, `proto_a4.png`, `proto_a5.png`;
  - the test font subset: `dv.woff2`.
- These are not the build. The prototype still places the source in the title meta; this spec moves it into line 1 of the description.