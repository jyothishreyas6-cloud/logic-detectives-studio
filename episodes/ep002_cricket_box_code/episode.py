"""Episode 002: The cricket box code (Years 3-4, Maths, Representing numbers using place value).

Setting: a park picnic table next to the cricket oval. The club's cricket box has a four-dial
lock. Mabel left a clue in base-ten (number) blocks: 3 thousands, no hundreds, 5 tens, 2 ones.
Otto reads "three, five, two" and forgets the empty hundreds place. A place value mat shows the
zero holds the hundreds place: 3052. Funny moment: a real cricket hops out of the cricket box.

True sizes (K = 15 px per cm): squirrel sitting 20 cm, hedgehog 12 cm tall and 20 cm long,
base-ten blocks (thousand cube 10 cm, ten stick 10 x 1 x 1 cm, one cube 1 cm),
lock box 25 x 9 cm front with 18 cm deep lid, dials 1.8 x 2.7 cm, cricket ball 7.2 cm,
field cricket about 2.5 cm, $1 coin 25 mm, $10 note 137 x 65 mm, cloth pouch 10 x 12 cm.
"""
import math

import cairo

import render as R
import rig14 as rig
from render import W, INK, OCHRE, SAGE, ellipse, rrect, text, src, prog, lerp, ease, sparkles, NOW
from kit import Line

K = 15.0                       # px per cm
SQ_S = K / 10.4                # squirrel scale (20 cm sitting)
BR_S = 0.95 * K / 10.4         # hedgehog scale (12 cm tall, 20 cm long)
FEET = 1690
OTTO_X, BR_X, IVY_X = 200, 470, 880
GREEN = "#6E8460"

LINES = [
    Line("B", "Case open!", gap=0.4),                                                    # 0
    Line("O", "Hey! That's not fair! The cricket box is locked!", gap=0.6),              # 1
    Line("I", "The lock needs a code with four digits.", gap=1.0),                       # 2
    Line("N", "Today's case: a code hidden in thousands, hundreds, tens and ones.", gap=1.0),  # 3
    Line("N", "Digits are the numbers zero to nine.", gap=0.8),                          # 4
    Line("N", "Place value means a digit's place shows its size.", gap=1.5),             # 5
    Line("N", "Like at the canteen. Ten one-dollar coins make one ten-dollar note.", gap=1.5),  # 6
    Line("N", "Mabel left a clue made of number blocks.", gap=0.8),                      # 7
    Line("N", "Big cubes are thousands. Flats are hundreds.", gap=0.8),                  # 8
    Line("N", "Long sticks are tens. Little cubes are ones.", gap=1.5),                  # 9
    Line("O", "Three cubes, five sticks, two little cubes. It's three, five, two!", gap=0.8),  # 10
    Line("I", "But the lock has four dials.", gap=1.0),                                  # 11
    Line("B", "Let's not guess. Let's test.", gap=0.8),                                  # 12
    Line("B", "Can you find the hundreds? Point to them.", gap=4.0),                     # 13
    Line("N", "There are no flats. So there are no hundreds.", gap=1.5),                 # 14
    Line("B", "Which code opens the lock?", gap=0.8),                                    # 15
    Line("N", "A. Three, five, two, zero.", gap=0.6),                                    # 16
    Line("N", "B. Three, zero, five, two.", gap=0.6),                                    # 17
    Line("N", "Pause and think.", gap=5.0),                                              # 18
    Line("N", "Put each block in its place. Three thousands.", gap=0.8),                 # 19
    Line("N", "No hundreds, so we write zero.", gap=0.8),                                # 20
    Line("N", "Five tens. Two ones.", gap=1.0),                                          # 21
    Line("N", "Zero holds the hundreds place. It's B!", gap=0.8),                        # 22
    Line("O", "Oh! The zero was hiding!", gap=1.0),                                      # 23
    Line("N", "Let's count the blocks to check.", gap=0.6),                    # 24
    Line("N", "Three thousand. Three thousand and fifty. Three thousand and fifty-two.", gap=1.5),  # 25
    Line("O", "Three, zero, five, two.", gap=0.8),                                       # 26
    Line("B", "Case solved!", gap=2.0),                                                  # 27
    Line("I", "Look! A real cricket!", gap=0.6),                                         # 28
    Line("O", "Not that kind of cricket!", gap=1.5),                                     # 29
    Line("N", "Remember. Zero holds a place when there are none.", gap=1.0),             # 30
    Line("N", "Say it with me. Zero holds the place.", gap=2.2),                         # 31
    Line("N", "Try it at home. Make a secret code with a zero.", gap=1.2),               # 32
    Line("N", "Next case: counting to ten, one acorn at a time.", gap=0.6),              # 33
]
STRIP_HIDDEN = {3, 27}
CHILD_TURN = 31
STAMP_LINE = 27
OPEN_LINE = 0
CUT = [(0, 2), (7, 11), (13, 13), (15, 22), (26, 29), (31, 31), (33, 33)]

# ---------------------------------------------------------------- geometry
BOX_X0, BOX_X1, BOX_Y, BOX_H = 630, 1005, 980, 135        # 25 cm x 9 cm front
BOX_DX, BOX_DY = 54, -54                                  # lid depth (oblique)
DIAL_W, DIAL_H, DIAL_GAP = 27, 40, 7                      # 1.8 x 2.7 cm dials
DIAL_X0 = (BOX_X0 + BOX_X1) / 2 - (4 * DIAL_W + 3 * DIAL_GAP) / 2
DIAL_Y = 893
DIALS_C = ((BOX_X0 + BOX_X1) / 2, DIAL_Y + DIAL_H / 2)
CODE = (3, 0, 5, 2)

LOOSE_BASE = 1240
LOOSE_CUBES = [(62, LOOSE_BASE), (228, LOOSE_BASE - 8), (395, LOOSE_BASE)]
LOOSE_STICKS = [(640, 1240), (655, 1217), (628, 1194), (662, 1171), (645, 1148)]
LOOSE_ONES = [(852, 1240), (893, 1232)]

MAT_X0, MAT_X1, MAT_Y0, MAT_Y1 = 50, 1030, 780, 1320
COLS = [("Thousands", 50, 440), ("Hundreds", 440, 630), ("Tens", 630, 840), ("Ones", 840, 1030)]
MAT_BASE = 1190
MAT_CUBES = [(70, MAT_BASE), (232, MAT_BASE), (151, MAT_BASE - 150)]
MAT_STICKS = [(660, MAT_BASE - 23 * k) for k in range(5)]
MAT_ONES = [(902, MAT_BASE), (950, MAT_BASE)]
DIGIT_Y = 1258

WOOD_F, WOOD_T, WOOD_S, WOOD_G = "#E7C48A", "#F3DAAB", "#C99E66", "#B0874F"


# ---------------------------------------------------------------- props
def block(ctx, x, y, wcm, hcm, dcm, sc=1.0, a=1.0, glow=0.0):
    """Base-ten block: front face from (x, y-h) to (x+w, y), oblique top and right faces, 1 cm grid."""
    k = K * sc
    w, h = wcm * k, hcm * k
    ox, oy = dcm * k * 0.3, -dcm * k * 0.3
    if glow > 0:
        R.glow(ctx, x + w / 2 + ox / 2, y - h / 2 + oy / 2, max(w, h) * 0.75 + 30, OCHRE, glow)
    # top
    ctx.move_to(x, y - h)
    ctx.line_to(x + ox, y - h + oy)
    ctx.line_to(x + w + ox, y - h + oy)
    ctx.line_to(x + w, y - h)
    ctx.close_path()
    src(ctx, WOOD_T, a)
    ctx.fill()
    # right side
    ctx.move_to(x + w, y - h)
    ctx.line_to(x + w + ox, y - h + oy)
    ctx.line_to(x + w + ox, y + oy)
    ctx.line_to(x + w, y)
    ctx.close_path()
    src(ctx, WOOD_S, a)
    ctx.fill()
    # front
    g = cairo.LinearGradient(x, y - h, x + w, y)
    g.add_color_stop_rgba(0, *R.rgb("#EFD09A"), a)
    g.add_color_stop_rgba(1, *R.rgb(WOOD_F), a)
    ctx.set_source(g)
    ctx.rectangle(x, y - h, w, h)
    ctx.fill()
    # grid (1 cm)
    ctx.set_line_width(max(1.0, 1.4 * sc))
    src(ctx, WOOD_G, 0.55 * a)
    for i in range(1, int(round(wcm))):
        ctx.move_to(x + i * k, y - h)
        ctx.line_to(x + i * k, y)
        ctx.move_to(x + i * k, y - h)
        ctx.line_to(x + i * k + ox, y - h + oy)
    for j in range(1, int(round(hcm))):
        ctx.move_to(x, y - j * k)
        ctx.line_to(x + w, y - j * k)
        ctx.move_to(x + w, y - j * k)
        ctx.line_to(x + w + ox, y - j * k + oy)
    for d in range(1, int(round(dcm))):
        f = d / dcm
        ctx.move_to(x + ox * f, y - h + oy * f)
        ctx.line_to(x + w + ox * f, y - h + oy * f)
        ctx.move_to(x + w + ox * f, y - h + oy * f)
        ctx.line_to(x + w + ox * f, y + oy * f)
    ctx.stroke()
    ctx.set_line_width(max(1.2, 2.0 * sc))
    src(ctx, "#A57B45", 0.8 * a)
    ctx.rectangle(x, y - h, w, h)
    ctx.stroke()


def cube1000(ctx, x, y, sc=1.0, a=1.0, glow=0.0):
    block(ctx, x, y, 10, 10, 10, sc, a, glow)


def flat100(ctx, x, y, sc=1.0, a=1.0):
    block(ctx, x, y, 10, 1, 10, sc, a)


def stick10(ctx, x, y, sc=1.0, a=1.0, glow=0.0):
    block(ctx, x, y, 10, 1, 1, sc, a, glow)


def one1(ctx, x, y, sc=1.0, a=1.0, glow=0.0):
    block(ctx, x, y, 1, 1, 1, sc, a, glow)


def lockbox(ctx, digits, lid=0.0, roll=None):
    x0, x1, yb, h = BOX_X0, BOX_X1, BOX_Y, BOX_H
    yt = yb - h
    rig.soft_shadow(ctx, (x0 + x1) / 2 + 20, yb + 4, 230, 24, 0.3)
    # right side
    ctx.move_to(x1, yt)
    ctx.line_to(x1 + BOX_DX, yt + BOX_DY)
    ctx.line_to(x1 + BOX_DX, yb + BOX_DY)
    ctx.line_to(x1, yb)
    ctx.close_path()
    src(ctx, "#557C6A")
    ctx.fill()
    # top: lid closed, or open interior
    if lid <= 0:
        ctx.move_to(x0, yt)
        ctx.line_to(x0 + BOX_DX, yt + BOX_DY)
        ctx.line_to(x1 + BOX_DX, yt + BOX_DY)
        ctx.line_to(x1, yt)
        ctx.close_path()
        src(ctx, "#8DB6A2")
        ctx.fill()
        # carry handle
        ctx.set_line_width(9)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        src(ctx, "#3F5A4D")
        hx, hy = (x0 + x1) / 2 + BOX_DX / 2, yt + BOX_DY / 2
        ctx.move_to(hx - 60, hy + 4)
        ctx.curve_to(hx - 50, hy - 30, hx + 50, hy - 30, hx + 60, hy + 4)
        ctx.stroke()
    else:
        ctx.move_to(x0, yt)
        ctx.line_to(x0 + BOX_DX, yt + BOX_DY)
        ctx.line_to(x1 + BOX_DX, yt + BOX_DY)
        ctx.line_to(x1, yt)
        ctx.close_path()
        src(ctx, "#2F3B35")
        ctx.fill_preserve()
        ctx.save()
        ctx.clip()
        rig.ball(ctx, 760, yt - 6, 54, 54, "#B8423A", hi=0.32, lo=-0.3)     # 7.2 cm cricket ball
        ctx.set_line_width(3)
        src(ctx, "#F3E9DA", 0.9)
        ctx.arc(760, yt - 6, 46, math.radians(200), math.radians(340))
        ctx.stroke()
        ctx.restore()
        # lid rises from the back edge
        bl, br = (x0 + BOX_DX, yt + BOX_DY), (x1 + BOX_DX, yt + BOX_DY)
        fl = (lerp(x0, x0 + BOX_DX, lid), lerp(yt, yt + BOX_DY - 190, lid))
        fr = (lerp(x1, x1 + BOX_DX, lid), lerp(yt, yt + BOX_DY - 190, lid))
        ctx.move_to(*bl)
        ctx.line_to(*br)
        ctx.line_to(*fr)
        ctx.line_to(*fl)
        ctx.close_path()
        src(ctx, "#4E7363")
        ctx.fill()
    # front
    g = cairo.LinearGradient(x0, yt, x1, yb)
    g.add_color_stop_rgb(0, *R.rgb("#86AE9A"))
    g.add_color_stop_rgb(1, *R.rgb("#6E9A86"))
    ctx.set_source(g)
    ctx.rectangle(x0, yt, x1 - x0, h)
    ctx.fill()
    src(ctx, "#FFFFFF", 0.18)
    ctx.rectangle(x0, yt + 6, x1 - x0, 5)
    ctx.fill()
    # dial plate and four dials
    rrect(ctx, DIAL_X0 - 10, DIAL_Y - 8, 4 * DIAL_W + 3 * DIAL_GAP + 20, DIAL_H + 16, 8, "#34463D")
    for i in range(4):
        dx = DIAL_X0 + i * (DIAL_W + DIAL_GAP)
        rrect(ctx, dx, DIAL_Y, DIAL_W, DIAL_H, 5, "#F4EBDC")
        src(ctx, "#000000", 0.12)
        ctx.rectangle(dx, DIAL_Y, DIAL_W, 7)
        ctx.rectangle(dx, DIAL_Y + DIAL_H - 7, DIAL_W, 7)
        ctx.fill()
        text(ctx, str(digits[i]), dx + DIAL_W / 2, DIAL_Y + DIAL_H / 2 + 1, 26, INK)


def pouch(ctx, x, y, a=1.0):
    """Cloth drawstring pouch, about 10 cm wide and 12 cm tall."""
    if a <= 0:
        return
    rig.soft_shadow(ctx, x, y + 2, 95, 16, 0.25 * a)
    ctx.move_to(x - 75, y)
    ctx.curve_to(x - 95, y - 90, x - 55, y - 150, x - 30, y - 165)
    ctx.line_to(x + 30, y - 165)
    ctx.curve_to(x + 55, y - 150, x + 95, y - 90, x + 75, y)
    ctx.close_path()
    g = cairo.LinearGradient(x - 80, 0, x + 80, 0)
    g.add_color_stop_rgba(0, *R.rgb("#D8C49A"), a)
    g.add_color_stop_rgba(1, *R.rgb("#BFA77A"), a)
    ctx.set_source(g)
    ctx.fill()
    ellipse(ctx, x, y - 168, 42, 12, "#C9B48A", a)
    ctx.set_line_width(4)
    src(ctx, "#8A6A45", a)
    ctx.move_to(x - 34, y - 160)
    ctx.curve_to(x - 10, y - 150, x + 10, y - 150, x + 34, y - 160)
    ctx.stroke()
    # tag with a leaf (Mabel's garden)
    ctx.move_to(x + 30, y - 158)
    ctx.line_to(x + 70, y - 120)
    ctx.stroke()
    rrect(ctx, x + 58, y - 124, 44, 30, 6, "#FBF6EC", a)
    ellipse(ctx, x + 80, y - 109, 12, 7, R.LEAF, a)


def cricket_bug(ctx, x, y, f=1, kick=0.0):
    """Field cricket, about 2.5 cm long."""
    s = K / 10.0
    ellipse(ctx, x, y + 3 * s, 14 * s, 3 * s, "#000000", 0.15)
    ctx.set_line_width(1.6 * s)
    src(ctx, "#3B2A1E")
    ctx.move_to(x + 10 * s * f, y - 4 * s)
    ctx.curve_to(x + 22 * s * f, y - 18 * s, x + 30 * s * f, y - 16 * s, x + 36 * s * f, y - 22 * s)
    ctx.move_to(x + 10 * s * f, y - 4 * s)
    ctx.curve_to(x + 24 * s * f, y - 12 * s, x + 32 * s * f, y - 6 * s, x + 38 * s * f, y - 10 * s)
    ctx.stroke()
    rig.ball(ctx, x - 2 * s * f, y - 4 * s, 9 * s, 4.2 * s, "#4A3524", hi=0.3)
    rig.ball(ctx, x + 8 * s * f, y - 5 * s, 4 * s, 3.6 * s, "#3B2A1E", hi=0.3)
    ellipse(ctx, x + 10 * s * f, y - 6 * s, 1.2 * s, 1.2 * s, "#F3E9DA")
    ctx.set_line_width(2.2 * s)
    src(ctx, "#4A3524")
    kx = -8 - 6 * kick
    ctx.move_to(x - 2 * s * f, y - 4 * s)
    ctx.line_to(x + kx * s * f, y - 12 * s + 6 * kick * s)
    ctx.line_to(x + (kx - 6) * s * f, y + 2 * s + 6 * kick * s)
    ctx.stroke()


# ---------------------------------------------------------------- background
def park(ctx):
    g = cairo.LinearGradient(0, 0, 0, 640)
    g.add_color_stop_rgb(0, *R.rgb("#CFE2EC"))
    g.add_color_stop_rgb(1, *R.rgb("#EEF2E4"))
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, 660)
    ctx.fill()
    drift = NOW[0] * 6
    for cx0, cy0, cw in ((300, 120, 120), (850, 230, 150)):
        cx = (cx0 + drift) % 1500 - 200
        ellipse(ctx, cx, cy0, cw, cw * 0.34, "#FFFFFF", 0.75)
        ellipse(ctx, cx + cw * 0.4, cy0 - cw * 0.18, cw * 0.55, cw * 0.3, "#FFFFFF", 0.75)
    # far gum trees
    for i, (tx, tr) in enumerate(((170, 70), (300, 90), (430, 60), (980, 80), (1080, 70))):
        ellipse(ctx, tx, 470 - tr * 0.4, tr * 1.3, tr, "#9BAE8C", 0.9)
    # pavilion with a green roof
    rrect(ctx, 640, 420, 260, 120, 6, "#F1E6D2")
    ctx.move_to(620, 425)
    ctx.line_to(770, 360)
    ctx.line_to(920, 425)
    ctx.close_path()
    src(ctx, "#6F8F6C")
    ctx.fill()
    for k in range(4):
        rrect(ctx, 665 + k * 60, 455, 36, 50, 4, "#B9C9D6")
    # oval and its white boundary
    src(ctx, "#B3C99A")
    ctx.rectangle(0, 520, W, 140)
    ctx.fill()
    ctx.set_line_width(5)
    src(ctx, "#FFFFFF", 0.85)
    ctx.move_to(-20, 560)
    ctx.curve_to(300, 548, 780, 548, 1100, 560)
    ctx.stroke()
    ellipse(ctx, 540, 610, 160, 18, "#D8CDA6", 0.8)    # the pitch
    # picnic table top (planks)
    g = cairo.LinearGradient(0, 640, 0, 1920)
    g.add_color_stop_rgb(0, *R.rgb("#BE946A"))
    g.add_color_stop_rgb(1, *R.rgb("#A97E55"))
    ctx.set_source(g)
    ctx.rectangle(0, 640, W, 1920 - 640)
    ctx.fill()
    src(ctx, "#8E6643", 0.55)
    for yy in (640, 820, 1020, 1240, 1480):
        ctx.rectangle(0, yy, W, 6)
    ctx.fill()
    ctx.set_line_width(2)
    for i, yy in enumerate((700, 760, 900, 960, 1100, 1180, 1320, 1400, 1560, 1640)):
        src(ctx, "#9C7350", 0.22)
        ctx.move_to(0, yy + 6 * math.sin(i))
        ctx.curve_to(W * 0.3, yy - 8, W * 0.6, yy + 10, W, yy + 3 * math.cos(i))
        ctx.stroke()


# ---------------------------------------------------------------- views
def dial_digits(ep, T):
    s, e = ep.s(26), ep.e(26)
    out = []
    for i in range(4):
        t0 = s + (i + 0.2) / 4.4 * (e - s)
        p = prog(T, t0, t0 + 0.3)
        out.append(int(round(CODE[i] * p)))
    return out


def blocks_at(ep, T):
    """Positions of every block: loose, sliding into the mat columns during lines 19 and 21."""
    pc = prog(T, ep.s(19) + 1.0, ep.s(19) + 2.4)
    ps = prog(T, ep.s(21) - 0.1, ep.s(21) + 0.9)
    po = prog(T, ep.s(21) + 0.6, ep.s(21) + 1.6)
    cubes = [(lerp(a[0], b[0], pc), lerp(a[1], b[1], pc)) for a, b in zip(LOOSE_CUBES, MAT_CUBES)]
    sticks = [(lerp(a[0], b[0], ps), lerp(a[1], b[1], ps)) for a, b in zip(LOOSE_STICKS, MAT_STICKS)]
    ones = [(lerp(a[0], b[0], po), lerp(a[1], b[1], po)) for a, b in zip(LOOSE_ONES, MAT_ONES)]
    return cubes, sticks, ones


def count_glow(ep, T):
    s, e = ep.s(25), ep.e(25)
    d = e - s
    g1 = prog(T, s, s + 0.4) * (1 - prog(T, s + 0.25 * d, s + 0.25 * d + 0.4))
    g2 = prog(T, s + 0.25 * d, s + 0.25 * d + 0.4) * (1 - prog(T, s + 0.62 * d, s + 0.62 * d + 0.4))
    g3 = prog(T, s + 0.62 * d, s + 0.62 * d + 0.4) * (1 - prog(T, e + 0.6, e + 1.2))
    return g1, g2, g3


def draw_blocks(ctx, ep, T, a=1.0):
    cubes, sticks, ones = blocks_at(ep, T)
    g1, g2, g3 = count_glow(ep, T)
    # back to front: the stacked cube last so it sits on top
    order = [1, 0, 2] if T > ep.s(19) + 1.6 else [0, 1, 2]
    for i in order:
        cube1000(ctx, *cubes[i], a=a, glow=0.5 * g1 if i == 1 else 0.0)
    for i in range(4, -1, -1):
        stick10(ctx, *sticks[i], a=a, glow=0.45 * g2 if i == 2 else 0.0)
    for i in range(2):
        one1(ctx, *ones[i], a=a, glow=0.35 * g3 if i == 0 else 0.0)


def view_box(ctx, ep, T, end=False):
    lid = prog(T, ep.e(27) + 1.6, ep.e(27) + 2.3) if end else 0.0
    lockbox(ctx, dial_digits(ep, T) if end else (0, 0, 0, 0), lid)
    if not end:
        pa = 1 - prog(T, ep.s(7) - 0.5, ep.s(7) + 0.1)
        pouch(ctx, 300, 1235, pa)
        ba = prog(T, ep.s(7) - 0.2, ep.s(7) + 0.5)
        if ba > 0:
            draw_blocks(ctx, ep, T, ba)
            sparkles(ctx, 360, 1150, 300, ba * (1 - prog(T, ep.s(7) + 1.0, ep.s(7) + 2.0)), 0.4)
    else:
        bug(ctx, ep, T)


def bug(ctx, ep, T):
    t0 = ep.e(27) + 2.0                  # lid is open
    j1, j2, j3 = t0 + 0.2, ep.s(28) + 0.6, ep.e(29) + 0.4
    if T < j1:
        return
    if T < j1 + 0.7:                    # first hop: out of the box onto the table
        p = (T - j1) / 0.7
        x, y = lerp(780, 560, p), lerp(BOX_Y - BOX_H - 10, 1150, p) - 230 * math.sin(math.pi * p)
        cricket_bug(ctx, x, y, -1, 1.0)
    elif T < j2:
        cricket_bug(ctx, 560, 1150, -1)
    elif T < j2 + 0.6:                  # second hop: closer to Ivy and Otto, still above them
        p = (T - j2) / 0.6
        cricket_bug(ctx, lerp(560, 420, p), lerp(1150, 1210, p) - 150 * math.sin(math.pi * p), -1, 1.0)
    elif T < j3:
        cricket_bug(ctx, 420, 1210, -1)
    elif T < j3 + 0.9:                  # off it goes, out of the frame on the left
        p = (T - j3) / 0.9
        cricket_bug(ctx, lerp(420, -60, p), lerp(1210, 1100, p) - 200 * math.sin(math.pi * p), -1, 1.0)


def view_mat(ctx, ep, T):
    rig.soft_shadow(ctx, 540, MAT_Y1 + 4, 520, 26, 0.25)
    rrect(ctx, MAT_X0, MAT_Y0, MAT_X1 - MAT_X0, MAT_Y1 - MAT_Y0, 22, "#FBF6EC")
    hcol = {"Thousands": "#E9D6B0", "Hundreds": "#DCE6D2", "Tens": "#D9E3EC", "Ones": "#F0D9D2"}
    for name, x0, x1 in COLS:
        rrect(ctx, x0 + 8, MAT_Y0 + 8, x1 - x0 - 16, 58, 14, hcol[name])
        text(ctx, name, (x0 + x1) / 2, MAT_Y0 + 38, 30 if name != "Thousands" else 32, INK)
        if x0 > MAT_X0:
            ctx.set_line_width(4)
            src(ctx, "#D7C9B0")
            ctx.move_to(x0, MAT_Y0 + 76)
            ctx.line_to(x0, MAT_Y1 - 14)
            ctx.stroke()
    src(ctx, "#D7C9B0")
    ctx.rectangle(MAT_X0 + 14, DIGIT_Y - 62, MAT_X1 - MAT_X0 - 28, 3)
    ctx.fill()
    draw_blocks(ctx, ep, T)
    # digits written under each column
    times = (ep.s(19) + 0.75 * (ep.e(19) - ep.s(19)), ep.s(20) + 0.6 * (ep.e(20) - ep.s(20)),
             ep.s(21) + 0.3 * (ep.e(21) - ep.s(21)), ep.s(21) + 0.85 * (ep.e(21) - ep.s(21)))
    for (name, x0, x1), d, t0 in zip(COLS, CODE, times):
        a = prog(T, t0, t0 + 0.4)
        text(ctx, str(d), (x0 + x1) / 2, DIGIT_Y, 96, "#B4473E" if d == 0 else INK, a)


def mat_window(ep):
    return ep.s(19) - 0.8, ep.e(25) + 0.9


def scene(ctx, ep, T):
    park(ctx)
    m0, m1 = mat_window(ep)
    wm = prog(T, m0, m0 + 0.7) * (1 - prog(T, m1, m1 + 0.7))
    end = T > m1 + 0.35
    if wm < 1:
        view_box(ctx, ep, T, end=end)
    if wm > 0:
        ctx.push_group()
        view_mat(ctx, ep, T)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(wm)
    rig.squirrel(ctx, OTTO_X, FEET, SQ_S, OCHRE, f=1, seed=2.0)
    rig.bramble(ctx, BR_X, FEET, BR_S, f=1)
    rig.squirrel(ctx, IVY_X, FEET, SQ_S, SAGE, f=-1, seed=0.7)


# ---------------------------------------------------------------- cues, poses, foley
def cues(ep):
    m0, m1 = mat_window(ep)
    d22 = ep.e(22) - ep.s(22)
    return [
        ("ring", ep.s(1) - 0.1, ep.e(2) + 0.6, 838, 880, 260, 150),
        ("zoom", ep.s(7) + 0.2, ep.e(9) + 0.8, 540, 1650, 1.1),
        ("lens", ep.s(11) - 0.1, ep.e(11) + 1.0, *DIALS_C, 380, 600, 150, 2.0),
        ("zoom", ep.s(19) + 0.2, ep.e(21) + 0.6, 540, 1650, 1.08),
        ("ring", ep.s(22) - 0.1, ep.s(22) + 0.62 * d22, 535, 1030, 120, 260),
        ("lens", ep.s(26) - 0.2, ep.e(26) + 0.7, *DIALS_C, 380, 600, 150, 2.0),
        ("zoom", ep.e(27) + 1.7, ep.e(29) + 0.9, 540, 1650, 1.1),
    ]


def foley(ep):
    out = [("pop", ep.s(7) - 0.1), ("whoosh", mat_window(ep)[0]), ("whoosh", mat_window(ep)[1])]
    s, e = ep.s(26), ep.e(26)
    for i in range(4):
        out.append(("snip", s + (i + 0.2) / 4.4 * (e - s) + 0.25))
    out += [("pop", ep.s(6) + 0.6 * (ep.e(6) - ep.s(6))), ("whoosh", ep.e(27) + 1.6),
            ("step", ep.e(27) + 2.2), ("step", ep.e(27) + 2.9), ("step", ep.s(28) + 0.6),
            ("step", ep.s(28) + 1.2)]
    return out


def poses(ep, T):
    S, E = ep.s, ep.e

    def during(i, pre=0.2, post=0.6):
        return S(i) - pre <= T <= E(i) + post

    def ramp(t0):
        return prog(T, t0, t0 + 0.5)

    B = {"face": 1, "expr": "think"}
    O = {"face": 1}
    I = {"face": -1}
    if T < S(3):
        O["expr"] = "sad"
        I["expr"] = "think"
    if during(10, 0.2, 0.3):
        O.update(expr="happy", point=(330, 1120), amt=ramp(S(10)))
    if S(11) - 0.2 <= T <= E(12) + 0.4:
        O["expr"] = "think"
        I["expr"] = "think"
        B.update(point=DIALS_C, amt=ramp(S(11)))
    if S(13) - 0.2 <= T <= E(14) + 1.0:
        O["scratch"] = prog(T, S(13), S(13) + 0.6)
        O["expr"] = "think"
    if during(14):
        I.update(expr="surprise")
    if S(16) <= T <= S(19):
        O["expr"] = I["expr"] = "think"
    if during(22, 0.2, 0.2):
        I.update(point=(560, 1060), amt=ramp(S(22)))
        I["expr"] = "happy"
    if during(23, 0.2, 1.0):
        O["expr"] = "surprise"
    if S(26) - 0.2 <= T <= E(26) + 0.6:
        O["expr"] = "happy"
        B.update(point=DIALS_C, amt=ramp(S(26) - 0.2))
    if T >= S(27) - 0.2:
        B["expr"] = O["expr"] = I["expr"] = "happy"
        hop = (T - S(27)) / 0.55
        if 0 <= hop <= 1:
            O["jump"] = 42 * math.sin(math.pi * hop)
    if during(28, 0.3, 0.4):
        I["expr"] = O["expr"] = "surprise"
    if during(29, 0.1, 0.8):
        O["expr"] = "happy"
        O["scratch"] = prog(T, S(29), S(29) + 0.5) * (1 - prog(T, E(29) + 0.3, E(29) + 0.8))
    return {"B": B, "O": O, "I": I}


# ---------------------------------------------------------------- cards
def card(ctx, x, y, w, h, a, col="#FFFFFF"):
    rig.soft_shadow(ctx, x + w / 2, y + h + 6, w * 0.5, 16, 0.18 * a)
    rrect(ctx, x, y, w, h, 40, col, 0.95 * a)


def window(T, s, e, fin=0.35, fout=0.4):
    return prog(T, s, s + fin) * (1 - prog(T, e - fout, e))


def dial_row(ctx, cx, cy, digits, a, size=1.0, ring_i=None, blank=None):
    dw, dh, gap = 74 * size, 104 * size, 16 * size
    x0 = cx - (4 * dw + 3 * gap) / 2
    rrect(ctx, x0 - 16 * size, cy - dh / 2 - 14 * size, 4 * dw + 3 * gap + 32 * size, dh + 28 * size,
          18 * size, "#34463D", a)
    for i in range(4):
        x = x0 + i * (dw + gap)
        rrect(ctx, x, cy - dh / 2, dw, dh, 12 * size, "#F4EBDC", a)
        d = digits[i]
        if d is None:
            text(ctx, "?", x + dw / 2, cy, 64 * size, "#A99D90", a)
        else:
            text(ctx, str(d), x + dw / 2, cy, 70 * size, "#B4473E" if i == ring_i else INK, a)
        if i == ring_i:
            ctx.set_line_width(7 * size)
            src(ctx, "#F2C85B", a)
            ctx.arc(x + dw / 2, cy, dh * 0.62, 0, 2 * math.pi)
            ctx.stroke()


def coin(ctx, x, y, a):
    r = 1.25 * K                         # $1 coin, 25 mm across
    rig.ball(ctx, x, y, r, r, "#D9B44A", a, hi=0.35, lo=-0.25)
    ctx.set_line_width(2)
    src(ctx, "#A9832A", a)
    ctx.arc(x, y, r * 0.78, 0, 2 * math.pi)
    ctx.stroke()
    text(ctx, "1", x, y + 1, 18, "#7A5A1A", a)


def note10(ctx, x, y, a):
    w, h = 13.7 * K, 6.5 * K             # $10 note, 137 x 65 mm
    rrect(ctx, x - w / 2, y - h / 2, w, h, 8, "#6E8FC4", a)
    rrect(ctx, x - w / 2 + 8, y - h / 2 + 8, w - 16, h - 16, 6, "#8FAAD6", a)
    ellipse(ctx, x + w * 0.22, y, h * 0.28, h * 0.32, "#C9D7EE", a)
    text(ctx, "10", x - w * 0.22, y + 2, 46, "#FFFFFF", a)


def cards(ctx, ep, T):
    S, E = ep.s, ep.e
    # Today's case title (read word for word)
    a = window(T, S(3) - 0.3, E(3) + 0.9)
    if a > 0:
        card(ctx, 70, 140, 940, 420, a)
        rrect(ctx, 120, 184, 60, 46, 8, OCHRE, a)
        rrect(ctx, 120, 176, 28, 14, 5, OCHRE, a)
        text(ctx, "Today's case", 560, 210, 46, "#9C7429", a)
        for k, s_ in enumerate(("A code hidden in", "thousands, hundreds,", "tens and ones")):
            text(ctx, s_, W / 2, 300 + k * 82, 64, INK, a)
    # digits 0 to 9
    a = window(T, S(4) - 0.2, E(4) + 0.6)
    if a > 0:
        card(ctx, 70, 170, 940, 240, a)
        text(ctx, "Digits", W / 2, 225, 44, "#9C7429", a)
        for d in range(10):
            text(ctx, str(d), 140 + d * 89, 330, 74, INK, a * prog(T, S(4) + 0.05 * d, S(4) + 0.05 * d + 0.3))
    # place value: the same 7 in different places
    a = window(T, S(5) - 0.2, E(5) + 1.2)
    if a > 0:
        card(ctx, 70, 150, 940, 340, a)
        for k, (num, lab, x) in enumerate((("700", "7 hundreds", 230), ("70", "7 tens", 540), ("7", "7 ones", 850))):
            ak = a * prog(T, S(5) + 0.4 * k, S(5) + 0.4 * k + 0.4)
            ctx.select_font_face(R.FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(110)
            tw = ctx.text_extents(num)[4]
            cw = ctx.text_extents("7")[4]
            xx = x - tw / 2
            for ch in num:
                ctx.move_to(xx, 330)
                src(ctx, OCHRE if ch == "7" else INK, ak)
                ctx.show_text(ch)
                xx += cw
            text(ctx, lab, x, 420, 38, "#7A6E62", ak)
    # canteen: ten $1 coins make one $10 note
    a = window(T, S(6) - 0.2, E(6) + 1.3)
    if a > 0:
        card(ctx, 70, 150, 940, 420, a)
        text(ctx, "Canteen", W / 2, 205, 44, "#9C7429", a)
        merge = prog(T, S(6) + 0.55 * (E(6) - S(6)), S(6) + 0.75 * (E(6) - S(6)))
        for i in range(10):
            x0 = 290 + (i - 4.5) * 50
            cx = lerp(x0, 540 - 230, merge)
            coin(ctx, cx, 330, a * (1 - merge))
        if merge > 0:
            note10(ctx, 540, 330, a * merge)
        text(ctx, "10 ones = 1 ten", W / 2, 490, 50, INK, a * prog(T, E(6) - 0.4, E(6)))
    # number block key
    a = window(T, S(8) - 0.2, E(9) + 1.0)
    if a > 0:
        card(ctx, 70, 120, 940, 520, a)
        sc = 0.62
        a1 = a * prog(T, S(8), S(8) + 0.4)
        a2 = a * prog(T, S(8) + 0.5 * (E(8) - S(8)), S(8) + 0.5 * (E(8) - S(8)) + 0.4)
        a3 = a * prog(T, S(9), S(9) + 0.4)
        a4 = a * prog(T, S(9) + 0.5 * (E(9) - S(9)), S(9) + 0.5 * (E(9) - S(9)) + 0.4)
        cube1000(ctx, 130, 330, sc, a1)
        text(ctx, "thousand", 380, 280, 46, INK, a1)
        flat100(ctx, 590, 330, sc, a2)
        text(ctx, "hundred", 850, 280, 46, INK, a2)
        stick10(ctx, 130, 520, sc, a3)
        text(ctx, "ten", 380, 505, 46, INK, a3)
        one1(ctx, 610, 520, 1.0, a4)
        text(ctx, "one", 850, 505, 46, INK, a4)
    # Otto's guess: three digits for four dials
    a = window(T, S(10) + 0.6 * (E(10) - S(10)), E(11) + 1.0)
    if a > 0:
        card(ctx, 190, 150, 700, 240, a)
        dial_row(ctx, W / 2, 270, (3, 5, 2, None), a)
    # no hundreds
    a = window(T, S(14) - 0.2, E(14) + 1.0)
    if a > 0:
        card(ctx, 190, 150, 700, 260, a)
        flat100(ctx, 270, 330, 0.6, a * 0.35)
        text(ctx, "hundreds:", 620, 250, 50, INK, a)
        text(ctx, "0", 620, 340, 90, "#B4473E", a)
    # A or B
    aA = window(T, S(16) - 0.2, E(22) + 1.4)
    if aA > 0:
        aB = aA * prog(T, S(17) - 0.2, S(17) + 0.2)
        aA2 = aA * prog(T, S(16) - 0.2, S(16) + 0.2)
        d22 = E(22) - S(22)
        picked = prog(T, S(22) + 0.7 * d22, S(22) + 0.7 * d22 + 0.4)
        for lab, x, digits, aa, pk in (("A", 70, (3, 5, 2, 0), aA2, 0.0), ("B", 560, (3, 0, 5, 2), aB, picked)):
            dim = picked if lab == "A" else 0.0
            ak = aa * (1 - 0.5 * dim)
            card(ctx, x, 150, 450, 300, aa)
            ellipse(ctx, x + 64, 210, 38, 38, OCHRE if lab == "A" else SAGE, ak)
            text(ctx, lab, x + 64, 212, 48, "#FFFFFF", ak)
            dial_row(ctx, x + 225, 340, digits, ak, size=0.8)
            if pk > 0:
                ctx.set_line_width(10)
                src(ctx, GREEN, pk * aa)
                ctx.new_sub_path()
                r = 40
                x0, y0, w, h = x, 150, 450, 300
                ctx.arc(x0 + w - r, y0 + r, r, -math.pi / 2, 0)
                ctx.arc(x0 + w - r, y0 + h - r, r, 0, math.pi / 2)
                ctx.arc(x0 + r, y0 + h - r, r, math.pi / 2, math.pi)
                ctx.arc(x0 + r, y0 + r, r, math.pi, 1.5 * math.pi)
                ctx.close_path()
                ctx.stroke()
                ellipse(ctx, x + w - 56, 210, 36, 36, GREEN, pk * aa)
                ctx.set_line_width(9)
                ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                src(ctx, "#FFFFFF", pk * aa)
                ctx.move_to(x + w - 72, 210)
                ctx.line_to(x + w - 60, 223)
                ctx.line_to(x + w - 38, 197)
                ctx.stroke()
        # think ring fills during the 5 s pause, then a small tick
        g0, g1 = E(18) + 0.2, E(18) + 4.9
        ra = aA * window(T, S(18), S(19) + 0.3, 0.3, 0.4)
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
    # counting on: 3000, 3050, 3052
    a = window(T, S(25) - 0.3, E(25) + 1.2)
    if a > 0:
        d = E(25) - S(25)
        n = "3000" if T < S(25) + 0.25 * d else ("3050" if T < S(25) + 0.62 * d else "3052")
        card(ctx, 290, 170, 500, 230, a)
        text(ctx, n, W / 2, 285, 120, INK, a)
    # recap
    ra = window(T, S(30) - 0.3, S(33) - 0.1, 0.5, 0.5)
    if ra > 0:
        card(ctx, 60, 130, 960, 1010, ra, "#FBF6EC")
        rrect(ctx, 300, 160, 480, 110, 50, OCHRE, ra)
        text(ctx, "Remember", W / 2, 215, 62, "#FFFFFF", ra)
        r1 = ra * prog(T, S(30) + 0.3, S(30) + 0.9)
        rrect(ctx, 100, 320, 880, 330, 36, "#FFFFFF", 0.95 * r1)
        dial_row(ctx, W / 2, 420, CODE, r1, size=0.75, ring_i=1)
        text(ctx, "Zero holds the place", W / 2, 575, 56, INK, r1)
        r2 = ra * prog(T, S(32), S(32) + 0.6)
        rrect(ctx, 100, 700, 880, 380, 36, "#FFFFFF", 0.95 * r2)
        text(ctx, "Try it at home:", W / 2, 770, 50, "#9C7429", r2)
        text(ctx, "make a secret code", W / 2, 850, 56, INK, r2)
        text(ctx, "with a zero", W / 2, 920, 56, INK, r2)
        dial_row(ctx, W / 2, 1010, (None, 0, None, None), r2, size=0.5)
    # teaser
    ta = window(T, S(33) - 0.1, ep.total - 1.0, 0.4, 0.5)
    if ta > 0:
        card(ctx, 140, 200, 800, 470, ta)
        rrect(ctx, 330, 230, 420, 100, 46, SAGE, ta)
        text(ctx, "Next case", W / 2, 280, 54, "#FFFFFF", ta)
        for k in range(10):
            x = 210 + k * 73
            y = 440 + (12 if k % 2 else 0)
            ellipse(ctx, x, y + 12, 22, 27, "#B07A43", ta)
            rrect(ctx, x - 26, y - 22, 52, 22, 10, "#7A5A3A", ta)
            rrect(ctx, x - 3, y - 34, 6, 14, 3, "#5E4630", ta)
        text(ctx, "Counting to 10", W / 2, 590, 60, INK, ta)
