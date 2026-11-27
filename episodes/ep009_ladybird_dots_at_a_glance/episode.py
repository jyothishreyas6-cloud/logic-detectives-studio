"""Episode 009: Ladybird dots at a glance (Kindergarten, Maths, Representing whole numbers:
seeing small groups at a glance, subitising).

Setting: Mabel's veggie patch, morning. Mabel painted a garden stepping stone as a ladybird
with four dots, two on each wing. Ivy says "four" at once; Otto calls it unfair and counts,
but touches the first dot twice and gets five. At a glance means one quick look, like the
dots on a dice. Test: two dots on this wing, two on that wing, two and two make four (seen,
not counted). Second proof: touch each dot only once, one, two, three, four. Funny moment: a
real ladybird lands on Otto's nose and he asks it to count.

True sizes (K = 16 px per cm): squirrel sitting 20 cm, hedgehog 12 cm tall and 20 cm long.
Round garden stepping stone 30 cm across (480 px). A real ladybird is about 7 mm long; the
one on Otto's nose is drawn about 1 cm (it is nearer the camera). A dice is 16 mm (cards
show it enlarged as a picture).
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
STONE = (540, 1000)            # middle of the stepping stone (30 cm across)
STONE_R = 240
BUG = (540, 1020)              # middle of the painted ladybird's body
DOTS = [(460, 970), (468, 1080), (620, 970), (612, 1080)]   # two dots on each wing
OTTO_TAPS = [0, 1, 2, 3, 0]    # Otto's count: he touches the first dot again
TAP_BADGE = [(388, 970), (396, 1080), (692, 970), (684, 1080)]
FIFTH_BADGE = (430, 898)       # where Otto's "5" sits (above the first dot)
NOSE = (OTTO_X + 70, 1476)     # tip of Otto's nose (he faces right)

CASE_NO = 9
RULE = "You can see small groups without counting."
SETTING = "Mabel's veggie patch"
SENTENCE_LIMIT = 8

LINES = [
    Line("B", "Case open!", gap=0.4),                                          # 0
    Line("O", "Hey! That's not fair! Ivy didn't count!", gap=0.6),             # 1
    Line("I", "I didn't need to. I just saw it.", gap=0.7),                    # 2
    Line("N", "Today's case: ladybird dots at a glance.", gap=0.7),            # 3
    Line("N", "At a glance means one quick look.", gap=0.7),                   # 4
    Line("N", "Like the dots on a dice.", gap=1.0),                            # 5
    Line("N", "Mabel painted this ladybird stepping stone.", gap=0.6),         # 6
    Line("N", "How many dots does it have?", gap=0.8),                         # 7
    Line("O", "I'll count. One, two, three, four, five!", gap=0.6),            # 8
    Line("I", "Hmm. I saw four at a glance.", gap=0.6),                        # 9
    Line("O", "Four? You guessed!", gap=0.8),                                  # 10
    Line("B", "Let's not guess. Let's test.", gap=0.8),                        # 11
    Line("B", "Can you point to the dots?", gap=3.5),                          # 12
    Line("B", "How many dots? Take a quick look.", gap=0.8),                   # 13
    Line("N", "A. Five dots.", gap=0.6),                                       # 14
    Line("N", "B. Four dots.", gap=0.6),                                       # 15
    Line("N", "Pause and think.", gap=5.0),                                    # 16
    Line("N", "You can see small groups without counting.", gap=1.0),          # 17
    Line("N", "Two dots on this wing.", gap=0.8),                              # 18
    Line("N", "Two dots on that wing.", gap=0.8),                              # 19
    Line("N", "Two and two make four.", gap=1.0),                              # 20
    Line("N", "It's B! Four dots.", gap=0.6),                                  # 21
    Line("O", "Oh! I touched one dot twice!", gap=0.8),                        # 22
    Line("B", "Let's check another way.", gap=0.6),                            # 23
    Line("N", "Touch each dot only once.", gap=0.6),                           # 24
    Line("N", "One, two, three, four.", gap=0.8),                              # 25
    Line("I", "Four! Same as my quick look!", gap=0.8),                        # 26
    Line("B", "Case solved!", gap=1.9),                                        # 27
    Line("O", "Hello, tiny ladybird! Can you count?", gap=0.6),                # 28
    Line("I", "Ladybirds can't count, Otto!", gap=0.8),                        # 29
    Line("N", "Remember. You can see small groups without counting.", gap=0.9),  # 30
    Line("N", "Say it with me. You can see small groups without counting.", gap=2.2),  # 31
    Line("N", "Try it at home. Roll a dice. Say the number fast!", gap=0.9),   # 32
    Line("N", "Next case: the shuffled clue cards.", gap=0.6),                 # 33
]

STRIP_HIDDEN = {3, 27, 30}
CHILD_TURN = 31
STAMP_LINE = 27
OPEN_LINE = 0
CUT = [(0, 3), (8, 10), (17, 22), (27, 27), (31, 31), (33, 33)]


# ---------------------------------------------------------------- props
def letter(ctx, s, x, base, size, col=INK, a=1.0):
    """One glyph centred on x, sitting on a shared baseline (so digits line up)."""
    if a <= 0:
        return
    ctx.select_font_face(R.FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    xb, yb, tw, th, xa, _ = ctx.text_extents(s)
    ctx.move_to(x - tw / 2 - xb, base)
    src(ctx, col, a)
    ctx.show_text(s)


def badge(ctx, x, y, s, a, col=INK, r=26):
    if a <= 0:
        return
    ellipse(ctx, x, y + 2, r, r, "#000000", 0.12 * a)
    ellipse(ctx, x, y, r, r, "#FFFFFF", 0.97 * a)
    ctx.set_line_width(3)
    src(ctx, "#E3D6BF", a)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.stroke()
    text(ctx, s, x, y + 1, r * 1.15, col, a)


PIPS = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)],
        4: [(-1, -1), (1, -1), (-1, 1), (1, 1)], 5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)],
        6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]}


def dice(ctx, x, y, s, n, a=1.0):
    """A dice face (picture on a card); (x, y) is its middle, s its width."""
    if a <= 0:
        return
    rig.soft_shadow(ctx, x + 4, y + s / 2, s * 0.45, s * 0.06, 0.16 * a)
    rrect(ctx, x - s / 2, y - s / 2, s, s, s * 0.18, "#D9CDB8", a)
    rrect(ctx, x - s / 2 + 4, y - s / 2 + 4, s - 8, s - 8, s * 0.16, "#FFFFFF", a)
    for px, py in PIPS[n]:
        ellipse(ctx, x + px * s * 0.27, y + py * s * 0.27, s * 0.09, s * 0.09, INK, a)


def painted_ladybird(ctx, cx, cy, sc=1.0, a=1.0):
    """The ladybird painted on the stone: four dots, two on each wing; (cx, cy) is the body."""
    if a <= 0:
        return
    ellipse(ctx, cx, cy - 152 * sc, 60 * sc, 56 * sc, INK, a)                 # head
    ellipse(ctx, cx - 24 * sc, cy - 170 * sc, 11 * sc, 11 * sc, "#FFFFFF", a)
    ellipse(ctx, cx + 24 * sc, cy - 170 * sc, 11 * sc, 11 * sc, "#FFFFFF", a)
    ellipse(ctx, cx, cy, 175 * sc, 150 * sc, "#C9473F", a)
    ellipse(ctx, cx - 70 * sc, cy - 80 * sc, 60 * sc, 26 * sc, "#FFFFFF", 0.22 * a)
    rrect(ctx, cx - 4 * sc, cy - 146 * sc, 8 * sc, 292 * sc, 4 * sc, INK, a)
    for dx, dy in ((-80, -50), (-72, 60), (80, -50), (72, 60)):
        ellipse(ctx, cx + dx * sc, cy + dy * sc, 32 * sc, 32 * sc, INK, a)


def tiny_ladybird(ctx, x, y, a=1.0, r=10):
    """A real ladybird (drawn about 1 cm, a little nearer the camera)."""
    if a <= 0:
        return
    ellipse(ctx, x - r * 0.9, y, r * 0.45, r * 0.45, INK, a)
    ellipse(ctx, x, y, r, r * 0.8, "#C9473F", a)
    ellipse(ctx, x - r * 0.35, y - r * 0.35, r * 0.18, r * 0.18, INK, a)
    ellipse(ctx, x + r * 0.35, y + r * 0.3, r * 0.18, r * 0.18, INK, a)


def stone(ctx):
    """Round garden stepping stone, 30 cm across, lying on the lawn."""
    x, y = STONE
    rig.soft_shadow(ctx, x + 6, y + STONE_R * 0.95, STONE_R * 0.95, 26, 0.24)
    ellipse(ctx, x, y + 10, STONE_R, STONE_R * 0.96, "#9E968A")
    ellipse(ctx, x, y, STONE_R, STONE_R * 0.96, "#C4BCAF")
    ellipse(ctx, x - 70, y - 90, 120, 60, "#FFFFFF", 0.12)
    painted_ladybird(ctx, *BUG)


def clue_card(ctx, x, y, s, a, rot):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    rig.soft_shadow(ctx, 4, 70, 60, 8, 0.16 * a)
    rrect(ctx, -60, -76, 120, 152, 14, "#FBF1DC", a)
    ctx.set_line_width(4)
    src(ctx, "#D9C49A", a)
    ctx.rectangle(-50, -66, 100, 132)
    ctx.stroke()
    text(ctx, s, 0, 2, 76, INK, a)
    ctx.restore()


# ---------------------------------------------------------------- background
def garden(ctx, T, ep):
    g = cairo.LinearGradient(0, 0, 0, 600)
    g.add_color_stop_rgb(0, *R.rgb("#C6DFEA"))
    g.add_color_stop_rgb(1, *R.rgb("#EEF3E6"))
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, 640)
    ctx.fill()
    ellipse(ctx, 890, 140, 70, 70, "#FFF4D6", 0.9)                     # morning sun
    drift = NOW[0] * 5
    for cx0, cy0, cw in ((260, 150, 120), (700, 230, 100)):
        cx = (cx0 + drift) % 1300 - 100
        ellipse(ctx, cx, cy0, cw, cw * 0.3, "#FFFFFF", 0.75)
    # timber paling fence
    rrect(ctx, 0, 336, W, 264, 0, "#A88B6C")
    for k in range(14):
        rrect(ctx, k * 80 + 4, 320, 72, 290, 6, "#C2A583")
    rrect(ctx, 0, 380, W, 16, 0, "#987B5E")
    rrect(ctx, 0, 520, W, 16, 0, "#987B5E")
    # Mabel's raised veggie bed: lettuces, carrots tops and a tomato stake
    rrect(ctx, 40, 560, 1000, 120, 14, "#8E6F52")
    rrect(ctx, 56, 570, 968, 40, 10, "#6F5440")
    for k in range(6):
        lx = 120 + k * 160
        ellipse(ctx, lx, 566, 54, 34, "#7FA36A")
        ellipse(ctx, lx - 14, 556, 30, 20, "#A3C28A")
    for k in range(5):
        tx = 200 + k * 160
        for d in (-10, 0, 10):
            ctx.set_line_width(5)
            src(ctx, "#6E9858")
            ctx.move_to(tx, 566)
            ctx.line_to(tx + d * 1.6, 520)
            ctx.stroke()
    rrect(ctx, 986, 400, 10, 170, 3, "#8E7F70")
    for ty in (430, 470, 510):
        ellipse(ctx, 1004, ty, 14, 14, "#D9634F")
    # lawn
    g = cairo.LinearGradient(0, 680, 0, 1920)
    g.add_color_stop_rgb(0, *R.rgb("#A7C088"))
    g.add_color_stop_rgb(1, *R.rgb("#8FA971"))
    ctx.set_source(g)
    ctx.rectangle(0, 680, W, 1240)
    ctx.fill()
    ctx.set_line_width(3)
    src(ctx, "#7F9A62", 0.7)
    for gx, gy in ((90, 760), (980, 800), (130, 1330), (960, 1300), (300, 1560), (780, 1580)):
        for d in (-8, 0, 8):
            ctx.move_to(gx, gy)
            ctx.line_to(gx + d, gy - 22)
        ctx.stroke()


# ---------------------------------------------------------------- the count on the stone
def word_t(ep, i, j, n):
    s, e = ep.s(i), ep.e(i)
    return s + (j + 0.25) / n * (e - s)


def otto_badges(ctx, ep, T):
    """Otto's count: 1 to 4, then a "5" when he touches the first dot again."""
    S, E = ep.s, ep.e
    vis = (1 - prog(T, S(11) - 0.4, S(11))) if T < S(12) else window(T, S(22) - 0.2, E(22) + 0.8)
    if vis <= 0:
        return
    for k, d in enumerate(OTTO_TAPS):
        t = word_t(ep, 8, 2 + k, 7)
        b = vis * prog(T, t, t + 0.25) if T < S(12) else vis
        x, y = FIFTH_BADGE if k == 4 else TAP_BADGE[d]
        badge(ctx, x, y, str(k + 1), b, "#9C7429")


def check_badges(ctx, ep, T):
    """Second proof: touch each dot only once (green 1 to 4)."""
    S, E = ep.s, ep.e
    vis = window(T, S(25) - 0.1, E(26) + 0.8)
    for k in range(4):
        t = word_t(ep, 25, k, 4)
        badge(ctx, *TAP_BADGE[k], str(k + 1), vis * prog(T, t, t + 0.25), GREEN)


def bug_path(ep, T):
    """The real ladybird flies in to Otto's nose after the stamp and flies off later."""
    S, E = ep.s, ep.e
    t0, t1 = S(28) - 1.6, S(28) - 0.3
    t2, t3 = E(29) + 0.4, E(29) + 1.6
    if T < t0 or T > t3:
        return None
    if T <= t1:
        p = ease(prog(T, t0, t1))
        x, y = lerp(990, NOSE[0], p), lerp(1180, NOSE[1], p) - 90 * math.sin(math.pi * p)
    elif T <= t2:
        x, y = NOSE
    else:
        p = ease(prog(T, t2, t3))
        x, y = lerp(NOSE[0], 1040, p), lerp(NOSE[1], 760, p) - 60 * math.sin(math.pi * p)
    return x, y


# ---------------------------------------------------------------- scene
def scene(ctx, ep, T):
    garden(ctx, T, ep)
    stone(ctx)
    otto_badges(ctx, ep, T)
    check_badges(ctx, ep, T)
    rig.squirrel(ctx, OTTO_X, FEET, SQ_S, OCHRE, f=1, seed=2.0)
    rig.bramble(ctx, BR_X, FEET, BR_S, f=1)
    rig.squirrel(ctx, IVY_X, FEET, SQ_S, SAGE, f=-1, seed=0.7)
    p = bug_path(ep, T)
    if p:
        tiny_ladybird(ctx, *p)


# ---------------------------------------------------------------- cues, poses, foley
def cues(ep):
    return [
        ("ring", ep.s(1) - 0.1, ep.e(2) + 0.5, STONE[0], STONE[1] - 20, 270, 270),
        ("zoom", ep.s(8) - 0.2, ep.e(10) + 0.5, 540, 1100, 1.1),
        ("ring", ep.s(12) - 0.1, ep.e(12) + 3.8, BUG[0], BUG[1] - 20, 230, 220),
        ("ring", ep.s(18) - 0.1, ep.e(18) + 0.4, 464, 1025, 90, 118),
        ("ring", ep.s(19) - 0.1, ep.e(19) + 0.4, 616, 1025, 90, 118),
        ("ring", ep.s(22) - 0.1, ep.e(22) + 0.6, 424, 940, 92, 92),
        ("zoom", ep.s(28) - 0.4, ep.e(29) + 0.6, OTTO_X + 60, 1420, 1.15),
    ]


def foley(ep):
    S = ep.s
    out = [("whoosh", S(3) - 0.3), ("whoosh", S(4) - 0.3), ("whoosh", S(14) - 0.3)]
    out += [("pop", word_t(ep, 8, 2 + k, 7)) for k in range(5)]
    out += [("pop", word_t(ep, 25, k, 4)) for k in range(4)]
    out.append(("step", S(27) + 0.5))
    out.append(("whoosh", S(28) - 1.5))
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
        O["expr"] = "sad"
    if during(1, 0.1, 0.3):
        O.update(point=(430, 1040), amt=ramp(S(1)))
    if during(2, 0.1, 0.4):
        I.update(expr="happy", point=(650, 1040), amt=ramp(S(2)))
    if S(8) - 0.3 <= T <= E(8) + 0.4:
        O.update(expr="happy", point=(440, 1060), amt=ramp(S(8) - 0.3))
    if during(9, 0.2, 0.4):
        I.update(expr="think", point=(650, 1040), amt=ramp(S(9) - 0.2))
    if during(10, 0.2, 0.6):
        O["expr"] = "think"
    if S(11) - 0.2 <= T <= E(12) + 3.8:
        B["expr"] = "think" if T < S(12) else "happy"
    if S(12) - 0.1 <= T <= E(12) + 3.6:
        B.update(point=(700, 1080), amt=ramp(S(12) - 0.1))
    if S(13) <= T <= S(17):
        O["expr"] = I["expr"] = "think"
    if during(17, 0.2, 0.6):
        B["expr"] = "think"
    if S(18) - 0.1 <= T <= E(20) + 0.4:
        B.update(expr="happy", point=(700, 1080), amt=ramp(S(18) - 0.1))
    if during(21, 0.2, 0.3):
        I["expr"] = "happy"
    if during(22, 0.2, 0.8):
        O["expr"] = "surprise"
        O["scratch"] = prog(T, S(22) - 0.1, S(22) + 0.4) * (1 - prog(T, E(22) + 0.3, E(22) + 0.8))
    if S(23) - 0.2 <= T <= E(26) + 0.4:
        B["expr"] = "think" if T < S(26) else "happy"
        O["expr"] = I["expr"] = "think" if T < S(26) else "happy"
    if T >= S(27) - 0.2:
        B["expr"] = O["expr"] = I["expr"] = "happy"
        hop = (T - S(27)) / 0.55
        if 0 <= hop <= 1:
            O["jump"] = 42 * math.sin(math.pi * hop)
    if S(28) - 0.3 <= T <= E(29) + 0.4:
        O["expr"] = "surprise" if T < S(28) else "happy"
    if during(33, 0.1, 0.5):
        I["expr"] = "surprise"
    return {"B": B, "O": O, "I": I}


# ---------------------------------------------------------------- cards
def word_chip(ctx, s, x, y, a, col=INK, bg="#FFFFFF", size=46):
    w = 40 + 0.56 * size * len(s)
    rrect(ctx, x - w / 2, y - 36, w, 72, 36, bg, 0.97 * a)
    text(ctx, s, x, y + 1, size, col, a)



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
        for k, s_ in enumerate(("Ladybird dots", "at a glance")):
            text(ctx, s_, W / 2, 330 + k * 92, 68, INK, a)
    # at a glance: one quick look, like the dots on a dice
    a = window(T, S(4) - 0.2, E(5) + 0.9)
    if a > 0:
        card(ctx, 70, 140, 940, 420, a)
        text(ctx, "At a glance =", W / 2, 206, 50, "#9C7429", a)
        text(ctx, "one quick look", W / 2, 268, 50, "#9C7429", a)
        b = a * prog(T, S(5) - 0.2, S(5) + 0.3)
        dice(ctx, W / 2, 420, 170, 4, b)
    # A or B
    aA = window(T, S(14) - 0.2, E(21) + 0.6)
    if aA > 0:
        aA2 = aA * prog(T, S(14) - 0.2, S(14) + 0.2)
        aB = aA * prog(T, S(15) - 0.2, S(15) + 0.2)
        d = E(21) - S(21)
        picked = prog(T, S(21) + 0.2 * d, S(21) + 0.2 * d + 0.4)
        ak = aA2 * (1 - 0.5 * picked)
        card(ctx, 70, 150, 450, 300, aA2)
        ellipse(ctx, 134, 210, 38, 38, OCHRE, ak)
        text(ctx, "A", 134, 212, 48, "#FFFFFF", ak)
        text(ctx, "5 dots", 295, 320, 76, INK, ak)
        card(ctx, 560, 150, 450, 300, aB)
        ellipse(ctx, 624, 210, 38, 38, SAGE, aB)
        text(ctx, "B", 624, 212, 48, "#FFFFFF", aB)
        text(ctx, "4 dots", 785, 320, 76, INK, aB)
        if picked > 0:
            tick_box(ctx, 560, 150, 450, 300, picked * aB)
        g0, g1 = E(16) + 0.2, E(16) + 4.9
        ra = aA * window(T, S(16), S(17) + 0.3, 0.3, 0.4)
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
        card(ctx, 30, 130, 1020, 900, ra, "#FBF6EC", 1.0)
        rrect(ctx, 300, 160, 480, 110, 50, OCHRE, ra)
        text(ctx, "Remember", W / 2, 215, 62, "#FFFFFF", ra)
        r1 = ra * prog(T, S(30) + 0.3, S(30) + 0.9)
        rrect(ctx, 100, 300, 880, 320, 36, "#FFFFFF", 0.95 * r1)
        ctx.push_group()
        painted_ladybird(ctx, W / 2, 420, 0.42)
        text(ctx, "You can see small groups", W / 2, 516, 54, INK)
        text(ctx, "without counting.", W / 2, 582, 54, INK)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(r1)
        r2 = ra * prog(T, S(32), S(32) + 0.6)
        rrect(ctx, 100, 650, 880, 350, 36, "#FFFFFF", 0.95 * r2)
        text(ctx, "Try it at home:", W / 2, 712, 50, "#9C7429", r2)
        text(ctx, "Roll a dice.", W / 2, 790, 56, INK, r2)
        dice(ctx, 300, 905, 130, 3, r2)
        text(ctx, "Say the number fast!", 650, 905, 46, INK, r2)
    # teaser
    ta = window(T, S(33) - 0.1, ep.total - 1.0, 0.4, 0.5)
    if ta > 0:
        card(ctx, 140, 170, 800, 460, ta)
        rrect(ctx, 330, 200, 420, 100, 46, SAGE, ta)
        text(ctx, "Next case", W / 2, 250, 54, "#FFFFFF", ta)
        for k, (s_, rot) in enumerate((("3", -0.12), ("1", 0.06), ("2", -0.04))):
            clue_card(ctx, W / 2 - 170 + k * 170, 420, s_, ta, rot)
        text(ctx, "The shuffled clue cards", W / 2, 580, 44, INK, ta)
