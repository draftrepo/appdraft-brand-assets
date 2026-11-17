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
    (r"\bbuilds from\b", "bills from"), (r"\bputting it to the\b", "fitting it to the"), (r"links to records", "links to the records"), (r"\bbuild from a deal\b", "bill from a deal"),
    (r"\bFinance lives\b", "finance lives"), (r"credit notes statements", "credit notes, statements"),
    (r"who's late what", "who's late, what"), (r"off the deals you", "off the deals, you"),
    (r"branded emails helping", "branded emails, helping"), (r"own AI Agentforce", "own AI, Agentforce"),
    (r"Salesforce by itself so", "Salesforce by itself, so"), (r"works for you rather", "works for you, rather"),
    (r"post it to Xero so", "post it to Xero, so"),
    (r"\bstraightaway\b", "straight away"), (r"\bon a difficult part\b", "on the difficult part"), (r"\bcredit note\b", "credit note"),
]

def shift(t):
    add = 0.0
    for at, by in SHIFTS:
        if t >= at - 1e-6:
            add = by
    return t + add

import math
FIXW = {"builds": "bills", "build": "build"}
# Sentences first, then each sentence split into balanced lines of at most MAX_CHARS,
# preferring to break after a comma.
sents, cur = [], []
for w in words:
    cur.append(w)
    if re.search(r"[.?!]$", w["w"].strip()):
        sents.append(cur); cur = []
if cur: sents.append(cur)
lines = []
for sw in sents:
    text = "".join(x["w"] for x in sw).strip()
    k = max(1, math.ceil(len(text) / MAX_CHARS))
    while True:
        target = len(text) / k; chunks, buf = [], []
        for i, w in enumerate(sw):
            buf.append(w)
            ln = len("".join(x["w"] for x in buf).strip())
            rest = len(sw) - i - 1
            comma = w["w"].strip().endswith(",")
            if rest and len(chunks) < k - 1 and (ln >= target * 0.98 or (comma and ln >= target * 0.6)):
                chunks.append(buf); buf = []
        if buf: chunks.append(buf)
        if all(len("".join(x["w"] for x in c).strip()) <= MAX_CHARS for c in chunks) or k > 6: break
        k += 1
    for c in chunks:
        lines.append((c[0]["s"], c[-1]["e"], "".join(x["w"] for x in c).strip()))

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
