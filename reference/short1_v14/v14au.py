"""Short 1 v14: engagement update on the v13 layout.

New: "Case open!" opening, fairness hook ("Hey! That's not fair!"), lamington example,
Bramble asks the viewer ("Can you point to the middle?" + 4 s), "Case solved!" stamp,
Otto's scarf gag, "Say it with me" recap with a 2 s child's turn, facial expressions,
read-along caption strip (replaces speech bubbles), music only in silent gaps, no pad under speech.

  python3 v14.py audio | frames 0 5 ... | video | cut
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
import v7
import v8
import v9
import v12
import v13                      # sets the v13 scene list, cue list and poses (we extend them)
import scenes13 as S
import scenes14 as S14
import rig14 as rig
from render import W, H, FPS, INK, OCHRE, SAGE, rrect, text, src, prog, ease, clamp

rig.install()
R._rig = rig
SR = 24000
D12 = "/mnt/user-data/uploads/Videos/Logic Detectives/kokoro/v12_lines"
D14 = "/mnt/user-data/uploads/Videos/Logic Detectives/kokoro/v14_lines"

# (who, text, file, old-timeline anchor, silence after)
LINES = [
    ("B", "Case open!", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l00.wav", 0.05, 0.4),
    ("O", "Hey! That's not fair!", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l01.wav", 0.5, 0.6),
    ("N", "Is this really half?", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l02.wav", 1.0, 1.0),
    ("N", "Today's case: what is a half?", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l03.wav", 3.3, 0.8),
    ("N", "Half means two pieces. Both pieces are the same size.", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l04.wav", 5.9, 1.5),
    ("N", "Like a lamington for two friends. Each friend gets the same.", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l05.wav", 9.7, 1.5),
    ("O", "One ribbon, two kites. I'll cut it right here!", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l06.wav", 14.3, 0.8),
    ("I", "Wait. Is that the middle?", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l07.wav", 17.3, 1.0),
    ("N", "The mark might not be in the middle. Then one piece is longer.", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l08.wav", 20.4, 1.5),
    ("B", "Let's not guess. Let's test.", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l09.wav", 26.4, 0.8),
    ("N", "A. At Otto's mark.", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l10.wav", 29.1, 0.6),
    ("N", "B. Somewhere else.", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l11.wav", 29.5, 0.6),
    ("N", "Pause and think.", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l12.wav", 29.9, 5.4),
    ("B", "Can you point to the middle?", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l13.wav", 33.05, 4.4),
    ("N", "Watch the ends. Bring one end to meet the other.", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l14.wav", 33.4, 1.0),
    ("B", "Ends together.", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l15.wav", 36.8, 0.8),
    ("N", "The two ends match. So both sides are the same length.", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l16.wav", 38.5, 1.5),
    ("N", "The fold shows the middle.", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l17.wav", 42.0, 1.5),
    ("N", "The middle is here. Otto's mark is over there. It's B!", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l18.wav", 45.7, 0.8),
    ("O", "Oops. My mark was too far.", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l19.wav", 49.2, 1.0),
    ("N", "Cut at the fold.", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l20.wav", 51.1, 0.8),
    ("N", "Line them up.", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l21.wav", 53.1, 1.0),
    ("N", "Ten centimetres, and ten centimetres.", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l22.wav", 55.9, 0.8),
    ("N", "Same length!", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l23.wav", 58.5, 0.8),
    ("B", "Case solved!", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l24.wav", 59.6, 1.8),
    ("I", "They match!", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l25.wav", 60.9, 0.8),
    ("N", "Two equal pieces. Equal means the same. Each one is a half.", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l26.wav", 62.3, 1.0),
    ("O", "Yay!", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l27.wav", 65.5, 0.6),
    ("O", "Oops! Who turned off the lights?", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l28.wav", 66.3, 1.4),
    ("N", "Remember. Say it with me.", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l29.wav", 68.8, 0.5),
    ("N", "Half means...", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l30.wav", 69.6, 2.2),
    ("N", "two equal parts!", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l31.wav", 70.4, 1.5),
    ("N", "To find the middle, fold it end to end.", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l32.wav", 71.8, 1.5),
    ("N", "Try it at home. Use string or paper.", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l33.wav", 75.5, 1.0),
    ("N", "Next case: four pieces. Are they fair?", f"/home/claude/logic-detectives-studio/episodes/ep001_is_this_really_half/lines/l34.wav", 79.0, 0.6),
]
STRIP_HIDDEN = {3, 16, 24, 30, 31, 32, 33}     # a card already shows these words
CHILD_TURN = 30                                 # the 2 s gap after this line is for the child
I_THINK, I_ASK, I_SOLVED, I_GAG = 12, 13, 24, 28


def load(path):
    with wave.open(path) as w:
        sr = w.getframerate()
        raw, width = w.readframes(w.getnframes()), w.getsampwidth()
    d = (np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0) if width == 2 \
        else np.frombuffer(raw, dtype=np.float32)
    if sr != SR:
        x = np.linspace(0, 1, int(len(d) * SR / sr))
        d = np.interp(x, np.linspace(0, 1, len(d)), d).astype(np.float32)
    nz = np.where(np.abs(d) > 0.005)[0]
    d = d[max(0, nz[0] - 240): nz[-1] + 1200]
    return d / (np.max(np.abs(d)) + 1e-9) * 0.8


def plan():
    clips = [load(p) for _, _, p, _, _ in LINES]
    rows, anchors = [], [(0.0, 0.0)]
    s = 0.35
    for i, ((who, line, _, old, gap), clip) in enumerate(zip(LINES, clips)):
        if i:
            pold, pgap = LINES[i - 1][3], LINES[i - 1][4]
            s = max(rows[-1]["end"] + pgap, rows[-1]["start"] + (old - pold))
        e = s + len(clip) / SR
        rows.append({"who": who, "text": line, "start": round(s, 3), "end": round(e, 3)})
        anchors.append((s, old))
        if i == I_THINK:
            anchors.append((e + 5.0, 33.0))
        if i == I_ASK:
            anchors.append((e + 4.0, 33.3))
    last = rows[-1]["end"]
    anchors += [(last + 0.6, 82.0), (last + 1.6, 83.0)]
    return rows, clips, anchors, last + 1.6


ROWS, CLIPS, ANCH, TOTAL = plan()
AN_NEW, AN_OLD = [a for a, _ in ANCH], [b for _, b in ANCH]


def to_old(T):
    return float(np.interp(T, AN_NEW, AN_OLD))


def to_new(t):
    return float(np.interp(t, AN_OLD, AN_NEW))


# ---------------------------------------------------------------- scenes, cues, poses
v7.SCENES[0] = (0.0, 3.0, lambda c, lt: S14.scene_open(c, lt))
v7.SCENES[1] = (3.0, 14.0, lambda c, lt: S14.scene_ctx(c, lt))
v7.SCENES[8] = (60.5, 68.5, lambda c, lt: S14.scene_kites(c, lt))
v7.SCENES[9] = (68.5, 78.8, lambda c, lt: S14.scene_recap(c, lt))
v7.SCENES[11] = (82.0, 83.0, lambda c, lt: S14.scene_loop(c, lt))


def cue_new(c):
    c = list(c)
    if c[0] == "ring":
        c[7] = ""
    elif c[0] == "lens":
        c[9] = ""
    else:
        c[6] = ""
    c[1], c[2] = to_new(c[1]), to_new(c[2])
    return tuple(c)


CUES = [cue_new(c) for c in v13.CUES_OLD]
_stamp_at = ROWS[I_SOLVED]["start"] - 0.35       # one focus at a time: cues end before the stamp
CUES = [c[:2] + (min(c[2], _stamp_at),) + c[3:] if c[1] < _stamp_at < c[2] else c for c in CUES]
# the halves ring follows the lamington halves
CUES[2] = ("ring", CUES[2][1], CUES[2][2], 540, S.HALF_Y - 20, 240, 170, "", 0, 0)


_base_poses = v13.poses


def poses(t):
    P = _base_poses(t)
    O, I, B = P["O"], P["I"], P["B"]
    T = to_new(t)

    def during(i, pre=0.2, post=0.6):
        r = ROWS[i]
        return r["start"] - pre <= T <= r["end"] + post

    if t < 3.0 or t >= 82.0:
        O["expr"] = "sad"
        B["expr"] = "think"
        I["expr"] = None
    elif t < 14.0:
        if t > 9.5:
            O["expr"] = I["expr"] = "happy"
    elif t < 26.0:
        if during(6):
            O["expr"] = "happy"
        if during(7, post=1.5):
            I["expr"] = "think"
        if t >= 20.0:
            O["expr"] = "think"
    elif t < 33.0:
        I["expr"] = "think"
        O["expr"] = "happy"
        if T <= ROWS[I_THINK]["end"] + 5.0 and T >= ROWS[10]["start"]:
            B["expr"] = "think"
    elif t < 45.5:
        if during(I_ASK, post=4.0):
            B["expr"] = "think"
        if t >= 42.0:
            O["expr"] = "surprise"
            B["expr"] = "happy"
    elif t < 50.9:
        B["expr"] = "think" if t < 48.0 else "happy"
        if t >= 49.0:
            O["expr"] = "surprise"
    elif t < 60.5:
        if t >= 58.3:
            O["expr"] = B["expr"] = "happy"
    elif t < 68.5:
        I["expr"] = O["expr"] = "happy"
        r = ROWS[I_GAG]
        k = clamp((T - (r["start"] - 0.6)) / 0.4) * (1 - clamp((T - (r["end"] + 0.6)) / 0.4))
        if k > 0:
            O["blind"] = k
            O["expr"] = "surprise"
            O["jump"] = 0.0
    elif t < 78.8:
        B["expr"] = "happy"
    else:
        B["expr"] = "think"
    return P


rig.TALK = [(r["start"], r["end"], r["who"]) for r in ROWS if r["who"] in ("O", "I", "B")]
rig.TIME_OFFSET = v6.IDLE0
SCENE_SURF = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)


def draw_scenes(ctx, T, t):
    rig.POSE.clear()
    rig.POSE.update(poses(t))
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


# ---------------------------------------------------------------- overlays
STRIP_Y = H - S14.SHIFT
SPEAKER = {"N": ("#E9DCC4", "#7A6A55"), "B": ("#8B6A4E", "#FFFFFF"),
           "O": (OCHRE, "#FFFFFF"), "I": (SAGE, "#FFFFFF")}


def face_icon(ctx, x, y, who):
    """Tiny round face in the speaker's colour."""
    bg, fg = SPEAKER[who]
    R.ellipse(ctx, x, y, 44, 44, bg)
    if who in ("O", "I"):
        for ex in (-22, 22):
            src(ctx, bg)
            ctx.move_to(x + ex - 12, y - 30)
            ctx.line_to(x + ex * 1.3, y - 62)
            ctx.line_to(x + ex + 12, y - 34)
            ctx.close_path()
            ctx.fill()
    if who == "B":
        for k in range(7):
            a = math.pi + k * math.pi / 6
            src(ctx, "#6F5440")
            ctx.move_to(x + 38 * math.cos(a - 0.2), y + 38 * math.sin(a - 0.2))
            ctx.line_to(x + 58 * math.cos(a), y + 58 * math.sin(a))
            ctx.line_to(x + 38 * math.cos(a + 0.2), y + 38 * math.sin(a + 0.2))
            ctx.fill()
        R.ellipse(ctx, x, y, 44, 44, bg)
    R.ellipse(ctx, x - 14, y - 6, 5, 6, INK if who != "B" else "#2B211B")
    R.ellipse(ctx, x + 14, y - 6, 5, 6, INK if who != "B" else "#2B211B")
    ctx.set_line_width(4)
    src(ctx, INK)
    ctx.arc(x, y + 6, 13, 0.3, math.pi - 0.3)
    ctx.stroke()


def word_times(r):
    words = r["text"].split()
    weights = [max(2, len(w.strip(".,!?:"))) + 2 for w in words]
    tot = sum(weights)
    dur = r["end"] - r["start"]
    out, acc = [], r["start"]
    for w, k in zip(words, weights):
        out.append((w, acc))
        acc += dur * k / tot
    return out


def wrap(ctx, words, maxw):
    lines, cur = [], []
    for w in words:
        test = " ".join([x for x, _ in cur] + [w[0]])
        if cur and ctx.text_extents(test)[2] > maxw:
            lines.append(cur)
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(cur)
    return lines


def caption_strip(ctx, T):
    for i, r in enumerate(ROWS):
        if i in STRIP_HIDDEN:
            continue
        a = prog(T, r["start"] - 0.25, r["start"]) * (1 - prog(T, r["end"] + 0.5, r["end"] + 0.8))
        if a <= 0:
            continue
        y0 = STRIP_Y + 14
        rrect(ctx, 20, y0, W - 40, S14.SHIFT - 30, 34, "#FFFFFF", 0.96 * a)
        face_icon(ctx, 96, y0 + (S14.SHIFT - 30) / 2, r["who"])
        ctx.select_font_face(R.FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        size = 50
        ctx.set_font_size(size)
        lines = wrap(ctx, word_times(r), W - 220)
        if len(lines) > 2:
            size = 42
            ctx.set_font_size(size)
            lines = wrap(ctx, word_times(r), W - 220)
        lh = size * 1.2
        ytop = y0 + (S14.SHIFT - 30) / 2 - lh * (len(lines) - 1) / 2
        for li, ln in enumerate(lines):
            full = " ".join(w for w, _ in ln)
            x = 170 + (W - 210 - ctx.text_extents(full)[2]) / 2
            for w, ts in ln:
                said = T >= ts
                col = INK if said else "#A99D90"
                ctx.set_source_rgba(*R.rgb(col), a)
                ext = ctx.text_extents(w + " ")
                ctx.move_to(x, ytop + li * lh + size * 0.35)
                ctx.show_text(w + " ")
                if said and T < ts + 0.6:   # soft underline under the word being said
                    ctx.set_source_rgba(*R.rgb("#F2C85B"), a * (1 - (T - ts) / 0.6))
                    ctx.rectangle(x, ytop + li * lh + size * 0.5, ext[4] - 12, 6)
                    ctx.fill()
                x += ext[4]
        return


def case_open(ctx, T):
    """Magnifying glass sweeps across the frame (0.15 to 1.75 s)."""
    p = prog(T, 0.15, 1.75)
    if p <= 0 or p >= 1:
        return
    lx = -260 + (W + 520) * ease(p)
    ly = 880 + 60 * math.sin(p * math.pi)
    r = 150
    ctx.save()
    ctx.arc(lx, ly, r, 0, 2 * math.pi)
    ctx.clip()
    pat = cairo.SurfacePattern(SCENE_SURF)
    m = cairo.Matrix()
    m.translate(lx, ly)
    m.scale(1 / 1.35, 1 / 1.35)
    m.translate(-lx, -ly)
    pat.set_matrix(m)
    ctx.set_source(pat)
    ctx.paint()
    ctx.set_source_rgba(1, 1, 1, 0.12)
    ctx.arc(lx - r * 0.35, ly - r * 0.35, r * 0.45, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()
    ctx.set_line_width(22)
    src(ctx, "#9A7350")
    ctx.arc(lx, ly, r, 0, 2 * math.pi)
    ctx.stroke()
    ctx.set_line_width(30)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(lx + r * 0.72, ly + r * 0.72)
    ctx.line_to(lx + r * 1.5, ly + r * 1.5)
    ctx.stroke()


def paw_print(ctx, x, y, s, col, a):
    R.ellipse(ctx, x, y + 10 * s, 24 * s, 20 * s, col, a)
    for dx, dy in ((-24, -18), (-8, -30), (8, -30), (24, -18)):
        R.ellipse(ctx, x + dx * s, y + dy * s, 8 * s, 10 * s, col, a)


def stamp(ctx, T):
    r = ROWS[I_SOLVED]
    s0 = r["start"] - 0.15
    a = prog(T, s0, s0 + 0.35) * (1 - prog(T, r["end"] + 1.4, r["end"] + 1.9))
    if a <= 0:
        return
    k = 1.35 - 0.35 * ease(prog(T, s0, s0 + 0.35))
    cx, cy = W / 2, S14.TOP + 330
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(-0.08)
    ctx.scale(k, k)
    col = "#B4473E"
    rrect(ctx, -340, -95, 680, 190, 30, "#FFFFFF", 0.9 * a)
    ctx.set_line_width(10)
    ctx.set_source_rgba(*R.rgb(col), 0.9 * a)
    ctx.new_sub_path()
    rr = 30
    for (px, py, a0) in ((340 - rr, -95 + rr, -math.pi / 2), (340 - rr, 95 - rr, 0), (-340 + rr, 95 - rr, math.pi / 2), (-340 + rr, -95 + rr, math.pi)):
        ctx.arc(px, py, rr, a0, a0 + math.pi / 2)
    ctx.close_path()
    ctx.stroke()
    paw_print(ctx, -255, 6, 1.5, col, 0.9 * a)
    text(ctx, "Case solved!", 55, 0, 64, col, a)
    ctx.restore()


def draw_frame(ctx, T):
    t = to_old(T)
    sc = cairo.Context(SCENE_SURF)
    sc.set_operator(cairo.OPERATOR_SOURCE)
    src(sc, R.CREAM)
    sc.paint()
    sc.set_operator(cairo.OPERATOR_OVER)
    draw_scenes(sc, T, t)
    SCENE_SURF.flush()
    src(ctx, R.CREAM)
    ctx.paint()
    ctx.save()
    ctx.translate(0, -S14.SHIFT)
    ctx.save()
    zm = v13.v11.zoom_amount(t)
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
    for c in CUES:
        kind, s, e = c[0], c[1], c[2]
        if not (s <= T <= e):
            continue
        a = prog(T, s, s + 0.4) * (1 - prog(T, e - 0.35, e))
        if kind == "ring":
            v12.ring_only(ctx, c[3], c[4], c[5], c[6], a)
        elif kind == "lens":
            v9.lens(ctx, SCENE_SURF, *c[3:12], a)
    r16 = ROWS[16]
    ka = prog(T, r16["start"] - 0.2, r16["start"] + 0.3) * (1 - prog(T, r16["end"] + 0.7, r16["end"] + 1.2))
    if ka > 0:
        rrect(ctx, 70, v13.CARD_Y, 940, 190, 40, "#FFFFFF", 0.94 * ka)
        text(ctx, "The two ends match.", W / 2, v13.CARD_Y + 62, 50, INK, ka)
        text(ctx, "So both sides are the same length.", W / 2, v13.CARD_Y + 130, 50, INK, ka)
    case_open(ctx, T)
    stamp(ctx, T)
    ctx.restore()
    src(ctx, "#F3EBDD")
    ctx.rectangle(0, STRIP_Y, W, S14.SHIFT)
    ctx.fill()
    src(ctx, "#E3D6BF")
    ctx.rectangle(0, STRIP_Y, W, 4)
    ctx.fill()
    caption_strip(ctx, T)


# ---------------------------------------------------------------- audio
def bell(freq, dur=1.2, amp=0.5):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    env = np.exp(-tt * 3.2) * np.minimum(1, tt / 0.01)
    w = np.sin(2 * np.pi * freq * tt) + 0.3 * np.sin(2 * np.pi * freq * 2.01 * tt) * np.exp(-tt * 6)
    return (amp * env * w).astype(np.float32)


def thud():
    n = int(0.35 * SR)
    tt = np.arange(n) / SR
    w = np.sin(2 * np.pi * (110 - 60 * tt) * tt) * np.exp(-tt * 14)
    return (0.5 * w).astype(np.float32)


MOTIF = [523.25, 659.25, 783.99, 880.0, 783.99, 659.25, 587.33, 523.25]   # soft pentatonic tune


def build_audio():
    import narration as Nn
    n = int(TOTAL * SR)
    voice = np.zeros(n, dtype=np.float32)
    for r, clip in zip(ROWS, CLIPS):
        a = int(r["start"] * SR)
        b = min(n, a + len(clip))
        voice[a:b] += clip[: b - a]
    sfx = np.zeros(n, dtype=np.float32)

    def put(clip, at, gain=1.0):
        a = int(at * SR)
        b = min(n, a + len(clip))
        if a < n:
            sfx[a:b] += clip[: b - a].astype(np.float32) * gain

    # signature opening: soft two-note jingle and a gentle sweep
    put(bell(783.99, 1.0, 0.22), 0.12)
    put(bell(1046.5, 1.4, 0.22), 0.42)
    put(Nn.whoosh(1.0), 0.2, 0.5)
    # Foley for real actions (old timeline -> new)
    for at, clip in ((3.1, Nn.pop()), (6.45, Nn.snip()), (14.6, Nn.snip()), (28.8, Nn.pop()),
                     (51.8, Nn.snip()), (52.05, Nn.snip()), (68.6, Nn.pop())):
        put(clip, to_new(at), 0.8)
    for k in range(7):
        put(Nn.step(), to_new(26.1 + k * 0.33), 0.8)
    # Case solved stamp
    put(thud(), ROWS[I_SOLVED]["start"] - 0.12)
    put(bell(1174.66, 1.6, 0.18), ROWS[I_SOLVED]["start"] + 0.1)
    # look chimes
    ch = v9.look_chime()
    for c in CUES:
        put(ch, c[1] + 0.05)
    # melody only in silent gaps of 2 s or more (never under speech, never in the child's turn)
    music = np.zeros(n, dtype=np.float32)
    note_i = 0
    for i in range(len(ROWS) - 1):
        g0, g1 = ROWS[i]["end"] + 0.25, ROWS[i + 1]["start"] - 0.35
        if i == CHILD_TURN or g1 - g0 < 1.6:
            continue
        tt = g0
        while tt + 0.5 < g1:
            note = bell(MOTIF[note_i % len(MOTIF)] / 2, 1.0, 0.16)
            a = int(tt * SR)
            b = min(int(g1 * SR), a + len(note))
            music[a:b] += note[: b - a]
            note_i += 1
            tt += 0.5
        # fade out before the next line
        a, b = int((g1 - 0.4) * SR), int(g1 * SR)
        music[a:b] *= np.linspace(1, 0, b - a)
    mix = voice + sfx + music
    f = int(0.3 * SR)
    mix[-f:] *= np.linspace(1, 0, f)
    mix = np.clip(mix, -1, 1)
    with wave.open("audio_v14au_raw.wav", "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", "audio_v14au_raw.wav", "-af",
                    "highpass=f=70,loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000", "audio_v14au.wav"], check=True)
    json.dump(ROWS, open("timings_v14au.json", "w"), indent=1)
    write_srt(ROWS, "captions_v14au_en-AU.srt")
    for r in ROWS:
        print(f"{r['start']:6.2f}-{r['end']:6.2f} {r['who']} {r['text']}")
    print("TOTAL", round(TOTAL, 2))


def ts(x):
    ms = int(round(x * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write_srt(rows, path):
    names = {"N": "", "B": "BRAMBLE: ", "O": "OTTO: ", "I": "IVY: "}
    with open(path, "w") as fh:
        for k, r in enumerate(rows, 1):
            fh.write(f"{k}\n{ts(r['start'])} --> {ts(r['end'] + 0.4)}\n{names[r['who']]}{r['text']}\n\n")


# ---------------------------------------------------------------- 45 to 60 s discovery cut
def cut_segments():
    R_ = ROWS
    return [
        (0.0, R_[2]["end"] + 0.7),                       # Case open, not fair, is this really half?
        (R_[6]["start"] - 0.4, R_[7]["end"] + 0.8),      # I'll cut it right here / Wait. Is that the middle?
        (R_[14]["start"] - 0.4, R_[18]["end"] + 0.7),    # fold, ends match, the middle, It's B!
        (R_[I_SOLVED]["start"] - 0.5, R_[I_SOLVED]["end"] + 1.6),
        (R_[29]["start"] - 0.4, R_[31]["end"] + 1.0),    # Say it with me
        (R_[34]["start"] - 0.5, TOTAL),                  # teaser and loop
    ]


def build_cut():
    segs = cut_segments()
    XF = 0.4
    parts = []
    for k, (a, b) in enumerate(segs):
        out = f"cut_part{k}.mp4"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i",
                        "logic_detectives_short1_v14au.mp4", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-ar", "48000", out], check=True)
        parts.append((out, b - a))
    # chain gentle cross-dissolves
    inputs, fc, vlab, alab, off = [], [], "[0:v]", "[0:a]", 0.0
    for k, (p, d) in enumerate(parts):
        inputs += ["-i", p]
    off = parts[0][1] - XF
    for k in range(1, len(parts)):
        fc.append(f"{vlab}[{k}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[v{k}]")
        fc.append(f"{alab}[{k}:a]acrossfade=d={XF}[a{k}]")
        vlab, alab = f"[v{k}]", f"[a{k}]"
        off += parts[k][1] - XF
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc),
                    "-map", vlab, "-map", alab, "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
                    "logic_detectives_short1_v14au_cut.mp4"], check=True)
    # captions for the cut
    rows, base = [], 0.0
    for k, (a, b) in enumerate(segs):
        for r in ROWS:
            if r["start"] >= a and r["end"] <= b:
                rows.append({"who": r["who"], "text": r["text"],
                             "start": r["start"] - a + base, "end": r["end"] - a + base})
        base += (b - a) - XF
    write_srt(rows, "captions_v14au_cut_en-AU.srt")
    print("cut length", round(base + XF, 2))


def main():
    mode = sys.argv[1]
    if mode == "audio":
        build_audio()
        return
    if mode == "cut":
        build_cut()
        return
    if mode == "frames":
        for ts_ in sys.argv[2:]:
            surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
            ctx = cairo.Context(surf)
            draw_frame(ctx, float(ts_))
            surf.write_to_png(f"v14au_{float(ts_):05.1f}.png")
        return
    n = int(TOTAL * FPS)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "audio_v14au.wav",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart",
         "logic_detectives_short1_v14au.mp4"], stdin=subprocess.PIPE)
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
