"""Episode 005: The screeching witness (Years 3 to 4, English, Vocabulary).

Setting: the cake stall at a school fete on a sunny afternoon. Otto's lamington has gone
from the plate. Pip the mouse saw it happen and wrote "It was big. It was loud." Two big,
loud birds sit on the fence behind the stall: a kookaburra and a cockatoo. Otto blames the
kookaburra. A synonym means nearly the same (hungry and starving, at a sausage sizzle);
Pip swaps the dull word "loud" for the more exact "screeching". Kookaburras laugh;
cockatoos screech, so it was the cockatoo. Second proof: coconut crumbs on its beak.
Funny moment: the kookaburra laughs, glad it was not blamed.

True sizes (K = 16 px per cm): squirrel sitting 20 cm, hedgehog 12 cm tall and 20 cm long,
mouse about 8 cm, lamington 5 to 6 cm. Sulphur-crested cockatoo about 45 to 50 cm and
laughing kookaburra about 40 to 45 cm long; they perch on the fence about 2 m further back,
so they are drawn about 0.45 x (still taller than the squirrels, which is why "big" fits both).
Sulphur-crested cockatoos are known for raiding food at picnics and fetes.
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
RAIL_Y = 1080                  # top rail of the fence the birds sit on
KOOK_X, COCKY_X = 300, 790
BIRD_S = 0.45 * K              # birds about 2 m further back
TABLE_L, TABLE_R, TABLE_TOP = 330, 770, 1200
PLATE_X, PLATE_Y = 470, 1196
GAP_X = 512                    # the empty spot where Otto's lamington was
PIP_X = 720
LAM = 5.5 * K * NEAR           # lamington side (5.5 cm)

CASE_NO = 5
RULE = "Swap a dull word for a more exact synonym."
SETTING = "the school fete cake stall"
SENTENCE_LIMIT = 10

LINES = [
    Line("B", "Case open!", gap=0.4),                                        # 0
    Line("O", "Hey! That's not fair! My lamington is gone!", gap=0.6),       # 1
    Line("I", "Pip saw who took it.", gap=0.8),                              # 2
    Line("N", "Today's case: a witness who needs better words.", gap=0.7),   # 3
    Line("N", "Pip wrote it down. It was big. It was loud.", gap=0.8),      # 4
    Line("N", "Big and loud are dull words. They fit lots of things.", gap=0.8),  # 5
    Line("N", "A synonym means nearly the same thing.", gap=0.8),            # 6
    Line("N", "It's like a sausage sizzle.", gap=0.6),                       # 7
    Line("N", "Hungry and starving are synonyms. Starving is more exact.", gap=1.0),  # 8
    Line("O", "Big and loud? It was the kookaburra!", gap=0.8),              # 9
    Line("I", "Hmm. The cockatoo is big and loud too.", gap=0.8),            # 10
    Line("B", "Let's not guess. Let's test.", gap=0.8),                      # 11
    Line("B", "Can you point to the two big birds?", gap=4.0),               # 12
    Line("B", "Pip swapped loud for screeching. Which bird screeches?", gap=0.8),  # 13
    Line("N", "A. The kookaburra.", gap=0.6),                                # 14
    Line("N", "B. The cockatoo.", gap=0.6),                                  # 15
    Line("N", "Pause and think.", gap=5.0),                                  # 16
    Line("N", "Swap a dull word for a more exact synonym.", gap=0.8),        # 17
    Line("N", "Kookaburras don't screech. They laugh.", gap=0.8),            # 18
    Line("N", "Cockatoos screech. Loud and sharp.", gap=0.8),                # 19
    Line("N", "It's B! The cockatoo.", gap=0.6),                             # 20
    Line("O", "Oh! I picked too fast!", gap=0.8),                            # 21
    Line("B", "Let's check another way. Look closely.", gap=0.8),            # 22
    Line("N", "Coconut crumbs on the cockatoo's beak!", gap=0.8),            # 23
    Line("I", "Both clues point to the cockatoo!", gap=0.8),                 # 24
    Line("B", "Case solved!", gap=1.9),                                      # 25
    Line("I", "Listen! The kookaburra is laughing!", gap=0.6),               # 26
    Line("O", "It's glad we didn't blame it!", gap=1.0),                     # 27
    Line("N", "Remember. Swap a dull word for a more exact synonym.", gap=0.9),  # 28
    Line("N", "Say it with me. Swap a dull word for a more exact synonym.", gap=2.2),  # 29
    Line("N", "Try it at home. Find a better word for nice.", gap=0.9),     # 30
    Line("N", "Next case: clapping the syllables in our names.", gap=0.6),   # 31
]

STRIP_HIDDEN = {3, 25, 28}
CHILD_TURN = 29
STAMP_LINE = 25
OPEN_LINE = 0
CUT = [(0, 2), (9, 10), (13, 13), (17, 21), (25, 27), (29, 29), (31, 31)]


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


def plate(ctx, ep, T):
    rig.soft_shadow(ctx, PLATE_X, PLATE_Y + 6, 175, 16, 0.22)
    ellipse(ctx, PLATE_X, PLATE_Y, 168, 30, "#E6E2DA")
    ellipse(ctx, PLATE_X, PLATE_Y - 4, 150, 24, "#FBFAF7")
    for k, lx in enumerate((PLATE_X - 104, PLATE_X)):
        lamington(ctx, lx, PLATE_Y + 6, 1.0, 1.0, k + 2)
    # crumbs where Otto's lamington was
    for i in range(7):
        ellipse(ctx, GAP_X - 30 + (i * 23) % 64, PLATE_Y - 6 + (i * 7) % 12, 4, 3, "#6B4430" if i % 2 else "#F6EFE2")


def table(ctx):
    rig.soft_shadow(ctx, (TABLE_L + TABLE_R) / 2, 1352, (TABLE_R - TABLE_L) * 0.55, 14, 0.22)
    rrect(ctx, TABLE_L - 20, TABLE_TOP - 14, TABLE_R - TABLE_L + 40, 28, 8, "#F4EEE3")
    # gingham cloth
    rrect(ctx, TABLE_L - 20, TABLE_TOP, TABLE_R - TABLE_L + 40, 140, 6, "#F4EEE3")
    src(ctx, "#C9605A", 0.35)
    for xx in range(TABLE_L - 20, TABLE_R + 20, 40):
        ctx.rectangle(xx, TABLE_TOP, 20, 140)
    ctx.fill()
    for yy in range(TABLE_TOP, TABLE_TOP + 140, 40):
        src(ctx, "#C9605A", 0.35)
        ctx.rectangle(TABLE_L - 20, yy, TABLE_R - TABLE_L + 40, 20)
        ctx.fill()
    rrect(ctx, 430, 1236, 220, 70, 14, "#FFF8E6")
    text(ctx, "Cake stall", 540, 1272, 36, "#9C7429")


def bird_feet(ctx, x, y, u, a):
    for dx in (-2.2, 1.6):
        rrect(ctx, x + dx * u - 1.2 * u, y - 1.0 * u, 2.4 * u, 1.6 * u, 0.8 * u, "#6E6A66", a)


def kookaburra(ctx, x, y, u, f=1, laugh=0.0, a=1.0):
    """Laughing kookaburra perched on a rail; (x, y) is where its feet grip."""
    if a <= 0:
        return
    sw = 0.6 * math.sin(NOW[0] * 1.3)
    # barred rufous tail hangs behind the rail
    rrect(ctx, x - f * 4.5 * u - 2.2 * u, y - 4 * u, 4.4 * u, 17 * u, 2 * u, "#A7643A", a)
    src(ctx, "#5B3A24", 0.6 * a)
    for j in range(4):
        ctx.rectangle(x - f * 4.5 * u - 2.2 * u, y + (j * 3.6 + 1) * u, 4.4 * u, 1.0 * u)
    ctx.fill()
    rig.ball(ctx, x, y - 12 * u, 8.5 * u, 12.5 * u, "#F1E7D2", a, f=f)          # cream belly
    rig.ball(ctx, x - f * 3.2 * u, y - 13 * u, 6.5 * u, 11 * u, "#7A5638", a, f=f)  # brown wing
    ellipse(ctx, x - f * 2.6 * u, y - 12 * u, 3.6 * u, 4 * u, "#8FB4C8", 0.7 * a)  # blue wing patch
    hx, hy = x + f * 2.0 * u, y - 27 * u + sw
    rig.ball(ctx, hx, hy, 7.2 * u, 6.6 * u, "#F1E7D2", a, f=f)
    # crown and the dark eye stripe
    ellipse(ctx, hx - f * 1.0 * u, hy - 4.2 * u, 5.4 * u, 2.6 * u, "#8A6A50", 0.85 * a)
    src(ctx, "#4A3424", a)
    ctx.move_to(hx - f * 6.5 * u, hy - 0.4 * u)
    ctx.line_to(hx + f * 3.6 * u, hy - 1.4 * u)
    ctx.line_to(hx + f * 3.6 * u, hy + 0.6 * u)
    ctx.line_to(hx - f * 6.5 * u, hy + 1.6 * u)
    ctx.close_path()
    ctx.fill()
    ellipse(ctx, hx + f * 2.4 * u, hy - 0.4 * u, 1.3 * u, 1.3 * u, "#1E1A16", a)
    ellipse(ctx, hx + f * 2.0 * u, hy - 0.8 * u, 0.4 * u, 0.4 * u, "#FFFFFF", a)
    # big beak (dark top, pale lower); opens when laughing
    op = 2.4 * u * laugh * (0.6 + 0.4 * abs(math.sin(NOW[0] * 14)))
    bx = hx + f * 5.8 * u
    src(ctx, "#3A332E", a)
    ctx.move_to(bx, hy - 1.6 * u)
    ctx.line_to(bx + f * 9 * u, hy + 0.6 * u - op * 0.3)
    ctx.line_to(bx, hy + 1.0 * u)
    ctx.close_path()
    ctx.fill()
    src(ctx, "#D9CBB4", a)
    ctx.move_to(bx, hy + 1.0 * u)
    ctx.line_to(bx + f * 8 * u, hy + 1.2 * u + op)
    ctx.line_to(bx, hy + 3.0 * u)
    ctx.close_path()
    ctx.fill()
    bird_feet(ctx, x, y, u, a)


def cockatoo(ctx, x, y, u, f=-1, screech=0.0, crumbs=0.0, a=1.0):
    """Sulphur-crested cockatoo perched on a rail; (x, y) is where its feet grip."""
    if a <= 0:
        return
    sw = 0.6 * math.sin(NOW[0] * 1.1 + 1.0)
    rrect(ctx, x - f * 4 * u - 2.4 * u, y - 4 * u, 4.8 * u, 16 * u, 2.2 * u, "#EDEDE6", a)
    ellipse(ctx, x - f * 4 * u, y + 9 * u, 2 * u, 3 * u, "#EBD97A", 0.6 * a)
    rig.ball(ctx, x, y - 13 * u, 8.5 * u, 13 * u, "#FAFAF6", a, f=f)
    rig.ball(ctx, x - f * 3 * u, y - 13 * u, 6.2 * u, 11 * u, "#EFEFE9", a, f=f)
    hx, hy = x + f * 2.0 * u, y - 28 * u + sw
    # yellow crest: lies back, fans up when it screeches
    up = 0.25 + 0.75 * screech
    for j in range(5):
        ang = math.pi * (0.5 + f * (0.15 + 0.12 * j) * (1.6 - up))
        ln = (7 + j * 1.2) * u * (0.7 + 0.3 * up)
        bx0, by0 = hx - f * 1.5 * u, hy - 4.5 * u
        ctx.move_to(bx0, by0)
        ctx.line_to(bx0 - math.cos(ang) * ln - 1.0 * u, by0 - math.sin(ang) * ln)
        ctx.line_to(bx0 - math.cos(ang) * ln + 1.0 * u, by0 - math.sin(ang) * ln)
        ctx.close_path()
        src(ctx, "#F2D24E", a)
        ctx.fill()
    rig.ball(ctx, hx, hy, 6.8 * u, 6.4 * u, "#FCFCF8", a, f=f)
    ellipse(ctx, hx + f * 2.0 * u, hy - 0.6 * u, 1.8 * u, 1.8 * u, "#DCE9EF", a)   # pale eye ring
    ellipse(ctx, hx + f * 2.0 * u, hy - 0.6 * u, 1.1 * u, 1.1 * u, "#1E1A16", a)
    ellipse(ctx, hx + f * 1.7 * u, hy - 1.0 * u, 0.35 * u, 0.35 * u, "#FFFFFF", a)
    # curved grey-black beak; opens when it screeches
    op = 2.0 * u * screech * (0.6 + 0.4 * abs(math.sin(NOW[0] * 18)))
    bx, by = hx + f * 5.2 * u, hy + 0.6 * u
    src(ctx, "#3A3633", a)
    ctx.move_to(bx, by - 2.6 * u)
    ctx.curve_to(bx + f * 4.2 * u, by - 3.0 * u, bx + f * 4.6 * u, by + 1.0 * u, bx + f * 2.6 * u, by + 2.8 * u - op * 0.2)
    ctx.line_to(bx, by + 0.6 * u)
    ctx.close_path()
    ctx.fill()
    src(ctx, "#4A4541", a)
    ctx.move_to(bx, by + 1.0 * u)
    ctx.line_to(bx + f * 2.2 * u, by + 2.4 * u + op)
    ctx.line_to(bx, by + 3.0 * u + op * 0.5)
    ctx.close_path()
    ctx.fill()
    if crumbs > 0:   # coconut and chocolate crumbs on the beak
        for i, (dx, dy) in enumerate(((1.0, -1.6), (2.4, -0.6), (1.6, 0.8), (3.2, -1.9), (0.6, 1.8))):
            ellipse(ctx, bx + f * dx * u, by + dy * u, 0.55 * u, 0.45 * u,
                    "#F6EFE2" if i % 2 == 0 else "#86573D", crumbs * a)
    bird_feet(ctx, x, y, u, a)


def beak_pt(kind):
    u = BIRD_S
    if kind == "cocky":
        return COCKY_X - 2.0 * u - 6.8 * u, RAIL_Y - 28 * u + 0.6 * u
    return KOOK_X + 2.0 * u + 9 * u, RAIL_Y - 27 * u


def sound_marks(ctx, kind, a):
    """Little sound lines by a beak: soft waves for a laugh, sharp zigzags for a screech."""
    if a <= 0:
        return
    bx, by = beak_pt(kind)
    f = -1 if kind == "cocky" else 1
    ctx.set_line_width(6)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ph = (NOW[0] * 3) % 1.0
    for j in range(3):
        aj = a * (0.5 + 0.5 * math.sin(math.pi * ((ph + j / 3) % 1.0)))
        if kind == "cocky":
            src(ctx, "#B4473E", aj)
            x0 = bx + f * (26 + j * 26)
            ctx.move_to(x0, by - 34 + j * 4)
            for k in range(4):
                ctx.line_to(x0 + f * (8 if k % 2 == 0 else -2), by - 34 + j * 4 + (k + 1) * 17)
            ctx.stroke()
        else:
            src(ctx, "#9C7429", aj)
            r = 26 + j * 22
            ctx.arc(bx, by, r, -0.6, 0.6)
            ctx.stroke()


def sausage_sizzle(ctx, x, y, a):
    """A sausage in a slice of bread with a line of sauce."""
    rrect(ctx, x - 110, y - 34, 220, 68, 30, "#E9C88E", a)
    rrect(ctx, x - 104, y - 28, 208, 56, 26, "#F6E3B8", a)
    rrect(ctx, x - 120, y - 18, 240, 36, 18, "#9A5434", a)
    src(ctx, "#B4473E", a)
    ctx.set_line_width(6)
    ctx.move_to(x - 96, y - 2)
    for i in range(1, 13):
        ctx.line_to(x - 96 + i * 16, y - 2 + (6 if i % 2 else -6))
    ctx.stroke()


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


# ---------------------------------------------------------------- background
def fete(ctx):
    g = cairo.LinearGradient(0, 0, 0, 720)
    g.add_color_stop_rgb(0, *R.rgb("#C6DEEA"))
    g.add_color_stop_rgb(1, *R.rgb("#EEF2E6"))
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, 760)
    ctx.fill()
    drift = NOW[0] * 5
    for cx0, cy0, cw in ((240, 140, 120), (800, 220, 140)):
        cx = (cx0 + drift) % 1500 - 200
        ellipse(ctx, cx, cy0, cw, cw * 0.34, "#FFFFFF", 0.75)
        ellipse(ctx, cx + cw * 0.4, cy0 - cw * 0.18, cw * 0.55, cw * 0.3, "#FFFFFF", 0.75)
    # school building far back
    rrect(ctx, 150, 560, 780, 210, 6, "#C98F74")
    ctx.move_to(130, 566)
    ctx.line_to(540, 470)
    ctx.line_to(950, 566)
    ctx.close_path()
    src(ctx, "#8E6F5E")
    ctx.fill()
    for k in range(6):
        rrect(ctx, 195 + k * 120, 610, 70, 60, 4, "#DDEBF0")
    rrect(ctx, 505, 690, 70, 80, 4, "#7B5B45")
    # gum trees
    for px, ph, cr in ((70, 420, 120), (1010, 380, 110)):
        rrect(ctx, px - 12, 780 - ph, 24, ph, 8, "#D8CFC2")
        for dx, dy, rr in ((-60, -ph, cr), (40, -ph + 20, cr * 0.9), (-10, -ph - 60, cr * 0.8)):
            ellipse(ctx, px + dx, 780 + dy, rr, rr * 0.7, "#8BA27A", 0.95)
    # bunting along the roofline
    ctx.set_line_width(3)
    src(ctx, "#8E7F70")
    ctx.move_to(150, 560)
    ctx.curve_to(400, 610, 680, 610, 930, 560)
    ctx.stroke()
    cols = ("#E6A15B", "#8FB4C8", "#C9605A", "#E6D79A", "#9FBF8F")
    for i in range(11):
        t = i / 10.0
        bx = 150 + t * 780
        by = 560 + 4 * 46 * t * (1 - t) * 0.82
        ctx.move_to(bx - 22, by)
        ctx.line_to(bx + 22, by)
        ctx.line_to(bx, by + 40)
        ctx.close_path()
        src(ctx, cols[i % 5])
        ctx.fill()
    # oval grass
    g = cairo.LinearGradient(0, 760, 0, 1920)
    g.add_color_stop_rgb(0, *R.rgb("#B9CC9E"))
    g.add_color_stop_rgb(1, *R.rgb("#A3BB86"))
    ctx.set_source(g)
    ctx.rectangle(0, 770, W, 1920 - 770)
    ctx.fill()
    # timber fence behind the stall
    for px in (40, 300, 540, 790, 1040):
        rrect(ctx, px - 14, RAIL_Y - 30, 28, 1250 - RAIL_Y + 30, 4, "#9C8F80")
    for ry in (RAIL_Y, RAIL_Y + 80):
        rrect(ctx, 0, ry, W, 22, 4, "#B0A393")
        src(ctx, "#000000", 0.08)
        ctx.rectangle(0, ry + 14, W, 8)
        ctx.fill()
    ctx.set_line_width(2)
    for i in range(16):
        xb = 40 + (i * 167) % 1000
        yb = 1380 + (i * 97) % 300
        src(ctx, "#8FA673", 0.5)
        ctx.move_to(xb, yb)
        ctx.line_to(xb - 5, yb - 14)
        ctx.move_to(xb + 6, yb)
        ctx.line_to(xb + 9, yb - 12)
        ctx.stroke()


# ---------------------------------------------------------------- scene
def scene(ctx, ep, T):
    S, E = ep.s, ep.e
    fete(ctx)
    laugh = max(R.clamp(prog(T, S(18), S(18) + 0.3) * (1 - prog(T, E(18), E(18) + 0.4))),
                R.clamp(prog(T, S(26) - 0.2, S(26) + 0.2) * (1 - prog(T, E(27) + 0.3, E(27) + 0.8))))
    screech = R.clamp(prog(T, S(19), S(19) + 0.3) * (1 - prog(T, E(19), E(19) + 0.4)))
    crumbs = 0.55 + 0.45 * prog(T, S(23), S(23) + 0.4)
    kookaburra(ctx, KOOK_X, RAIL_Y, BIRD_S, 1, laugh)
    cockatoo(ctx, COCKY_X, RAIL_Y, BIRD_S, -1, screech, crumbs)
    sound_marks(ctx, "kook", laugh)
    sound_marks(ctx, "cocky", screech)
    table(ctx)
    plate(ctx, ep, T)
    R.mouse(ctx, PIP_X, TABLE_TOP + 2, 1.3, -1)
    rig.squirrel(ctx, OTTO_X, FEET, SQ_S, OCHRE, f=1, seed=2.0)
    rig.bramble(ctx, BR_X, FEET, BR_S, f=1)
    rig.squirrel(ctx, IVY_X, FEET, SQ_S, SAGE, f=-1, seed=0.7)


# ---------------------------------------------------------------- cues, poses, foley
def cues(ep):
    bx, by = beak_pt("cocky")
    return [
        ("ring", ep.s(1) - 0.1, ep.e(1) + 0.5, GAP_X, PLATE_Y - 30, 80, 60),
        ("zoom", ep.s(9) - 0.2, ep.e(10) + 0.5, 545, 1150, 1.1),
        ("ring", ep.s(12) - 0.1, ep.e(12) + 3.8, 545, RAIL_Y - 100, 380, 200),
        ("zoom", ep.s(17) - 0.3, ep.e(19) + 0.4, 545, 1000, 1.1),
        ("ring", ep.s(20) - 0.1, ep.e(20) + 0.5, COCKY_X, RAIL_Y - 110, 150, 175),
        ("lens", ep.s(23) - 0.1, ep.e(23) + 0.8, bx - 12, by, 560, 640, 140, 2.2),
    ]


def foley(ep):
    out = [("whoosh", ep.s(3) - 0.3), ("whoosh", ep.s(4) - 0.3), ("whoosh", ep.s(7) - 0.3),
           ("whoosh", ep.s(13) - 0.3), ("whoosh", ep.s(14) - 0.3)]
    out.append(("pop", ep.s(13) + 0.45 * (ep.e(13) - ep.s(13))))
    out.append(("step", ep.s(25) + 0.5))
    return out


def poses(ep, T):
    S, E = ep.s, ep.e

    def during(i, pre=0.2, post=0.6):
        return S(i) - pre <= T <= E(i) + post

    def ramp(t0):
        return prog(T, t0, t0 + 0.5)

    gap_pt = (GAP_X, PLATE_Y - 20)
    kook_pt = (KOOK_X + 40, RAIL_Y - 150)
    cocky_pt = (COCKY_X - 30, RAIL_Y - 150)
    B = {"face": 1}
    O = {"face": 1}
    I = {"face": -1}
    if T < S(3):
        O["expr"] = "sad"
    if during(1, 0.1, 0.3):
        O.update(point=gap_pt, amt=ramp(S(1)))
    if during(2, 0.1, 0.4):
        I.update(expr="think", point=(PIP_X, TABLE_TOP - 60), amt=ramp(S(2)))
    if during(9, 0.3, 0.4):
        O.update(expr="happy", point=kook_pt, amt=ramp(S(9) - 0.3))
    if during(10, 0.2, 0.8):
        I.update(expr="think", point=cocky_pt, amt=ramp(S(10) - 0.2))
        O["expr"] = "think"
    if S(11) - 0.2 <= T <= E(12) + 3.8:
        B["expr"] = "think" if T < S(12) else "happy"
    if S(13) <= T <= S(17):
        O["expr"] = I["expr"] = "think"
    if S(17) - 0.2 <= T <= E(17) + 0.6:
        B["expr"] = "think"
    if during(19, 0.1, 0.4):
        B.update(expr="happy", point=cocky_pt, amt=ramp(S(19) - 0.1))
    if during(20, 0.2, 0.3):
        I["expr"] = "happy"
    if during(21, 0.2, 0.8):
        O["expr"] = "surprise"
        O["scratch"] = prog(T, S(21) + 0.3, S(21) + 0.8) * (1 - prog(T, E(21) + 0.4, E(21) + 0.8))
    if S(22) - 0.2 <= T <= E(23) + 0.4:
        bx, by = beak_pt("cocky")
        B.update(expr="think", point=(bx, by + 20), amt=ramp(S(22) - 0.2))
    if during(24, 0.2, 0.6):
        I["expr"] = "happy"
    if T >= S(25) - 0.2:
        B["expr"] = O["expr"] = I["expr"] = "happy"
        hop = (T - S(25)) / 0.55
        if 0 <= hop <= 1:
            O["jump"] = 42 * math.sin(math.pi * hop)
    if during(26, 0.1, 0.3):
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


def notebook(ctx, ep, T, a, swap):
    """Pip's witness notes: 'It was big. It was loud.'; swap crosses out loud for screeching."""
    card(ctx, 70, 140, 940, 420, a)
    text(ctx, "Pip's notes", W / 2, 200, 46, "#9C7429", a)
    rrect(ctx, 170, 250, 740, 270, 12, "#FFF8E6", a)
    ctx.set_line_width(2)
    src(ctx, "#9CB7D0", a)
    for yy in (340, 450):
        ctx.move_to(200, yy + 30)
        ctx.line_to(880, yy + 30)
    ctx.stroke()
    text(ctx, "It was big.", W / 2, 330, 60, INK, a)
    if swap <= 0:
        text(ctx, "It was loud.", W / 2, 440, 60, INK, a)
        return
    text(ctx, "It was", 360, 440, 60, INK, a)
    text(ctx, "loud.", 560, 440, 60, INK, a * (1 - 0.5 * swap))
    ctx.set_line_width(7)
    src(ctx, "#B4473E", a * swap)
    ctx.move_to(490, 440)
    ctx.line_to(490 + 140 * swap, 440)
    ctx.stroke()
    text(ctx, "screeching!", 760, 500, 50, OCHRE, a * prog(swap, 0.5, 1.0))


def cards(ctx, ep, T):
    S, E = ep.s, ep.e
    # Today's case title (read word for word)
    a = window(T, S(3) - 0.3, E(3) + 0.9)
    if a > 0:
        card(ctx, 70, 140, 940, 420, a)
        rrect(ctx, 120, 184, 60, 46, 8, OCHRE, a)
        rrect(ctx, 120, 176, 28, 14, 5, OCHRE, a)
        text(ctx, "Today's case", 560, 210, 46, "#9C7429", a)
        for k, s_ in enumerate(("A witness who", "needs better words")):
            text(ctx, s_, W / 2, 330 + k * 92, 72, INK, a)
    # Pip's notes
    a = window(T, S(4) - 0.2, E(5) + 0.9)
    if a > 0:
        notebook(ctx, ep, T, a, 0.0)
    # synonyms: a sausage sizzle, hungry and starving
    a = window(T, S(7) - 0.2, E(8) + 1.0)
    if a > 0:
        card(ctx, 70, 140, 940, 420, a)
        text(ctx, "Synonyms", W / 2, 196, 46, "#9C7429", a)
        ctx.save()
        ctx.translate(W / 2, 315)
        ctx.scale(1.6, 1.6)
        sausage_sizzle(ctx, 0, 0, a)
        ctx.restore()
        b = prog(T, S(8) - 0.1, S(8) + 0.3)
        c = prog(T, S(8) + 0.35 * (E(8) - S(8)), S(8) + 0.35 * (E(8) - S(8)) + 0.3)
        word_chip(ctx, "hungry", 330, 450, a * b, INK, "#F1ECE2")
        arrow(ctx, 470, 580, 450, a * c)
        word_chip(ctx, "starving", 750, 450, a * c, OCHRE, "#FBF1DC")
    # Pip swaps loud for screeching
    a = window(T, S(13) - 0.2, S(14) - 0.15)
    if a > 0:
        sw = prog(T, S(13) + 0.25 * (E(13) - S(13)), S(13) + 0.6 * (E(13) - S(13)))
        notebook(ctx, ep, T, a, sw)
    # A or B
    aA = window(T, S(14) - 0.2, E(20) + 1.4)
    if aA > 0:
        aA2 = aA * prog(T, S(14) - 0.2, S(14) + 0.2)
        aB = aA * prog(T, S(15) - 0.2, S(15) + 0.2)
        d = E(20) - S(20)
        picked = prog(T, S(20) + 0.2 * d, S(20) + 0.2 * d + 0.4)
        ak = aA2 * (1 - 0.5 * picked)
        card(ctx, 70, 150, 450, 300, aA2)
        ellipse(ctx, 134, 210, 38, 38, OCHRE, ak)
        text(ctx, "A", 134, 212, 48, "#FFFFFF", ak)
        ctx.save()
        ctx.rectangle(70, 150, 450, 300)
        ctx.clip()
        rrect(ctx, 70, 400, 450, 18, 4, "#B0A393", ak)
        kookaburra(ctx, 270, 402, 0.36 * K, 1, 0.0, ak)
        ctx.restore()
        card(ctx, 560, 150, 450, 300, aB)
        ellipse(ctx, 624, 210, 38, 38, SAGE, aB)
        text(ctx, "B", 624, 212, 48, "#FFFFFF", aB)
        ctx.save()
        ctx.rectangle(560, 150, 450, 300)
        ctx.clip()
        rrect(ctx, 560, 400, 450, 18, 4, "#B0A393", aB)
        cockatoo(ctx, 815, 402, 0.36 * K, -1, 0.0, 0.0, aB)
        ctx.restore()
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
    ra = window(T, S(28) - 0.3, S(31) - 0.1, 0.5, 0.5)
    if ra > 0:
        card(ctx, 30, 130, 1020, 1010, ra, "#FBF6EC", 1.0)
        rrect(ctx, 300, 160, 480, 110, 50, OCHRE, ra)
        text(ctx, "Remember", W / 2, 215, 62, "#FFFFFF", ra)
        r1 = ra * prog(T, S(28) + 0.3, S(28) + 0.9)
        rrect(ctx, 100, 310, 880, 350, 36, "#FFFFFF", 0.95 * r1)
        ctx.push_group()
        word_chip(ctx, "loud", 330, 410, 1.0, INK, "#F1ECE2")
        arrow(ctx, 450, 560, 410, 1.0)
        word_chip(ctx, "screeching", 760, 410, 1.0, OCHRE, "#FBF1DC")
        text(ctx, "Swap a dull word for", W / 2, 540, 54, INK)
        text(ctx, "a more exact synonym.", W / 2, 608, 54, INK)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(r1)
        r2 = ra * prog(T, S(30), S(30) + 0.6)
        rrect(ctx, 100, 700, 880, 400, 36, "#FFFFFF", 0.95 * r2)
        text(ctx, "Try it at home:", W / 2, 770, 50, "#9C7429", r2)
        text(ctx, "find a better word", W / 2, 850, 56, INK, r2)
        text(ctx, "for nice", W / 2, 920, 56, INK, r2)
        word_chip(ctx, "nice", 250, 1020, r2, INK, "#F1ECE2", 42)
        arrow(ctx, 340, 420, 1020, r2)
        word_chip(ctx, "kind", 540, 1020, r2, OCHRE, "#FBF1DC", 42)
        word_chip(ctx, "delicious", 780, 1020, r2, OCHRE, "#FBF1DC", 42)
    # teaser
    ta = window(T, S(31) - 0.1, ep.total - 1.0, 0.4, 0.5)
    if ta > 0:
        card(ctx, 140, 170, 800, 460, ta)
        rrect(ctx, 330, 200, 420, 100, 46, SAGE, ta)
        text(ctx, "Next case", W / 2, 250, 54, "#FFFFFF", ta)
        # names split into claps
        for row, parts in enumerate((("Ot", "to"), ("I", "vy"))):
            y = 370 + row * 80
            for j, p in enumerate(parts):
                word_chip(ctx, p, 450 + j * 180, y, ta, INK, "#FBF1DC", 44)
            ellipse(ctx, 540, y, 8, 8, OCHRE, ta)
        text(ctx, "Clapping the syllables", W / 2, 540, 44, INK, ta)
        text(ctx, "in our names", W / 2, 592, 44, INK, ta)
