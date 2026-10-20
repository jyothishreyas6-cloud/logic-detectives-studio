"""Short 1 v8: v7 plus a 'look here' focus overlay on every action moment.

The rest of the frame dims softly, a warm ring circles the exact spot, and a short label
with an arrow names it. Fades in and out over about 0.4 s; never flashes.

  python3 v8.py frames 0 5 ...   -> check stills
  python3 v8.py video            -> logic_detectives_short1_v8.mp4 (uses audio_v7.wav)
"""
import math
import subprocess
import sys

import cairo

import render as R
import v6
import v7
from render import W, H, FPS, INK, rrect, text, src, prog, ease

RING = "#F2C85B"
LABEL_INK = "#5C4A1E"

# (start, end, cx, cy, rx, ry, label, label_x, label_y)  - screen coordinates
FOCUS = [
    (0.0, 3.0, 545, 900, 300, 250, "One long, one short", 540, 470),
    (5.9, 9.3, 540, 1260, 250, 250, "Split in the middle", 540, 1610),
    (9.7, 13.3, 540, 1340, 330, 230, "Same size for each friend", 540, 1010),
    (14.3, 17.0, 640, 1165, 120, 95, "Otto's mark", 820, 1420),
    (17.3, 19.5, 575, 1165, 230, 90, "Is the middle here?", 560, 1420),
    (20.6, 25.4, 555, 1110, 470, 140, "One piece longer", 540, 1420),
    (29.1, 32.9, 540, 545, 505, 300, "Choose A or B", 540, 915),
    (33.4, 36.6, 540, 1000, 490, 140, "Watch the ends", 540, 1270),
    (36.8, 38.3, 100, 990, 110, 110, "Ends together", 330, 1250),
    (42.0, 44.6, 540, 990, 130, 130, "The middle", 540, 1260),
    (45.7, 47.9, 580, 1000, 140, 120, "Not the same spot", 540, 1330),
    (48.1, 50.6, 689, 402, 165, 130, "B is right", 689, 620),
    (51.1, 52.8, 545, 1000, 125, 110, "Cut here", 760, 1250),
    (53.1, 55.6, 490, 1010, 330, 200, "Line them up", 540, 1340),
    (55.9, 58.3, 490, 1050, 350, 210, "10 cm and 10 cm", 540, 1400),
    (58.5, 60.3, 700, 1020, 120, 200, "Ends line up", 870, 1330),
    (62.3, 66.0, 540, 860, 290, 230, "Same length tails", 540, 1230),
    (79.0, 81.6, 560, 820, 330, 230, "Four pieces", 540, 1180),
]


def focus(ctx, cx, cy, rx, ry, label, lx, ly, a):
    if a <= 0:
        return
    # 1. soft dim everywhere except an elliptical window
    g = cairo.RadialGradient(0, 0, 0, 0, 0, 1)
    g.add_color_stop_rgba(0.0, 0.12, 0.10, 0.08, 0.0)
    g.add_color_stop_rgba(0.80, 0.12, 0.10, 0.08, 0.0)
    g.add_color_stop_rgba(1.0, 0.12, 0.10, 0.08, 0.34 * a)
    k = 1.35
    g.set_matrix(cairo.Matrix(1 / (rx * k), 0, 0, 1 / (ry * k), -cx / (rx * k), -cy / (ry * k)))
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, H)
    ctx.fill()
    # 2. a warm ring that gently breathes
    br = 1.0 + 0.035 * math.sin(R.NOW[0] * 3.2)
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(rx * 1.08 * br, ry * 1.08 * br)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_line_width(9)
    r, gg, b = R.rgb(RING)
    ctx.set_source_rgba(r, gg, b, 0.95 * a)
    ctx.stroke()
    # 3. label pill + arrow to the ring edge
    ctx.select_font_face(R.FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(44)
    tw = ctx.text_extents(label)[2]
    pw, ph = tw + 64, 84
    dx, dy = cx - lx, cy - ly
    ang = math.atan2(dy, dx)
    # where the ring edge is, along the line from the label to the centre
    t_edge = 1.0 / math.sqrt((math.cos(ang) / (rx * 1.12)) ** 2 + (math.sin(ang) / (ry * 1.12)) ** 2)
    ex, ey = cx - t_edge * math.cos(ang), cy - t_edge * math.sin(ang)
    # start the arrow at the pill's edge
    sx = lx + math.cos(ang) * min(pw / 2, abs((ph / 2) / (math.sin(ang) + 1e-9)))
    sy = ly + math.sin(ang) * min(ph / 2, abs((pw / 2) / (math.cos(ang) + 1e-9)))
    if math.hypot(ex - sx, ey - sy) > 30:
        ctx.set_line_width(7)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_source_rgba(r, gg, b, 0.95 * a)
        ctx.move_to(sx, sy)
        ctx.line_to(ex - 18 * math.cos(ang), ey - 18 * math.sin(ang))
        ctx.stroke()
        hx, hy = ex, ey
        ctx.move_to(hx, hy)
        ctx.line_to(hx - 30 * math.cos(ang - 0.45), hy - 30 * math.sin(ang - 0.45))
        ctx.line_to(hx - 30 * math.cos(ang + 0.45), hy - 30 * math.sin(ang + 0.45))
        ctx.close_path()
        ctx.fill()
    rrect(ctx, lx - pw / 2, ly - ph / 2, pw, ph, 40, RING, 0.97 * a)
    text(ctx, label, lx, ly, 44, LABEL_INK, a)


def draw_frame(ctx, t):
    R.NOW[0] = t + v6.IDLE0
    for i, (a, b, fn) in enumerate(v7.SCENES):
        if a <= t < b or (i == len(v7.SCENES) - 1 and t >= a):
            ctx.save()
            fn(ctx, t - a)
            ctx.restore()
            if i + 1 < len(v7.SCENES) and t > b - v7.XF:
                na, _, nfn = v7.SCENES[i + 1]
                ctx.push_group()
                ctx.save()
                nfn(ctx, max(0.0, t - na))
                ctx.restore()
                ctx.pop_group_to_source()
                ctx.paint_with_alpha(ease((t - (b - v7.XF)) / v7.XF))
            break
    R.NOW[0] = t + v6.IDLE0
    # Otto's scissors hover over his mark while he says "I'll cut it right here!"
    sa = prog(t, 14.1, 14.5) * (1 - prog(t, 17.0, 17.4))
    if sa > 0:
        ang = math.atan2(1165 - 1060, 637 - 715)
        ctx.push_group()
        ctx.set_dash([10, 8])
        ctx.set_line_width(4)
        src(ctx, "#FFFFFF", 0.9)
        ctx.move_to(637, 1120)
        ctx.line_to(637, 1215)
        ctx.stroke()
        ctx.set_dash([])
        R.scissors(ctx, 715, 1060, 1.35, 0.15 + 0.45 * abs(math.sin(t * 2.6)), rot=ang)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(sa)
    # look-here overlay first, so speech bubbles and explanation cards stay bright
    for s, e, cx, cy, rx, ry, label, lx, ly in FOCUS:
        a = prog(t, s, s + 0.4) * (1 - prog(t, e - 0.35, e))
        focus(ctx, cx, cy, rx, ry, label, lx, ly, a)
    ka = prog(t, 38.4, 38.9) * (1 - prog(t, 41.6, 42.1))
    if ka > 0:
        rrect(ctx, 150, 1220, 780, 190, 40, "#FFFFFF", 0.94 * ka)
        text(ctx, "Ends match, so both", W / 2, 1282, 50, INK, ka)
        text(ctx, "sides are the same length", W / 2, 1350, 50, INK, ka)
    for s, e, cx, cy, lines, tx, ty in v7.BUBBLES:
        a = prog(t, s - 0.1, s + 0.25) * (1 - prog(t, e - 0.2, e + 0.15))
        v6.bubble(ctx, cx, cy, lines, tx, ty, a)


def main():
    mode = sys.argv[1]
    if mode == "frames":
        for ts_ in sys.argv[2:]:
            surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
            ctx = cairo.Context(surf)
            src(ctx, R.CREAM)
            ctx.paint()
            draw_frame(ctx, float(ts_))
            surf.write_to_png(f"v8_{float(ts_):05.1f}.png")
        return
    n = int(v7.TOTAL * FPS)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "audio_v7.wav",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart",
         "logic_detectives_short1_v8.mp4"], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    for i in range(n):
        ctx.identity_matrix()
        ctx.set_operator(cairo.OPERATOR_SOURCE)
        src(ctx, R.CREAM)
        ctx.paint()
        ctx.set_operator(cairo.OPERATOR_OVER)
        draw_frame(ctx, i / FPS)
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
    ff.stdin.close()
    ff.wait()
    print("done", ff.returncode)


if __name__ == "__main__":
    main()
