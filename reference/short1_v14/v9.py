"""Short 1 v9: mixed attention cues, chosen by type of moment.

- LENS  (tiny details): Bramble's magnifying glass shows an enlarged view of the spot,
         joined to it by a thin line and a small ring.
- ZOOM  (big actions): the camera slowly pushes in on the action, then eases back out.
- RING  (comparisons of two things): soft dim, ring and arrow label (from v8).
- Every cue starts with a soft two-note "look" chime.

  python3 v9.py frames 0 5 ...   -> check stills
  python3 v9.py audio            -> audio_v9.wav (v7 mix + look chimes)
  python3 v9.py video            -> logic_detectives_short1_v9.mp4
"""
import math
import subprocess
import sys
import wave

import cairo
import numpy as np

import render as R
import v6
import v7
import v8
from render import W, H, FPS, INK, rrect, text, src, prog, ease

RING = v8.RING
LABEL_INK = v8.LABEL_INK

# kind, start, end, then per kind:
#   ring: cx, cy, rx, ry, label, lx, ly
#   lens: tx, ty (target), lx, ly (lens centre), r, mag, label, label_x, label_y
#   zoom: cx, cy, z, label, label_x, label_y
CUES = [
    ("ring", 0.0, 3.0, 545, 900, 300, 250, "One long, one short", 540, 470),
    ("zoom", 5.9, 9.3, 540, 1260, 1.35, "Split in the middle", 540, 1700),
    ("ring", 9.7, 13.3, 540, 1340, 330, 230, "Same size for each friend", 540, 1010),
    ("lens", 14.3, 17.0, 637, 1160, 185, 570, 150, 2.4, "Otto's mark", 190, 790),
    ("ring", 17.3, 19.5, 575, 1165, 230, 90, "Is the middle here?", 560, 1420),
    ("ring", 20.6, 25.4, 555, 1110, 470, 140, "One piece longer", 540, 1420),
    ("ring", 29.1, 32.9, 540, 545, 505, 300, "Choose A or B", 540, 915),
    ("zoom", 33.4, 36.6, 540, 1000, 1.28, "Watch the ends", 540, 1330),
    ("lens", 36.8, 38.3, 100, 990, 380, 520, 170, 2.2, "Ends together", 380, 300),
    ("lens", 42.0, 44.6, 540, 990, 540, 520, 170, 2.2, "The middle", 540, 300),
    ("lens", 45.7, 47.9, 578, 1000, 540, 520, 170, 2.2, "Not the same spot", 540, 300),
    ("zoom", 48.1, 50.6, 689, 402, 1.45, "B is right", 689, 760),
    ("zoom", 51.1, 52.8, 545, 1000, 1.5, "Cut here", 545, 1330),
    ("zoom", 53.1, 55.6, 490, 1010, 1.25, "Line them up", 540, 1420),
    ("ring", 55.9, 58.3, 490, 1050, 350, 210, "10 cm and 10 cm", 540, 1400),
    ("lens", 58.5, 60.3, 700, 1010, 700, 520, 170, 2.2, "Ends line up", 700, 300),
    ("ring", 62.3, 66.0, 540, 860, 290, 230, "Same length tails", 540, 1230),
    ("zoom", 79.0, 81.3, 560, 820, 1.35, "Four pieces", 540, 1250),
]


def env(t, s, e, ramp=0.6):
    return ease((t - s) / ramp) * (1 - ease((t - (e - ramp)) / ramp))


def zoom_amount(t):
    """(z, cx, cy) for the camera at time t, or None."""
    for c in CUES:
        if c[0] == "zoom" and c[1] <= t <= c[2]:
            k = env(t, c[1], c[2], 0.8)
            return 1 + (c[5] - 1) * k, c[3], c[4]
    return None


def label_pill(ctx, label, lx, ly, a):
    ctx.select_font_face(R.FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(44)
    pw = ctx.text_extents(label)[2] + 64
    rrect(ctx, lx - pw / 2, ly - 42, pw, 84, 40, RING, 0.97 * a)
    text(ctx, label, lx, ly, 44, LABEL_INK, a)


def lens(ctx, scene_surf, tx, ty, lx, ly, r, mag, label, bx, by, a):
    if a <= 0:
        return
    rr, gg, bb = R.rgb(RING)
    grow = 0.7 + 0.3 * a
    rad = r * grow
    # thin line from the lens to the exact spot, and a small ring on the spot
    ang = math.atan2(ty - ly, tx - lx)
    ctx.set_line_width(5)
    ctx.set_source_rgba(rr, gg, bb, 0.95 * a)
    ctx.move_to(lx + (rad + 12) * math.cos(ang), ly + (rad + 12) * math.sin(ang))
    ctx.line_to(tx - 46 * math.cos(ang), ty - 46 * math.sin(ang))
    ctx.stroke()
    ctx.set_line_width(6)
    ctx.arc(tx, ty, 42 + 3 * math.sin(R.NOW[0] * 3.2), 0, 2 * math.pi)
    ctx.stroke()
    # handle, pointing away from the target
    hang = ang + math.pi + 0.5
    ctx.set_line_width(30 * grow)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    src(ctx, "#9A7350", a)
    ctx.move_to(lx + rad * math.cos(hang), ly + rad * math.sin(hang))
    ctx.line_to(lx + (rad + 120 * grow) * math.cos(hang), ly + (rad + 120 * grow) * math.sin(hang))
    ctx.stroke()
    # the magnified view, sampled from the clean scene
    ctx.save()
    ctx.arc(lx, ly, rad, 0, 2 * math.pi)
    ctx.clip()
    pat = cairo.SurfacePattern(scene_surf)
    m = cairo.Matrix()
    m.translate(tx, ty)
    m.scale(1 / mag, 1 / mag)
    m.translate(-lx, -ly)
    pat.set_matrix(m)
    pat.set_filter(cairo.FILTER_GOOD)
    ctx.set_source(pat)
    ctx.paint_with_alpha(a)
    # glass sheen
    ctx.set_source_rgba(1, 1, 1, 0.12 * a)
    ctx.arc(lx - rad * 0.35, ly - rad * 0.35, rad * 0.45, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()
    ctx.set_line_width(22 * grow)
    src(ctx, "#9A7350", a)
    ctx.arc(lx, ly, rad, 0, 2 * math.pi)
    ctx.stroke()
    label_pill(ctx, label, bx, by, a)


def draw_scenes(ctx, t):
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
    # Otto's scissors over his mark (part of the scene, so the camera and lens see them)
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


SCENE_SURF = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)


def draw_frame(ctx, t):
    # 1. the scene, drawn once onto its own surface (the lens samples from it)
    sc = cairo.Context(SCENE_SURF)
    sc.set_operator(cairo.OPERATOR_SOURCE)
    src(sc, R.CREAM)
    sc.paint()
    sc.set_operator(cairo.OPERATOR_OVER)
    draw_scenes(sc, t)
    SCENE_SURF.flush()
    # 2. camera: paint the scene, zoomed when a zoom cue is active
    ctx.save()
    zm = zoom_amount(t)
    if zm:
        z, cx, cy = zm
        ctx.translate(cx, cy)
        ctx.scale(z, z)
        ctx.translate(-cx, -cy)
    ctx.set_source_surface(SCENE_SURF, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint()
    ctx.restore()
    R.NOW[0] = t + v6.IDLE0
    # 3. cues
    for c in CUES:
        kind, s, e = c[0], c[1], c[2]
        if not (s <= t <= e):
            continue
        a = prog(t, s, s + 0.4) * (1 - prog(t, e - 0.35, e))
        if kind == "ring":
            v8.focus(ctx, *c[3:10], a)
        elif kind == "lens":
            lens(ctx, SCENE_SURF, *c[3:12], a)
        elif kind == "zoom":
            label_pill(ctx, c[6], c[7], c[8], a)
    # 4. explanation card and speech bubbles stay on top, undimmed
    ka = prog(t, 38.4, 38.9) * (1 - prog(t, 41.6, 42.1))
    if ka > 0:
        rrect(ctx, 150, 1220, 780, 190, 40, "#FFFFFF", 0.94 * ka)
        text(ctx, "Ends match, so both", W / 2, 1282, 50, INK, ka)
        text(ctx, "sides are the same length", W / 2, 1350, 50, INK, ka)
    for s, e, cx, cy, lines, tx, ty in v7.BUBBLES:
        a = prog(t, s - 0.1, s + 0.25) * (1 - prog(t, e - 0.2, e + 0.15))
        v6.bubble(ctx, cx, cy, lines, tx, ty, a)


def look_chime():
    sr = 24000
    out = np.zeros(int(0.9 * sr), dtype=np.float32)
    for f0, at in ((1318.5, 0.0), (1760.0, 0.11)):
        n = len(out) - int(at * sr)
        tt = np.arange(n) / sr
        tone = np.sin(2 * np.pi * f0 * tt) * np.minimum(tt / 0.006, 1) * np.exp(-tt / 0.22)
        out[int(at * sr):] += (tone * 0.045).astype(np.float32)
    return out


def build_audio():
    with wave.open("audio_v7_raw.wav") as w:
        sr = w.getframerate()
        mix = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    ch = look_chime()
    for c in CUES:
        a = int(c[1] * sr) + int(0.05 * sr)
        b = min(len(mix), a + len(ch))
        mix[a:b] += ch[: b - a]
    mix = np.clip(mix, -1, 1)
    with wave.open("audio_v9_raw.wav", "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", "audio_v9_raw.wav", "-af",
                    "highpass=f=70,loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000", "audio_v9.wav"], check=True)
    print("audio_v9.wav written")


def main():
    mode = sys.argv[1]
    if mode == "frames":
        for ts_ in sys.argv[2:]:
            surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
            ctx = cairo.Context(surf)
            draw_frame(ctx, float(ts_))
            surf.write_to_png(f"v9_{float(ts_):05.1f}.png")
        return
    if mode == "audio":
        build_audio()
        return
    n = int(v7.TOTAL * FPS)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "audio_v9.wav",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart",
         "logic_detectives_short1_v9.mp4"], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    for i in range(n):
        ctx.identity_matrix()
        draw_frame(ctx, i / FPS)
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
    ff.stdin.close()
    ff.wait()
    print("done", ff.returncode)


if __name__ == "__main__":
    main()
