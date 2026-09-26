# Reference Style Guide: True-Crime Vertical Series

### Decisions confirmed with the producer

- **Government-released public records may be used**, with a source tag. This covers court filings
  such as the divorce petition, police bodycam and welfare-check footage, and booking photos.
- **Real adults' faces may be shown, but only in genuine real material.** Never in AI-generated or
  AI-edited shots.
- **Music:** the producer supplies the background track. If none is provided, use royalty-free stock
  or a generated suspense bed.
- **Naming:** the series is **"Lori Vallow"**. Episode 1 is **"The Man Who Was Afraid"**.
  - Title kicker: `LORI VALLOW · EPISODE 1`
  - Title: `THE MAN WHO WAS AFRAID`, with AFRAID in red
  - End card: `EPISODE 2`, `FOLLOW FOR WHAT HAPPENED NEXT`, `LORI VALLOW`
- **Other languages:** a German version (if made) is a separate render built from its own VO file.
  Captions are re-timed to that VO.

## 0. Production rules (binding; they override anything below)

1. **No minor's face is ever visible.** This applies to real footage, photos, stock and AI shots alike.
   Minors appear only from behind, in silhouette, out of focus, or as objects (a toy, shoes, an empty
   bed). Minors' faces in any real photo or clip are blurred.
2. **Real footage is used only if it is copyright-free** (public domain or clearly licensed for reuse).
   Anything else is replaced with stock footage or AI-generated content. News-station clips are not
   used.
3. **Real footage is preferred.** Use real or stock live-action footage wherever it fits, and AI only
   to fill gaps. The finished video must look realistic, like filmed footage and not like AI.
4. **The audio is the product.** The provided voiceover is the master clock. Every cut, caption and
   SFX is timed to it, and visuals only support it.
5. **AI shots never show or imitate a real person's face.** A real person appears in real footage, or
   in AI shots only from behind or in silhouette, with no morphing or likeness generation.
6. **Characters stay consistent across AI shots.** Each real person has a fixed physical description
   (build, height, hair or baldness, age, typical clothing) in the character bible (section 8). Every
   AI shot of them, including back views, must match it. A reference image per character is
   generated once and reused for every shot.
7. **Dark true-crime grade, slightly brighter than the references.** Target an average brightness of
   about 0.28–0.32 (the references sit at 0.20–0.25). Shadows keep detail and faces or subjects stay
   readable.
8. **Suspense/mystery music bed that never competes with the VO.** Keep it about 18–22 dB below the
   voice while speech plays, let it rise slightly in pauses, and duck it under key lines.
9. **Built in HyperFrames.** The whole edit is authored as HyperFrames HTML code: timeline, cuts, grade,
   captions, graphics, music, SFX and mix. It is rendered with the HyperFrames CLI to a 1080x1920 MP4.


Analysis of the three reference episodes (Drive folder `1enDtRYuVCA7pJROopqtHa2rwEBhE3ubq`).
Frames were sampled at 2 fps and inspected, with frame-by-frame passes (30 fps) on transitions and
animations. Narration was transcribed with word timestamps. Audio was measured (EBU R128, spectrograms,
speech-gap analysis), and grade statistics were taken from the image area above the captions.

| Ref | File | Length | Format | Cuts | Avg shot |
|---|---|---|---|---|---|
| A | ChrisWatts_EP01_v9_captions_fixed.mp4 | 1:38 | 1080x1920, 30 fps, ~7 Mbps | ~24 | ~4.1 s |
| B | Lindsy Clancy Episode 2.mp4 | 1:59 | 1080x1920, 24 fps, ~7 Mbps | ~20 (long animated holds) | ~5.7 s |
| C | CharlieKirk_EP06_Im_In_For_A_Million_final.mp4 | 2:56 | 1080x1920, 30 fps, ~11 Mbps | ~55 | ~3.2 s |

A and B share one house style: word-chunk ALL-CAPS captions with a red keyword. C is a variant for
archival-heavy episodes, with a letterbox and sentence subtitles. The Lori Vallow script is mostly AI
recreation plus a few real documents, so **A/B is the template**. C contributes the document/quote card,
the chapter number, and the count-up.

---

## 1. Palette: black / white / red only

- **Red** `~#D0202A` (saturated, slightly warm crimson). It is used for the keyword in each caption,
  source tags, underline rules, the title's last word, timestamp card underlines, map borders and
  highlighted quote text. It never appears as a large fill except in small label boxes.
- **White** `#FFFFFF` for captions and titles. Secondary labels are warm off-white/grey `~#CFC9BF`.
- **Black / near-black** `#0A0A0B` for end cards, letterbox bars and card backgrounds.
  The map uses charcoal-navy `~#1C1F26`.
- **Cream paper** `~#EFE9DC` is used only for document/quote cards (ref C), with a red top border.
- The footage stays muted, so red on screen always comes from graphics, apart from diegetic accents
  such as the red pregnancy-test lines and red envelope tape, which were chosen on purpose.

## 2. Color grade

Measured on the picture area above the captions:

| | Mean luma | Saturation | 2% black | 98% white | Cast |
|---|---|---|---|---|---|
| A Watts | 0.25 | 0.39 | 0.02 | 0.76 | neutral mids, **cool/teal shadows** (B>R) |
| B Clancy | 0.21 | 0.29 | 0.03 | 0.69 | **cold, desaturated blue-grey**, lifted blacks |
| C Kirk | 0.20 | 0.50 | 0.00 | 0.70 | **warm sepia/amber**, crushed blacks |

Common traits:
- **Dark, low-key images.** Average luma is around 20–25%, highlights are capped around 70–75%, and there
  is no pure white in the picture, which leaves white captions as the brightest element.
- **Heavy vignette.** In ref A it is a strong oval vignette combined with **edge blur/defocus**, a
  "peering through a lens" look that is always present, including on bodycam.
- Real footage (bodycam, news, CCTV) gets the same grade and vignette, so it matches the AI shots.
- AI shots are lit as **dusk/night or cold overcast**. Practical warm windows against blue night are a
  recurring motif ("the house at night" establishing shot).
- Subtle film grain/softness. Nothing looks crisp or digital.
- Ref C adds a **red monochrome duotone** on the title and first name-card still.
- Suggested ffmpeg starting point: `eq=contrast=1.08:brightness=-0.06:saturation=0.75`, then
  `colorbalance=bs=.06:bm=.02:rh=-.02`, then `vignette=PI/4.5`, plus an edge-blur mask and light
  `noise=alls=6:allf=t`.

## 3. Captions (the signature element)

**Style A/B (use this one):**
- Font: **Anton** or an equivalent heavy condensed grotesque, in ALL CAPS, white, with a soft dark
  drop shadow and no box.
- Size: roughly 60–70 px cap height at 1080 wide. One line, or two when the chunk is long.
- **Chunking: 2–4 words per caption, synced to the word timestamps** of the VO. Each chunk appears
  when its first word starts and holds until the next chunk. Chunk breaks follow natural speech
  phrases.
- **One red word per chunk at most.** It is the semantic keyword: nouns and emotional words such as
  FATHER, MISSING, GIRLS, HOME, TIRED, SCARED, PREGNANT, LOCKED, OPEN, QUIET, WRONG, plus people's
  first names. Function words are never red, and many chunks have no red word at all.
- Position: horizontally centered, **about 80% down the frame in A**. **B places them at about 65%**,
  over the subject's lower body. Keep them clear of the bottom 12% because of the platform UI.
- Animation: a quick 2–3 frame fade/brightness pop-in. There is no bouncing, no word-by-word karaoke
  and no scaling. Caption changes are independent of picture cuts.
- **Direct quotes** from real people are set in **Playfair Display Italic**, sentence case and white,
  with quotation marks, for example *"If you're out there, just come back."* This is the only serif
  used in captions.
- The first caption appears about 0.45 s in. The last caption clears about 0.5 s after the final word.

**Style C (reference only):** Oswald Medium sentence-case subtitles of full clauses, with a black
letterbox above and below the picture.

## 4. On-screen graphics kit

All labels use **Oswald** (condensed, wide tracking of about 0.15–0.25em, ALL CAPS, small).

1. **Episode title card over the first shot, at 0.6–0.9 s.** A tiny tracked kicker reads
   `SERIES · EPISODE 1`, then a large Anton title whose **last word is red** ("JUST COME **BACK**",
   "FIFTY-FOUR / **MINUTES**"), then a short red underline rule. It fades in with a slight blur
   (~0.2 s), holds about 3 s and fades out. It sits in the upper-middle of the frame, above the
   captions.
2. **Source tag, top-left.** A red box with white Oswald text (`NEWS INTERVIEW`, `BODYCAM`,
   `SURVEILLANCE FOOTAGE`, `COURT EXHIBIT`) and a grey Oswald line beneath it with the source/date
   (`FREDERICK POLICE · AUGUST 2018`). It appears about 0.25 s after the cut and is used on all real
   footage.
3. **`REENACTMENT` / `AI ILLUSTRATION` tag, top-right.** Tiny text in a thin outline box, shown on every
   AI shot. This is a trust and legal device.
4. **Date/place card, top-center.** A small grey kicker with a red dot (`• FREDERICK, COLORADO`) above a
   dark box with a large white date (`AUGUST 14, 2018`) and a red underline. A variant is the
   time-jump card (`• BEFORE THAT DAY` / `EARLIER THAT SUMMER`).
5. **Timestamp card (ref B).** A mono/typewriter time (`5:23 PM`) that types in character by character
   over about 0.3 s, with a red-dot kicker (`• HER APPLE WATCH · JAN 24`) and a red underline. It is
   used as a structural beat.
6. **Address card, top-left.** A dark box with a red left bar, white bold address, grey city and red
   date.
7. **Photo/"polaroid" card.** A real photo in a white-bordered print with a caption strip
   (`CHRIS WATTS`), centered over a **blurred, darkened, enlarged copy of the same image**. It enters
   with a 0.2 s scale-settle (1.1 to 1.0) and a ghost double-exposure, **landing on a low boom SFX**.
   It is used to introduce each real person.
8. **Name super (ref C).** A big Anton name with a red Oswald subtitle line
   (`TURNING POINT USA 2017 TO 2019 · PODCASTER`).
9. **Map sequence.** A dark charcoal state map with a red outline and a label reading "COLORADO"
   that zooms to the county, which is filled in dark red. A red ring pin marks the town, with a label
   box (`FREDERICK / WELD COUNTY, COLORADO / 20 MILES NORTH OF DENVER`).
10. **Social-media phone mockup.** A dark Instagram UI in a phone frame. Posts scroll or swap on each
    narrated item, hearts turn red, and the captions name each post.
11. **Document/quote card (ref C).** A cream paper card with a red top border, the author's name in bold,
    a handle/date line in mono, body text in typewriter, and **the key phrase in red with a red
    underline**, plus a source line (`POST ON X, AS SHOWN BY NEWSNATION`). It floats over a dimmed
    background. **This is the template for the divorce-petition threat line in Lori Ep1.**
12. **Chapter numeral (ref C).** A huge red Anton `06` that scales and blurs in, under a small
    `CHAPTER` kicker.
13. **Count-up number.** A big number (`$125,000` counting to `$1,150,000`) that turns red when it
    lands, with a small tracked label beneath.
14. **Call UI overlay.** An iOS-style "Incoming call" banner with a live ticking timer that ends in a
    red "Call Ended".
15. **End card.** Near-black background. A hard cut to black lands on a boom. `EPISODE 2` fades in
    over about 0.4 s in white Anton, followed by `FOLLOW FOR WHAT HAPPENED NEXT` in tracked Oswald, a
    red rule, the series name `A PERFECT FAMILY` and a tiny `THE CHRIS WATTS CASE` line. It holds
    about 2.5 s. Add a helpline line when the episode touches on self-harm (ref B). Ref C instead
    shows `NEXT 07 · <title>` over the last shot, then a series card with source credits.

## 5. Shot selection versus narration

- **Literal-but-oblique illustration.** Each shot shows what the sentence names, usually through an
  object or place rather than a person. Examples: "he works the oil fields" is a pumpjack silhouette;
  "she runs a business from her phone" is a woman's hand and phone with no face; "two little girls"
  is **empty car seats**, and "Bella… CeCe" is **an empty bed with a stuffed bunny**; "pregnant" is a
  test with red lines, and "a baby boy" is blue booties; "the house is really quiet" is a car in the
  driveway at dusk; "the window is open" is billowing curtains.
- **Minors are never shown.** Children appear as backs or silhouettes, or are replaced by objects,
  and faces in real photos are **blurred**. The Lori script already requires this.
- **Real public-record material leads whenever it exists** (news interview, bodycam, mugshot, CCTV,
  court exhibits, posts), always with a source tag. AI recreation fills the gaps and is always tagged.
- **Cuts happen on phrase or sentence boundaries**, usually at the onset of the new idea's first word.
  Cuts are hard. The dissolves that do appear are short, and a caption often carries across a cut.
- Pacing is one new image per sentence, about 3–6 s per shot. Shots get longer on emotional beats.
- **Every AI shot moves.** They are image-to-video clips with a slow dolly or push-in, curtains
  moving, snow falling or a sprinkler running. There are no dead stills; real stills get a Ken Burns
  push.
- **Recurring motifs** bookend the episode: the family house (day at the start, blue-hour night with
  lit windows at the end), with the ending line placed over the night house.
- **Structure:** a cold open on the most dramatic real footage, then "to understand how… you have to go
  back" into the backstory with a time-jump card, then who/where (polaroids and map), then the life
  details, then a turn line ("But…"), then a closing ominous line, black, and the end card.
  Titles are a quote or phrase from the story ("Just Come Back", "I'm In For A Million").

## 6. Sound

- **Loudness:** -14.5 to -15.2 LUFS integrated, with a very tight LRA of 2.7–4.3 LU (VO heavily
  compressed), 48 kHz stereo AAC at 200–300 kbps.
- **VO** runs almost wall to wall from frame 0, with short 0.6–1.5 s pauses between sentences. Pace is
  145–170 wpm, with a calm, measured, documentary delivery.
- **Music bed:** a dark sustained **drone/pad** sitting about 9–10 dB under the VO (VO median around
  -16 dB RMS, gaps around -26 dB).
  - A: an almost single-note low drone (C#). Very tonal and minimal, with no percussion.
  - B: a denser tense texture with more movement (E/D/C# cluster).
  - C: a D-centered drone with a busier high-frequency texture.
  - The bed never stops before the end card.
- **SFX are sparse and motivated:**
  - **Low sub-boom/impact** on key reveals: the cut to bodycam, the **mugshot/"His name is Chris"**,
    the cut to black and the end card. Ref A has only about 6–8 in 98 s.
  - **Diegetic SFX** fit the story beat: a phone ringing and "call rings out", and a whoosh or riser
    into the window reveal.
  - **Dropouts:** a near-silence gap just before a big line (ref B at about 33 s, before "the call rings
    out").
  - Real clip audio (such as Candace's podcast) plays with the VO paused and the bed ducked.
- **Ending:** the last line lands, the image holds about 1 s with only the bed, there is a hard cut to
  black on a boom, the end card appears, and the bed tails and fades over the last 4–6 s.

## 7. Applying this to Lori Vallow Ep1 ("The Man Who Was Afraid")

- Title card: `LORI VALLOW · EPISODE 1` over "THE MAN WHO WAS **AFRAID**" (red last word). End card series line: `LORI VALLOW`.
- The quote *"a translated being who cannot taste death"* goes in the Playfair Italic quote style over
  the night-sky shot.
- Charles's divorce petition uses the cream document card, with the threat line in red plus underline:
  *"I will kill you. Because you're not Charles. And nobody will care."* The source tag reads
  `COURT FILING · FEB 2019`.
- Bodycam or welfare check: the `BODYCAM` red tag.
- Map: Arizona, zooming to Maricopa County, with a pin on the family’s town (Gilbert or Chandler; verify against the Feb-2019 filings).
- JJ and Tylee get no faces. Use objects or backs (a small boy's sneakers or toy; a teen's back in a
  doorway). Chad stays faceless.
- Close on the big man alone in the emptying room at blue hour, then black, a boom, and
  `EPISODE 2 · SELF-DEFENSE`.

## 8. Character bible (to be filled and verified against real reference photos before generating)

| Character | Fixed traits for AI back and silhouette shots |
|---|---|
| Charles Vallow | Large, heavyset "big bear" man, early 60s. Head and hair to be verified from photos. Casual polo/button-down. |
| Lori Vallow | Slim woman, mid-40s, long light-blonde hair (verify). |
| Tylee (minor in story) | Teen girl, long brown hair (verify). Back or silhouette only. |
| JJ (minor) | Small 7-year-old boy (hair to be verified). Back, silhouette or objects only. |
| Chad Daybell | A different build from Charles (verify). Always faceless and in shadow. |
