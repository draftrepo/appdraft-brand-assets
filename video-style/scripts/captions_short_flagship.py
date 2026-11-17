"""Captions for the 1080x1350 short: big two-line phrases under the video window.
Usage: captions_short_flagship.py <words.json> <out.ass> [end_at]"""
import json, re, sys
words = [w for s in json.load(open(sys.argv[1])) for w in s["words"]]
END = float(sys.argv[3]) if len(sys.argv) > 3 else 1e9
MAX, GAP = 34, 0.45
FIXES = [(r"\bzero\b", "Xero"), (r"\bon a difficult part\b", "on the difficult part"), (r"\bagent ?force\b", "Agentforce")]
lines, cur = [], []
def flush():
    if cur: lines.append((cur[0]["s"], cur[-1]["e"], "".join(w["w"] for w in cur).strip())); cur.clear()
for w in words:
    t = "".join(x["w"] for x in cur) + w["w"]
    gap = w["s"] - cur[-1]["e"] if cur else 0
    if cur and (len(t.strip()) > MAX or gap > GAP): flush()
    cur.append(w)
    if re.search(r"[.?!,]$", w["w"].strip()) and len("".join(x["w"] for x in cur).strip()) >= 14: flush()
flush()
ts = lambda t: f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1350
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter SemiBold,60,&H00F8F6F3,&H00F8F6F3,&H001D140B,&H001D140B,0,0,0,0,100,100,-0.5,0,1,0,0,8,72,72,935,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
with open(sys.argv[2], "w") as f:
    f.write(head)
    for i, (s, e, text) in enumerate(lines):
        if s >= END: break
        for a, b in FIXES: text = re.sub(a, b, text, flags=re.I)
        text = re.sub(r"\s+", " ", text).strip().rstrip(",")
        nxt = lines[i + 1][0] if i + 1 < len(lines) else e + 1
        end = min(e + 0.4, nxt - 0.02, END)
        f.write(f"Dialogue: 0,{ts(s)},{ts(end)},Cap,,0,0,0,,{{\\fad(100,100)}}{text}\n")
        print(ts(s), text)
