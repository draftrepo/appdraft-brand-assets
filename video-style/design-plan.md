# Xero and Salesforce film: design plan

Flagship website walkthrough, 1920x1080, 30 fps. Voice about 3:25, finished film about 3:45
(title 5.2 s, three part cards at 3.8 s each, end card hold 3.5 s).

Everything here is built and rendered. Templates are in `templates/`, proposed code in
`patches/`, review frames in `previews/`. Nothing in the demo-video skill folder was changed.
The whole chain (patched edit, callouts, transitions, cards, captions, assembly, music duck)
was run end to end on stand-in screens: `previews/pipeline-proof-standin-screens.mp4`.

The screens in every preview are made-up stand-ins (`tools/mock.html`), not the Brightline
org. Every x, y in this plan that points at the UI is therefore a description, not a
measurement: read the real numbers off the dry-run stills.

---

## 1. The idea

**One stage, one line.**

- **The stage.** The screen recording never fills the frame. It sits in a rounded window on a
  dark AppDraft backdrop, with a quiet footer underneath. Cards, captions and the wordmark all
  live on that same backdrop, so the film is one continuous space: the screen sinks away, words
  rise, the next screen rises. Nothing ever "cuts to a slide". This is what makes it read as a
  film about work rather than an advert for software.
- **The line.** One hairline with one teal piece. In the title it is two lines that stop short
  of each other (sales one side, finance the other) and the teal piece closes the gap. On the
  part cards it is four segments with the current one teal. In the footer it is four ticks. On
  the end card it comes back already joined. That is the only motif. No icons, no logos, no
  illustration.

What it must never do: bounce, spin, glow, flash, count up, use a stock transition, show a
Salesforce or Xero logo, or put a slogan over the footage.

---

## 2. Visual system

### Palette

| Token | Hex | Use |
|---|---|---|
| ink | `#0b141d` | backdrop base, callout plates (93% opaque), dim layer (46%) |
| navy | `#1f2d3d` | AppDraft navy: soft lift in the backdrop's top left only |
| blue | `#19779b` | AppDraft blue: backdrop glow, bottom right, 60% falling to 0 |
| teal | `#3cd6bf` | AppDraft teal: **the single accent**. The join, the current part, callout dots, leaders, ticks, the URL. Never for body text, never as a fill larger than a pill icon |
| paper | `#f3f6f8` | all primary text |
| mist | paper at 62% | secondary text, footer marker |
| faint | paper at 34% | "/ 04", inactive ticks |
| hair | paper at 14 to 30% | hairlines |
| amber | `#f2b84b` | one use only: the focus ring on the overdue tile in the credit control scene |

Backdrop = ink + blue radial glow from beyond the bottom-right corner + navy lift top left +
11% fine grain (overlay blend). The grain is not decoration: it stops the dark gradient
banding once encoded. Do not remove it.

### Type (Inter 500 / 600 / 700 from `assets/fonts`; 700 is not used)

| Style | Size / line | Weight | Tracking | Used for |
|---|---|---|---|---|
| Display | 124 / 1.03 | 600 | -0.038em | title, part names, end line |
| Body | 34 / 1.38 | 500 | -0.008em | sub lines on cards (mist) |
| URL | 44 | 600 | -0.015em | appdraft.com (teal) |
| Part number | 30 | 600 | +0.06em | "02" teal, "/ 04" faint |
| Eyebrow | 22 | 600 | +0.16em, caps | "SALES IN SALESFORCE", "FINANCE IN XERO" |
| Caption | 37 (ASS size 44) | 500 | -0.005em | the voice, in the footer |
| Footer marker | 21 | 600 | +0.01em | part name (mist) |
| Callout text | 27 lower, 23 chip, 40 value, 14 caps label | 600 | see `callout.html` | over the footage (sizes in recording pixels, shown 4% larger) |

Tabular figures are on everywhere, so numbers do not shift.

### Grid and safe areas (1920x1080)

- **Window**: x 128, y 44, 1664x936, corner radius 14. The 1600x900 recording is scaled 1.04x
  into it (close to native, so text stays sharp). Shadow `0 44px 110px -20px rgba(0,0,0,.62)`
  plus a 1 px light edge.
- **Text margin**: 128 px left and right, the same as the window edge. Every card is left
  aligned to it.
- **Card skeleton** (title, part cards and end card share it exactly): small line at y 362,
  the line at y 416, display type from y 486, sub line beneath.
- **Footer band**: y 980 to 1080, centred on y 1030. Left: four ticks (26x3, 6 gap) and the
  part name. Centre: the caption. Right: AppDraft wordmark, 132 wide, 72%.
- **Inside the window**: keep callouts 36 px from its edges (recording pixels). The lower
  third sits at left 36, bottom 36.

### Motion

| Curve | Value | Used for |
|---|---|---|
| enter | `cubic-bezier(.16, 1, .3, 1)` | anything arriving. Fast start, long settle |
| exit | `cubic-bezier(.7, 0, .84, 0)` | anything leaving. Exits are about half the length of entrances |
| move | `cubic-bezier(.65, 0, .35, 1)` | things travelling: the join, pushes, camera |
| draw | `cubic-bezier(.6, 0, .2, 1)` | lines drawing |

| Move | Duration | Detail |
|---|---|---|
| Display line reveal | 900 ms, enter | each line rises out of its own baseline (masked), 100 to 110 ms stagger |
| Small text in | 800 ms, enter | 22 px rise with fade |
| Text out | 380 ms, exit | 18 px up with fade |
| Hairline draw | 800 to 1100 ms, draw | from the outer end inwards |
| The join | 700 ms, move | teal piece grows from its centre |
| Window in | 850 ms, enter | from 34 px low, 97.2% scale, transparent |
| Window out | 500 ms, exit | to 20 px low, 97.2% scale, transparent |
| Callout dot | 450 ms, enter | plus one ring that expands and fades (900 ms). Once, never looping |
| Callout leader, plate | 400 ms draw, then 600 ms enter | plate lands 380 ms after the dot |
| Lower third | 700 ms, enter | plate wipes open left to right, teal bar draws down, text slides 10 px |
| Callout out | 300 ms, linear fade | |
| Caption | 120 ms fade in and out | |

Rules: one thing moves at a time; text never travels more than 34 px; nothing overshoots;
every graphic is fully still for at least 1.2 s before it leaves.

---

## 3. Graphics

### 3.1 Title sequence: `intro.html`, 5.2 s, no voice
Previews: `01-intro-sequence.png`, `02-intro-title.png`

| Time | What happens |
|---|---|
| 0.0 to 0.45 | up from black; wordmark top left at 0.3 |
| 0.45 to 1.55 | two hairlines draw in from the frame edges and stop 184 px apart |
| 0.95, 1.1 | "SALES IN SALESFORCE" over the left end, "FINANCE IN XERO" over the right |
| 1.85 to 2.55 | the teal piece closes the gap; the two labels fade |
| 2.2 to 3.2 | title rises, two lines: "Xero and Salesforce," / "joined up" |
| 2.75 | sub: "A walkthrough of the whole billing cycle" |
| 4.05 | text and line leave |
| 4.3 to 5.2 | the first frame of the recording rises into the window; footer marker "Who we are" fades in |

It ends on exactly the frame the footage starts on, so the join is a plain cut. Part 1 gets no
card of its own: the title is its opener, and the footer marker names it. (A Part 1 card is
rendered in `04-part-cards-all-four.png` in case one is wanted; I recommend against it, two
cards back to back.)

### 3.2 Part cards: `part.html`, 3.8 s each, no voice
Previews: `03-part-card-sequence.png`, `04-part-cards-all-four.png`, `05-part-card-02.png`

| Time | What happens |
|---|---|
| 0 to 0.5 | the outgoing screen sinks away; old footer marker fades |
| 0.3 | "02 / 04" |
| 0.28 to 1.3 | four segments draw left to right, the current one teal and thicker |
| 0.4 | part name rises |
| 0.75 | sub line |
| 2.75 | text leaves |
| 2.95 to 3.8 | the incoming screen rises; footer marker returns with the next tick lit |

| Card | Title | Sub |
|---|---|---|
| 02 | Money coming in | Invoices, branded documents, payments, credit control |
| 03 | Money going out | Purchase orders and supplier bills |
| 04 | Seeing the numbers | What was sold, what was billed, what is owed |

The voice pauses for each card (the assembler inserts 3.8 s of silence at the part boundary),
and the music bed is what you hear.

### 3.3 Footer marker (part of the stage): `stage.html`
Always on while footage is showing: four ticks and the part name, bottom left. It tells a
viewer where they are in a film with four parts, without a progress bar.

### 3.4 Callouts over the screen: `callout.html`
Previews: `06-callouts-on-screen.png`, `07`, `07b`, `07c`, `08`

Rendered with a transparent background at 1600x900, the recording's own pixel space, and laid
on by the edit. Two kinds of placement: **pinned** (moves and grows with the camera, for
anything pointing at the UI) and **flat** (ignores the camera, for the lower third).

| Type | Looks like | Use it for |
|---|---|---|
| lower | dark plate, teal bar on its left edge, one line of 27 px text, bottom left of the window | the scene's one-line statement (the script's Caption column) |
| chip | teal dot on the UI, short leader, dark pill with a tick that draws itself | a state change: "Posted to Xero", "Paid" |
| value | same dot and leader, plate with a small caps label and a 40 px value | a number worth reading: the Xero invoice number |
| focus | everything outside one rounded rectangle dims to 46% ink; 3 px teal ring | "look here". Amber ring for overdue only |

Rules:
- At most one focus and one chip or value on screen together. Never a lower third at the same
  time as a chip or value.
- A lower third arrives 0.6 s after its scene starts, stays 3.2 s, and goes. It is the
  script's caption line, word for word; it must not repeat the sentence being spoken at that
  moment (if it would, move it to the next pause).
- Point the leader into the emptiest nearby area. Never cover the thing the voice is naming.
- Callouts start once the action has landed and must be gone 0.4 s before the beat ends. The
  edit prints a warning if one overruns.
- Lower thirds are flat; chip, value and focus are pinned.

### 3.5 Captions
Preview: `07-stage-chip-and-caption.png`; real libass output in the proof film.

One line, Inter Medium, paper white, centred in the footer band at y 1030, **no box and no
outline** (the band is already dark). Maximum 42 characters so a line never reaches the part
marker or the wordmark. 120 ms fades. Captions stop when the end card takes over, because the
card carries the words.

The transcriber mishears (the current `words.json` has "a lot of paying for businesses").
Captions are for muted viewers, so every line must be read against the script and corrected
in `FIXES` before the final render; the caption script prints them all for that.

### 3.6 End card: `end.html`
Previews: `09-end-card-sequence.png`, `10-end-card.png`

Reads **AppDraft · Getting more out of Salesforce · appdraft.com** as three stacked elements:
the wordmark (330 wide) above the line, "Getting more / out of Salesforce" in display type
below it, appdraft.com in teal. No full stop. No Salesforce logo; the word is description.

The owner's direction: the card should land as the last line finishes. So:

| Moment | What happens |
|---|---|
| voice says "...get more out of Salesforce." | still on the dashboard wide shot |
| end card takes over 2.4 s before the voice ends (during "If you want to talk about this...") | screen sinks, the line draws in already joined |
| card time 1.0 | "Getting more out of Salesforce" rises |
| on "please get in touch" (about card time 2.0) | appdraft.com rises; card is complete as the voice stops |
| voice end + 3.5 s | hold, then 0.8 s fade to black |

Set `end.at` to the cue for "If you want to talk" plus about 1.5 s, and `urlat` from the cue
for "please". `assemble plan` prints the card length to render.

---

## 4. Transitions

| Name | Length | What it is | Where |
|---|---|---|---|
| Continuous | 0 | no transition: the recording simply carries on | inside a scene |
| Dissolve | 0.35 s | plain cross-fade (existing) | hidden page loads; same record, new state |
| Push | 0.6 s | old screen leaves left, new arrives from the right, 28 px dark gutter, slight motion blur, `move` curve | a new subject inside a part |
| Through | 0.7 s | camera pushes into a point on the old screen (to 142%), softens, comes out on the new screen settling from 110% | going *into* something: a document, a drill-in |
| Part card | 3.8 s | 3.2 above | between parts |
| Window rise / sink | 0.85 / 0.5 s | title into footage, footage into end card | start and end |

Rule of thumb: *through* means deeper, *push* means next, *dissolve* means the same thing a
moment later. No more than four *through* in the film.

Preview: `11-transitions-push-and-through.png`.

---

## 5. Scene by scene

Zoom targets are described against the UI; convert to 1600x900 pixels from the dry-run stills.
"Hold" = ease in once the action lands (edit.py's existing hold mode). Leave the automatic
hold creep on everywhere else so nothing sits frozen.

| # | Scene | Arrives by | Camera | Graphics |
|---|---|---|---|---|
| | Title | from black | | title sequence |
| 1 | The gap (opportunity, then invoice) | window rise | wide on the opportunity. On "finance lives in Xero" **push** to the invoice | lower third "Sales in Salesforce. Finance in Xero." on the pause after "gap in the middle" |
| 2 | Who we are (account, Xero tabs) | push | wide, then 1.25x hold on the row of Xero related tabs as they are clicked through | lower third "Built around how you bill" at "So our time goes on..." |
| | Part card 02 | | | Money coming in |
| 3 | Billing from the deal | window rise | 1.3x on the Create Xero Invoice button for the click; back wide as the invoice fills; after Post, 1.5x hold on the status and Xero number | focus on status + number, chip "Posted to Xero" (2.6 s); then value "Xero invoice number" on the number (2.6 s). Lower third "Billed from Salesforce, straight into Xero" over "You might bill from a deal, an order..." |
| 4 | Branded documents | **through**, into the Send button | PDF: start 1.35x on the Brightline logo and header, drift down to the totals; email wide | lower third "Your branding on every document" |
| 5 | Payments come back | push | 1.4x hold on the Paid status, then the Payments tab row | chip "Paid" on the status; lower third "Payments come back on their own" |
| 6 | Credit control (voice only) | push to the dashboard | 1.4x hold on the Overdue tile, then **through** into the overdue invoice, 1.3x on days overdue | amber focus on the Overdue tile (the film's only amber); lower third "Automated reminders, less bad debt". This scene has no footage of the reminders, so the lower third and the focus carry it |
| 7 | Statements | push | 1.3x on Send Statement for the click; **through** into the PDF; drift down the running balance column | lower third "Statements in a couple of clicks" |
| 8 | Voids and credit notes | dissolve (quick) | void: wide, quick. Credit note: 1.4x hold on Amount due as it drops | focus on Amount due as it changes (no plate); lower third "Voids and credit notes, from Salesforce" |
| | Part card 03 | | | Money going out |
| 9 | Purchase order to bill | window rise | wide for Create PO; 1.3x on PO status after Post; dissolve to "later"; 1.3x on Create Bill from PO; 1.4x hold on the bill lines filling | chip "Sent to supplier" on the PO; chip "Posted to Xero" on the bill; lower third "Purchase orders and supplier bills" during "this goes well beyond invoicing" |
| | Part card 04 | | | Seeing the numbers |
| 10 | Deals against invoices | window rise | 1.4x hold on deal value, invoiced, paid; push to the Invoiced and collected chart | focus spanning the three figures; lower third "What was sold vs what was paid" |
| 11 | Dashboard | continuous or dissolve | wide on the tiles (let it breathe 1.5 s), slow drift down to the 13-week forecast, 1.25x on Top debtors for the click, hold on the side panel | lower third "Your numbers, laid out your way". No focus: the dashboard is the picture |
| 12 | Agentforce | continuous (panel slides in on its own) | 1.35x on the assistant panel, anchored right, so questions and answers are legible; hold on each answer; ease back wide on the Ridgeway link click | lower third "Ask your billing data a question" as the panel opens. No callouts on the answers: let them be read |
| 13 | Health monitoring | push | 1.2x hold down the column of green checks | lower third "Health monitoring built in" |
| | Close | dissolve to dashboard wide | wide, slow creep only | none until the end card |
| | End card | window sink | | 3.6 above |

Tally: 4 through, 7 push, 3 part cards, about 12 lower thirds, 5 chips or values, 4 focuses.
If anything has to go for time, drop lower thirds first (scenes 5 and 13), never the camera.

---

## 6. Music

**Recommend a very quiet bed, not silence.** Reason: the part cards insert 3.8 s of no voice
three times, plus 5 s at the top and 3.5 s at the end. With no bed those are dead air and feel
like faults. With one, they feel deliberate.

- Character: slow ambient, warm pad or soft felt piano, 60 to 80 bpm, no drums, no hook, no
  build, no "uplifting corporate". If it would suit an advert, it is wrong.
- Source: Mixkit (licence already cleared in the skill), Ambient category. Audition three
  against the title sequence and one part card; I have not chosen a track, and Adam should
  hear the choice.
- Level: bed at 0.09 (about -21 dB) in the clear, ducked by the voice with a 12:1 sidechain,
  20 ms attack, 900 ms release, so under speech it is close to inaudible and it swells back
  gently in each card. 1.2 s fade in, 3 s fade out under the end card. All in `assemble.py`.
- If no track passes the "would this suit an advert" test, use none and shorten the part
  cards to 3.0 s.

---

## 7. What has to change in the toolkit

All proposed, none applied. Files in `patches/`.

| # | Change | File |
|---|---|---|
| 1 | New folder `<skill>/gfx/` holding the five templates plus `system.css` and `system.js` (sibling of `scripts/`, so `../assets` resolves) | `templates/*` |
| 2 | `gfx.ts`: card.ts generalised. Transparent background (`ALPHA=1`), waits for images, single still (`STILL=1`) | `gfx.ts` |
| 3 | `render_gfx()` in common.py and a `gfx` subcommand in run.sh, plus `assemble` and `captions-flagship` | `common_gfx.py`, `run_sh_gfx_case.txt` |
| 4 | edit.py: `canvas` (output size, 1664x936 for the window), `fade_in` (0 here; today a 1 s fade from black is forced and would break the join with the title), `transitions` per beat, `overlays` (callout frames, pinned or flat), zoomed frames resized straight to the canvas instead of via 1600x900, writes `<out>.timeline.json` | `edit_flagship.py` (full file), `edit.py.diff` (84 lines added, 8 removed) |
| 5 | `transitions.py`: push, through, dissolve as PIL functions | `transitions.py` |
| 6 | `assemble.py` replaces compose.sh for this film: `plan` saves the stills the cards need and the caption shifts; `render` places the footage in the window under the stage cover, cuts in the cards with silence, runs the voice on under the end card, burns captions, ducks the music | `assemble.py` |
| 7 | `captions_flagship.py`: footer style, 42 characters, shifted for every inserted card, stops at the end card | `captions_flagship.py` |

compose.sh itself is left alone; other videos keep using it.

### Build order

1. `edit` with the flagship config (canvas, fade_in 0, zooms, transitions; overlays can be added on a second pass once timings are known from the printed beat table).
2. `gfx stage.html` four times with `hole=1 alpha=1 still=1`: one cover per part.
3. `assemble plan`: saves `stills/` and prints each card's length.
4. `gfx intro.html`, `gfx part.html` x3, `gfx end.html` using those stills; `gfx callout.html` per callout (`alpha=1 w=1600 h=900`, or `scale=2 w=3200 h=1800` for sharper text under a zoom).
5. `captions-flagship`, read every line.
6. `assemble render`, then `check` with `--head 5.2 --tail <end card length>`.

---

## 8. Not sure about

- **Framed versus full bleed.** The window makes the UI about 13% smaller than filling the
  frame. I think the gain in polish and the clean caption band are worth it, and the zooms
  cover legibility, but it is the one decision that changes the whole film. Full bleed would
  need boxed captions again and cards that cut rather than flow.
- **Title wording.** "Xero and Salesforce, joined up" and "A walkthrough of the whole billing
  cycle" are mine, not from the script. Both are parameters.
- **Part card sub lines** are also mine.
- **"Through" at its midpoint** shows two screens of text softened together for about four
  frames. Fine on the stand-ins; check on the real Lightning pages, and fall back to push if
  it looks muddy.
- **The check step** (freeze detection) has not been run on the assembled proof; lower thirds
  and callouts add motion, the part cards are animated, but the long dashboard holds are
  where a 3 s still could appear.
- **Rendering was done with a standalone headless Chromium** (`tools/render.mjs`) using the
  same seek method as card.ts, not through the shared dev-browser server. `gfx.ts` is written
  for the server but has not been run there.
- **Music**: no track chosen.
