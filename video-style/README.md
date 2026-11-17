# AppDraft demo video style

The house style for AppDraft walkthrough films and social clips, first used for the
Salesforce and Xero videos (November 2026). Adam's verdict: "incredible", "fucking
awesome". Reuse this for every demo video so they all look like one series.

Finished examples:
- Long: https://appdraft.com/accelerators/salesforce-xero (Cloudflare Stream id
  a2ab213d03beb01bb07627ff05dfb80e), 3:38, 1920x1080.
- Short: 0:42, 1080x1350 (LinkedIn), kept in Adam's Downloads as "Xero short.mp4".
- Stills: `examples/` (from the real films) and `previews/` (the design frames).

## The look in one paragraph

**One stage, one line.** The screen recording never fills the frame: it sits in a rounded
window (x128 y44, 1664x936 on 1920x1080) on a dark AppDraft backdrop (ink #0b141d, blue
glow bottom right, navy lift top left, fine grain so it does not band). Under it a quiet
footer: four part ticks, the caption, the AppDraft wordmark. The only motif is a hairline
with one teal (#3cd6bf) piece: two lines that close a gap on the title, four segments on
the part cards, ticks in the footer, joined again on the end card. Inter 500/600 only.
No logos (no Salesforce or Xero logo), no icons, no bounce, glow, flash, count-ups, stock
transitions or slogans over footage. Full spec: `design-plan.md`.

## Building blocks

| Piece | What it is | Files |
|---|---|---|
| Title card | ~5 s. Two lines slide in, teal piece closes the gap, title rises. Title in plain voice, e.g. "Salesforce and Xero, working as one" + one subline | templates/intro.html |
| Part cards | 3.8 s between parts: screen sinks back, "02 Money coming in" rises, next screen comes forward | templates/part.html |
| Stage | Rounded window + footer (part ticks, caption, wordmark) | templates/stage.html, system.css, system.js |
| Callouts | chip ("Posted to Xero" with leader to the field), value, focus/spotlight (dims all but one field), lower-third label | templates/callout.html |
| Transitions | push, through (zoom through), dissolve. Never hard cuts between screens | patches/transitions.py |
| End card | Line rejoins, "Getting the most out of Salesforce" rises, then appdraft.com as the voice says "get in touch" | templates/end.html (short: short-end.html, short-bg.html) |
| Captions | Burned in, one line, sentence case, under the window | scripts/captions_flagship.py, captions_short*.py |
| Music | Mixkit "Vastness" (free licence, no credit), very quiet, ducked under the voice, a little louder on cards | scripts/mix_music.sh |

Rendering: templates are HTML rendered to frames with `tools/render.mjs`; the edit and
assembly scripts in `scripts/` (edit.py, transitions.py, assemble.py at 30 fps, compose.sh,
check.py, tighten.py, cues.py) plug into the demo-video skill pipeline (patches in
`patches/` show how: edit.py.diff, gfx.ts, run_sh_gfx_case.txt). The demo-video skill
itself was never modified: copy these into a work folder per film.

## Recipe

1. **Script first, in Adam's voice.** Plain, not an advert. AppDraft is a Salesforce
   partner, not a software vendor: "we've built the basics into a solution we can reuse, so
   our time goes on fitting it to the way you bill". Never say "accelerator" in the voice.
   No figures in the voiceover. Long: 4 parts (who we are, money in, money out, seeing the
   numbers) + close. Short: ~45 s, one idea per line, works muted.
2. **Shared sign-off on every video:** "It's just one of the ways we help customers get the
   most out of Salesforce. If you want to talk about this, or anything else you're trying to
   do with Salesforce, please get in touch." Short uses the first sentence only. End card:
   AppDraft · Getting the most out of Salesforce · appdraft.com.
3. **Show Adam the script in chat to refine before editing the page.** Put the final
   voiceover-only version in a Google Doc for him to read from.
4. **Prep the demo org** so nothing breaks on camera (pages activated, actions on layouts,
   tenant named after the demo brand, Health green, records ready for each scene). Dry-run
   and look at stills before filming.
5. **Record the voice on an iPhone (Voice Memos) in a wardrobe**, a hand's width from the
   mouth. NOT the headset: it records at 16 kHz phone quality and sounds tinny, and no
   cleaner fixes that. Check with ffprobe: want 48 kHz.
6. **Light audio only:** cut fluffs, shorten long pauses (keep room tone), highpass 80 Hz,
   loudnorm I=-16 TP=-1.5. No compression or EQ: it makes the voice sound processed.
7. **Film, then edit to the voice:** beats timed to the transcript (faster-whisper),
   part-break pauses, callouts at the key moments, ~9 s of silence in the short for the
   assistant typing a question letter by letter.
8. **Fix Whisper's mishearings in captions:** Xero ("zero"), bills ("builds"),
   Agentforce ("Agent Force").
9. **Checks before handing over:** freeze check, plus a flicker scan (frame-difference
   series; look for A-B-A patterns: one or more single frames of another screen flashing
   up). Look at contact sheets of every part.
10. **Deliver** to Downloads; upload/post only with Adam's yes. Website videos go to the
    AppDraft Cloudflare Stream account and onto the accelerator page with the StreamVideo
    component (appdraft-new repo).

## Lessons from the Xero films

- **Flicker** came from: fast zoom in then straight back out; pop-ups and in-between pages
  flashing for under a second; a scroll that jumped back and forth; and single frames of
  the next shot leaking into a hold. Rules now: zooms ease in over ~1.3 s and out over
  ~1.5 s and must hold still at least 2 s; go straight to the target page (no sub-second
  intermediate screens); scan the final file frame by frame.
- **Short format:** 1080x1350 (4:5), not 9:16. At 9:16 the Salesforce screens are too
  small to read. Title above the window, captions below.
- **Things that need a login** (e.g. the Xero web app) are not filmed: show the Xero number
  arriving on the Salesforce record with a "Posted to Xero" chip instead.
- **PDFs** download rather than open when recorded: show a rendered picture of the PDF.
- **Never click Send** on emails in a demo; cancel before the final send.
- **Agentforce on camera:** only ask questions tested beforehand that give strong answers
  with the demo data, typed exactly as tested.
- Do not film client orgs.
