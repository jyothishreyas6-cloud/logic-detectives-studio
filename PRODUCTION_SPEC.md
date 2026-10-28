# Logic Detectives production spec (finalised 20/10/2026)

Calm, story-led educational cases for NSW children aged about 5 to 10 (Kindergarten to Year 4). YouTube and Instagram only. Owner: Shreyas Jyothi (Sydney). Australian English spelling, dates DD/MM/YYYY, no em dashes anywhere.

## Story spine: context, takeaway, continuity, consistency (added 28/10/2026)
Every episode must have all four. `python3 engine/kit.py EP story` checks them from the script alone; run it before voicing and fix every FAIL. `manifest` and `check` run it too.

**1. Context (the viewer knows what is going on within about 10 s)**
- Frame 1 already shows the place and the problem. Name the place in `SETTING` (episode.py) and use it in the upload copy.
- Lines 1 to 2: Otto or Ivy says the problem as a fairness or feelings hook ("Hey! That's not fair! Otto got more!"). The viewer hears who has the problem and why it matters to them.
- By line 4: "Today's case: ..." read word for word from the title card.
- Before the test: explain the word taught ("Half means ...") and tie it to an everyday Australian example ("It's like a sausage sizzle.").

**2. Takeaway (one rule the child can say back)**
- Exactly one `RULE` per episode: one sentence within the sentence limit (for example "The last number tells how many.").
- Say the RULE word for word at least three times: first while proving it (before "Case solved!"), then "Remember. <RULE>" and "Say it with me. <RULE>" (2 s child's turn). The Remember card shows the same words.
- "Try it at home." practises that same rule with things every home has.
- The upload copy's learning goal and the Instagram caption quote the RULE in the same words.

**3. Continuity (inside the video and across the series)**
- Inside the video: one setting and one time of day; props stay where they were unless we see them move; characters keep their side of the frame; every count, length or number on screen matches what is said at that moment.
- Across the series: `CASE_NO` matches the folder number. The last line is "Next case: ..." naming the next row of the production order. The next episode's "Today's case" picks up that teaser's words. If the order changed after a teaser went out, say so in the report.
- Fixed roles keep the pattern familiar: Otto rushes or makes the mistake, Ivy notices, Bramble tests and asks the viewer, the narrator explains, Pip or Mabel bring clues.

**4. Consistency (every episode feels like the same show)**
- The fixed beat order, with locked words: "Case open!" → hook → "Today's case: ..." → word explained + everyday example → the attempt or mistake → "Let's not guess. Let's test." → Bramble asks the viewer to point or show (3 to 5 s silence) → A or B read aloud → "Pause and think." (5 s) → test step by step, a reason after each step → reveal ("It's A!" or "It's B!") with a character's "Oh!" → proof a second way → "Case solved!" stamp → funny moment → "Remember. <RULE>" → "Say it with me. <RULE>" → "Try it at home. ..." → "Next case: ..." → loop to frame 1.
- Same cast looks, scarf colours, voices, fonts, card styles, caption strip, stamp, jingle and colours every time; reuse the engine's drawing code rather than redrawing characters.
- Same upload copy shape, title pattern and posting slots.

## Voice and accent
- Every voice speaks with an **Australian accent**: Google Cloud Text-to-Speech, Chirp 3 HD voices, language en-AU.
- Cast (first choice, then fallback if the voice is not offered in en-AU): Narrator Sulafat (warm, female; fallback Vindemiatrix, Achernar), Bramble Sadaltager (knowledgeable, male; fallback Schedar, Charon), Otto Puck (upbeat, male; fallback Fenrir), Ivy Leda (youthful, female; fallback Kore, Aoede).
- Pace: narrator speakingRate about 0.85 (aim for 140 to 150 words per minute within a line for Kindergarten to Year 2, about 160 for Years 3 to 4), characters about 0.9. If a line still runs faster than the target, slow it a little more.
- Kokoro (af_heart, bm_george, am_puck, bf_emma) is the fallback only if Google TTS is unavailable; it has no Australian voices, so flag it to Shreyas.

## Cast and look
- Detective Bramble, calm hedgehog with a magnifying glass ("Let's not guess. Let's test."); Otto, eager red squirrel, ochre scarf; Ivy, thoughtful red squirrel, sage scarf; Pip, field mouse in a straw hat; Mabel, neighbour with the vegetable garden.
- Soft 3D style: rounded shaded volumes lit from the upper left, highlights, shaded limbs, soft contact shadows, calm illustrated backgrounds, muted palette.
- Faces carry the emotion: eyebrows, wide eyes for surprise, one raised brow for thinking, "oh!" mouth for discovery, big smile for success.

## Age-level language and pace
- Sentences: Kindergarten to Year 2 at most 8 words (aim 4 to 6); Years 3 to 4 at most 10. One idea per sentence; split "if/when/to ..." openers into two sentences.
- Everyday words; a harder word only when it is the word taught, and explain it the first time ("Equal means the same.").
- At least 0.8 s of silence between lines, about 1.5 s after each key idea, at least 5 s after a question the child answers.

## Layout and real-life sizes
- No overlaps: never two characters, two objects of interest, two focus points or two moving things on top of each other. Captions, labels and cards sit in clear space.
- Use the whole 9:16 frame in zones: card or question at the top, the object being taught in the middle, characters above the caption strip at the bottom.
- True-to-life sizes: squirrel sitting about 20 cm (feet to ear tips), hedgehog about 12 cm tall and 20 cm long, mouse about 8 cm, cookie 8 cm, lamington about 5 to 6 cm, children's scissors 9 cm, ruler 10 cm, toy kite 14 cm. Look up any new object. Nearer things up to about 10% larger.
- Characters face what they point at; place them on the side that allows it.

## Engagement and parent trust
- Signature opening: "Case open!" (magnifying glass sweeps across, soft two-note jingle) over a problem already visible in frame 1.
- Fairness or feelings hook in the first 3 s, spoken by a character ("Hey! That's not fair!").
- One gentle funny moment per video, never at anyone's expense, never mid-teaching.
- Bramble asks the viewer directly at least twice (point or show, and predict), each followed by 3 to 5 s of silence.
- Prediction: A or B picture cards (max 3 words each), narrator reads both, "Pause and think", 5 s silence while a ring fills, then a tick.
- Proof a second way (measure, count, match), then the "Case solved!" paw-print stamp.
- Recap card with "Say it with me" call-and-response (2 s gap for the child) and a "Try it at home" activity.
- Teaser for the next case, then loop back to frame 1.
- Read-along caption strip at the bottom: every spoken line, word-by-word highlight, speaker face icon and colour. It hides while a card shows the same words. No speech bubbles.
- Attention cues: lens for tiny details, gentle zoom (about 1.2x, at least 18 s apart, about four per Short) for big actions, ring for comparisons, look chime on each. One cue at a time; with the caption strip on, cues carry no text labels.
- Characters are always alive (breathing, sway, blinks, twitches) but movement never competes with the observation spot. Pointing with an open paw (fingers together, thumb out) or the magnifying glass, never a single raised finger, arm on a diagonal, never across the face; the arm rises once and holds still. One single hop for joy; paw on head for unsure.
- Audio: no music under speech; a soft original melody only in silent gaps of about 2 s or more (never in the child's turn); soft Foley for real actions; loudness about -14 LUFS.
- Everyday Australian examples (lamington, Vegemite toast, sausage sizzle, cricket, the beach, school canteen) plus a mix of homes, families and places.

## Formats
- Full Short: vertical 1080x1920, 90 to 130 s.
- Discovery cut: 45 to 60 s from the same footage (hook, key step, answer, "Case solved!", "Say it with me", teaser), gentle 0.4 s dissolves.
- Long-form (when used): 16:9, 6 to 8 minutes, same structure, YouTube chapters.

## Upload details (YouTube via Metricool)
- Made for kids: yes. Category: Education. Type: short. Altered or synthetic content: no (clearly animated).
- Title: the question or skill in plain words + "| Logic Detectives #Shorts". No sensational or keyword-stuffed titles.
- Description starts with "For grown-ups" (learning goal, verified NSW syllabus link, question to ask, try-at-home activity), then hook, What your child will learn, What happens in this case, Key words, Try it at home, About Logic Detectives.
- Tags; playlists by subject and by Year or Stage; captions file (en-AU); no calls to action asking children to comment, subscribe or share.
- Publishing: schedule in Metricool with autoPublish false, so Shreyas gets a phone notification and publishes with one tap. Nothing goes live unseen.
- Instagram Reel (discovery cut) captions are written for parents, never to children.

## Quality bar (YouTube kids principles)
Reward: learning and curiosity, kindness, creativity and play, life skills, showing them the world. Avoid: deceptively educational, hard to follow, sensational, heavily promotional, unclear audio. Check every fact and sum. Every case needs a new setting, problem shape, example, funny moment and reveal (inauthentic-content policy). Teacher review line left blank for Shreyas; never claim teacher review unless filled.
