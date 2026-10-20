"""Short 1 v13 scene layouts: true-to-life sizes and no overlapping subjects.

Sizes (real life, used to set every scale):
  red squirrel sitting, feet to ear tips ~20 cm   hedgehog ~12 cm tall, ~20 cm long
  ribbon 20 cm (two 10 cm halves; Otto's mark at 12 cm)   cookie 8 cm across
  toy kite 14 cm tall   children's scissors 9 cm   ruler: 10 cm marked
At scale s, a squirrel drawing is 208*s px tall, so one scene's px-per-cm is k = 10.4*s.
A hedgehog drawn at 0.95x the squirrel scale is 0.6x as tall (12 cm vs 20 cm), as in life.
A character nearer the camera may be up to ~10% larger (perspective).

Layout rules: characters never overlap each other; each object of interest has its own
space; speech bubbles, labels and cards sit in clear areas; the whole 9:16 frame is used.
Scene-local times match v7.SCENES, so the v12 timeline, audio and warp still apply.
"""
import math

import cairo

import render as R
import v6
from render import (W, H, INK, OCHRE, SAGE, RIBBON, RIBBON_D, SPINE_D, ellipse, rrect, text, src,
                    prog, clamp, lerp, glow, sparkles, NOW)

PX_PER_CM_SQ = 10.4          # squirrel scale 1.0 -> 10.4 px per cm


def sq_s(k):
    return k / PX_PER_CM_SQ


def br_s(k, near=1.0):
    return 0.95 * k / PX_PER_CM_SQ * near


# ---------------------------------------------------------------- backgrounds
def garden(ctx, ox=0.0):
    """Garden without falling leaves; butterflies stay in the top corners, away from subjects."""
    g = cairo.LinearGradient(0, 0, 0, 1000)
    g.add_color_stop_rgb(0, *R.rgb(R.SKY_T))
    g.add_color_stop_rgb(1, *R.rgb(R.SKY_B))
    ctx.set_source(g)
    ctx.paint()
    ellipse(ctx, 200 + ox * 0.3, 1000, 600, 220, R.HILL)
    ellipse(ctx, 1100 + ox * 0.3, 1020, 700, 260, "#B8C9A2")
    drift = NOW[0] * 6
    for cx0, cy0, cw in ((260, 150, 110), (900, 260, 140)):
        cxx = (cx0 + drift) % 1500 - 200
        ellipse(ctx, cxx, cy0, cw, cw * 0.36, "#FFFFFF", 0.7)
        ellipse(ctx, cxx + cw * 0.4, cy0 - cw * 0.18, cw * 0.55, cw * 0.3, "#FFFFFF", 0.7)
    for px in range(-80, 1600, 95):
        xx = px + ox
        rrect(ctx, xx, 860, 60, 300, 10, R.FENCE)
        src(ctx, R.FENCE)
        ctx.move_to(xx, 870)
        ctx.line_to(xx + 30, 830)
        ctx.line_to(xx + 60, 870)
        ctx.fill()
    rrect(ctx, -10 + ox, 930, 1700, 26, 6, R.FENCE_D)
    rrect(ctx, -10 + ox, 1060, 1700, 26, 6, R.FENCE_D)
    for i in range(22):
        fx = i * 75 - 40 + ox + 20 * math.sin(i)
        sway = 4 * math.sin(NOW[0] * 1.1 + i)
        ctx.set_line_width(4)
        src(ctx, "#7F9B62")
        ctx.move_to(fx, 1150)
        ctx.line_to(fx + sway, 1090 - (i % 3) * 18)
        ctx.stroke()
        col = ("#E9B7A6", "#F1D58A", "#C9B6DA")[i % 3]
        for kk in range(5):
            a = kk * 2 * math.pi / 5
            ellipse(ctx, fx + sway + 10 * math.cos(a), 1090 - (i % 3) * 18 + 10 * math.sin(a), 8, 8, col)
        ellipse(ctx, fx + sway, 1090 - (i % 3) * 18, 6, 6, "#E0A44A")
    src(ctx, R.GRASS)
    ctx.rectangle(0, 1130, W, H - 1130)
    ctx.fill()
    for i in range(60):
        gx = (i * 137) % 1600 + ox
        gy = 1200 + (i * 211) % 700
        sway = 3 * math.sin(NOW[0] * 1.5 + i)
        ctx.set_line_width(4)
        src(ctx, "#8FA874", 0.8)
        ctx.move_to(gx - 8, gy)
        ctx.line_to(gx - 10 + sway, gy - 22)
        ctx.move_to(gx + 6, gy)
        ctx.line_to(gx + 9 + sway, gy - 18)
        ctx.stroke()
    t0 = NOW[0]
    R.butterfly(ctx, 120 + 40 * math.sin(t0 * 0.35), 110 + 25 * math.sin(t0 * 0.6), 1.0, "#E9B7A6", 0.0)
    R.butterfly(ctx, 960 + 40 * math.cos(t0 * 0.3), 90 + 20 * math.sin(t0 * 0.7 + 1), 0.9, "#C9B6DA", 1.0)


def room(ctx):
    """Table-top room; the dust in the light beam stays on the wall, off the table."""
    _now = NOW[0]
    R.table_top(ctx)            # draws wall, window, clock, shelf, table
    # cover the dust specks that drift over the table with the table colour band
    g = cairo.LinearGradient(0, 640, 0, H)
    g.add_color_stop_rgb(0, *R.rgb(R.WOOD))
    g.add_color_stop_rgb(1, *R.rgb(R.WOOD_D))
    ctx.set_source(g)
    ctx.rectangle(0, 660, W, H - 660)
    ctx.fill()
    ctx.set_line_width(3)
    for i, yy in enumerate(range(700, H, 90)):
        src(ctx, "#A97F5B", 0.25)
        ctx.move_to(0, yy + 10 * math.sin(i))
        ctx.curve_to(W * 0.3, yy - 12, W * 0.6, yy + 14, W, yy + 4 * math.cos(i))
        ctx.stroke()
    src(ctx, "#FFF8E6", 0.10)   # light beam continues softly on the table
    ctx.move_to(250, 660)
    ctx.line_to(560, 660)
    ctx.line_to(900, 1300)
    ctx.line_to(300, 1300)
    ctx.close_path()
    ctx.fill()


def kite_tail(ctx, x, y, t, length, width):
    pts = [(x + 0.06 * length * math.sin(f * 2 * math.pi + t * 1.6) * f, y + length * f)
           for f in (i / 40 for i in range(41))]
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(width)
    src(ctx, RIBBON)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.stroke()
    for kk in (14, 28):
        bx, by = pts[kk]
        ellipse(ctx, bx - width * 0.7, by, width * 0.65, width * 0.38, RIBBON_D)
        ellipse(ctx, bx + width * 0.7, by, width * 0.65, width * 0.38, RIBBON_D)
    return pts[-1]


# ---------------------------------------------------------------- wide garden (hook, kites)
KW = 19.0                      # px per cm
WIDE_SQ = sq_s(KW)             # 1.6
WIDE_BR = br_s(KW, 1.05)       # Bramble a little nearer the camera
KITE_S = 14 * KW / 140         # kite drawing is 140*s tall -> 14 cm
KITES_X = (350, 730)
KITE_Y = 520
TAIL_W = 1.0 * KW              # ribbon 1 cm wide
IVY_X, OTTO_X, SQ_Y = 175, 905, 1760
BR_X, BR_Y = 465, 1870


def wide_scene(ctx, t, tails, glass_on=True, guides=0.0):
    garden(ctx, -220)
    ky = KITE_Y + 8 * math.sin(t * 0.9)
    sway = 0.04 * math.sin(t * 0.7)
    ends = []
    for (kx, col, sw), ln in zip(((KITES_X[0], "#E7B98C", sway), (KITES_X[1], "#B9C9DE", -sway)), tails):
        bx, by = kx - 80 * KITE_S * math.sin(sw), ky + 80 * KITE_S * math.cos(sw)
        ends.append((bx, by, kite_tail(ctx, bx, by, t, ln, TAIL_W)))
        R.kite(ctx, kx, ky, KITE_S, col, sw, tail=False)
    if guides > 0:
        top = ends[0][1]
        bot = top + tails[0]
        ctx.set_dash([14, 12])
        ctx.set_line_width(4)
        src(ctx, "#6E8460", guides)
        for yy in (top, bot):
            ctx.move_to(KITES_X[0] - 90, yy)
            ctx.line_to(KITES_X[1] + 90, yy)
        ctx.stroke()
        ctx.set_dash([])
    ax, ay = R.squirrel(ctx, IVY_X, SQ_Y, WIDE_SQ, SAGE, f=1, arm_up=1.0, arm_out=1.0, seed=0.7)
    bx2, by2 = R.squirrel(ctx, OTTO_X, SQ_Y, WIDE_SQ, OCHRE, f=-1, arm_up=1.0, arm_out=1.0, seed=2.0)
    ctx.set_line_width(2.5)
    src(ctx, "#7A6E62", 0.8)
    ctx.move_to(ax, ay)
    ctx.line_to(KITES_X[0], ky)
    ctx.move_to(bx2, by2)
    ctx.line_to(KITES_X[1], ky)
    ctx.stroke()
    R.bramble(ctx, BR_X, BR_Y, WIDE_BR, 1, glass=glass_on, look=1.0)
    return ends


def scene_open(ctx, t):
    """Frame 1: one tail long (12 cm), one short (8 cm). Only the question is written."""
    wide_scene(ctx, t, (12 * KW, 8 * KW))
    rrect(ctx, 340, 120, 400, 170, 40, "#FFFFFF", 0.92)
    text(ctx, "Half?", W / 2, 205, 110, INK)


def scene_loop(ctx, t):
    keep = NOW[0]
    NOW[0] = v6.IDLE0
    scene_open(ctx, 0.0)
    NOW[0] = keep


def scene_kites(ctx, t, t_text=1.8):
    """Both tails now 10 cm: equal halves."""
    lift = prog(t, 0.2, 2.5)
    ga = prog(t, t_text + 1.0, t_text + 1.8)
    wide_scene(ctx, t, (10 * KW, 10 * KW), guides=ga)
    a = prog(t, t_text, t_text + 1.0)
    if a > 0:   # 1/2 and 1/2 as symbols only (no extra words)
        rrect(ctx, 280, 110, 520, 230, 50, "#FFFFFF", 0.8 * a)
        R.fraction(ctx, 430, 225, 80, a)
        R.fraction(ctx, 650, 225, 80, a)
        sparkles(ctx, W / 2, 225, 300, a * prog(t, t_text + 3.4, t_text + 4.2), 1.1)


# ---------------------------------------------------------------- cookie (today's case)
KC = 25.0
C_SQ = sq_s(KC)                # 2.4
COOKIE_R = 4 * KC              # 8 cm cookie
C_IVY_X, C_OTTO_X, C_SQ_Y = 190, 890, 1900
HALF_L, HALF_R, HALF_Y = (430, 1260), (650, 1260), 1260


def cookie_half(ctx, cx, cy, r, side, a=1.0):
    ctx.save()
    if side < 0:
        ctx.rectangle(cx - r - 4, cy - r - 4, r + 4, 2 * r + 8)
    else:
        ctx.rectangle(cx, cy - r - 4, r + 4, 2 * r + 8)
    ctx.clip()
    ellipse(ctx, cx, cy, r, r, "#C98E52", a)
    ellipse(ctx, cx, cy, r * 0.9, r * 0.9, "#DDA867", a)
    for dx, dy, s in ((-0.45, -0.3, 0.09), (0.35, -0.45, 0.08), (-0.2, 0.35, 0.1), (0.5, 0.2, 0.08),
                      (-0.6, 0.15, 0.07), (0.1, -0.05, 0.08), (0.25, 0.6, 0.07), (-0.35, 0.65, 0.06)):
        ellipse(ctx, cx + dx * r, cy + dy * r, s * r, s * r * 0.85, "#5E4636", a)
    ctx.restore()


def scene_ctx(ctx, t):
    room(ctx)
    a_title = prog(t, 0.1, 0.7)
    rrect(ctx, 120, 150, 840, 250, 44, "#FFFFFF", 0.93 * a_title)
    rrect(ctx, 160, 190, 70, 54, 8, OCHRE, a_title)
    rrect(ctx, 160, 180, 32, 16, 5, OCHRE, a_title)
    text(ctx, "Today's case", 560, 218, 46, "#9C7429", a_title)
    text(ctx, "What is a half?", W / 2, 326, 84, INK, a_title)
    split = prog(t, 3.4, 4.6)
    share = prog(t, 6.8, 8.6)
    cx, cy, r = W / 2, 930, COOKIE_R
    gap = 40 * split
    lx = lerp(cx - gap, HALF_L[0] + r / 2, share)
    rx = lerp(cx + gap, HALF_R[0] - r / 2, share)
    yy = lerp(cy, HALF_Y, share)
    cookie_half(ctx, lx, yy, r, -1)
    cookie_half(ctx, rx, yy, r, +1)
    dash_a = prog(t, 2.9, 3.4) * (1 - split)
    if dash_a > 0:
        ctx.set_dash([14, 12])
        ctx.set_line_width(6)
        src(ctx, "#FFFFFF", dash_a)
        ctx.move_to(cx, cy - r - 16)
        ctx.line_to(cx, cy + r + 16)
        ctx.stroke()
        ctx.set_dash([])
    la = prog(t, 4.6, 5.3)
    if la > 0:
        for x0, sgn in ((lx, -1), (rx, 1)):
            rrect(ctx, x0 + sgn * r * 0.5 - 34, yy - 46, 68, 92, 18, "#FFFFFF", 0.9 * la)
            R.fraction(ctx, x0 + sgn * r * 0.5, yy, 36, la)
        text(ctx, "same size", cx, cy - r - 60, 50, "#6E8460", la * (1 - share))
    sq = prog(t, 6.4, 7.4)
    if sq > 0:
        R.squirrel(ctx, C_IVY_X, lerp(2450, C_SQ_Y, sq), C_SQ, SAGE, f=1, seed=0.7)
        R.squirrel(ctx, C_OTTO_X, lerp(2450, C_SQ_Y, sq), C_SQ, OCHRE, f=-1, seed=2.0)


# ---------------------------------------------------------------- garden bench (b, c, d)
KB = 26.0
B_SQ = sq_s(KB)                       # 2.5
B_BR = br_s(KB, 1.05)                 # Bramble nearer, in front of the bench
RIB_L, RIB_R, RIB_Y = 280, 280 + 20 * KB, 1236     # ribbon 20 cm on the bench top
RIB_MID = (RIB_L + RIB_R) / 2
RIB_MARK = RIB_L + 12 * KB            # Otto's mark at 12 cm
B_IVY_X, B_OTTO_X, B_GROUND = 120, 960, 1500
SCISSORS_S = 9 * KB / 92              # scissors drawing is ~92*s long -> 9 cm


def bench(ctx):
    rrect(ctx, 220, 1250, 640, 30, 8, "#B8875E")          # top
    rrect(ctx, 236, 1278, 608, 150, 6, "#A97F5B")          # front apron
    rrect(ctx, 250, 1420, 34, 90, 6, "#8E6A48")
    rrect(ctx, 796, 1420, 34, 90, 6, "#8E6A48")
    R.ellipse(ctx, 540, 1512, 330, 18, "#000000", 0.08)


def bench_kites(ctx, t):
    """The two kites lean against the fence behind the bench (no tails yet)."""
    s = 14 * KB / 140 * 0.62           # 14 cm kites, farther back
    R.kite(ctx, 330, 1000 + 4 * math.sin(t * 0.8), s, "#E7B98C", 0.08, tail=False)
    R.kite(ctx, 750, 1000 + 4 * math.sin(t * 0.8 + 1), s, "#B9C9DE", -0.08, tail=False)


def bench_people(ctx, t):
    """Ivy at the left end of the bench, Otto at the right end with his scissors."""
    rig = R._rig
    PO = rig.POSE.get("O", {})
    R.squirrel(ctx, B_IVY_X, B_GROUND, B_SQ, SAGE, f=1, arm_up=0.2, arm_out=0.4, seed=0.7)
    pointing = PO.get("point") and PO.get("amt", 0) > 0.05
    if pointing:
        rig.POSE["O"] = dict(PO, closed=True)
    ax2, ay2 = R.squirrel(ctx, B_OTTO_X, B_GROUND, B_SQ, OCHRE, f=-1, arm_up=0.3, arm_out=0.8, seed=2.0)
    if pointing:
        px, py = PO["point"]
        rot = math.atan2(py - ay2, px - ax2)
        opn = 0.12
    else:
        rot = math.pi + 0.5
        opn = 0.25
    if not PO.get("scratch"):
        R.scissors(ctx, ax2, ay2, SCISSORS_S, opn, rot=rot)


def bench_base(ctx, t, ribbon_fn=None):
    garden(ctx, -160)
    bench_kites(ctx, t)
    bench(ctx)
    if ribbon_fn:
        ribbon_fn()
    else:
        R.ribbon(ctx, RIB_L, RIB_R, RIB_Y, th=KB * 1.0)
        R.pencil_mark(ctx, RIB_MARK, RIB_Y - 4)
    bench_people(ctx, t)


def scene_b(ctx, t):
    bench_base(ctx, t)


def scene_c(ctx, t):
    sp = prog(t, 0.8, 2.0)
    gap, lift = 14 * sp, 22 * sp

    def rib():
        a_ghost = 1.0 - 0.35 * sp
        R.ribbon(ctx, RIB_L, RIB_MARK - gap, RIB_Y - lift, th=KB, a=a_ghost)
        R.ribbon(ctx, RIB_MARK + gap, RIB_R, RIB_Y - lift, th=KB, a=a_ghost)
        if sp < 0.5:
            R.pencil_mark(ctx, RIB_MARK, RIB_Y - 4)
        a = prog(t, 2.2, 3.2)
        if a > 0:
            for x1, x2, col in ((RIB_L, RIB_MARK, SAGE), (RIB_MARK, RIB_R, OCHRE)):
                ctx.set_line_width(7)
                ctx.set_line_cap(cairo.LINE_CAP_ROUND)
                src(ctx, col, a)
                ctx.move_to(x1 + 6, RIB_Y - lift - 40)
                ctx.line_to(x1 + 6, RIB_Y - lift - 62)
                ctx.line_to(x2 - 6, RIB_Y - lift - 62)
                ctx.line_to(x2 - 6, RIB_Y - lift - 40)
                ctx.stroke()
    bench_base(ctx, t, rib)


def scene_d(ctx, t):
    """Bramble walks in (in front of the bench, below it); the A or B cards sit in the sky."""
    bench_base(ctx, t)
    walk = prog(t, 0.0, 3.0)
    bx = lerp(-260, 420, walk)
    R.bramble(ctx, bx, 1860, B_BR, 1, glass=False, look=1.0, step=t * 11 if walk < 1 else None)
    a = prog(t, 2.7, 3.3) * (1 - prog(t, 6.4, 7.0))
    v6.ab_cards(ctx, a)
    if a > 0:
        cx, cy = W / 2, 740
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


# ---------------------------------------------------------------- table close-ups (e, f, g)
KT = 30.0
L, R_, M = 240, 240 + 20 * KT, 240 + 10 * KT       # 20 cm ribbon; true middle at 10 cm
MARK = L + 12 * KT                                  # Otto's mark at 12 cm
RY = 970
T_BR = br_s(KT, 1.05)                               # ~2.9
T_SQ = sq_s(KT)                                     # ~2.9
T_BR_X, T_BR_Y = 790, 1880
T_OT_X, T_OT_Y = 190, 1890
RTH = 1.2 * KT                                      # ribbon about 1.2 cm wide


def closeup_people(ctx, t, otto=True, otto_kw=None):
    R.bramble(ctx, T_BR_X, T_BR_Y, T_BR, -1, glass=False, look=1.0)
    if otto:
        kw = dict(f=1, seed=2.0)
        kw.update(otto_kw or {})
        R.squirrel(ctx, T_OT_X, T_OT_Y - kw.pop("hop", 0.0), T_SQ, OCHRE, **kw)


def scene_e(ctx, t, t_fold=0.6, t_ends=3.8, t_mid=9.0):
    room(ctx)
    p = prog(t, t_fold, t_fold + 3.4)
    k = math.cos(p * math.pi)
    lift = -40 * math.sin(p * math.pi) - 12 * p
    R.ribbon(ctx, L, M, RY, th=RTH)
    rx2 = M + k * (R_ - M)
    col = RIBBON if k >= 0 else "#6E90AC"
    R.ribbon(ctx, min(M, rx2), max(M, rx2), RY + lift, th=RTH, color=col)
    mk = M + k * (MARK - M)
    if k > -0.98:
        R.pencil_mark(ctx, mk, RY + lift - 6, a=clamp(abs(k) * 1.2))
    a_end = prog(t, t_ends, t_ends + 0.8) * (1 - prog(t, t_mid, t_mid + 1))
    glow(ctx, L, RY, 80, SAGE, a_end)
    a_mid = prog(t, t_mid, t_mid + 1.2)
    glow(ctx, M, RY, 90, OCHRE, a_mid)
    if a_mid > 0:   # small pointer under the fold (no extra word)
        src(ctx, "#9C7429", a_mid)
        ctx.move_to(M, RY + 60)
        ctx.line_to(M - 20, RY + 94)
        ctx.line_to(M + 20, RY + 94)
        ctx.close_path()
        ctx.fill()
    sparkles(ctx, M, RY, 110, a_mid * (1 - prog(t, t_mid + 3.0, t_mid + 4.0)))
    closeup_people(ctx, t)


def scene_f(ctx, t):
    room(ctx)
    R.ribbon(ctx, L, R_, RY, th=RTH)
    src(ctx, "#5F7F99", 0.9)
    ctx.set_line_width(4)
    ctx.move_to(M, RY - RTH / 2)
    ctx.line_to(M, RY + RTH / 2)
    ctx.stroke()
    R.pencil_mark(ctx, MARK, RY - 6)
    glow(ctx, (M + MARK) / 2, RY, 110, "#E8D59A", prog(t, 0.2, 1.2))
    closeup_people(ctx, t, otto_kw=dict(tilt=-0.1 * prog(t, 3.5, 4.0)))
    pick = prog(t, 2.6, 3.2)
    a = prog(t, 2.4, 2.9) * (1 - prog(t, 4.6, 5.2))
    if a > 0:   # small A/B cards on the wall, clear of the ribbon
        ctx.save()
        ctx.translate(W / 2, 300)
        ctx.scale(0.62, 0.62)
        ctx.translate(-W / 2, -300)
        v6.ab_cards(ctx, a, picked=pick)
        ctx.restore()


def ruler(ctx, x, y, length, a):
    rrect(ctx, x - 14, y, length + 28, 50, 8, "#EAD9A8", a)
    ctx.set_line_width(3)
    for cm in range(11):
        xx = x + length * cm / 10
        tall = 22 if cm in (0, 5, 10) else 13
        src(ctx, INK, a)
        ctx.move_to(xx, y)
        ctx.line_to(xx, y + tall)
        ctx.stroke()
    text(ctx, "0", x, y + 38, 22, INK, a)
    text(ctx, "10", x + length, y + 38, 22, INK, a)


PIECE_Y = (RY - 120, RY + 110)


def scene_g(ctx, t, t_cut=0.4, t_lay=2.0, t_same=7.6):
    room(ctx)
    hop = 60 * math.sin(math.pi * clamp((t - t_same - 0.3) / 0.9)) if t_same + 0.3 < t < t_same + 1.2 else 0
    cut = prog(t, t_cut + 0.6, t_cut + 1.6)
    gap = 24 * cut
    lift = prog(t, t_lay, t_lay + 1.0)
    slide = prog(t, t_lay + 1.0, t_lay + 2.4)
    piece = M - L
    ax1, ay1 = L, lerp(RY, PIECE_Y[0], lift)
    ax2, ay2 = lerp(M + gap, L, slide), lerp(RY, PIECE_Y[1], lift)
    R.ribbon(ctx, ax1, ax1 + piece, ay1, th=RTH)
    R.ribbon(ctx, ax2, ax2 + piece, ay2, th=RTH)
    ra = prog(t, t_lay + 2.4, t_lay + 3.1)
    if ra > 0:
        for ry0 in PIECE_Y:
            ruler(ctx, L, ry0 + RTH / 2 + 8, piece, ra)
    sa = prog(t, t_cut - 0.2, t_cut + 0.5) * (1 - prog(t, t_cut + 1.8, t_cut + 2.4))
    if sa > 0:   # 9 cm scissors come in from the right, above the ribbon line
        sx = lerp(W + 150, M + 70 * 9 * KT / 92, prog(t, t_cut - 0.2, t_cut + 0.5))
        op = 0.6 if t < t_cut + 0.9 else 0.05
        ctx.push_group()
        R.scissors(ctx, sx, RY, 9 * KT / 92, op, rot=math.pi)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(sa)
    if slide >= 1.0:
        ga = prog(t, t_same - 0.8, t_same)
        for xx in (L, L + piece):
            ctx.set_dash([14, 12])
            ctx.set_line_width(4)
            src(ctx, "#6E8460", ga)
            ctx.move_to(xx, PIECE_Y[0] - 50)
            ctx.line_to(xx, PIECE_Y[1] + 90)
            ctx.stroke()
        ctx.set_dash([])
        sl = prog(t, t_same - 2.4, t_same - 0.4)
        if 0 < sl < 1:
            glow(ctx, lerp(L, L + piece, sl), (PIECE_Y[0] + PIECE_Y[1]) / 2, 80, "#E8D59A", 1.0)
        a = prog(t, t_same, t_same + 0.8)
        sparkles(ctx, L + piece / 2, (PIECE_Y[0] + PIECE_Y[1]) / 2, 260, a, 0.4)
    closeup_people(ctx, t, otto_kw=dict(hop=hop, tilt=0.12 * prog(t, t_same, t_same + 0.6)))


# ---------------------------------------------------------------- recap
ROW_Y = (330, 630, 930)


def scene_recap(ctx, t):
    import v7
    room(ctx)
    src(ctx, R.CREAM)                 # plain wall behind the cards (no window or clock to overlap)
    ctx.rectangle(0, 0, W, 620)
    ctx.fill()
    for i in range(0, W, 90):
        for j in range(40, 620, 90):
            ellipse(ctx, i + (j // 90 % 2) * 45, j, 5, 5, "#E6DAC4")
    a0 = prog(t, 0.0, 0.6)
    rrect(ctx, 300, 150, 480, 130, 50, OCHRE, a0)
    text(ctx, "Remember", W / 2, 215, 70, "#FFFFFF", a0)
    v7.recap_row(ctx, ROW_Y[0], prog(t, 0.3, 0.9), v7.icon_equal, ["Half means", "2 equal parts"])
    v7.recap_row(ctx, ROW_Y[1], prog(t, 3.3, 3.9), v7.icon_fold, ["Fold end to end", "to find the middle"])
    v7.recap_row(ctx, ROW_Y[2], prog(t, 7.0, 7.6), v7.icon_home, ["Try it at home:", "string or paper"])
    R.bramble(ctx, 560, 1860, 2.9, -1, glass=False, look=0.5)


# ---------------------------------------------------------------- teaser
def scene_i(ctx, t):
    g = cairo.LinearGradient(0, 0, 0, 1000)
    g.add_color_stop_rgb(0, *R.rgb(R.SKY_T))
    g.add_color_stop_rgb(1, *R.rgb(R.SKY_B))
    ctx.set_source(g)
    ctx.paint()
    ellipse(ctx, 540, 900, 900, 260, R.HILL)
    px, py, ps = 200, 420, 680                # a 60 cm square herb patch, farther away
    ctx.save()
    ctx.translate(px + ps / 2, py + ps / 2)
    ctx.scale(1.0, 0.62)
    ctx.translate(-(px + ps / 2), -(py + ps / 2))
    rrect(ctx, px, py, ps, ps, 18, R.SOIL)
    for i in range(6):
        for j in range(6):
            ellipse(ctx, px + 60 + i * 112, py + 60 + j * 112, 20, 15, R.LEAF)
    ctx.set_line_width(5)
    src(ctx, "#F5EFE2")
    ctx.move_to(px + ps / 2, py)
    ctx.line_to(px + ps / 2, py + ps)
    ctx.move_to(px, py + ps * 0.38)
    ctx.line_to(px + ps, py + ps * 0.38)
    ctx.stroke()
    ctx.restore()
    # Pip (8 cm field mouse) at the patch edge, sized to the 60 cm patch
    R.mouse(ctx, 800 + 20 * prog(t, 0.5, 3.0), 1000, 0.85, f=-1)
    for xx in range(-40, W + 100, 95):        # low garden edging
        rrect(ctx, xx, 1130, 60, 260, 10, R.FENCE)
        src(ctx, R.FENCE)
        ctx.move_to(xx, 1140)
        ctx.line_to(xx + 30, 1100)
        ctx.line_to(xx + 60, 1140)
        ctx.fill()
    rrect(ctx, -10, 1190, W + 20, 26, 6, R.FENCE_D)
    rrect(ctx, -10, 1320, W + 20, 26, 6, R.FENCE_D)
    src(ctx, R.GRASS)
    ctx.rectangle(0, 1390, W, H - 1390)
    ctx.fill()
    turn = prog(t, 0.0, 1.5)
    R.bramble(ctx, lerp(380, 420, turn), 1800, 2.6, 1)
