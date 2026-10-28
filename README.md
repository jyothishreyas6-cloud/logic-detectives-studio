# logic-detectives-studio
Logic Detectives Studio video generation

---

## How the studio works

Everything needed to make a Logic Detectives episode in the cloud, once a week (Saturday, with a Sunday catch-up), with Australian voices.

- `PRODUCTION_SPEC.md`: the finalised style, voice, layout, engagement and upload rules. Follow it exactly.
- `engine/kit.py`: the episode kit (timeline from voice files, read-along caption strip, "Case open!" sweep, "Case solved!" stamp, ring, lens and zoom cues, Foley, melody in gaps only, loudness, captions, discovery cut, checks, loop back to frame 1).
- `engine/rig14.py`: Bramble, Otto and Ivy (3D shading, faces with expressions, open-paw pointing, single hops, talking mouths). Poses come from each episode's `poses()`.
- `engine/scenes13.py`, `engine/scenes14.py`, `engine/render.py`: backgrounds (garden, room), props (ribbon, ruler, kites, scissors, lamington, cards, recap rows) and true-to-life scale helpers (`sq_s(px_per_cm)`, `br_s(px_per_cm)`).
- `episodes/epNNN_slug/episode.py`: one folder per episode (see `episodes/ep000_kit_test` for the shape, and `reference/short1_v14/` for the full Short 1 build).
- `tools/tts_google.py` + `.github/workflows/tts.yml`: the GitHub Action that turns `lines.json` into Australian voices (Google Chirp 3 HD, en-AU) using the repository secret `GOOGLE_TTS_API_KEY`.
- `media/`: finished files, published by the raw GitHub URL so Metricool can fetch them.

## Making an episode
1. `pip install pycairo numpy pillow` and make sure `ffmpeg` and the Comfortaa font (`fonts-comfortaa`) are installed.
2. Create `episodes/epNNN_slug/episode.py` with `CASE_NO`, `RULE`, `SETTING`, `SENTENCE_LIMIT`, `LINES` (and `STRIP_HIDDEN`, `CHILD_TURN`, `STAMP_LINE`, `OPEN_LINE`, `CUT`, `cues`, `poses`, `scene`, optional `cards`, `foley`).
3. `python3 engine/kit.py episodes/epNNN_slug story` and fix every FAIL (context, takeaway, continuity, consistency; see PRODUCTION_SPEC.md "Story spine"). Then `python3 engine/kit.py episodes/epNNN_slug manifest`, commit and push `lines.json`. The Action makes `lines/lNN.wav` and pushes them back (about a minute). `git pull` until they appear.
4. `python3 engine/kit.py episodes/epNNN_slug audio`, then `frames ...` and `sheet` to check stills against the spec (no overlaps, real sizes, one focus, text matches speech, characters above the caption strip).
5. `video`, `cut`, `check` (pace, sentence length, loop, loudness). Fix anything flagged and render again.
6. Copy `short.mp4`, `cut.mp4` and both captions to `media/epNNN_slug/`, commit and push, then schedule in Metricool with the raw URLs (autoPublish false).
