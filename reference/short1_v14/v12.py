"""Short 1 v12: paced for 6 to 8 year olds.

- 28 lines rewritten so no sentence is longer than 8 words; voices regenerated slower
  (narrator Kokoro speed 0.78, characters 0.85) in kokoro/v12_lines.
- New timeline: at least 0.8 s between lines, 1.5 s after each key idea, 5 s of silent
  thinking time on the A or B question. Visuals are time-warped onto the new timeline,
  anchored at each line, so every action still lands on its words.
- On-screen text: every label repeats the words being spoken, and only one piece of text
  shows at a time (labels hide while a speech bubble or explanation card is up).
- A or B cards: 2 to 3 words each, larger text, read aloud by the narrator.

  python3 v12.py audio     -> audio_v12.wav, timings_v12.json, captions_v12_en-AU.srt
  python3 v12.py frames 0 5 ...
  python3 v12.py video     -> logic_detectives_short1_v12.mp4
"""
import bisect
import json
import math
import subprocess
import sys
import wave

import cairo
import numpy as np

import render as R
import v6
import v7
import v8
import v9
import v11                     # rig3d characters, poses, cue list (old timeline)
import rig3d as rig
from render import W, H, FPS, INK, rrect, text, src, prog, ease

SR = 24000
D = "/mnt/user-data/uploads/Videos/Logic Detectives/kokoro/v12_lines"

# (who, text, old-timeline anchor, silence after this line)
LINES = [
    ("N", "Is this really half?", 0.3, 1.0),
    ("N", "Today's case: what is a half?", 3.3, 0.8),
    ("N", "Half means two pieces. Both pieces are the same size.", 5.9, 1.5),
    ("N", "Like a cookie for two friends. Each friend gets the same.", 9.7, 1.5),
    ("O", "One ribbon, two kites. I'll cut it right here!", 14.3, 0.8),
    ("I", "Wait. Is that the middle?", 17.3, 1.0),
    ("N", "The mark might not be in the middle. Then one piece is longer.", 20.4, 1.5),
    ("B", "Let's not guess. Let's test.", 26.4, 0.8),
    ("N", "A. At Otto's mark.", 29.1, 0.6),
    ("N", "B. Somewhere else.", 29.5, 0.6),
    ("N", "Pause and think.", 29.9, 5.4),
    ("N", "Watch the ends. Bring one end to meet the other.", 33.4, 1.0),
    ("B", "Ends together.", 36.8, 0.8),
    ("N", "The two ends match. So both sides are the same length.", 38.5, 1.5),
    ("N", "The fold shows the middle.", 42.0, 1.5),
    ("N", "The middle is here. Otto's mark is over there. It's B!", 45.7, 0.8),
    ("O", "Oops. My mark was too far.", 49.2, 1.0),
    ("N", "Cut at the fold.", 51.1, 0.8),
    ("N", "Line them up.", 53.1, 1.0),
    ("N", "Ten centimetres, and ten centimetres.", 55.9, 0.8),
    ("N", "Same length!", 58.5, 0.8),
    ("I", "They match!", 60.9, 0.8),
    ("N", "Two equal pieces. Equal means the same. Each one is a half.", 62.3, 1.0),
    ("O", "Yay!", 65.5, 1.2),
    ("N", "Remember: half means two equal parts.", 68.8, 1.5),
    ("N", "To find the middle, fold it end to end.", 71.8, 1.5),
    ("N", "Try it at home. Use string or paper.", 75.5, 1.0),
    ("N", "Next case: four pieces. Are they fair?", 79.0, 0.6),
]


def load(path):
    with wave.open(path) as w:
        sr = w.getframerate()
        raw, width = w.readframes(w.getnframes()), w.getsampwidth()
    d = (np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0) if width == 2 \
        else np.frombuffer(raw, dtype=np.float32)
    if sr != SR:   # simple resample if needed
        x = np.linspace(0, 1, int(len(d) * SR / sr))
        d = np.interp(x, np.linspace(0, 1, len(d)), d).astype(np.float32)
    nz = np.where(np.abs(d) > 0.005)[0]
    d = d[max(0, nz[0] - 240): nz[-1] + 1200]
    return d / (np.max(np.abs(d)) + 1e-9) * 0.8


def plan():
    """New start/end per line and the (new, old) time-warp anchors."""
    clips = [load(f"{D}/l{i:02d}.wav") for i in range(len(LINES))]
    rows, anchors = [], [(0.0, 0.0)]
    s = LINES[0][2]
    for i, ((who, line, old, gap), clip) in enumerate(zip(LINES, clips)):
        if i:
            pw, pl, pold, pgap = LINES[i - 1]
            s = max(rows[-1]["end"] + pgap, rows[-1]["start"] + (old - pold))
        e = s + len(clip) / SR
        rows.append({"who": who, "text": line, "start": round(s, 3), "end": round(e, 3)})
        anchors.append((s, old))
        if i == 10:   # the think ring fills during the silence
            anchors.append((e + 5.0, 33.0))
    last = rows[-1]["end"]
    anchors += [(last + 0.6, 82.0), (last + 1.6, 83.0)]
    return rows, clips, anchors, last + 1.6


ROWS, CLIPS, ANCH, TOTAL = plan()
AN_NEW = [a for a, _ in ANCH]
AN_OLD = [b for _, b in ANCH]


def to_old(T):
    return float(np.interp(T, AN_NEW, AN_OLD))


def to_new(t):
    return float(np.interp(t, AN_OLD, AN_NEW))


# ---------------------------------------------------------------- on-screen text
LABELS = {
    "One long, one short": "", "Split in the middle": "", "Same size for each friend": "Each friend gets the same",
    "Otto's mark": "", "Is the middle here?": "", "One piece longer": "One piece is longer",
    "Choose A or B": "", "Watch the ends": "Watch the ends", "Ends together": "",
    "The middle": "The middle", "Not the same spot": "The middle is here", "B is right": "It's B!",
    "Cut here": "Cut at the fold", "Line them up": "Line them up", "10 cm and 10 cm": "10 cm and 10 cm",
    "Ends line up": "Same length!", "Same length tails": "Two equal pieces", "Four pieces": "Four pieces",
}


def relabel(c):
    c = list(c)
    if c[0] == "ring":
        c[7] = LABELS.get(c[7], c[7])
    elif c[0] == "lens":
        c[9] = LABELS.get(c[9], c[9])
    else:
        c[6] = LABELS.get(c[6], c[6])
    c[1], c[2] = to_new(c[1]), to_new(c[2])
    return tuple(c)


CUES = [relabel(c) for c in v11.CUES]

# speech bubbles follow the new line timings and stay up 1 s after the line ends
BUB_LINE = {0: 4, 1: 5, 2: 7, 3: 12, 4: 16, 5: 21, 6: 23}
BUBBLES = []
for k, (s, e, cx, cy, lines, tx, ty) in enumerate(v7.BUBBLES):
    r = ROWS[BUB_LINE[k]]
    BUBBLES.append((r["start"] - 0.1, r["end"] + 1.0, cx, cy, lines, tx, ty))
CARD = (ROWS[13]["start"] - 0.2, ROWS[13]["end"] + 1.2)   # "The two ends match ..." card

_orig_label_pill = v9.label_pill


def _pill(ctx, label, lx, ly, a):
    if label and a > 0.01:
        _orig_label_pill(ctx, label, lx, ly, a)


v9.label_pill = _pill

_orig_R_text = R.text


def _scene_text(ctx, s, *a, **k):        # drop extra words that repeat a bubble
    if s in ("ends together",):
        return
    return _orig_R_text(ctx, s, *a, **k)


R.text = _scene_text
R.case_badge = lambda ctx, a: None       # "Case: The Kite Ribbon" competed with Otto's line

_orig_v6_text = v6.text
CARD_WORDS = {"At Otto's": 0, "mark": 1, "Somewhere": 0, "else": 1}


def _card_text(ctx, s, x, y, size, *a, **k):
    if size == 34 and s in CARD_WORDS:
        size, y = 50, y - 12 + 18 * CARD_WORDS[s]
    return _orig_v6_text(ctx, s, x, y, size, *a, **k)


v6.text = _card_text


def _ab_cards(ctx, a, picked=0.0):
    v6.choice_card(ctx, 90, "A", ("At Otto's", "mark"), 0.5, a, dim=picked)
    v6.choice_card(ctx, 570, "B", ("Somewhere", "else"), 0.62, a, picked=picked)


v6.ab_cards = _ab_cards

RECAP = {"Fold end to end": ["To find the middle,", "fold it end to end"],
         "Try it at home:": ["Try it at home.", "Use string or paper."]}
_orig_row = v7.recap_row


def _row(ctx, y, a, icon, lines):
    return _orig_row(ctx, y, a, icon, RECAP.get(lines[0], lines))


v7.recap_row = _row


def ring_only(ctx, cx, cy, rx, ry, a):
    g = cairo.RadialGradient(0, 0, 0, 0, 0, 1)
    g.add_color_stop_rgba(0.0, 0.12, 0.10, 0.08, 0.0)
    g.add_color_stop_rgba(0.80, 0.12, 0.10, 0.08, 0.0)
    g.add_color_stop_rgba(1.0, 0.12, 0.10, 0.08, 0.34 * a)
    k = 1.35
    g.set_matrix(cairo.Matrix(1 / (rx * k), 0, 0, 1 / (ry * k), -cx / (rx * k), -cy / (ry * k)))
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, H)
    ctx.fill()
    br = 1.0 + 0.035 * math.sin(R.NOW[0] * 3.2)
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(rx * 1.08 * br, ry * 1.08 * br)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_line_width(9)
    ctx.set_source_rgba(*R.rgb(v8.RING), 0.95 * a)
    ctx.stroke()


def text_busy(T):
    """1 while a speech bubble or explanation card is showing (labels give way)."""
    b = 0.0
    for s, e, *_ in BUBBLES:
        b = max(b, prog(T, s - 0.3, s) * (1 - prog(T, e, e + 0.3)))
    b = max(b, prog(T, CARD[0] - 0.3, CARD[0]) * (1 - prog(T, CARD[1], CARD[1] + 0.3)))
    return b


# ---------------------------------------------------------------- frames
rig.TALK = [(r["start"], r["end"], r["who"]) for r in ROWS if r["who"] in ("O", "I", "B")]
rig.TIME_OFFSET = v6.IDLE0
SCENE_SURF = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)


def draw_scenes(ctx, T, t):
    rig.POSE.clear()
    rig.POSE.update(v11.poses(t))
    for i, (a, b, fn) in enumerate(v7.SCENES):
        if a <= t < b or (i == len(v7.SCENES) - 1 and t >= a):
            R.NOW[0] = T + v6.IDLE0
            ctx.save()
            fn(ctx, t - a)
            ctx.restore()
            if i + 1 < len(v7.SCENES) and t > b - v7.XF:
                na, _, nfn = v7.SCENES[i + 1]
                R.NOW[0] = T + v6.IDLE0
                ctx.push_group()
                ctx.save()
                nfn(ctx, max(0.0, t - na))
                ctx.restore()
                ctx.pop_group_to_source()
                ctx.paint_with_alpha(ease((t - (b - v7.XF)) / v7.XF))
            break


def draw_frame(ctx, T):
    t = to_old(T)
    sc = cairo.Context(SCENE_SURF)
    sc.set_operator(cairo.OPERATOR_SOURCE)
    src(sc, R.CREAM)
    sc.paint()
    sc.set_operator(cairo.OPERATOR_OVER)
    draw_scenes(sc, T, t)
    SCENE_SURF.flush()
    ctx.save()
    zm = v11.zoom_amount(t)
    if zm:
        z, cx, cy = zm
        ctx.translate(cx, cy)
        ctx.scale(z, z)
        ctx.translate(-cx, -cy)
    ctx.set_source_surface(SCENE_SURF, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint()
    ctx.restore()
    R.NOW[0] = T + v6.IDLE0
    busy = text_busy(T)
    for c in CUES:
        kind, s, e = c[0], c[1], c[2]
        if not (s <= T <= e):
            continue
        a = prog(T, s, s + 0.4) * (1 - prog(T, e - 0.35, e))
        la = a * (1 - busy)
        if kind == "ring":
            cx, cy, rx, ry, label, lx, ly = c[3:10]
            if label and la > 0.01:
                ring_only(ctx, cx, cy, rx, ry, a * busy) if busy > 0 else None
                v8.focus(ctx, cx, cy, rx, ry, label, lx, ly, la)
            else:
                ring_only(ctx, cx, cy, rx, ry, a)
        elif kind == "lens":
            args = list(c[3:12])
            args[6] = args[6] if la > 0.01 else ""
            v9.lens(ctx, SCENE_SURF, *args, a)
        elif kind == "zoom":
            _pill(ctx, c[6], c[7], c[8], la)
    ka = prog(T, CARD[0], CARD[0] + 0.5) * (1 - prog(T, CARD[1] - 0.5, CARD[1]))
    if ka > 0:
        rrect(ctx, 70, 1220, 940, 190, 40, "#FFFFFF", 0.94 * ka)
        text(ctx, "The two ends match.", W / 2, 1282, 50, INK, ka)
        text(ctx, "So both sides are the same length.", W / 2, 1350, 50, INK, ka)
    for s, e, cx, cy, lines, tx, ty in BUBBLES:
        a = prog(T, s - 0.1, s + 0.25) * (1 - prog(T, e - 0.2, e + 0.15))
        v6.bubble(ctx, cx, cy, lines, tx, ty, a)


# ---------------------------------------------------------------- audio
def build_audio():
    import narration as Nn
    n = int(TOTAL * SR)
    voice = np.zeros(n, dtype=np.float32)
    for r, clip in zip(ROWS, CLIPS):
        a = int(r["start"] * SR)
        b = min(n, a + len(clip))
        voice[a:b] += clip[: b - a]
    sfx = np.zeros(n, dtype=np.float32)

    def put(clip, at_old):
        a = int(to_new(at_old) * SR)
        b = min(n, a + len(clip))
        sfx[a:b] += clip[: b - a].astype(np.float32)

    put(Nn.chime(784), 0.05)
    put(Nn.pop(), 3.1)
    put(Nn.snip(), 6.45)
    put(Nn.chime(880, 1.2), 7.7)
    put(Nn.whoosh(1.0), 9.8)
    put(Nn.snip(), 14.6)
    put(Nn.whoosh(1.0), 20.8)
    for k in range(7):
        put(Nn.step(), 26.1 + k * 0.33)
    put(Nn.pop(), 28.8)
    put(Nn.chime(660, 1.2), 33.0)
    put(Nn.chime(880), 42.1)
    put(Nn.chime(1047, 1.4), 48.6)
    put(Nn.snip(), 51.8)
    put(Nn.snip(), 52.05)
    put(Nn.chime(988), 58.55)
    put(Nn.whoosh(), 60.6)
    put(Nn.chime(1175, 2.0), 64.1)
    put(Nn.pop(), 68.6)
    put(Nn.chime(880, 1.0), 71.7)
    put(Nn.chime(988, 1.0), 75.4)
    ch = v9.look_chime()
    for c in CUES:
        a = int(c[1] * SR) + int(0.05 * SR)
        b = min(n, a + len(ch))
        sfx[a:b] += ch[: b - a] * 1.0
    mix = voice + Nn.pad_track(n) + sfx
    f = int(0.3 * SR)
    mix[-f:] *= np.linspace(1, 0, f)
    mix = np.clip(mix, -1, 1)
    with wave.open("audio_v12_raw.wav", "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", "audio_v12_raw.wav", "-af",
                    "highpass=f=70,loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000", "audio_v12.wav"], check=True)
    json.dump(ROWS, open("timings_v12.json", "w"), indent=1)

    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    names = {"N": "", "B": "BRAMBLE: ", "O": "OTTO: ", "I": "IVY: "}
    with open("captions_v12_en-AU.srt", "w") as fh:
        for k, r in enumerate(ROWS, 1):
            fh.write(f"{k}\n{ts(r['start'])} --> {ts(r['end'] + 0.4)}\n{names[r['who']]}{r['text']}\n\n")
    for r in ROWS:
        print(f"{r['start']:6.2f}-{r['end']:6.2f} {r['who']} {r['text']}")
    print("TOTAL", round(TOTAL, 2))


def main():
    mode = sys.argv[1]
    if mode == "audio":
        build_audio()
        return
    if mode == "frames":
        for ts_ in sys.argv[2:]:
            surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
            ctx = cairo.Context(surf)
            draw_frame(ctx, float(ts_))
            surf.write_to_png(f"v12_{float(ts_):05.1f}.png")
        return
    n = int(TOTAL * FPS)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "audio_v12.wav",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart",
         "logic_detectives_short1_v12.mp4"], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    for i in range(n):
        ctx.identity_matrix()
        draw_frame(ctx, i / FPS)
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
    ff.stdin.close()
    ff.wait()
    print("done", ff.returncode)


if __name__ == "__main__":
    main()
