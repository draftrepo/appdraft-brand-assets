"""Burned-in captions for the flagship film: one line of plain text in the footer band,
no box, timed to the voice and moved along for every card the assembler inserts.

Usage: demo-video captions-flagship <words.json> <assembly.json> <out.ass> [script.txt]

assembly.json comes from `assemble.py plan` and holds "shifts": [[seconds on the edit's
clock, seconds to add from there on], ...] (the intro, then each part card), and
"end_at": captions stop there, because the end card carries the words itself.

Captions are for people watching muted, so they must be right. The transcriber is not:
edit FIXES for anything it mishears, and read every line against the script before the
final render (the list is printed).
"""
import json, re, sys

WORDS, ASSEMBLY, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
MAX_CHARS, GAP = 42, 0.55          # one line must fit between the part marker and the wordmark
asm = json.load(open(ASSEMBLY))
SHIFTS, END_AT = asm["shifts"], asm.get("end_at")
words = [w for s in json.load(open(WORDS)) for w in s["words"]]

FIXES = [
    (r"\bzero\b", "Xero"), (r"\bxero\b", "Xero"), (r"\bsales ?force\b", "Salesforce"),
    (r"\bagent ?force\b", "Agentforce"), (r"\bbright ?line\b", "Brightline"), (r"\bridge ?way\b", "Ridgeway"),
    (r"\bground work\b", "groundwork"), (r"\boff the shelf\b", "off-the-shelf"),
    (r"\bpurchase order\b", "purchase order"), (r"\bcredit note\b", "credit note"),
]

def shift(t):
    add = 0.0
    for at, by in SHIFTS:
        if t >= at - 1e-6:
            add = by
    return t + add

lines, cur = [], []
def flush():
    if cur:
        lines.append((cur[0]["s"], cur[-1]["e"], "".join(w["w"] for w in cur).strip()))
        cur.clear()
for w in words:
    text = "".join(x["w"] for x in cur) + w["w"]
    gap = w["s"] - cur[-1]["e"] if cur else 0
    if cur and (len(text.strip()) > MAX_CHARS or gap > GAP):
        flush()
    cur.append(w)
    if re.search(r"[.?!]$", w["w"].strip()) and len("".join(x["w"] for x in cur).strip()) >= 18:
        flush()
flush()

def ts(t):
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

# Inter Medium, 44 (about 37 px of text), paper white, no outline, no box: the footer band
# behind it is already dark. Bottom centre, 25 px up, which centres the line in the band.
head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Medium,44,&H00F8F6F3,&H00F8F6F3,&H001D140B,&H001D140B,0,0,0,0,100,100,-0.2,0,1,0,0,2,500,500,25,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
n = 0
with open(OUT, "w") as f:
    f.write(head)
    for i, (s, e, text) in enumerate(lines):
        if END_AT is not None and s >= END_AT - 0.05:
            break
        for a, b in FIXES:
            text = re.sub(a, b, text, flags=re.I)
        text = re.sub(r"\s+", " ", text).strip().rstrip(",")
        nxt = lines[i + 1][0] if i + 1 < len(lines) else e + 1
        end = min(e + 0.35, nxt - 0.02)
        if END_AT is not None:
            end = min(end, END_AT)
        # a 120 ms fade in and out: lines arrive, they do not blink
        f.write(f"Dialogue: 0,{ts(shift(s))},{ts(shift(s) + (end - s))},Cap,,0,0,0,,{{\\fad(120,120)}}{text}\n")
        print(f"{ts(shift(s))}  {text}"); n += 1
print(n, "caption lines")
