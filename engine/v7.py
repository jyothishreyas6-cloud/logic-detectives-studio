"""Short 1 v7 (83 s): v6 plus a 'Today's case' context opening, extra explanation at the fold,
a 'Remember' recap and a try-at-home prompt.

  python3 v7.py frames 0 5 ...   -> check stills
  python3 v7.py audio            -> audio_v7.wav, timings_v7.json, captions_v7_en-AU.srt
  python3 v7.py video            -> logic_detectives_short1_v7.mp4
"""
import json
import math
import subprocess
import sys
import wave

import cairo
import numpy as np

import render as R
import v6
from render import (W, H, FPS, INK, OCHRE, SAGE, RIBBON, ellipse, rrect, text, src, prog, clamp,
                    ease, lerp, sparkles)

TOTAL = 83.0
SR = 24000
D6 = "/mnt/user-data/uploads/Videos/Logic Detectives/kokoro/v6_lines"
D7 = "/mnt/user-data/uploads/Videos/Logic Detectives/kokoro/v7_extra"

# (start, speaker, file, text)
LINES = [
    (0.3, "N", f"{D6}/line00.wav", "Is this really half?"),
    (3.3, "N", f"{D7}/x00.wav", "Today's case: what does half mean?"),
    (5.9, "N", f"{D7}/x01.wav", "Half means two pieces that are exactly the same size."),
    (9.7, "N", f"{D7}/x02.wav", "Like sharing a cookie, so you and your friend get the same amount."),
    (14.3, "O", f"{D6}/line01.wav", "One ribbon, two kites. I'll cut it right here!"),
    (17.3, "I", f"{D6}/line02.wav", "Wait. Is that the middle?"),
    (20.4, "N", f"{D6}/line03.wav", "If the mark isn't in the middle, one piece will be longer."),
    (26.4, "B", f"{D6}/line04.wav", "Let's not guess. Let's test."),
    (29.1, "N", f"{D6}/line05.wav", "What do you think? A, or B?"),
    (33.4, "N", f"{D6}/line07.wav", "Bring one end to meet the other."),
    (36.8, "B", f"{D6}/line06.wav", "Ends together."),
    (38.5, "N", f"{D7}/x03.wav", "When the two ends match, both sides are the same length."),
    (42.0, "N", f"{D6}/line08.wav", "The fold shows the middle."),
    (45.7, "N", f"{D6}/line09.wav", "The middle is here. Otto's mark is over there. It's B!"),
    (49.2, "O", f"{D6}/line10.wav", "Oops. My mark was too far."),
    (51.1, "N", f"{D6}/line11.wav", "Cut at the fold."),
    (53.1, "N", f"{D6}/line12.wav", "Line them up."),
    (55.9, "N", f"{D6}/line13.wav", "Ten centimetres, and ten centimetres."),
    (58.5, "N", f"{D6}/line14.wav", "Same length!"),
    (60.9, "I", f"{D6}/line15.wav", "They match!"),
    (62.3, "N", f"{D6}/line16.wav", "Two equal pieces. Each one is a half."),
    (65.5, "O", f"{D6}/line17.wav", "Yay!"),
    (68.8, "N", f"{D7}/x04.wav", "Remember: half means two equal parts."),
    (71.8, "N", f"{D7}/x05.wav", "To find the middle of something long, fold it end to end."),
    (75.5, "N", f"{D7}/x06.wav", "Try it at home with a piece of string or paper."),
    (79.0, "N", f"{D6}/line18.wav", "Next case: four pieces. Are they fair?"),
]

BUBBLES = [
    (14.3, 17.0, 640, 830, ["One ribbon, two kites.", "I'll cut it right here!"], 900, 1040),
    (17.3, 19.4, 420, 830, ["Wait. Is that", "the middle?"], 200, 1040),
    (26.4, 29.0, 560, 820, ["Let's not guess.", "Let's test."], 520, 1080),
    (36.8, 38.6, 560, 1460, ["Ends together."], 420, 1690),
    (49.2, 50.9, 640, 1460, ["Oops. My mark", "was too far."], 900, 1650),
    (60.9, 62.4, 360, 1150, ["They match!"], 250, 1330),
    (65.5, 66.9, 760, 1150, ["Yay!"], 850, 1330),
]


# ---------- new scenes ----------
def cookie_half(ctx, cx, cy, r, side, a=1.0):
    """Draw the left (side=-1) or right (side=+1) half of a cookie centred at (cx, cy)."""
    ctx.save()
    if side < 0:
        ctx.rectangle(cx - r - 4, cy - r - 4, r + 4, 2 * r + 8)
    else:
        ctx.rectangle(cx, cy - r - 4, r + 4, 2 * r + 8)
    ctx.clip()
    ellipse(ctx, cx, cy, r, r, "#C98E52", a)
    ellipse(ctx, cx, cy, r * 0.9, r * 0.9, "#DDA867", a)
    for dx, dy, s in ((-0.45, -0.3, 0.09), (0.35, -0.45, 0.08), (-0.2, 0.35, 0.1), (0.5, 0.2, 0.08),
                      (-0.6, 0.15, 0.07), (0.1, -0.05, 0.08), (0.25, 0.6, 0.07), (-0.35, 0.65, 0.06)):
        ellipse(ctx, cx + dx * r, cy + dy * r, s * r, s * r * 0.85, "#5E4636", a)
    ctx.restore()


def scene_ctx(ctx, t):
    """'Today's case': what half means, shown with a cookie shared between Ivy and Otto."""
    v6.R.table_top(ctx)
    a_title = prog(t, 0.1, 0.7)
    rrect(ctx, 120, 650, 840, 250, 44, "#FFFFFF", 0.93 * a_title)
    rrect(ctx, 160, 690, 70, 54, 8, OCHRE, a_title)
    rrect(ctx, 160, 680, 32, 16, 5, OCHRE, a_title)
    text(ctx, "Today's case", 560, 718, 46, "#9C7429", a_title)
    text(ctx, "What is a half?", W / 2, 826, 84, INK, a_title)
    # the cookie: whole, then a dashed line down the middle, then two equal halves
    split = prog(t, 3.4, 4.6)
    share = prog(t, 6.8, 8.6)
    cx, cy, r = W / 2, 1260, 210 - 45 * share
    gap = 60 * split
    lx = cx - gap - 70 * share
    rx = cx + gap + 70 * share
    yy = cy + 90 * share
    cookie_half(ctx, lx, yy, r, -1)
    cookie_half(ctx, rx, yy, r, +1)
    dash_a = prog(t, 2.9, 3.4) * (1 - split)
    if dash_a > 0:
        ctx.set_dash([18, 14])
        ctx.set_line_width(7)
        src(ctx, "#FFFFFF", dash_a)
        ctx.move_to(cx, cy - r - 20)
        ctx.line_to(cx, cy + r + 20)
        ctx.stroke()
        ctx.set_dash([])
    la = prog(t, 4.6, 5.3)
    if la > 0:
        for x0, sgn in ((lx, -1), (rx, 1)):
            rrect(ctx, x0 + sgn * r * 0.5 - 70, yy - 52, 140, 104, 24, "#FFFFFF", 0.9 * la)
            v6.R.fraction(ctx, x0 + sgn * r * 0.5, yy, 46, la)
        text(ctx, "same size", cx, yy - r - 50 + 260 * share * 0, 50, "#6E8460", la * (1 - share))
        sparkles(ctx, cx, yy, r + 60, la * (1 - prog(t, 6.0, 6.8)), 0.2)
    sq = prog(t, 6.4, 7.4)
    if sq > 0:
        R.squirrel(ctx, 150, lerp(2400, 2150, sq), 2.0, SAGE, f=1, arm_up=0.6 * share, seed=0.7)
        R.squirrel(ctx, 930, lerp(2400, 2150, sq), 2.0, OCHRE, f=-1, arm_up=0.6 * share, seed=2.0)


def recap_row(ctx, y, a, icon, lines):
    if a <= 0:
        return
    rrect(ctx, 110, y, 860, 250, 36, "#FFFFFF", 0.94 * a)
    icon(ctx, 250, y + 125, a)
    for i, s in enumerate(lines):
        text(ctx, s, 640, y + 125 + (i - (len(lines) - 1) / 2) * 64, 50, INK, a)


def icon_equal(ctx, x, y, a):
    R.ribbon(ctx, x - 90, x + 90, y - 34, th=28, a=a)
    R.ribbon(ctx, x - 90, x + 90, y + 34, th=28, a=a)
    ctx.set_dash([10, 8])
    ctx.set_line_width(4)
    src(ctx, "#6E8460", a)
    for xx in (x - 90, x + 90):
        ctx.move_to(xx, y - 70)
        ctx.line_to(xx, y + 70)
    ctx.stroke()
    ctx.set_dash([])


def icon_fold(ctx, x, y, a):
    R.ribbon(ctx, x - 100, x + 40, y + 10, th=28, a=a)
    R.ribbon(ctx, x - 100, x + 40, y - 22, th=28, color="#6E90AC", a=a)
    ctx.set_line_width(6)
    src(ctx, "#9C7429", a)
    ctx.arc(x + 40, y - 6, 34, -math.pi / 2, math.pi / 2)
    ctx.stroke()
    R.glow(ctx, x + 40, y - 6, 60, OCHRE, a)


def icon_home(ctx, x, y, a):
    src(ctx, "#C98B6B", a)
    ctx.move_to(x - 80, y - 10)
    ctx.line_to(x, y - 80)
    ctx.line_to(x + 80, y - 10)
    ctx.close_path()
    ctx.fill()
    rrect(ctx, x - 62, y - 14, 124, 92, 8, "#E9D9A6", a)
    rrect(ctx, x - 16, y + 24, 32, 54, 6, "#9A7350", a)


def scene_recap(ctx, t):
    v6.R.table_top(ctx)
    a0 = prog(t, 0.0, 0.6)
    rrect(ctx, 300, 700, 480, 130, 50, OCHRE, a0)
    text(ctx, "Remember", W / 2, 765, 70, "#FFFFFF", a0)
    recap_row(ctx, 880, prog(t, 0.3, 0.9), icon_equal, ["Half means", "2 equal parts"])
    recap_row(ctx, 1160, prog(t, 3.3, 3.9), icon_fold, ["Fold end to end", "to find the middle"])
    recap_row(ctx, 1440, prog(t, 7.0, 7.6), icon_home, ["Try it at home:", "string or paper"])
    R.bramble(ctx, 200, 2090 - 18 * abs(math.sin(t * 1.4)) * prog(t, 0.3, 1.0), 2.6, 1, glass=False,
              look=0.5)


SCENES = [
    (0.0, 3.0, lambda c, lt: v6.scene_open(c, lt)),
    (3.0, 14.0, lambda c, lt: scene_ctx(c, lt)),
    (14.0, 20.0, lambda c, lt: v6.scene_b6(c, lt)),
    (20.0, 26.0, lambda c, lt: v6.scene_c6(c, lt)),
    (26.0, 33.0, lambda c, lt: v6.scene_d6(c, lt)),
    (33.0, 45.5, lambda c, lt: R.scene_e(c, lt, 0.6, 3.8, 9.0)),
    (45.5, 50.9, lambda c, lt: v6.scene_f6(c, lt)),
    (50.9, 60.5, lambda c, lt: R.scene_g(c, lt, 0.4, 2.0, 7.6)),
    (60.5, 68.5, lambda c, lt: R.scene_h(c, lt, 1.8)),
    (68.5, 78.8, lambda c, lt: scene_recap(c, lt)),
    (78.8, 82.0, lambda c, lt: R.scene_i(c, lt)),
    (82.0, TOTAL, lambda c, lt: v6.scene_loop(c, lt)),
]
XF = 0.6


def draw_frame(ctx, t):
    R.NOW[0] = t + v6.IDLE0
    for i, (a, b, fn) in enumerate(SCENES):
        if a <= t < b or (i == len(SCENES) - 1 and t >= a):
            ctx.save()
            fn(ctx, t - a)
            ctx.restore()
            if i + 1 < len(SCENES) and t > b - XF:
                na, _, nfn = SCENES[i + 1]
                ctx.push_group()
                ctx.save()
                nfn(ctx, max(0.0, t - na))
                ctx.restore()
                ctx.pop_group_to_source()
                ctx.paint_with_alpha(ease((t - (b - XF)) / XF))
            break
    R.NOW[0] = t + v6.IDLE0
    ka = prog(t, 38.4, 38.9) * (1 - prog(t, 41.6, 42.1))
    if ka > 0:
        rrect(ctx, 150, 1220, 780, 190, 40, "#FFFFFF", 0.94 * ka)
        text(ctx, "Ends match, so both", W / 2, 1282, 50, INK, ka)
        text(ctx, "sides are the same length", W / 2, 1350, 50, INK, ka)
    for s, e, cx, cy, lines, tx, ty in BUBBLES:
        a = prog(t, s - 0.1, s + 0.25) * (1 - prog(t, e - 0.2, e + 0.15))
        v6.bubble(ctx, cx, cy, lines, tx, ty, a)


def load(path):
    with wave.open(path) as w:
        assert w.getframerate() == SR
        raw, width = w.readframes(w.getnframes()), w.getsampwidth()
    d = (np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0) if width == 2 \
        else np.frombuffer(raw, dtype=np.float32)
    nz = np.where(np.abs(d) > 0.005)[0]
    d = d[max(0, nz[0] - 240): nz[-1] + 1200]
    return d / (np.max(np.abs(d)) + 1e-9) * 0.8


def build_audio():
    import narration as Nn
    n = int(TOTAL * SR)
    voice = np.zeros(n, dtype=np.float32)
    timings = []
    for start, who, path, line in LINES:
        clip = load(path)
        a = int(start * SR)
        b = min(n, a + len(clip))
        voice[a:b] += clip[: b - a]
        timings.append({"who": who, "text": line, "start": start, "end": round(b / SR, 2)})
    for p, q in zip(timings, timings[1:]):
        assert p["end"] <= q["start"] + 0.05, f"overlap: {p['text']} / {q['text']}"
    sfx = np.zeros(n, dtype=np.float32)

    def put(clip, at):
        a = int(at * SR)
        b = min(n, a + len(clip))
        sfx[a:b] += clip[: b - a].astype(np.float32)

    put(Nn.chime(784), 0.05)
    put(Nn.pop(), 3.1)                       # Today's case card
    put(Nn.snip(), 6.45)                     # cookie splits
    put(Nn.chime(880, 1.2), 7.7)             # two equal halves
    put(Nn.whoosh(1.0), 9.8)                 # shared out
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
    mix = voice + Nn.pad_track(n) + sfx
    f = int(0.3 * SR)
    mix[-f:] *= np.linspace(1, 0, f)
    mix = np.clip(mix, -1, 1)
    with wave.open("audio_v7_raw.wav", "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", "audio_v7_raw.wav", "-af",
                    "highpass=f=70,loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000", "audio_v7.wav"], check=True)
    json.dump(timings, open("timings_v7.json", "w"), indent=1)

    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    names = {"N": "", "B": "BRAMBLE: ", "O": "OTTO: ", "I": "IVY: "}
    with open("captions_v7_en-AU.srt", "w") as fh:
        for k, r in enumerate(timings, 1):
            fh.write(f"{k}\n{ts(r['start'])} --> {ts(r['end'] + 0.3)}\n{names[r['who']]}{r['text']}\n\n")
    for r in timings:
        print(f"{r['start']:6.2f}-{r['end']:6.2f} {r['who']} {r['text']}")


def main():
    mode = sys.argv[1]
    if mode == "frames":
        for ts_ in sys.argv[2:]:
            surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
            ctx = cairo.Context(surf)
            src(ctx, R.CREAM)
            ctx.paint()
            draw_frame(ctx, float(ts_))
            surf.write_to_png(f"v7_{float(ts_):05.1f}.png")
        return
    if mode == "audio":
        build_audio()
        return
    n = int(TOTAL * FPS)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "audio_v7.wav",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart",
         "logic_detectives_short1_v7.mp4"], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    for i in range(n):
        ctx.identity_matrix()
        ctx.set_operator(cairo.OPERATOR_SOURCE)
        src(ctx, R.CREAM)
        ctx.paint()
        ctx.set_operator(cairo.OPERATOR_OVER)
        draw_frame(ctx, i / FPS)
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
    ff.stdin.close()
    ff.wait()
    print("done", ff.returncode)


if __name__ == "__main__":
    main()
