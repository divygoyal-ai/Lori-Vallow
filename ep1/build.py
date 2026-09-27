#!/usr/bin/env python3
"""Generates index.html - the HyperFrames composition for Lori Vallow, Episode 1.

The shot list below is the edit. Every time is in seconds on the voiceover's clock
(assets/audio/vo.wav starts at 0). Word timings come from a Whisper word-level
transcript of the final VO, so every cut, highlight and SFX lands on the word.

Rules this edit follows (see docs/STYLE_GUIDE.md section 0):
  - no minor's face anywhere (AI kids shots are from behind only)
  - real people's faces appear only in real, government-released footage/photos
  - AI shots of Charles are always the same heavyset man from behind
  - dark true-crime grade, a little brighter than the references
  - producer's music bed kept well under the VO; SFX sparse and motivated
  - no captions (added later)
"""
import json
import os

W, H = 1080, 1920
DUR = 155.0

# ------------------------------------------------------------------ grades (HyperFrames media treatment)
def grade(exp=-0.15, contrast=0.12, hi=-0.22, sh=0.06, blacks=-0.06, sat=-0.3, temp=-0.04,
          vig=0.42, grain=0.12, blur=None, cool=0.12):
    g = {
        "intensity": 1,
        "adjust": {"exposure": exp, "contrast": contrast, "highlights": hi, "shadows": sh,
                   "blacks": blacks, "saturation": sat, "temperature": temp},
        "wheels": {"shadows": {"hue": 200, "amount": cool, "level": 0},
                   "highlights": {"hue": 32, "amount": 0.05, "level": 0}},
        "details": {"vignette": vig, "vignetteFeather": 0.72, "grain": grain, "grainSize": 0.22,
                    "grainRoughness": 0.55},
    }
    if blur is not None:
        g["effects"] = {"blur": blur}
    return g


G = {
    "base": grade(),
    "day": grade(exp=-0.42, hi=-0.4, sat=-0.36, contrast=0.14, vig=0.5),  # bright AI daylight
    "ai": grade(exp=-0.08, sat=-0.26),
    "night": grade(exp=0.28, sh=0.22, hi=-0.1, sat=-0.32, grain=0.18, contrast=0.1, vig=0.38),
    "interview": grade(exp=-0.32, hi=-0.32, sat=-0.34, temp=-0.06, vig=0.45),
    "photo": grade(exp=-0.18, sat=-0.25),
    "doc": grade(exp=-0.3, hi=-0.35, sat=-0.6, temp=0.05, contrast=0.1, vig=0.55, grain=0.1, cool=0.04),
    "bgblur": grade(exp=-1.1, sat=-0.4, vig=0.6, blur=0.85, grain=0.08),
}

# ------------------------------------------------------------------ the edit
# kind: video | image | doc | inset | polaroid
# for video: src, media start (ms), rate; kb = (scale_from, scale_to, x_from%, x_to%)
SHOTS = [
    # --- cold open: meet Charles (real bodycam, then freeze on his face)
    dict(id="s01v", kind="video", t=0.00, d=2.22, src="real_charles_day.mp4", ms=0.0, rate=0.45, g="base", kb=(1.0, 1.05, 0, 0), grp="s01"),
    dict(id="s01i", kind="image", t=2.22, d=2.33, src="charles_day_face.jpg", g="base", kb=(1.05, 1.12, 0, 0), grp="s01"),
    dict(id="s02", kind="image", t=4.55, d=3.60, src="chandler_aerial.jpg", g="base", kb=(1.18, 1.3, -6, 6), fit="cover"),
    dict(id="s03", kind="video", t=8.15, d=2.80, src="ai_house_back.mp4", ms=0.0, rate=0.93, g="day", kb=(1.0, 1.07, 0, 0), ai=True),
    dict(id="s04", kind="video", t=10.95, d=1.45, src="ai_laptop.mp4", ms=0.0, rate=0.69, g="ai", kb=(1.05, 1.1, 0, 0), ai=True),
    dict(id="s05", kind="video", t=12.40, d=2.50, src="ai_family_tv.mp4", ms=0.0, rate=1.0, g="ai", kb=(1.0, 1.06, 0, 0), ai=True),
    # --- Lori (real) and the kids (never faces)
    dict(id="s06", kind="video", t=14.90, d=2.08, src="real_lori_car.mp4", ms=0.2, rate=1.0, g="base", kb=(1.0, 1.06, 0, 0),
         tag=("BODYCAM", "ARIZONA POLICE · 2019")),
    dict(id="s07", kind="video", t=16.98, d=3.42, src="ai_garden_kids.mp4", ms=0.3, rate=1.0, g="ai", kb=(1.0, 1.06, 0, 0), ai=True),
    dict(id="s08", kind="video", t=20.40, d=4.70, src="ai_boy_floor.mp4", ms=0.0, rate=0.72, g="ai", kb=(1.0, 1.08, 0, 0), ai=True),
    dict(id="s09", kind="video", t=25.10, d=3.40, src="ai_family_tv.mp4", ms=1.3, rate=0.74, g="ai", kb=(1.22, 1.32, 0, 0), ai=True),
    dict(id="s10", kind="image", t=28.50, d=3.45, src="gilbert.jpg", g="base", kb=(1.12, 1.2, 4, -4), fit="cover"),
    # --- the turn: Charles is terrified (real bodycam, Jan 31 2019)
    dict(id="s11", kind="video", t=31.95, d=4.65, src="real_charles_night_a.mp4", ms=0.5, rate=1.0, g="night", kb=(1.0, 1.06, 0, 0),
         tag=("BODYCAM", "CHANDLER POLICE · JAN 31, 2019")),
    dict(id="s12", kind="inset", t=36.60, d=4.30, src="real_lori_int_wide_b.mp4", ms=0.0, rate=1.0, g="interview",
         tag=("POLICE INTERVIEW", "CHANDLER POLICE · 2019")),
    dict(id="s13", kind="video", t=40.90, d=3.80, src="real_lori_int_a.mp4", ms=0.8, rate=1.0, g="interview", kb=(1.0, 1.1, 0, 0),
         tag=("POLICE INTERVIEW", "CHANDLER POLICE · 2019")),
    dict(id="s14", kind="polaroid", t=44.70, d=4.20, src="lori_booking.jpg", label="LORI VALLOW", g="photo",
         tag=("BOOKING PHOTO", "KAUAI POLICE · 2020")),
    # --- in her own words: the real divorce filing, page 4
    dict(id="s15", kind="doc", t=48.90, d=11.20, src="doc_p04.jpg", g="doc",
         tag=("COURT FILING", "MARICOPA COUNTY · FEB 2019"),
         cam=[(0.0, 722, 935, 0.7), (1.2, 952, 685, 1.6), (3.0, 952, 685, 1.6), (3.7, 500, 410, 1.6),
              (7.4, 500, 410, 1.6), (8.2, 900, 410, 1.6)],
         hl=[(1.45, 868, 664, 176, 42), (4.85, 262, 392, 490, 40), (8.95, 958, 390, 214, 42)]),
    dict(id="s16", kind="video", t=60.10, d=4.80, src="ai_planet.mp4", ms=0.0, rate=0.56, g="ai", kb=(1.0, 1.1, 0, 0), ai=True),
    dict(id="s17", kind="video", t=64.90, d=2.90, src="ai_calendar.mp4", ms=0.2, rate=1.0, g="day", kb=(1.0, 1.08, 0, 0), ai=True),
    dict(id="s18a", kind="doc", t=67.80, d=2.50, src="doc_p03.jpg", g="doc",
         tag=("COURT FILING", "MARICOPA COUNTY · FEB 2019"),
         cam=[(0.0, 560, 890, 1.45), (2.5, 570, 890, 1.52)],
         hl=[(0.9, 270, 901, 250, 40)]),
    dict(id="s18b", kind="doc", t=70.30, d=3.10, src="doc_p04.jpg", g="doc",
         tag=("COURT FILING", "MARICOPA COUNTY · FEB 2019"),
         cam=[(0.0, 600, 1070, 1.3), (3.1, 610, 1070, 1.38)],
         hl=[(0.75, 312, 1052, 572, 42)]),
    dict(id="s19", kind="inset", t=73.40, d=3.90, src="real_lori_int_wide.mp4", ms=0.5, rate=1.0, g="interview",
         tag=("POLICE INTERVIEW", "CHANDLER POLICE · 2019")),
    # --- "he is not Charles anymore"
    dict(id="s20", kind="video", t=77.30, d=3.60, src="real_charles_night_c.mp4", ms=0.8, rate=1.0, g="night", kb=(1.0, 1.08, 0, 0),
         tag=("BODYCAM", "CHANDLER POLICE · JAN 31, 2019")),
    dict(id="s21", kind="video", t=80.90, d=3.30, src="ai_house_back_b.mp4", ms=0.0, rate=0.73, g="day", kb=(1.08, 1.0, 0, 0), ai=True,
         veil=0.5),
    dict(id="s22", kind="image", t=84.20, d=3.10, src="ai_mirror_charles.jpg", g="ai", kb=(1.0, 1.14, 0, 0), ai=True),
    dict(id="s23", kind="image", t=87.30, d=3.05, src="charles_day_face.jpg", g="base", kb=(1.2, 1.34, 0, 0), veil=0.45),
    dict(id="s24", kind="doc", t=90.35, d=4.55, src="doc_p04.jpg", g="doc",
         tag=("COURT FILING", "MARICOPA COUNTY · FEB 2019"),
         cam=[(0.0, 770, 900, 1.0), (4.55, 770, 905, 1.08)],
         hl=[(2.0, 1201, 829, 76, 40), (2.15, 264, 889, 134, 40), (2.75, 851, 940, 424, 40), (2.95, 266, 999, 98, 40)]),
    # --- the writer from out of state (Chad - never seen)
    dict(id="s25", kind="video", t=94.90, d=9.70, src="ai_writer_desk.mp4", ms=0.0, rate=0.74, g="ai", kb=(1.0, 1.12, 0, 0), ai=True),
    dict(id="s26", kind="video", t=104.60, d=3.00, src="real_lori_int_b.mp4", ms=0.0, rate=1.0, g="interview", kb=(1.05, 1.14, 0, 0),
         tag=("POLICE INTERVIEW", "CHANDLER POLICE · 2019")),
    # --- Charles acts
    dict(id="s27", kind="video", t=107.60, d=4.70, src="ai_watching.mp4", ms=0.0, rate=0.83, g="ai", kb=(1.0, 1.07, 0, 0), ai=True),
    dict(id="s28", kind="video", t=112.30, d=4.40, src="real_bodycam_walk.mp4", ms=0.0, rate=0.5, g="night", kb=(1.0, 1.05, 0, 0),
         tag=("BODYCAM", "CHANDLER POLICE · JAN 31, 2019")),
    dict(id="s29", kind="video", t=116.70, d=2.80, src="ai_family_court.mp4", ms=0.0, rate=1.0, g="ai", kb=(1.0, 1.06, 0, 0), ai=True),
    dict(id="s30", kind="doc", t=119.50, d=3.10, src="doc_p01.jpg", g="doc",
         tag=("COURT FILING", "MARICOPA COUNTY SUPERIOR COURT"),
         cam=[(0.0, 560, 820, 1.2), (3.1, 580, 830, 1.3)],
         hl=[(0.8, 266, 722, 272, 36), (1.8, 266, 887, 244, 36)]),
    dict(id="s31", kind="video", t=122.60, d=3.70, src="ai_writing.mp4", ms=0.3, rate=1.0, g="ai", kb=(1.0, 1.08, 0, 0), ai=True),
    # --- the threat, in the court record
    dict(id="s32", kind="doc", t=126.30, d=5.70, src="doc_p04.jpg", g="doc",
         tag=("COURT FILING", "MARICOPA COUNTY · FEB 2019"),
         cam=[(0.0, 780, 990, 1.05), (5.7, 775, 995, 1.09)],
         hl=[(0.3, 800, 993, 478, 40), (2.2, 756, 940, 520, 40), (2.45, 266, 999, 98, 40)]),
    dict(id="s33", kind="image", t=132.00, d=2.20, src="charles_night_face.jpg", g="night", kb=(1.05, 1.12, 0, 0), veil=0.35),
    dict(id="s34", kind="video", t=134.20, d=2.20, src="real_charles_night_b.mp4", ms=0.0, rate=1.0, g="night", kb=(1.0, 1.05, 0, 0),
         tag=("BODYCAM", "CHANDLER POLICE · JAN 31, 2019")),
    dict(id="s35", kind="image", t=136.40, d=4.50, src="maricopa_court.jpg", g="base", kb=(1.1, 1.2, -5, 5), fit="cover",
         loc=("MARICOPA COUNTY SUPERIOR COURT", "PHOENIX, ARIZONA")),
    dict(id="s36", kind="image", t=140.90, d=4.90, src="charles_day_face.jpg", g="base", kb=(1.12, 1.24, 0, 0),
         tag=("BODYCAM", "ARIZONA POLICE · 2019")),
    dict(id="s37", kind="video", t=145.80, d=4.60, src="ai_house_back.mp4", ms=0.0, rate=0.56, g="day", kb=(1.14, 1.0, 0, 0), ai=True,
         veil=0.6),
]

CUT_TO_BLACK = 150.40
DOC_K = 1.7  # papers are laid out at 1.7x and only ever scaled down (upscaled layers tile badly in capture)

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
    fx("x_wh1", "whoosh-short.mp3", hit(4.55, 0.16), -25),
    fx("x_turn", "impact-bass-2.mp3", hit(31.95, 1.83), KEY_HIT),
    fx("x_lori", "impact-bass-1.mp3", hit(44.70, 0.10), SOFT_HIT),
    fx("x_paper1", "paper.wav", 48.85, -26),
    fx("x_mk1", "marker.wav", 48.90 + 1.45, -27),
    fx("x_mk2", "marker.wav", 48.90 + 4.85, -27),
    fx("x_mk3", "marker.wav", 48.90 + 8.95, -27),
    fx("x_end", "whoosh-cinematic.mp3", hit(60.10, 2.91), -23),
    fx("x_wh2", "whoosh-short.mp3", hit(64.90, 0.16), -26),
    fx("x_paper2", "paper.wav", 67.75, -27),
    fx("x_mk4", "marker.wav", 67.80 + 0.9, -27),
    fx("x_mk5", "marker.wav", 70.30 + 0.75, -27),
    fx("x_swell", "whoosh-cinematic.mp3", hit(77.30, 2.91), -24),
    fx("x_notch", "impact-bass-1.mp3", hit(77.30, 0.10), HIT),
    fx("x_glitch", "glitch-3.mp3", 84.25, -28),
    fx("x_hb1", "heartbeat.wav", 85.10, -24),
    fx("x_hb2", "heartbeat.wav", 86.30, -25),
    fx("x_face", "impact-bass-2.mp3", hit(89.06, 1.83), SOFT_HIT),
    fx("x_paper3", "paper.wav", 90.30, -27),
    fx("x_mk6", "marker.wav", 90.35 + 2.0, -27),
    fx("x_mk7", "marker.wav", 90.35 + 2.75, -27),
    fx("x_wh3", "whoosh-short.mp3", hit(94.90, 0.16), -26),
    fx("x_siren", "siren_distant.wav", 111.95, -31),
    fx("x_radio", "radio_squelch.wav", 112.35, -26),
    fx("x_divorce", "impact-bass-1.mp3", hit(116.72, 0.10), SOFT_HIT),
    fx("x_paper4", "paper.wav", 119.45, -27),
    fx("x_pen", "pen_writing.wav", 122.70, -28),
    fx("x_kill", "impact-bass-2.mp3", hit(126.34, 1.83), KEY_HIT),
    fx("x_mk8", "marker.wav", 126.30 + 0.3, -27),
    fx("x_mk9", "marker.wav", 126.30 + 2.2, -27),
    fx("x_hb3", "heartbeat.wav", 132.15, -23),
    fx("x_hb4", "heartbeat.wav", 133.35, -24),
    fx("x_wh4", "whoosh-short.mp3", hit(136.40, 0.16), -26),
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
def gattr(k):
    return json.dumps(G[k], separators=(",", ":"))


def tag_html(sid, t, d, label, sub):
    return (f'<div id="{sid}-tag" class="clip ovl" data-start="{t + 0.25:.2f}" data-duration="{max(0.3, d - 0.25):.2f}" data-track-index="6">'
            f'<div class="srctag"><span class="srctag-box">{label}</span><span class="srctag-sub">{sub}</span></div></div>')


def reenact_html(sid, t, d):
    return (f'<div id="{sid}-re" class="clip ovl" data-start="{t:.2f}" data-duration="{d:.2f}" data-track-index="7">'
            f'<div class="reenact">REENACTMENT</div></div>')


def build():
    body, js, veils = [], [], []
    groups = {}
    for s in SHOTS:
        sid, t, d = s["id"], s["t"], s["d"]
        k = s["kind"]
        track = 1 if SHOTS.index(s) % 2 == 0 else 2
        if k in ("video", "image"):
            grp = s.get("grp", sid)
            if grp not in groups:
                groups[grp] = []
                body.append(f'<div id="{grp}-w" class="shotw">')
                body.append(f"<!--{grp}-->")
            style = ""
            if k == "video":
                el = (f'<video id="{sid}" class="clip media" src="assets/video/{s["src"]}" data-start="{t:.2f}" '
                      f'data-duration="{d:.2f}" data-media-start="{s["ms"]}" data-playback-rate="{s["rate"]}" '
                      f"data-track-index=\"{track}\" {style} muted playsinline></video>")
            else:
                el = (f'<img id="{sid}" class="clip media" src="assets/img/{s["src"]}" data-start="{t:.2f}" data-duration="{d:.2f}" '
                      f"data-track-index=\"{track}\" {style} alt=\"\" />")
            groups[grp].append(el)
            idx = body.index(f"<!--{grp}-->")
            body.insert(idx, el)
            if grp == sid or s is SHOTS[[x["id"] for x in SHOTS].index(sid)]:
                pass
            kb = s["kb"]
            gt = min(x["t"] for x in SHOTS if x.get("grp", x["id"]) == grp)
            gd = max(x["t"] + x["d"] for x in SHOTS if x.get("grp", x["id"]) == grp) - gt
            if grp == sid or sid == [x["id"] for x in SHOTS if x.get("grp") == grp][0]:
                js.append(f'tl.fromTo("#{grp}-w", {{scale:{kb[0]}, xPercent:{kb[2]}}}, '
                          f'{{scale:{kb[1]}, xPercent:{kb[3]}, duration:{gd:.2f}, ease:"none"}}, {gt:.2f});')
            if "veil" in s:
                # darken toward the end of the shot: a timed black veil just above this shot
                veils.append(f'<div id="{sid}-veil" class="clip veil" data-start="{t:.2f}" data-duration="{d:.2f}" data-track-index="4"></div>')
                js.append(f'tl.fromTo("#{sid}-veil", {{opacity:0}}, {{opacity:{s["veil"]}, duration:{d * 0.85:.2f}, ease:"power1.in"}}, {t + d * 0.15:.2f});')
        elif k == "inset":
            body.append(f'<div id="{sid}-w" class="shotw">'
                        f'<video id="{sid}-bg" class="clip media" src="assets/video/{s["src"].replace(".mp4", "_bg.mp4")}" data-start="{t:.2f}" data-duration="{d:.2f}" '
                        f'data-media-start="{s["ms"]}" data-track-index="{track}" muted playsinline></video>'
                        f'<video id="{sid}-fg" class="clip inset-media" src="assets/video/{s["src"]}" data-start="{t:.2f}" data-duration="{d:.2f}" '
                        f'data-media-start="{s["ms"]}" data-track-index="{track + 2}" muted playsinline></video>'
                        f"</div>")
            body.append(f'<div id="{sid}-frame" class="clip ovl" data-start="{t:.2f}" data-duration="{d:.2f}" data-track-index="5">'
                        f'<div class="inset-frame"></div></div>')
            js.append(f'tl.fromTo("#{sid}-w", {{scale:1.0}}, {{scale:1.04, duration:{d:.2f}, ease:"none"}}, {t:.2f});')
        elif k == "polaroid":
            body.append(f'<div id="{sid}" class="clip scene" data-start="{t:.2f}" data-duration="{d:.2f}" data-track-index="{track}">'
                        f'<img class="fill" src="assets/img/{s["src"].replace(".jpg", "_bg.jpg")}" alt="" />'
                        f'<div id="{sid}-card" class="polaroid"><img src="assets/img/{s["src"]}" alt="" />'
                        f'<div class="polaroid-label">{s["label"]}</div></div></div>')
            js.append(f'tl.fromTo("#{sid}-card", {{scale:1.16, rotation:-4, opacity:0}}, {{scale:1, rotation:-2, opacity:1, duration:0.28, ease:"power3.out"}}, {t:.2f});')
            js.append(f'tl.to("#{sid}-card", {{scale:1.05, duration:{d - 0.3:.2f}, ease:"none"}}, {t + 0.3:.2f});')
        elif k == "doc":
            uniq = f"{sid}_{s['src']}"
            if not os.path.exists(f"assets/img/{uniq}"):
                os.link(f"assets/img/{s['src']}", f"assets/img/{uniq}")
            s = dict(s, src=uniq)
            K = DOC_K
            hls = "".join(
                f'<div id="{sid}-h{i}" class="hl" style="left:{x * K:.0f}px;top:{y * K:.0f}px;width:{w * K:.0f}px;height:{h * K:.0f}px"><div class="hl-u"></div></div>'
                for i, (_, x, y, w, h) in enumerate(s["hl"]))
            body.append(f'<div id="{sid}" class="clip scene docbg" data-start="{t:.2f}" data-duration="{d:.2f}" data-track-index="{track}">'
                        f'<div id="{sid}-cam" class="doccam"><div class="paper">'
                        f'<img src="assets/img/{s["src"]}" alt="" />{hls}</div></div></div>')
            cam = s["cam"]

            def pos(cx, cy, sc):
                return f"x:{W / 2 - cx * sc:.1f}, y:{H / 2 - cy * sc:.1f}, scale:{sc / DOC_K:.4f}"

            js.append(f'tl.set("#{sid}-cam", {{{pos(*cam[0][1:])}}}, {t:.2f});')
            for (a, *pa), (b, *pb) in zip(cam, cam[1:]):
                if pa == pb:
                    continue
                ease = "none" if (pa == pb or abs(pa[2] - pb[2]) < 0.2 and abs(pa[0] - pb[0]) < 60) else "power2.inOut"
                js.append(f'tl.to("#{sid}-cam", {{{pos(*pb)}, duration:{b - a:.2f}, ease:"{ease}"}}, {t + a:.2f});')
            for i, (ht, *_rest) in enumerate(s["hl"]):
                js.append(f'tl.fromTo("#{sid}-h{i}", {{scaleX:0}}, {{scaleX:1, duration:0.42, ease:"power2.out"}}, {t + ht:.2f});')
        body.extend(veils)
        veils.clear()
        if s.get("ai"):
            body.append(reenact_html(sid, t, d))
        if s.get("tag"):
            body.append(tag_html(sid, t, d, *s["tag"]))
            js.append(f'tl.fromTo("#{sid}-tag .srctag", {{opacity:0, x:-14}}, {{opacity:1, x:0, duration:0.3, ease:"power2.out"}}, {t + 0.25:.2f});')
        if s.get("loc"):
            a, b = s["loc"]
            body.append(f'<div id="{sid}-loc" class="clip ovl" data-start="{t + 0.3:.2f}" data-duration="{d - 0.5:.2f}" data-track-index="6">'
                        f'<div class="loc"><div class="loc-kick"><span class="dot"></span>{b}</div><div class="loc-main">{a}</div></div></div>')
            js.append(f'tl.fromTo("#{sid}-loc .loc", {{opacity:0, y:12}}, {{opacity:1, y:0, duration:0.35, ease:"power2.out"}}, {t + 0.3:.2f});')
    for grp in groups:
        body = [b for b in body if b != f"<!--{grp}-->"]
    # close wrappers: each wrapper opened with '<div id="x-w" class="shotw">' is followed by its media; close after them
    out, open_w = [], False
    for b in body:
        if b.startswith('<div id="') and b.endswith('class="shotw">'):
            if open_w:
                out.append("</div>")
            out.append(b)
            open_w = True
            continue
        if open_w and not b.startswith(("<video", "<img")):
            out.append("</div>")
            open_w = False
        out.append(b)
    if open_w:
        out.append("</div>")
    return out, js


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
/* inset card (real footage shown 16:9 over a blurred copy, like the reference court-exhibit cards) */
.inset-media {{ position: absolute; left: 0; top: 656px; width: 1080px; height: 608px; object-fit: cover; }}
.inset-frame {{ position: absolute; left: 0; top: 650px; width: 1080px; height: 614px; border-top: 6px solid var(--red);
  box-shadow: 0 30px 80px rgba(0,0,0,0.7); }}
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
