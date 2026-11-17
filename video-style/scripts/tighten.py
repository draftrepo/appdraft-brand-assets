"""Shorten every pause longer than 0.4s for short-form pacing, keeping every word.

Usage: FFMPEG=... python3 tighten.py <voice.wav> <words.json> <out.wav> <out_words.json>
Leaves 0.14s of room either side of each long gap. Writes word timings moved to match,
so cues.py and the caption scripts run on the tightened audio.
"""
import json, os, subprocess, sys

FF = os.environ["FFMPEG"]
src, words_in, out_wav, words_out = sys.argv[1:5]
KEEP = 0.14
segs = json.load(open(words_in))
W = [w for s in segs for w in s["words"]]
keep, cur = [], max(0.0, W[0]["s"] - 0.25)
for i in range(len(W) - 1):
    g0, g1 = W[i]["e"], W[i + 1]["s"]
    if g1 - g0 > 0.4:
        keep.append((cur, g0 + KEEP)); cur = g1 - KEEP
keep.append((cur, W[-1]["e"] + 0.6))

def moved(t):
    off = 0.0
    for a, b in keep:
        if t < a: return off
        if t <= b: return off + (t - a)
        off += b - a
    return off

fc = "".join(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[p{i}];" for i, (a, b) in enumerate(keep))
fc += "".join(f"[p{i}]" for i in range(len(keep))) + f"concat=n={len(keep)}:v=0:a=1[out]"
subprocess.run([FF, "-y", "-loglevel", "error", "-i", src, "-filter_complex", fc, "-map", "[out]", out_wav], check=True)
out = []
for s in segs:
    ws = [{**w, "s": round(moved(w["s"]), 3), "e": round(moved(w["e"]), 3)} for w in s["words"]]
    out.append({"start": ws[0]["s"], "end": ws[-1]["e"], "text": s.get("text", ""), "words": ws})
json.dump(out, open(words_out, "w"), indent=1)
print(f"{W[-1]['e']:.1f}s -> {sum(b - a for a, b in keep):.1f}s")
