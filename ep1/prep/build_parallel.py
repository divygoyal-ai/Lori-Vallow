#!/usr/bin/env python3
"""Run prep_assets' video + image steps across worker processes (each clip is independent)."""
import os
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep_assets as p  # noqa: E402


def one(item):
    out, (src, t0, t1, vf, g, rate) = item
    mode = "blend" if src in (p.B03, p.B05) else "mci"
    p.clip(src, t0, t1, out, vf, g, rate, mode)
    if out.startswith("real_"):
        bgvf = p.BG if vf != p.PORTRAIT and not vf.startswith("crop=950") else "scale=1080:1920"
        p.clip(src, t0, t1, out.replace(".mp4", "_bg.mp4"), bgvf, "bgblur", rate, "blend")
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(p.A, "video"), exist_ok=True)
    with Pool(4) as pool:
        for out in pool.imap_unordered(one, list(p.CLIPS.items())):
            print("built", out, flush=True)
    p.still(["-ss", "135.95", "-i", p.DRAFT], "charles_day_face.jpg", p.PORTRAIT, "real")
    p.images()
    print("all done", flush=True)
