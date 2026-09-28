#!/usr/bin/env python3
"""Run prep_assets' video + image steps across worker processes (each clip is independent)."""
import os
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep_assets as p  # noqa: E402


def one(job):
    kind, out, spec = job
    if kind == "clip":
        src, t0, t1, vf, g, rate = spec
        p.clip(src, t0, t1, out, vf, g, rate, "blend" if src == p.B05 else "mci")
        if src == p.B05:
            p.clip(src, t0, t1, out.replace(".mp4", "_bg.mp4"), p.BG, "bgblur", rate, "blend")
    else:
        name, dur, g, rate = spec
        src, vf = p.real_v(name)
        p.clip(src, 0, dur, out, vf, g, rate, "mci" if name == "charles_day" else "blend")
    return out


if __name__ == "__main__":
    os.makedirs(os.path.join(p.A, "video"), exist_ok=True)
    jobs = [("clip", o, s) for o, s in p.CLIPS.items()] + [("real", o, s) for o, s in p.REAL_V.items()]
    with Pool(4) as pool:
        for out in pool.imap_unordered(one, jobs):
            print("built", out, flush=True)
    src, vf = p.real_v("charles_day")
    p.still(["-ss", "0.95", "-i", src], "charles_day_face.jpg", vf, "real")
    p.images()
    print("all done", flush=True)
