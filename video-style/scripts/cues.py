"""Find when each beat's cue phrase is spoken.

Usage: python3 cues.py <words.json> <phrases.json> <cues.json>

phrases.json is a list of [beat, phrase] in order, e.g.
  [["open", "Once a deal"], ["tab", "Deal Builder is an"], ["type", "If I start typing"]]
Pick a phrase of two to four words that starts the sentence the beat goes with.
Each search starts after the previous cue, so repeated words are fine.
The output also has "end" (the last spoken word), which the editor needs.
"""
import json, re, sys

words = [w for s in json.load(open(sys.argv[1])) for w in s["words"]]
norm = lambda x: re.sub(r"[^a-z0-9%]", "", x.lower())
toks = [norm(w["w"]) for w in words]

def find(phrase, after):
    p = [norm(x) for x in phrase.split()]
    for i in range(len(toks) - len(p) + 1):
        if words[i]["s"] >= after and toks[i:i + len(p)] == p:
            return words[i]["s"]
    sys.exit(f'Cue phrase not found after {after:.1f}s: "{phrase}". Check the transcript and use the words as spoken.')

out, t = {}, 0.0
for beat, phrase in json.load(open(sys.argv[2])):
    t = find(phrase, t)
    out[beat] = t
    print(f"{beat:10s} {t:7.2f}  {phrase}")
out["end"] = words[-1]["e"]
print("end", out["end"])
json.dump(out, open(sys.argv[3], "w"), indent=1)
