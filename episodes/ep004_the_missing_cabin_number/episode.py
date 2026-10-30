"""Episode 004: The missing cabin number (Years 1 to 2, Maths, Representing whole numbers).

Setting: a beach caravan park on a sunny morning. A row of holiday cabins is numbered
99, 100, 101, ?, 103, 104. Ivy and Otto's cabin has lost its number plate. Otto counts
"ninety-nine, one hundred, two hundred!" but the next cabin already says 101. Counting on
by ones past one hundred (like runs on a cricket scoreboard) gives 102, and counting back
from 104 proves it a second way. Funny moment: a snail moves in, and it brought its own house.

True sizes (K = 16 px per cm): squirrel sitting 20 cm, hedgehog 12 cm tall and 20 cm long.
Garden snail shell about 3 cm, body about 5 cm (drawn about 0.85 x because it sits a little
further back on the lawn). Cabins are about 3 m wide and 30 m back, so they are drawn small.
Holiday park cabins (not street houses) are numbered one after another, so counting by ones
along the row is true to life.
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
SKY_Y = 640
CAB_X = [95, 273, 451, 629, 807, 985]
CAB_N = ["99", "100", "101", "", "103", "104"]
CAB_COL = ["#E9C9A6", "#B9D0D8", "#E6D79A", "#D9B8B0", "#C6D4B0", "#D2C3DC"]
CAB_W, CAB_TOP, CAB_BOT = 160, 860, 1120
PLATE_Y = 925
MISSING = 3
SNAIL_Y = 1262

CASE_NO = 4
RULE = "Past one hundred, keep counting by ones."
SETTING = "the beach caravan park"
SENTENCE_LIMIT = 8

LINES = [
    Line("B", "Case open!", gap=0.4),                                    # 0
    Line("I", "Oh no! Our cabin lost its number!", gap=0.6),             # 1
    Line("O", "Easy! It's number two hundred!", gap=0.8),                # 2
    Line("N", "Today's case: a missing house number.", gap=0.7),         # 3
    Line("N", "Counting on means saying the next number.", gap=0.8),     # 4
    Line("N", "It's like a cricket scoreboard.", gap=0.6),               # 5
    Line("N", "One more run. One more number.", gap=0.6),                # 6
    Line("N", "Ninety-nine, one hundred, one hundred and one.", gap=1.0),  # 7
    Line("O", "Ninety-nine, one hundred, two hundred!", gap=0.8),        # 8
    Line("I", "Hmm. That cabin says one hundred and one.", gap=0.8),     # 9
    Line("B", "Let's not guess. Let's test.", gap=0.8),                  # 10
    Line("B", "Can you point to the empty sign?", gap=4.0),              # 11
    Line("B", "What number goes there?", gap=0.8),                       # 12
    Line("N", "A. Two hundred.", gap=0.6),                               # 13
    Line("N", "B. One hundred and two.", gap=0.6),                       # 14
    Line("N", "Pause and think.", gap=5.0),                              # 15
    Line("N", "Let's count on from ninety-nine.", gap=0.6),              # 16
    Line("N", "Ninety-nine. One hundred.", gap=0.6),                     # 17
    Line("N", "Past one hundred, keep counting by ones.", gap=0.8),      # 18
    Line("N", "One hundred and one.", gap=0.6),                          # 19
    Line("N", "Then one hundred and two!", gap=1.2),                     # 20
    Line("O", "Oh! I jumped way too far!", gap=0.8),                     # 21
    Line("N", "It's B! One hundred and two.", gap=0.8),                  # 22
    Line("B", "Let's check another way. Count back.", gap=0.8),          # 23
    Line("N", "One hundred and four. One hundred and three.", gap=0.6),  # 24
    Line("N", "One hundred and two!", gap=0.8),                          # 25
    Line("I", "Both ways say one hundred and two!", gap=0.8),            # 26
    Line("B", "Case solved!", gap=1.9),                                  # 27
    Line("I", "Look! A snail is moving in!", gap=0.6),                   # 28
    Line("O", "It brought its own house!", gap=1.0),                     # 29
    Line("N", "Remember. Past one hundred, keep counting by ones.", gap=0.9),  # 30
    Line("N", "Say it with me. Past one hundred, keep counting by ones.", gap=2.2),  # 31
    Line("N", "Try it at home. Read house numbers on a walk.", gap=0.9),  # 32
    Line("N", "Next case: a witness who needs better words.", gap=0.6),  # 33
]

STRIP_HIDDEN = {3, 27, 30}
CHILD_TURN = 31
STAMP_LINE = 27
OPEN_LINE = 0
CUT = [(0, 2), (8, 9), (17, 22), (27, 29), (31, 31), (33, 33)]


# ---------------------------------------------------------------- props
def pill(ctx, s, x, y, a, col=INK, h=56):
    """Number tag above a cabin (white pill, coloured number)."""
    if a <= 0:
        return
    w = 40 + 26 * len(s)
    ellipse(ctx, x, y + 3, w / 2, h / 2, "#000000", 0.10 * a)
    rrect(ctx, x - w / 2, y - h / 2, w, h, h / 2, "#FFFFFF", 0.97 * a)
    ctx.set_line_width(3)
    src(ctx, "#E3D6BF", a)
    ctx.new_sub_path()
    ctx.arc(x - w / 2 + h / 2, y, h / 2, math.pi / 2, 1.5 * math.pi)
    ctx.arc(x + w / 2 - h / 2, y, h / 2, -math.pi / 2, math.pi / 2)
    ctx.close_path()
    ctx.stroke()
    text(ctx, s, x, y + 1, 40, col, a)


def plate(ctx, x, y, s, a=1.0, sc=1.0):
    """Cabin number plate (white with a blue edge); empty shows two screw holes."""
    w, h = 92 * sc, 50 * sc
    rrect(ctx, x - w / 2 - 3, y - h / 2 - 3, w + 6, h + 6, 10 * sc, "#4F6B8C", a)
    rrect(ctx, x - w / 2, y - h / 2, w, h, 8 * sc, "#FFFFFF", a)
    if s:
        text(ctx, s, x, y + 1, 38 * sc, INK, a)
    else:
        for dx in (-30, 30):
            ellipse(ctx, x + dx * sc, y, 4 * sc, 4 * sc, "#9AA3A8", a)
        rrect(ctx, x - 26 * sc, y - 14 * sc, 52 * sc, 28 * sc, 4 * sc, "#EDE7DB", 0.8 * a)


def cabin(ctx, k, num_a=0.0):
    x, col = CAB_X[k], CAB_COL[k]
    l, r = x - CAB_W / 2, x + CAB_W / 2
    rig.soft_shadow(ctx, x + 6, CAB_BOT + 4, CAB_W * 0.58, 12, 0.22)
    rrect(ctx, l, CAB_TOP, CAB_W, CAB_BOT - CAB_TOP, 6, col)
    src(ctx, "#000000", 0.06)
    ctx.rectangle(x + CAB_W * 0.25, CAB_TOP, CAB_W * 0.25, CAB_BOT - CAB_TOP)
    ctx.fill()
    # roof
    ctx.move_to(l - 14, CAB_TOP + 4)
    ctx.line_to(x, CAB_TOP - 86)
    ctx.line_to(r + 14, CAB_TOP + 4)
    ctx.close_path()
    src(ctx, "#8E6F5E")
    ctx.fill()
    ctx.move_to(x, CAB_TOP - 86)
    ctx.line_to(r + 14, CAB_TOP + 4)
    ctx.line_to(x + 30, CAB_TOP + 4)
    ctx.close_path()
    src(ctx, "#000000", 0.10)
    ctx.fill()
    # door, window, steps
    rrect(ctx, x - 26, 990, 52, CAB_BOT - 990, 4, "#8B6A4E")
    ellipse(ctx, x + 16, 1058, 4, 4, "#E8C77E")
    rrect(ctx, l + 12, 990, 28, 40, 3, "#DDEBF0")
    rrect(ctx, r - 40, 990, 28, 40, 3, "#DDEBF0")
    rrect(ctx, x - 40, CAB_BOT - 4, 80, 14, 3, "#B8AFA2")
    s = CAB_N[k]
    if k == MISSING:
        plate(ctx, x, PLATE_Y, "")
        if num_a > 0:
            plate(ctx, x, PLATE_Y, "102", num_a)
    else:
        plate(ctx, x, PLATE_Y, s)


def snail(ctx, x, y, a=1.0, f=-1):
    """Garden snail heading left (f=-1); (x, y) is the middle of its foot."""
    if a <= 0:
        return
    s = K * 0.85
    rig.soft_shadow(ctx, x, y + 2, 2.8 * s, 0.35 * s, 0.25 * a)
    # body
    rrect(ctx, x - 2.6 * s, y - 0.7 * s, 5.2 * s, 0.9 * s, 0.45 * s, "#B9A58E", a)
    hx = x + f * 2.5 * s
    ellipse(ctx, hx, y - 0.75 * s, 0.6 * s, 0.55 * s, "#B9A58E", a)
    ctx.set_line_width(3)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    src(ctx, "#9C876F", a)
    for dx, top in ((0.1, 1.9), (0.5, 1.6)):
        ctx.move_to(hx + f * dx * s, y - 1.1 * s)
        ctx.line_to(hx + f * (dx + 0.25) * s, y - top * s)
    ctx.stroke()
    for dx, top in ((0.1, 1.9), (0.5, 1.6)):
        ellipse(ctx, hx + f * (dx + 0.25) * s, y - top * s, 3.5, 3.5, "#7E6A55", a)
    # shell (about 3 cm), a spiral
    sx, sy, sr = x - f * 0.3 * s, y - 1.6 * s, 1.5 * s
    rig.ball(ctx, sx, sy, sr, sr, "#C08A55", a)
    ctx.set_line_width(4)
    src(ctx, "#8C5D30", 0.8 * a)
    ctx.move_to(sx, sy)
    for i in range(1, 60):
        th = i * 0.18
        rr = sr * 0.9 * i / 60
        ctx.line_to(sx + rr * math.cos(th), sy + rr * math.sin(th))
    ctx.stroke()


def scoreboard(ctx, x, y, n, a):
    """Cricket scoreboard panel showing the runs."""
    rrect(ctx, x - 230, y - 120, 460, 230, 18, "#2F5D46", a)
    rrect(ctx, x - 214, y - 104, 428, 198, 12, "#3A6E54", a)
    text(ctx, "RUNS", x, y - 72, 34, "#DCE8D8", a)
    rrect(ctx, x - 170, y - 46, 340, 130, 10, "#1F3B2E", a)
    text(ctx, str(n), x, y + 20, 104, "#F2C85B", a)


# ---------------------------------------------------------------- background
def park(ctx):
    g = cairo.LinearGradient(0, 0, 0, 560)
    g.add_color_stop_rgb(0, *R.rgb("#C6DEEA"))
    g.add_color_stop_rgb(1, *R.rgb("#EEF2E6"))
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, 600)
    ctx.fill()
    drift = NOW[0] * 5
    for cx0, cy0, cw in ((260, 150, 120), (780, 230, 140)):
        cx = (cx0 + drift) % 1500 - 200
        ellipse(ctx, cx, cy0, cw, cw * 0.34, "#FFFFFF", 0.75)
        ellipse(ctx, cx + cw * 0.4, cy0 - cw * 0.18, cw * 0.55, cw * 0.3, "#FFFFFF", 0.75)
    # sea and dunes behind the park
    src(ctx, "#9CC3CF")
    ctx.rectangle(0, 560, W, 50)
    ctx.fill()
    src(ctx, "#FFFFFF", 0.5)
    for i in range(7):
        xw = (i * 173 + NOW[0] * 8) % 1180 - 50
        ctx.rectangle(xw, 578 + (i % 3) * 9, 60, 3)
    ctx.fill()
    ellipse(ctx, 300, 640, 460, 50, "#E8D9B5")
    ellipse(ctx, 860, 645, 420, 46, "#E3D3AE")
    # Norfolk Island pines
    for px, ph in ((200, 330), (930, 300)):
        rrect(ctx, px - 6, 700 - ph, 12, ph, 4, "#7A6250")
        for j in range(7):
            yy = 700 - ph + 30 + j * (ph - 60) / 7
            ww = 30 + j * 12
            ctx.move_to(px - ww, yy + 22)
            ctx.line_to(px, yy - 6)
            ctx.line_to(px + ww, yy + 22)
            ctx.close_path()
            src(ctx, "#6F8A63", 0.95)
            ctx.fill()
    # lawn
    g = cairo.LinearGradient(0, 640, 0, 1920)
    g.add_color_stop_rgb(0, *R.rgb("#B9CC9E"))
    g.add_color_stop_rgb(1, *R.rgb("#A3BB86"))
    ctx.set_source(g)
    ctx.rectangle(0, 660, W, 1920 - 660)
    ctx.fill()
    # gravel road in front of the cabins
    src(ctx, "#DCD3C3")
    ctx.rectangle(0, 1150, W, 70)
    ctx.fill()
    src(ctx, "#C9BFAE", 0.8)
    ctx.rectangle(0, 1150, W, 5)
    ctx.rectangle(0, 1215, W, 5)
    ctx.fill()
    ctx.set_line_width(2)
    for i in range(16):
        xb = 40 + (i * 167) % 1000
        yb = 1300 + (i * 97) % 380
        src(ctx, "#8FA673", 0.5)
        ctx.move_to(xb, yb)
        ctx.line_to(xb - 5, yb - 14)
        ctx.move_to(xb + 6, yb)
        ctx.line_to(xb + 9, yb - 12)
        ctx.stroke()


# ---------------------------------------------------------------- timing helpers
def word_t(ep, i, j, n):
    s, e = ep.s(i), ep.e(i)
    return s + (j + 0.25) / n * (e - s)


def otto_tags(ep):
    """Otto's count: (time, cabin, label)."""
    return [(word_t(ep, 8, 0, 5), 0, "99"), (word_t(ep, 8, 1, 5), 1, "100"), (word_t(ep, 8, 3, 5), 2, "200")]


def fwd_tags(ep):
    return [(word_t(ep, 17, 0, 3), 0, "99"), (word_t(ep, 17, 1, 3), 1, "100"),
            (ep.s(19) + 0.1, 2, "101"), (word_t(ep, 20, 1, 5), 3, "102")]


def back_tags(ep):
    return [(word_t(ep, 24, 0, 8), 5, "104"), (word_t(ep, 24, 4, 8), 4, "103"), (ep.s(25) + 0.1, 3, "102")]


def snail_x(ep, T):
    return lerp(800, 690, prog(T, ep.s(28) - 0.6, ep.total))


# ---------------------------------------------------------------- scene
TAG_Y = 728


def scene(ctx, ep, T):
    park(ctx)
    num_a = prog(T, word_t(ep, 22, 2, 6), word_t(ep, 22, 2, 6) + 0.4)
    for k in range(6):
        if k == MISSING:
            g0 = word_t(ep, 20, 1, 5)
            R.glow(ctx, CAB_X[k], PLATE_Y, 110, OCHRE, 0.6 * prog(T, g0, g0 + 0.3) * (1 - prog(T, ep.e(20) + 0.8, ep.e(20) + 1.3)))
        cabin(ctx, k, num_a)
    # Otto's count: the third tag lands on 101, and says 200
    fo = 1 - prog(T, ep.s(16) - 0.6, ep.s(16) - 0.1)
    for t0, k, lab in otto_tags(ep):
        pill(ctx, lab, CAB_X[k], TAG_Y, prog(T, t0, t0 + 0.25) * fo, "#B4473E" if lab == "200" else INK)
    # counting on from 99
    ff = 1 - prog(T, ep.s(23) - 0.2, ep.s(23) + 0.3)
    for t0, k, lab in fwd_tags(ep):
        pill(ctx, lab, CAB_X[k], TAG_Y, prog(T, t0, t0 + 0.25) * ff, OCHRE if k == MISSING else INK)
    # counting back from 104
    fb = 1 - prog(T, ep.s(27) - 0.2, ep.s(27) + 0.3)
    for t0, k, lab in back_tags(ep):
        pill(ctx, lab, CAB_X[k], TAG_Y, prog(T, t0, t0 + 0.25) * fb, "#5F7A4E")
    # funny moment: a snail heads for cabin 102
    snail(ctx, snail_x(ep, T), SNAIL_Y, prog(T, ep.s(28) - 0.8, ep.s(28) - 0.2))
    rig.squirrel(ctx, OTTO_X, FEET, SQ_S, OCHRE, f=1, seed=2.0)
    rig.bramble(ctx, BR_X, FEET, BR_S, f=1)
    rig.squirrel(ctx, IVY_X, FEET, SQ_S, SAGE, f=-1, seed=0.7)


# ---------------------------------------------------------------- cues, poses, foley
def cues(ep):
    px = CAB_X[MISSING]
    return [
        ("ring", ep.s(1) - 0.1, ep.e(1) + 0.5, px, PLATE_Y, 85, 60),
        ("zoom", ep.s(8) - 0.2, ep.e(9) + 0.5, 300, FEET, 1.12),
        ("ring", ep.s(11) - 0.1, ep.e(11) + 4.4, px, PLATE_Y, 85, 60),
        ("zoom", ep.s(17) - 0.3, ep.e(20) + 0.4, 360, FEET, 1.1),
        ("ring", ep.s(24) - 0.1, ep.e(25) + 0.4, CAB_X[4], 880, 268, 200),
        ("lens", ep.s(28) - 0.1, ep.e(29) + 0.8, 730, SNAIL_Y - 20, 300, 1000, 140, 1.8),
    ]


def foley(ep):
    out = [("whoosh", ep.s(3) - 0.3), ("whoosh", ep.s(5) - 0.3), ("whoosh", ep.s(12) - 0.3)]
    for tags in (otto_tags(ep), fwd_tags(ep), back_tags(ep)):
        for t0, _, _ in tags:
            out.append(("pop", t0 + 0.1))
    out.append(("pop", word_t(ep, 22, 2, 6) + 0.1))
    out.append(("step", ep.s(27) + 0.5))
    return out


def poses(ep, T):
    S, E = ep.s, ep.e

    def during(i, pre=0.2, post=0.6):
        return S(i) - pre <= T <= E(i) + post

    def ramp(t0):
        return prog(T, t0, t0 + 0.5)

    plate_pt = (CAB_X[MISSING], PLATE_Y + 20)
    B = {"face": 1}
    O = {"face": 1}
    I = {"face": -1}
    if T < S(3):
        I["expr"] = "sad"
    if during(2, 0.1, 0.3):
        O.update(expr="happy", point=plate_pt, amt=ramp(S(2)))
    if S(8) - 0.3 <= T <= E(8) + 0.4:
        O.update(expr="happy", point=(CAB_X[1], 960), amt=ramp(S(8) - 0.3))
    if during(9, 0.2, 0.8):
        I["expr"] = "think"
        O["expr"] = "think"
    if S(10) - 0.2 <= T <= E(11) + 4.2:
        B.update(expr="think" if T < S(11) else "happy")
        if T >= S(11) - 0.1:
            B.update(point=plate_pt, amt=ramp(S(11) - 0.1))
    if S(12) <= T <= S(16):
        O["expr"] = I["expr"] = "think"
    if S(16) - 0.2 <= T <= E(20) + 0.3:
        B.update(expr="happy" if T > S(20) else "think", point=plate_pt, amt=ramp(S(16) - 0.2))
    if during(21, 0.2, 0.8):
        O["expr"] = "surprise"
        O["scratch"] = prog(T, S(21) + 0.3, S(21) + 0.8) * (1 - prog(T, E(21) + 0.4, E(21) + 0.8))
    if during(22, 0.2, 0.6):
        I["expr"] = "happy"
    if S(23) - 0.2 <= T <= E(25) + 0.3:
        B.update(expr="think", point=(CAB_X[4], 960), amt=ramp(S(23) - 0.2))
    if during(26, 0.2, 0.6):
        I["expr"] = "happy"
    if T >= S(27) - 0.2:
        B["expr"] = O["expr"] = I["expr"] = "happy"
        hop = (T - S(27)) / 0.55
        if 0 <= hop <= 1:
            O["jump"] = 42 * math.sin(math.pi * hop)
    if during(28, 0.1, 0.3):
        I["expr"] = "surprise"
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
    # Today's case title (read word for word)
    a = window(T, S(3) - 0.3, E(3) + 0.9)
    if a > 0:
        card(ctx, 70, 140, 940, 420, a)
        rrect(ctx, 120, 184, 60, 46, 8, OCHRE, a)
        rrect(ctx, 120, 176, 28, 14, 5, OCHRE, a)
        text(ctx, "Today's case", 560, 210, 46, "#9C7429", a)
        for k, s_ in enumerate(("A missing", "house number")):
            text(ctx, s_, W / 2, 330 + k * 92, 72, INK, a)
    # counting on: a cricket scoreboard, one more run, one more number
    a = window(T, S(5) - 0.2, E(7) + 1.0)
    if a > 0:
        card(ctx, 70, 140, 940, 420, a)
        text(ctx, "Cricket scoreboard", W / 2, 196, 44, "#9C7429", a)
        n = 99
        if T >= word_t(ep, 7, 1, 7):
            n = 100
        if T >= word_t(ep, 7, 3, 7):
            n = 101
        scoreboard(ctx, W / 2, 380, n, a)
        b = prog(T, word_t(ep, 6, 1, 6), word_t(ep, 6, 1, 6) + 0.3)
        text(ctx, "+1", 850, 380, 70, GREEN, a * b)
    # A or B
    aA = window(T, S(12) - 0.2, E(22) + 1.4)
    if aA > 0:
        aA2 = aA * prog(T, S(13) - 0.2, S(13) + 0.2)
        aB = aA * prog(T, S(14) - 0.2, S(14) + 0.2)
        d = E(22) - S(22)
        picked = prog(T, S(22) + 0.2 * d, S(22) + 0.2 * d + 0.4)
        ak = aA2 * (1 - 0.5 * picked)
        card(ctx, 70, 150, 450, 300, aA2)
        ellipse(ctx, 134, 210, 38, 38, OCHRE, ak)
        text(ctx, "A", 134, 212, 48, "#FFFFFF", ak)
        plate(ctx, 295, 320, "200", ak, 1.9)
        card(ctx, 560, 150, 450, 300, aB)
        ellipse(ctx, 624, 210, 38, 38, SAGE, aB)
        text(ctx, "B", 624, 212, 48, "#FFFFFF", aB)
        plate(ctx, 785, 320, "102", aB, 1.9)
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
    ra = window(T, S(30) - 0.3, S(33) - 0.1, 0.5, 0.5)
    if ra > 0:
        card(ctx, 30, 130, 1020, 1010, ra, "#FBF6EC", 1.0)
        rrect(ctx, 300, 160, 480, 110, 50, OCHRE, ra)
        text(ctx, "Remember", W / 2, 215, 62, "#FFFFFF", ra)
        r1 = ra * prog(T, S(30) + 0.3, S(30) + 0.9)
        rrect(ctx, 100, 310, 880, 350, 36, "#FFFFFF", 0.95 * r1)
        ctx.push_group()
        for j, lab in enumerate(("99", "100", "101", "102")):
            x = 205 + j * 223
            plate(ctx, x, 410, lab, 1.0, 1.25)
            if j < 3:
                text(ctx, "+1", x + 112, 372, 34, GREEN)
        text(ctx, "Past one hundred,", W / 2, 540, 54, INK)
        text(ctx, "keep counting by ones.", W / 2, 608, 54, INK)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(r1)
        r2 = ra * prog(T, S(32), S(32) + 0.6)
        rrect(ctx, 100, 700, 880, 400, 36, "#FFFFFF", 0.95 * r2)
        text(ctx, "Try it at home:", W / 2, 770, 50, "#9C7429", r2)
        text(ctx, "read house numbers", W / 2, 850, 56, INK, r2)
        text(ctx, "on a walk", W / 2, 920, 56, INK, r2)
        for j, (x, lab) in enumerate(((380, "103"), (700, "104"))):
            ctx.move_to(x - 85, 1010)
            ctx.line_to(x, 960)
            ctx.line_to(x + 85, 1010)
            ctx.close_path()
            src(ctx, ("#B4473E", "#7A8BA0")[j], r2)
            ctx.fill()
            rrect(ctx, x - 70, 1008, 140, 76, 6, "#F1E6D2", r2)
            rrect(ctx, x - 16, 1034, 32, 50, 4, "#8B6A4E", r2)
            plate(ctx, x + 112, 1040, lab, r2, 0.75)
    # teaser
    ta = window(T, S(33) - 0.1, ep.total - 1.0, 0.4, 0.5)
    if ta > 0:
        card(ctx, 140, 170, 800, 460, ta)
        rrect(ctx, 330, 200, 420, 100, 46, SAGE, ta)
        text(ctx, "Next case", W / 2, 250, 54, "#FFFFFF", ta)
        # a detective's notebook: a dull word crossed out
        rrect(ctx, 390, 330, 300, 170, 10, "#FFF8E6", ta)
        ctx.set_line_width(2)
        src(ctx, "#9CB7D0", ta)
        for yy in (380, 425, 470):
            ctx.move_to(410, yy)
            ctx.line_to(670, yy)
        ctx.stroke()
        text(ctx, "It was big.", 540, 400, 40, INK, ta)
        ctx.set_line_width(5)
        src(ctx, "#B4473E", ta)
        ctx.move_to(555, 400)
        ctx.line_to(620, 400)
        ctx.stroke()
        text(ctx, "huge? tall?", 540, 452, 34, "#9C7429", ta)
        text(ctx, "A witness who", W / 2, 548, 46, INK, ta)
        text(ctx, "needs better words", W / 2, 600, 46, INK, ta)
