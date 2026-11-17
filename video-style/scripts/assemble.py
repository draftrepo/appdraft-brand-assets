"""Final assembly for the flagship film. Replaces compose.sh for this kind of video.

    demo-video assemble plan   film.json     work out the joins, save the stills the cards need
    demo-video assemble render film.json     build the finished film

The edit (edit_flagship.py, "canvas": [1664, 936]) gives one continuous video timed to
the voice. This places it in the window on the stage, opens with the title sequence,
cuts a part card in at each part boundary (the voice pauses for it), hands over to the
end card while the voice finishes, burns the captions and lays the music bed under it all.

film.json (paths relative to it):
  main      the edit's MP4; its .timeline.json must sit beside it
  window    [x, y] of the window on the 1920x1080 canvas (default [128, 44])
  intro     {"frames": "gfx/intro", "len": 5.2}
  parts     in order. The first has only a cover; the rest start at a beat and have a card:
            [{"cover": "gfx/cover-1/0000.png"},
             {"at": "billing", "card": "gfx/part-2", "len": 3.8, "cover": "gfx/cover-2/0000.png"}, ...]
  end       {"at": "signoff", "frames": "gfx/end", "hold": 3.0}
            "at": the beat (or seconds on the edit's clock) where the end card takes over.
            The card must run to the end of the voice plus `hold`; plan prints that length.
  captions  ASS file from captions_flagship.py (optional)
  fonts     folder holding the Inter TTFs
  music     optional {"file": "bed.mp3", "level": 0.09, "start": 0}
  out       the finished MP4

plan writes assembly.json (the joins, and the caption shifts) and stills/: intro-to.png,
part-N-from.png, part-N-to.png, end-from.png. Render the cards from those, make the
captions, then render.
"""
import json, os, subprocess, sys

MODE, CFG_PATH = sys.argv[1], os.path.abspath(sys.argv[2])
D = os.path.dirname(CFG_PATH)
cfg = json.load(open(CFG_PATH))
P = lambda p: p if os.path.isabs(p) else os.path.join(D, p)
FF = os.environ.get("FFMPEG") or "ffmpeg"
MAIN = P(cfg["main"])
tl = json.load(open(os.path.splitext(MAIN)[0] + ".timeline.json"))
FPS, LENGTH = tl["fps"], tl["length"]
START = {b["name"]: b["start"] for b in tl["beats"]}
WX, WY = cfg.get("window", [128, 44])
CW, CH = tl.get("canvas", [1664, 936])

def when(at):
    if isinstance(at, (int, float)):
        return float(at)
    if isinstance(at, list):
        return START[at[0]] + at[1]
    return START[at]

fr = lambda t: int(round(t * FPS))
intro_len = cfg["intro"]["len"]
parts = cfg["parts"]
cuts = [0] + [fr(when(p["at"])) for p in parts[1:]]          # frame where each part starts
end_f = fr(when(cfg["end"]["at"]))
main_frames = fr(LENGTH)
end_len = round((main_frames - end_f) / FPS + cfg["end"].get("hold", 3.0), 2)

# Caption shifts: everything after a join moves along by what was put in before it.
shifts, add = [], intro_len
shifts.append([0.0, add])
for p, c in zip(parts[1:], cuts[1:]):
    add += p["len"]
    shifts.append([c / FPS, round(add, 3)])
asm = {"shifts": shifts, "end_at": end_f / FPS, "end_len": end_len, "cuts": cuts, "end_frame": end_f}

def still(frame, name):
    out = os.path.join(D, "stills", name); os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run([FF, "-y", "-loglevel", "error", "-ss", f"{(frame + 0.5) / FPS:.4f}", "-i", MAIN,
                    "-frames:v", "1", out], check=True)
    return out

if MODE == "plan":
    json.dump(asm, open(os.path.join(D, "assembly.json"), "w"), indent=1)
    still(0, "intro-to.png")
    for i, c in enumerate(cuts[1:], start=2):
        still(c - 1, f"part-{i}-from.png"); still(c, f"part-{i}-to.png")
    still(end_f - 1, "end-from.png")
    print(f"intro   {intro_len:.1f}s   to=stills/intro-to.png")
    for i, (p, c) in enumerate(zip(parts[1:], cuts[1:]), start=2):
        print(f"part {i}  {p['len']:.1f}s   cut in at {c / FPS:7.2f}s on the edit's clock   from=stills/part-{i}-from.png to=stills/part-{i}-to.png")
    print(f"end     {end_len:.2f}s  takes over at {end_f / FPS:7.2f}s   from=stills/end-from.png   (render end.html with len={end_len})")
    print("wrote", os.path.join(D, "assembly.json"))
    sys.exit(0)

# ------------------------------------------------------------------ render
def count(folder):
    return len([n for n in os.listdir(P(folder)) if n.endswith(".png")])

assert abs(count(cfg["intro"]["frames"]) / FPS - intro_len) < 0.05, "intro frames do not match intro.len"
for p in parts[1:]:
    assert abs(count(p["card"]) / FPS - p["len"]) < 0.05, f"{p['card']} frames do not match its len"
got = count(cfg["end"]["frames"]) / FPS
assert got >= (main_frames - end_f) / FPS + 0.5, f"end card is {got:.1f}s but the voice needs {(main_frames - end_f) / FPS:.1f}s plus a hold: render it at len={end_len}"

inputs, graph, vcat, acat = ["-i", MAIN], [], [], []
idx = 1
def add_seq(folder):
    global idx
    inputs.extend(["-framerate", str(FPS), "-i", os.path.join(P(folder), "%04d.png")]); idx += 1
    return idx - 1
def add_img(path):
    global idx
    inputs.extend(["-i", P(path)]); idx += 1
    return idx - 1

n_main = len(parts)
# fps first: the edit's MP4 is not strictly constant frame rate (held frames are stored once),
# and the joins are counted in frames.
graph.append(f"[0:v]fps={FPS},split={n_main}" + "".join(f"[m{i}]" for i in range(n_main)))
graph.append(f"[0:a]asplit={n_main}" + "".join(f"[a{i}]" for i in range(n_main)))

def card(folder, seconds, tag):
    i = add_seq(folder)
    graph.append(f"[{i}:v]fps={FPS},scale=1920:1080,setsar=1,format=yuv420p[v{tag}]")
    graph.append(f"anullsrc=r=48000:cl=stereo,atrim=0:{seconds:.4f}[s{tag}]")
    vcat.append(f"[v{tag}]"); acat.append(f"[s{tag}]")

card(cfg["intro"]["frames"], intro_len, "intro")
bounds = cuts + [end_f]
for i, p in enumerate(parts):
    if i > 0:
        card(p["card"], p["len"], f"card{i}")
    a, b = bounds[i], bounds[i + 1]
    c = add_img(p["cover"])
    # the footage, placed in the window, with the stage cover (rounded corners, shadow, footer) on top
    graph.append(f"[m{i}]trim=start_frame={a}:end_frame={b},setpts=PTS-STARTPTS,"
                 f"pad=1920:1080:{WX}:{WY}:color=0x0b141d,setsar=1[p{i}]")
    graph.append(f"[p{i}][{c}:v]overlay=0:0:format=auto,format=yuv420p[seg{i}]")
    last = i == len(parts) - 1
    # the last stretch of voice carries on under the end card
    graph.append(f"[a{i}]atrim=start={a / FPS:.4f}" + ("" if last else f":end={b / FPS:.4f}") + f",asetpts=PTS-STARTPTS[as{i}]")
    vcat.append(f"[seg{i}]"); acat.append(f"[as{i}]")
e = add_seq(cfg["end"]["frames"])
graph.append(f"[{e}:v]fps={FPS},scale=1920:1080,setsar=1,format=yuv420p[vend]")
vcat.append("[vend]")

total = intro_len + sum(p["len"] for p in parts[1:]) + end_f / FPS + got
graph.append("".join(vcat) + f"concat=n={len(vcat)}:v=1:a=0[cat]")
graph.append("".join(acat) + f"concat=n={len(acat)}:v=0:a=1,apad,atrim=0:{total:.3f}[voice]")
if cfg.get("captions"):
    graph.append(f"[cat]subtitles=filename='{P(cfg['captions'])}':fontsdir='{P(cfg['fonts'])}'[v]")
else:
    graph.append("[cat]null[v]")
m = cfg.get("music")
if m:
    mi = add_img(m["file"])   # any input: here the music file
    lvl, st = m.get("level", 0.09), m.get("start", 0)
    # The bed is heard in the open, on the part cards and under the end card; the voice
    # pushes it almost out of hearing whenever it speaks, and it comes back slowly.
    graph.append(f"[{mi}:a]atrim=start={st},asetpts=PTS-STARTPTS,aloop=loop=-1:size=2147483647,atrim=0:{total:.3f},"
                 f"volume={lvl},afade=t=in:d=1.2,afade=t=out:st={total - 3.0:.3f}:d=3.0[bed]")
    graph.append("[voice]asplit=2[vo][key]")
    graph.append("[bed][key]sidechaincompress=threshold=0.02:ratio=12:attack=20:release=900[duck]")
    graph.append("[vo][duck]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[au]")
else:
    graph.append("[voice]anull[au]")

fg = os.path.join(D, "assemble.filter"); open(fg, "w").write(";\n".join(graph) + "\n")
out = P(cfg["out"])
subprocess.run([FF, "-y", "-loglevel", "error", *inputs, "-/filter_complex", fg, "-map", "[v]", "-map", "[au]",
                "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                "-ar", "48000", "-t", f"{total:.3f}", "-movflags", "+faststart", out], check=True)
print(f"wrote {out}  ({total:.1f}s: intro {intro_len}s, {len(parts) - 1} part cards, end card {got:.1f}s)")
