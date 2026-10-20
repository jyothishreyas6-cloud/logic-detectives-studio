"""Short 1 v14 scene changes on top of scenes13.

- Frame is shown shifted up by SHIFT px so the read-along caption strip has the bottom band;
  top cards move down to stay in view.
- Today's case uses an Australian lamington (about 5.5 cm cube) instead of a cookie.
- No extra on-screen words that the caption strip already shows ("same size" removed).
"""
import math

import cairo

import render as R
import v6
import scenes13 as S
from render import W, INK, OCHRE, SAGE, ellipse, rrect, text, src, prog, lerp, sparkles, NOW

SHIFT = 190          # scene px hidden at the top; the bottom 190 px hold the caption strip
TOP = SHIFT + 12     # first scene y that is visible


def scene_open(ctx, t):
    S.wide_scene(ctx, t, (12 * S.KW, 8 * S.KW))
    rrect(ctx, 360, TOP + 6, 360, 150, 40, "#FFFFFF", 0.92)
    text(ctx, "Half?", W / 2, TOP + 82, 100, INK)


def scene_loop(ctx, t):
    keep = NOW[0]
    NOW[0] = v6.IDLE0
    scene_open(ctx, 0.0)
    NOW[0] = keep


def scene_kites(ctx, t, t_text=1.8):
    ga = prog(t, t_text + 1.0, t_text + 1.8)
    S.wide_scene(ctx, t, (10 * S.KW, 10 * S.KW), guides=ga)
    a = prog(t, t_text, t_text + 1.0)
    if a > 0:
        rrect(ctx, 330, TOP + 4, 420, 180, 46, "#FFFFFF", 0.8 * a)
        R.fraction(ctx, 460, TOP + 94, 66, a)
        R.fraction(ctx, 620, TOP + 94, 66, a)


# ---------------------------------------------------------------- lamington
LAM = 5.5 * S.KC          # 5.5 cm lamington at the cookie scene scale
CHOC, CHOC_D, COCO, CREAMF = "#7A4B32", "#5E3826", "#F6EFE6", "#F3E3C8"


def lam_block(ctx, x, y, w, h, d, a=1.0, cut_side=0):
    """A lamington block: front face (x..x+w, y-h..y), top face going back by d.
    cut_side -1/+1 shows the cut face (sponge and jam) on that side."""
    # top face
    ctx.move_to(x, y - h)
    ctx.line_to(x + d * 0.6, y - h - d * 0.5)
    ctx.line_to(x + w + d * 0.6, y - h - d * 0.5)
    ctx.line_to(x + w, y - h)
    ctx.close_path()
    src(ctx, CHOC, a)
    ctx.fill()
    # right side face
    ctx.move_to(x + w, y - h)
    ctx.line_to(x + w + d * 0.6, y - h - d * 0.5)
    ctx.line_to(x + w + d * 0.6, y - d * 0.5)
    ctx.line_to(x + w, y)
    ctx.close_path()
    src(ctx, CHOC_D, a)
    ctx.fill()
    # front face
    if cut_side:
        rrect(ctx, x, y - h, w, h, 3, "#E9CF9E", a)          # sponge
        rrect(ctx, x, y - h * 0.55, w, h * 0.1, 2, "#C0504D", a)   # jam
        ctx.set_line_width(h * 0.08)
        src(ctx, CHOC, a)
        ctx.rectangle(x, y - h, w, h)
        ctx.stroke()
    else:
        g = cairo.LinearGradient(x, 0, x + w, 0)
        g.add_color_stop_rgba(0, *R.rgb("#8A573B"), a)
        g.add_color_stop_rgba(1, *R.rgb(CHOC), a)
        ctx.set_source(g)
        ctx.rectangle(x, y - h, w, h)
        ctx.fill()
    # coconut flecks
    for i in range(int(w * h / 260)):
        fx = x + (i * 37) % max(1, int(w))
        fy = y - h + (i * 53) % max(1, int(h))
        if cut_side and (y - h * 0.9 < fy < y - h * 0.1) and (x + w * 0.1 < fx < x + w * 0.9):
            continue
        ellipse(ctx, fx, fy, 2.6, 1.8, COCO, 0.9 * a)
    for i in range(int(w * d / 300)):
        fx = x + (i * 41) % max(1, int(w)) + d * 0.3
        fy = y - h - d * 0.25 + ((i * 29) % 9) - 4
        ellipse(ctx, fx, fy, 2.6, 1.8, COCO, 0.9 * a)


def scene_ctx(ctx, t):
    S.room(ctx)
    a_title = prog(t, 0.1, 0.7)
    y0 = TOP + 10
    rrect(ctx, 120, y0, 840, 240, 44, "#FFFFFF", 0.93 * a_title)
    rrect(ctx, 160, y0 + 40, 70, 54, 8, OCHRE, a_title)
    rrect(ctx, 160, y0 + 30, 32, 16, 5, OCHRE, a_title)
    text(ctx, "Today's case", 560, y0 + 68, 46, "#9C7429", a_title)
    text(ctx, "What is a half?", W / 2, y0 + 172, 84, INK, a_title)
    split = prog(t, 3.4, 4.6)
    share = prog(t, 6.8, 8.6)
    w, h, d = LAM, LAM, LAM * 0.55
    cx, base = W / 2, 1010
    gap = 26 * split
    lx = lerp(cx - w / 2 - gap, S.HALF_L[0] - w / 2 + 20, share)
    rx = lerp(cx + gap, S.HALF_R[0] - 20, share)
    yy = lerp(base, S.HALF_Y + h / 2, share)
    lam_block(ctx, lx, yy, w / 2, h, d, cut_side=1 if split > 0.3 else 0)
    lam_block(ctx, rx, yy, w / 2, h, d, cut_side=-1 if split > 0.3 else 0)
    dash_a = prog(t, 2.9, 3.4) * (1 - split)
    if dash_a > 0:
        ctx.set_dash([12, 10])
        ctx.set_line_width(5)
        src(ctx, "#FFFFFF", dash_a)
        ctx.move_to(cx, base - h - d * 0.5 - 14)
        ctx.line_to(cx, base + 14)
        ctx.stroke()
        ctx.set_dash([])
    la = prog(t, 4.6, 5.3)
    if la > 0:
        for x0 in (lx + w / 4, rx + w / 4):
            rrect(ctx, x0 - 38, yy - h - d * 0.5 - 124, 76, 108, 18, "#FFFFFF", 0.9 * la)
            R.fraction(ctx, x0, yy - h - d * 0.5 - 70, 42, la)
        sparkles(ctx, cx, yy - h / 2, w + 40, la * (1 - prog(t, 6.0, 6.8)), 0.2)
    sq = prog(t, 6.4, 7.4)
    if sq > 0:
        R.squirrel(ctx, S.C_IVY_X, lerp(2450, S.C_SQ_Y, sq), S.C_SQ, SAGE, f=1, seed=0.7)
        R.squirrel(ctx, S.C_OTTO_X, lerp(2450, S.C_SQ_Y, sq), S.C_SQ, OCHRE, f=-1, seed=2.0)


def scene_recap(ctx, t):
    import v7
    S.room(ctx)
    src(ctx, R.CREAM)
    ctx.rectangle(0, 0, W, 620)
    ctx.fill()
    for i in range(0, W, 90):
        for j in range(40, 620, 90):
            ellipse(ctx, i + (j // 90 % 2) * 45, j, 5, 5, "#E6DAC4")
    a0 = prog(t, 0.0, 0.6)
    rrect(ctx, 300, TOP + 6, 480, 120, 50, OCHRE, a0)
    text(ctx, "Remember", W / 2, TOP + 66, 66, "#FFFFFF", a0)
    rows = (TOP + 160, TOP + 440, TOP + 720)
    v7.recap_row(ctx, rows[0], prog(t, 0.3, 0.9), v7.icon_equal, ["Half means", "2 equal parts"])
    v7.recap_row(ctx, rows[1], prog(t, 3.3, 3.9), v7.icon_fold, ["Fold end to end", "to find the middle"])
    v7.recap_row(ctx, rows[2], prog(t, 7.0, 7.6), v7.icon_home, ["Try it at home:", "string or paper"])
    R.bramble(ctx, 560, 1860, 2.9, -1, glass=False, look=0.5)


RECAP_ROW_MID = (TOP + 160 + 125, TOP + 440 + 125, TOP + 720 + 125)
