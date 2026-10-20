"""Short 1 v10: living characters that point at the action, and gentler, spaced-out zooms.

- rig.py replaces the character drawings (idle life, talking mouths, pointing arms, walking,
  jumping, head scratching).
- POSES below decide, second by second, who points at what (in each scene's own coordinates).
- Only four zooms, each at least 18 s apart and gentler; other moments use the lens or ring.

  python3 v10.py frames 0 5 ...   -> check stills
  python3 v10.py video            -> logic_detectives_short1_v10.mp4 (uses audio_v9.wav)
"""
import json
import math
import subprocess
import sys

import cairo

import render as R
import rig
import v6
import v7
import v8
import v9
from render import W, H, FPS, INK, rrect, text, src, prog, ease

rig.install()
rig.TALK = [(r["start"], r["end"], r["who"]) for r in json.load(open("timings_v7.json"))
            if r["who"] in ("O", "I", "B")]
rig.TIME_OFFSET = v6.IDLE0


def win(t, s, e, fade=0.4):
    """0 -> 1 -> 0 envelope for a pose held from s to e."""
    return ease((t - s) / fade) * (1 - ease((t - (e - fade)) / fade))


def hop(t, s, e, height):
    return height * abs(math.sin((t - s) * 6.0)) if s <= t <= e else 0.0


def poses(t):
    P = {"O": {}, "I": {}, "B": {}}
    O, I, B = P["O"], P["I"], P["B"]
    # 0-3 s hook (and the loop frame): Bramble faces the kites and points at the short tail
    if t < 3.0 or t >= 82.0:
        B["face"] = 1
        if t < 3.0:
            B.update(point=(690, 900), amt=win(t, 0.6, 3.0))
    # 3-14 s Today's case: Ivy and Otto reach for their cookie halves, then hop
    elif t < 14.0:
        I.update(point=(410, 1350), amt=win(t, 9.9, 13.8), jump=hop(t, 11.6, 12.6, 30))
        O.update(point=(670, 1350), amt=win(t, 9.9, 13.8), jump=hop(t, 11.7, 12.7, 30))
    # 14-26 s garden: Otto walks to his mark and holds the scissors over it; Ivy points at the middle
    elif t < 26.0:
        walk = prog(t, 14.0, 14.9)
        O["dx"] = -110 * walk
        if 14.0 <= t < 14.9:
            O["walk"] = t * 14.0
        if t < 20.0:
            O.update(point=(610, 1150), amt=win(t, 14.5, 17.4))
            I.update(point=(550, 1160), amt=win(t, 17.3, 19.7))
        else:   # what-if split: Otto unsure, Ivy points at the longer piece
            O.update(scratch=win(t, 20.6, 24.8), tilt=0.12 * win(t, 20.6, 24.8))
            I.update(point=(425, 1130), amt=win(t, 20.8, 25.2))
    # 26-33 s Bramble arrives; Otto points at card A (his guess), Ivy at card B
    elif t < 33.0:
        O["dx"] = -110
        B["walk"] = t * 11 if t < 29.0 else None
        O.update(point=(352, 615), amt=win(t, 29.3, 32.8), jump=hop(t, 29.4, 29.9, 14))
        I.update(point=(727, 615), amt=win(t, 29.5, 32.8))
    # 33-45.5 s fold close-up: Bramble points at the ends, then at the middle
    elif t < 45.5:
        if t < 40.0:
            B.update(point=(110, 1000), amt=win(t, 36.8, 38.6))
        else:
            B.update(point=(540, 990), amt=win(t, 42.0, 45.0))
    # 45.5-50.9 s compare: Bramble aims his glass at the gap; Otto scratches his head ("Oops")
    elif t < 50.9:
        B.update(point=(578, 1000), amt=win(t, 45.8, 48.4))
        O.update(scratch=win(t, 49.1, 50.8), tilt=-0.1 * win(t, 49.1, 50.8))
    # 50.9-60.5 s proof: Bramble points at the cut, then the pieces; Otto points at the rulers
    elif t < 60.5:
        if t < 53.0:
            B.update(point=(545, 1000), amt=win(t, 51.1, 52.9))
        else:
            B.update(point=(490, 1010), amt=win(t, 53.1, 55.7))
        O.update(point=(700, 1160), amt=win(t, 55.9, 58.4))
    # 60.5-68.5 s kites: Ivy hops on "They match!", Otto on "Yay!"
    elif t < 68.5:
        I["jump"] = hop(t, 60.9, 61.9, 26)
        O["jump"] = hop(t, 65.5, 66.6, 30)
    # 68.5-78.8 s Remember: Bramble points at each recap row as it is read
    elif t < 78.8:
        for s_, e_, y_ in ((68.8, 71.6, 1005), (71.8, 75.3, 1285), (75.5, 78.6, 1565)):
            if s_ - 0.1 <= t <= e_:
                B.update(point=(330, y_), amt=win(t, s_, e_))
    # 78.8-82 s teaser: Bramble aims his glass at Mabel's patch
    else:
        B.update(point=(560, 820), amt=win(t, 79.0, 81.6))
    return P


# Four gentle zooms, at least 18 s apart. Other moments use the lens or the ring.
CUES = []
for c in v9.CUES:
    if c[0] == "zoom" and c[1] in (48.1, 53.1):
        continue
    CUES.append(c)
CUES += [
    ("ring", 48.1, 50.6, 689, 402, 160, 135, "B is right", 689, 640),
    ("ring", 53.1, 55.6, 490, 1010, 330, 200, "Line them up", 540, 1340),
]
ZOOM_Z = {5.9: 1.22, 33.4: 1.18, 51.1: 1.28, 79.0: 1.22}
CUES = [(c[0], c[1], c[2], c[3], c[4], ZOOM_Z[c[1]]) + tuple(c[6:]) if c[0] == "zoom" else c for c in CUES]
CUES.sort(key=lambda c: c[1])


def zoom_amount(t):
    for c in CUES:
        if c[0] == "zoom" and c[1] <= t <= c[2]:
            k = ease((t - c[1]) / 1.1) * (1 - ease((t - (c[2] - 1.1)) / 1.1))
            return 1 + (c[5] - 1) * k, c[3], c[4]
    return None


def draw_scenes(ctx, t):
    rig.POSE.clear()
    rig.POSE.update(poses(t))
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


SCENE_SURF = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)


def draw_frame(ctx, t):
    sc = cairo.Context(SCENE_SURF)
    sc.set_operator(cairo.OPERATOR_SOURCE)
    src(sc, R.CREAM)
    sc.paint()
    sc.set_operator(cairo.OPERATOR_OVER)
    draw_scenes(sc, t)
    SCENE_SURF.flush()
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
    for c in CUES:
        kind, s, e = c[0], c[1], c[2]
        if not (s <= t <= e):
            continue
        a = prog(t, s, s + 0.4) * (1 - prog(t, e - 0.35, e))
        if kind == "ring":
            v8.focus(ctx, *c[3:10], a)
        elif kind == "lens":
            v9.lens(ctx, SCENE_SURF, *c[3:12], a)
        elif kind == "zoom":
            v9.label_pill(ctx, c[6], c[7], c[8], a)
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
            draw_frame(ctx, float(ts_))
            surf.write_to_png(f"v10_{float(ts_):05.1f}.png")
        return
    n = int(v7.TOTAL * FPS)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "audio_v9.wav",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart",
         "logic_detectives_short1_v10.mp4"], stdin=subprocess.PIPE)
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
