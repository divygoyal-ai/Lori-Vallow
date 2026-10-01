# Lori Vallow series: handoff for a new session

Everything a fresh session needs to carry on the series exactly as it was built in Episode 1.
Read this first, then `docs/STYLE_GUIDE.md` (binding production rules and the caption spec).

## What this is

A vertical 9:16 true-crime series, "Lori Vallow", 12 episodes. **Episode 1, "The Man Who Was Afraid"
(2:35), is finished and approved by the producer ("perfect, no further changes")** at v7. The
producer supplies the voiceover (VO) and music; visuals exist only to complement the audio.

Final v7 master (1080x1920, 30 fps, captions on): Drive file `1M-xEoz6RgFhK4aNDREAq5HKWKxhtirQ_`
in the Episode 1 folder.

## Drive folders

| What | Folder id |
|---|---|
| Episode 1 (audio, draft, finished renders) | `1PoBu34ngp3UAU5yjymm9TV-r2joGUGE6` |
| AI generated shots (producer's originals) | `1h2kwOkEkonGFSNPTQp9tUhQSo_CILtyW` |
| Real images / videos + audio source | `16kzcywyGM1VugvTQWHIrmeGk_trV5PQS` |
| Sample reference episodes (Watts, Clancy, Kirk) | `1enDtRYuVCA7pJROopqtHa2rwEBhE3ubq` |

Source media is **not in git** (`ep1_src/`, `ep1/assets/video|audio`, `ep1/renders/` are ignored). A new
machine must re-download sources from Drive before `ep1/prep/prep_assets.py` can run.

## Producer's rules (non-negotiable)

1. **No minors' faces. No faces in AI shots at all**: every AI person is seen from behind or out of
   frame. Adult faces appear only in real, public footage or photos. A baby's face is blurred.
2. Only copyright-free / public real footage. **Real footage is 70-80% of runtime; AI is 20-30%**
   (Episode 1 ended at 27%). Landscape shots at most 5-10%; everything else is full-screen vertical.
3. Charles Vallow in AI shots is always the same bald, heavyset man in a dark navy polo, from behind.
4. One dark, warm, low-key grade (see "Grade"). Nothing "blacked out": faces and rooms must read.
5. No whooshes, no pen-scratch SFX, no more underline graphics than the ones already designed.
   Underlines get a soft, low pencil stroke, never a marker squeak.
6. Every shot is new: no repeats.
7. **Credits: never run a paid operation without telling the producer the exact cost and getting a yes.**
   Episode 1 burned ~26,000 credits on video upscaling the producer had not approved. Do not repeat it.
   Use Kling 2.5 (not 3.0) for video unless told otherwise.

## How an AI shot is made (Magnific)

1. **Reference image with Nano Banana 2**, 9:16. Attach a still of Charles from behind as the image
   reference so he stays consistent. Prompts state "strictly from behind / no faces visible anywhere".
2. **Animate with Kling** (2.5 = ~140 credits at 720p, 5 s), start frame = that image, 9:16. Prompts ask
   for minimal, slow, calm motion, "nobody turns around", and often slow motion.
3. Download, cut to the exact length used in the edit.

The producer wants this done in the **Magnific website with the "Infinite image generation" toggle on**,
driven by Claude in Chrome (credits are charged when it is called through the API connector, which is
what the cloud sessions used). Save finished images and clips into the episode's Drive folder.

Reusable Charles reference: a clean frame of him from behind (bald head, navy polo, broad shoulders).
Episode 1's came from the producer's own AI clips; regenerate one if needed and keep it fixed.

### Prompt patterns that worked

- *Reference stills*: "Photoreal cinematic film still ... the same bald, heavyset man in his early 60s from
  the reference image, dark navy polo shirt, seen strictly from behind ... No text. Low-key moody true-crime
  documentary look, muted colours, deep but detailed shadows, subtle film texture."
- *Kling*: "Slow cinematic push-in from behind ... he never turns around, his face is never visible ...
  realistic, calm, documentary cinematography."

### Lessons (things that went wrong)

- AI drifts: people turn their heads toward camera near the end of clips, or a background person shows a
  face. **Watch every second**; trim before the turn or blur a small patch.
- AI invents garbled text on screens (TV, signs): replace the screen with a soft blur.
- Kling shows a young-looking person if the subject is small or backlit. Check apparent age. A man
  writing at a desk read as a kid, so Chad Daybell got his real booking photo plus an empty desk instead.
- Motion that "pushes back" or jerks reads as a glitch; prefer a still with a slow push-in.
- Magnific's content filter falsely rejected a prompt with "hug" phrasing; reword neutrally.
- Symbolic images: simple and believable (Earth from orbit), not exaggerated disaster art.
- Tag AI shots on screen: REENACTMENT (stand-in for a real moment) or ILLUSTRATION (symbolic).

## Real footage

- Government-released bodycam and interview footage is 16:9 at 720p. **Never crop and blow up 2.7x**:
  either show it as a native-resolution card over a blurred copy (used for the two interview cards), or cut a
  face-centred 9:16 crop and (only with the producer's approval of the cost) upscale it.
- Bodycam burnt-in timestamps are zoomed out of frame (push-in origin low).
- Source tags on every real shot: BODYCAM / POLICE INTERVIEW / COURT FILING / FAMILY PHOTO / BOOKING PHOTO
  plus place and date.
- Court filings are real PDFs shown with a camera path, red pencil highlights, and a dark fade behind the
  captions so the text stays readable.

## Grade (baked by `ep1/prep/prep_assets.py`, per-clip solved to a target)

Warm, low-key, muted colour, no grain. Mean luma targets: AI 0.14, real footage 0.19-0.21, photos 0.24,
documents ~0.38 (warm paper), booking photos 0.34 (white height chart), daylight AI 0.13.
Curve `0/0 0.08/0.045 0.3/0.21 0.6/0.5 0.85/0.8 1/0.93`, warm balance, light vignette.

## Audio

VO normalised to -14 LUFS; music bed held ~18-20 dB under the VO and lifted in pauses; sparse motivated
SFX (bass hits, paper, heartbeat, distant siren, soft pencil). Final mix measures ~ -15.7 LUFS.
Music lane and SFX times are in `ep1/build.py`. A new episode needs its own timings.

## Captions (added in v5; producer approved)

Spec is in `docs/STYLE_GUIDE.md` section 3. Implementation: `ep1/captions.py` (hand-chunked lines,
`*word*` marks the red keyword, `>` marks a quote in Playfair Display Italic) aligned to Whisper word
timings in `ep1/transcript.json`. Anton caps, white, soft shadow, ~80% down the frame.

## Pipeline for a new episode

1. Get VO + music; transcribe with Whisper (word timings) into `transcript.json`.
2. Write the shot list (`SHOTS` in `ep1/build.py`: video / image / card / polaroid / doc). Every cut lands
   on a word.
3. Gather real footage/photos first; generate AI shots only where real material can't cover the line.
4. `python3 prep/build_parallel.py` (bakes grade, cuts clips) then `python3 build.py` to write `index.html`.
5. `npx -y hyperframes@0.8.79 lint`, then `snapshot` with `--at` for every shot and look at each one.
6. Render: `npx -y hyperframes@0.8.79 render --quality delivery --video-frame-format png --video-bitrate 9M -o renders/<name>.mp4`
   (about 25 minutes, ~170 MB, software GPU). Verify size, loudness, spot-check frames.
7. Upload to the Episode folder on Drive and send a 720p preview.

Copy `ep1/` to `ep2/` (etc.) and change the shot list, captions and audio timings.

## Episode 1 shot map (for reference)

Real Charles portrait opening -> aerial of Chandler -> AI party (Charles from behind) -> AI family on the porch
(slow motion) -> wedding photo -> AI garden (kids from behind) -> AI boy on the floor -> Charles with baby
(baby's face blurred) -> AI family watching TV -> real bodycam (Jan 31, 2019) -> Lori bodycam -> Lori police
interview -> Lori booking photo -> divorce filing pages (highlights) -> Earth from orbit -> calendar July 2020
-> filing pages -> Lori interview -> bodycam -> real photo of Charles -> filing -> Chad Daybell booking photo
-> writer's desk (empty) -> Lori interview -> AI watching (Charles from behind) -> bodycam -> AI family court
-> filing -> "I will..." still -> filing -> bodycam x2 -> Maricopa court card -> Charles daylight bodycam ->
bodycam walk-away -> black, end card "EPISODE 2".

## Credits and accounts

Magnific plan had ~81,000 credits left after Episode 1. Drive uploads were done through a Composio
Google Drive connector (`GOOGLEDRIVE_UPLOAD_FROM_URL`, then `GOOGLEDRIVE_MOVE_FILE` into the Episode folder).

## Clip Check on Episode 1 (v7), 2026-10-01

Run with the Osira episode review skill. Files in `reviews/ep1_clip_check/`: the PDF report, the xlsx
clearance log (formulas recalculated, zero errors), and the scripts (`data.py`, `build_report.py`).
`OSIRA_CONTEXT_HANDOFF.md` and the source registry were not available, so every source was researched fresh.

Status: **BLOCKED** (self-check, not a sign-off; verdicts are internal working rules, not legal advice).
Third-party material is 109.6 s of 155 s (71%). Verdicts: 1 USE, 23 USE IF, 0 LICENSE, 12 DON'T, 4 NOT CLEARED.

Open items, in order:
1. A: the on-screen and spoken "exact words" quote is not in the court filing. Re-record or soften.
2. B: bodycam is a Law&Crime copy with the logo cropped out, tagged Chandler PD but released by Gilbert PD.
3. C: four photos of Charles (homicide victim) with no consent or traced owner.
4. D: AI labels must read KI-GENERIERT / AI-GENERATED and be larger. E: add CC credits (aerial, court sign).
5. F to H: trace unidentified sources, blur the minor's name on filing page 1, drop the circled 24th on the calendar.

New rule for later episodes: log source and capture method for every file when it arrives, never crop out a
logo, and tag the agency that actually released footage. Seven questions for counsel are in the report.
