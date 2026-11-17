"""Addition to common.py: render any template in <skill>/gfx/ to PNG frames.

Paste render_gfx() into common.py beside render_card(), copy gfx.ts into scripts/, add
"gfx.ts" to the cp line in run.sh setup, and add the `gfx` case from run_sh_gfx_case.txt.
"""
import os, subprocess, sys
from urllib.parse import urlencode
from common import SKILL, ensure_server, node_cmd, stage


def render_gfx(template, out_dir, length, params, alpha=False, still=False, size=(1920, 1080), page="gfx"):
    """template: file name in <skill>/gfx (intro.html, part.html, end.html, stage.html, callout.html).
    params: the template's query values. Image values (from, to, bg, img) must be absolute paths."""
    ensure_server()
    d = stage("gfx.ts")
    q = {k: v for k, v in params.items() if v not in ("", None)}
    for k in ("from", "to", "bg", "img"):
        if k in q and not str(q[k]).startswith("file:"):
            q[k] = "file://" + os.path.abspath(q[k])
    q["len"] = length
    url = "file://" + os.path.join(SKILL, "gfx", template) + "?" + urlencode(q)
    env = dict(os.environ, CARD_URL=url, LEN=str(length), OUT=os.path.abspath(out_dir), CARD_PAGE=page,
               W=str(size[0]), H=str(size[1]))
    if alpha:
        env["ALPHA"] = "1"
    if still:
        env["STILL"] = "1"
    for attempt in (1, 2):   # the server is shared: retry once, as render_card does
        if subprocess.run(node_cmd("npx", "tsx", "tmp/gfx.ts"), cwd=d, env=env, stdout=subprocess.DEVNULL).returncode == 0:
            return
        ensure_server()
    sys.exit(f"gfx render failed twice ({template} -> {out_dir}); run `demo-video setup`.")
