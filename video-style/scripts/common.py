"""Shared helpers for the demo-video scripts: paths, ffmpeg, the dev-browser server,
card rendering, caption styling and idle-stretch detection.

Nothing here hard-codes a machine path. The skill directory is found from this file's
location, ffmpeg from $FFMPEG / imageio-ffmpeg / PATH, and the dev-browser directory
from $DEV_BROWSER or the usual install locations.
"""
import json, os, shutil, subprocess, sys, time, urllib.request
from urllib.parse import urlencode

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(SCRIPTS)
FPS = 30


def _has_filters(ff):
    try:
        out = subprocess.run([ff, "-hide_banner", "-filters"], capture_output=True, text=True, timeout=30).stdout
        return " subtitles " in out and " freezedetect " in out
    except Exception:
        return False


def ffmpeg():
    """An ffmpeg that can burn captions (libass) and detect freezes. Homebrew builds often
    lack libass; the imageio-ffmpeg binary has it (x86_64 on Apple silicon, via Rosetta)."""
    import glob
    cands = [os.environ.get("FFMPEG")]
    try:
        import imageio_ffmpeg
        cands.append(imageio_ffmpeg.get_ffmpeg_exe())
        cands += sorted(glob.glob(os.path.join(os.path.dirname(imageio_ffmpeg.__file__), "binaries", "ffmpeg*")))
    except Exception:
        pass
    cands += sorted(glob.glob(os.path.expanduser("~/Library/Python/*/lib/python/site-packages/imageio_ffmpeg/binaries/ffmpeg*")))
    cands.append("ffmpeg")
    seen = set()
    for c in cands:
        c = c and (shutil.which(c) or c)
        if not c or c in seen or not os.path.isfile(c):
            continue
        seen.add(c)
        if _has_filters(c):
            return c
    sys.exit("No ffmpeg with the subtitles (libass) and freezedetect filters. Run: demo-video setup")


def dev_browser():
    """The dev-browser skill directory that holds node_modules and the logged-in profile."""
    cands = [os.environ.get("DEV_BROWSER"), os.path.expanduser("~/.claude/skills/dev-browser"),
             os.path.join(SKILL, "..", "dev-browser")]
    for c in cands:
        if c and os.path.isfile(os.path.join(c, "server.sh")) and os.path.isdir(os.path.join(c, "node_modules")):
            return os.path.realpath(c)
    for c in cands:
        if c and os.path.isfile(os.path.join(c, "server.sh")):
            return os.path.realpath(c)
    sys.exit("No dev-browser directory found. Set DEV_BROWSER to the dev-browser skill folder.")


def server_up():
    try:
        urllib.request.urlopen("http://localhost:9222/pages", timeout=3).read()
        return True
    except Exception:
        return False


def ensure_server():
    if server_up():
        return
    d = dev_browser()
    os.makedirs(os.path.join(d, "tmp"), exist_ok=True)
    log = open(os.path.join(d, "tmp", "server.log"), "a")
    subprocess.Popen(["./server.sh", "--headless"], cwd=d, stdout=log, stderr=log, start_new_session=True)
    for _ in range(60):
        time.sleep(1)
        if server_up():
            return
    sys.exit(f"dev-browser server did not start; see {d}/tmp/server.log")


def node_cmd(*args):
    """A command line that runs node tooling natively on Apple silicon. A child of an
    x86_64 python (Rosetta) inherits x86_64, so a universal node starts under emulation
    and esbuild then wants @esbuild/darwin-x64, which is rarely installed."""
    try:
        if subprocess.run(["arch", "-arm64", "/usr/bin/true"], capture_output=True).returncode == 0:
            return ["arch", "-arm64", *args]
    except Exception:
        pass
    return list(args)


def stage(*names):
    """Copy skill scripts (recorder.ts, card.ts) into dev-browser/tmp, where tsx resolves @/client.js."""
    d = dev_browser()
    os.makedirs(os.path.join(d, "tmp"), exist_ok=True)
    for n in names:
        shutil.copy(os.path.join(SCRIPTS, n), os.path.join(d, "tmp", n))
    return d


def render_card(out_dir, length, text, square=False, banner=False, page="gfx"):
    """Render card.html to PNG frames. text: eyebrow, title, sub, url (any may be empty)."""
    ensure_server()
    d = stage("card.ts")
    q = {k: v for k, v in text.items() if v}
    q["len"] = length
    if square:
        q["sq"] = 1
    if banner:
        q["banner"] = 1
    url = "file://" + os.path.join(SCRIPTS, "card.html") + "?" + urlencode(q)
    env = dict(os.environ, CARD_URL=url, LEN=str(length), OUT=os.path.abspath(out_dir), CARD_PAGE=page)
    if square:
        env.update(W="1080", H="1080")
    # The server is shared with other sessions, which may close pages under us: retry once.
    for attempt in (1, 2):
        r = subprocess.run(node_cmd("npx", "tsx", "tmp/card.ts"), cwd=d, env=env, stdout=subprocess.DEVNULL)
        if r.returncode == 0:
            return
        ensure_server()
    sys.exit(f"card render failed twice ({out_dir}). The error above is from tsx in {d}; "
             "run `demo-video setup`, which proves tsx can run there and says what to install if not.")


# Caption style for 16:9 videos (shared by captions_long.py and captions_mode.py).
ASS_HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter SemiBold,46,&H00FFFFFF,&H00FFFFFF,&H283D2D1F,&H283D2D1F,0,0,0,0,100,100,0,0,3,14,0,2,80,80,56,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ass_time(t):
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


# ---------------------------------------------------------------- idle stretches
# The screencast sends frames when anything repaints, including the fake cursor
# gliding over a page that is otherwise still. A viewer reads that as frozen, so a
# frame counts as a change only when something other than the cursor moved.
SCALE = 4            # compare at 1/4 size (400x225)
DIFF_LEVEL = 24      # grey-level difference that counts as a changed pixel
CURSOR_PX = 40       # without cursor marks: changed pixels a cursor alone can make
MASKED_PX = 6        # with cursor marks: the cursor is masked, so any real change counts
CURSOR_BOX = 34      # half-size (source px) of the box masked around the cursor


def _cursor_at(moves, t):
    """Cursor box (x0, y0, x1, y1) in source pixels at time t, from recorder 'cursor' marks."""
    import bisect
    i = bisect.bisect_right([m["t"] for m in moves], t) - 1
    if i < 0:
        return None
    m = moves[i]
    x, y = m["x"], m["y"]
    if t <= m["t"] + m.get("ms", 450) + 120 and "fx" in m:
        x0, x1 = sorted((m["fx"], x)); y0, y1 = sorted((m["fy"], y))
    else:
        x0 = x1 = x; y0 = y1 = y
    return (x0 - CURSOR_BOX, y0 - CURSOR_BOX, x1 + CURSOR_BOX, y1 + CURSOR_BOX)


def change_times(run_dir, marks, frames):
    """Timestamps (ms) of frames where the screen really changed. Cached in the run folder."""
    from PIL import Image, ImageChops, ImageDraw
    moves = [m for m in marks if m.get("kind") == "cursor"]
    cache = os.path.join(run_dir, ".changes.json")
    key = {"v": 2, "n": len(frames), "cursor": len(moves)}
    try:
        c = json.load(open(cache))
        if c.get("key") == key:
            return c["times"]
    except Exception:
        pass
    w, h = 1600 // SCALE, 900 // SCALE
    times, last, last_t = [], None, None
    for f in frames:
        try:
            im = Image.open(f["f"]); im.draft("L", (w, h)); im = im.convert("L").resize((w, h))
        except Exception:
            continue
        if last is None:
            times.append(f["t"]); last, last_t = im, f["t"]
            continue
        diff = ImageChops.difference(im, last).point(lambda v: 255 if v > DIFF_LEVEL else 0)
        limit = CURSOR_PX
        if moves:
            dr = ImageDraw.Draw(diff)
            for box in (_cursor_at(moves, last_t), _cursor_at(moves, f["t"])):
                if box:
                    dr.rectangle([v / SCALE for v in box], fill=0)
            limit = MASKED_PX
        if diff.histogram()[255] > limit:
            times.append(f["t"]); last, last_t = im, f["t"]
    try:
        json.dump({"key": key, "times": times}, open(cache, "w"))
    except OSError:
        pass
    return times


def tighten_ranges(ranges, changes, keep=1.1):
    """Remove still stretches from (start, end) ranges in seconds, keeping `keep`
    seconds after each change, so no stretch of an unchanged screen lasts longer."""
    out = []
    for a, e in ranges:
        inside = [t for t in changes if a < t < e]
        edges = [a] + inside + [e]
        cur = a
        for x, y in zip(edges, edges[1:]):
            if y - x > keep + 0.3:
                out.append((cur, x + keep)); cur = y - 0.1
        out.append((cur, e))
    return [(a, e) for a, e in out if e - a > 0.02]
