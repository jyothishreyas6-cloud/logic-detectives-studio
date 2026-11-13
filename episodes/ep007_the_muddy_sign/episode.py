"""Episode 007: The muddy sign (Years 1 to 2, English, Phonic knowledge: digraphs sh, ch).

Setting: Mabel's farm stall on a country lane, the morning after rain. Mud has splashed
over Mabel's new sign, so nobody can read the stall's name. A digraph is two letters that
make one sound (sh like fish, ch like chips). Pip wipes the mud away and Otto sounds out
every letter: "Suh-huh-op!" Reading s and h as one sound gives "Shop": Mabel's Shop.
Second proof: count the sounds with sound buttons (one line under sh, a dot under o and
p): four letters, three sounds. Funny moment: Otto tries ch and sounds like a train.

True sizes (K = 16 px per cm): squirrel sitting 20 cm, hedgehog 12 cm tall and 20 cm long,
mouse about 8 cm. A small hand-painted stall sign is about 40 by 20 cm (640 by 320 px) on
a 2.5 cm post. The stall stands further back (drawn at about 0.3 scale): an 80 cm table,
a 30 cm egg carton and 7 cm lemons.
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
SIGN_X, SIGN_T, SIGN_B = 540, 680, 1000   # sign board: 640 px (40 cm) wide, top and bottom
SIGN_W = 40 * K
POST_B = 1330                  # where the post meets the lane
BASE = 940                     # baseline of the big letters
LET = (("S", 392), ("h", 488), ("o", 612), ("p", 716))
MARK_Y = 974                   # sound buttons under the letters
MUD = (452, 880)               # middle of the mud splash
WORD = (556, 880)              # middle of the word
PIP_REST = (800, SIGN_T)       # Pip sits on the top edge of the sign

CASE_NO = 7
RULE = "Two letters can make one sound."
SETTING = "Mabel's farm stall on a country lane"
SENTENCE_LIMIT = 8

LINES = [
    Line("B", "Case open!", gap=0.4),                                          # 0
    Line("O", "Oh no! Mud on Mabel's new sign!", gap=0.6),                     # 1
    Line("I", "Now we can't read the name.", gap=0.8),                         # 2
    Line("N", "Today's case: the name on a muddy sign.", gap=0.7),             # 3
    Line("N", "A digraph means two letters, one sound.", gap=0.8),             # 4
    Line("N", "S and h say sh. Like fish.", gap=0.8,
         say="S and H say shh. Like fish."),                                   # 5
    Line("N", "C and h say ch. Like chips.", gap=1.0,
         say="C and H say chuh. Like chips."),                      # 6
    Line("N", "Pip wipes the mud away.", gap=0.8),                             # 7
    Line("O", "S. H. O. P. Suh-huh-op!", gap=0.8,
         say="S. H. O. P. Suh. Huh. Op!"),                                     # 8
    Line("I", "Hmm. That's not a word.", gap=0.8),                             # 9
    Line("B", "Let's not guess. Let's test.", gap=0.8),                        # 10
    Line("B", "Can you show me the sh sound?", gap=4.0,
         say="Can you show me the shh sound?"),                                # 11
    Line("B", "What does the sign say?", gap=0.8),                             # 12
    Line("N", "A. Suh-huh-op.", gap=0.6, say="A. Suh. Huh. Op."),              # 13
    Line("N", "B. Shop.", gap=0.6),                                            # 14
    Line("N", "Pause and think.", gap=5.0),                                    # 15
    Line("N", "Two letters can make one sound.", gap=0.8),                     # 16
    Line("N", "S and h make sh.", gap=0.8, say="S and H make shh."),           # 17
    Line("N", "Sh. Op.", gap=1.0, say="Shh. Op."),                             # 18
    Line("N", "Shop!", gap=0.8),                                               # 19
    Line("N", "It's B! Shop.", gap=0.6),                                       # 20
    Line("O", "Oh! It says Mabel's Shop!", gap=0.8),                           # 21
    Line("B", "Let's check another way. Count the sounds.", gap=0.8),          # 22
    Line("N", "Sh is one sound. One line.", gap=0.8,
         say="Shh is one sound. One line."),                                   # 23
    Line("N", "O and p. Two dots.", gap=0.8),                                  # 24
    Line("N", "Four letters. Three sounds.", gap=0.8),                         # 25
    Line("I", "Three sounds make shop!", gap=0.8),                             # 26
    Line("B", "Case solved!", gap=1.9),                                        # 27
    Line("I", "Now try ch, Otto.", gap=0.8, say="Now try chuh, Otto."),  # 28
    Line("O", "Ch, ch, ch! I sound like a train!", gap=1.0,
         say="Chuh, chuh, chuh! I sound like a train!"),                       # 29
    Line("N", "Remember. Two letters can make one sound.", gap=0.9),           # 30
    Line("N", "Say it with me. Two letters can make one sound.", gap=2.2),     # 31
    Line("N", "Try it at home. Hunt for sh words.", gap=0.9,
         say="Try it at home. Hunt for shh words."),                           # 32
    Line("N", "Next case: the till that won't balance.", gap=0.6),             # 33
]

STRIP_HIDDEN = {3, 27, 30}
CHILD_TURN = 31
STAMP_LINE = 27
OPEN_LINE = 0
CUT = [(0, 3), (8, 8), (12, 12), (16, 20), (23, 25), (27, 27), (31, 31), (33, 33)]


# ---------------------------------------------------------------- props
def letter(ctx, s, x, base, size, col=INK, a=1.0):
    """One glyph centred on x, sitting on a shared baseline (so h, o and p line up)."""
    if a <= 0:
        return
    ctx.select_font_face(R.FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    xb, yb, tw, th, xa, _ = ctx.text_extents(s)
    ctx.move_to(x - tw / 2 - xb, base)
    src(ctx, col, a)
    ctx.show_text(s)


def mud_blob(ctx, x, y, a):
    for dx, dy, rx, ry, col in ((-70, -10, 112, 70, "#7A5A40"), (40, 20, 92, 60, "#6E5039"),
                                (-20, 60, 70, 40, "#7A5A40"), (-110, 50, 40, 26, "#6E5039"),
                                (90, -50, 36, 24, "#7A5A40"), (-60, -40, 30, 16, "#9A7658")):
        ellipse(ctx, x + dx, y + dy, rx, ry, col, a)
    for dx, ln in ((-90, 70), (10, 96), (70, 60)):      # drips
        rrect(ctx, x + dx - 9, y + 40, 18, ln, 9, "#6E5039", a)


def sign(ctx, mud=1.0, gold=0.0):
    """Mabel's stall sign on its post. mud 1 = fully splashed, 0 = wiped clean."""
    x0 = SIGN_X - SIGN_W / 2
    rig.soft_shadow(ctx, SIGN_X + 10, POST_B + 4, 70, 12, 0.25)
    g = cairo.LinearGradient(SIGN_X - 20, 0, SIGN_X + 20, 0)
    g.add_color_stop_rgb(0, *R.rgb("#9C7A5E"))
    g.add_color_stop_rgb(1, *R.rgb("#7A5C45"))
    ctx.set_source(g)
    ctx.rectangle(SIGN_X - 20, SIGN_B - 10, 40, POST_B - SIGN_B + 10)
    ctx.fill()
    rig.soft_shadow(ctx, SIGN_X + 12, SIGN_B + 14, SIGN_W * 0.48, 12, 0.18)
    rrect(ctx, x0, SIGN_T, SIGN_W, SIGN_B - SIGN_T, 22, "#A98463")
    rrect(ctx, x0 + 16, SIGN_T + 16, SIGN_W - 32, SIGN_B - SIGN_T - 32, 14, "#F3E6CB")
    src(ctx, "#E6D3AE", 0.6)
    for k in range(4):                                   # painted board grain
        yy = SIGN_T + 70 + k * 72
        ctx.rectangle(x0 + 30, yy, SIGN_W - 60, 3)
    ctx.fill()
    text(ctx, "Mabel's", SIGN_X, SIGN_T + 66, 52, "#6E8460")
    for j, (s, x) in enumerate(LET):
        col = INK
        if j < 2 and gold > 0:
            col = OCHRE if gold > 0.5 else INK
        letter(ctx, s, x, BASE, 168, col)
    if mud > 0:
        mud_blob(ctx, *MUD, mud)


def sound_line(ctx, a, glow=0.0):
    if a <= 0:
        return
    w = 1 + 0.12 * glow
    rrect(ctx, 340 - 8 * glow, MARK_Y - 9 * w, 200 + 16 * glow, 18 * w, 9, OCHRE, a)


def sound_dots(ctx, a, t=None, t0=0.0):
    for k, (s, x) in enumerate(LET[2:]):
        b = a if t is None else a * prog(t, t0 + k * 0.45, t0 + k * 0.45 + 0.15)
        if b > 0:
            ellipse(ctx, x, MARK_Y, 13, 13, OCHRE, b)


def cloth(ctx, x, y, a):
    rrect(ctx, x - 34, y - 26, 68, 52, 10, "#8FB4C8", a)
    src(ctx, "#FFFFFF", 0.5 * a)
    ctx.rectangle(x - 34, y - 6, 68, 6)
    ctx.rectangle(x - 6, y - 26, 6, 52)
    ctx.fill()


def fish(ctx, x, y, s, a):
    ellipse(ctx, x, y, 46 * s, 26 * s, "#8FB4C8", a)
    src(ctx, "#8FB4C8", a)
    ctx.move_to(x + 40 * s, y)
    ctx.line_to(x + 74 * s, y - 24 * s)
    ctx.line_to(x + 74 * s, y + 24 * s)
    ctx.close_path()
    ctx.fill()
    ellipse(ctx, x - 24 * s, y - 6 * s, 6 * s, 6 * s, INK, a)


def chips(ctx, x, y, s, a):
    src(ctx, "#E9C46A", a)
    for k, (dx, h) in enumerate(((-26, 70), (-12, 84), (2, 76), (16, 88), (28, 68))):
        ctx.save()
        ctx.translate(x + dx * s, y - 20 * s)
        ctx.rotate((k - 2) * 0.12)
        ctx.rectangle(-6 * s, -h * s, 12 * s, h * s)
        ctx.restore()
    ctx.fill()
    src(ctx, "#C9605A", a)
    ctx.move_to(x - 44 * s, y - 34 * s)
    ctx.line_to(x + 44 * s, y - 34 * s)
    ctx.line_to(x + 32 * s, y + 34 * s)
    ctx.line_to(x - 32 * s, y + 34 * s)
    ctx.close_path()
    ctx.fill()


def till(ctx, x, y, a):
    """A shop till for the teaser; (x, y) is the middle of its base."""
    rrect(ctx, x - 150, y - 60, 300, 60, 12, "#8E7F70", a)        # drawer
    rrect(ctx, x - 20, y - 36, 40, 12, 6, "#C9B9A2", a)
    rrect(ctx, x - 130, y - 170, 260, 110, 18, "#B9A98F", a)       # keys
    for r in range(2):
        for c in range(4):
            rrect(ctx, x - 104 + c * 56, y - 152 + r * 46, 40, 32, 8, "#F4EEE3", a)
    rrect(ctx, x - 80, y - 250, 160, 70, 14, "#5E6B5A", a)          # screen
    text(ctx, "$ ?", x, y - 214, 40, "#E9F2D8", a)


def stall(ctx):
    """Mabel's honesty stall, further back on the left (about 0.3 scale)."""
    rig.soft_shadow(ctx, 200, 1252, 190, 10, 0.18)
    for lx in (40, 360):
        rrect(ctx, lx, 1120, 14, 130, 4, "#8E6F5E")
    rrect(ctx, 20, 1100, 360, 26, 8, "#A98463")
    rrect(ctx, 20, 1124, 360, 8, 4, "#8E6F5E")
    rrect(ctx, 30, 940, 12, 165, 4, "#8E6F5E")                      # awning posts
    rrect(ctx, 358, 940, 12, 165, 4, "#8E6F5E")
    for k in range(6):
        src(ctx, "#C9605A" if k % 2 == 0 else "#F4EEE3")
        ctx.rectangle(14 + k * 62, 920, 62, 40)
        ctx.fill()
    rrect(ctx, 60, 1062, 144, 40, 8, "#C9B9A2")                     # egg carton
    for k in range(6):
        ellipse(ctx, 76 + k * 22, 1062, 9, 11, "#F6EFE2")
    for k, (dx, dy) in enumerate(((0, 0), (20, 0), (40, 0), (10, -14), (30, -14))):
        ellipse(ctx, 250 + dx, 1088 + dy, 11, 10, "#E9C46A")         # lemons
    rrect(ctx, 316, 1070, 40, 32, 6, "#6E8460")                     # honesty box
    rrect(ctx, 326, 1074, 20, 4, 2, INK)


# ---------------------------------------------------------------- background
def lane(ctx):
    g = cairo.LinearGradient(0, 0, 0, 640)
    g.add_color_stop_rgb(0, *R.rgb("#C9DCE6"))
    g.add_color_stop_rgb(1, *R.rgb("#EEF2E6"))
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, 640)
    ctx.fill()
    drift = NOW[0] * 5
    for cx0, cy0, cw in ((260, 160, 120), (820, 260, 150)):
        cx = (cx0 + drift) % 1500 - 200
        ellipse(ctx, cx, cy0, cw, cw * 0.34, "#FFFFFF", 0.75)
        ellipse(ctx, cx + cw * 0.4, cy0 - cw * 0.18, cw * 0.55, cw * 0.3, "#FFFFFF", 0.75)
    # far hills and paddock
    src(ctx, "#A9BC92")
    ctx.move_to(0, 700)
    ctx.curve_to(260, 560, 520, 640, 760, 600)
    ctx.curve_to(900, 580, 1000, 620, W, 610)
    ctx.line_to(W, 900)
    ctx.line_to(0, 900)
    ctx.close_path()
    ctx.fill()
    g = cairo.LinearGradient(0, 680, 0, 1160)
    g.add_color_stop_rgb(0, *R.rgb("#B8C99C"))
    g.add_color_stop_rgb(1, *R.rgb("#9FB384"))
    ctx.set_source(g)
    ctx.move_to(0, 760)
    ctx.curve_to(300, 700, 700, 740, W, 700)
    ctx.line_to(W, 1180)
    ctx.line_to(0, 1180)
    ctx.close_path()
    ctx.fill()
    # wire fence along the paddock
    ctx.set_line_width(3)
    src(ctx, "#8E7F70", 0.7)
    for yy in (1012, 1040):
        ctx.move_to(0, yy)
        ctx.line_to(W, yy - 20)
    ctx.stroke()
    for k in range(9):
        xx = 20 + k * 130
        rrect(ctx, xx, 990 - k * 2.4, 10, 80, 3, "#9C7A5E")
    # gum tree on the right
    src(ctx, "#D9D2C4")
    ctx.move_to(950, 1180)
    ctx.curve_to(960, 900, 940, 700, 990, 520)
    ctx.line_to(1020, 520)
    ctx.curve_to(1000, 720, 1010, 940, 1040, 1180)
    ctx.close_path()
    ctx.fill()
    for cx, cy, r in ((930, 470, 110), (1040, 420, 120), (1000, 540, 90)):
        ellipse(ctx, cx, cy, r, r * 0.7, "#7E9468", 0.95)
    # dirt lane after rain
    g = cairo.LinearGradient(0, 1160, 0, 1920)
    g.add_color_stop_rgb(0, *R.rgb("#CDB48F"))
    g.add_color_stop_rgb(1, *R.rgb("#B99D78"))
    ctx.set_source(g)
    ctx.rectangle(0, 1170, W, 750)
    ctx.fill()
    src(ctx, "#B9A07C")
    ctx.move_to(0, 1180)
    ctx.curve_to(400, 1160, 700, 1190, W, 1170)
    ctx.line_to(W, 1186)
    ctx.curve_to(700, 1206, 400, 1176, 0, 1196)
    ctx.close_path()
    ctx.fill()
    for px, py, rx, ry in ((760, 1300, 110, 22), (320, 1356, 80, 16), (980, 1420, 70, 14)):
        ellipse(ctx, px, py, rx, ry, "#9FB7C2", 0.85)
        ellipse(ctx, px - rx * 0.3, py - ry * 0.3, rx * 0.35, ry * 0.3, "#FFFFFF", 0.35)
    for i in range(16):
        xb = 30 + (i * 173) % 1020
        yb = 1440 + (i * 89) % 230
        ellipse(ctx, xb, yb, 6, 4, "#A88C68", 0.7)


# ---------------------------------------------------------------- scene
def wipe(ep):
    d = ep.e(7) - ep.s(7)
    return ep.s(7) + 0.15 * d, ep.e(7) + 0.5


def scene(ctx, ep, T):
    S, E = ep.s, ep.e
    lane(ctx)
    stall(ctx)
    w0, w1 = wipe(ep)
    mud = 1 - prog(T, w0 + 0.3, w1)
    gold = prog(T, S(17), S(17) + 0.3) * (1 - prog(T, E(20), E(20) + 0.4))
    sign(ctx, mud, gold)
    # sound buttons: the line under sh from line 17, the dots from line 24
    sound_line(ctx, prog(T, S(17) + 0.4, S(17) + 0.7) * (1 - prog(T, ep.total - 1.2, ep.total - 0.6)),
               max(0.0, 1 - abs(T - S(23) - 0.6) / 0.6))
    if T >= S(24):
        sound_dots(ctx, 1 - prog(T, ep.total - 1.2, ep.total - 0.6), T, S(24) + 0.2)
    # Pip walks along the top of the sign, wipes the mud with a cloth, then walks back
    go = prog(T, w0 - 0.4, w0)
    back = prog(T, w1 - 0.2, w1 + 0.4)
    px = lerp(PIP_REST[0], MUD[0] + 40, ease(go) * (1 - ease(back)))
    f = -1 if go > 0 and back < 1 else 1
    if w0 <= T <= w1:
        k = (T - w0) / (w1 - w0)
        cx = MUD[0] - 60 + 120 * (0.5 + 0.5 * math.sin(k * 6 * math.pi))
        cy = MUD[1] - 50 + 100 * k
        ctx.set_line_width(5)
        src(ctx, "#A8A29A")
        ctx.move_to(px - 20, SIGN_T - 20)
        ctx.line_to(cx, cy - 20)
        ctx.stroke()
        cloth(ctx, cx, cy, 1.0)
    R.mouse(ctx, px, SIGN_T, 1.3, f)
    rig.squirrel(ctx, OTTO_X, FEET, SQ_S, OCHRE, f=1, seed=2.0)
    rig.bramble(ctx, BR_X, FEET, BR_S, f=1)
    rig.squirrel(ctx, IVY_X, FEET, SQ_S, SAGE, f=-1, seed=0.7)


# ---------------------------------------------------------------- cues, poses, foley
def cues(ep):
    return [
        ("ring", ep.s(1) - 0.1, ep.e(2) + 0.5, MUD[0], MUD[1] + 10, 200, 120),
        ("zoom", ep.s(8) - 0.2, ep.e(9) + 0.5, 545, 1150, 1.1),
        ("ring", ep.s(12) - 0.1, ep.e(12) + 0.5, WORD[0], WORD[1] - 10, 260, 110),
        ("zoom", ep.s(17) - 0.3, ep.e(20) + 0.4, 540, 1100, 1.1),
        ("lens", ep.s(23) - 0.3, ep.e(25) + 0.6, 556, MARK_Y - 50, 760, 1190, 140, 1.6),
    ]


def foley(ep):
    w0, w1 = wipe(ep)
    out = [("whoosh", ep.s(3) - 0.3), ("whoosh", ep.s(4) - 0.3), ("whoosh", w0 + 0.2),
           ("whoosh", ep.s(13) - 0.3), ("pop", ep.s(17) + 0.5)]
    out += [("pop", ep.s(24) + 0.2 + k * 0.45) for k in range(2)]
    out.append(("step", ep.s(27) + 0.5))
    return out


def poses(ep, T):
    S, E = ep.s, ep.e

    def during(i, pre=0.2, post=0.6):
        return S(i) - pre <= T <= E(i) + post

    def ramp(t0):
        return prog(T, t0, t0 + 0.5)

    sh = (440, 900)
    B = {"face": 1}
    O = {"face": 1}
    I = {"face": -1}
    if T < S(3):
        O["expr"] = "sad"
    if during(1, 0.1, 0.3):
        O.update(point=MUD, amt=ramp(S(1)))
    if during(2, 0.1, 0.4):
        I.update(expr="think", point=MUD, amt=ramp(S(2)))
    if during(8, 0.3, 0.4):
        O.update(expr="happy", point=WORD, amt=ramp(S(8) - 0.3))
    if during(9, 0.2, 0.8):
        I.update(expr="think", point=WORD, amt=ramp(S(9) - 0.2))
        O["expr"] = "think"
    if S(10) - 0.2 <= T <= E(11) + 3.8:
        B["expr"] = "think" if T < S(11) else "happy"
    if S(12) <= T <= S(16):
        O["expr"] = I["expr"] = "think"
    if S(16) - 0.2 <= T <= E(16) + 0.6:
        B["expr"] = "think"
    if S(17) - 0.1 <= T <= E(19) + 0.4:
        B.update(expr="happy", point=sh, amt=ramp(S(17) - 0.1))
    if during(20, 0.2, 0.3):
        I["expr"] = "happy"
    if during(21, 0.2, 0.8):
        O["expr"] = "surprise"
        O["scratch"] = prog(T, S(21) + 0.3, S(21) + 0.8) * (1 - prog(T, E(21) + 0.4, E(21) + 0.8))
    if S(22) - 0.2 <= T <= E(25) + 0.4:
        B.update(expr="think", point=(WORD[0], MARK_Y - 30), amt=ramp(S(22) - 0.2))
    if during(26, 0.2, 0.6):
        I["expr"] = "happy"
    if T >= S(27) - 0.2:
        B["expr"] = O["expr"] = I["expr"] = "happy"
        hop = (T - S(27)) / 0.55
        if 0 <= hop <= 1:
            O["jump"] = 42 * math.sin(math.pi * hop)
    if during(29, 0.1, 0.5):
        O["expr"] = "surprise"
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



def sh_mark(ctx, x, y, a, size=96):
    """The digraph 'sh' with its sound-button line underneath."""
    text(ctx, "sh", x, y, size, INK, a)
    rrect(ctx, x - 0.62 * size, y + 0.62 * size, 1.24 * size, 14, 7, OCHRE, a)


def cards(ctx, ep, T):
    S, E = ep.s, ep.e
    # Today's case title (read word for word)
    a = window(T, S(3) - 0.3, E(3) + 0.9)
    if a > 0:
        card(ctx, 70, 140, 940, 420, a)
        rrect(ctx, 120, 184, 60, 46, 8, OCHRE, a)
        rrect(ctx, 120, 176, 28, 14, 5, OCHRE, a)
        text(ctx, "Today's case", 560, 210, 46, "#9C7429", a)
        for k, s_ in enumerate(("The name on", "a muddy sign")):
            text(ctx, s_, W / 2, 330 + k * 92, 68, INK, a)
    # a digraph: two letters, one sound (sh like fish, ch like chips)
    a = window(T, S(4) - 0.2, E(6) + 0.9)
    if a > 0:
        card(ctx, 70, 140, 940, 420, a)
        text(ctx, "Digraph = two letters, one sound", W / 2, 196, 42, "#9C7429", a)
        for k, (dg, word, i) in enumerate((("sh", "fish", 5), ("ch", "chips", 6))):
            b = a * prog(T, S(i) - 0.2, S(i) + 0.2)
            if b <= 0:
                continue
            y = 318 + k * 136
            word_chip(ctx, dg, 250, y, b, INK, "#FBF1DC", 64)
            text(ctx, "like", 440, y, 44, "#9C7429", b)
            if k == 0:
                fish(ctx, 610, y, 1.0, b)
            else:
                chips(ctx, 610, y + 20, 0.8, b)
            text(ctx, word, 830, y, 56, INK, b)
    # show me the sh sound
    a = window(T, S(11) - 0.1, E(11) + 3.9)
    if a > 0:
        card(ctx, 290, 170, 500, 300, a)
        ph = (T - S(11)) * 1.0
        pulse = 1 + 0.10 * max(0.0, math.sin(2 * math.pi * ph)) ** 4
        sh_mark(ctx, W / 2, 300, a, 110 * pulse)
    # A or B
    aA = window(T, S(13) - 0.2, E(20) + 1.4)
    if aA > 0:
        aA2 = aA * prog(T, S(13) - 0.2, S(13) + 0.2)
        aB = aA * prog(T, S(14) - 0.2, S(14) + 0.2)
        d = E(20) - S(20)
        picked = prog(T, S(20) + 0.2 * d, S(20) + 0.2 * d + 0.4)
        ak = aA2 * (1 - 0.5 * picked)
        card(ctx, 70, 150, 450, 300, aA2)
        ellipse(ctx, 134, 210, 38, 38, OCHRE, ak)
        text(ctx, "A", 134, 212, 48, "#FFFFFF", ak)
        text(ctx, "Suh-huh-op", 295, 320, 54, INK, ak)
        card(ctx, 560, 150, 450, 300, aB)
        ellipse(ctx, 624, 210, 38, 38, SAGE, aB)
        text(ctx, "B", 624, 212, 48, "#FFFFFF", aB)
        text(ctx, "Shop", 785, 320, 70, INK, aB)
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
    # four letters, three sounds
    a = window(T, S(25) - 0.2, E(26) + 0.8)
    if a > 0:
        card(ctx, 150, 190, 780, 240, a)
        word_chip(ctx, "4 letters", 345, 310, a, INK, "#FBF1DC", 52)
        word_chip(ctx, "3 sounds", 735, 310, a * prog(T, S(25) + 0.6, S(25) + 0.9), INK, "#FBF1DC", 52)
    # ch, ch, ch: Otto the train
    a = window(T, S(29) - 0.1, E(29) + 0.6, 0.3, 0.4)
    if a > 0:
        card(ctx, 150, 210, 780, 220, a)
        for k in range(3):
            b = a * prog(T, S(29) + k * 0.35, S(29) + k * 0.35 + 0.15)
            word_chip(ctx, "ch", 340 + k * 200, 320, b, INK, "#FBF1DC", 60)
    # recap
    ra = window(T, S(30) - 0.3, S(33) - 0.1, 0.5, 0.5)
    if ra > 0:
        card(ctx, 30, 130, 1020, 900, ra, "#FBF6EC", 1.0)
        rrect(ctx, 300, 160, 480, 110, 50, OCHRE, ra)
        text(ctx, "Remember", W / 2, 215, 62, "#FFFFFF", ra)
        r1 = ra * prog(T, S(30) + 0.3, S(30) + 0.9)
        rrect(ctx, 100, 300, 880, 320, 36, "#FFFFFF", 0.95 * r1)
        ctx.push_group()
        sh_mark(ctx, W / 2, 380, 1.0, 88)
        text(ctx, "Two letters can", W / 2, 506, 56, INK)
        text(ctx, "make one sound.", W / 2, 574, 56, INK)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(r1)
        r2 = ra * prog(T, S(32), S(32) + 0.6)
        rrect(ctx, 100, 650, 880, 350, 36, "#FFFFFF", 0.95 * r2)
        text(ctx, "Try it at home:", W / 2, 712, 50, "#9C7429", r2)
        text(ctx, "hunt for sh words", W / 2, 796, 56, INK, r2)
        for k, w_ in enumerate(("shoe", "shell", "brush")):
            word_chip(ctx, w_, 270 + k * 270, 900, r2, INK, "#FBF1DC", 46)
    # teaser
    ta = window(T, S(33) - 0.1, ep.total - 1.0, 0.4, 0.5)
    if ta > 0:
        card(ctx, 140, 170, 800, 460, ta)
        rrect(ctx, 330, 200, 420, 100, 46, SAGE, ta)
        text(ctx, "Next case", W / 2, 250, 54, "#FFFFFF", ta)
        till(ctx, W / 2, 555, ta)
        text(ctx, "The till that won't balance", W / 2, 600, 42, INK, ta)
