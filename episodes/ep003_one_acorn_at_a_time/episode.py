"""Episode 003: One acorn at a time (Kindergarten, Maths, Representing whole numbers).

Setting: the back verandah table on a sunny afternoon, with a Hills Hoist and a gum tree in
the backyard. Otto and Ivy each gathered acorns. Ivy's sit in two neat rows of five. Otto's
lie in a loose ring, and he counts round the ring and back onto his first acorn: "eleven!"
A ten frame shows one number for each acorn: the last number is ten. Matching the acorns in
pairs proves it a second way. Funny moment: Otto tries to count Bramble's spines.

True sizes (K = 16 px per cm): squirrel sitting 20 cm, hedgehog 12 cm tall and 20 cm long
(about 5,000 spines), English oak acorn 2 to 2.5 cm long and about 1.6 cm wide (drawn 2.4 x
1.6 cm, 10% larger because the table is nearer the camera than the characters), ten frame
printed on A4 paper (29.7 cm wide, boxes 5.5 cm), timber verandah table.
"""
import math

import cairo

import render as R
import rig14 as rig
from render import W, INK, OCHRE, SAGE, ellipse, rrect, text, src, prog, lerp, ease, sparkles, NOW
import kit
from kit import Line

K = 16.0                       # px per cm
SQ_S = K / 10.4                # squirrel scale (20 cm sitting)
BR_S = 0.95 * K / 10.4         # hedgehog scale (12 cm tall, 20 cm long)
NEAR = 1.1                     # table things are nearer the camera
FEET = 1690
OTTO_X, BR_X, IVY_X = 215, 540, 865
GREEN = "#6E8460"
ACORN, ACORN_L, CAP = "#B07A43", "#CE9A5E", "#7A5A3A"

LINES = [
    Line("B", "Case open!", gap=0.4),                                    # 0
    Line("I", "Hey! That's not fair! Otto got more!", gap=0.6),          # 1
    Line("O", "I counted eleven acorns. You have ten!", gap=0.8),        # 2
    Line("N", "Today's case: counting to ten, one acorn at a time.", gap=0.7),  # 3
    Line("N", "It's like a sausage sizzle.", gap=0.6),                   # 4
    Line("N", "One sausage goes on each bread.", gap=0.6),               # 5
    Line("N", "One number goes with each thing.", gap=1.0),              # 6
    Line("O", "One, two, three, four, five, six.", gap=0.3),             # 7
    Line("O", "Seven, eight, nine, ten, eleven!", gap=0.8),              # 8
    Line("I", "Hmm. Something looks funny.", gap=0.8),                   # 9
    Line("B", "Let's not guess. Let's test.", gap=0.8),                  # 10
    Line("B", "Can you point to each acorn?", gap=4.0),                  # 11
    Line("B", "Who has more acorns?", gap=0.8),                          # 12
    Line("N", "A. Otto has more.", gap=0.6),                             # 13
    Line("N", "B. They have the same.", gap=0.6),                        # 14
    Line("N", "Pause and think.", gap=5.0),                              # 15
    Line("N", "A ten frame has ten boxes.", gap=0.6),                    # 16
    Line("N", "Move each acorn once. Say one number.", gap=0.8),         # 17
    Line("N", "One, two, three, four, five.", gap=0.6),                  # 18
    Line("N", "Six, seven, eight, nine, ten.", gap=0.8),                 # 19
    Line("N", "The last number tells how many. Ten!", gap=1.2),          # 20
    Line("O", "Oh! I counted one acorn twice!", gap=0.8),                # 21
    Line("N", "Both have ten. It's B!", gap=0.8),                        # 22
    Line("B", "Let's check another way. Make pairs.", gap=0.8),          # 23
    Line("N", "Every acorn has a partner.", gap=0.8),                    # 24
    Line("I", "Ten and ten. The same!", gap=0.8),                        # 25
    Line("B", "Case solved!", gap=1.9),                                  # 26
    Line("O", "Now let's count your spines, Bramble!", gap=0.6),         # 27
    Line("B", "I have about five thousand.", gap=0.6),                   # 28
    Line("O", "One, two, three... maybe tomorrow!", gap=1.0),            # 29
    Line("N", "Say it with me. The last number tells how many.", gap=2.2),  # 30
    Line("N", "Try it at home. Count ten pegs into a cup.", gap=0.9),    # 31
    Line("N", "Next case: a missing house number.", gap=0.6),            # 32
]

STRIP_HIDDEN = {3, 26}
CHILD_TURN = 30
STAMP_LINE = 26
OPEN_LINE = 0
CUT = [(0, 2), (7, 8), (19, 20), (22, 22), (26, 29), (30, 30), (32, 32)]

# ---------------------------------------------------------------- geometry
PILE_C = (275, 1080)
OTTO_RING = []
for _k in range(10):
    _a = math.radians(180 + 32 * _k)
    _j = (7 * math.sin(_k * 2.3), 6 * math.cos(_k * 1.7))
    OTTO_RING.append((PILE_C[0] + 170 * math.cos(_a) + _j[0], PILE_C[1] + 88 * math.sin(_a) + _j[1]))
IVY_GRID = [(660 + 75 * (k % 5), 1050 + 95 * (k // 5)) for k in range(10)]

PAPER = (300, 712, 480, 236)
BOX = 88
BX0, BY0 = 320, 742
FRAME_C = (540, 830)


def box_c(k):
    return BX0 + BOX / 2 + BOX * (k % 5), BY0 + BOX / 2 + BOX * (k // 5)


ROW_X = [150 + 87 * k for k in range(10)]
ROW_O, ROW_I = 1010, 1135
SPINE_TAGS = [(470, 1462), (540, 1444), (610, 1462)]


# ---------------------------------------------------------------- props
def acorn(ctx, x, y, sc=1.0, a=1.0, glow=0.0):
    """English oak acorn, 2.4 cm long and 1.6 cm wide; (x, y) is the bottom tip."""
    if a <= 0:
        return
    k = K * NEAR * sc
    h, w = 2.4 * k, 1.6 * k
    if glow > 0:
        R.glow(ctx, x, y - h / 2, h * 0.95, OCHRE, glow)
    if sc >= 0.9:
        rig.soft_shadow(ctx, x + 3, y + 1, w * 0.6, w * 0.16, 0.25 * a)
    # nut
    ctx.save()
    ctx.move_to(x, y)
    ctx.curve_to(x - w * 0.62, y - h * 0.05, x - w * 0.55, y - h * 0.72, x, y - h * 0.68)
    ctx.curve_to(x + w * 0.55, y - h * 0.72, x + w * 0.62, y - h * 0.05, x, y)
    ctx.close_path()
    g = cairo.RadialGradient(x - w * 0.18, y - h * 0.5, 1, x, y - h * 0.35, h * 0.55)
    g.add_color_stop_rgba(0, *R.rgb(ACORN_L), a)
    g.add_color_stop_rgba(0.6, *R.rgb(ACORN), a)
    g.add_color_stop_rgba(1, *R.rgb("#8C5D30"), a)
    ctx.set_source(g)
    ctx.fill()
    ctx.restore()
    ellipse(ctx, x - w * 0.16, y - h * 0.42, w * 0.08, h * 0.12, "#FFFFFF", 0.25 * a)
    ellipse(ctx, x, y - h * 0.02, w * 0.07, w * 0.07, "#6B4A2C", a)
    # cap
    ctx.save()
    ctx.move_to(x - w * 0.56, y - h * 0.62)
    ctx.curve_to(x - w * 0.6, y - h * 0.86, x + w * 0.6, y - h * 0.86, x + w * 0.56, y - h * 0.62)
    ctx.curve_to(x + w * 0.3, y - h * 0.56, x - w * 0.3, y - h * 0.56, x - w * 0.56, y - h * 0.62)
    ctx.close_path()
    g = cairo.LinearGradient(x - w * 0.5, y - h * 0.85, x + w * 0.5, y - h * 0.6)
    g.add_color_stop_rgba(0, *R.rgb("#9A7650"), a)
    g.add_color_stop_rgba(1, *R.rgb(CAP), a)
    ctx.set_source(g)
    ctx.fill()
    ctx.restore()
    src(ctx, "#5E4630", 0.45 * a)
    for i in range(5):
        ctx.arc(x - w * 0.36 + i * w * 0.18, y - h * 0.7 + (0.02 * h if i % 2 else 0), max(1.0, w * 0.04), 0, 2 * math.pi)
        ctx.fill()
    ctx.set_line_width(max(2.0, w * 0.14))
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    src(ctx, "#5E4630", a)
    ctx.move_to(x, y - h * 0.8)
    ctx.line_to(x + w * 0.08, y - h * 0.95)
    ctx.stroke()


def badge(ctx, x, y, s, a, col=INK, r=24):
    if a <= 0:
        return
    ellipse(ctx, x, y + 2, r, r, "#000000", 0.12 * a)
    ellipse(ctx, x, y, r, r, "#FFFFFF", 0.97 * a)
    ctx.set_line_width(3)
    src(ctx, "#E3D6BF", a)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.stroke()
    text(ctx, s, x, y + 1, r * 1.15, col, a)


def ten_frame(ctx, a, x0=None, y0=None, box=BOX, paper=True):
    if a <= 0:
        return
    x0 = BX0 if x0 is None else x0
    y0 = BY0 if y0 is None else y0
    if paper:
        px, py, pw, ph = PAPER
        rig.soft_shadow(ctx, px + pw / 2 + 10, py + ph + 4, pw * 0.5, 18, 0.25 * a)
        rrect(ctx, px, py, pw, ph, 6, "#FDFBF6", a)
    ctx.set_line_width(5 if box > 60 else 3)
    src(ctx, "#4F6B8C", a)
    for c in range(6):
        ctx.move_to(x0 + c * box, y0)
        ctx.line_to(x0 + c * box, y0 + 2 * box)
    for r in range(3):
        ctx.move_to(x0, y0 + r * box)
        ctx.line_to(x0 + 5 * box, y0 + r * box)
    ctx.stroke()


def bread_sausage(ctx, x, y, drop, a):
    """Sausage in a folded slice of white bread (card illustration)."""
    rrect(ctx, x - 105, y - 30, 210, 80, 28, "#C9965A", a)
    rrect(ctx, x - 98, y - 24, 196, 66, 24, "#F6E7C4", a)
    if drop > 0:
        yy = lerp(y - 85, y - 18, ease(drop))
        aa = a * min(1.0, drop * 3)
        rrect(ctx, x - 110, yy - 22, 220, 44, 22, "#9A4E32", aa)
        rrect(ctx, x - 92, yy - 16, 170, 10, 5, "#C27A5C", 0.7 * aa)


def peg(ctx, x, y, col, a, sc=1.0):
    """Wooden clothes peg, about 7 cm long (card illustration)."""
    rrect(ctx, x - 9 * sc, y - 38 * sc, 18 * sc, 76 * sc, 7 * sc, col, a)
    src(ctx, "#000000", 0.18 * a)
    ctx.rectangle(x - 1 * sc, y - 36 * sc, 2 * sc, 72 * sc)
    ctx.fill()
    rrect(ctx, x - 12 * sc, y - 4 * sc, 24 * sc, 8 * sc, 3 * sc, "#9AA3A8", a)


# ---------------------------------------------------------------- background
def verandah(ctx):
    g = cairo.LinearGradient(0, 0, 0, 600)
    g.add_color_stop_rgb(0, *R.rgb("#CBE0EA"))
    g.add_color_stop_rgb(1, *R.rgb("#EEF1E2"))
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, 670)
    ctx.fill()
    drift = NOW[0] * 5
    for cx0, cy0, cw in ((320, 170, 120), (820, 250, 140)):
        cx = (cx0 + drift) % 1500 - 200
        ellipse(ctx, cx, cy0, cw, cw * 0.34, "#FFFFFF", 0.75)
        ellipse(ctx, cx + cw * 0.4, cy0 - cw * 0.18, cw * 0.55, cw * 0.3, "#FFFFFF", 0.75)
    # backyard lawn, gum tree, Hills Hoist
    src(ctx, "#B5CA9C")
    ctx.rectangle(0, 500, W, 170)
    ctx.fill()
    ellipse(ctx, 540, 505, 700, 26, "#A9BF8F", 0.6)
    ctx.set_line_width(26)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    src(ctx, "#E4DED2")
    ctx.move_to(880, 560)
    ctx.curve_to(870, 470, 900, 380, 885, 300)
    ctx.stroke()
    for ex, ey, er in ((820, 300, 95), (930, 270, 110), (880, 210, 90), (990, 330, 70)):
        ellipse(ctx, ex, ey, er, er * 0.62, "#8FA383", 0.95)
    ctx.set_line_width(7)
    src(ctx, "#9AA3A8")
    ctx.move_to(300, 560)
    ctx.line_to(300, 360)
    ctx.stroke()
    ctx.set_line_width(4)
    for dx, dy in ((-150, 18), (150, -12), (-60, -30), (60, 30)):
        ctx.move_to(300, 365)
        ctx.line_to(300 + dx, 375 + dy)
    ctx.stroke()
    ctx.set_line_width(1.5)
    src(ctx, "#9AA3A8", 0.8)
    for r_ in (0.45, 0.75, 1.0):
        ctx.save()
        ctx.translate(300, 372)
        ctx.scale(150 * r_, 32 * r_)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        ctx.stroke()
    for i, (px, col) in enumerate(((190, "#E9B7A6"), (240, "#F1D58A"), (360, "#9CB7D0"), (410, "#C9B6DA"))):
        py = 372 + 32 * math.sin(math.acos((px - 300) / 150.0))
        rrect(ctx, px - 3, py - 4, 6, 16, 2, col)
    # verandah roof edge and posts
    src(ctx, "#DCD8CF")
    ctx.rectangle(0, 0, W, 64)
    ctx.fill()
    src(ctx, "#C7C2B7", 0.8)
    for x in range(0, W, 36):
        ctx.rectangle(x, 0, 14, 64)
    ctx.fill()
    src(ctx, "#F4EFE4")
    ctx.rectangle(0, 64, W, 16)
    ctx.fill()
    for px in (0, 1046):
        rrect(ctx, px - 6, 70, 40, 610, 4, "#F4EFE4")
        src(ctx, "#000000", 0.06)
        ctx.rectangle(px + 22, 80, 10, 590)
        ctx.fill()
    # timber table, boards running away from us
    g = cairo.LinearGradient(0, 660, 0, 1920)
    g.add_color_stop_rgb(0, *R.rgb("#CDA57A"))
    g.add_color_stop_rgb(1, *R.rgb("#B88E63"))
    ctx.set_source(g)
    ctx.rectangle(0, 660, W, 1920 - 660)
    ctx.fill()
    src(ctx, "#E2C39C", 0.9)
    ctx.rectangle(0, 660, W, 10)
    ctx.fill()
    ctx.set_line_width(4)
    for i in range(9):
        xb = 60 + i * 120
        src(ctx, "#9C7350", 0.35)
        ctx.move_to(540 + (xb - 540) * 0.9, 670)
        ctx.line_to(xb + (xb - 540) * 0.25, 1920)
        ctx.stroke()
    ctx.set_line_width(2)
    for i in range(14):
        xb = 90 + (i * 167) % 960
        yb = 760 + (i * 283) % 1000
        src(ctx, "#9C7350", 0.18)
        ctx.move_to(xb, yb)
        ctx.curve_to(xb + 6, yb + 60, xb - 4, yb + 120, xb + 3, yb + 180)
        ctx.stroke()


# ---------------------------------------------------------------- timing helpers
def word_t(ep, i, j, n):
    s, e = ep.s(i), ep.e(i)
    return s + (j + 0.25) / n * (e - s)


def move_t(ep, k):
    return word_t(ep, 18, k, 5) if k < 5 else word_t(ep, 19, k - 5, 5)


def arc_move(p0, p1, p, lift=70):
    q = ease(p)
    return lerp(p0[0], p1[0], q), lerp(p0[1], p1[1], q) - lift * math.sin(math.pi * q)


def otto_pos(ep, T, k):
    t1 = move_t(ep, k) - 0.15
    bx, by = box_c(k)
    in_box = (bx, by + 1.2 * K * NEAR)
    t2 = ep.s(23) + 0.3 + 0.07 * k
    if T < t1:
        return OTTO_RING[k]
    if T < t2:
        return arc_move(OTTO_RING[k], in_box, prog(T, t1, t1 + 0.55), 90)
    return arc_move(in_box, (ROW_X[k], ROW_O), prog(T, t2, t2 + 0.7), 40)


def ivy_pos(ep, T, k):
    t2 = ep.s(23) + 0.9 + 0.07 * k
    return arc_move(IVY_GRID[k], (ROW_X[k], ROW_I), prog(T, t2, t2 + 0.7), 40)


def otto_count_times(ep):
    ts = [word_t(ep, 7, j, 6) for j in range(6)] + [word_t(ep, 8, j, 5) for j in range(5)]
    return ts          # 11 numbers: the 11th lands back on acorn 0


def paper_alpha(ep, T):
    return prog(T, ep.s(16) - 0.5, ep.s(16) + 0.1) * (1 - prog(T, ep.s(23) + 1.4, ep.s(23) + 2.2))


# ---------------------------------------------------------------- scene
def scene(ctx, ep, T):
    verandah(ctx)
    pa = paper_alpha(ep, T)
    if pa > 0:
        ten_frame(ctx, pa)
        for k in range(10):     # small number in each filled box
            t0 = move_t(ep, k) + 0.4
            bx, by = box_c(k)
            text(ctx, str(k + 1), bx + 30, by - 30, 22, "#7A8BA0", pa * prog(T, t0, t0 + 0.3))
        la = prog(T, word_t(ep, 20, 6, 7), word_t(ep, 20, 6, 7) + 0.4) * (1 - prog(T, ep.e(22) + 0.6, ep.e(22) + 1.1))
        text(ctx, "10", 905, 835, 110, OCHRE, la)
    # pair links between the two rows
    for k in range(10):
        t0 = ep.s(24) + k / 10.0 * (ep.e(24) - ep.s(24))
        a = prog(T, t0, t0 + 0.3)
        if a > 0:
            ctx.set_line_width(7)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            src(ctx, SAGE, a)
            ctx.move_to(ROW_X[k], ROW_O + 14)
            ctx.line_to(ROW_X[k], ROW_I - 48)
            ctx.stroke()
    # acorns
    last = word_t(ep, 20, 6, 7)
    for k in range(10):
        x, y = ivy_pos(ep, T, k)
        acorn(ctx, x, y)
    for k in range(10):
        x, y = otto_pos(ep, T, k)
        gl = 0.0
        if k == 9:
            gl = 0.6 * prog(T, last, last + 0.3) * (1 - prog(T, ep.e(20) + 0.8, ep.e(20) + 1.3))
        acorn(ctx, x, y, glow=gl)
    # Otto's fast count: a number lands on each acorn, and the 11th lands on acorn 0 again
    fade = 1 - prog(T, ep.s(16) - 0.6, ep.s(16) - 0.1)
    if fade > 0:
        for n, t0 in enumerate(otto_count_times(ep)):
            a = prog(T, t0, t0 + 0.25) * fade
            k = n if n < 10 else 0
            x, y = OTTO_RING[k]
            dx = 0 if n < 10 else -54
            col = "#B4473E" if n in (0, 10) and T > otto_count_times(ep)[10] else INK
            badge(ctx, x + dx, y - 74, str(n + 1), a, col)
    # funny moment: numbers on Bramble's spines
    for j, (sx, sy) in enumerate(SPINE_TAGS):
        t0 = word_t(ep, 29, j, 5)
        a = prog(T, t0, t0 + 0.25) * (1 - prog(T, ep.e(29) + 0.6, ep.e(29) + 1.1))
        badge(ctx, sx, sy, str(j + 1), a, r=22)
    rig.squirrel(ctx, OTTO_X, FEET, SQ_S, OCHRE, f=1, seed=2.0)
    rig.bramble(ctx, BR_X, FEET, BR_S, f=1)
    rig.squirrel(ctx, IVY_X, FEET, SQ_S, SAGE, f=-1, seed=0.7)


# ---------------------------------------------------------------- cues, poses, foley
def cues(ep):
    a0 = OTTO_RING[0]
    return [
        ("ring", ep.s(1) - 0.1, ep.e(1) + 0.5, PILE_C[0], PILE_C[1] - 20, 215, 125),
        ("zoom", ep.s(7) - 0.2, ep.e(8) + 0.5, PILE_C[0], FEET, 1.14),
        ("lens", ep.s(9) - 0.1, ep.e(9) + 1.1, a0[0] - 27, a0[1] - 74, 330, 520, 150, 1.7),
        ("ring", ep.s(11) - 0.1, ep.e(11) + 4.4, PILE_C[0], PILE_C[1] - 20, 215, 125),
        ("ring", ep.s(16) - 0.1, ep.e(16) + 0.5, FRAME_C[0], FRAME_C[1], 270, 140),
        ("zoom", ep.s(18) - 0.3, ep.e(20) + 0.4, FRAME_C[0], FEET, 1.12),
        ("ring", ep.s(24) - 0.1, ep.e(25) + 0.4, 540, 1105, 470, 120),
        ("zoom", ep.s(27) - 0.2, ep.e(29) + 0.5, BR_X, FEET, 1.12),
    ]


def foley(ep):
    out = [("whoosh", ep.s(3) - 0.3), ("whoosh", ep.s(16) - 0.5), ("whoosh", ep.s(23) + 0.3)]
    for k in range(10):
        out.append(("pop", move_t(ep, k) + 0.4))
    for j in (1, 3, 5):
        out.append(("pop", word_t(ep, 5, j, 6) + 0.3))
    out.append(("step", ep.s(26) + 0.5))
    return out


def poses(ep, T):
    S, E = ep.s, ep.e

    def during(i, pre=0.2, post=0.6):
        return S(i) - pre <= T <= E(i) + post

    def ramp(t0):
        return prog(T, t0, t0 + 0.5)

    B = {"face": 1}
    O = {"face": 1}
    I = {"face": -1}
    if T < S(3):
        I["expr"] = "sad"
        O["expr"] = "happy"
    if during(2, 0.1, 0.3):
        O.update(point=(PILE_C[0], PILE_C[1] - 30), amt=ramp(S(2)))
    if S(7) - 0.3 <= T <= E(8) + 0.4:
        O.update(expr="happy", point=(PILE_C[0], PILE_C[1] - 30), amt=ramp(S(7) - 0.3))
    if during(9, 0.2, 0.8):
        I["expr"] = "think"
        O["expr"] = "think"
    if S(10) - 0.2 <= T <= E(11) + 4.2:
        B.update(face=-1 if T < S(11) else 1, expr="think" if T < S(11) else "happy")
    if S(12) <= T <= S(16):
        O["expr"] = I["expr"] = "think"
    if S(16) - 0.2 <= T <= E(20) + 0.3:
        B.update(expr="happy" if T > S(20) else None, point=(FRAME_C[0] + 60, FRAME_C[1] + 60), amt=ramp(S(16) - 0.2))
        if B["expr"] is None:
            del B["expr"]
    if during(21, 0.2, 0.8):
        O["expr"] = "surprise"
        O["scratch"] = prog(T, S(21) + 0.3, S(21) + 0.8) * (1 - prog(T, E(21) + 0.4, E(21) + 0.8))
    if during(22, 0.2, 0.6):
        I["expr"] = "happy"
    if S(23) - 0.2 <= T <= E(25) + 0.4:
        I["expr"] = "happy" if T > S(25) - 0.2 else "think"
    if T >= S(26) - 0.2:
        B["expr"] = O["expr"] = I["expr"] = "happy"
        hop = (T - S(26)) / 0.55
        if 0 <= hop <= 1:
            O["jump"] = 42 * math.sin(math.pi * hop)
    if during(27, 0.1, 0.3):
        O.update(point=(420, 1470), amt=ramp(S(27)))
    if during(29, 0.1, 0.9):
        O["scratch"] = prog(T, word_t(ep, 29, 3, 5) - 0.2, word_t(ep, 29, 3, 5) + 0.3) * \
            (1 - prog(T, E(29) + 0.5, E(29) + 0.9))
    return {"B": B, "O": O, "I": I}


# ---------------------------------------------------------------- cards
def card(ctx, x, y, w, h, a, col="#FFFFFF", op=0.95):
    rig.soft_shadow(ctx, x + w / 2, y + h + 6, w * 0.5, 16, 0.18 * a)
    rrect(ctx, x, y, w, h, 40, col, op * a)


def window(T, s, e, fin=0.35, fout=0.4):
    return prog(T, s, s + fin) * (1 - prog(T, e - fout, e))


def tick_box(ctx, x0, y0, w, h, pk):
    ctx.set_line_width(10)
    src(ctx, GREEN, pk)
    ctx.new_sub_path()
    r = 40
    ctx.arc(x0 + w - r, y0 + r, r, -math.pi / 2, 0)
    ctx.arc(x0 + w - r, y0 + h - r, r, 0, math.pi / 2)
    ctx.arc(x0 + r, y0 + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x0 + r, y0 + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()
    ctx.stroke()
    ellipse(ctx, x0 + w - 56, y0 + 60, 36, 36, GREEN, pk)
    ctx.set_line_width(9)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    src(ctx, "#FFFFFF", pk)
    ctx.move_to(x0 + w - 72, y0 + 60)
    ctx.line_to(x0 + w - 60, y0 + 73)
    ctx.line_to(x0 + w - 38, y0 + 47)
    ctx.stroke()


def cards(ctx, ep, T):
    S, E = ep.s, ep.e
    # Otto's claim
    a = window(T, S(2) - 0.2, E(2) + 0.9)
    if a > 0:
        card(ctx, 190, 150, 700, 250, a)
        ctx.push_group()
        kit.face_icon(ctx, 330, 285, "O")
        text(ctx, "11", 450, 280, 100, INK)
        kit.face_icon(ctx, 640, 285, "I")
        text(ctx, "10", 760, 280, 100, INK)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(a)
    # Today's case title (read word for word)
    a = window(T, S(3) - 0.3, E(3) + 0.9)
    if a > 0:
        card(ctx, 70, 140, 940, 420, a)
        rrect(ctx, 120, 184, 60, 46, 8, OCHRE, a)
        rrect(ctx, 120, 176, 28, 14, 5, OCHRE, a)
        text(ctx, "Today's case", 560, 210, 46, "#9C7429", a)
        for k, s_ in enumerate(("Counting to ten,", "one acorn", "at a time")):
            text(ctx, s_, W / 2, 310 + k * 82, 66, INK, a)
    # sausage sizzle: one sausage on each bread, one number with each thing
    a = window(T, S(4) - 0.2, E(6) + 1.2)
    if a > 0:
        card(ctx, 70, 140, 940, 420, a)
        text(ctx, "Sausage sizzle", W / 2, 200, 44, "#9C7429", a)
        for j, x in enumerate((250, 540, 830)):
            drop = prog(T, word_t(ep, 5, 2 * j + 1, 6) - 0.1, word_t(ep, 5, 2 * j + 1, 6) + 0.4)
            bread_sausage(ctx, x, 345, drop, a)
            t0 = word_t(ep, 6, 2 * j + 1, 6)
            badge(ctx, x, 470, str(j + 1), a * prog(T, t0, t0 + 0.3), r=30)
    # A or B
    aA = window(T, S(12) - 0.2, E(22) + 1.4)
    if aA > 0:
        aA2 = aA * prog(T, S(13) - 0.2, S(13) + 0.2)
        aB = aA * prog(T, S(14) - 0.2, S(14) + 0.2)
        d = E(22) - S(22)
        picked = prog(T, S(22) + 0.7 * d, S(22) + 0.7 * d + 0.4)
        # A: Otto has more
        ak = aA2 * (1 - 0.5 * picked)
        card(ctx, 70, 150, 450, 300, aA2)
        ellipse(ctx, 134, 210, 38, 38, OCHRE, ak)
        text(ctx, "A", 134, 212, 48, "#FFFFFF", ak)
        for j in range(6):
            acorn(ctx, 200 + 34 * (j % 3), 300 + 46 * (j // 3), sc=0.75, a=ak)
        for j in range(3):
            acorn(ctx, 360 + 34 * j, 346, sc=0.75, a=ak)
        text(ctx, "Otto has more", 295, 405, 40, INK, ak)
        # B: the same
        card(ctx, 560, 150, 450, 300, aB)
        ellipse(ctx, 624, 210, 38, 38, SAGE, aB)
        text(ctx, "B", 624, 212, 48, "#FFFFFF", aB)
        for j in range(5):
            acorn(ctx, 700 + 48 * j, 290, sc=0.75, a=aB)
            acorn(ctx, 700 + 48 * j, 350, sc=0.75, a=aB)
        text(ctx, "The same", 785, 405, 44, INK, aB)
        if picked > 0:
            tick_box(ctx, 560, 150, 450, 300, picked * aB)
        g0, g1 = E(15) + 0.2, E(15) + 4.9
        ra = aA * window(T, S(15), S(16) + 0.3, 0.3, 0.4)
        if ra > 0:
            cx, cy = W / 2, 520
            ellipse(ctx, cx, cy, 52, 52, "#FFFFFF", 0.95 * ra)
            ctx.set_line_width(10)
            src(ctx, "#E3D6BF", ra)
            ctx.arc(cx, cy, 38, 0, 2 * math.pi)
            ctx.stroke()
            f = R.clamp((T - g0) / (g1 - g0))
            if f > 0:
                src(ctx, "#F2C85B", ra)
                ctx.arc(cx, cy, 38, -math.pi / 2, -math.pi / 2 + 2 * math.pi * f)
                ctx.stroke()
            if f >= 1:
                ctx.set_line_width(7)
                ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                src(ctx, GREEN, ra)
                ctx.move_to(cx - 16, cy)
                ctx.line_to(cx - 4, cy + 12)
                ctx.line_to(cx + 18, cy - 14)
                ctx.stroke()
    # recap
    ra = window(T, S(30) - 0.3, S(32) - 0.1, 0.5, 0.5)
    if ra > 0:
        card(ctx, 30, 130, 1020, 1010, ra, "#FBF6EC", 1.0)
        rrect(ctx, 300, 160, 480, 110, 50, OCHRE, ra)
        text(ctx, "Remember", W / 2, 215, 62, "#FFFFFF", ra)
        r1 = ra * prog(T, S(30) + 0.3, S(30) + 0.9)
        rrect(ctx, 100, 310, 880, 350, 36, "#FFFFFF", 0.95 * r1)
        bx0, by0, bb = 290, 345, 62
        ctx.push_group()
        ten_frame(ctx, 1.0, bx0, by0, bb, paper=False)
        for k in range(10):
            acorn(ctx, bx0 + bb / 2 + bb * (k % 5), by0 + bb * (k // 5) + bb - 12, sc=0.85)
        text(ctx, "10", 830, 408, 84, OCHRE)
        text(ctx, "The last number", W / 2, 540, 54, INK)
        text(ctx, "tells how many", W / 2, 608, 54, INK)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(r1)
        r2 = ra * prog(T, S(31), S(31) + 0.6)
        rrect(ctx, 100, 700, 880, 400, 36, "#FFFFFF", 0.95 * r2)
        text(ctx, "Try it at home:", W / 2, 770, 50, "#9C7429", r2)
        text(ctx, "count ten pegs", W / 2, 850, 56, INK, r2)
        text(ctx, "into a cup", W / 2, 920, 56, INK, r2)
        cols = ("#E9B7A6", "#F1D58A", "#9CB7D0", "#C9B6DA", "#B5CA9C")
        for j in range(5):
            peg(ctx, 250 + j * 50, 1020, cols[j], r2)
        # cup
        ctx.move_to(700, 980)
        ctx.line_to(820, 980)
        ctx.line_to(806, 1068)
        ctx.line_to(714, 1068)
        ctx.close_path()
        src(ctx, "#9CB7D0", r2)
        ctx.fill()
        ellipse(ctx, 760, 980, 60, 12, "#7E9DB8", r2)
        peg(ctx, 745, 968, "#F1D58A", r2, 0.8)
        peg(ctx, 775, 972, "#E9B7A6", r2, 0.8)
    # teaser
    ta = window(T, S(32) - 0.1, ep.total - 1.0, 0.4, 0.5)
    if ta > 0:
        card(ctx, 140, 170, 800, 460, ta)
        rrect(ctx, 330, 200, 420, 100, 46, SAGE, ta)
        text(ctx, "Next case", W / 2, 250, 54, "#FFFFFF", ta)
        for j, (x, lab) in enumerate(((300, "101"), (540, "102"), (780, "?"))):
            ctx.move_to(x - 85, 400)
            ctx.line_to(x, 335)
            ctx.line_to(x + 85, 400)
            ctx.close_path()
            src(ctx, ("#B4473E", "#7A8BA0", "#C9973A")[j], ta)
            ctx.fill()
            rrect(ctx, x - 70, 398, 140, 100, 6, "#F1E6D2", ta)
            rrect(ctx, x - 18, 440, 36, 58, 4, "#8B6A4E", ta)
            rrect(ctx, x - 40, 405, 80, 30, 6, "#FFFFFF", ta)
            text(ctx, lab, x, 421, 24, INK, ta)
        text(ctx, "A missing house number", W / 2, 565, 50, INK, ta)
