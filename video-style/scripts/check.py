"""Check a rendered video before anyone sees it: no frozen stretches, and a contact sheet to look at.

Usage: demo-video check <video.mp4> [--out DIR] [--max-still 3] [--head S] [--tail S] [--step S]

- Runs ffmpeg freezedetect (n=0.001) and fails if any still lasts longer than
  --max-still seconds (default 3), ignoring the first --head and last --tail seconds
  (the intro and end cards, which are meant to hold). A still frame from each freeze
  is saved as freeze-<seconds>.jpg so you can see what sat still.
- Pulls a still every --step seconds (default: about 36 across the video, 2 to 5 s
  apart) and tiles them, timestamped, into sheet-01.png, sheet-02.png ... (12 a sheet).
  Read every sheet: captions readable and matching the screen, zooms not cutting
  titles, no pop-ups, toasts, hover cards or error banners, nothing private.

Exit code 1 if a freeze fails the check.
"""
import argparse, glob, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import SKILL, ffmpeg

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("--out")
ap.add_argument("--max-still", type=float, default=3.0)
ap.add_argument("--head", type=float, default=0.0)
ap.add_argument("--tail", type=float, default=0.0)
ap.add_argument("--step", type=float)
a = ap.parse_args()

FF = ffmpeg()
video = os.path.abspath(a.video)
out = os.path.abspath(a.out or os.path.splitext(video)[0] + "-check")
os.makedirs(out, exist_ok=True)
for f in glob.glob(os.path.join(out, "*.png")) + glob.glob(os.path.join(out, "*.jpg")):
    os.remove(f)

log = subprocess.run([FF, "-hide_banner", "-i", video, "-map", "0:v", "-vf", "freezedetect=n=0.001:d=1",
                      "-f", "null", "-"], capture_output=True, text=True).stderr
m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", log)
dur = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
starts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", log)]
ends = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", log)]
ends += [dur] * (len(starts) - len(ends))

lo, hi = a.head, dur - a.tail
fails, notes = [], []
for s, e in zip(starts, ends):
    seen = min(e, hi) - max(s, lo)
    if seen > a.max_still:
        fails.append((s, e))
    elif e - s > a.max_still and seen > 0:
        notes.append((s, e))

def grab(t, path, width=640):
    subprocess.run([FF, "-y", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1",
                    "-vf", f"scale={width}:-2", path], check=True)

for s, e in fails:
    grab(s + min(1.0, (e - s) / 2), os.path.join(out, f"freeze-{s:06.1f}.jpg"), 960)

step = a.step or min(5.0, max(2.0, dur / 36))
times, t = [], 0.5
while t < dur - 0.2:
    times.append(t); t += step
font_path = os.path.join(SKILL, "assets", "fonts", "Inter-600.ttf")
try:
    font = ImageFont.truetype(font_path, 22)
except Exception:
    font = ImageFont.load_default()
tiles = []
for i, t in enumerate(times):
    p = os.path.join(out, f"_s{i:03d}.jpg")
    grab(t, p)
    im = Image.open(p).convert("RGB"); os.remove(p)
    label = f"{int(t // 60)}:{t % 60:04.1f}"
    frozen = any(s <= t <= e for s, e in fails)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 92 if not frozen else 190, 30], fill=(200, 30, 30) if frozen else (0, 0, 0))
    d.text((8, 3), label + ("  STILL" if frozen else ""), fill=(255, 255, 255), font=font)
    tiles.append(im)
sheets = []
for k in range(0, len(tiles), 12):
    group = tiles[k:k + 12]
    w, h = group[0].size
    sheet = Image.new("RGB", (w * 3 + 8, h * 4 + 12), (255, 255, 255))
    for j, im in enumerate(group):
        sheet.paste(im, ((j % 3) * (w + 4), (j // 3) * (h + 4)))
    path = os.path.join(out, f"sheet-{len(sheets) + 1:02d}.png")
    sheet.save(path); sheets.append(path)

print(f"length {dur:.1f}s; stills over {a.max_still:g}s outside the first {a.head:g}s and last {a.tail:g}s: {len(fails)}")
for s, e in fails:
    print(f"  STILL {s:6.1f}s to {e:6.1f}s ({e - s:.1f}s)  see freeze-{s:06.1f}.jpg")
for s, e in notes:
    print(f"  note: {s:.1f}s to {e:.1f}s is still for {e - s:.1f}s but mostly inside a card")
print("contact sheets (read every one):")
for p in sheets:
    print("  " + p)
if fails:
    print("FAIL: fix every still before delivery (see SKILL.md, No frozen screens).")
    sys.exit(1)
print("PASS")
