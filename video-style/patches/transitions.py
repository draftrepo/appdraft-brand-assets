"""Scene transitions for edit.py, as pure functions on PIL images.

Each takes the outgoing and incoming source frames (both 1600x900) and a progress
e in 0..1, and returns the frame to show. edit_flagship.py calls transition() for the
first DUR[kind] seconds of any beat named under "transitions" in the config.

  dissolve  0.35 s  plain cross-fade (what edit.py already does at cuts)
  push      0.60 s  the old screen leaves to the left as the new one arrives from the right,
                    with a narrow dark gutter between them and a little motion blur
  through   0.70 s  the camera pushes into a point on the old screen and comes out on the
                    new one, which settles from slightly too close
  cut       0       nothing
"""
from PIL import Image

DUR = {"cut": 0.0, "dissolve": 0.35, "push": 0.60, "through": 0.70}
INK = (11, 20, 29)
GUTTER = 28          # px of backdrop colour between the two screens in a push

def ease_io(x):      # cubic-bezier(.65,0,.35,1), near enough: cubic in-out
    return 4 * x * x * x if x < 0.5 else 1 - pow(-2 * x + 2, 3) / 2

def ease_in(x):
    return x * x * x

def ease_out(x):
    return 1 - pow(1 - x, 3)

def _hblur(im, amount):
    """Cheap horizontal motion blur: squeeze the width, stretch it back."""
    if amount < 1.5:
        return im
    w, h = im.size
    return im.resize((max(8, int(w / amount)), h), Image.BOX).resize((w, h), Image.BILINEAR)

def _soft(im, amount):
    if amount < 1.2:
        return im
    w, h = im.size
    return im.resize((max(8, int(w / amount)), max(8, int(h / amount))), Image.BOX).resize((w, h), Image.BILINEAR)

def _zoom(im, z, fx, fy):
    """Scale the image by z about (fx, fy), keeping the frame size."""
    w, h = im.size
    cw, ch = w / z, h / z
    x0 = min(max(fx - cw * fx / w, 0), w - cw); y0 = min(max(fy - ch * fy / h, 0), h - ch)
    return im.resize((w, h), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))

def dissolve(a, b, e):
    return Image.blend(a, b, e)

def push(a, b, e):
    w, h = a.size
    p = ease_io(e)
    speed = abs(ease_io(min(e + 0.02, 1)) - ease_io(max(e - 0.02, 0))) / 0.04     # 0..~3
    blur = 1 + speed * 5
    shift = int(round(p * (w + GUTTER)))
    out = Image.new("RGB", (w, h), INK)
    out.paste(_hblur(a, blur), (-shift, 0))
    out.paste(_hblur(b, blur), (w + GUTTER - shift, 0))
    return out

def through(a, b, e, fx=800, fy=450):
    za = 1 + 0.42 * ease_in(e)                 # old screen: accelerating in
    zb = 1 + 0.10 * (1 - ease_out(e))          # new screen: settles from 10% too close
    mix = min(max((e - 0.28) / 0.44, 0), 1)    # cross over the middle of the move
    mix = mix * mix * (3 - 2 * mix)
    soft = 1 + 6.0 * (1 - abs(2 * e - 1)) ** 2 # softest at the crossing, so two screens of text never read at once
    fa = _soft(_zoom(a, za, fx, fy), soft)
    fb = _soft(_zoom(b, zb, fx, fy), soft if e < 0.8 else 1)
    return Image.blend(fa, fb, mix)

def transition(kind, a, b, e, focus=None):
    a, b = a.convert("RGB"), b.convert("RGB")
    if b.size != a.size:
        b = b.resize(a.size, Image.LANCZOS)
    if kind == "push":
        return push(a, b, e)
    if kind == "through":
        return through(a, b, e, *(focus or (a.size[0] / 2, a.size[1] / 2)))
    return dissolve(a, b, e)

if __name__ == "__main__":   # preview: python3 transitions.py from.png to.png out_dir
    import os, sys
    a, b, out = Image.open(sys.argv[1]), Image.open(sys.argv[2]), sys.argv[3]
    os.makedirs(out, exist_ok=True)
    for kind, focus in (("push", None), ("through", (1560, 190))):
        n = int(DUR[kind] * 30)
        for i in range(n):
            transition(kind, a, b, i / n, focus).save(os.path.join(out, f"{kind}-{i:02d}.png"))
    print("wrote", out)
