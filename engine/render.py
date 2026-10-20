"""Render Short 1 'Is This Really Half?' (Logic Detectives) as a 1080x1920 30fps video.

Usage:
  python3 render.py frames <t1> <t2> ...   -> write PNG stills at those times (for checking)
  python3 render.py video                  -> pipe all frames to ffmpeg, mux with audio.wav
"""
import math
import subprocess
import sys

import cairo

W, H, FPS, TOTAL = 1080, 1920, 30, 77.0
FONT = "Comfortaa"


# ---------- helpers ----------
def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def src(ctx, h, a=1.0):
    r, g, b = rgb(h)
    ctx.set_source_rgba(r, g, b, a)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def prog(t, a, b):
    return ease((t - a) / (b - a))


def lerp(a, b, p):
    return a + (b - a) * p


def ellipse(ctx, cx, cy, rx, ry, color, a=1.0):
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(rx, ry)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    src(ctx, color, a)
    ctx.fill()


def rrect(ctx, x, y, w, h, r, color, a=1.0):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()
    src(ctx, color, a)
    ctx.fill()


def text(ctx, s, x, y, size, color="#4A3F35", a=1.0, bold=True):
    if a <= 0:
        return
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    xb, yb, tw, th, _, _ = ctx.text_extents(s)
    ctx.move_to(x - tw / 2 - xb, y - th / 2 - yb)
    src(ctx, color, a)
    ctx.show_text(s)


NOW = [0.0]  # current video time, for idle motion


def blink(seed=0.0):
    """1.0 = open, ~0.1 = closed. Each character blinks on its own rhythm."""
    period = 3.4 + seed * 0.7
    ph = (NOW[0] + seed * 1.9) % period
    return 0.12 if ph < 0.14 else 1.0


def breathe(seed=0.0):
    return 1.0 + 0.018 * math.sin(NOW[0] * 2.1 + seed)


def shadow(ctx, x, y, w):
    ellipse(ctx, x, y + 2, w, w * 0.16, "#000000", 0.10)


def sparkles(ctx, cx, cy, r, a, seed=0.0):
    """Soft twinkling 4-point stars around a point (slow, never flashing)."""
    if a <= 0:
        return
    for i in range(7):
        ang = i * 2 * math.pi / 7 + seed
        rr = r * (0.75 + 0.25 * math.sin(i * 1.7))
        x, y = cx + rr * math.cos(ang), cy + rr * 0.8 * math.sin(ang)
        tw = 0.55 + 0.45 * math.sin(NOW[0] * 2.4 + i * 1.3)
        sz = (10 + 8 * tw) * (0.8 + 0.2 * (i % 3))
        src(ctx, "#F2D27A", a * (0.45 + 0.55 * tw))
        ctx.move_to(x, y - sz)
        ctx.curve_to(x + sz * 0.15, y - sz * 0.15, x + sz * 0.15, y - sz * 0.15, x + sz, y)
        ctx.curve_to(x + sz * 0.15, y + sz * 0.15, x + sz * 0.15, y + sz * 0.15, x, y + sz)
        ctx.curve_to(x - sz * 0.15, y + sz * 0.15, x - sz * 0.15, y + sz * 0.15, x - sz, y)
        ctx.curve_to(x - sz * 0.15, y - sz * 0.15, x - sz * 0.15, y - sz * 0.15, x, y - sz)
        ctx.fill()


def butterfly(ctx, x, y, s, color, seed=0.0):
    flap = abs(math.sin(NOW[0] * 7 + seed))
    for sgn in (1, -1):
        ellipse(ctx, x + sgn * 14 * s * (0.35 + 0.65 * flap), y - 6 * s, 14 * s * (0.35 + 0.65 * flap), 12 * s, color, 0.9)
        ellipse(ctx, x + sgn * 10 * s * (0.35 + 0.65 * flap), y + 8 * s, 9 * s * (0.35 + 0.65 * flap), 8 * s, color, 0.8)
    ellipse(ctx, x, y, 3 * s, 12 * s, INK)


# ---------- palette ----------
CREAM = "#F3EBDD"
WOOD = "#C9A27E"
WOOD_D = "#B48C68"
RIBBON = "#7A9CB8"
RIBBON_D = "#5F7F99"
SKY_T, SKY_B = "#D5E3EA", "#EEF1E6"
GRASS = "#A9BF8F"
HILL = "#C3D2AE"
FENCE = "#E8DCC6"
FENCE_D = "#D4C4A8"
SPINE = "#8B6A4E"
SPINE_D = "#6F5440"
FACE = "#F2E3C9"
INK = "#3B3029"
SQ = "#B5643C"
SQ_T = "#C77A4E"
BELLY = "#EAD3B5"
OCHRE = "#C9973A"
SAGE = "#9CAF88"
MOUSE = "#A8A29A"
STRAW = "#D9C27A"
SOIL = "#9B7653"
LEAF = "#7F9B62"


# ---------- characters ----------
def bramble(ctx, x, y, s, f=1, glass=True, paw_up=0.0, look=0.0, step=None):
    """Side-view hedgehog. (x, y) = ground point under the body. f = facing (+1 right)."""
    shadow(ctx, x + 20 * s * f, y, 95 * s)
    br = breathe(0.3)
    st = math.sin(step) if step is not None else 0.0
    ellipse(ctx, x - 25 * s * f + 6 * s * st, y - 4 * s - 7 * s * max(0, -st), 16 * s, 7 * s, SPINE_D)
    ellipse(ctx, x + 30 * s * f - 6 * s * st, y - 4 * s - 7 * s * max(0, st), 16 * s, 7 * s, SPINE_D)
    # spines: triangles around the back
    cx, cy, rx, ry = x - 5 * s * f, y - 55 * s * br, 72 * s, 56 * s * br
    src(ctx, SPINE_D)
    for i in range(15):
        ang = math.radians(150 + i * 15) if f > 0 else math.radians(30 - i * 15)
        bx, by = cx + rx * math.cos(ang), cy + ry * math.sin(ang)
        tx, ty = cx + (rx + 20 * s) * math.cos(ang), cy + (ry + 20 * s) * math.sin(ang)
        da = math.radians(9)
        ctx.move_to(cx + rx * math.cos(ang - da), cy + ry * math.sin(ang - da))
        ctx.line_to(tx, ty)
        ctx.line_to(cx + rx * math.cos(ang + da), cy + ry * math.sin(ang + da))
        ctx.close_path()
        ctx.fill()
    ellipse(ctx, cx, cy, rx, ry, SPINE)
    # face + belly
    ellipse(ctx, x + 38 * s * f, y - 42 * s, 42 * s, 36 * s, FACE)
    ellipse(ctx, x + 72 * s * f, y - 52 * s, 30 * s, 22 * s, FACE)
    ellipse(ctx, x + 99 * s * f, y - 56 * s, 8 * s, 7 * s, INK)  # nose
    bl = blink(0.0)
    ex, ey = x + (62 + 2.5 * look) * s * f, y - 70 * s
    ellipse(ctx, ex, ey, 6.5 * s, 7.5 * s * bl, INK)  # eye
    if bl > 0.5:
        ellipse(ctx, ex + 2 * s * f, ey - 2.5 * s, 2.2 * s, 2.2 * s, "#FFFFFF")
    ellipse(ctx, x + 40 * s * f, y - 56 * s, 9 * s, 6 * s, "#E8C2A8", 0.6)  # cheek
    ctx.set_line_width(2.6 * s)
    src(ctx, INK)
    ctx.arc(x + 80 * s * f, y - 47 * s, 9 * s, math.radians(30), math.radians(140)) if f > 0 else \
        ctx.arc(x - 80 * s, y - 47 * s, 9 * s, math.radians(40), math.radians(150))
    ctx.stroke()
    # arm + magnifying glass
    if glass:
        hx, hy = x + 70 * s * f, y - 28 * s - paw_up * 40 * s
        gx, gy = x + 118 * s * f, y - 95 * s - paw_up * 40 * s
        ctx.set_line_width(7 * s)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        src(ctx, "#9A7350")
        ctx.move_to(hx, hy)
        ctx.line_to(gx - 14 * s * f, gy + 18 * s)
        ctx.stroke()
        ellipse(ctx, gx, gy, 22 * s, 22 * s, "#DCEAF0", 0.55)
        ctx.set_line_width(5 * s)
        src(ctx, "#9A7350")
        ctx.arc(gx, gy, 22 * s, 0, 2 * math.pi)
        ctx.stroke()
        ellipse(ctx, hx, hy, 9 * s, 8 * s, SPINE_D)
    else:
        ellipse(ctx, x + 66 * s * f, y - 24 * s - paw_up * 30 * s, 10 * s, 8 * s, SPINE_D)


def squirrel(ctx, x, y, s, scarf, f=1, tilt=0.0, arm_up=0.0, arm_out=0.0, seed=0.0):
    """Side-ish view squirrel. (x, y) = feet."""
    shadow(ctx, x, y, 60 * s)
    # tail (gentle swish)
    ctx.save()
    ctx.translate(x - 20 * s * f, y - 30 * s)
    ctx.rotate(0.07 * math.sin(NOW[0] * 1.5 + seed) * f)
    ctx.translate(-(x - 20 * s * f), -(y - 30 * s))
    src(ctx, SQ_T)
    ctx.move_to(x - 30 * s * f, y - 20 * s)
    ctx.curve_to(x - 120 * s * f, y - 40 * s, x - 130 * s * f, y - 190 * s, x - 70 * s * f, y - 230 * s)
    ctx.curve_to(x - 20 * s * f, y - 260 * s, x - 10 * s * f, y - 200 * s, x - 50 * s * f, y - 190 * s)
    ctx.curve_to(x - 80 * s * f, y - 150 * s, x - 60 * s * f, y - 60 * s, x - 10 * s * f, y - 40 * s)
    ctx.close_path()
    ctx.fill()
    ctx.restore()
    ellipse(ctx, x - 12 * s * f, y - 4 * s, 18 * s, 7 * s, SQ)
    ellipse(ctx, x + 18 * s * f, y - 4 * s, 18 * s, 7 * s, SQ)
    ellipse(ctx, x, y - 62 * s, 42 * s, 60 * s * breathe(seed), SQ)
    ellipse(ctx, x + 10 * s * f, y - 54 * s, 24 * s, 40 * s, BELLY)
    # arm
    ax = x + (18 + 30 * arm_out) * s * f
    ay = y - (70 + 45 * arm_up) * s
    ctx.set_line_width(14 * s)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    src(ctx, SQ)
    ctx.move_to(x + 10 * s * f, y - 88 * s)
    ctx.line_to(ax, ay)
    ctx.stroke()
    # head (tilts around neck)
    ctx.save()
    ctx.translate(x + 4 * s * f, y - 118 * s)
    ctx.rotate(tilt * f)
    hx, hy = 0, -32 * s
    src(ctx, SQ)
    for ex in (-18, 14):
        ctx.move_to(hx + (ex - 10) * s * f, hy - 22 * s)
        ctx.line_to(hx + (ex + 2) * s * f, hy - 58 * s)
        ctx.line_to(hx + (ex + 12) * s * f, hy - 20 * s)
        ctx.close_path()
        ctx.fill()
    ellipse(ctx, hx, hy, 38 * s, 34 * s, SQ)
    ellipse(ctx, hx + 26 * s * f, hy + 8 * s, 18 * s, 14 * s, BELLY)
    ellipse(ctx, hx + 41 * s * f, hy + 4 * s, 5 * s, 4.5 * s, INK)
    bl = blink(seed + 0.8)
    ellipse(ctx, hx + 14 * s * f, hy - 8 * s, 5.5 * s, 6.5 * s * bl, INK)
    if bl > 0.5:
        ellipse(ctx, hx + 15.5 * s * f, hy - 10 * s, 1.8 * s, 1.8 * s, "#FFFFFF")
    ctx.restore()
    # scarf
    rrect(ctx, x - 34 * s, y - 122 * s, 70 * s, 18 * s, 8 * s, scarf)
    ctx.save()
    ctx.translate(x - 22 * s * f, y - 110 * s)
    ctx.rotate(0.25 * f)
    rrect(ctx, -8 * s, 0, 16 * s, 38 * s, 6 * s, scarf)
    ctx.restore()
    return ax, ay


def mouse(ctx, x, y, s, f=1):
    ctx.set_line_width(4 * s)
    src(ctx, "#C9A9A0")
    ctx.move_to(x - 30 * s * f, y - 15 * s)
    ctx.curve_to(x - 80 * s * f, y - 10 * s, x - 70 * s * f, y - 60 * s, x - 100 * s * f, y - 50 * s)
    ctx.stroke()
    ellipse(ctx, x, y - 32 * s, 36 * s, 32 * s, MOUSE)
    ellipse(ctx, x + 30 * s * f, y - 52 * s, 24 * s, 20 * s, MOUSE)
    ellipse(ctx, x + 20 * s * f, y - 76 * s, 15 * s, 15 * s, MOUSE)
    ellipse(ctx, x + 20 * s * f, y - 76 * s, 9 * s, 9 * s, "#E3B9B0")
    ellipse(ctx, x + 52 * s * f, y - 50 * s, 4 * s, 4 * s, INK)
    ellipse(ctx, x + 36 * s * f, y - 58 * s, 4 * s, 4.5 * s * blink(2.2), INK)
    # straw hat
    ellipse(ctx, x + 28 * s * f, y - 72 * s, 34 * s, 8 * s, STRAW)
    rrect(ctx, x + 12 * s * f - 6 * s, y - 94 * s, 34 * s, 22 * s, 8 * s, STRAW)
    rrect(ctx, x + 12 * s * f - 6 * s, y - 80 * s, 34 * s, 5 * s, 2 * s, "#B85C4A")


def kite(ctx, x, y, s, color, sway=0.0, tail=True):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(sway)
    src(ctx, color)
    ctx.move_to(0, -60 * s)
    ctx.line_to(42 * s, 0)
    ctx.line_to(0, 80 * s)
    ctx.line_to(-42 * s, 0)
    ctx.close_path()
    ctx.fill()
    ctx.set_line_width(3 * s)
    src(ctx, "#FFFFFF", 0.6)
    ctx.move_to(0, -60 * s)
    ctx.line_to(0, 80 * s)
    ctx.move_to(-42 * s, 0)
    ctx.line_to(42 * s, 0)
    ctx.stroke()
    if tail:
        ctx.set_line_width(9 * s)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        src(ctx, RIBBON)
        ctx.move_to(0, 80 * s)
        ctx.curve_to(25 * s, 130 * s, -25 * s, 170 * s, 8 * s, 220 * s)
        ctx.stroke()
        for k in (0.35, 0.7):
            by = (80 + 140 * k) * s
            ellipse(ctx, -10 * s, by, 9 * s, 5 * s, RIBBON_D)
            ellipse(ctx, 10 * s, by, 9 * s, 5 * s, RIBBON_D)
    ctx.restore()


def ribbon(ctx, x1, x2, y, th=26, color=RIBBON, a=1.0):
    if x2 < x1:
        x1, x2 = x2, x1
    rrect(ctx, x1, y - th / 2, max(x2 - x1, 1), th, min(6, th / 2), color, a)
    rrect(ctx, x1, y + th / 2 - 6, max(x2 - x1, 1), 6, 3, RIBBON_D, 0.5 * a)


def pencil_mark(ctx, x, y, a=1.0):
    ctx.set_line_width(5)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    src(ctx, "#4B4B4B", a)
    ctx.move_to(x, y - 30)
    ctx.line_to(x, y - 12)
    ctx.stroke()


def scissors(ctx, x, y, s, open_=0.3, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    for sgn in (1, -1):
        ctx.save()
        ctx.rotate(sgn * open_ * 0.5)
        src(ctx, "#B9BEC2")
        ctx.move_to(0, 0)
        ctx.line_to(70 * s, -5 * s * sgn)
        ctx.line_to(70 * s, 2 * s * sgn)
        ctx.close_path()
        ctx.fill()
        ctx.set_line_width(7 * s)
        src(ctx, OCHRE)
        ctx.arc(-22 * s, 12 * s * sgn, 13 * s, 0, 2 * math.pi)
        ctx.stroke()
        ctx.restore()
    ctx.restore()


def glow(ctx, x, y, r, color, a):
    if a <= 0:
        return
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    cr, cg, cb = rgb(color)
    g.add_color_stop_rgba(0, cr, cg, cb, 0.0)
    g.add_color_stop_rgba(0.7, cr, cg, cb, 0.25 * a)
    g.add_color_stop_rgba(0.85, cr, cg, cb, 0.55 * a)
    g.add_color_stop_rgba(1.0, cr, cg, cb, 0.0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()


def pointer(ctx, x, y, color, a, label=None):
    if a <= 0:
        return
    src(ctx, color, a)
    ctx.move_to(x, y)
    ctx.line_to(x - 22, y + 36)
    ctx.line_to(x + 22, y + 36)
    ctx.close_path()
    ctx.fill()
    if label:
        text(ctx, label, x, y + 90, 56, color, a)


# ---------- backgrounds ----------
def table_top(ctx):
    src(ctx, CREAM)
    ctx.paint()
    # wallpaper dots
    for i in range(0, W, 90):
        for j in range(40, 620, 90):
            ellipse(ctx, i + (j // 90 % 2) * 45, j, 5, 5, "#E6DAC4")
    # window with drifting cloud
    rrect(ctx, 90, 110, 380, 420, 24, "#B8875E")
    g = cairo.LinearGradient(0, 130, 0, 510)
    g.add_color_stop_rgb(0, *rgb(SKY_T))
    g.add_color_stop_rgb(1, *rgb(SKY_B))
    ctx.set_source(g)
    ctx.rectangle(110, 130, 340, 380)
    ctx.fill()
    cx0 = 110 + (NOW[0] * 12) % 420 - 40
    ctx.save()
    ctx.rectangle(110, 130, 340, 380)
    ctx.clip()
    ellipse(ctx, cx0, 250, 70, 24, "#FFFFFF", 0.85)
    ellipse(ctx, cx0 + 30, 236, 40, 20, "#FFFFFF", 0.85)
    ellipse(ctx, 280, 560, 260, 90, HILL)
    ctx.restore()
    rrect(ctx, 274, 130, 12, 380, 4, "#B8875E")
    rrect(ctx, 110, 314, 340, 12, 4, "#B8875E")
    # soft light beam with floating dust
    src(ctx, "#FFF8E6", 0.18)
    ctx.move_to(110, 510)
    ctx.line_to(450, 510)
    ctx.line_to(900, 1300)
    ctx.line_to(300, 1300)
    ctx.close_path()
    ctx.fill()
    for i in range(16):
        dx = 200 + (i * 53 + NOW[0] * (6 + i % 4)) % 500
        dy = 560 + (i * 97 + NOW[0] * (9 + i % 3)) % 700
        ellipse(ctx, dx + (dy - 560) * 0.35, dy, 3 + i % 3, 3 + i % 3, "#FFFFFF", 0.35)
    # clock with a slowly moving hand
    ellipse(ctx, 800, 230, 96, 96, "#B8875E")
    ellipse(ctx, 800, 230, 82, 82, "#FBF6EC")
    for k in range(12):
        a = k * math.pi / 6
        ellipse(ctx, 800 + 66 * math.cos(a), 230 + 66 * math.sin(a), 4, 4, INK)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(7)
    src(ctx, INK)
    ctx.move_to(800, 230)
    ctx.line_to(800 + 40 * math.cos(-1.2), 230 + 40 * math.sin(-1.2))
    ctx.stroke()
    ctx.set_line_width(4)
    a = -math.pi / 2 + NOW[0] * 2 * math.pi / 60
    src(ctx, "#B85C4A")
    ctx.move_to(800, 230)
    ctx.line_to(800 + 62 * math.cos(a), 230 + 62 * math.sin(a))
    ctx.stroke()
    # shelf with a jar of buttons and a plant
    rrect(ctx, 610, 450, 400, 22, 6, "#B8875E")
    rrect(ctx, 650, 360, 90, 92, 14, "#DCEAF0", 0.8)
    for k, col in enumerate(("#E9B7A6", "#F1D58A", "#9CAF88", "#7A9CB8", "#C9B6DA")):
        ellipse(ctx, 670 + (k % 3) * 25, 425 - (k // 3) * 22, 11, 11, col)
    rrect(ctx, 860, 390, 80, 62, 10, "#C98B6B")
    for k in range(5):
        a = -math.pi / 2 + (k - 2) * 0.45 + 0.05 * math.sin(NOW[0] + k)
        ctx.save()
        ctx.translate(900 + 45 * math.cos(a), 380 + 45 * math.sin(a))
        ctx.rotate(a + math.pi / 2)
        ellipse(ctx, 0, 0, 14, 30, LEAF)
        ctx.restore()
    g = cairo.LinearGradient(0, 640, 0, H)
    g.add_color_stop_rgb(0, *rgb(WOOD))
    g.add_color_stop_rgb(1, *rgb(WOOD_D))
    ctx.set_source(g)
    ctx.rectangle(0, 640, W, H - 640)
    ctx.fill()
    ctx.set_line_width(3)
    for i, yy in enumerate(range(700, H, 90)):
        src(ctx, "#A97F5B", 0.25)
        ctx.move_to(0, yy + 10 * math.sin(i))
        ctx.curve_to(W * 0.3, yy - 12, W * 0.6, yy + 14, W, yy + 4 * math.cos(i))
        ctx.stroke()
    rrect(ctx, 0, 620, W, 40, 0, "#B48C68")


def garden(ctx, ox=0.0):
    g = cairo.LinearGradient(0, 0, 0, 1000)
    g.add_color_stop_rgb(0, *rgb(SKY_T))
    g.add_color_stop_rgb(1, *rgb(SKY_B))
    ctx.set_source(g)
    ctx.paint()
    ellipse(ctx, 200 + ox * 0.3, 1000, 600, 220, HILL)
    ellipse(ctx, 1100 + ox * 0.3, 1020, 700, 260, "#B8C9A2")
    drift = NOW[0] * 9
    for cx0, cy0, cw in ((260, 260, 110), (900, 380, 140), (1500, 200, 120)):
        cxx = (cx0 + ox * 0.2 + drift) % 1700 - 200
        ellipse(ctx, cxx, cy0, cw, cw * 0.36, "#FFFFFF", 0.7)
        ellipse(ctx, cxx + cw * 0.4, cy0 - cw * 0.18, cw * 0.55, cw * 0.3, "#FFFFFF", 0.7)
    # fence
    for px in range(-80, 1600, 95):
        xx = px + ox
        rrect(ctx, xx, 860, 60, 300, 10, FENCE)
        src(ctx, FENCE)
        ctx.move_to(xx, 870)
        ctx.line_to(xx + 30, 830)
        ctx.line_to(xx + 60, 870)
        ctx.fill()
    rrect(ctx, -10 + ox, 930, 1700, 26, 6, FENCE_D)
    rrect(ctx, -10 + ox, 1060, 1700, 26, 6, FENCE_D)
    # birdhouse on a post
    rrect(ctx, 1240 + ox, 760, 90, 100, 10, "#C98B6B")
    src(ctx, "#A86B50")
    ctx.move_to(1225 + ox, 770)
    ctx.line_to(1285 + ox, 715)
    ctx.line_to(1345 + ox, 770)
    ctx.close_path()
    ctx.fill()
    ellipse(ctx, 1285 + ox, 805, 16, 16, "#5E4636")
    # flowers along the fence
    for i in range(22):
        fx = i * 75 - 40 + ox + 20 * math.sin(i)
        sway = 6 * math.sin(NOW[0] * 1.3 + i)
        ctx.set_line_width(4)
        src(ctx, "#7F9B62")
        ctx.move_to(fx, 1150)
        ctx.line_to(fx + sway, 1090 - (i % 3) * 18)
        ctx.stroke()
        col = ("#E9B7A6", "#F1D58A", "#C9B6DA")[i % 3]
        for k in range(5):
            a = k * 2 * math.pi / 5
            ellipse(ctx, fx + sway + 10 * math.cos(a), 1090 - (i % 3) * 18 + 10 * math.sin(a), 8, 8, col)
        ellipse(ctx, fx + sway, 1090 - (i % 3) * 18, 6, 6, "#E0A44A")
    src(ctx, GRASS)
    ctx.rectangle(0, 1130, W, H - 1130)
    ctx.fill()
    for i in range(60):
        gx = (i * 137) % 1600 + ox
        gy = 1200 + (i * 211) % 700
        sway = 4 * math.sin(NOW[0] * 1.8 + i)
        ctx.set_line_width(4)
        src(ctx, "#8FA874", 0.8)
        ctx.move_to(gx - 8, gy)
        ctx.line_to(gx - 10 + sway, gy - 22)
        ctx.move_to(gx + 6, gy)
        ctx.line_to(gx + 9 + sway, gy - 18)
        ctx.stroke()
    t0 = NOW[0]
    for i in range(5):
        lx = (i * 330 + t0 * 22) % 1500 - 150 + ox * 0.5
        ly = (i * 260 + t0 * 45) % 1400 - 100
        ctx.save()
        ctx.translate(lx + 30 * math.sin(t0 * 1.2 + i), ly)
        ctx.rotate(t0 * 0.8 + i)
        ellipse(ctx, 0, 0, 16, 7, ("#C9973A", "#9CAF88", "#C98B6B")[i % 3], 0.85)
        ctx.restore()
    butterfly(ctx, 820 + ox + 120 * math.sin(t0 * 0.35), 620 + 70 * math.sin(t0 * 0.6), 1.3, "#E9B7A6", 0.0)
    butterfly(ctx, 380 + ox + 100 * math.cos(t0 * 0.3), 980 + 50 * math.sin(t0 * 0.7 + 1), 1.1, "#C9B6DA", 1.0)


def garden_table(ctx, ox):
    rrect(ctx, 300 + ox, 1180, 820, 44, 10, "#B8875E")
    rrect(ctx, 340 + ox, 1220, 30, 260, 8, "#A0724C")
    rrect(ctx, 1050 + ox, 1220, 30, 260, 8, "#A0724C")


# ---------- scenes ----------
# Scene A: close-up of ribbon with mark; Bramble rises; "Half?"
def scene_a(ctx, t, loop=False):
    ctx.save()
    z = 1.0 + 0.05 * clamp(t / 3.3) if not loop else 1.0
    ctx.translate(W / 2, 1000)
    ctx.scale(z, z)
    ctx.translate(-W / 2, -1000)
    table_top(ctx)
    ribbon(ctx, 60, 1020, 1000, th=46)
    pencil_mark(ctx, 615, 1000 - 6)
    if not loop:
        rise = prog(t, 0.4, 2.6)
        bramble(ctx, 380, lerp(2550, 1990, rise), 4.4, 1)
    ctx.restore()
    if loop:
        a = prog(t, 0.2, 0.9) * (1 - prog(t, 2.2, 2.8))
    else:
        a = prog(t, 0.3, 1.0)
    rrect(ctx, 340, 720, 400, 170, 40, "#FFFFFF", 0.85 * a)
    text(ctx, "Half?", W / 2, 805, 110, INK, a)


def garden_people(ctx, t, ox, scene):
    """Ivy and Otto behind the table; ribbon on table."""
    # Ivy (left) holds kites up
    tilt = 0.0
    if scene == "c":
        tilt = 0.18 * math.sin(clamp((t - 0.5) / 2.5) * math.pi / 2) - 0.06 * math.sin(t * 0.8)
    kite(ctx, 300 + ox, 640 + 8 * math.sin(t * 0.9), 0.9, "#E7B98C", 0.06 * math.sin(t * 0.7), tail=False)
    kite(ctx, 470 + ox, 600 + 8 * math.sin(t * 0.8 + 1), 0.9, "#B9C9DE", -0.05 * math.sin(t * 0.6), tail=False)
    ax, ay = squirrel(ctx, 400 + ox, 1330, 1.25, SAGE, f=1, tilt=tilt, arm_up=1.0, arm_out=0.1, seed=0.7)
    ctx.set_line_width(2)
    src(ctx, "#7A6E62", 0.8)
    ctx.move_to(ax, ay)
    ctx.line_to(300 + ox, 720)
    ctx.move_to(ax, ay)
    ctx.line_to(470 + ox, 680)
    ctx.stroke()
    # Otto (right) with scissors near the mark
    lowered = prog(t, 0.3, 1.5) if scene == "c" else 0.0
    ax2, ay2 = squirrel(ctx, 1000 + ox, 1330, 1.25, OCHRE, f=-1, arm_up=0.3 - 0.5 * lowered, arm_out=1.0, seed=2.0)
    snip = 0.35 if scene != "b" else 0.15 + 0.3 * abs(math.sin(t * 2.2))
    scissors(ctx, ax2 - 20, ay2 + 10 * lowered, 0.9, snip, rot=math.pi + 0.3 + 0.6 * lowered)


def zoom_table(ctx, z=1.28):
    ctx.translate(W / 2, 1150)
    ctx.scale(z, z)
    ctx.translate(-W / 2, -1150)


def case_badge(ctx, a):
    if a <= 0:
        return
    rrect(ctx, 230, 120, 620, 150, 36, "#FFFFFF", 0.85 * a)
    rrect(ctx, 270, 160, 90, 70, 10, OCHRE, a)
    rrect(ctx, 270, 148, 40, 20, 6, OCHRE, a)
    text(ctx, "Case:", 540, 168, 40, "#9C7429", a)
    text(ctx, "The Kite Ribbon", 590, 225, 50, INK, a)


def scene_b(ctx, t):
    ox = -lerp(40, 160, prog(t, 0.0, 10.0))
    ctx.save()
    zoom_table(ctx)
    garden(ctx, ox)
    garden_people(ctx, t, ox, "b")
    garden_table(ctx, ox)
    ribbon(ctx, 400 + ox, 1020 + ox, 1166, th=22)
    pencil_mark(ctx, 770 + ox, 1166 - 4)
    ctx.restore()
    case_badge(ctx, prog(t, 0.4, 1.2) * (1 - prog(t, 5.6, 6.4)))


def scene_c(ctx, t, t_long):
    ox = -160
    zoom_table(ctx)
    garden(ctx, ox)
    garden_people(ctx, t, ox, "c")
    garden_table(ctx, ox)
    ribbon(ctx, 400 + ox, 1020 + ox, 1166, th=22)
    pencil_mark(ctx, 770 + ox, 1166 - 4)
    # two unequal tails: brackets above the ribbon
    a = prog(t, t_long, t_long + 1.2)
    if a > 0:
        for x1, x2, col, yy in ((400, 770, SAGE, 1080), (770, 1020, OCHRE, 1080)):
            ctx.set_line_width(8)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            src(ctx, col, a)
            ctx.move_to(x1 + ox + 6, yy + 30)
            ctx.line_to(x1 + ox + 6, yy)
            ctx.line_to(x2 + ox - 6, yy)
            ctx.line_to(x2 + ox - 6, yy + 30)
            ctx.stroke()
        text(ctx, "longer", (400 + 770) / 2 + ox, 1030, 46, "#6E8460", a)
        text(ctx, "shorter", (770 + 1020) / 2 + ox, 1030, 46, "#9C7429", a)


def scene_d(ctx, t, t_what):
    ox = -160
    z = 1.28 + 0.3 * prog(t, t_what - 0.6, t_what + 2.5)
    ctx.save()
    cx, cy = W / 2, 1150
    ctx.translate(cx, cy)
    ctx.scale(z, z)
    ctx.translate(-cx, -cy)
    garden(ctx, ox)
    garden_people(ctx, t, ox, "b")
    garden_table(ctx, ox)
    ribbon(ctx, 400 + ox, 1020 + ox, 1166, th=22)
    pencil_mark(ctx, 770 + ox, 1166 - 4)
    walk = prog(t, 0.0, 3.0)
    bx = lerp(-150, 470, walk)
    bob = 8 * abs(math.sin(t * 6)) * (1 - walk) if walk < 1 else 0
    paw = prog(t, 3.2, 4.0)
    bramble(ctx, bx, 1440 - bob, 1.7, 1, glass=False, paw_up=paw * 3.0,
            step=t * 11 if walk < 1 else None)
    if paw > 0.5:
        ellipse(ctx, bx + 112, 1190, 24, 13, SPINE_D, clamp((paw - 0.5) * 2))
    ctx.restore()
    think = prog(t, t_what - 0.1, t_what + 0.6) * (1 - prog(t, t_what + 3.6, t_what + 4.2))
    if think > 0:
        bx0, by0 = 540, 560
        ellipse(ctx, 330, 900, 18, 18, "#FFFFFF", 0.9 * think)
        ellipse(ctx, 390, 820, 28, 28, "#FFFFFF", 0.9 * think)
        ellipse(ctx, bx0, by0, 250, 190, "#FFFFFF", 0.92 * think)
        fill = clamp((t - t_what) / 3.0)
        ctx.set_line_width(16)
        src(ctx, "#E6DAC4", think)
        ctx.arc(bx0, by0 - 10, 100, 0, 2 * math.pi)
        ctx.stroke()
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        src(ctx, SAGE, think)
        ctx.arc(bx0, by0 - 10, 100, -math.pi / 2, -math.pi / 2 + 2 * math.pi * fill)
        ctx.stroke()
        text(ctx, "?", bx0, by0 - 10, 110, INK, think)
        text(ctx, "Pause and think", bx0, by0 + 140, 42, "#6E8460", think)


L, R, M, MARK = 110, 970, 540, 615  # close-up ribbon geometry (true middle M, Otto's mark)
RY = 1000


def paw(ctx, x, y, a=1.0):
    ellipse(ctx, x, y, 34, 26, SPINE_D, a)
    for dx in (-18, 0, 18):
        ellipse(ctx, x + dx, y - 20, 9, 9, "#5E4636", a)


def kb(ctx, t, dur, z1=1.06):
    """slow Ken Burns push-in"""
    z = 1.0 + (z1 - 1.0) * clamp(t / dur)
    ctx.translate(W / 2, 1000)
    ctx.scale(z, z)
    ctx.translate(-W / 2, -1000)


def scene_e(ctx, t, t_fold, t_ends, t_mid):
    kb(ctx, t, 11.6)
    table_top(ctx)
    bramble(ctx, 250, 2010, 3.4, 1, glass=False, look=1.0)
    p = prog(t, t_fold, t_fold + 3.4)
    k = math.cos(p * math.pi)  # 1 -> -1 : right half flips over onto left half
    lift = -46 * math.sin(p * math.pi) - 16 * p
    ribbon(ctx, L, M, RY, th=46)
    rx2 = M + k * (R - M)
    col = RIBBON if k >= 0 else "#6E90AC"
    ribbon(ctx, min(M, rx2), max(M, rx2), RY + lift, th=46, color=col)
    mk = M + k * (MARK - M)
    if k > -0.98:
        pencil_mark(ctx, mk, RY + lift - 6, a=clamp(abs(k) * 1.2))
    paw(ctx, L - 10, RY + 40)
    paw(ctx, rx2 + (12 if k >= 0 else -12), RY + lift + 40)
    a_end = prog(t, t_ends, t_ends + 0.8)
    glow(ctx, L, RY, 90, SAGE, a_end * (1 - prog(t, t_mid, t_mid + 1)))
    text(ctx, "ends together", L + 150, RY - 130, 48, "#6E8460", a_end * (1 - prog(t, t_mid, t_mid + 1)))
    if a_end > 0:  # small arrows showing both ends meeting
        src(ctx, "#6E8460", a_end * (1 - prog(t, t_mid, t_mid + 1)))
        for yy in (RY - 30, RY - 62):
            ctx.move_to(L - 60, yy)
            ctx.line_to(L - 30, yy + 12)
            ctx.line_to(L - 60, yy + 24)
            ctx.close_path()
            ctx.fill()
    a_mid = prog(t, t_mid, t_mid + 1.2)
    glow(ctx, M, RY, 110, OCHRE, a_mid)
    pointer(ctx, M, RY + 90, "#9C7429", a_mid, "fold")
    sparkles(ctx, M, RY, 130, a_mid * (1 - prog(t, t_mid + 3.0, t_mid + 4.0)))


def scene_f(ctx, t, t_look, t_fold, t_mark):
    kb(ctx, t, 8.0, 1.08)
    table_top(ctx)
    bramble(ctx, 220, 2000 - 30 * prog(t, t_look - 0.3, t_look + 0.5), 3.4, 1, glass=True,
            paw_up=0.3, look=1.0)
    ribbon(ctx, L, R, RY, th=46)
    src(ctx, "#5F7F99", 0.9)
    ctx.set_line_width(4)
    ctx.move_to(M, RY - 17)
    ctx.line_to(M, RY + 17)
    ctx.stroke()
    pencil_mark(ctx, MARK, RY - 6)
    glow(ctx, (M + MARK) / 2, RY, 130, "#E8D59A", prog(t, t_look, t_look + 1.0))
    pointer(ctx, M, RY + 60, "#6E8460", prog(t, t_fold, t_fold + 0.8), "fold")
    a = prog(t, t_mark, t_mark + 0.8)
    if a > 0:
        src(ctx, "#9C7429", a)
        ctx.move_to(MARK, RY - 60)
        ctx.line_to(MARK - 22, RY - 96)
        ctx.line_to(MARK + 22, RY - 96)
        ctx.close_path()
        ctx.fill()
        text(ctx, "mark", MARK, RY - 150, 56, "#9C7429", a)


def ruler(ctx, x, y, length, a):
    """Wooden ruler under a piece: 10 cm across `length` pixels."""
    rrect(ctx, x - 14, y, length + 28, 54, 8, "#EAD9A8", a)
    ctx.set_line_width(3)
    for cm in range(11):
        xx = x + length * cm / 10
        tall = 24 if cm in (0, 5, 10) else 14
        src(ctx, INK, a)
        ctx.move_to(xx, y)
        ctx.line_to(xx, y + tall)
        ctx.stroke()
    text(ctx, "0", x, y + 40, 22, INK, a)
    text(ctx, "10", x + length, y + 40, 22, INK, a)
    text(ctx, "10 cm", x + length / 2, y + 100, 46, "#5F7F99", a)


def scene_g(ctx, t, t_cut, t_lay, t_same):
    kb(ctx, t, 10.0, 1.05)
    table_top(ctx)
    bramble(ctx, 230, 2010, 3.4, 1, glass=False, look=1.0)
    hop = 40 * abs(math.sin((t - t_same - 0.3) * 5)) if t_same + 0.3 < t < t_same + 1.55 else 0
    squirrel(ctx, 960, 2060 - hop, 2.4, OCHRE, f=-1, arm_up=0.8 * prog(t, t_same, t_same + 0.5),
             tilt=0.12 * prog(t, t_same, t_same + 0.6), seed=2.0)
    cut = prog(t, t_cut + 0.6, t_cut + 1.6)
    gap = 30 * cut
    lift = prog(t, t_lay, t_lay + 1.0)          # step 1: pieces move apart vertically
    slide = prog(t, t_lay + 1.0, t_lay + 2.4)   # step 2: line up the left ends
    ax1, ay1 = lerp(L, 270, slide), lerp(RY, 900, lift)
    ax2, ay2 = lerp(M + gap, 270, slide), lerp(RY, 1120, lift)
    piece = M - L
    ribbon(ctx, ax1, ax1 + piece, ay1, th=46)
    ribbon(ctx, ax2, ax2 + piece, ay2, th=46)
    # rulers prove it: 10 cm and 10 cm
    ra = prog(t, t_lay + 2.4, t_lay + 3.1)
    if ra > 0:
        for ry0 in (900, 1120):
            ruler(ctx, 270, ry0 + 42, piece, ra)
    # scissors sweep in and snip
    sa = prog(t, t_cut - 0.2, t_cut + 0.5) * (1 - prog(t, t_cut + 1.8, t_cut + 2.4))
    if sa > 0:
        sx = lerp(W + 100, M + 52, prog(t, t_cut - 0.2, t_cut + 0.5))
        op = 0.6 if t < t_cut + 0.9 else 0.05
        ctx.push_group()
        scissors(ctx, sx, RY, 1.4, op, rot=math.pi)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(sa)
    # line-up check
    if slide >= 1.0:
        ga = prog(t, t_same - 0.8, t_same)
        for xx in (270, 270 + piece):
            ctx.set_dash([14, 12])
            ctx.set_line_width(4)
            src(ctx, "#6E8460", ga)
            ctx.move_to(xx, 840)
            ctx.line_to(xx, 1220)
            ctx.stroke()
        ctx.set_dash([])
        sl = prog(t, t_same - 2.4, t_same - 0.4)
        if 0 < sl < 1:
            glow(ctx, lerp(270, 270 + piece, sl), 1010, 90, "#E8D59A", 1.0)
        a = prog(t, t_same, t_same + 0.8)
        text(ctx, "=", 880, 1060, 170, INK, a)
        sparkles(ctx, 490, 1010, 300, a, 0.4)


def fraction(ctx, x, y, size, a):
    text(ctx, "1", x, y - size * 0.55, size, INK, a)
    rrect(ctx, x - size * 0.35, y - 4, size * 0.7, 8, 4, INK, a)
    text(ctx, "2", x, y + size * 0.55, size, INK, a)


TAIL = 270  # px: both kite tails are exactly this long (the two equal halves)


def kite_tail(ctx, x, y, t, a_guides=0.0):
    """Hang an equal-length ribbon tail straight down from (x, y), with a gentle wave
    that is identical for both kites (same phase), so the lengths always match."""
    pts = []
    for i in range(41):
        f = i / 40
        pts.append((x + 10 * math.sin(f * 2 * math.pi + t * 1.6) * f, y + TAIL * f))
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_width(16)
    src(ctx, RIBBON)
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.stroke()
    for k in (14, 28):
        bx, by = pts[k]
        ellipse(ctx, bx - 12, by, 11, 6, RIBBON_D)
        ellipse(ctx, bx + 12, by, 11, 6, RIBBON_D)
    return pts[-1]


def scene_h(ctx, t, t_text):
    garden(ctx, -220)
    # mirror-image flight: same height, same bob, mirrored sway
    lift = prog(t, 0.2, 2.5)
    ky = 600 + 10 * math.sin(t * 0.9) + (1 - lift) * 320
    sway = 0.05 * math.sin(t * 0.7)
    kites = ((400, "#E7B98C", sway), (680, "#B9C9DE", -sway))
    ends = []
    for kx, col, sw in kites:
        s_k = 1.15
        bx, by = kx - 80 * s_k * math.sin(sw), ky + 80 * s_k * math.cos(sw)
        ends.append((bx, by, kite_tail(ctx, bx, by, t)))
        kite(ctx, kx, ky, s_k, col, sw, tail=False)
    # equal strings: squirrels stand symmetrically
    ax, ay = squirrel(ctx, 220, 1560, 1.3, SAGE, f=1, arm_up=1.0, arm_out=0.2, seed=0.7)
    bx2, by2 = squirrel(ctx, 860, 1560, 1.3, OCHRE, f=-1, arm_up=1.0, arm_out=0.2, seed=2.0)
    ctx.set_line_width(2.5)
    src(ctx, "#7A6E62", 0.8)
    ctx.move_to(ax, ay)
    ctx.line_to(400, ky)
    ctx.move_to(bx2, by2)
    ctx.line_to(680, ky)
    ctx.stroke()
    # dashed guides across the top and bottom of both tails: same length
    ga = prog(t, t_text + 1.0, t_text + 1.8)
    if ga > 0:
        top = ends[0][1]
        bot = top + TAIL
        ctx.set_dash([14, 12])
        ctx.set_line_width(4)
        src(ctx, "#6E8460", ga)
        for yy in (top, bot):
            ctx.move_to(330, yy)
            ctx.line_to(750, yy)
        ctx.stroke()
        ctx.set_dash([])
        rrect(ctx, 440, (top + bot) / 2 - 34, 200, 68, 30, "#FFFFFF", 0.8 * ga)
        text(ctx, "same", W / 2, (top + bot) / 2, 44, "#6E8460", ga)
    a = prog(t, t_text, t_text + 1.0)
    rrect(ctx, 210, 150, 660, 300, 50, "#FFFFFF", 0.75 * a)
    fraction(ctx, 360, 300, 90, a)
    text(ctx, "and", W / 2, 300, 60, INK, a)
    fraction(ctx, 720, 300, 90, a)
    sparkles(ctx, W / 2, 300, 360, a * prog(t, t_text + 3.4, t_text + 4.2), 1.1)


def scene_i(ctx, t):
    g = cairo.LinearGradient(0, 0, 0, 1000)
    g.add_color_stop_rgb(0, *rgb(SKY_T))
    g.add_color_stop_rgb(1, *rgb(SKY_B))
    ctx.set_source(g)
    ctx.paint()
    ellipse(ctx, 540, 900, 900, 260, HILL)
    # Mabel's square patch (beyond the fence)
    px, py, ps = 300, 560, 520
    ctx.save()
    ctx.translate(px + ps / 2, py + ps / 2)
    ctx.scale(1.0, 0.62)
    ctx.translate(-(px + ps / 2), -(py + ps / 2))
    rrect(ctx, px, py, ps, ps, 18, SOIL)
    for i in range(6):
        for j in range(6):
            ellipse(ctx, px + 45 + i * 86, py + 45 + j * 86, 16, 12, LEAF)
    ctx.set_line_width(5)
    src(ctx, "#F5EFE2")
    ctx.move_to(px + ps / 2, py)
    ctx.line_to(px + ps / 2, py + ps)
    ctx.move_to(px, py + ps * 0.38)  # one string a little off-centre: is it fair?
    ctx.line_to(px + ps, py + ps * 0.38)
    ctx.stroke()
    ctx.restore()
    mouse(ctx, 520 + 30 * prog(t, 0.5, 3.0), 950, 1.2, f=1)
    # fence in front
    for xx in range(-40, W + 100, 95):
        rrect(ctx, xx, 1080, 60, 330, 10, FENCE)
        src(ctx, FENCE)
        ctx.move_to(xx, 1090)
        ctx.line_to(xx + 30, 1050)
        ctx.line_to(xx + 60, 1090)
        ctx.fill()
    rrect(ctx, -10, 1150, W + 20, 26, 6, FENCE_D)
    rrect(ctx, -10, 1300, W + 20, 26, 6, FENCE_D)
    src(ctx, GRASS)
    ctx.rectangle(0, 1380, W, H - 1380)
    ctx.fill()
    turn = prog(t, 0.0, 1.5)
    bramble(ctx, lerp(260, 300, turn), 1700, 2.6, 1)


# ---------- timeline (from narration timings) ----------
T = {
    "b": 3.3, "c": 13.3, "c_long": 2.0, "d": 20.2, "d_what": 25.0,
    "e": 28.2, "e_fold": 28.8, "e_ends": 32.8, "e_mid": 34.8,
    "f": 39.8, "f_look": 40.4, "f_fold": 41.8, "f_mark": 44.0,
    "g": 47.8, "g_cut": 48.4, "g_lay": 50.8, "g_same": 54.8,
    "h": 57.8, "h_text": 58.4, "i": 65.8, "a2": 74.2,
}

SCENES = [  # (start, end, draw(ctx, local_t))
    (0.0, T["b"], lambda c, lt: scene_a(c, lt)),
    (T["b"], T["c"], lambda c, lt: scene_b(c, lt)),
    (T["c"], T["d"], lambda c, lt: scene_c(c, lt, T["c_long"])),
    (T["d"], T["e"], lambda c, lt: scene_d(c, lt, T["d_what"] - T["d"])),
    (T["e"], T["f"], lambda c, lt: scene_e(c, lt, T["e_fold"] - T["e"], T["e_ends"] - T["e"], T["e_mid"] - T["e"])),
    (T["f"], T["g"], lambda c, lt: scene_f(c, lt, T["f_look"] - T["f"], T["f_fold"] - T["f"], T["f_mark"] - T["f"])),
    (T["g"], T["h"], lambda c, lt: scene_g(c, lt, T["g_cut"] - T["g"], T["g_lay"] - T["g"], T["g_same"] - T["g"])),
    (T["h"], T["i"], lambda c, lt: scene_h(c, lt, T["h_text"] - T["h"])),
    (T["i"], T["a2"], lambda c, lt: scene_i(c, lt)),
    (T["a2"], TOTAL, lambda c, lt: scene_a(c, lt, loop=True)),
]
XF = 0.7  # crossfade seconds (slow dissolve, never a flash)


def draw_frame(ctx, t):
    NOW[0] = t
    for i, (a, b, fn) in enumerate(SCENES):
        if a <= t < b or (i == len(SCENES) - 1 and t >= a):
            ctx.save()
            fn(ctx, t - a)
            ctx.restore()
            # dissolve into the next scene during the last XF seconds
            if i + 1 < len(SCENES) and t > b - XF:
                na, _, nfn = SCENES[i + 1]
                ctx.push_group()
                ctx.save()
                nfn(ctx, max(0.0, t - na))
                ctx.restore()
                ctx.pop_group_to_source()
                ctx.paint_with_alpha(ease((t - (b - XF)) / XF))
            return


def make_surface():
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    return surf, cairo.Context(surf)


def main():
    mode = sys.argv[1]
    if mode == "frames":
        for ts in sys.argv[2:]:
            surf, ctx = make_surface()
            draw_frame(ctx, float(ts))
            surf.write_to_png(f"check_{float(ts):05.1f}.png")
        return
    n = int(TOTAL * FPS)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "audio_norm.wav",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-shortest", "-movflags", "+faststart",
         "logic_detectives_short1_is_this_really_half_v5.mp4"],
        stdin=subprocess.PIPE,
    )
    surf, ctx = make_surface()
    for i in range(n):
        ctx.identity_matrix()
        ctx.set_operator(cairo.OPERATOR_SOURCE)
        src(ctx, CREAM)
        ctx.paint()
        ctx.set_operator(cairo.OPERATOR_OVER)
        draw_frame(ctx, i / FPS)
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
        if i % 300 == 0:
            print(f"frame {i}/{n}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("done", ff.returncode)


if __name__ == "__main__":
    main()
