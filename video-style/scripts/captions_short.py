"""Short-form captions (ASS, 1080x1080): a few big words at a time, the spoken word lit up teal, each group popping in.

Usage: demo-video captions-short <words.json> <out.ass> ["Deal Builder,Field Service"]
The optional third argument (or KEEP in the environment) lists product names to keep on one line.
"""
import json, re, sys

WORDS, OUT = sys.argv[1], sys.argv[2]
MAX_CHARS, GAP = 20, 0.35
TEAL, WHITE = r"&HBFD63C&", r"&HFFFFFF&"   # ASS colours are BGR
FIX = {"license": "licence", "licenses": "licences"}

words = [dict(w) for s in json.load(open(WORDS)) for w in s["words"]]
for w in words:
    core = re.sub(r"[^A-Za-z]", "", w["w"]).lower()
    if core in FIX:
        w["w"] = w["w"].replace(core, FIX[core])

# Keep product names on one caption line: KEEP="Deal Builder,Field Service" (comma-separated).
import os
KEEP = [k.split() for k in (sys.argv[3] if len(sys.argv) > 3 else os.environ.get("KEEP", "")).split(",") if k.strip()]
clean = lambda w: re.sub(r"[^A-Za-z0-9]", "", w).lower()
merged, i = [], 0
while i < len(words):
    for k in KEEP:
        if [clean(x["w"]) for x in words[i:i + len(k)]] == [clean(x) for x in k]:
            merged.append({**words[i], "w": "".join(x["w"] for x in words[i:i + len(k)]), "e": words[i + len(k) - 1]["e"]})
            i += len(k); break
    else:
        merged.append(words[i]); i += 1
words = merged

groups, cur = [], []
for w in words:
    text = "".join(x["w"] for x in cur) + w["w"]
    gap = w["s"] - cur[-1]["e"] if cur else 0
    if cur and (len(text.strip()) > MAX_CHARS or gap > GAP):
        groups.append(cur); cur = []
    cur.append(w)
    if re.search(r"[.?!,]$", w["w"].strip()) and len(cur) >= 2:
        groups.append(cur); cur = []
if cur: groups.append(cur)

def ts(t):
    t = max(0, t); return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"

head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1080
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Pop,Inter Bold,74,&H00FFFFFF,&H00FFFFFF,&H003D2D1F,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,50,50,92,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
lines = []
for gi, g in enumerate(groups):
    g_end = min(g[-1]["e"] + 0.25, groups[gi + 1][0]["s"] - 0.01) if gi + 1 < len(groups) else g[-1]["e"] + 0.6
    for wi, w in enumerate(g):
        start = w["s"] if wi else g[0]["s"]
        end = g[wi + 1]["s"] if wi + 1 < len(g) else g_end
        parts = []
        for k, x in enumerate(g):
            t = x["w"].strip()
            parts.append(("{\\c" + TEAL + "}" if k == wi else "{\\c" + WHITE + "}") + t)
        pop = "{\\fscx82\\fscy82\\t(0,90,\\fscx100\\fscy100)}" if wi == 0 else ""
        lines.append(f"Dialogue: 0,{ts(start)},{ts(end)},Pop,,0,0,0,,{pop}{' '.join(parts)}")
open(OUT, "w").write(head + "\n".join(lines) + "\n")
print(len(groups), "groups;", " | ".join(" ".join(x["w"].strip() for x in g) for g in groups[:8]))
