"""Short 1 v13: true-to-life sizes and no overlapping subjects (on the v12 timeline and audio).

  python3 v13.py frames 0 5 ...
  python3 v13.py video     -> logic_detectives_short1_v13.mp4 (uses audio_v12.wav)
"""
import math
import subprocess
import sys

import cairo

import render as R
import rig3d
import v6
import v7
import v8
import v9
import v11
import v12
import scenes13 as S
from render import W, H, FPS, INK, rrect, text, src, prog, ease

R._rig = rig3d

# same scene timings (old timeline) with the new layouts
v7.SCENES[:] = [
    (0.0, 3.0, lambda c, lt: S.scene_open(c, lt)),
    (3.0, 14.0, lambda c, lt: S.scene_ctx(c, lt)),
    (14.0, 20.0, lambda c, lt: S.scene_b(c, lt)),
    (20.0, 26.0, lambda c, lt: S.scene_c(c, lt)),
    (26.0, 33.0, lambda c, lt: S.scene_d(c, lt)),
    (33.0, 45.5, lambda c, lt: S.scene_e(c, lt)),
    (45.5, 50.9, lambda c, lt: S.scene_f(c, lt)),
    (50.9, 60.5, lambda c, lt: S.scene_g(c, lt)),
    (60.5, 68.5, lambda c, lt: S.scene_kites(c, lt)),
    (68.5, 78.8, lambda c, lt: S.scene_recap(c, lt)),
    (78.8, 82.0, lambda c, lt: S.scene_i(c, lt)),
    (82.0, 83.0, lambda c, lt: S.scene_loop(c, lt)),
]

RM, RY, L, M = S.RIB_MARK, S.RIB_Y, S.L, S.M
# Cues on the old timeline (same times as v11, so the v12 look chimes still line up).
# ring: cx, cy, rx, ry, label, lx, ly | lens: tx, ty, lx, ly, r, mag, label, bx, by | zoom: cx, cy, z, label, lx, ly
CUES_OLD = [
    ("ring", 0.0, 3.0, 540, 790, 320, 200, "", 540, 470),
    ("zoom", 5.9, 9.3, 540, 930, 1.22, "", 540, 1250),
    ("ring", 9.7, 13.3, 540, 1260, 230, 150, "Each friend gets the same", 540, 1050),
    ("lens", 14.3, 17.0, RM, RY, 300, 470, 120, 2.4, "", 300, 640),
    ("ring", 17.3, 19.5, (S.RIB_MID + RM) / 2, RY, 130, 60, "", 540, 1640),
    ("ring", 20.6, 25.4, S.RIB_MID, RY - 15, 320, 90, "One piece is longer", 540, 1640),
    ("ring", 29.1, 32.9, 540, 465, 500, 210, "", 540, 900),
    ("zoom", 33.4, 36.6, 540, S.RY, 1.18, "Watch the ends", 540, 1180),
    ("lens", 36.8, 38.3, L, S.RY, 300, 400, 130, 2.2, "", 300, 590),
    ("lens", 42.0, 44.6, M, S.RY, 540, 380, 130, 2.2, "The middle", 540, 590),
    ("lens", 45.7, 47.9, (M + S.MARK) / 2, S.RY, 540, 380, 130, 2.2, "The middle is here", 540, 590),
    ("ring", 48.1, 50.6, 689, 402, 150, 120, "It's B!", 689, 600),
    ("zoom", 51.1, 52.8, 540, S.RY, 1.28, "Cut at the fold", 540, 1180),
    ("ring", 53.1, 55.6, 390, S.RY - 5, 230, 190, "Line them up", 540, 1240),
    ("ring", 55.9, 58.3, 390, S.RY + 25, 240, 200, "10 cm and 10 cm", 540, 1240),
    ("lens", 58.5, 60.3, M, S.RY - 5, 800, 420, 130, 2.2, "Same length!", 800, 610),
    ("ring", 62.3, 66.0, 540, 780, 280, 125, "Two equal pieces", 540, 1050),
    ("zoom", 79.0, 81.3, 540, 760, 1.22, "Four pieces", 540, 1240),
]
assert [c[1] for c in CUES_OLD] == [c[1] for c in v11.CUES], "cue times must match the v12 audio"
v11.CUES[:] = CUES_OLD
v12.CUES[:] = [v12.relabel(c) for c in CUES_OLD]

# speech bubbles: (line index, cx, cy, lines, tail x, tail y), all in clear space
BUB = [
    (4, 800, 520, ["One ribbon, two kites.", "I'll cut it right here!"], 900, 975),
    (5, 300, 560, ["Wait. Is that", "the middle?"], 160, 975),
    (7, 800, 1690, ["Let's not guess.", "Let's test."], 640, 1700),
    (12, 560, 1400, ["Ends together."], 600, 1600),
    (16, 420, 1190, ["Oops. My mark", "was too far."], 280, 1380),
    (21, 330, 1210, ["They match!"], 220, 1400),
    (23, 820, 1210, ["Yay!"], 880, 1400),
]
v12.BUBBLES[:] = [(v12.ROWS[i]["start"] - 0.1, v12.ROWS[i]["end"] + 1.0, cx, cy, ln, tx, ty)
                  for i, cx, cy, ln, tx, ty in BUB]
CARD_Y = 1080


def win(t, s, e, fade=0.4):
    return ease((t - s) / fade) * (1 - ease((t - (e - fade)) / fade))


def hop(t, s, e, height):
    return height * math.sin(math.pi * (t - s) / (e - s)) if s <= t <= e else 0.0


def poses(t):
    P = {"O": {}, "I": {}, "B": {}}
    O, I, B = P["O"], P["I"], P["B"]
    if t < 3.0 or t >= 82.0:
        B["face"] = 1
        if t < 3.0:
            B.update(point=(720, 830), amt=win(t, 0.6, 3.0))
    elif t < 14.0:
        I.update(point=(440, 1260), amt=win(t, 9.9, 13.8), jump=hop(t, 11.6, 12.6, 40))
        O.update(point=(640, 1260), amt=win(t, 9.9, 13.8), jump=hop(t, 11.7, 12.7, 40))
    elif t < 26.0:
        walk = prog(t, 14.0, 14.9)
        O["dx"] = -20 * walk
        if 14.0 <= t < 14.9:
            O["walk"] = t * 14.0
        if t < 20.0:
            O.update(point=(RM, RY), amt=win(t, 14.5, 17.4))
            I.update(point=(S.RIB_MID, RY), amt=win(t, 17.3, 19.7))
        else:
            O.update(scratch=win(t, 20.6, 24.8), tilt=0.12 * win(t, 20.6, 24.8))
            I.update(point=((S.RIB_L + RM) / 2, RY - 20), amt=win(t, 20.8, 25.2))
    elif t < 33.0:
        O["dx"] = -20
        B["walk"] = t * 11 if t < 29.0 else None
        O.update(point=(300, 465), amt=win(t, 29.3, 32.8), jump=hop(t, 29.4, 29.9, 16))
        I.update(point=(780, 465), amt=win(t, 29.5, 32.8))
    elif t < 45.5:
        if t < 40.0:
            B.update(point=(L, S.RY), amt=win(t, 36.8, 38.6), glass=True)
        else:
            B.update(point=(M, S.RY), amt=win(t, 42.0, 45.0), glass=True)
    elif t < 50.9:
        B.update(point=((M + S.MARK) / 2, S.RY), amt=win(t, 45.8, 48.4), glass=True)
        O.update(scratch=win(t, 49.1, 50.8), tilt=-0.1 * win(t, 49.1, 50.8))
    elif t < 60.5:
        if t < 53.0:
            B.update(point=(M, S.RY), amt=win(t, 51.1, 52.9), glass=True)
        else:
            B.update(point=(390, S.RY - 5), amt=win(t, 53.1, 55.7))
        pass   # Otto watches; the ring alone marks the rulers
    elif t < 68.5:
        I["jump"] = hop(t, 60.9, 61.9, 40)
        O["jump"] = hop(t, 65.5, 66.6, 40)
    elif t < 78.8:
        for s_, e_, y_ in ((68.8, 71.6, 455), (71.8, 75.3, 755), (75.5, 78.6, 1055)):
            if s_ - 0.1 <= t <= e_:
                B.update(point=(400, y_), amt=win(t, s_, e_))
    else:
        B.update(point=(540, 760), amt=win(t, 79.0, 81.6), glass=True)
    return P


v11.poses = poses
SCENE_SURF = v12.SCENE_SURF


def draw_frame(ctx, T):
    t = v12.to_old(T)
    sc = cairo.Context(SCENE_SURF)
    sc.set_operator(cairo.OPERATOR_SOURCE)
    src(sc, R.CREAM)
    sc.paint()
    sc.set_operator(cairo.OPERATOR_OVER)
    v12.draw_scenes(sc, T, t)
    SCENE_SURF.flush()
    ctx.save()
    zm = v11.zoom_amount(t)
    if zm:
        z, cx, cy = zm
        ctx.translate(cx, cy)
        ctx.scale(z, z)
        ctx.translate(-cx, -cy)
    ctx.set_source_surface(SCENE_SURF, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint()
    ctx.restore()
    R.NOW[0] = T + v6.IDLE0
    busy = v12.text_busy(T)
    for c in v12.CUES:
        kind, s, e = c[0], c[1], c[2]
        if not (s <= T <= e):
            continue
        a = prog(T, s, s + 0.4) * (1 - prog(T, e - 0.35, e))
        la = a * (1 - busy)
        if kind == "ring":
            cx, cy, rx, ry, label, lx, ly = c[3:10]
            if label and la > 0.01:
                v8.focus(ctx, cx, cy, rx, ry, label, lx, ly, la)
                if busy > 0:
                    v12.ring_only(ctx, cx, cy, rx, ry, a * busy)
            else:
                v12.ring_only(ctx, cx, cy, rx, ry, a)
        elif kind == "lens":
            args = list(c[3:12])
            if la <= 0.01:
                args[6] = ""
            v9.lens(ctx, SCENE_SURF, *args, a)
        elif kind == "zoom":
            v12._pill(ctx, c[6], c[7], c[8], la)
    c0, c1 = v12.CARD
    ka = prog(T, c0, c0 + 0.5) * (1 - prog(T, c1 - 0.5, c1))
    if ka > 0:
        rrect(ctx, 70, CARD_Y, 940, 190, 40, "#FFFFFF", 0.94 * ka)
        text(ctx, "The two ends match.", W / 2, CARD_Y + 62, 50, INK, ka)
        text(ctx, "So both sides are the same length.", W / 2, CARD_Y + 130, 50, INK, ka)
    for s, e, cx, cy, lines, tx, ty in v12.BUBBLES:
        a = prog(T, s - 0.1, s + 0.25) * (1 - prog(T, e - 0.2, e + 0.15))
        v6.bubble(ctx, cx, cy, lines, tx, ty, a)


def main():
    mode = sys.argv[1]
    if mode == "frames":
        for ts_ in sys.argv[2:]:
            surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
            ctx = cairo.Context(surf)
            draw_frame(ctx, float(ts_))
            surf.write_to_png(f"v13_{float(ts_):05.1f}.png")
        return
    n = int(v12.TOTAL * FPS)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "audio_v12.wav",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart",
         "logic_detectives_short1_v13.mp4"], stdin=subprocess.PIPE)
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
