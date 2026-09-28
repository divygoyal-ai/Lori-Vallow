#!/usr/bin/env python3
"""Generates index.html - the HyperFrames composition for Lori Vallow, Episode 1.

The shot list below is the edit. Every time is in seconds on the voiceover's clock
(assets/audio/vo.wav starts at 0). Word timings come from a Whisper word-level
transcript of the final VO, so every cut, highlight and SFX lands on the word.

Rules this edit follows (see docs/STYLE_GUIDE.md section 0):
  - no minor's face anywhere (AI kids shots are from behind only)
  - real people's faces appear only in real, government-released footage/photos
  - AI shots of Charles are always the same heavyset man from behind
  - one dark, low-key true-crime grade (baked in prep), matched to the producer's reference frame
  - real footage is never blown up: 16:9 bodycam/interview sits on cards at native resolution
  - producer's music bed kept well under the VO; SFX sparse and motivated
  - no captions (added later)
"""
import json
import os

W, H = 1080, 1920
DUR = 155.0

# ------------------------------------------------------------------ the edit
# Grading is baked into every asset by prep/prep_assets.py (one look for the whole episode, matched to
# the producer's reference frame). Every clip is also pre-cut to exactly the length it plays for, so
# media always starts at 0 and plays at rate 1.
#
# kind:
#   video / image  full-frame shot            kb = (scale_from, scale_to, x_from%, x_to%), origin = push target
#   card           real 16:9 footage on a card over a blurred copy of itself (native resolution, never blown up)
#   pcard          real 9:16 footage on a portrait card (optional freeze-frame `still` after `dv` seconds)
#   polaroid       real photo print over a blurred copy
#   doc            the court filing, with a camera path and highlights
# ai = "REENACTMENT" (AI stand-in for a real moment) or "ILLUSTRATION" (symbolic AI image)
FACE = "50% 22%"  # push-ins on Charles travel toward his head, not his hands
BODYCAM_JAN = ("BODYCAM", "CHANDLER POLICE · JAN 31, 2019")
INTERVIEW = ("POLICE INTERVIEW", "CHANDLER POLICE · JUL 11, 2019")
FILING = ("COURT FILING", "MARICOPA COUNTY · FEB 2019")
SHOTS = [
    # --- cold open: meet Charles (real bodycam; the push carries on through a freeze to his face)
    dict(id="s01", kind="pcard", t=0.00, d=4.55, src="real_charles_day.mp4", dv=2.22, still="charles_day_face.jpg",
         kb=(1.0, 1.22, 0, 0), origin="42% 14%", tag=("BODYCAM", "CHANDLER POLICE · 2019")),
    dict(id="s02", kind="image", t=4.55, d=3.60, src="chandler_aerial.jpg", kb=(1.18, 1.3, -6, 6)),
    dict(id="s03", kind="video", t=8.15, d=2.80, src="ai_house_back.mp4", kb=(1.0, 1.07, 0, 0), ai="REENACTMENT"),
    dict(id="s04", kind="video", t=10.95, d=1.45, src="ai_laptop.mp4", kb=(1.05, 1.1, 0, 0), ai="REENACTMENT"),
    dict(id="s05", kind="image", t=12.40, d=2.50, src="ai_family_tv.jpg", kb=(1.0, 1.08, 0, 0), origin="30% 40%", ai="REENACTMENT"),
    # --- Lori (real) and the kids (never faces)
    dict(id="s06", kind="polaroid", t=14.90, d=2.08, src="photo_wedding.jpg", label="CHARLES & LORI", tag=("FAMILY PHOTO", "VALLOW FAMILY")),
    dict(id="s07", kind="video", t=16.98, d=3.42, src="ai_garden_kids.mp4", kb=(1.0, 1.06, 0, 0), ai="REENACTMENT"),
    dict(id="s08", kind="video", t=20.40, d=4.70, src="ai_boy_floor.mp4", kb=(1.0, 1.08, 0, 0), ai="REENACTMENT"),
    dict(id="s09", kind="polaroid", t=25.10, d=3.40, src="photo_charles_baby.jpg", label="CHARLES VALLOW", tag=("FAMILY PHOTO", "VALLOW FAMILY")),
    dict(id="s10", kind="image", t=28.50, d=3.45, src="gilbert.jpg", kb=(1.12, 1.2, 4, -4)),
    # --- the turn: Charles is terrified (real bodycam, Jan 31 2019)
    dict(id="s11", kind="card", t=31.95, d=4.65, src="real_night_a.mp4", kb=(1.0, 1.14, 0, 0), origin="48% 30%", tag=BODYCAM_JAN),
    dict(id="s12", kind="pcard", t=36.60, d=4.30, src="real_lori_car.mp4", kb=(1.0, 1.1, 0, 0), origin="55% 25%",
         tag=("BODYCAM", "ARIZONA POLICE · 2019")),
    dict(id="s13", kind="card", t=40.90, d=3.80, src="real_int_1.mp4", kb=(1.0, 1.25, 0, 0), origin="27% 55%", tag=INTERVIEW),
    dict(id="s14", kind="polaroid", t=44.70, d=4.20, src="lori_booking.jpg", label="LORI VALLOW", tag=("BOOKING PHOTO", "KAUAI POLICE · 2020")),
    # --- in her own words: the real divorce filing, page 4
    dict(id="s15", kind="doc", t=48.90, d=11.20, src="doc_p04.jpg", tag=FILING,
         cam=[(0.0, 722, 935, 0.7), (1.2, 952, 685, 1.6), (3.0, 952, 685, 1.6), (3.7, 500, 410, 1.6),
              (7.4, 500, 410, 1.6), (8.2, 900, 410, 1.6)],
         hl=[(1.45, 868, 664, 176, 42), (4.85, 262, 392, 490, 40), (8.95, 958, 390, 214, 42)]),
    dict(id="s16", kind="video", t=60.10, d=4.80, src="ai_planet.mp4", kb=(1.0, 1.1, 0, 0), ai="ILLUSTRATION"),
    dict(id="s17", kind="video", t=64.90, d=2.90, src="ai_calendar.mp4", kb=(1.0, 1.08, 0, 0), ai="ILLUSTRATION"),
    dict(id="s18a", kind="doc", t=67.80, d=2.50, src="doc_p03.jpg", tag=FILING,
         cam=[(0.0, 560, 890, 1.45), (2.5, 570, 890, 1.52)],
         hl=[(0.9, 270, 901, 250, 40)]),
    dict(id="s18b", kind="doc", t=70.30, d=3.10, src="doc_p04.jpg", tag=FILING,
         cam=[(0.0, 600, 1070, 1.3), (3.1, 610, 1070, 1.38)],
         hl=[(0.75, 312, 1052, 572, 42)]),
    dict(id="s19", kind="card", t=73.40, d=3.90, src="real_int_2.mp4", kb=(1.05, 1.3, 0, 0), origin="27% 55%", tag=INTERVIEW),
    # --- "he is not Charles anymore"
    dict(id="s20", kind="card", t=77.30, d=3.60, src="real_night_c.mp4", kb=(1.0, 1.15, 0, 0), origin="49% 25%", tag=BODYCAM_JAN),
    dict(id="s21", kind="pcard", t=80.90, d=3.30, src="real_charles_cap.mp4", kb=(1.0, 1.08, 0, 0), origin="40% 20%",
         tag=("BODYCAM", "CHANDLER POLICE · 2019")),
    dict(id="s22", kind="card", t=84.20, d=3.10, src="real_to_door.mp4", kb=(1.0, 1.12, 0, 0), origin="57% 30%", tag=BODYCAM_JAN),
    dict(id="s23", kind="card", t=87.30, d=3.05, src="real_night_face.mp4", kb=(1.05, 1.45, 0, 0), origin="72% 40%", tag=BODYCAM_JAN),
    dict(id="s24", kind="doc", t=90.35, d=4.55, src="doc_p04.jpg", tag=FILING,
         cam=[(0.0, 770, 900, 1.0), (4.55, 770, 905, 1.08)],
         hl=[(2.0, 1201, 829, 76, 40), (2.15, 264, 889, 134, 40), (2.75, 851, 940, 424, 40), (2.95, 266, 999, 98, 40)]),
    # --- the writer from out of state (Chad - never seen)
    dict(id="s25", kind="video", t=94.90, d=9.70, src="ai_writer_desk.mp4", kb=(1.0, 1.12, 0, 0), ai="REENACTMENT"),
    dict(id="s26", kind="card", t=104.60, d=3.00, src="real_int_3.mp4", kb=(1.2, 1.4, 0, 0), origin="27% 55%", tag=INTERVIEW),
    # --- Charles acts
    dict(id="s27", kind="video", t=107.60, d=4.70, src="ai_watching.mp4", kb=(1.0, 1.07, 0, 0), origin="30% 30%", ai="REENACTMENT"),
    dict(id="s28", kind="card", t=112.30, d=4.40, src="real_bodycam_walk.mp4", kb=(1.0, 1.08, 0, 0), origin="41% 40%", tag=BODYCAM_JAN),
    dict(id="s29", kind="video", t=116.70, d=2.80, src="ai_family_court.mp4", kb=(1.0, 1.06, 0, 0), ai="REENACTMENT"),
    dict(id="s30", kind="doc", t=119.50, d=3.10, src="doc_p01.jpg", tag=("COURT FILING", "MARICOPA COUNTY SUPERIOR COURT"),
         cam=[(0.0, 560, 820, 1.2), (3.1, 580, 830, 1.3)],
         hl=[(0.8, 266, 722, 272, 36), (1.8, 266, 887, 244, 36)]),
    dict(id="s31", kind="video", t=122.60, d=3.70, src="ai_writing.mp4", kb=(1.0, 1.08, 0, 0), ai="REENACTMENT"),
    # --- the threat, in the court record
    dict(id="s32", kind="doc", t=126.30, d=5.70, src="doc_p04.jpg", tag=FILING,
         cam=[(0.0, 780, 990, 1.05), (5.7, 775, 995, 1.09)],
         hl=[(0.3, 800, 993, 478, 40), (2.2, 756, 940, 520, 40), (2.45, 266, 999, 98, 40)]),
    dict(id="s33", kind="card", t=132.00, d=2.20, src="real_gate.mp4", kb=(1.0, 1.06, 0, 0), origin="71% 40%", tag=BODYCAM_JAN),
    dict(id="s34", kind="card", t=134.20, d=2.20, src="real_night_b.mp4", kb=(1.0, 1.1, 0, 0), origin="49% 25%", tag=BODYCAM_JAN),
    dict(id="s35", kind="image", t=136.40, d=4.50, src="maricopa_court.jpg", kb=(1.1, 1.2, -5, 5),
         loc=("MARICOPA COUNTY SUPERIOR COURT", "PHOENIX, ARIZONA")),
    dict(id="s36", kind="polaroid", t=140.90, d=2.20, src="photo_charles.jpg", label="CHARLES VALLOW", tag=("FAMILY PHOTO", "VALLOW FAMILY")),
    dict(id="s37", kind="card", t=143.10, d=2.70, src="real_charles_close.mp4", kb=(1.0, 1.12, 0, 0), origin="18% 35%", tag=BODYCAM_JAN),
    dict(id="s38", kind="card", t=145.80, d=4.60, src="real_walkaway.mp4", kb=(1.06, 1.0, 0, 0), origin="25% 40%", veil=0.6, tag=BODYCAM_JAN),
]

CUT_TO_BLACK = 150.40
DOC_K = 1.7  # papers are laid out at 1.7x and only ever scaled down (upscaled layers tile badly in capture)
CARD = dict(x=40, y=640, w=1000, h=562)  # 16:9 card: 1104x621 source shown at 1000x562 (downscaled = sharp)
PCARD = dict(x=190, y=300, w=700, h=1244)  # 9:16 portrait card

# ------------------------------------------------------------------ audio
# (id, file, start, volume, media_start)
def hit(peak_time, peak_offset):  # start so the file's peak lands on peak_time
    return round(peak_time - peak_offset, 3)


# Loudness calibration. Integrated LUFS of each file (measured with ebur128) and the loudness each
# class of effect should sit at in the mix. The VO is -16 LUFS: impacts are felt, never on top of words.
SFX_LUFS = {"impact-bass-1.mp3": -6.5, "impact-bass-2.mp3": -4.5, "whoosh-cinematic.mp3": -14.1, "whoosh-short.mp3": -15.2,
            "glitch-3.mp3": -22.3, "heartbeat.wav": -17.9, "marker.wav": -10.0, "paper.wav": -14.8, "pen_writing.wav": -13.5,
            "radio_squelch.wav": -9.8, "siren_distant.wav": -8.6, "sub_drop.wav": -15.2}


MIX_LIFT = 2.0  # dB: VO is normalised to -14 LUFS; every SFX target rides up with it


def vol(f, target_lufs):
    return round(min(1.0, 10 ** ((target_lufs + MIX_LIFT - SFX_LUFS[f]) / 20)), 3)


def fx(aid, f, start, target):
    return (aid, f, start, vol(f, target), 0)


HIT, SOFT_HIT, KEY_HIT = -21, -24, -18.5
SFX = [
    fx("x_title", "impact-bass-1.mp3", hit(0.35, 0.10), HIT),
    fx("x_turn", "impact-bass-2.mp3", hit(31.95, 1.83), KEY_HIT),
    fx("x_lori", "impact-bass-1.mp3", hit(44.70, 0.10), SOFT_HIT),
    fx("x_paper1", "paper.wav", 48.85, -26),
    fx("x_mk1", "marker.wav", 48.90 + 1.45, -27),
    fx("x_mk2", "marker.wav", 48.90 + 4.85, -27),
    fx("x_mk3", "marker.wav", 48.90 + 8.95, -27),
    fx("x_planet", "impact-bass-2.mp3", hit(60.10, 1.83), SOFT_HIT),
    fx("x_paper2", "paper.wav", 67.75, -27),
    fx("x_mk4", "marker.wav", 67.80 + 0.9, -27),
    fx("x_mk5", "marker.wav", 70.30 + 0.75, -27),
    fx("x_notch", "impact-bass-1.mp3", hit(77.30, 0.10), HIT),
    fx("x_hb1", "heartbeat.wav", 85.10, -24),
    fx("x_hb2", "heartbeat.wav", 86.30, -25),
    fx("x_face", "impact-bass-2.mp3", hit(89.06, 1.83), SOFT_HIT),
    fx("x_paper3", "paper.wav", 90.30, -27),
    fx("x_mk6", "marker.wav", 90.35 + 2.0, -27),
    fx("x_mk7", "marker.wav", 90.35 + 2.75, -27),
    fx("x_siren", "siren_distant.wav", 111.95, -31),
    fx("x_radio", "radio_squelch.wav", 112.35, -26),
    fx("x_divorce", "impact-bass-1.mp3", hit(116.72, 0.10), SOFT_HIT),
    fx("x_paper4", "paper.wav", 119.45, -27),
    fx("x_kill", "impact-bass-2.mp3", hit(126.34, 1.83), KEY_HIT),
    fx("x_mk8", "marker.wav", 126.30 + 0.3, -27),
    fx("x_mk9", "marker.wav", 126.30 + 2.2, -27),
    fx("x_hb3", "heartbeat.wav", 132.15, -23),
    fx("x_hb4", "heartbeat.wav", 133.35, -24),
    fx("x_black", "impact-bass-2.mp3", hit(CUT_TO_BLACK, 1.83), -17),
    fx("x_sub", "sub_drop.wav", CUT_TO_BLACK, -21),
]

# music: producer's bed. Its first ~16s are ~15 dB quieter than the body, so the lane lifts the
# intro, then holds ~18-20 dB under the VO, breathes up in the two long pauses and carries the ending.
MUSIC_LANE = [
    (0.0, 0.0), (0.6, 1.0), (14.0, 1.0), (17.5, 0.139),
    (131.0, 0.139), (131.4, 0.214), (133.9, 0.214), (134.3, 0.139),
    (148.4, 0.139), (149.2, 0.252), (CUT_TO_BLACK, 0.252), (CUT_TO_BLACK + 0.1, 0.164), (DUR - 0.3, 0.0),
]


# ------------------------------------------------------------------ html
def tag_html(sid, t, d, label, sub):
    return (f'<div id="{sid}-tag" class="clip ovl" data-start="{t + 0.25:.2f}" data-duration="{max(0.3, d - 0.25):.2f}" data-track-index="6">'
            f'<div class="srctag"><span class="srctag-box">{label}</span><span class="srctag-sub">{sub}</span></div></div>')


def ai_html(sid, t, d, label):
    return (f'<div id="{sid}-re" class="clip ovl" data-start="{t:.2f}" data-duration="{d:.2f}" data-track-index="7">'
            f'<div class="reenact">{label}</div></div>')


def box(g):
    return f'left:{g["x"]}px;top:{g["y"]}px;width:{g["w"]}px;height:{g["h"]}px'


def build():
    body, js = [], []
    for i, s in enumerate(SHOTS):
        sid, t, d, k = s["id"], s["t"], s["d"], s["kind"]
        track = 1 if i % 2 == 0 else 2
        timing = f'data-start="{t:.2f}" data-duration="{d:.2f}"'
        if k in ("video", "image"):
            if k == "video":
                el = (f'<video id="{sid}" class="clip media" src="assets/video/{s["src"]}" {timing} data-media-start="0" '
                      f'data-track-index="{track}" muted playsinline></video>')
            else:
                el = f'<img id="{sid}" class="clip media" src="assets/img/{s["src"]}" {timing} data-track-index="{track}" alt="" />'
            body.append(f'<div id="{sid}-w" class="shotw">{el}</div>')
            kb, org = s["kb"], s.get("origin", "50% 50%")
            js.append(f'tl.fromTo("#{sid}-w", {{scale:{kb[0]}, xPercent:{kb[2]}, transformOrigin:"{org}"}}, '
                      f'{{scale:{kb[1]}, xPercent:{kb[3]}, duration:{d:.2f}, ease:"none"}}, {t:.2f});')
        elif k in ("card", "pcard"):
            g = CARD if k == "card" else PCARD
            bg = s["src"].replace(".mp4", "_bg.mp4")
            body.append(f'<div id="{sid}-bw" class="shotw"><video id="{sid}-bg" class="clip media" src="assets/video/{bg}" {timing} '
                        f'data-media-start="0" data-track-index="{track}" muted playsinline></video></div>')
            dv = s.get("dv", d)
            media = (f'<video id="{sid}-fg" class="clip cardmedia" src="assets/video/{s["src"]}" data-start="{t:.2f}" data-duration="{dv:.2f}" '
                     f'data-media-start="0" data-track-index="{track + 2}" muted playsinline></video>')
            if "still" in s:
                media += (f'<img id="{sid}-st" class="clip cardmedia" src="assets/img/{s["still"]}" data-start="{t + dv:.2f}" '
                          f'data-duration="{d - dv:.2f}" data-track-index="{track + 2}" alt="" />')
            body.append(f'<div class="cardclip" style="{box(g)}"><div id="{sid}-push" class="cardpush">{media}</div></div>')
            label, sub = s.get("tag", ("", ""))
            tag = (f'<div class="ctag" style="left:{g["x"] + 26}px;top:{g["y"] - 19}px">{label}</div>'
                   f'<div class="csub" style="left:{g["x"]}px;width:{g["w"]}px;top:{g["y"] + g["h"] + 22}px">{sub}</div>') if label else ""
            body.append(f'<div id="{sid}-frame" class="clip ovl" {timing} data-track-index="5">'
                        f'<div class="card-frame" style="{box(g)}"></div>{tag}</div>')
            kb, org = s["kb"], s.get("origin", "50% 50%")
            js.append(f'tl.fromTo("#{sid}-push", {{scale:{kb[0]}, transformOrigin:"{org}"}}, {{scale:{kb[1]}, duration:{d:.2f}, ease:"none"}}, {t:.2f});')
            js.append(f'tl.fromTo("#{sid}-bw", {{scale:1.0}}, {{scale:1.05, duration:{d:.2f}, ease:"none"}}, {t:.2f});')
            if label:
                js.append(f'tl.fromTo("#{sid}-frame .ctag, #{sid}-frame .csub", {{opacity:0, y:8}}, '
                          f'{{opacity:1, y:0, duration:0.3, ease:"power2.out"}}, {t + 0.2:.2f});')
        elif k == "polaroid":
            body.append(f'<div id="{sid}" class="clip scene" {timing} data-track-index="{track}">'
                        f'<img class="fill" src="assets/img/{s["src"].replace(".jpg", "_bg.jpg")}" alt="" />'
                        f'<div id="{sid}-card" class="polaroid"><img src="assets/img/{s["src"]}" alt="" />'
                        f'<div class="polaroid-label">{s["label"]}</div></div></div>')
            rot = -2 if i % 2 else 2
            js.append(f'tl.fromTo("#{sid}-card", {{scale:1.16, rotation:{rot * 2}, opacity:0}}, '
                      f'{{scale:1, rotation:{rot}, opacity:1, duration:0.28, ease:"power3.out"}}, {t:.2f});')
            js.append(f'tl.to("#{sid}-card", {{scale:1.05, duration:{d - 0.3:.2f}, ease:"none"}}, {t + 0.3:.2f});')
        elif k == "doc":
            uniq = f"{sid}_{s['src']}"
            if os.path.exists(f"assets/img/{uniq}"):
                os.remove(f"assets/img/{uniq}")
            os.link(f"assets/img/{s['src']}", f"assets/img/{uniq}")  # own file per shot: no shared-media dedupe
            K = DOC_K
            hls = "".join(
                f'<div id="{sid}-h{j}" class="hl" style="left:{x * K:.0f}px;top:{y * K:.0f}px;width:{w * K:.0f}px;height:{h * K:.0f}px"><div class="hl-u"></div></div>'
                for j, (_, x, y, w, h) in enumerate(s["hl"]))
            body.append(f'<div id="{sid}" class="clip scene docbg" {timing} data-track-index="{track}">'
                        f'<div id="{sid}-cam" class="doccam"><div class="paper">'
                        f'<img src="assets/img/{uniq}" alt="" />{hls}</div></div></div>')
            cam = s["cam"]

            def pos(cx, cy, sc):
                return f"x:{W / 2 - cx * sc:.1f}, y:{H / 2 - cy * sc:.1f}, scale:{sc / DOC_K:.4f}"

            js.append(f'tl.set("#{sid}-cam", {{{pos(*cam[0][1:])}}}, {t:.2f});')
            for (a, *pa), (b, *pb) in zip(cam, cam[1:]):
                if pa == pb:
                    continue
                ease = "none" if (abs(pa[2] - pb[2]) < 0.2 and abs(pa[0] - pb[0]) < 60) else "power2.inOut"
                js.append(f'tl.to("#{sid}-cam", {{{pos(*pb)}, duration:{b - a:.2f}, ease:"{ease}"}}, {t + a:.2f});')
            for j, (ht, *_rest) in enumerate(s["hl"]):
                js.append(f'tl.fromTo("#{sid}-h{j}", {{scaleX:0}}, {{scaleX:1, duration:0.42, ease:"power2.out"}}, {t + ht:.2f});')
        if "veil" in s:  # darken toward the end of the shot
            body.append(f'<div id="{sid}-veil" class="clip veil" {timing} data-track-index="4"></div>')
            js.append(f'tl.fromTo("#{sid}-veil", {{opacity:0}}, {{opacity:{s["veil"]}, duration:{d * 0.85:.2f}, ease:"power1.in"}}, {t + d * 0.15:.2f});')
        if s.get("ai"):
            body.append(ai_html(sid, t, d, s["ai"]))
        if s.get("tag") and k in ("doc", "polaroid"):
            body.append(tag_html(sid, t, d, *s["tag"]))
            js.append(f'tl.fromTo("#{sid}-tag .srctag", {{opacity:0, x:-14}}, {{opacity:1, x:0, duration:0.3, ease:"power2.out"}}, {t + 0.25:.2f});')
        if s.get("loc"):
            a, b = s["loc"]
            body.append(f'<div id="{sid}-loc" class="clip ovl" data-start="{t + 0.3:.2f}" data-duration="{d - 0.5:.2f}" data-track-index="6">'
                        f'<div class="loc"><div class="loc-kick"><span class="dot"></span>{b}</div><div class="loc-main">{a}</div></div></div>')
            js.append(f'tl.fromTo("#{sid}-loc .loc", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:0.35, ease:"power2.out"}}, {t + 0.3:.2f});')
    return body, js


def main():
    body, js = build()
    audio = [
        f'<audio id="vo" src="assets/audio/vo.wav" data-start="0" data-duration="{DUR - 0.2}" data-track-index="20" data-volume="1"></audio>',
        '<audio id="music" src="assets/audio/music.wav" data-start="0" data-duration="%.2f" data-track-index="21" data-volume="1" '
        "data-automation='%s'></audio>"
        % (DUR, json.dumps({"version": 1, "lanes": [{"target": "volume", "points": [{"t": a, "v": b} for a, b in MUSIC_LANE]}]},
                           separators=(",", ":"))),
    ]
    import subprocess
    for i, (aid, f, st, vol, ms) in enumerate(SFX):
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"assets/sfx/{f}"],
                                 capture_output=True, text=True).stdout)
        audio.append(f'<audio id="{aid}" src="assets/sfx/{f}" data-start="{max(0, st):.3f}" data-duration="{min(d, DUR - st):.3f}" '
                     f'data-track-index="{30 + i}" data-volume="{vol}"></audio>')

    title = f"""
<div id="title" class="clip ovl" data-start="0.30" data-duration="2.30" data-track-index="8">
  <div class="title-wrap">
    <div class="title-kick">LORI VALLOW · EPISODE 1</div>
    <div class="title-main">THE MAN WHO WAS <span class="red">AFRAID</span></div>
    <div class="title-rule"></div>
  </div>
</div>
<div id="namesuper" class="clip ovl" data-start="1.10" data-duration="3.35" data-track-index="9">
  <div class="name-wrap"><div class="name-main">CHARLES VALLOW</div><div class="name-sub">62 · SUBURBAN ARIZONA</div></div>
</div>
<div id="loc1" class="clip ovl" data-start="4.85" data-duration="3.20" data-track-index="9">
  <div class="loc"><div class="loc-kick"><span class="dot"></span>MARICOPA COUNTY</div><div class="loc-main">CHANDLER, ARIZONA</div></div>
</div>
<div id="endcard" class="clip scene endbg" data-start="{CUT_TO_BLACK:.2f}" data-duration="{DUR - CUT_TO_BLACK:.2f}" data-track-index="10">
  <div class="end-wrap">
    <div class="end-ep">EPISODE 2</div>
    <div class="end-follow">FOLLOW FOR WHAT HAPPENED NEXT</div>
    <div class="end-rule"></div>
    <div class="end-series">LORI VALLOW</div>
  </div>
</div>"""
    js_extra = f"""
tl.fromTo("#title .title-kick", {{opacity:0, scale:1.08}}, {{opacity:1, scale:1, duration:0.6, ease:"power2.out"}}, 0.30);
tl.fromTo("#title .title-main", {{opacity:0, scale:1.06, filter:"blur(8px)"}}, {{opacity:1, scale:1, filter:"blur(0px)", duration:0.35, ease:"power3.out"}}, 0.35);
tl.fromTo("#title .title-rule", {{scaleX:0}}, {{scaleX:1, duration:0.4, ease:"power2.out"}}, 0.6);
tl.to("#title .title-wrap", {{opacity:0, duration:0.3}}, 2.30);
tl.fromTo("#namesuper .name-wrap", {{opacity:0, y:16}}, {{opacity:1, y:0, duration:0.35, ease:"power2.out"}}, 1.10);
tl.to("#namesuper .name-wrap", {{opacity:0, duration:0.25}}, 4.20);
tl.fromTo("#loc1 .loc", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:0.35, ease:"power2.out"}}, 4.85);
tl.fromTo("#endcard .end-wrap", {{opacity:0}}, {{opacity:1, duration:0.45, ease:"power1.out"}}, {CUT_TO_BLACK + 0.45:.2f});
tl.fromTo("#endcard .end-rule", {{scaleX:0}}, {{scaleX:1, duration:0.4, ease:"power2.out"}}, {CUT_TO_BLACK + 0.7:.2f});
"""
    html = f"""<!doctype html>
<html lang="en" data-resolution="portrait">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width={W}, height={H}" />
<title>Lori Vallow · Episode 1 · The Man Who Was Afraid</title>
<script src="assets/gsap.min.js"></script>
<style>
@font-face {{ font-family: "Anton"; src: url("assets/fonts/anton-latin-400-normal.woff2") format("woff2"); font-weight: 400; }}
@font-face {{ font-family: "Oswald"; src: url("assets/fonts/oswald-latin-400-normal.woff2") format("woff2"); font-weight: 400; }}
@font-face {{ font-family: "Oswald"; src: url("assets/fonts/oswald-latin-500-normal.woff2") format("woff2"); font-weight: 500; }}
@font-face {{ font-family: "Oswald"; src: url("assets/fonts/oswald-latin-600-normal.woff2") format("woff2"); font-weight: 600; }}
:root {{ --red: #d0202a; --white: #ffffff; --grey: #cfc9bf; --ink: #0a0a0b; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: {W}px; height: {H}px; overflow: hidden; background: var(--ink); }}
#root {{ position: relative; width: 100%; height: 100%; overflow: hidden; background: var(--ink); font-family: "Oswald", sans-serif; }}
.shotw {{ position: absolute; inset: 0; overflow: hidden; }}
.media {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
.clip.scene {{ position: absolute; inset: 0; overflow: hidden; }}
.veil {{ position: absolute; inset: 0; background: #000; opacity: 0; }}
.clip.ovl {{ position: absolute; inset: 0; pointer-events: none; }}
.fill {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
.red {{ color: var(--red); }}
/* evidence cards: real footage at native resolution over a blurred, darkened copy of itself */
.cardclip {{ position: absolute; overflow: hidden; }}
.cardpush {{ position: absolute; inset: 0; }}
.cardmedia {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }}
.card-frame {{ position: absolute; border: 3px solid rgba(232,226,214,0.9); box-shadow: 0 30px 90px rgba(0,0,0,0.8), 0 0 0 1px rgba(0,0,0,0.6); }}
.ctag {{ position: absolute; background: var(--red); color: var(--white); font-weight: 600; font-size: 24px; letter-spacing: 0.18em;
  padding: 5px 13px 5px 15px; line-height: 1.2; }}
.csub {{ position: absolute; text-align: center; color: var(--grey); font-weight: 500; font-size: 22px; letter-spacing: 0.18em;
  text-shadow: 0 2px 8px rgba(0,0,0,0.9); }}
/* source tag, top-left */
.srctag {{ position: absolute; left: 64px; top: 170px; display: flex; flex-direction: column; align-items: flex-start; gap: 12px; }}
.srctag-box {{ background: var(--red); color: var(--white); font-weight: 600; font-size: 26px; letter-spacing: 0.2em; padding: 6px 14px 6px 16px; }}
.srctag-sub {{ color: var(--grey); font-weight: 500; font-size: 24px; letter-spacing: 0.16em; text-shadow: 0 2px 8px rgba(0,0,0,0.8); }}
/* reenactment tag, top-right */
.reenact {{ position: absolute; right: 60px; top: 174px; color: rgba(255,255,255,0.8); font-weight: 500; font-size: 19px; letter-spacing: 0.26em;
  border: 1.5px solid rgba(255,255,255,0.55); padding: 5px 10px 5px 13px; }}
/* title */
.title-wrap {{ position: absolute; left: 0; right: 0; top: 440px; display: flex; flex-direction: column; align-items: center; gap: 18px; }}
.title-kick {{ color: rgba(255,255,255,0.78); font-weight: 500; font-size: 28px; letter-spacing: 0.34em; text-shadow: 0 2px 10px rgba(0,0,0,0.8); }}
.title-main {{ font-family: "Anton", sans-serif; color: var(--white); font-size: 104px; line-height: 1.05; text-align: center; width: 900px;
  text-shadow: 0 6px 30px rgba(0,0,0,0.75); }}
.title-rule {{ width: 170px; height: 6px; background: var(--red); }}
/* name super */
.name-wrap {{ position: absolute; left: 0; right: 0; top: 1290px; display: flex; flex-direction: column; align-items: center; gap: 10px; }}
.name-main {{ font-family: "Anton", sans-serif; color: var(--white); font-size: 92px; text-shadow: 0 6px 26px rgba(0,0,0,0.8); }}
.name-sub {{ color: var(--white); background: var(--red); font-weight: 600; font-size: 28px; letter-spacing: 0.22em; padding: 4px 14px 4px 18px; }}
/* location card, top-center */
.loc {{ position: absolute; left: 0; right: 0; top: 190px; display: flex; flex-direction: column; align-items: center; gap: 12px; }}
.loc-kick {{ color: var(--grey); font-weight: 500; font-size: 24px; letter-spacing: 0.26em; display: flex; align-items: center; gap: 12px;
  text-shadow: 0 2px 8px rgba(0,0,0,0.9); }}
.dot {{ width: 12px; height: 12px; border-radius: 50%; background: var(--red); display: inline-block; }}
.loc-main {{ background: rgba(10,10,11,0.82); color: var(--white); font-weight: 600; font-size: 44px; letter-spacing: 0.08em;
  padding: 10px 26px; border-bottom: 5px solid var(--red); }}
/* polaroid */
.polaroid {{ position: absolute; left: 190px; top: 470px; width: 700px; padding: 26px 26px 110px; background: #efe9dc;
  box-shadow: 0 40px 90px rgba(0,0,0,0.75); }}
.polaroid img {{ display: block; width: 648px; height: 820px; object-fit: cover; }}
.polaroid-label {{ position: absolute; left: 0; right: 0; bottom: 30px; text-align: center; color: #2b2724; font-weight: 600; font-size: 34px;
  letter-spacing: 0.3em; }}
/* documents */
.docbg {{ background: radial-gradient(ellipse at 50% 45%, #2a2622 0%, #121110 60%, #070707 100%); }}
.doccam {{ position: absolute; left: 0; top: 0; width: {1445 * DOC_K:.0f}px; height: {1870 * DOC_K:.0f}px; transform-origin: 0 0; }}
.paper {{ position: absolute; left: 0; top: 0; width: {1445 * DOC_K:.0f}px; height: {1870 * DOC_K:.0f}px; box-shadow: 0 40px 120px rgba(0,0,0,0.85); }}
.paper img {{ display: block; width: {1445 * DOC_K:.0f}px; height: {1870 * DOC_K:.0f}px; }}
.hl {{ position: absolute; transform-origin: 0 50%; background: rgba(208,32,42,0.2); mix-blend-mode: multiply; }}
.hl-u {{ position: absolute; left: 0; right: 0; bottom: -6px; height: 11px; background: var(--red); }}
/* end card */
.endbg {{ background: #060607; }}
.end-wrap {{ position: absolute; left: 0; right: 0; top: 760px; display: flex; flex-direction: column; align-items: center; gap: 22px; }}
.end-ep {{ font-family: "Anton", sans-serif; color: var(--white); font-size: 120px; line-height: 1; }}
.end-follow {{ color: rgba(255,255,255,0.7); font-weight: 500; font-size: 28px; letter-spacing: 0.3em; }}
.end-rule {{ width: 120px; height: 5px; background: var(--red); margin: 14px 0; }}
.end-series {{ font-family: "Anton", sans-serif; color: var(--white); font-size: 72px; letter-spacing: 0.03em; }}
#fader {{ position: absolute; inset: 0; background: #000; opacity: 0; pointer-events: none; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
{chr(10).join(body)}
<div id="fader"></div>
{title}
{chr(10).join(audio)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{chr(10).join(js)}
// dip the last shot toward black before the hard cut
tl.fromTo("#fader", {{opacity:0}}, {{opacity:0.55, duration:{CUT_TO_BLACK - 148.4:.2f}, ease:"power1.in"}}, 148.4);
tl.set("#fader", {{opacity:0}}, {CUT_TO_BLACK});
{js_extra}
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
    open("index.html", "w").write(html)
    print("wrote index.html", len(SHOTS), "shots,", len(SFX), "sfx")


if __name__ == "__main__":
    main()
