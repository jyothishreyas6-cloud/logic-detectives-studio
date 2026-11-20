"""Episode 008: The till that won't balance (Years 3 to 4, Maths, Additive relations:
adding and subtracting with regrouping).

Setting: the surf club kiosk at the beach, late morning. Otto added up the till: a float of
$38 plus $27 of icy pole sales. He wrote 55, because 8 + 7 = 15 and he kept only the 5. The
money on the counting mat says otherwise. Regroup means swapping ten ones for one ten, like
ten $1 coins for a $10 note. Test: 8 coins and 7 coins make 15; swap ten for a note; 6 tens
and 5 ones is $65. Second proof: 65 take away 27 (regroup a ten into ten ones) leaves 38, the
float. Funny moment: Otto "carries the ten" on his head like a surfboard.

True sizes (K = 16 px per cm): squirrel sitting 20 cm, hedgehog 12 cm tall and 20 cm long.
Australian $1 coin 25 mm across (40 px). $10 note 137 by 65 mm (219 by 104 px). The counting
mat is 55 by 40 cm (880 by 640 px). The till sits further back on the counter (about 0.5
scale). The clipboard hangs on the kiosk window frame behind.
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
MAT_X, MAT_Y, MAT_W, MAT_H = 100, 650, 880, 640
TENS_X, ONES_X = 285, 725
NOTE_W, NOTE_H = 219, 104
COIN_R = 20
NOTE_Y0, NOTE_DY = 770, 62
COIN_DX = 58
CLIP = (230, 400)              # middle of Otto's clipboard sum
COINS = (ONES_X, 900)          # middle of the coins
TILL = (820, 622)              # middle of the till's base

CASE_NO = 8
RULE = "Ten ones and one ten are worth the same."
SETTING = "the surf club kiosk at the beach"
SENTENCE_LIMIT = 10

LINES = [
    Line("B", "Case open!", gap=0.4),                                          # 0
    Line("O", "Oh no! The till won't balance!", gap=0.6),                      # 1
    Line("I", "The sheet and the money don't match.", gap=0.8),                # 2
    Line("N", "Today's case: the till that won't balance.", gap=0.7),          # 3
    Line("N", "Regroup means swapping ten ones for one ten.", gap=0.8),        # 4
    Line("N", "Like ten one-dollar coins for a ten-dollar note.", gap=1.0),    # 5
    Line("N", "The till started with 38 dollars.", gap=0.6),                   # 6
    Line("N", "Then the kiosk sold 27 dollars of icy poles.", gap=0.8),        # 7
    Line("O", "Easy! Eight plus seven is fifteen. I'll write five.", gap=0.6), # 8
    Line("O", "Three plus two is five. So, 55 dollars!", gap=0.8),             # 9
    Line("I", "Hmm. Where did the extra ten go?", gap=0.8),                    # 10
    Line("B", "Let's not guess. Let's test.", gap=0.8),                        # 11
    Line("B", "Can you point to the one-dollar coins?", gap=4.0),              # 12
    Line("B", "How much should be in the till?", gap=0.8),                     # 13
    Line("N", "A. 55 dollars.", gap=0.6),                                      # 14
    Line("N", "B. 65 dollars.", gap=0.6),                                      # 15
    Line("N", "Pause and think.", gap=5.0),                                    # 16
    Line("N", "Ten ones and one ten are worth the same.", gap=0.8),            # 17
    Line("N", "Eight coins and seven coins make fifteen coins.", gap=0.8),     # 18
    Line("N", "Swap ten coins for one ten-dollar note.", gap=1.0),             # 19
    Line("N", "Now there are six tens and five ones.", gap=0.8),               # 20
    Line("N", "That's 65 dollars.", gap=0.8),                                  # 21
    Line("N", "It's B! 65 dollars.", gap=0.6),                                 # 22
    Line("O", "Oh! I forgot the ten from the swap!", gap=0.8),                 # 23
    Line("B", "Let's check another way. Take the sales away.", gap=0.8),       # 24
    Line("N", "65 take away 27. Five ones can't lose seven.", gap=0.8),        # 25
    Line("N", "So swap one ten for ten ones. Fifteen ones.", gap=0.8),         # 26
    Line("N", "Fifteen take away seven leaves eight.", gap=0.8),               # 27
    Line("N", "Five tens take away two tens leaves three.", gap=0.8),          # 28
    Line("N", "38 dollars. Just what the till started with!", gap=0.8),        # 29
    Line("I", "Now the till balances!", gap=0.8),                              # 30
    Line("B", "Case solved!", gap=1.9),                                        # 31
    Line("O", "Don't worry. I'll carry the ten!", gap=0.8),                    # 32
    Line("I", "Not like a surfboard, Otto!", gap=1.0),                         # 33
    Line("N", "Remember. Ten ones and one ten are worth the same.", gap=0.9),  # 34
    Line("N", "Say it with me. Ten ones and one ten are worth the same.", gap=2.2),  # 35
    Line("N", "Try it at home. Bundle ten pegs to make one ten.", gap=0.9),    # 36
    Line("N", "Next case: ladybird dots at a glance.", gap=0.6),               # 37
]

STRIP_HIDDEN = {3, 31, 34}
CHILD_TURN = 35
STAMP_LINE = 31
OPEN_LINE = 0
CUT = [(0, 3), (8, 10), (17, 23), (31, 31), (35, 35), (37, 37)]


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


def coin(ctx, x, y, a=1.0, r=COIN_R):
    """Australian $1 coin (25 mm across), gold coloured."""
    if a <= 0:
        return
    rig.soft_shadow(ctx, x + 2, y + r * 0.8, r * 0.9, r * 0.25, 0.18 * a)
    ellipse(ctx, x, y, r, r, "#D8B24C", a)
    ctx.set_line_width(max(1.5, r * 0.12))
    src(ctx, "#B08A2E", a)
    ctx.arc(x, y, r * 0.74, 0, 2 * math.pi)
    ctx.stroke()
    ellipse(ctx, x - r * 0.3, y - r * 0.35, r * 0.3, r * 0.2, "#FFF3C4", 0.6 * a)


def note(ctx, x, y, a=1.0, sc=1.0, rot=0.0):
    """Australian $10 note (137 by 65 mm), blue; (x, y) is its middle."""
    if a <= 0:
        return
    w, h = NOTE_W * sc, NOTE_H * sc
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    rig.soft_shadow(ctx, 4, h / 2, w * 0.45, 8 * sc, 0.16 * a)
    rrect(ctx, -w / 2, -h / 2, w, h, 10 * sc, "#6F9FCB", a)
    rrect(ctx, -w / 2 + 8 * sc, -h / 2 + 8 * sc, w - 16 * sc, h - 16 * sc, 8 * sc, "#9CC0DF", a)
    ellipse(ctx, 0, 0, 30 * sc, 34 * sc, "#6F9FCB", a)
    text(ctx, "10", -w / 2 + 40 * sc, -h / 2 + 32 * sc, 28 * sc, "#2F5B86", a)
    text(ctx, "10", w / 2 - 40 * sc, h / 2 - 30 * sc, 28 * sc, "#2F5B86", a)
    ctx.restore()


def mat(ctx):
    """Place-value counting mat on the counter: Tens on the left, Ones on the right."""
    rig.soft_shadow(ctx, MAT_X + MAT_W / 2, MAT_Y + MAT_H + 8, MAT_W * 0.5, 16, 0.2)
    rrect(ctx, MAT_X, MAT_Y, MAT_W, MAT_H, 30, "#EFE8D6")
    rrect(ctx, MAT_X, MAT_Y, MAT_W, 90, 30, "#E2D6BC")
    ctx.rectangle(MAT_X, MAT_Y + 60, MAT_W, 30)
    src(ctx, "#E2D6BC")
    ctx.fill()
    rrect(ctx, 468, MAT_Y + 14, 6, MAT_H - 28, 3, "#CDBE9F")
    text(ctx, "Tens", TENS_X, MAT_Y + 46, 46, "#2F5B86")
    text(ctx, "Ones", ONES_X, MAT_Y + 46, 46, "#9C7429")


def till(ctx, x, y, a=1.0, screen="$ ?"):
    """A shop till; (x, y) is the middle of its base."""
    rig.soft_shadow(ctx, x, y + 4, 160, 12, 0.2 * a)
    rrect(ctx, x - 150, y - 60, 300, 60, 12, "#8E7F70", a)        # drawer
    rrect(ctx, x - 20, y - 36, 40, 12, 6, "#C9B9A2", a)
    rrect(ctx, x - 130, y - 170, 260, 110, 18, "#B9A98F", a)       # keys
    for r in range(2):
        for c in range(4):
            rrect(ctx, x - 104 + c * 56, y - 152 + r * 46, 40, 32, 8, "#F4EEE3", a)
    rrect(ctx, x - 80, y - 250, 160, 70, 14, "#5E6B5A", a)          # screen
    text(ctx, screen, x, y - 214, 40, "#E9F2D8", a)


def clipboard(ctx, fixed=0.0):
    """Otto's sum on a clipboard: 38 + 27 = 55, corrected to 65 with a carried 1."""
    x0, y0, w, h = 90, 200, 290, 380
    rig.soft_shadow(ctx, x0 + w / 2 + 6, y0 + h + 6, w * 0.45, 10, 0.2)
    rrect(ctx, x0, y0, w, h, 18, "#A98463")
    rrect(ctx, x0 + 16, y0 + 30, w - 32, h - 46, 8, "#FBF8F0")
    rrect(ctx, x0 + w / 2 - 50, y0 - 12, 100, 40, 10, "#9AA3A8")
    tx, ox = 230, 290                                    # tens and ones columns
    letter(ctx, "3", tx, 330, 72)
    letter(ctx, "8", ox, 330, 72)
    letter(ctx, "+", 160, 420, 66)
    letter(ctx, "2", tx, 420, 72)
    letter(ctx, "7", ox, 420, 72)
    rrect(ctx, 140, 440, 200, 8, 4, INK)
    letter(ctx, "5", ox, 530, 72)
    letter(ctx, "5", tx, 530, 72, INK, 1 - fixed)
    if fixed > 0:
        letter(ctx, "6", tx, 530, 72, OCHRE, fixed)
        letter(ctx, "1", tx, 262, 40, OCHRE, fixed)       # the carried ten


def ladybird(ctx, x, y, r, a):
    ellipse(ctx, x - r * 0.95, y, r * 0.42, r * 0.42, INK, a)        # head
    ellipse(ctx, x, y, r, r * 0.82, "#C9473F", a)
    ellipse(ctx, x - r * 0.3, y - r * 0.35, r * 0.3, r * 0.16, "#FFFFFF", 0.35 * a)
    rrect(ctx, x - r, y - 3, 2 * r, 6, 3, INK, a)
    for dx, dy in ((-0.45, -0.45), (0.1, -0.5), (0.55, -0.3), (-0.4, 0.42), (0.15, 0.5), (0.6, 0.3)):
        ellipse(ctx, x + dx * r, y + dy * r, r * 0.13, r * 0.13, INK, a)


def peg(ctx, x, y, a, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    rrect(ctx, -7, -46, 14, 92, 5, "#C9A57E", a)
    rrect(ctx, -5, -6, 10, 10, 3, "#8E7F70", a)
    ctx.restore()


# ---------------------------------------------------------------- background
def kiosk(ctx, T, ep):
    # kiosk wall and awning
    rrect(ctx, 0, 0, W, 640, 0, "#E8DCC6")
    for k in range(9):
        src(ctx, "#C9605A" if k % 2 == 0 else "#F4EEE3")
        ctx.rectangle(k * 120, 0, 120, 70)
        ctx.fill()
    # window onto the beach
    wx0, wy0, wx1, wy1 = 40, 96, 1040, 600
    g = cairo.LinearGradient(0, wy0, 0, 360)
    g.add_color_stop_rgb(0, *R.rgb("#BFDCEB"))
    g.add_color_stop_rgb(1, *R.rgb("#E8F3F4"))
    ctx.set_source(g)
    ctx.rectangle(wx0, wy0, wx1 - wx0, 270)
    ctx.fill()
    drift = NOW[0] * 5
    for cx0, cy0, cw in ((300, 170, 110), (800, 220, 130)):
        cx = (cx0 + drift) % 1300 - 100
        ellipse(ctx, cx, cy0, cw, cw * 0.3, "#FFFFFF", 0.75)
    src(ctx, "#6FA7BF")
    ctx.rectangle(wx0, 360, wx1 - wx0, 70)
    ctx.fill()
    for k in range(5):                                    # gentle waves
        xx = (90 + k * 210 + NOW[0] * 12) % 1000 + 40
        ellipse(ctx, xx, 410, 60, 6, "#FFFFFF", 0.5)
    src(ctx, "#EAD8B0")
    ctx.rectangle(wx0, 430, wx1 - wx0, 170)
    ctx.fill()
    # beach umbrella and a Norfolk pine
    rrect(ctx, 597, 380, 6, 150, 3, "#8E7F70")
    src(ctx, "#E9C46A")
    ctx.move_to(500, 410)
    ctx.curve_to(530, 340, 670, 340, 700, 410)
    ctx.close_path()
    ctx.fill()
    rrect(ctx, 952, 180, 12, 260, 4, "#8E6F5E")
    for k in range(6):
        wdt = 30 + k * 16
        ellipse(ctx, 958, 200 + k * 40, wdt, 16, "#5F7F5A", 0.95)
    # window frame
    src(ctx, "#A98463")
    ctx.set_line_width(24)
    ctx.rectangle(wx0, wy0, wx1 - wx0, wy1 - wy0)
    ctx.stroke()
    # counter top
    g = cairo.LinearGradient(0, 600, 0, 1920)
    g.add_color_stop_rgb(0, *R.rgb("#CDAE86"))
    g.add_color_stop_rgb(1, *R.rgb("#B9966C"))
    ctx.set_source(g)
    ctx.rectangle(0, 600, W, 1320)
    ctx.fill()
    rrect(ctx, 0, 600, W, 22, 0, "#A98463")
    src(ctx, "#B08C64", 0.5)
    for k in range(7):
        ctx.rectangle(0, 700 + k * 170, W, 3)
    ctx.fill()


# ---------------------------------------------------------------- money on the mat
def coin_spots(ep, T):
    """Where each of the 15 coins is (x, y, alpha). Float coins 0..7, sales coins 8..14."""
    S, E = ep.s, ep.e
    m = ease(prog(T, S(18) + 0.2, S(18) + 1.4))                 # the two groups join
    sw = ease(prog(T, S(19) + 0.6, S(19) + 1.6))                 # ten coins go to the tens
    up = ease(prog(T, S(19) + 1.8, S(19) + 2.4))                 # the last row slides up
    out = []
    for j in range(15):
        if j < 8:
            r0, c0 = divmod(j, 5)
            y0 = 790 + r0 * 58
        else:
            r0, c0 = divmod(j - 8, 5)
            y0 = 960 + r0 * 58
        x0 = ONES_X - 2 * COIN_DX + c0 * COIN_DX
        r1, c1 = divmod(j, 5)
        x1 = ONES_X - 2 * 70 + c1 * 70
        y1 = 800 + r1 * 72
        x, y = lerp(x0, x1, m), lerp(y0, y1, m)
        a = 1.0
        if j < 10:
            x, y = lerp(x, TENS_X, sw), lerp(y, NOTE_Y0 + 5 * NOTE_DY, sw)
            a = 1 - prog(T, S(19) + 1.3, S(19) + 1.7)
        else:
            y = lerp(y, 800, up)
        out.append((x, y, a))
    return out


def note_spots(ep, T):
    S = ep.s
    m = ease(prog(T, S(18) + 0.2, S(18) + 1.4))
    out = []
    for k in range(5):
        y = NOTE_Y0 + k * NOTE_DY + (40 * (1 - m) if k >= 3 else 0)
        out.append((TENS_X, y, 1.0))
    out.append((TENS_X, NOTE_Y0 + 5 * NOTE_DY, prog(T, S(19) + 1.3, S(19) + 1.7)))
    return out


def carry_ten(ep, T):
    """Otto lifts the top-most note onto his head (lines 32 to 33) and puts it back."""
    S, E = ep.s, ep.e
    k = ease(prog(T, S(32) + 0.2, S(32) + 0.9)) * (1 - ease(prog(T, E(33) + 0.3, E(33) + 1.0)))
    return k


# ---------------------------------------------------------------- scene
def scene(ctx, ep, T):
    S, E = ep.s, ep.e
    kiosk(ctx, T, ep)
    clipboard(ctx, prog(T, S(23), S(23) + 0.5))
    till(ctx, *TILL, screen="$65" if T >= S(30) else "$ ?")
    mat(ctx)
    lift = carry_ten(ep, T)
    for k, (x, y, a) in enumerate(note_spots(ep, T)):
        if k == 5 and lift > 0.05:
            continue
        note(ctx, x, y, a)
    for x, y, a in coin_spots(ep, T):
        coin(ctx, x, y, a)
    rig.squirrel(ctx, OTTO_X, FEET, SQ_S, OCHRE, f=1, seed=2.0)
    if lift > 0.05:                                       # the note sits on Otto's head
        x, y, a = note_spots(ep, T)[5]
        note(ctx, lerp(x, OTTO_X + 10, lift), lerp(y, 1322, lift), a, 1.0, -0.08 * lift)
    rig.bramble(ctx, BR_X, FEET, BR_S, f=1)
    rig.squirrel(ctx, IVY_X, FEET, SQ_S, SAGE, f=-1, seed=0.7)


# ---------------------------------------------------------------- cues, poses, foley
def cues(ep):
    return [
        ("ring", ep.s(1) - 0.1, ep.e(2) + 0.5, 235, 430, 170, 190),
        ("zoom", ep.s(8) - 0.2, ep.e(10) + 0.5, 420, 1000, 1.1),
        ("ring", ep.s(12) - 0.1, ep.e(12) + 3.8, ONES_X, 900, 210, 190),
        ("zoom", ep.s(18) - 0.3, ep.e(21) + 0.4, 540, 1000, 1.1),
        ("ring", ep.s(23) - 0.1, ep.e(23) + 0.5, 235, 420, 170, 190),
        ("zoom", ep.s(32) - 0.2, ep.e(33) + 0.6, 360, 1350, 1.1),
    ]


def foley(ep):
    S = ep.s
    out = [("whoosh", S(3) - 0.3), ("whoosh", S(4) - 0.3), ("whoosh", S(14) - 0.3),
           ("pop", S(18) + 0.6), ("whoosh", S(19) + 0.7), ("pop", S(19) + 1.5),
           ("pop", S(23) + 0.2), ("whoosh", S(25) - 0.3)]
    out += [("pop", S(i) + 0.3) for i in (26, 27, 28)]
    out.append(("step", S(31) + 0.5))
    out.append(("whoosh", S(32) + 0.3))
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
        O.update(point=(CLIP[0], 520), amt=ramp(S(1)))
    if during(2, 0.1, 0.4):
        I.update(expr="think", point=COINS, amt=ramp(S(2)))
    if S(8) - 0.3 <= T <= E(9) + 0.4:
        O.update(expr="happy", point=(CLIP[0], 520), amt=ramp(S(8) - 0.3))
    if during(10, 0.2, 0.8):
        I.update(expr="think", point=COINS, amt=ramp(S(10) - 0.2))
        O["expr"] = "think"
    if S(11) - 0.2 <= T <= E(12) + 3.8:
        B["expr"] = "think" if T < S(12) else "happy"
    if S(12) - 0.1 <= T <= E(12) + 3.6:
        B.update(point=COINS, amt=ramp(S(12) - 0.1))
    if S(13) <= T <= S(17):
        O["expr"] = I["expr"] = "think"
    if during(17, 0.2, 0.6):
        B["expr"] = "think"
    if S(18) - 0.1 <= T <= E(21) + 0.4:
        B.update(expr="happy", point=(ONES_X - 60, 860), amt=ramp(S(18) - 0.1))
    if during(22, 0.2, 0.3):
        I["expr"] = "happy"
    if during(23, 0.2, 0.8):
        O["expr"] = "surprise"
        O["scratch"] = prog(T, S(23) + 0.3, S(23) + 0.8) * (1 - prog(T, E(23) + 0.4, E(23) + 0.8))
    if S(24) - 0.2 <= T <= E(29) + 0.4:
        B["expr"] = "think" if T < S(29) else "happy"
        O["expr"] = I["expr"] = "think" if T < S(29) else "happy"
    if during(30, 0.2, 0.6):
        I["expr"] = "happy"
    if T >= S(31) - 0.2:
        B["expr"] = O["expr"] = I["expr"] = "happy"
        hop = (T - S(31)) / 0.55
        if 0 <= hop <= 1:
            O["jump"] = 42 * math.sin(math.pi * hop)
    if S(32) <= T <= E(33) + 0.9:
        O.update(expr="happy", point=(OTTO_X + 60, 1300), amt=ramp(S(32) + 0.2))
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



def ten_for_one(ctx, x, y, a, sc=1.0):
    """Ten $1 coins = one $10 note (the regroup picture); (x, y) is the middle."""
    for k in range(10):
        r, c = divmod(k, 5)
        coin(ctx, x - 250 * sc + c * 46 * sc, y - 23 * sc + r * 46 * sc, a, COIN_R * sc)
    text(ctx, "=", x + 20 * sc, y, 64 * sc, INK, a)
    note(ctx, x + 200 * sc, y, a, 0.95 * sc)


def column_sum(ctx, T, ep, a):
    """65 take away 27, regrouping one ten into ten ones."""
    S = ep.s
    tx, ox = 480, 620
    r1 = a * prog(T, S(26), S(26) + 0.4)
    letter(ctx, "6", tx, 330, 84, INK, a)
    letter(ctx, "5", ox, 330, 84, INK, a)
    if r1 > 0:
        ctx.set_line_width(7)
        src(ctx, OCHRE, r1)
        for x in (tx, ox):
            ctx.move_to(x - 30, 320)
            ctx.line_to(x + 30, 270)
        ctx.stroke()
        letter(ctx, "5", tx, 240, 46, OCHRE, r1)
        letter(ctx, "15", ox, 240, 46, OCHRE, r1)
    letter(ctx, "−", 360, 430, 80, INK, a)
    letter(ctx, "2", tx, 430, 84, INK, a)
    letter(ctx, "7", ox, 430, 84, INK, a)
    rrect(ctx, 330, 454, 340, 8, 4, INK, a)
    letter(ctx, "8", ox, 548, 84, GREEN, a * prog(T, S(27) + 0.3, S(27) + 0.6))
    letter(ctx, "3", tx, 548, 84, GREEN, a * prog(T, S(28) + 0.3, S(28) + 0.6))
    letter(ctx, "$", 360, 548, 70, GREEN, a * prog(T, S(29), S(29) + 0.3))


def cards(ctx, ep, T):
    S, E = ep.s, ep.e
    # Today's case title (read word for word)
    a = window(T, S(3) - 0.3, E(3) + 0.9)
    if a > 0:
        card(ctx, 70, 140, 940, 420, a)
        rrect(ctx, 120, 184, 60, 46, 8, OCHRE, a)
        rrect(ctx, 120, 176, 28, 14, 5, OCHRE, a)
        text(ctx, "Today's case", 560, 210, 46, "#9C7429", a)
        for k, s_ in enumerate(("The till that", "won't balance")):
            text(ctx, s_, W / 2, 330 + k * 92, 68, INK, a)
    # regroup: swap ten ones for one ten
    a = window(T, S(4) - 0.2, E(5) + 0.9)
    if a > 0:
        card(ctx, 70, 140, 940, 420, a)
        text(ctx, "Regroup = swap", W / 2, 206, 50, "#9C7429", a)
        text(ctx, "ten ones for one ten", W / 2, 268, 50, "#9C7429", a)
        b = a * prog(T, S(5) - 0.2, S(5) + 0.3)
        ten_for_one(ctx, W / 2, 400, b)
        text(ctx, "10 ones", 345, 500, 40, INK, b)
        text(ctx, "1 ten", 760, 500, 40, INK, b)
    # A or B
    aA = window(T, S(14) - 0.2, E(22) + 0.6)
    if aA > 0:
        aA2 = aA * prog(T, S(14) - 0.2, S(14) + 0.2)
        aB = aA * prog(T, S(15) - 0.2, S(15) + 0.2)
        d = E(22) - S(22)
        picked = prog(T, S(22) + 0.2 * d, S(22) + 0.2 * d + 0.4)
        ak = aA2 * (1 - 0.5 * picked)
        card(ctx, 70, 150, 450, 300, aA2)
        ellipse(ctx, 134, 210, 38, 38, OCHRE, ak)
        text(ctx, "A", 134, 212, 48, "#FFFFFF", ak)
        text(ctx, "$55", 295, 320, 84, INK, ak)
        card(ctx, 560, 150, 450, 300, aB)
        ellipse(ctx, 624, 210, 38, 38, SAGE, aB)
        text(ctx, "B", 624, 212, 48, "#FFFFFF", aB)
        text(ctx, "$65", 785, 320, 84, INK, aB)
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
    # check another way: 65 take away 27
    a = window(T, S(25) - 0.3, E(29) + 0.8)
    if a > 0:
        card(ctx, 250, 150, 580, 450, a)
        column_sum(ctx, T, ep, a)
    # recap
    ra = window(T, S(34) - 0.3, S(37) - 0.1, 0.5, 0.5)
    if ra > 0:
        card(ctx, 30, 130, 1020, 900, ra, "#FBF6EC", 1.0)
        rrect(ctx, 300, 160, 480, 110, 50, OCHRE, ra)
        text(ctx, "Remember", W / 2, 215, 62, "#FFFFFF", ra)
        r1 = ra * prog(T, S(34) + 0.3, S(34) + 0.9)
        rrect(ctx, 100, 300, 880, 320, 36, "#FFFFFF", 0.95 * r1)
        ctx.push_group()
        ten_for_one(ctx, W / 2, 390, 1.0, 0.85)
        text(ctx, "Ten ones and one ten", W / 2, 506, 56, INK)
        text(ctx, "are worth the same.", W / 2, 574, 56, INK)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(r1)
        r2 = ra * prog(T, S(36), S(36) + 0.6)
        rrect(ctx, 100, 650, 880, 350, 36, "#FFFFFF", 0.95 * r2)
        text(ctx, "Try it at home:", W / 2, 712, 50, "#9C7429", r2)
        text(ctx, "bundle ten pegs", W / 2, 790, 56, INK, r2)
        for k in range(10):
            peg(ctx, 300 + k * 14, 900, r2, (k - 4.5) * 0.03)
        rrect(ctx, 286, 892, 154, 14, 7, "#C9605A", r2)
        text(ctx, "=", 540, 900, 64, INK, r2)
        word_chip(ctx, "1 ten", 740, 900, r2, INK, "#FBF1DC", 52)
    # teaser
    ta = window(T, S(37) - 0.1, ep.total - 1.0, 0.4, 0.5)
    if ta > 0:
        card(ctx, 140, 170, 800, 460, ta)
        rrect(ctx, 330, 200, 420, 100, 46, SAGE, ta)
        text(ctx, "Next case", W / 2, 250, 54, "#FFFFFF", ta)
        ladybird(ctx, W / 2, 430, 90, ta)
        text(ctx, "Ladybird dots at a glance", W / 2, 580, 44, INK, ta)
