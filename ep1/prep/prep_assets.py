#!/usr/bin/env python3
"""Prepare every media asset used by the Episode 1 HyperFrames composition.

Sources live in ../ep1_src (downloaded from the producer's Drive folder):
  audio/vo_main.mp3   final voiceover (its picture track is the clean, caption-free
                      draft, used only as the source of the AI shots)
  audio/bg_music.mp3  background music supplied by the producer
  videos/*.mp4        government-released bodycam / interview footage
  images/*.jpg        court filings, booking photo, CC location photos

  ai/*                the producer's original AI generations (720x1280) + one AI still

This trims every clip to exactly the length it plays for (baking slow motion
with motion interpolation), bakes the episode's colour grade, normalises
loudness and synthesises the few SFX the bundled library does not cover.
The edit itself lives in build.py -> index.html.
"""
import os
import subprocess

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
SRC = os.path.join(os.path.dirname(PROJ), "ep1_src")
A = os.path.join(PROJ, "assets")
DRAFT = os.path.join(SRC, "audio", "vo_main.mp3")
V = lambda n: os.path.join(SRC, "videos", n)


def ff(*args):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *args], check=True)


# v4 grade: the same dark, warm, low-key true-crime look as v3 (deep blacks, warm lamp-coloured
# highlights, muted colour, no added grain) but lifted after producer feedback that v3 was blacked
# out: a gentler toe keeps shadow detail and every clip is solved to a brighter target, so faces,
# rooms and objects always read. Only exposure (gamma) and saturation are solved per clip.
CURVE = "curves=all='0/0 0.08/0.045 0.3/0.21 0.6/0.5 0.85/0.8 1/0.93'"
WARM = "colorbalance=rs=0.01:bs=-0.012:rm=0.012:bm=-0.02:rh=0.045:gh=0.012:bh=-0.05"
VIG = "vignette=angle=PI/5"
# documents keep the v2 paper look the producer liked: warm, slightly dim paper on a dark desk
DOCLOOK = ("eq=contrast=1.1:saturation=0.3,curves=all='0/0 0.1/0.03 0.5/0.44 1/0.82',"
           "colorbalance=rh=0.04:gh=0.02:bh=-0.03,vignette=angle=PI/3.8")
# (target mean luma, target mean saturation)
TARGET = {
    "ai": (0.14, 0.3),  # AI shots
    "day": (0.13, 0.24),  # the daylight house shot at dusk
    "real": (0.19, 0.28),  # real footage from the draft
    "night": (0.19, 0.28),  # night bodycam, full-frame vertical
    "interview": (0.21, 0.28),  # interview room
    "photo": (0.24, 0.32),  # family photos / booking photo
    "portrait": (0.2, 0.4),
    "mugshot": (0.34, 0.3),  # booking photo on a white height chart: the bright chart would otherwise crush the face  # opening portrait of Charles: keeps natural skin colour
    "place": (0.16, 0.28),  # CC location photos, full frame
    "doc": (0.38, None),  # court filing paper on the dark desk (v2 look)
    "bgblur": (0.07, 0.24),  # blurred backdrops behind the two landscape cards / polaroid
}


def _stats(args, vf):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", *args, "-vf", vf + ",scale=108:192,format=rgb24", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, 3) / 255
    mx, mn = a.max(1), a.min(1)
    return (a @ [0.2126, 0.7152, 0.0722]).mean(), np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0).mean()


def graded(args, pre, g):
    ty, ts = TARGET[g]
    if g == "doc":
        lo, hi = 0.3, 4.0
        for _ in range(9):
            mid = (lo * hi) ** 0.5
            y, _s = _stats(args, f"{pre},eq=gamma={mid:.3f},{DOCLOOK}")
            lo, hi = (mid, hi) if y < ty else (lo, mid)
        return f"{pre},eq=gamma={(lo * hi) ** 0.5:.3f},{DOCLOOK}"
    extra = ",gblur=sigma=40" if g == "bgblur" else ""
    # measure on small frames: the look is per-pixel, so upscaling / sharpening / blur can be skipped here
    drop = ("scale=", "unsharp=", "gblur=") + (("crop=",) if g == "bgblur" else ())
    cheap = ",".join(f for f in pre.split(",") if not f.startswith(drop)) or "null"
    sat = 1.0
    for _ in range(2):  # saturation and exposure interact a little: two passes settle both
        lo, hi = 0.3, 4.0
        for _ in range(9):
            mid = (lo * hi) ** 0.5
            y, s = _stats(args, f"{cheap},eq=gamma={mid:.3f}:saturation={sat:.3f},{CURVE},{WARM}")
            lo, hi = (mid, hi) if y < ty else (lo, mid)
        gamma = (lo * hi) ** 0.5
        sat = float(np.clip(sat * ts / max(s, 1e-3), 0.75 if g == "ai" else 0.45, 1.2))  # AI shots keep their colour
    return f"{pre}{extra},eq=gamma={gamma:.3f}:saturation={sat:.3f},{CURVE},{WARM},{VIG}"


ENC = ["-an", "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-pix_fmt", "yuv420p", "-r", "30"]
UP = "scale=1080:1920:flags=lanczos,unsharp=5:5:0.45"  # 720x1280 AI originals -> 1080x1920


def slow(rate, mode="mci"):
    # slow-motion baked with motion interpolation, so slowed shots stay smooth instead of stepping
    if rate >= 0.999:
        return "fps=30"
    return f"setpts=PTS/{rate},minterpolate=fps=30:mi_mode={mode}" + (":mc_mode=aobmc:vsbmc=1" if mode == "mci" else "")


def clip(src, t0, t1, out, vf, g, rate=1.0, mode="mci"):
    p = os.path.join(A, "video", out)
    if os.path.exists(p):
        return
    vf = graded(["-ss", f"{t0}", "-to", f"{t1}", "-i", src, "-r", "0.7"], vf, g)
    vf = f"{slow(rate, mode)},{vf}"
    ff("-ss", f"{t0}", "-to", f"{t1}", "-i", src, "-vf", vf, *ENC, p)


def still(args, out, vf, g):
    ff(*args, "-frames:v", "1", "-vf", graded([*args, "-frames:v", "1"], vf, g), "-q:v", "1", os.path.join(A, "img", out))


AIDIR = os.path.join(SRC, "ai")
AIV = lambda n: os.path.join(AIDIR, n)
GEN = lambda n: os.path.join(SRC, "gen", n)  # Magnific: Nano Banana 2 reference image -> Kling 3.0 video
B05 = V("05_lori_interview.mp4")  # Chandler PD interview room, Jul 11 2019
WIDE = "unsharp=3:3:0.3"  # interview room, full 1280x720 frame (the only landscape shots, ~4% of the runtime)
KL = "scale=1080:1920:flags=lanczos"  # Kling 3.0 output (1080x1916) -> 1080x1920


def real_v(name):
    # Real footage, cut as a face-centred 9:16 crop (upin/, see crop list in docs) and upscaled to
    # 1080x1920 with Magnific Precision (upout/). Falls back to a plain lanczos upscale of the crop.
    up = os.path.join(SRC, "upout", name + ".mp4")
    if os.path.exists(up):
        return up, "scale=1080:1920:flags=lanczos"
    return os.path.join(SRC, "upin", name + ".mp4"), "scale=1080:1920:flags=lanczos,unsharp=5:5:0.5"


# (source, t0, t1, filter, grade, rate) -> every clip is baked to exactly the length it plays for
CLIPS = {
    # AI shots: the producer's original generations (720x1280), all faceless / from behind ...
    "ai_garden_kids.mp4": (AIV("m3_tCrF.mp4"), 0.3, 3.72, UP, "ai", 1.0),
    "ai_boy_floor.mp4": (AIV("m6_Lw3h.mp4"), 0.0, 3.62, UP, "ai", 0.77),  # ends before he turns his head
    # ... and new Magnific generations (Nano Banana 2 reference -> Kling 3.0), no faces anywhere
    "ai_party.mp4": (GEN("v_party_clean.mp4"), 0.0, 4.0, UP, "ai", 0.94),  # Kling 2.5, first second dropped (a guest faced camera), one background head softened
    "ai_family_hug.mp4": (GEN("v_porch.mp4"), 0.2, 2.0, UP, "ai", 0.72),  # Kling 2.5, slow motion: all four on the porch, from behind
    "ai_calendar.mp4": (GEN("v_calendar.mp4"), 0.0, 2.9, KL, "ai", 1.0),
    "ai_watching.mp4": (GEN("v_watching.mp4"), 0.0, 4.7, KL, "ai", 1.0),
    "ai_family_court.mp4": (GEN("v_court.mp4"), 0.0, 2.8, KL, "ai", 1.0),
    # Chandler PD interview with Lori, Jul 11 2019 -> the two landscape cards
    "real_int_1.mp4": (B05, 1194.5, 1198.3, WIDE, "interview", 1.0),
    "real_int_3.mp4": (B05, 1993.0, 1998.0, WIDE, "interview", 1.0),
    # Maricopa County Superior Court (CC photo), whole sign on a landscape card
    "real_court.mp4": (GEN("court_loop.mp4"), 0.0, 4.5, "null", "place", 1.0),
}
CARDS = {"real_int_1.mp4", "real_int_3.mp4", "real_court.mp4"}  # landscape cards get a blurred backdrop
# real footage, full-screen vertical: (crop name, seconds used, grade, rate)
REAL_V = {
    "real_charles_day.mp4": ("charles_day", 1.0, "real", 0.45),  # draft: Chandler PD bodycam, Charles in daylight
    "real_lori_car.mp4": ("lori_car", 4.3, "real", 1.0),
    "real_charles_cap.mp4": ("charles_cap", 3.3, "real", 1.0),  # Charles in his cap in the garage (cursor cropped out)
    "real_night_a.mp4": ("night_a", 4.65, "night", 1.0),  # Chandler PD bodycam, Jan 31 2019
    "real_night_b.mp4": ("night_b", 2.2, "night", 1.0),
    "real_night_c.mp4": ("night_c", 3.6, "night", 1.0),
    "real_to_door.mp4": ("to_door", 3.1, "night", 1.0),
    "real_night_face.mp4": ("night_face", 3.05, "night", 1.0),
    "real_bodycam_walk.mp4": ("bodycam_walk", 4.4, "night", 1.0),
    "real_gate.mp4": ("gate", 2.2, "night", 1.0),
    "real_charles_close.mp4": ("charles_close", 2.7, "night", 1.0),
    "real_walkaway.mp4": ("walkaway", 4.6, "night", 1.0),
    "real_int_2.mp4": ("int_2", 3.9, "interview", 1.0),
}
BG = "scale=-2:1920,crop=1080:1920"


def video():
    for out, (src, t0, t1, vf, g, rate) in CLIPS.items():
        clip(src, t0, t1, out, vf, g, rate, "blend" if src == B05 else "mci")
        if out in CARDS:  # blurred, darkened full-frame backdrop behind the landscape cards
            clip(src, t0, t1, out.replace(".mp4", "_bg.mp4"), BG, "bgblur", rate, "blend")
    for out, (name, dur, g, rate) in REAL_V.items():
        src, vf = real_v(name)
        clip(src, 0, dur, out, vf, g, rate, "mci" if name == "charles_day" else "blend")


def images():
    im = os.path.join(SRC, "images")
    img = lambda out: os.path.join(A, "img", out)
    for n, out in [("div_p01.jpg", "doc_p01.jpg"), ("div_p03.jpg", "doc_p03.jpg"), ("div_p04.jpg", "doc_p04.jpg")]:
        src = os.path.join(im, n)
        ff("-i", src, "-vf", graded(["-i", src], "null", "doc"), "-q:v", "1", img(out))
    for n in ["chandler_aerial.jpg"]:
        src = os.path.join(im, n)
        ff("-i", src, "-vf", graded(["-i", src], "scale=-2:2200:flags=lanczos", "place"), "-q:v", "1", img(n))
    # AI stills (pre-scaled to 1080x1920 in gen/): family watching TV (screen softened), the world
    # ending (Nano Banana 2, understated), and the "I will..." note from the draft
    for n, out in [("family_tv_still.png", "ai_family_tv.jpg"), ("world_end_1080.png", "ai_world.jpg"), ("i_will.png", "ai_i_will.jpg"),
                   ("writer_desk_1080.png", "ai_writer_desk.jpg")]:  # the writer's desk, nobody in frame
        still(["-i", GEN(n)], out, "null", "ai")
    # booking photo -> polaroid print (+ blurred backdrop); family photos -> full-screen stills
    src = ["-i", os.path.join(im, "mug_lori_kauai.jpg")]
    crop = "crop=440:557:172:4,scale=648:820:flags=lanczos"
    still(src, "lori_booking.jpg", crop, "photo")
    still(src, "lori_booking_bg.jpg", f"{crop},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", "bgblur")
    # Chad Daybell, booking photo (Fremont County, 2020) -> polaroid print + blurred backdrop
    src = ["-i", os.path.join(im, "mug_chad_2020.jpg")]
    crop = "crop=948:1200:440:0,scale=648:820:flags=lanczos"
    still(src, "chad_booking.jpg", crop, "mugshot")
    still(src, "chad_booking_bg.jpg", f"{crop},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", "bgblur")
    photos = {
        "photo_wedding.jpg": (["-ss", "138.3", "-i", DRAFT], "null"),
        # Charles holding a baby, shown whole on a tall polaroid print; the baby's face is blurred (gen/baby_photo_safe.png)
        "photo_charles_baby.jpg": (["-i", GEN("baby_photo_safe.png")], "crop=1080:1662:0:238"),
        "photo_charles.jpg": (["-ss", "133.2", "-i", DRAFT], "null"),
    }
    for out, (args, crop) in photos.items():
        still(args, out, crop, "photo")
    still(["-i", GEN("baby_photo_safe.png")], "photo_charles_baby_bg.jpg",
          "crop=1080:1662:0:238,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", "bgblur")
    # opening: Charles, arms crossed (real photo supplied by the producer), full screen
    # (pre-scaled to 1080x1920 first: the grade solver measures without scale filters, so it needs the final framing)
    big = GEN("charles_portrait_1080.png")
    ff("-i", os.path.join(im, "charles_portrait.png"), "-vf", "scale=1190:1920:flags=lanczos,crop=1080:1920:55:0,unsharp=5:5:0.25", big)
    still(["-i", big], "charles_portrait.jpg", "null", "portrait")


def audio():
    # VO: the product. Two-pass loudnorm to -16 LUFS / -1.5 dBTP so the final mix lands near the
    # references (-15 LUFS) once music and SFX sit under it.
    vo = os.path.join(SRC, "audio", "vo_main.mp3")
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", vo, "-af", "loudnorm=I=-14:TP=-1.2:LRA=7:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    import json

    j = json.loads(out[out.rindex("{") : out.rindex("}") + 1])
    ln = (
        f"loudnorm=I=-14:TP=-1.2:LRA=7:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
        f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true"
    )
    ff("-i", vo, "-vn", "-af", ln, "-ar", "48000", "-ac", "2", os.path.join(A, "audio", "vo.wav"))
    ff("-i", os.path.join(SRC, "audio", "bg_music.mp3"), "-ar", "48000", "-ac", "2", os.path.join(A, "audio", "music.wav"))


# ---------------------------------------------------------------- synthesised SFX (seeded, deterministic)
SR = 48000
rng = np.random.default_rng(7)


def save(name, x):
    x = np.asarray(x, np.float32)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.9
    p = os.path.join(A, "sfx", name)
    raw = p + ".raw"
    np.stack([x, x], 1).astype(np.float32).tofile(raw)
    ff("-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", raw, p)
    os.remove(raw)


def bandnoise(n, lo, hi):
    X = np.fft.rfft(rng.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, n)


def reverb(x, secs=1.6, mix=0.35):
    n = int(secs * SR)
    ir = rng.standard_normal(n) * np.exp(-np.linspace(0, 7, n))
    wet = np.convolve(x, ir)[: len(x) + n]
    wet = np.r_[wet, np.zeros(len(x) + n - len(wet))]
    dry = np.r_[x, np.zeros(n)]
    return dry * (1 - mix) + wet / (np.max(np.abs(wet)) + 1e-9) * np.max(np.abs(x)) * mix


def sfx():
    t = lambda s: np.arange(int(s * SR)) / SR
    # paper: a page sliding / settling on a desk
    n = int(0.9 * SR)
    env = np.exp(-((t(0.9) - 0.18) ** 2) / 0.004) + 0.5 * np.exp(-((t(0.9) - 0.45) ** 2) / 0.01)
    save("paper.wav", bandnoise(n, 900, 9000) * env * (0.6 + 0.4 * np.abs(np.sin(t(0.9) * 90))))
    # marker: one felt-tip underline stroke
    n = int(0.55 * SR)
    env = np.minimum(1, t(0.55) / 0.03) * np.exp(-np.maximum(0, t(0.55) - 0.4) / 0.05)
    save("marker.wav", bandnoise(n, 1800, 7000) * env * (0.7 + 0.3 * np.sin(t(0.55) * 2 * np.pi * 38)))
    # pencil: one soft graphite underline stroke - quiet, papery, no squeak (replaces the marker)
    n = int(0.5 * SR)
    tt = t(0.5)
    env = np.minimum(1, tt / 0.06) * np.exp(-np.maximum(0, tt - 0.32) / 0.06)
    grain = 0.55 + 0.45 * np.abs(bandnoise(n, 20, 90)) / 0.02
    x = bandnoise(n, 1200, 4200) * env * np.clip(grain, 0, 1.4) + bandnoise(n, 250, 900) * env * 0.35
    save("pencil.wav", reverb(x, 0.25, 0.15)[:n])
    # pen writing: ~3.4s of short scratchy strokes
    n = int(3.4 * SR)
    x = np.zeros(n)
    pos = 0.05
    while pos < 3.2:
        d = rng.uniform(0.08, 0.22)
        a, b = int(pos * SR), int((pos + d) * SR)
        seg = bandnoise(b - a, 2500, 9000) * np.hanning(b - a) * rng.uniform(0.5, 1)
        x[a:b] += seg
        pos += d + rng.uniform(0.02, 0.12)
    save("pen_writing.wav", x)
    # heartbeat: lub-dub, low and soft
    n = int(1.2 * SR)
    x = np.zeros(n)
    for s0, amp in [(0.0, 1.0), (0.28, 0.7)]:
        tt = t(0.25)
        k = np.sin(2 * np.pi * (48 + 30 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 18) * amp
        a = int(s0 * SR)
        x[a : a + len(k)] += k
    save("heartbeat.wav", x)
    # distant siren: US wail heard from blocks away (band-limited, reverberant, fades in/out)
    d = 5.0
    tt = t(d)
    f = 900 + 450 * np.sin(2 * np.pi * tt / 2.6 - np.pi / 2)
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(ph) + 0.3 * np.sin(2 * ph)
    env = np.minimum(1, tt / 1.5) * np.minimum(1, (d - tt) / 1.5)
    save("siren_distant.wav", reverb(tone * env * 0.5 + bandnoise(len(tt), 200, 1200) * 0.05, 2.0, 0.6))
    # police radio: squelch burst + short tone
    tt = t(0.6)
    x = bandnoise(len(tt), 600, 3500) * np.exp(-tt * 9) * 0.8
    beep = np.sin(2 * np.pi * 1250 * tt) * ((tt > 0.08) & (tt < 0.22)) * 0.5
    save("radio_squelch.wav", x + beep)
    # low sub drop for the final cut to black
    tt = t(3.0)
    x = np.sin(2 * np.pi * (38 + 40 * np.exp(-tt * 3)) * tt) * np.exp(-tt * 1.4)
    x += bandnoise(len(tt), 30, 400) * np.exp(-tt * 6) * 0.4
    save("sub_drop.wav", x)


if __name__ == "__main__":
    for d in ["video", "img", "audio", "sfx"]:
        os.makedirs(os.path.join(A, d), exist_ok=True)
    video()
    images()
    audio()
    sfx()
    print("assets ready")
