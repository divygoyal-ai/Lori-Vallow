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


# v3 grade, matched to the producer's reference frame (the AI laptop shot): low-key, deep crushed
# blacks, warm lamp-coloured highlights, muted colour, no added grain. Every clip gets the same look;
# only its exposure (gamma) and saturation are solved per clip so it lands on the reference's
# brightness and colour density, whatever the source looked like.
CURVE = "curves=all='0/0 0.1/0.03 0.3/0.15 0.6/0.44 0.85/0.74 1/0.88'"
WARM = "colorbalance=rs=0.01:bs=-0.012:rm=0.012:bm=-0.02:rh=0.045:gh=0.012:bh=-0.05"
VIG = "vignette=angle=PI/4.4"
# (target mean luma, target mean saturation). Reference frame: luma 0.06-0.09, saturation 0.21.
TARGET = {
    "ai": (0.085, 0.27),  # AI shots: stay right on the reference
    "real": (0.105, 0.26),  # bodycam / interview / draft real footage (inside cards, over a dark backdrop)
    "photo": (0.2, 0.3),  # family photos / booking photo (shown on a polaroid print)
    "place": (0.10, 0.26),  # CC location photos, full frame
    "doc": (0.26, 0.18),  # court filing paper on the dark desk
    "bgblur": (0.04, 0.22),  # blurred backdrops behind cards
}


def _stats(args, vf):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", *args, "-vf", vf + ",scale=108:192,format=rgb24", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    a = np.frombuffer(raw, np.uint8).reshape(-1, 3) / 255
    mx, mn = a.max(1), a.min(1)
    return (a @ [0.2126, 0.7152, 0.0722]).mean(), np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0).mean()


def graded(args, pre, g):
    ty, ts = TARGET[g]
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
B03 = V("03_charles_locked_out.mp4")  # Chandler PD bodycam, Jan 31 2019
B05 = V("05_lori_interview.mp4")  # Chandler PD interview room, Jul 11 2019
CARD = "crop=1104:621:176:0,unsharp=3:3:0.3"  # full 16:9 bodycam frame at native res, minus the re-uploader's corner bug
WIDE = "unsharp=3:3:0.3"  # interview room, full 1280x720 frame
PORTRAIT = "scale=1080:1920:flags=lanczos"  # draft real footage, shown as a portrait card

# (source, t0, t1, filter, grade, rate) -> every clip is baked to exactly the length it plays for
CLIPS = {
    # AI shots: the producer's original generations (720x1280) ...
    "ai_garden_kids.mp4": (AIV("m3_tCrF.mp4"), 0.3, 3.72, UP, "ai", 1.0),
    "ai_boy_floor.mp4": (AIV("m6_Lw3h.mp4"), 0.0, 3.62, UP, "ai", 0.77),  # ends before he turns his head
    "ai_planet.mp4": (AIV("m5_EbgV.mp4"), 0.0, 4.8, UP, "ai", 1.0),
    "ai_writer_desk.mp4": (AIV("m4_5jy8.mp4"), 0.0, 9.7, UP, "ai", 1.0),
    "ai_watching.mp4": (AIV("m2_ks9w.mp4"), 0.0, 2.6, UP, "ai", 0.55),  # before the woman's face turns to camera
    "ai_family_court.mp4": (AIV("m1_s7Z4.mp4"), 0.0, 2.8, UP, "ai", 1.0),
    # ... and the four with no original, from the clean draft picture (1080x1920)
    "ai_house_back.mp4": (DRAFT, 141.9, 144.5, "null", "ai", 0.93),
    "ai_laptop.mp4": (DRAFT, 11.0, 12.0, "null", "ai", 0.69),
    "ai_calendar.mp4": (DRAFT, 64.8, 67.7, "null", "ai", 1.0),
    "ai_writing.mp4": (DRAFT, 126.9, 130.6, "null", "ai", 1.0),
    # real footage from the draft (already 9:16) -> portrait cards
    "real_charles_day.mp4": (DRAFT, 135.0, 136.0, PORTRAIT, "real", 0.45),
    "real_lori_car.mp4": (DRAFT, 42.1, 46.4, PORTRAIT, "real", 1.0),
    # Charles in his cap in the garage: real Chandler PD footage (screen-recorded; the crop drops the cursor)
    "real_charles_cap.mp4": (DRAFT, 113.0, 116.3, "crop=950:1689:0:115,scale=1080:1920:flags=lanczos", "real", 1.0),
    # Chandler PD bodycam, Jan 31 2019 -> 16:9 cards at native resolution
    "real_night_a.mp4": (B03, 39.5, 44.15, CARD, "real", 1.0),
    "real_night_b.mp4": (B03, 89.0, 91.2, CARD, "real", 1.0),
    "real_night_c.mp4": (B03, 631.5, 635.1, CARD, "real", 1.0),
    "real_to_door.mp4": (B03, 621.3, 624.4, CARD, "real", 1.0),
    "real_night_face.mp4": (B03, 638.0, 641.05, CARD, "real", 1.0),
    "real_bodycam_walk.mp4": (B03, 7.8, 12.2, CARD, "real", 1.0),
    "real_gate.mp4": (B03, 788.5, 790.7, CARD, "real", 1.0),
    "real_charles_close.mp4": (B03, 1019.8, 1022.5, CARD, "real", 1.0),
    "real_walkaway.mp4": (B03, 583.0, 587.6, CARD, "real", 1.0),
    # Chandler PD interview with Lori, Jul 11 2019 -> 16:9 cards
    "real_int_1.mp4": (B05, 1194.5, 1198.3, WIDE, "real", 1.0),
    "real_int_2.mp4": (B05, 799.5, 803.4, WIDE, "real", 1.0),
    "real_int_3.mp4": (B05, 1995.0, 1998.0, WIDE, "real", 1.0),
}
BG = "scale=-2:1920,crop=1080:1920"


def video():
    for out, (src, t0, t1, vf, g, rate) in CLIPS.items():
        mode = "blend" if src in (B03, B05) else "mci"
        clip(src, t0, t1, out, vf, g, rate, mode)
        if out.startswith("real_"):  # blurred, darkened full-frame backdrop behind every card
            clip(src, t0, t1, out.replace(".mp4", "_bg.mp4"), BG if vf != PORTRAIT and not vf.startswith("crop=950") else "scale=1080:1920",
                 "bgblur", rate, "blend")
    # freeze of Charles at the end of his daylight clip (the push carries on to his face)
    still(["-ss", "135.95", "-i", DRAFT], "charles_day_face.jpg", PORTRAIT, "real")


def images():
    im = os.path.join(SRC, "images")
    img = lambda out: os.path.join(A, "img", out)
    for n, out in [("div_p01.jpg", "doc_p01.jpg"), ("div_p03.jpg", "doc_p03.jpg"), ("div_p04.jpg", "doc_p04.jpg")]:
        src = os.path.join(im, n)
        ff("-i", src, "-vf", graded(["-i", src], "null", "doc"), "-q:v", "1", img(out))
    for n in ["chandler_aerial.jpg", "gilbert.jpg", "maricopa_court.jpg"]:
        src = os.path.join(im, n)
        ff("-i", src, "-vf", graded(["-i", src], "scale=-2:2200:flags=lanczos", "place"), "-q:v", "1", img(n))
    # AI: the family on the couch, Charles bald and heavyset, everyone from behind (producer's image)
    src = os.path.join(AIDIR, "chatgpt_img.png")
    ff("-i", src, "-vf", graded(["-i", src], "scale=1080:1920:flags=lanczos,unsharp=5:5:0.4", "ai"), "-q:v", "1", img("ai_family_tv.jpg"))
    # real photos -> polaroids (cropped to the print's 648:820 aspect) + blurred backdrops
    photos = {
        "lori_booking.jpg": (["-i", os.path.join(im, "mug_lori_kauai.jpg")], "crop=440:557:172:4,scale=648:820:flags=lanczos"),
        "photo_wedding.jpg": (["-ss", "138.3", "-i", DRAFT], "crop=1080:1367:0:250"),
        "photo_charles_baby.jpg": (["-ss", "134.2", "-i", DRAFT], "crop=830:1050:250:185"),  # baby kept out of frame
        "photo_charles.jpg": (["-ss", "133.2", "-i", DRAFT], "crop=1080:1367:0:150"),
    }
    for out, (args, crop) in photos.items():
        still(args, out, crop, "photo")
        still(args, out.replace(".jpg", "_bg.jpg"), f"{crop},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920", "bgblur")


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
