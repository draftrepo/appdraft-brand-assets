"""Line a screen recording up with a voiceover (or captions) and render it.

Usage: demo-video edit config.json        (or python3 edit.py config.json)

The recorder (recorder.ts) logs, for each beat, when it started, when the screen
settled ("ready") and any loading stretches to cut ("cutStart"/"cutEnd"). The
voiceover's cue words (cues.py) say when each beat should land. This script maps
every output frame to a recorded frame so each beat starts just before its cue
word, cuts the loads, dissolves across cuts, and zooms.

Nothing may look frozen. Two things see to that, both on by default:
- Idle tightening: any stretch inside a beat where nothing but the cursor changes is
  cut down to `keep_still` seconds (frame pixel difference, cursor masked out).
- Hold zoom: when a beat's slot is longer than its action (the voice or caption
  needs the time), the held screen creeps in gently rather than sitting still.

Config keys (paths relative to the config file):
  audio        voice WAV; leave out (or null) for a silent track
  cues         cues JSON from cues.py ({beat: seconds, ..., "end": seconds})
  runs         {"A": "<recording dir with marks.json>", "B": ...}
  beats        [{"name": "open", "run": "A"}, ...] in screen order
  mode         "long" (zoom only on still moments) or "short" (always zoomed, panning)
  out          output MP4
  overrides    optional {beat: seconds} to move a cue
  lead, dissolve, tail, fps   optional timing (defaults 0.4, 0.35, 2.5, 30)
  long:  zoom  {beat: [x, y, zoom, "hold" | seconds]}  focus in 1600x900 source pixels
  short: base, focus {beat: [x, y]}, punch {beat: zoom}
  tighten      optional, false to keep idle stretches (default true)
  keep_still   optional, seconds of unchanged screen kept after each change (default 1.1)
  hold_zoom    optional, zoom gained per second of hold (default 0.012; 0 turns it off)
  audio_filter optional ffmpeg audio chain before levelling
  fade_out     optional, true to fade video and audio out at the end (long mode)

Flagship additions (all optional; without them the output is as before):
  canvas       [w, h] of the output video (default [1920, 1080]). The flagship film uses
               [1664, 936]: the size of the window the assembler places it in.
  fade_in      seconds of fade from black at the start (default 1 long, 0.4 short; 0 = none)
  transitions  {beat: "cut" | "dissolve" | "push" | "through" | ["through", x, y]}
               how that beat ARRIVES (see transitions.py). x, y: the point the camera
               pushes into, in 1600x900 source pixels.
  overlays     [{"beat": "post", "frames": "gfx/post", "at": 0.4, "from": "hold" | "start",
                 "space": "source" | "screen"}]
               a folder of transparent PNG frames (callout.html, 30 fps) laid over the
               footage, starting `at` seconds after the beat's action lands ("hold", the
               default) or after the beat starts. "source" (default) is pinned to the
               page, so it moves and grows with any zoom; "screen" ignores the zoom.
Also writes <out>.timeline.json (each beat's slot and hold times) for assemble.py.
"""
import bisect, json, math, os, shutil, subprocess, sys
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.environ.get("DEMO_VIDEO_SCRIPTS", os.path.dirname(os.path.abspath(__file__))))
from common import change_times, ffmpeg, tighten_ranges
import transitions as T

CFG_PATH = os.path.abspath(sys.argv[1])
D = os.path.dirname(CFG_PATH)
cfg = json.load(open(CFG_PATH))
P = lambda p: p if os.path.isabs(p) else os.path.join(D, p)

FF = ffmpeg()
W0, H0 = 1600, 900
FPS = cfg.get("fps", 30)
LEAD = cfg.get("lead", 0.4)
DISSOLVE = cfg.get("dissolve", 0.35)
TAIL = cfg.get("tail", 2.5)
MODE = cfg.get("mode", "long")
TIGHTEN = cfg.get("tighten", True)
KEEP = cfg.get("keep_still", 1.1)
HOLD_RATE = cfg.get("hold_zoom", 0.012)
HOLD_MIN = 1.2   # holds shorter than this need no zoom
CANVAS = tuple(cfg.get("canvas", [1920, 1080]))
FADE_IN = cfg.get("fade_in", 1 if MODE == "long" else 0.4)
TRANS = cfg.get("transitions", {})
OVERLAYS = cfg.get("overlays", [])

cues = json.load(open(P(cfg["cues"])))
cues.update(cfg.get("overrides", {}))
ORDER = [b["name"] for b in cfg["beats"]]
RUN_OF = {b["name"]: b["run"] for b in cfg["beats"]}


def load(path):
    d = json.load(open(os.path.join(P(path), "marks.json")))
    for f in d["frames"]:
        if not os.path.isabs(f["f"]) or not os.path.exists(f["f"]):
            f["f"] = os.path.join(P(path), "frames", os.path.basename(f["f"]))
    changes = [t / 1000 for t in change_times(P(path), d["marks"], d["frames"])] if TIGHTEN else []
    return d["marks"], d["frames"], changes


runs = {k: load(v) for k, v in cfg["runs"].items()}

beats = []
for name in ORDER:
    marks, _, changes = runs[RUN_OF[name]]
    st = next(m["t"] for m in marks if m["beat"] == name and m["kind"] == "start")
    rd = next(m["t"] for m in marks if m["beat"] == name and m["kind"] == "ready")
    cs = [m["t"] for m in marks if m["kind"] == "cutStart" and st <= m["t"] <= rd]
    ce = [m["t"] for m in marks if m["kind"] == "cutEnd" and st <= m["t"] <= rd]
    ranges, cur = [], st
    for a, b in zip(cs, ce):
        ranges.append((cur, a)); cur = b
    ranges.append((cur, rd))
    ranges = [(a / 1000, b / 1000) for a, b in ranges if b > a]
    raw = sum(b - a for a, b in ranges)
    if TIGHTEN:
        ranges = tighten_ranges(ranges, changes, KEEP)
    # Where the cursor last came to rest in this beat: the hold zoom leans towards it.
    rest = [m for m in marks if m.get("kind") == "cursor" and st <= m["t"] <= rd]
    beats.append({"name": name, "run": RUN_OF[name], "ranges": ranges, "raw": raw,
                  "dur": sum(b - a for a, b in ranges),
                  "rest": (rest[-1]["x"], rest[-1]["y"]) if rest else None})

end_t = cues["end"] + TAIL
for i, b in enumerate(beats):
    b["slot0"] = 0.0 if i == 0 else cues[b["name"]] - LEAD
for i, b in enumerate(beats):
    b["slot1"] = beats[i + 1]["slot0"] if i + 1 < len(beats) else end_t
    avail = b["slot1"] - b["slot0"]
    b["speed"] = max(1.0, b["dur"] / max(avail, 0.05))
    b["hold_at"] = b["slot0"] + b["dur"] / b["speed"]
    b["hold"] = b["slot1"] - b["hold_at"]
    flag = "  <-- fast" if b["speed"] > 2.5 else ""
    trim = f" (from {b['raw']:.1f})" if b["raw"] - b["dur"] > 0.05 else ""
    print(f"{b['name']:10s} at {b['slot0']:7.2f}s  slot {avail:5.1f}s  action {b['dur']:5.1f}s{trim}  "
          f"hold {max(b['hold'], 0):4.1f}s  speed {b['speed']:.2f}{flag}")

# Overlays: when each starts on the output clock, and its frames in order.
by_name = {b["name"]: b for b in beats}
for o in OVERLAYS:
    ob = by_name[o["beat"]]
    o["t0"] = (ob["slot0"] if o.get("from") == "start" else ob["hold_at"]) + o.get("at", 0.0)
    o["files"] = sorted(os.path.join(P(o["frames"]), n) for n in os.listdir(P(o["frames"])) if n.endswith(".png"))
    late = o["t0"] + len(o["files"]) / FPS - ob["slot1"]
    print(f"overlay {o['frames']:24s} on {o['beat']:10s} {o['t0']:7.2f}s for {len(o['files']) / FPS:4.1f}s"
          + (f"  <-- runs {late:.1f}s past its beat" if late > 0.05 else ""))

def overlays_at(k):
    """(png, space) for every overlay showing on output frame k."""
    hit = []
    for o in OVERLAYS:
        i = k - int(round(o["t0"] * FPS))
        if 0 <= i < len(o["files"]):
            hit.append((o["files"][i], o.get("space", "source")))
    return hit

def trans_of(name):
    spec = TRANS.get(name, "dissolve")
    if isinstance(spec, list):
        return spec[0], tuple(spec[1:3])
    return spec, None

frame_times = {r: [f["t"] / 1000 for f in runs[r][1]] for r in runs}
def frame_at(run, t):
    ts = frame_times[run]
    i = max(0, bisect.bisect_right(ts, t) - 1)
    return runs[run][1][i]["f"]

def source(b, local):
    """Seconds into a beat's slot -> (source time, range index, output seconds into that range)."""
    x = min(local * b["speed"], b["dur"] - 1e-3)
    for k, (a, e) in enumerate(b["ranges"]):
        if x <= e - a or k == len(b["ranges"]) - 1:
            return a + min(x, e - a), k, x / b["speed"]
        x -= e - a

smooth = lambda x: 0.0 if x <= 0 else 1.0 if x >= 1 else x * x * (3 - 2 * x)

def box_for(fx, fy, z):
    w, h = W0 / z, H0 / z
    x0 = min(max(fx - w / 2, 0), W0 - w); y0 = min(max(fy - h / 2, 0), H0 - h)
    return (round(x0, 1), round(y0, 1), round(w, 1), round(h, 1))

def creep_period(b):
    return min(max(b["hold"] - 0.8, 0.6), 8.0)

def creep(b, t):
    """0..1: a slow ease in across a held screen, back to 0 just before the next beat.
    Holds longer than about 9 s breathe in and out every 8 s, so they never sit still."""
    if HOLD_RATE <= 0 or b["hold"] < HOLD_MIN:
        return 0.0
    u = t - b["hold_at"]
    if u <= 0:
        return 0.0
    rise = 0.5 - 0.5 * math.cos(math.pi * u / creep_period(b))
    return rise * smooth((b["slot1"] - 0.1 - t) / 0.7)

def creep_amount(b):
    return min(0.15, max(0.04, HOLD_RATE * creep_period(b)))

def zoom_long(b, t):
    fx, fy, z = 800.0, 450.0, 1.0
    spec = cfg.get("zoom", {}).get(b["name"])
    if spec:
        sx, sy, sz, mode = spec
        zin = b["hold_at"] + 0.3 if mode == "hold" else b["slot1"] - mode
        if b["slot1"] - zin >= 1.2:
            e = smooth(t - zin) * smooth((b["slot1"] - 0.15 - t) / 0.7)
            fx, fy, z = 800 + (sx - 800) * e, 450 + (sy - 450) * e, 1 + (sz - 1) * e
    c = creep(b, t)
    if c > 0:
        if not spec and b["rest"]:
            # Lean halfway towards where the cursor came to rest.
            rx, ry = b["rest"]
            fx, fy = 800 + (rx - 800) * 0.5 * c, 450 + (ry - 450) * 0.5 * c
        z *= 1 + creep_amount(b) * c
    return None if z <= 1.0005 else box_for(fx, fy, z)

def zoom_short(b, t):
    base, focus, punch = cfg.get("base", 1.4), cfg["focus"], cfg.get("punch", {})
    i = ORDER.index(b["name"])
    fx, fy = focus[b["name"]]
    if i > 0:
        px, py = focus[ORDER[i - 1]]
        e = smooth((t - b["slot0"]) / 0.45)
        fx, fy = px + (fx - px) * e, py + (fy - py) * e
    z = base
    if b["name"] in punch:
        zin = b["slot0"] + b["dur"] / b["speed"] + 0.05
        if b["slot1"] - zin > 0.7:
            z = base + (punch[b["name"]] - base) * smooth((t - zin) / 0.3) * smooth((b["slot1"] - 0.02 - t) / 0.3)
    z *= 1 + 0.5 * creep_amount(b) * creep(b, t)
    return box_for(fx, fy, z)

zoom_at = zoom_short if MODE == "short" else zoom_long

# One working folder per config, so long.json and short.json in the same folder can run at once.
work = os.path.join(D, "_edit-" + os.path.splitext(os.path.basename(CFG_PATH))[0]); shutil.rmtree(work, ignore_errors=True)
os.makedirs(os.path.join(work, "blend")); os.makedirs(os.path.join(work, "zoom")); os.makedirs(os.path.join(work, "over"))
zoom_cache, entries, bi = {}, [], 0
for k in range(int(end_t * FPS)):
    t = k / FPS
    while bi + 1 < len(beats) and t >= beats[bi + 1]["slot0"]:
        bi += 1
    b = beats[bi]
    local = t - b["slot0"]
    st, ri, into_range = source(b, local)
    f = frame_at(b["run"], st)
    prev, since, kind, focus = None, 0, "dissolve", None
    if ri > 0:
        prev, since = frame_at(b["run"], b["ranges"][ri - 1][1]), into_range
    elif bi > 0 and (b["name"] in TRANS or beats[bi - 1]["run"] != b["run"]):
        # A beat arrives with a transition when the config names one, or (as before) with a
        # dissolve when it comes from a different recording.
        pb = beats[bi - 1]
        prev, since = frame_at(pb["run"], pb["ranges"][-1][1]), local
        kind, focus = trans_of(b["name"])
    dur = DISSOLVE if kind == "dissolve" else T.DUR[kind]
    if prev and dur > 0 and 0 <= since < dur and prev != f:
        out = os.path.join(work, "blend", f"{k:06d}.jpg")
        T.transition(kind, Image.open(prev), Image.open(f), since / dur, focus).save(out, quality=95)
        f = out
    box = zoom_at(b, t)
    over = overlays_at(k)
    if over:
        # Callouts: scale the footage to the canvas (through the zoom if there is one), then
        # lay each overlay on. A "source" overlay goes through the same zoom, so it stays
        # pinned to the page; a "screen" overlay is laid on flat.
        im = Image.open(f).convert("RGB")
        if box:
            x0, y0, w, h = box
            im = im.resize(CANVAS, Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h))
        elif im.size != CANVAS:
            im = im.resize(CANVAS, Image.LANCZOS)
        for png, space in over:
            ov = Image.open(png).convert("RGBA").convert("RGBa")     # premultiplied: no dark fringe when resized
            s = ov.width / W0
            if space == "source" and box:
                ov = ov.resize(CANVAS, Image.LANCZOS, box=(x0 * s, y0 * s, (x0 + w) * s, (y0 + h) * s))
            elif ov.size != CANVAS:
                ov = ov.resize(CANVAS, Image.LANCZOS)
            ov = ov.convert("RGBA")
            im.paste(ov, (0, 0), ov)
        f = os.path.join(work, "over", f"{k:06d}.jpg")
        im.save(f, quality=95)
    elif box:
        key = (f, box)
        if key not in zoom_cache:
            x0, y0, w, h = box
            out = os.path.join(work, "zoom", f"{k:06d}.jpg")
            Image.open(f).convert("RGB").resize(CANVAS, Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h)).save(out, quality=95)
            zoom_cache[key] = out
        f = zoom_cache[key]
    if entries and entries[-1][0] == f:
        entries[-1][1] += 1
    else:
        entries.append([f, 1])

lst = os.path.join(work, "frames.ffconcat")
with open(lst, "w") as fh:
    fh.write("ffconcat version 1.0\n")
    for f, c in entries:
        fh.write(f"file '{f}'\nduration {c / FPS:.6f}\n")
    fh.write(f"file '{entries[-1][0]}'\n")
print("length", round(end_t, 1), "s")

vf = f"fps={FPS},scale={CANVAS[0]}:{CANVAS[1]}:flags=lanczos,setsar=1,format=yuv420p"
if FADE_IN > 0:
    vf += f",fade=t=in:st=0:d={FADE_IN}"
if cfg.get("audio"):
    audio_in = ["-i", P(cfg["audio"])]
    af = cfg.get("audio_filter", "highpass=f=80") + ",loudnorm=I=-16:TP=-1.5:LRA=11," + f"apad,atrim=0:{end_t:.2f}"
else:
    audio_in = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    af = f"atrim=0:{end_t:.2f}"
if cfg.get("fade_out"):
    vf += f",fade=t=out:st={end_t - 1.5:.2f}:d=1.5"
    af += f",afade=t=out:st={end_t - 1.5:.2f}:d=1.5"
subprocess.run([FF, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, *audio_in,
                "-vf", vf, "-af", af, "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
                "-ar", "48000", "-t", f"{end_t:.2f}", "-movflags", "+faststart", P(cfg["out"])], check=True)
print("wrote", P(cfg["out"]))

# For assemble.py: where every beat sits on this video's clock.
tl = os.path.splitext(P(cfg["out"]))[0] + ".timeline.json"
json.dump({"fps": FPS, "length": round(end_t, 3), "voice_end": cues["end"], "canvas": list(CANVAS),
           "beats": [{"name": b["name"], "start": round(b["slot0"], 3), "hold_at": round(b["hold_at"], 3),
                      "end": round(b["slot1"], 3)} for b in beats]}, open(tl, "w"), indent=1)
print("wrote", tl)
