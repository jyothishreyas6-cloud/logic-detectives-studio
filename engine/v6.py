"""Short 1 v6 (Concept B, 58 s): character voices, problem-first opening, A/B prediction.

Reuses drawing code from render.py (v5) and adds the new scenes, speech bubbles,
a new timeline, the audio mix and an SRT caption file.

  python3 v6.py frames 0 5 ...   -> check stills
  python3 v6.py audio            -> audio_v6.wav, timings_v6.json, captions_v6.srt
  python3 v6.py video            -> logic_detectives_short1_v6.mp4
"""
import json
import math
import subprocess
import sys
import wave

import cairo
import numpy as np

import render as R
from render import (W, H, FPS, INK, OCHRE, SAGE, RIBBON, RIBBON_D, SPINE_D, ellipse, rrect, text,
                    src, prog, clamp, ease, lerp, glow, sparkles)

TOTAL = 58.0
SR = 24000
LINE_DIR = "/mnt/user-data/uploads/Videos/Logic Detectives/kokoro/v6_lines"

# (start s, speaker, text) - speaker N narrator, B Bramble, O Otto, I Ivy
LINES = [
    (0.3, "N", "Is this really half?"),
    (3.3, "O", "One ribbon, two kites. I'll cut it right here!"),
    (6.3, "I", "Wait. Is that the middle?"),
    (9.4, "N", "If the mark isn't in the middle, one piece will be longer."),
    (15.4, "B", "Let's not guess. Let's test."),
    (18.1, "N", "What do you think? A, or B?"),
    (25.8, "B", "Ends together."),          # file line06, placed after the fold motion
    (22.4, "N", "Bring one end to meet the other."),
    (28.2, "N", "The fold shows the middle."),
    (31.2, "N", "The middle is here. Otto's mark is over there. It's B!"),
    (34.7, "O", "Oops. My mark was too far."),
    (36.6, "N", "Cut at the fold."),
    (38.6, "N", "Line them up."),
    (41.4, "N", "Ten centimetres, and ten centimetres."),
    (44.0, "N", "Same length!"),
    (46.4, "I", "They match!"),
    (47.8, "N", "Two equal pieces. Each one is a half."),
    (51.0, "O", "Yay!"),
    (54.2, "N", "Next case: four pieces. Are they fair?"),
]

# speech bubbles: (start, end, cx, cy, [lines], tail_x, tail_y)
BUBBLES = [
    (3.3, 6.0, 640, 830, ["One ribbon, two kites.", "I'll cut it right here!"], 900, 1040),
    (6.3, 8.4, 420, 830, ["Wait. Is that", "the middle?"], 200, 1040),
    (15.4, 18.0, 560, 820, ["Let's not guess.", "Let's test."], 520, 1080),
    (25.8, 27.6, 560, 1460, ["Ends together."], 420, 1690),
    (34.7, 36.4, 640, 1460, ["Oops. My mark", "was too far."], 900, 1650),
    (46.4, 47.9, 360, 1150, ["They match!"], 250, 1330),
    (51.0, 52.4, 760, 1150, ["Yay!"], 850, 1330),
]

TAIL = R.TAIL


# ---------- new drawing pieces ----------
def bubble(ctx, cx, cy, lines, tx, ty, a):
    if a <= 0:
        return
    size = 46
    ctx.select_font_face(R.FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    w = max(ctx.text_extents(s)[2] for s in lines) + 70
    h = len(lines) * 62 + 40
    x0, y0 = cx - w / 2, cy - h / 2
    src(ctx, "#FFFFFF", 0.95 * a)
    ctx.move_to(clamp(tx, x0 + 40, x0 + w - 40) - 22, y0 + h - 2)
    ctx.line_to(tx, ty)
    ctx.line_to(clamp(tx, x0 + 40, x0 + w - 40) + 22, y0 + h - 2)
    ctx.close_path()
    ctx.fill()
    rrect(ctx, x0, y0, w, h, 36, "#FFFFFF", 0.95 * a)
    for i, s in enumerate(lines):
        text(ctx, s, cx, y0 + 50 + i * 62, size, INK, a)


def kite_tail(ctx, x, y, t, length):
    pts = [(x + 10 * math.sin(f * 2 * math.pi + t * 1.6) * f, y + length * f)
           for f in (i / 40 for i in range(41))]
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(16)
    src(ctx, RIBBON)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.stroke()
    for k in (14, 28):
        bx, by = pts[k]
        ellipse(ctx, bx - 12, by, 11, 6, RIBBON_D)
        ellipse(ctx, bx + 12, by, 11, 6, RIBBON_D)
    return pts[-1]


def scene_open(ctx, t):
    """Frame 1 shows the problem: two kites, one tail long, one short, under Bramble's glass."""
    R.garden(ctx, -220)
    ky = 640 + 8 * math.sin(t * 0.9)
    sway = 0.04 * math.sin(t * 0.7)
    ends = []
    for kx, col, sw, ln in ((400, "#E7B98C", sway, TAIL * 1.4), (680, "#B9C9DE", -sway, TAIL * 0.6)):
        bx, by = kx - 80 * 1.15 * math.sin(sw), ky + 80 * 1.15 * math.cos(sw)
        ends.append(kite_tail(ctx, bx, by, t, ln))
        R.kite(ctx, kx, ky, 1.15, col, sw, tail=False)
    ax, ay = R.squirrel(ctx, 220, 1560, 1.3, SAGE, f=1, arm_up=1.0, arm_out=0.2, seed=0.7)
    bx2, by2 = R.squirrel(ctx, 860, 1560, 1.3, OCHRE, f=-1, arm_up=1.0, arm_out=0.2, seed=2.0)
    ctx.set_line_width(2.5)
    src(ctx, "#7A6E62", 0.8)
    ctx.move_to(ax, ay)
    ctx.line_to(400, ky)
    ctx.move_to(bx2, by2)
    ctx.line_to(680, ky)
    ctx.stroke()
    # Bramble's magnifying glass over the short tail
    gx, gy = ends[1][0] + 10, ends[1][1] - 40
    ellipse(ctx, gx, gy, 92, 92, "#DCEAF0", 0.35)
    ctx.set_line_width(16)
    src(ctx, "#9A7350")
    ctx.arc(gx, gy, 92, 0, 2 * math.pi)
    ctx.stroke()
    ctx.set_line_width(26)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(gx + 66, gy + 66)
    ctx.line_to(gx + 170, gy + 170)
    ctx.stroke()
    R.bramble(ctx, 620, 1960, 2.4, -1, glass=False, look=1.0)
    # labels and the question, visible from the very first frame
    text(ctx, "long", 290, ends[0][1] - 140, 44, "#6E8460")
    text(ctx, "short", ends[1][0] + 150, ends[1][1] - 120, 44, "#9C7429")
    rrect(ctx, 340, 170, 400, 170, 40, "#FFFFFF", 0.92)
    text(ctx, "Half?", W / 2, 255, 110, INK)


def scene_b6(ctx, t):
    ox = -160
    z = 1.38 + 0.06 * prog(t, 0.0, 6.0)
    ctx.save()
    R.zoom_table(ctx, z)
    R.garden(ctx, ox)
    R.garden_people(ctx, t, ox, "b")
    R.garden_table(ctx, ox)
    R.ribbon(ctx, 400 + ox, 1020 + ox, 1166, th=22)
    R.pencil_mark(ctx, 770 + ox, 1166 - 4)
    ctx.restore()
    R.case_badge(ctx, prog(t, 0.0, 0.6) * (1 - prog(t, 2.6, 3.2)))


def scene_c6(ctx, t):
    """Ivy's 'what if': the ribbon splits at Otto's mark into a long and a short piece."""
    ox = -160
    ctx.save()
    R.zoom_table(ctx, 1.44)
    R.garden(ctx, ox)
    R.garden_people(ctx, t, ox, "c")
    R.garden_table(ctx, ox)
    sp = prog(t, 0.8, 2.0)
    gap, lift = 14 * sp, 34 * sp
    a_ghost = 1.0 - 0.35 * sp
    R.ribbon(ctx, 400 + ox, 770 + ox - gap, 1166 - lift, th=22, a=a_ghost)
    R.ribbon(ctx, 770 + ox + gap, 1020 + ox, 1166 - lift, th=22, a=a_ghost)
    if sp < 0.5:
        R.pencil_mark(ctx, 770 + ox, 1166 - 4)
    a = prog(t, 2.2, 3.2)
    if a > 0:
        for x1, x2, col in ((400, 770, SAGE), (770, 1020, OCHRE)):
            ctx.set_line_width(7)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            src(ctx, col, a)
            ctx.move_to(x1 + ox + 6, 1112)
            ctx.line_to(x1 + ox + 6, 1086)
            ctx.line_to(x2 + ox - 6, 1086)
            ctx.line_to(x2 + ox - 6, 1112)
            ctx.stroke()
        text(ctx, "longer", (400 + 770) / 2 + ox, 1052, 36, "#6E8460", a)
        text(ctx, "shorter", (770 + 1020) / 2 + ox, 1052, 36, "#9C7429", a)
    ctx.restore()


def choice_card(ctx, x, label, caption, mark_frac, a, picked=0.0, dim=0.0):
    w, h, y = 420, 330, 300
    rrect(ctx, x, y, w, h, 34, "#FFFFFF", 0.93 * a)
    if picked > 0:
        ctx.set_line_width(10)
        src(ctx, "#6E8460", picked * a)
        R.rrect  # noqa: keep namespace
        ctx.new_sub_path()
        r = 34
        ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
        ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
        ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
        ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
        ctx.close_path()
        ctx.stroke()
    fade = a * (1 - 0.55 * dim)
    ellipse(ctx, x + 60, y + 60, 36, 36, OCHRE if label == "A" else SAGE, fade)
    text(ctx, label, x + 60, y + 62, 46, "#FFFFFF", fade)
    rx1, rx2, ry = x + 50, x + w - 50, y + 165
    R.ribbon(ctx, rx1, rx2, ry, th=26, a=fade)
    mx = lerp(rx1, rx2, mark_frac)
    ctx.set_line_width(5)
    src(ctx, "#4B4B4B", fade)
    ctx.move_to(mx, ry - 40)
    ctx.line_to(mx, ry - 16)
    ctx.stroke()
    if label == "B":
        text(ctx, "?", (rx1 + rx2) / 2, ry + 50, 46, "#6E8460", fade)
    text(ctx, caption[0], x + w / 2, y + 255, 34, INK, fade)
    text(ctx, caption[1], x + w / 2, y + 295, 34, INK, fade)
    if picked > 0:
        ellipse(ctx, x + w - 50, y + 50, 34, 34, "#6E8460", picked * a)
        ctx.set_line_width(9)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        src(ctx, "#FFFFFF", picked * a)
        ctx.move_to(x + w - 66, y + 50)
        ctx.line_to(x + w - 54, y + 63)
        ctx.line_to(x + w - 33, y + 37)
        ctx.stroke()


def ab_cards(ctx, a, picked=0.0):
    choice_card(ctx, 90, "A", ("Otto's mark is", "the middle"), 0.5, a, dim=picked)
    choice_card(ctx, 570, "B", ("The middle is", "somewhere else"), 0.62, a, picked=picked)


def scene_d6(ctx, t):
    R.scene_d(ctx, t, 999.0)   # Bramble walks in; the old thought bubble is switched off
    a = prog(t, 2.7, 3.3) * (1 - prog(t, 6.4, 7.0))
    ab_cards(ctx, a)
    if a > 0:   # 3-second think ring below the cards
        cx, cy = W / 2, 760
        fill = clamp((t - 4.0) / 3.0)
        rrect(ctx, cx - 210, cy - 70, 420, 140, 60, "#FFFFFF", 0.9 * a)
        ctx.set_line_width(12)
        src(ctx, "#E6DAC4", a)
        ctx.arc(cx - 130, cy, 44, 0, 2 * math.pi)
        ctx.stroke()
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        src(ctx, SAGE, a)
        ctx.arc(cx - 130, cy, 44, -math.pi / 2, -math.pi / 2 + 2 * math.pi * fill)
        ctx.stroke()
        text(ctx, "Pause", cx + 50, cy - 22, 40, INK, a)
        text(ctx, "and think", cx + 50, cy + 26, 40, INK, a)


def scene_f6(ctx, t):
    ctx.save()
    R.scene_f(ctx, t, 0.2, 0.4, 1.4)
    ctx.restore()
    hop = 0.0
    R.squirrel(ctx, 960, 2060 - hop, 2.4, OCHRE, f=-1, arm_up=0.0, tilt=-0.1 * prog(t, 3.5, 4.0), seed=2.0)
    pick = prog(t, 2.6, 3.2)
    a = prog(t, 2.4, 2.9) * (1 - prog(t, 4.6, 5.2))
    if a > 0:
        ctx.save()
        ctx.translate(W / 2, 300)
        ctx.scale(0.62, 0.62)
        ctx.translate(-W / 2, -300)
        ab_cards(ctx, a, picked=pick)
        ctx.restore()


def scene_loop(ctx, t):
    keep = R.NOW[0]
    R.NOW[0] = IDLE0    # identical to frame 1 so the Short loops cleanly
    scene_open(ctx, 0.0)
    R.NOW[0] = keep


SCENES = [
    (0.0, 3.0, lambda c, lt: scene_open(c, lt)),
    (3.0, 9.0, lambda c, lt: scene_b6(c, lt)),
    (9.0, 15.0, lambda c, lt: scene_c6(c, lt)),
    (15.0, 22.0, lambda c, lt: scene_d6(c, lt)),
    (22.0, 31.0, lambda c, lt: R.scene_e(c, lt, 0.6, 3.8, 6.2)),
    (31.0, 36.4, lambda c, lt: scene_f6(c, lt)),
    (36.4, 46.0, lambda c, lt: R.scene_g(c, lt, 0.4, 2.0, 7.6)),
    (46.0, 54.0, lambda c, lt: R.scene_h(c, lt, 1.8)),
    (54.0, 57.2, lambda c, lt: R.scene_i(c, lt)),
    (57.2, TOTAL, lambda c, lt: scene_loop(c, lt)),
]
XF = 0.6


IDLE0 = 1.0  # idle-animation clock offset: frame 1 lands mid-breath with eyes open


def draw_frame(ctx, t):
    R.NOW[0] = t + IDLE0
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
    R.NOW[0] = t + IDLE0
    for s, e, cx, cy, lines, tx, ty in BUBBLES:
        a = prog(t, s - 0.1, s + 0.25) * (1 - prog(t, e - 0.2, e + 0.15))
        bubble(ctx, cx, cy, lines, tx, ty, a)


# ---------- audio ----------
def load_line(i):
    with wave.open(f"{LINE_DIR}/line{i:02d}.wav") as w:
        assert w.getframerate() == SR
        raw, width = w.readframes(w.getnframes()), w.getsampwidth()
    d = (np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0) if width == 2 \
        else np.frombuffer(raw, dtype=np.float32)
    nz = np.where(np.abs(d) > 0.005)[0]
    d = d[max(0, nz[0] - 240): nz[-1] + 1200]
    return d / (np.max(np.abs(d)) + 1e-9) * 0.8


def build_audio():
    import narration as Nn
    Nn.SR = SR
    n = int(TOTAL * SR)
    voice = np.zeros(n, dtype=np.float32)
    timings = []
    for i, (start, who, line) in enumerate(LINES):
        clip = load_line(i)
        a = int(start * SR)
        b = min(n, a + len(clip))
        voice[a:b] += clip[: b - a]
        timings.append({"i": i, "who": who, "text": line, "start": start, "end": round(b / SR, 2)})
    timings.sort(key=lambda r: r["start"])
    for p, q in zip(timings, timings[1:]):
        assert p["end"] <= q["start"] + 0.05, f"overlap: {p['text']} / {q['text']}"
    sfx = np.zeros(n, dtype=np.float32)

    def put(clip, at):
        a = int(at * SR)
        b = min(n, a + len(clip))
        sfx[a:b] += clip[: b - a].astype(np.float32)

    put(Nn.chime(784), 0.05)                # frame-1 chime
    put(Nn.snip(), 3.6)                     # Otto's scissors
    put(Nn.whoosh(1.0), 9.8)                # what-if split
    for k in range(7):
        put(Nn.step(), 15.1 + k * 0.33)     # Bramble walks in
    put(Nn.pop(), 17.8)                     # cards appear
    put(Nn.chime(660, 1.2), 22.0)           # think ring completes
    put(Nn.chime(880), 28.3)                # fold shows the middle
    put(Nn.chime(1047, 1.4), 34.1)          # "It's B!"
    put(Nn.snip(), 37.3)
    put(Nn.snip(), 37.55)
    put(Nn.chime(988), 44.05)               # same length
    put(Nn.whoosh(), 46.1)                  # kites lift
    put(Nn.chime(1175, 2.0), 49.6)          # each one is a half
    mix = voice + Nn.pad_track(n) * (n / (Nn.TOTAL * SR) if False else 1.0) + sfx
    f = int(0.3 * SR)
    mix[-f:] *= np.linspace(1, 0, f)
    mix = np.clip(mix, -1, 1)
    with wave.open("audio_v6_raw.wav", "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", "audio_v6_raw.wav", "-af",
                    "highpass=f=70,loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000", "audio_v6.wav"], check=True)
    json.dump(timings, open("timings_v6.json", "w"), indent=1)

    def ts(x):
        ms = int(round(x * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    names = {"N": "", "B": "BRAMBLE: ", "O": "OTTO: ", "I": "IVY: "}
    with open("captions_v6_en-AU.srt", "w") as fh:
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
            surf.write_to_png(f"v6_{float(ts_):05.1f}.png")
        return
    if mode == "audio":
        build_audio()
        return
    n = int(TOTAL * FPS)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "audio_v6.wav",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart",
         "logic_detectives_short1_v6.mp4"], stdin=subprocess.PIPE)
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
