#!/usr/bin/env python3
"""Prepare every media asset used by the Episode 1 HyperFrames composition.

Sources live in ../ep1_src (downloaded from the producer's Drive folder):
  audio/vo_main.mp3   final voiceover (its picture track is the clean, caption-free
                      draft, used only as the source of the AI shots)
  audio/bg_music.mp3  background music supplied by the producer
  videos/*.mp4        government-released bodycam / interview footage
  images/*.jpg        court filings, booking photo, CC location photos

Nothing here grades or edits for style: this only trims, crops to 9:16,
normalises formats and loudness, and synthesises the few SFX the bundled
HyperFrames library does not cover. All creative work is in index.html.
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


# Dark true-crime grade (a little brighter than the references), baked here so the HyperFrames render
# does not have to run per-clip WebGL grading in software. One shared look; each clip's gamma is solved
# so the graded clip lands on a target average brightness (references sit at 0.20-0.25; we aim a bit
# higher so nothing reads muddy).
# v2 grade, matched to the reference episodes (mean luma 0.20-0.25, true blacks at ~0.01-0.03,
# highlights rolled off around 0.8, muted but not washed-out colour, cool shadows, heavy vignette).
LOOK = ("eq=contrast=1.16:saturation=0.64,curves=all='0/0 0.07/0.012 0.5/0.46 0.85/0.79 1/0.88',"
        "colorbalance=rs=-0.04:gs=-0.01:bs=0.06:rh=0.03:bh=-0.03,vignette=angle=PI/3.9,noise=alls=4:allf=t+u")
DOCLOOK = ("eq=contrast=1.1:saturation=0.3,curves=all='0/0 0.1/0.03 0.5/0.44 1/0.82',"
           "colorbalance=rh=0.04:gh=0.02:bh=-0.03,vignette=angle=PI/3.8")
BGLOOK = "gblur=sigma=40,eq=saturation=0.5,vignette=angle=PI/3.2"
TARGET = {"base": 0.21, "ai": 0.2, "day": 0.22, "night": 0.19, "interview": 0.22, "photo": 0.25, "doc": 0.38, "bgblur": 0.08}


def look(g):
    return {"doc": DOCLOOK, "bgblur": BGLOOK}.get(g, LOOK)


def _mean(args, vf):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", *args, "-vf", vf + ",scale=108:192,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).mean() / 255


def solve_gamma(args, pre, g):
    lo, hi = 0.4, 3.5
    for _ in range(9):
        mid = (lo * hi) ** 0.5
        m = _mean(args, f"{pre},eq=gamma={mid:.3f},{look(g)}")
        lo, hi = (mid, hi) if m < TARGET[g] else (lo, mid)
    return (lo * hi) ** 0.5


def _levels(args, pre):
    # per-clip auto-levels: the source's darkest / brightest 1% become true black / near-white, so murky
    # bodycam and hazy AI footage get the same contrast as the references before the look is applied
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", *args, "-vf", pre + ",scale=108:192,format=gray", "-f", "rawvideo", "-"],
                         capture_output=True).stdout
    y = np.frombuffer(raw, np.uint8) / 255
    lo, hi = np.percentile(y, 1.0), np.percentile(y, 99.3)
    lo, hi = min(lo, 0.25), max(hi, lo + 0.25)
    return f"colorlevels=rimin={lo:.3f}:gimin={lo:.3f}:bimin={lo:.3f}:rimax={hi:.3f}:gimax={hi:.3f}:bimax={hi:.3f}"


def graded(args, pre, g):
    if g not in ("doc", "bgblur"):
        pre = f"{pre},{_levels(args, pre)}"
    return f"{pre},eq=gamma={solve_gamma(args, pre, g):.3f},{look(g)}"


ENC = ["-an", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-r", "30"]


def clip(src, t0, t1, out, vf="scale=1080:1920:flags=lanczos", g="ai"):
    if os.path.exists(os.path.join(A, "video", out)):
        return
    vf = graded(["-ss", f"{t0}", "-to", f"{t1}", "-i", src, "-r", "0.7"], vf, g)
    ff("-ss", f"{t0}", "-to", f"{t1}", "-i", src, "-vf", vf, *ENC, os.path.join(A, "video", out))


def still(src, t, out, vf="scale=1080:1920:flags=lanczos", g="base"):
    vf = graded(["-ss", f"{t}", "-i", src, "-frames:v", "1"], vf, g)
    ff("-ss", f"{t}", "-i", src, "-frames:v", "1", "-vf", vf, "-q:v", "2", os.path.join(A, "img", out))


def bodycam(x, w=405, y=0, h=720):
    # 16:9 720p bodycam -> 9:16 crop, upscaled, light sharpen to hold detail
    return f"crop={w}:{h}:{x}:{y},scale=1080:1920:flags=lanczos,unsharp=5:5:0.6"


# ---------------------------------------------------------------- AI shots (from the clean draft track)
AI_GRADE = {"ai_house_back.mp4": "day", "ai_calendar.mp4": "day"}
AI = {
    "ai_house_back.mp4": (141.9, 144.5),  # Charles (bald, heavyset) from behind, Arizona house, day
    "ai_laptop.mp4": (11.0, 12.0),  # Charles from behind at a desk
    "ai_garden_kids.mp4": (17.8, 22.35),  # teen girl + small boy from behind
    "ai_boy_floor.mp4": (23.1, 26.5),  # small boy from behind, playing
    "ai_planet.mp4": (61.2, 63.9),  # apocalyptic planet
    "ai_calendar.mp4": (64.6, 67.85),  # JULY 2020 calendar
    "ai_writer_desk.mp4": (95.8, 103.0),  # faceless man at desk (Chad - never shown)
    "ai_watching.mp4": (108.0, 111.9),  # Charles from behind watching across room
    "ai_cap_silhouette.mp4": (112.7, 117.0),  # man in a cap, pure silhouette (matches Charles's cap)
    "ai_family_court.mp4": (117.8, 125.35),  # Charles from behind, family court
    "ai_writing.mp4": (126.6, 131.1),  # hand writing "I will..."
}
# ---------------------------------------------------------------- real footage (government released)
B03 = V("03_charles_locked_out.mp4")  # Chandler PD bodycam, Jan 31 2019 (Charles locked out)
REAL = {
    "real_lori_car.mp4": (DRAFT, 41.9, 48.5, "scale=1080:1920:flags=lanczos", "base"),
    "real_charles_day.mp4": (DRAFT, 135.0, 136.0, "scale=1080:1920:flags=lanczos", "base"),
    "real_charles_night_a.mp4": (B03, 39.0, 45.0, bodycam(500), "night"),
    "real_charles_night_b.mp4": (B03, 89.0, 93.0, bodycam(520), "night"),
    "real_charles_night_c.mp4": (B03, 631.5, 635.2, bodycam(520), "night"),
    "real_charles_close.mp4": (B03, 1019.8, 1023.9, bodycam(175), "night"),  # big man walking in with officers, lit garage
    "real_charles_to_door.mp4": (B03, 620.5, 625.0, bodycam(600), "night"),  # silhouette walking to the door
    "real_street_walkaway.mp4": (B03, 582.0, 590.0, bodycam(250), "night"),  # figures walking off down the street
    "real_gate_flashlight.mp4": (B03, 788.0, 792.0, bodycam(760), "night"),
    "real_bodycam_walk.mp4": (B03, 7.5, 12.5, bodycam(430), "night"),
    # Chandler PD bodycam, 2019 (640x360): suburban street, used as a 16:9 inset card
    "real_chandler_street.mp4": (V("01_charles_shooting.mp4"), 9.2, 13.2, "crop=544:306:0:20,scale=1920:1080:flags=lanczos", "base"),
    # Chandler PD interview, 2019-07-11: tight 9:16 crops on Lori, and full 16:9 frames for inset cards
    "real_lori_int_a.mp4": (V("05_lori_interview.mp4"), 449.0, 454.0, bodycam(200, 300, 187, 533), "interview"),
    "real_lori_int_b.mp4": (V("05_lori_interview.mp4"), 1995.0, 2003.0, bodycam(200, 300, 187, 533), "interview"),
    "real_lori_int_wide.mp4": (V("05_lori_interview.mp4"), 799.0, 805.0, "scale=1920:1080:flags=lanczos", "interview"),
    "real_lori_int_wide_b.mp4": (V("05_lori_interview.mp4"), 1194.5, 1200.0, "scale=1920:1080:flags=lanczos", "interview"),
}


def video():
    for out, (t0, t1) in AI.items():
        clip(DRAFT, t0, t1, out, g=AI_GRADE.get(out, "ai"))
    for out, (src, t0, t1, vf, g) in REAL.items():
        clip(src, t0, t1, out, vf, g)
    # blurred full-frame backdrops for the 16:9 inset cards
    for n, (src, t0, t1) in {"real_lori_int_wide_bg.mp4": (V("05_lori_interview.mp4"), 799.0, 805.0),
                             "real_lori_int_wide_b_bg.mp4": (V("05_lori_interview.mp4"), 1194.5, 1200.0),
                             "real_chandler_street_bg.mp4": (V("01_charles_shooting.mp4"), 9.2, 13.2)}.items():
        clip(src, t0, t1, n, "scale=-2:1920,crop=1080:1920", "bgblur")
    still(DRAFT, 135.7, "charles_day_face.jpg")
    still(B03, 635.6, "charles_night_face.jpg", bodycam(520), "night")
    # detail insert from the toy corner of the boy shot (no child in frame)
    still(DRAFT, 24.2, "ai_toys_detail.jpg", "crop=480:853:600:1067,scale=1080:1920:flags=lanczos", "ai")


def images():
    im = os.path.join(SRC, "images")
    img = lambda out: os.path.join(A, "img", out)
    for n, out, g in [
        ("div_p01.jpg", "doc_p01.jpg", "doc"),
        ("div_p03.jpg", "doc_p03.jpg", "doc"),
        ("div_p04.jpg", "doc_p04.jpg", "doc"),
        ("mug_lori_kauai.jpg", "lori_booking.jpg", "photo"),
    ]:
        ff("-i", os.path.join(im, n), "-vf", graded(["-i", os.path.join(im, n)], "null", g), "-q:v", "2", img(out))
    # blurred backdrop behind the booking-photo polaroid
    src = os.path.join(im, "mug_lori_kauai.jpg")
    pre = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    ff("-i", src, "-vf", graded(["-i", src], pre, "bgblur"), "-q:v", "2", img("lori_booking_bg.jpg"))
    for n in ["chandler_aerial.jpg", "gilbert.jpg", "maricopa_court.jpg"]:
        src = os.path.join(im, n)
        ff("-i", src, "-vf", graded(["-i", src], "scale=-2:2200:flags=lanczos", "base"), "-q:v", "2", img(n))


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
