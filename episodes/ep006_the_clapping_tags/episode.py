"""Episode 006: The clapping tags (Kindergarten, English, Phonological awareness).

Setting: the beach on a sunny morning. Two beach buckets look just the same. Mabel marked
each tag with dots, not names: one dot and two dots. Otto can't tell which bucket is his.
A syllable is a beat in a word (lam-ing-ton, three claps). Otto thinks one dot is "O for
Otto". Clapping the names shows Ot-to has two claps and Pip has one, so the two-dot tag is
Otto's. Second proof: the back of the tag says Otto. Funny moment: Otto claps
"Detective Bramble" (five claps) and his paws are tired.

True sizes (K = 16 px per cm): squirrel sitting 20 cm, hedgehog 12 cm tall and 20 cm long,
mouse about 8 cm, lamington 5 to 6 cm. A child's beach bucket is about 15 cm tall and 16 cm
across the top; the card tags are about 7 by 9 cm.
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
NEAR = 1.0
FEET = 1690
OTTO_X, BR_X, IVY_X = 215, 540, 865
GREEN = "#6E8460"
BUCK_Y = 1300                  # sand line the buckets stand on
BUCK_A, BUCK_B = 330, 640      # one-dot bucket (Pip's), two-dot bucket (Otto's)
BUCK_H = 15 * K
TAG_Y = BUCK_Y - 118           # middle of each tag
PIP_X, PIP_Y = 900, 1300
LAM = 5.5 * K                  # lamington side (5.5 cm)

CASE_NO = 6
RULE = "Clap once for each syllable."
SETTING = "the beach"
SENTENCE_LIMIT = 8

LINES = [
    Line("B", "Case open!", gap=0.4),                                        # 0
    Line("O", "Oh no! Which bucket is mine?", gap=0.6),                      # 1
    Line("I", "The tags have dots, not names.", gap=0.8),                    # 2
    Line("N", "Today's case: clapping the syllables in our names.", gap=0.7),  # 3
    Line("N", "A syllable is a beat in a word.", gap=0.8),                   # 4
    Line("N", "It's like lamington.", gap=0.6),                              # 5
    Line("N", "Lam-ing-ton.", gap=1.9),                                      # 6
    Line("N", "Three claps.", gap=1.0),                                      # 7
    Line("O", "One dot! O for Otto! Mine!", gap=0.8),                        # 8
    Line("I", "Hmm. Pip has a bucket too.", gap=0.8),                        # 9
    Line("B", "Let's not guess. Let's test.", gap=0.8),                      # 10
    Line("B", "Can you show me two claps?", gap=4.0),                        # 11
    Line("B", "Which tag has Otto's claps?", gap=0.8),                       # 12
    Line("N", "A. One dot.", gap=0.6),                                       # 13
    Line("N", "B. Two dots.", gap=0.6),                                      # 14
    Line("N", "Pause and think.", gap=5.0),                                  # 15
    Line("N", "Clap once for each syllable.", gap=0.8),                      # 16
    Line("N", "Ot-to.", gap=1.7),                                            # 17
    Line("N", "Two claps for Otto.", gap=0.8),                               # 18
    Line("N", "Pip.", gap=1.2),                                              # 19
    Line("N", "One clap for Pip.", gap=0.8),                                 # 20
    Line("N", "It's B! Two dots.", gap=0.6),                                 # 21
    Line("O", "Oh! The dots are claps!", gap=0.8),                           # 22
    Line("B", "Let's check another way. Flip the tag.", gap=0.8),            # 23
    Line("N", "The back says Otto!", gap=0.8),                               # 24
    Line("I", "Both clues match!", gap=0.8),                                 # 25
    Line("B", "Case solved!", gap=1.9),                                      # 26
    Line("I", "Now clap Detective Bramble.", gap=1.9),                       # 27
    Line("O", "Five claps! My paws are tired!", gap=1.0),                    # 28
    Line("N", "Remember. Clap once for each syllable.", gap=0.9),            # 29
    Line("N", "Say it with me. Clap once for each syllable.", gap=2.2),      # 30
    Line("N", "Try it at home. Clap your own name.", gap=0.9),               # 31
    Line("N", "Next case: the name on a muddy sign.", gap=0.6),              # 32
]

STRIP_HIDDEN = {3, 26, 29}
CHILD_TURN = 30
STAMP_LINE = 26
OPEN_LINE = 0
CUT = [(0, 3), (8, 8), (12, 12), (16, 18), (21, 24), (26, 26), (30, 30), (32, 32)]


def clap_times(ep, i, n, first=0.3, step=0.5):
    """Times of the n claps that echo line i in the silence after it."""
    return [ep.e(i) + first + k * step for k in range(n)]


def claps(ep):
    return {6: clap_times(ep, 6, 3), 17: clap_times(ep, 17, 2, 0.3, 0.6),
            19: clap_times(ep, 19, 1, 0.35), 27: clap_times(ep, 27, 5, 0.25, 0.33)}


# ---------------------------------------------------------------- props
def coconut(ctx, x0, y0, w, h, a, seed=1):
    for i in range(int(w * h / 160)):
        u = ((i * 37 + seed * 11) % 97) / 97.0
        v = ((i * 61 + seed * 7) % 89) / 89.0
        ellipse(ctx, x0 + 4 + u * (w - 8), y0 + 4 + v * (h - 8), 2.6, 2.0, "#F6EFE2", 0.9 * a)


def lamington(ctx, x, y, a=1.0, sc=1.0, seed=1):
    """A lamington cube; (x, y) is the middle of its bottom edge."""
    if a <= 0:
        return
    s = LAM * sc
    rig.soft_shadow(ctx, x + 4, y + 2, s * 0.6, 6 * sc, 0.25 * a)
    top = s * 0.28
    rrect(ctx, x - s / 2, y - s, s, s, 10 * sc, "#6B4430", a)
    rrect(ctx, x - s / 2 + 4, y - s - top + 8, s - 8, top + 8, 10 * sc, "#86573D", a)
    src(ctx, "#000000", 0.10 * a)
    ctx.rectangle(x + s * 0.18, y - s + 6, s * 0.32 - 4, s - 12)
    ctx.fill()
    coconut(ctx, x - s / 2, y - s - top + 8, s, s + top - 8, a, seed)


def word_chip(ctx, s, x, y, a, col=INK, bg="#FFFFFF", size=46):
    w = 40 + 0.56 * size * len(s)
    rrect(ctx, x - w / 2, y - 36, w, 72, 36, bg, 0.97 * a)
    text(ctx, s, x, y + 1, size, col, a)


def arrow(ctx, x0, x1, y, a):
    ctx.set_line_width(7)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    src(ctx, GREEN, a)
    ctx.move_to(x0, y)
    ctx.line_to(x1, y)
    ctx.move_to(x1 - 16, y - 14)
    ctx.line_to(x1, y)
    ctx.line_to(x1 - 16, y + 14)
    ctx.stroke()


def tag(ctx, x, y, dots, flip=0.0, a=1.0, sc=1.0, name="Otto"):
    """A card tag with clap dots; flip 0..1 turns it over to show the name on the back."""
    if a <= 0:
        return
    sx = abs(math.cos(math.pi * flip))
    w, h = 124 * sc * max(sx, 0.04), 150 * sc
    rig.soft_shadow(ctx, x + 4, y + h / 2 + 4, w * 0.5, 6, 0.18 * a)
    rrect(ctx, x - w / 2, y - h / 2, w, h, 14 * sc, "#FFFDF6", a)
    ellipse(ctx, x, y - h / 2 + 18 * sc, 7 * sc * max(sx, 0.2), 7 * sc, "#B9A98F", a)
    if flip < 0.5:
        for k in range(dots):
            dx = (k - (dots - 1) / 2) * 52 * sc * sx
            ellipse(ctx, x + dx, y + 14 * sc, 21 * sc * sx, 21 * sc, INK, a)
    elif sx > 0.3:
        ctx.save()
        ctx.translate(x, y + 14 * sc)
        ctx.scale(sx, 1)
        text(ctx, name, 0, 0, 40 * sc, INK, a)
        ctx.restore()


def bucket(ctx, x, dots, flip=0.0):
    """A child's beach bucket standing on the sand, with its tag hanging on the front."""
    y, h = BUCK_Y, BUCK_H
    tw, bw = 8 * K, 5.6 * K
    rig.soft_shadow(ctx, x + 8, y + 4, bw * 1.2, 16, 0.24)
    g = cairo.LinearGradient(x - tw, 0, x + tw, 0)
    g.add_color_stop_rgb(0, *R.rgb("#A9CBDA"))
    g.add_color_stop_rgb(0.45, *R.rgb("#8FB4C8"))
    g.add_color_stop_rgb(1, *R.rgb("#6F97AD"))
    ctx.set_source(g)
    ctx.move_to(x - tw, y - h)
    ctx.line_to(x + tw, y - h)
    ctx.line_to(x + bw, y - 10)
    ctx.curve_to(x + bw, y + 6, x - bw, y + 6, x - bw, y - 10)
    ctx.close_path()
    ctx.fill()
    ellipse(ctx, x, y - h, tw, 20, "#7CA3B8")
    ellipse(ctx, x, y - h + 3, tw - 12, 13, "#E2D0A8")       # sand inside
    rrect(ctx, x - tw - 4, y - h - 4, 2 * tw + 8, 16, 8, "#BBD7E3")
    # handle resting on the front, with the tag string
    ctx.set_line_width(7)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    src(ctx, "#F4EEE3")
    ctx.move_to(x - tw + 6, y - h + 12)
    ctx.curve_to(x - tw * 0.6, y - h + 78, x + tw * 0.6, y - h + 78, x + tw - 6, y - h + 12)
    ctx.stroke()
    ctx.set_line_width(3)
    src(ctx, "#8E7F70")
    ctx.move_to(x, y - h + 60)
    ctx.line_to(x, TAG_Y - 60)
    ctx.stroke()
    tag(ctx, x, TAG_Y, dots, flip)


def clap_dot(ctx, x, y, r, t, tk, a=1.0, col=OCHRE):
    """A clap mark that pops in at time tk."""
    p = prog(t, tk - 0.05, tk + 0.12)
    if p <= 0 or a <= 0:
        return
    bump = 1 + 0.35 * max(0.0, 1 - abs(t - tk - 0.12) / 0.2)
    ellipse(ctx, x, y, r * bump, r * bump, col, a * p)


def muddy_sign(ctx, x, y, a):
    rrect(ctx, x - 10, y - 10, 20, 150, 6, "#8E6F5E", a)
    rrect(ctx, x - 190, y - 100, 380, 120, 16, "#C9A77C", a)
    rrect(ctx, x - 178, y - 88, 356, 96, 12, "#E6CFA6", a)
    text(ctx, "op", x + 70, y - 38, 76, INK, a)
    for dx, dy, rx, ry in ((-90, -44, 78, 40), (-40, -22, 46, 26), (-128, -18, 34, 20)):
        ellipse(ctx, x + dx, y + dy, rx, ry, "#7A5A40", a)
    ellipse(ctx, x - 104, y - 56, 16, 9, "#9A7658", 0.8 * a)


# ---------------------------------------------------------------- background
def beach(ctx):
    g = cairo.LinearGradient(0, 0, 0, 620)
    g.add_color_stop_rgb(0, *R.rgb("#C6DEEA"))
    g.add_color_stop_rgb(1, *R.rgb("#EAF1EA"))
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, 620)
    ctx.fill()
    drift = NOW[0] * 5
    for cx0, cy0, cw in ((240, 150, 120), (800, 250, 140)):
        cx = (cx0 + drift) % 1500 - 200
        ellipse(ctx, cx, cy0, cw, cw * 0.34, "#FFFFFF", 0.75)
        ellipse(ctx, cx + cw * 0.4, cy0 - cw * 0.18, cw * 0.55, cw * 0.3, "#FFFFFF", 0.75)
    # sea with slow soft wave lines
    g = cairo.LinearGradient(0, 610, 0, 800)
    g.add_color_stop_rgb(0, *R.rgb("#7FB3C4"))
    g.add_color_stop_rgb(1, *R.rgb("#A8D0D6"))
    ctx.set_source(g)
    ctx.rectangle(0, 610, W, 200)
    ctx.fill()
    ctx.set_line_width(4)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(7):
        yy = 640 + i * 22
        xx = (i * 173 + NOW[0] * (6 + i)) % 1300 - 150
        src(ctx, "#FFFFFF", 0.35)
        ctx.move_to(xx, yy)
        ctx.curve_to(xx + 40, yy - 8, xx + 80, yy + 8, xx + 130, yy)
        ctx.stroke()
    # sand
    g = cairo.LinearGradient(0, 790, 0, 1920)
    g.add_color_stop_rgb(0, *R.rgb("#EFE3C6"))
    g.add_color_stop_rgb(1, *R.rgb("#E2D0A8"))
    ctx.set_source(g)
    ctx.rectangle(0, 800, W, 1920 - 800)
    ctx.fill()
    fo = 6 * math.sin(NOW[0] * 0.8)
    ctx.set_line_width(14)
    src(ctx, "#FFFFFF", 0.8)
    ctx.move_to(-20, 800 + fo)
    ctx.curve_to(260, 786 + fo, 520, 816 + fo, 800, 800 + fo)
    ctx.curve_to(920, 792 + fo, 1010, 806 + fo, 1100, 800 + fo)
    ctx.stroke()
    # beach umbrella and towel, further back
    rrect(ctx, 790, 912, 270, 40, 10, "#F4EEE3")
    src(ctx, "#C9605A", 0.55)
    for xx in range(790, 1060, 60):
        ctx.rectangle(xx, 912, 30, 40)
    ctx.fill()
    rrect(ctx, 856, 600, 10, 320, 4, "#B9A98F")
    for k, col in enumerate(("#C9605A", "#F4EEE3", "#C9605A", "#F4EEE3", "#C9605A")):
        a0 = math.pi + k * math.pi / 5
        ctx.move_to(861, 640)
        ctx.arc(861, 640, 160, a0, a0 + math.pi / 5)
        ctx.close_path()
        src(ctx, col)
        ctx.fill()
    # sandcastle, further back on the left
    for cx, cw, ch in ((150, 150, 70), (105, 46, 120), (195, 46, 120), (150, 56, 150)):
        rrect(ctx, cx - cw / 2, 960 - ch, cw, ch, 8, "#DCC592")
    src(ctx, "#C9605A")
    ctx.move_to(150, 810)
    ctx.line_to(150, 776)
    ctx.line_to(178, 786)
    ctx.line_to(150, 796)
    ctx.close_path()
    ctx.fill()
    rig.soft_shadow(ctx, 150, 962, 90, 8, 0.15)
    # shells and sand speckles
    for i in range(18):
        xb = 40 + (i * 167) % 1000
        yb = 1390 + (i * 97) % 280
        ellipse(ctx, xb, yb, 5, 3, "#D2BE93", 0.7)
    for sx_, sy_ in ((470, 1010), (980, 1120), (60, 1180)):
        ellipse(ctx, sx_, sy_, 14, 10, "#F6E7DA")
        ellipse(ctx, sx_ - 3, sy_ - 2, 6, 4, "#E9C9B8")


# ---------------------------------------------------------------- scene
def scene(ctx, ep, T):
    S, E = ep.s, ep.e
    beach(ctx)
    d = E(23) - S(23)
    flip = prog(T, S(23) + 0.55 * d, S(23) + 0.55 * d + 0.9)
    bucket(ctx, BUCK_A, 1)
    bucket(ctx, BUCK_B, 2, flip)
    R.mouse(ctx, PIP_X, PIP_Y, 1.3, -1)
    rig.squirrel(ctx, OTTO_X, FEET, SQ_S, OCHRE, f=1, seed=2.0)
    rig.bramble(ctx, BR_X, FEET, BR_S, f=1)
    rig.squirrel(ctx, IVY_X, FEET, SQ_S, SAGE, f=-1, seed=0.7)


# ---------------------------------------------------------------- cues, poses, foley
def cues(ep):
    return [
        ("ring", ep.s(1) - 0.1, ep.e(2) + 0.5, 485, TAG_Y, 260, 115),
        ("zoom", ep.s(8) - 0.2, ep.e(9) + 0.5, 545, 1200, 1.1),
        ("ring", ep.s(12) - 0.1, ep.e(12) + 0.5, 485, TAG_Y, 260, 115),
        ("zoom", ep.s(17) - 0.3, ep.e(20) + 0.4, 500, 1150, 1.1),
        ("ring", ep.s(21) - 0.1, ep.e(21) + 0.5, BUCK_B, TAG_Y, 100, 110),
        ("lens", ep.s(24) - 0.3, ep.e(24) + 0.9, BUCK_B, TAG_Y + 10, 540, 760, 150, 2.2),
    ]


def foley(ep):
    out = [("whoosh", ep.s(3) - 0.3), ("whoosh", ep.s(4) - 0.3), ("whoosh", ep.s(13) - 0.3)]
    for ts in claps(ep).values():
        out += [("pop", t) for t in ts]
    out.append(("step", ep.s(26) + 0.5))
    return out


def poses(ep, T):
    S, E = ep.s, ep.e

    def during(i, pre=0.2, post=0.6):
        return S(i) - pre <= T <= E(i) + post

    def ramp(t0):
        return prog(T, t0, t0 + 0.5)

    tag_a = (BUCK_A, TAG_Y)
    tag_b = (BUCK_B, TAG_Y)
    B = {"face": 1}
    O = {"face": 1}
    I = {"face": -1}
    if T < S(3):
        O["expr"] = "sad"
    if during(1, 0.1, 0.3):
        O.update(point=tag_a, amt=ramp(S(1)))
    if during(2, 0.1, 0.4):
        I.update(expr="think", point=tag_b, amt=ramp(S(2)))
    if during(8, 0.3, 0.4):
        O.update(expr="happy", point=tag_a, amt=ramp(S(8) - 0.3))
    if during(9, 0.2, 0.8):
        I.update(expr="think", point=(PIP_X - 40, PIP_Y - 60), amt=ramp(S(9) - 0.2))
        O["expr"] = "think"
    if S(10) - 0.2 <= T <= E(11) + 3.8:
        B["expr"] = "think" if T < S(11) else "happy"
    if S(12) <= T <= S(16):
        O["expr"] = I["expr"] = "think"
    if S(16) - 0.2 <= T <= E(16) + 0.6:
        B["expr"] = "think"
    if S(17) - 0.1 <= T <= E(18) + 0.4:
        B.update(expr="happy", point=tag_b, amt=ramp(S(17) - 0.1))
    if during(21, 0.2, 0.3):
        I["expr"] = "happy"
    if during(22, 0.2, 0.8):
        O["expr"] = "surprise"
        O["scratch"] = prog(T, S(22) + 0.3, S(22) + 0.8) * (1 - prog(T, E(22) + 0.4, E(22) + 0.8))
    if S(23) - 0.2 <= T <= E(24) + 0.4:
        B.update(expr="think", point=tag_b, amt=ramp(S(23) - 0.2))
    if during(25, 0.2, 0.6):
        I["expr"] = "happy"
    if T >= S(26) - 0.2:
        B["expr"] = O["expr"] = I["expr"] = "happy"
        hop = (T - S(26)) / 0.55
        if 0 <= hop <= 1:
            O["jump"] = 42 * math.sin(math.pi * hop)
    if during(28, 0.1, 0.5):
        O["expr"] = "surprise"
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


def name_claps(ctx, parts, cx, y, T, times, a, size=46, gapx=150):
    """Name chips, one per syllable, each with a clap dot that pops under it."""
    n = len(parts)
    for j, p in enumerate(parts):
        x = cx + (j - (n - 1) / 2) * gapx
        on = prog(T, times[j] - 0.05, times[j] + 0.15) if times else 1.0
        word_chip(ctx, p, x, y, a * (0.35 + 0.65 * on), INK, "#FBF1DC", size)
        if times:
            clap_dot(ctx, x, y + 62, 15, T, times[j], a)
        else:
            ellipse(ctx, x, y + 62, 15, 15, OCHRE, a)


def cards(ctx, ep, T):
    S, E = ep.s, ep.e
    cl = claps(ep)
    # Today's case title (read word for word)
    a = window(T, S(3) - 0.3, E(3) + 0.9)
    if a > 0:
        card(ctx, 70, 140, 940, 420, a)
        rrect(ctx, 120, 184, 60, 46, 8, OCHRE, a)
        rrect(ctx, 120, 176, 28, 14, 5, OCHRE, a)
        text(ctx, "Today's case", 560, 210, 46, "#9C7429", a)
        for k, s_ in enumerate(("Clapping the syllables", "in our names")):
            text(ctx, s_, W / 2, 330 + k * 92, 68, INK, a)
    # a syllable is a beat: lam-ing-ton
    a = window(T, S(4) - 0.2, E(7) + 1.0)
    if a > 0:
        card(ctx, 70, 140, 940, 420, a)
        text(ctx, "Syllable = a beat in a word", W / 2, 196, 44, "#9C7429", a)
        b = prog(T, S(5) - 0.1, S(5) + 0.3)
        lamington(ctx, W / 2, 392, a * b, 1.3, 3)
        if T >= S(6) - 0.2:
            name_claps(ctx, ("Lam", "ing", "ton"), W / 2, 462, T, cl[6], a * prog(T, S(6) - 0.2, S(6) + 0.1), 46, 210)
    # show me two claps
    a = window(T, S(11) - 0.1, E(11) + 3.9)
    if a > 0:
        card(ctx, 290, 190, 500, 260, a)
        for k in range(2):
            ph = (T - S(11)) * 1.2 - k * 0.5
            pulse = 1 + 0.18 * max(0.0, math.sin(2 * math.pi * ph)) ** 6
            ellipse(ctx, 440 + k * 200, 320, 62 * pulse, 62 * pulse, OCHRE, a)
    # A or B
    aA = window(T, S(13) - 0.2, E(21) + 1.4)
    if aA > 0:
        aA2 = aA * prog(T, S(13) - 0.2, S(13) + 0.2)
        aB = aA * prog(T, S(14) - 0.2, S(14) + 0.2)
        d = E(21) - S(21)
        picked = prog(T, S(21) + 0.2 * d, S(21) + 0.2 * d + 0.4)
        ak = aA2 * (1 - 0.5 * picked)
        card(ctx, 70, 150, 450, 300, aA2)
        ellipse(ctx, 134, 210, 38, 38, OCHRE, ak)
        text(ctx, "A", 134, 212, 48, "#FFFFFF", ak)
        rrect(ctx, 228, 196, 204, 228, 24, "#EFE3C6", ak)
        tag(ctx, 330, 310, 1, 0.0, ak, 1.3)
        card(ctx, 560, 150, 450, 300, aB)
        ellipse(ctx, 624, 210, 38, 38, SAGE, aB)
        text(ctx, "B", 624, 212, 48, "#FFFFFF", aB)
        rrect(ctx, 718, 196, 204, 228, 24, "#EFE3C6", aB)
        tag(ctx, 820, 310, 2, 0.0, aB, 1.3)
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
    # the names clapped, each above its own bucket
    a = window(T, S(17) - 0.2, E(21) + 1.0)
    if a > 0:
        name_claps(ctx, ("Ot", "to"), BUCK_B, 900, T, cl[17], a, 46, 130)
    a = window(T, S(19) - 0.2, E(21) + 1.0)
    if a > 0:
        name_claps(ctx, ("Pip",), BUCK_A, 900, T, cl[19], a, 46)
    # five claps for Detective Bramble
    a = window(T, S(27) - 0.1, E(28) + 0.5, 0.3, 0.4)
    if a > 0:
        card(ctx, 110, 210, 860, 250, a)
        name_claps(ctx, ("De", "tec", "tive", "Bram", "ble"), W / 2, 300, T, cl[27], a, 40, 160)
    # recap
    ra = window(T, S(29) - 0.3, S(32) - 0.1, 0.5, 0.5)
    if ra > 0:
        card(ctx, 30, 130, 1020, 900, ra, "#FBF6EC", 1.0)
        rrect(ctx, 300, 160, 480, 110, 50, OCHRE, ra)
        text(ctx, "Remember", W / 2, 215, 62, "#FFFFFF", ra)
        r1 = ra * prog(T, S(29) + 0.3, S(29) + 0.9)
        rrect(ctx, 100, 300, 880, 320, 36, "#FFFFFF", 0.95 * r1)
        ctx.push_group()
        name_claps(ctx, ("Ot", "to"), W / 2, 372, T, None, 1.0, 46, 150)
        text(ctx, "Clap once for", W / 2, 506, 56, INK)
        text(ctx, "each syllable.", W / 2, 574, 56, INK)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(r1)
        r2 = ra * prog(T, S(31), S(31) + 0.6)
        rrect(ctx, 100, 650, 880, 350, 36, "#FFFFFF", 0.95 * r2)
        text(ctx, "Try it at home:", W / 2, 712, 50, "#9C7429", r2)
        text(ctx, "clap your own name", W / 2, 796, 56, INK, r2)
        ctx.push_group()
        name_claps(ctx, ("I", "vy"), W / 2, 888, T, None, 1.0, 44, 150)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(r2)
    # teaser
    ta = window(T, S(32) - 0.1, ep.total - 1.0, 0.4, 0.5)
    if ta > 0:
        card(ctx, 140, 170, 800, 460, ta)
        rrect(ctx, 330, 200, 420, 100, 46, SAGE, ta)
        text(ctx, "Next case", W / 2, 250, 54, "#FFFFFF", ta)
        ctx.push_group()
        muddy_sign(ctx, W / 2, 430, 1.0)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(ta)
        text(ctx, "The name on a muddy sign", W / 2, 586, 44, INK, ta)
