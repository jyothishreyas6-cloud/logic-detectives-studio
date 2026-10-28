"""Logic Detectives episode kit: everything an episode needs except its own scenes.

An episode is a folder episodes/epNNN_slug/ with episode.py defining:

    CASE_NO = 4                   # episode number (matches the folder epNNN)
    RULE = "The last number tells how many."   # the ONE takeaway, said word for word 3+ times
    SETTING = "the back verandah"  # where the case happens (context, upload copy)
    SENTENCE_LIMIT = 8            # 8 for Kindergarten to Year 2, 10 for Years 3 to 4
    LINES  = [Line("B", "Case open!", gap=0.4), ...]   # gap = silence after the line (s)
    STRIP_HIDDEN = {i, ...}       # lines whose words a card already shows
    CHILD_TURN = i or None        # no music in the gap after this line
    STAMP_LINE = i                # "Case solved!" line (stamp appears with it)
    OPEN_LINE = 0                 # "Case open!" line (glass sweep at the start)
    CUT = [(first_line, last_line), ...]   # 45 to 60 s discovery cut, in line ranges
    def cues(ep):  -> list of ("ring", s, e, cx, cy, rx, ry) / ("lens", s, e, tx, ty, lx, ly, r, mag)
                                  / ("zoom", s, e, cx, cy, z)        (real seconds)
    def poses(ep, T): -> {"B": {...}, "O": {...}, "I": {...}}   (rig14 POSE dicts)
    def scene(ctx, ep, T): draw the scene for time T (frame coordinates; keep the bottom
                           STRIP_H px for the caption strip: characters' feet at most y 1700)
    def cards(ctx, ep, T): optional, draw cards/overlays above cues (title, A/B, recap)

`ep` gives ep.rows[i]["start"/"end"], ep.s(i), ep.e(i), ep.total.

Commands (run from the repo root):
    python3 engine/kit.py EPISODE_DIR story      -> story spine check (context, takeaway,
                                                    continuity, consistency); run before voicing
    python3 engine/kit.py EPISODE_DIR manifest   -> lines.json for the voice Action
    python3 engine/kit.py EPISODE_DIR audio      -> audio.wav, timings.json, captions_en-AU.srt
    python3 engine/kit.py EPISODE_DIR frames 0 5 12.5 ...   -> stills/ (check them)
    python3 engine/kit.py EPISODE_DIR sheet      -> stills/contact.png (every 4 s)
    python3 engine/kit.py EPISODE_DIR keys 3 40 66 ...   -> stills/keys.png (key beats in one image)
    python3 engine/kit.py EPISODE_DIR video      -> short.mp4
    python3 engine/kit.py EPISODE_DIR cut        -> cut.mp4, captions_cut_en-AU.srt
    python3 engine/kit.py EPISODE_DIR check      -> stats: wpm, sentence lengths, loop, loudness
"""
import importlib.util
import json
import math
import os
import re
import subprocess
import sys
import wave
from dataclasses import dataclass

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cairo  # noqa: E402
import numpy as np  # noqa: E402

import render as R  # noqa: E402
import rig14 as rig  # noqa: E402
import narration as Nn  # noqa: E402

rig.install()
R._rig = rig
W, H, FPS = R.W, R.H, R.FPS
SR = 24000
STRIP_H = 190
STRIP_Y = H - STRIP_H
IDLE0 = 1.0
INK, OCHRE, SAGE = R.INK, R.OCHRE, R.SAGE
VOICES = {"N": "narrator", "B": "bramble", "O": "otto", "I": "ivy"}


@dataclass
class Line:
    who: str
    text: str
    gap: float = 0.8          # silence after this line
    min_start: float = 0.0    # optional earliest start (s)


# ---------------------------------------------------------------- episode loading
class Episode:
    def __init__(self, folder):
        self.dir = os.path.abspath(folder)
        spec = importlib.util.spec_from_file_location("episode", os.path.join(self.dir, "episode.py"))
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)
        self.lines = self.m.LINES
        self.rows, self.clips, self.total = None, None, None

    def path(self, *p):
        return os.path.join(self.dir, *p)

    def load_voices(self):
        clips = []
        for i, ln in enumerate(self.lines):
            p = self.path("lines", f"l{i:02d}.wav")
            if not os.path.exists(p):
                raise SystemExit(f"missing voice file {p}: run the voice Action first")
            clips.append(load_wav(p))
        self.clips = clips
        rows, s = [], 0.35
        for i, (ln, clip) in enumerate(zip(self.lines, clips)):
            if i:
                s = max(rows[-1]["end"] + self.lines[i - 1].gap, ln.min_start)
            e = s + len(clip) / SR
            rows.append({"who": ln.who, "text": ln.text, "start": round(s, 3), "end": round(e, 3)})
        self.rows = rows
        self.total = rows[-1]["end"] + self.lines[-1].gap + 1.0
        return self

    def s(self, i):
        return self.rows[i]["start"]

    def e(self, i):
        return self.rows[i]["end"]


def load_wav(path):
    with wave.open(path) as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        raw, width = w.readframes(w.getnframes()), w.getsampwidth()
    d = (np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0) if width == 2 \
        else np.frombuffer(raw, dtype=np.float32)
    if ch > 1:
        d = d.reshape(-1, ch).mean(axis=1)
    if sr != SR:
        x = np.linspace(0, 1, int(len(d) * SR / sr))
        d = np.interp(x, np.linspace(0, 1, len(d)), d).astype(np.float32)
    nz = np.where(np.abs(d) > 0.005)[0]
    d = d[max(0, nz[0] - 240): nz[-1] + 1200]
    return d / (np.max(np.abs(d)) + 1e-9) * 0.8


def prog(t, a, b):
    return R.prog(t, a, b)


def ease(x):
    return R.ease(x)


# ---------------------------------------------------------------- cues
RING = "#F2C85B"


def ring(ctx, cx, cy, rx, ry, a):
    if a <= 0:
        return
    g = cairo.RadialGradient(0, 0, 0, 0, 0, 1)
    g.add_color_stop_rgba(0.0, 0.12, 0.10, 0.08, 0.0)
    g.add_color_stop_rgba(0.80, 0.12, 0.10, 0.08, 0.0)
    g.add_color_stop_rgba(1.0, 0.12, 0.10, 0.08, 0.34 * a)
    k = 1.35
    g.set_matrix(cairo.Matrix(1 / (rx * k), 0, 0, 1 / (ry * k), -cx / (rx * k), -cy / (ry * k)))
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, H)
    ctx.fill()
    br = 1.0 + 0.035 * math.sin(R.NOW[0] * 3.2)
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(rx * 1.08 * br, ry * 1.08 * br)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_line_width(9)
    ctx.set_source_rgba(*R.rgb(RING), 0.95 * a)
    ctx.stroke()


def lens(ctx, surf, tx, ty, lx, ly, r, mag, a):
    if a <= 0:
        return
    rr, gg, bb = R.rgb(RING)
    rad = r * (0.7 + 0.3 * a)
    ang = math.atan2(ty - ly, tx - lx)
    ctx.set_line_width(5)
    ctx.set_source_rgba(rr, gg, bb, 0.95 * a)
    ctx.move_to(lx + (rad + 12) * math.cos(ang), ly + (rad + 12) * math.sin(ang))
    ctx.line_to(tx - 46 * math.cos(ang), ty - 46 * math.sin(ang))
    ctx.stroke()
    ctx.set_line_width(6)
    ctx.arc(tx, ty, 42 + 3 * math.sin(R.NOW[0] * 3.2), 0, 2 * math.pi)
    ctx.stroke()
    hang = ang + math.pi + 0.5
    ctx.set_line_width(30 * (0.7 + 0.3 * a))
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    R.src(ctx, "#9A7350", a)
    ctx.move_to(lx + rad * math.cos(hang), ly + rad * math.sin(hang))
    ctx.line_to(lx + (rad + 120) * math.cos(hang), ly + (rad + 120) * math.sin(hang))
    ctx.stroke()
    ctx.save()
    ctx.arc(lx, ly, rad, 0, 2 * math.pi)
    ctx.clip()
    pat = cairo.SurfacePattern(surf)
    m = cairo.Matrix()
    m.translate(tx, ty)
    m.scale(1 / mag, 1 / mag)
    m.translate(-lx, -ly)
    pat.set_matrix(m)
    pat.set_filter(cairo.FILTER_GOOD)
    ctx.set_source(pat)
    ctx.paint_with_alpha(a)
    ctx.set_source_rgba(1, 1, 1, 0.12 * a)
    ctx.arc(lx - rad * 0.35, ly - rad * 0.35, rad * 0.45, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()
    ctx.set_line_width(22)
    R.src(ctx, "#9A7350", a)
    ctx.arc(lx, ly, rad, 0, 2 * math.pi)
    ctx.stroke()


def zoom_at(cues, T):
    for c in cues:
        if c[0] == "zoom" and c[1] <= T <= c[2]:
            k = ease((T - c[1]) / 1.1) * (1 - ease((T - (c[2] - 1.1)) / 1.1))
            return 1 + (c[5] - 1) * k, c[3], c[4]
    return None


# ---------------------------------------------------------------- caption strip
SPEAKER = {"N": ("#E9DCC4", INK), "B": ("#8B6A4E", "#FFFFFF"), "O": (OCHRE, "#FFFFFF"), "I": (SAGE, "#FFFFFF")}


def face_icon(ctx, x, y, who):
    bg, _ = SPEAKER[who]
    if who in ("O", "I"):
        for ex in (-22, 22):
            R.src(ctx, bg)
            ctx.move_to(x + ex - 12, y - 30)
            ctx.line_to(x + ex * 1.3, y - 62)
            ctx.line_to(x + ex + 12, y - 34)
            ctx.close_path()
            ctx.fill()
    if who == "B":
        for k in range(7):
            a = math.pi + k * math.pi / 6
            R.src(ctx, "#6F5440")
            ctx.move_to(x + 38 * math.cos(a - 0.2), y + 38 * math.sin(a - 0.2))
            ctx.line_to(x + 58 * math.cos(a), y + 58 * math.sin(a))
            ctx.line_to(x + 38 * math.cos(a + 0.2), y + 38 * math.sin(a + 0.2))
            ctx.fill()
    R.ellipse(ctx, x, y, 44, 44, bg)
    R.ellipse(ctx, x - 14, y - 6, 5, 6, INK)
    R.ellipse(ctx, x + 14, y - 6, 5, 6, INK)
    ctx.set_line_width(4)
    R.src(ctx, INK)
    ctx.arc(x, y + 6, 13, 0.3, math.pi - 0.3)
    ctx.stroke()


def word_times(r):
    words = r["text"].split()
    weights = [max(2, len(w.strip(".,!?:"))) + 2 for w in words]
    tot = sum(weights)
    out, acc = [], r["start"]
    for w, k in zip(words, weights):
        out.append((w, acc))
        acc += (r["end"] - r["start"]) * k / tot
    return out


def _wrap(ctx, words, maxw):
    lines, cur = [], []
    for w in words:
        test = " ".join([x for x, _ in cur] + [w[0]])
        if cur and ctx.text_extents(test)[2] > maxw:
            lines.append(cur)
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(cur)
    return lines


def caption_strip(ctx, ep, T):
    R.src(ctx, "#F3EBDD")
    ctx.rectangle(0, STRIP_Y, W, STRIP_H)
    ctx.fill()
    R.src(ctx, "#E3D6BF")
    ctx.rectangle(0, STRIP_Y, W, 4)
    ctx.fill()
    hidden = getattr(ep.m, "STRIP_HIDDEN", set())
    for i, r in enumerate(ep.rows):
        if i in hidden:
            continue
        a = prog(T, r["start"] - 0.25, r["start"]) * (1 - prog(T, r["end"] + 0.5, r["end"] + 0.8))
        if a <= 0:
            continue
        y0 = STRIP_Y + 14
        bh = STRIP_H - 30
        R.rrect(ctx, 20, y0, W - 40, bh, 34, "#FFFFFF", 0.96 * a)
        face_icon(ctx, 96, y0 + bh / 2, r["who"])
        ctx.select_font_face(R.FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        size = 50
        ctx.set_font_size(size)
        lines = _wrap(ctx, word_times(r), W - 220)
        if len(lines) > 2:
            size = 42
            ctx.set_font_size(size)
            lines = _wrap(ctx, word_times(r), W - 220)
        lh = size * 1.2
        ytop = y0 + bh / 2 - lh * (len(lines) - 1) / 2
        for li, ln in enumerate(lines):
            full = " ".join(w for w, _ in ln)
            x = 170 + (W - 210 - ctx.text_extents(full)[2]) / 2
            for w, ts in ln:
                said = T >= ts
                ctx.set_source_rgba(*R.rgb(INK if said else "#A99D90"), a)
                ext = ctx.text_extents(w + " ")
                ctx.move_to(x, ytop + li * lh + size * 0.35)
                ctx.show_text(w + " ")
                if said and T < ts + 0.6:
                    ctx.set_source_rgba(*R.rgb(RING), a * (1 - (T - ts) / 0.6))
                    ctx.rectangle(x, ytop + li * lh + size * 0.5, ext[4] - 12, 6)
                    ctx.fill()
                x += ext[4]
        return


# ---------------------------------------------------------------- signature beats
def case_open(ctx, surf, T, y=880):
    p = prog(T, 0.15, 1.75)
    if p <= 0 or p >= 1:
        return
    lx = -260 + (W + 520) * ease(p)
    ly = y + 60 * math.sin(p * math.pi)
    r = 150
    ctx.save()
    ctx.arc(lx, ly, r, 0, 2 * math.pi)
    ctx.clip()
    pat = cairo.SurfacePattern(surf)
    m = cairo.Matrix()
    m.translate(lx, ly)
    m.scale(1 / 1.35, 1 / 1.35)
    m.translate(-lx, -ly)
    pat.set_matrix(m)
    ctx.set_source(pat)
    ctx.paint()
    ctx.restore()
    ctx.set_line_width(22)
    R.src(ctx, "#9A7350")
    ctx.arc(lx, ly, r, 0, 2 * math.pi)
    ctx.stroke()
    ctx.set_line_width(30)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(lx + r * 0.72, ly + r * 0.72)
    ctx.line_to(lx + r * 1.5, ly + r * 1.5)
    ctx.stroke()


def paw_print(ctx, x, y, s, col, a):
    R.ellipse(ctx, x, y + 10 * s, 24 * s, 20 * s, col, a)
    for dx, dy in ((-24, -18), (-8, -30), (8, -30), (24, -18)):
        R.ellipse(ctx, x + dx * s, y + dy * s, 8 * s, 10 * s, col, a)


def stamp(ctx, ep, T, cy=540):
    i = getattr(ep.m, "STAMP_LINE", None)
    if i is None:
        return
    s0 = ep.s(i) - 0.15
    a = prog(T, s0, s0 + 0.35) * (1 - prog(T, ep.e(i) + 1.4, ep.e(i) + 1.9))
    if a <= 0:
        return
    k = 1.35 - 0.35 * ease(prog(T, s0, s0 + 0.35))
    col = "#B4473E"
    ctx.save()
    ctx.translate(W / 2, cy)
    ctx.rotate(-0.08)
    ctx.scale(k, k)
    R.rrect(ctx, -340, -95, 680, 190, 30, "#FFFFFF", 0.9 * a)
    ctx.set_line_width(10)
    ctx.set_source_rgba(*R.rgb(col), 0.9 * a)
    ctx.new_sub_path()
    rr = 30
    for px, py, a0 in ((340 - rr, -95 + rr, -math.pi / 2), (340 - rr, 95 - rr, 0),
                       (-340 + rr, 95 - rr, math.pi / 2), (-340 + rr, -95 + rr, math.pi)):
        ctx.arc(px, py, rr, a0, a0 + math.pi / 2)
    ctx.close_path()
    ctx.stroke()
    paw_print(ctx, -255, 6, 1.5, col, 0.9 * a)
    R.text(ctx, "Case solved!", 55, 0, 64, col, a)
    ctx.restore()


# ---------------------------------------------------------------- frame
_SURF = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)


def draw_frame(ctx, ep, T, cue_list):
    R.NOW[0] = T + IDLE0
    rig.POSE.clear()
    rig.POSE.update(ep.m.poses(ep, T))
    rig.TALK = [(r["start"], r["end"], r["who"]) for r in ep.rows if r["who"] in ("O", "I", "B")]
    rig.TIME_OFFSET = IDLE0
    sc = cairo.Context(_SURF)
    sc.set_operator(cairo.OPERATOR_SOURCE)
    R.src(sc, R.CREAM)
    sc.paint()
    sc.set_operator(cairo.OPERATOR_OVER)
    ep.m.scene(sc, ep, T)
    _SURF.flush()
    R.src(ctx, R.CREAM)
    ctx.paint()
    ctx.save()
    zm = zoom_at(cue_list, T)
    if zm:
        z, cx, cy = zm
        ctx.translate(cx, cy)
        ctx.scale(z, z)
        ctx.translate(-cx, -cy)
    ctx.set_source_surface(_SURF, 0, 0)
    ctx.get_source().set_filter(cairo.FILTER_GOOD)
    ctx.paint()
    ctx.restore()
    R.NOW[0] = T + IDLE0
    for c in cue_list:
        if not (c[1] <= T <= c[2]) or c[0] == "zoom":
            continue
        a = prog(T, c[1], c[1] + 0.4) * (1 - prog(T, c[2] - 0.35, c[2]))
        if c[0] == "ring":
            ring(ctx, *c[3:7], a)
        elif c[0] == "lens":
            lens(ctx, _SURF, *c[3:9], a)
    if hasattr(ep.m, "cards"):
        ep.m.cards(ctx, ep, T)
    if getattr(ep.m, "OPEN_LINE", 0) is not None:
        case_open(ctx, _SURF, T)
    stamp(ctx, ep, T)
    caption_strip(ctx, ep, T)


_FRAME0 = {}


def draw_with_loop(ctx, ep, T, cue_list):
    """Draw frame T; over the last 1.4 s dissolve into frame 1 so the Short loops cleanly."""
    draw_frame(ctx, ep, T, cue_list)
    a = prog(T, ep.total - 1.4, ep.total - 0.6)
    if a > 0:
        if id(ep) not in _FRAME0:
            f0 = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
            draw_frame(cairo.Context(f0), ep, 0.0, cue_list)
            _FRAME0[id(ep)] = f0
        ctx.save()
        ctx.identity_matrix()
        ctx.set_source_surface(_FRAME0[id(ep)], 0, 0)
        ctx.paint_with_alpha(a)
        ctx.restore()


def cue_list(ep):
    cl = sorted(ep.m.cues(ep), key=lambda c: c[1])
    i = getattr(ep.m, "STAMP_LINE", None)
    if i is not None:   # one focus at a time: cues end before the stamp
        st = ep.s(i) - 0.35
        cl = [c[:2] + (min(c[2], st),) + c[3:] if c[1] < st < c[2] else c for c in cl]
    zs = [c[1] for c in cl if c[0] == "zoom"]
    for a, b in zip(zs, zs[1:]):
        if b - a < 18:
            print(f"WARNING: zooms at {a:.1f}s and {b:.1f}s are less than 18 s apart")
    return cl


# ---------------------------------------------------------------- audio
def bell(freq, dur=1.2, amp=0.5):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    env = np.exp(-tt * 3.2) * np.minimum(1, tt / 0.01)
    w = np.sin(2 * np.pi * freq * tt) + 0.3 * np.sin(2 * np.pi * freq * 2.01 * tt) * np.exp(-tt * 6)
    return (amp * env * w).astype(np.float32)


def thud():
    n = int(0.35 * SR)
    tt = np.arange(n) / SR
    return (0.5 * np.sin(2 * np.pi * (110 - 60 * tt) * tt) * np.exp(-tt * 14)).astype(np.float32)


def look_chime():
    out = np.zeros(int(0.9 * SR), dtype=np.float32)
    for f0, at in ((1318.5, 0.0), (1760.0, 0.11)):
        n = len(out) - int(at * SR)
        tt = np.arange(n) / SR
        tone = np.sin(2 * np.pi * f0 * tt) * np.minimum(tt / 0.006, 1) * np.exp(-tt / 0.22)
        out[int(at * SR):] += (tone * 0.045).astype(np.float32)
    return out


MOTIF = [523.25, 659.25, 783.99, 880.0, 783.99, 659.25, 587.33, 523.25]
FOLEY = {"pop": Nn.pop, "snip": Nn.snip, "step": Nn.step, "whoosh": Nn.whoosh,
         "chime": lambda: Nn.chime(880, 1.2), "thud": thud}


def build_audio(ep):
    n = int(ep.total * SR)
    voice = np.zeros(n, dtype=np.float32)
    for r, clip in zip(ep.rows, ep.clips):
        a = int(r["start"] * SR)
        b = min(n, a + len(clip))
        voice[a:b] += clip[: b - a]
    sfx = np.zeros(n, dtype=np.float32)

    def put(clip, at, gain=1.0):
        a = int(at * SR)
        b = min(n, a + len(clip))
        if 0 <= a < n:
            sfx[a:b] += clip[: b - a].astype(np.float32) * gain

    if getattr(ep.m, "OPEN_LINE", 0) is not None:
        put(bell(783.99, 1.0, 0.22), 0.12)
        put(bell(1046.5, 1.4, 0.22), 0.42)
        put(Nn.whoosh(1.0), 0.2, 0.5)
    for kind, at in (ep.m.foley(ep) if hasattr(ep.m, "foley") else []):
        put(FOLEY[kind](), at, 0.8)
    i = getattr(ep.m, "STAMP_LINE", None)
    if i is not None:
        put(thud(), ep.s(i) - 0.12)
        put(bell(1174.66, 1.6, 0.18), ep.s(i) + 0.1)
    ch = look_chime()
    for c in cue_list(ep):
        put(ch, c[1] + 0.05)
    music = np.zeros(n, dtype=np.float32)
    note_i = 0
    child = getattr(ep.m, "CHILD_TURN", None)
    for k in range(len(ep.rows) - 1):
        g0, g1 = ep.rows[k]["end"] + 0.25, ep.rows[k + 1]["start"] - 0.35
        if k == child or g1 - g0 < 1.6:
            continue
        tt = g0
        while tt + 0.5 < g1:
            note = bell(MOTIF[note_i % len(MOTIF)] / 2, 1.0, 0.16)
            a = int(tt * SR)
            b = min(int(g1 * SR), a + len(note))
            music[a:b] += note[: b - a]
            note_i += 1
            tt += 0.5
        a, b = int((g1 - 0.4) * SR), int(g1 * SR)
        music[a:b] *= np.linspace(1, 0, b - a)
    mix = np.clip(voice + sfx + music, -1, 1)
    f = int(0.3 * SR)
    mix[-f:] *= np.linspace(1, 0, f)
    raw = ep.path("audio_raw.wav")
    with wave.open(raw, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw, "-af",
                    "highpass=f=70,loudnorm=I=-14:TP=-1.5:LRA=9", "-ar", "48000", ep.path("audio.wav")],
                   check=True)
    json.dump(ep.rows, open(ep.path("timings.json"), "w"), indent=1)
    write_srt(ep.rows, ep.path("captions_en-AU.srt"))


def ts(x):
    ms = int(round(x * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write_srt(rows, path):
    names = {"N": "", "B": "BRAMBLE: ", "O": "OTTO: ", "I": "IVY: "}
    with open(path, "w") as fh:
        for k, r in enumerate(rows, 1):
            fh.write(f"{k}\n{ts(r['start'])} --> {ts(r['end'] + 0.4)}\n{names[r['who']]}{r['text']}\n\n")


# ---------------------------------------------------------------- outputs
def render_video(ep):
    cl = cue_list(ep)
    n = int(ep.total * FPS)
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", ep.path("audio.wav"),
         "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-shortest", "-movflags", "+faststart",
         ep.path("short.mp4")], stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    for i in range(n):
        ctx.identity_matrix()
        draw_with_loop(ctx, ep, i / FPS, cl)
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
    ff.stdin.close()
    ff.wait()


def stills(ep, times):
    os.makedirs(ep.path("stills"), exist_ok=True)
    cl = cue_list(ep)
    out = []
    for t in times:
        surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
        ctx = cairo.Context(surf)
        draw_with_loop(ctx, ep, float(t), cl)
        p = ep.path("stills", f"f{float(t):06.1f}.png")
        surf.write_to_png(p)
        out.append(p)
    return out


def sheet(ep, step=4.0):
    ts_ = list(np.arange(0, ep.total, step))
    paths = stills(ep, ts_)
    from PIL import Image
    cols = 8
    rows = math.ceil(len(paths) / cols)
    s = Image.new("RGB", (cols * 216, rows * 384), "white")
    for k, p in enumerate(paths):
        s.paste(Image.open(p).resize((216, 384)), ((k % cols) * 216, (k // cols) * 384))
    s.save(ep.path("stills", "contact.png"))
    print(ep.path("stills", "contact.png"))


def keyframes(ep, times):
    """Several moments in ONE small image (540x960 each, up to 4 across): one Read instead of many."""
    paths = stills(ep, times)
    from PIL import Image
    cols = min(4, len(paths))
    rows = math.ceil(len(paths) / cols)
    s = Image.new("RGB", (cols * 540, rows * 960), "white")
    for k, p in enumerate(paths):
        s.paste(Image.open(p).resize((540, 960)), ((k % cols) * 540, (k // cols) * 960))
    out = ep.path("stills", "keys.png")
    s.save(out)
    print(out)


def build_cut(ep):
    XF = 0.4
    segs = []
    for a, b in ep.m.CUT:
        s = 0.0 if a == 0 else ep.s(a) - 0.4
        e = ep.total if b == len(ep.rows) - 1 else ep.e(b) + 0.8
        segs.append((s, e))
    parts = []
    for k, (a, b) in enumerate(segs):
        out = ep.path(f"cut_part{k}.mp4")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", ep.path("short.mp4"),
                        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", out],
                       check=True)
        parts.append((out, b - a))
    inputs, fc, vlab, alab = [], [], "[0:v]", "[0:a]"
    for p, _ in parts:
        inputs += ["-i", p]
    off = parts[0][1] - XF
    for k in range(1, len(parts)):
        fc.append(f"{vlab}[{k}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[v{k}]")
        fc.append(f"{alab}[{k}:a]acrossfade=d={XF}[a{k}]")
        vlab, alab = f"[v{k}]", f"[a{k}]"
        off += parts[k][1] - XF
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc), "-map", vlab,
                    "-map", alab, "-c:v", "libx264", "-crf", "22", "-pix_fmt", "yuv420p", "-c:a", "aac",
                    "-b:a", "160k", "-movflags", "+faststart", ep.path("cut.mp4")], check=True)
    for p, _ in parts:
        os.remove(p)
    rows, base = [], 0.0
    for a, b in segs:
        for r in ep.rows:
            if r["start"] >= a and r["end"] <= b:
                rows.append(dict(r, start=r["start"] - a + base, end=r["end"] - a + base))
        base += (b - a) - XF
    write_srt(rows, ep.path("captions_cut_en-AU.srt"))
    print("cut length", round(base + XF, 1))


def check(ep):
    words = lambda s: re.findall(r"[A-Za-z']+|\d+", s)
    rates = [len(words(r["text"])) / max(0.1, r["end"] - r["start"]) * 60 for r in ep.rows]
    sents = [s for r in ep.rows for s in re.split(r"(?<=[.!?:])\s+", r["text"]) if words(s)]
    lens_ = [len(words(s)) for s in sents]
    tot_w = sum(len(words(r["text"])) for r in ep.rows)
    sp = sum(r["end"] - r["start"] for r in ep.rows)
    print(f"total {ep.total:.1f}s | words/min within lines {tot_w / sp * 60:.0f} (max {max(rates):.0f})"
          f" | sentences avg {sum(lens_) / len(lens_):.1f} words, longest {max(lens_)}")
    for r, x in zip(ep.rows, rates):
        if x > 170:
            print(f"  fast line ({x:.0f} wpm): {r['text']}")
    for s in sents:
        if len(words(s)) > 10:
            print(f"  long sentence ({len(words(s))} words): {s}")
    if os.path.exists(ep.path("short.mp4")):
        a, b = stills(ep, [0.0, ep.total - 1.0 / FPS])
        from PIL import Image, ImageChops
        print("loop frame matches frame 1:", ImageChops.difference(Image.open(a), Image.open(b)).getbbox() is None)
        out = subprocess.run(["ffmpeg", "-i", ep.path("short.mp4"), "-af", "loudnorm=print_format=summary",
                              "-f", "null", "-"], capture_output=True, text=True).stderr
        m = re.search(r"Input Integrated:\s+(-?[\d.]+)", out)
        print("loudness LUFS:", m.group(1) if m else "?")


LOCKED = ["Case open!", "Today's case:", "Let's not guess. Let's test.", "Pause and think.",
          "Case solved!", "Remember.", "Say it with me.", "Try it at home.", "Next case:"]


def _norm(s):
    return " ".join(re.findall(r"[a-z0-9']+", s.lower()))


def story(ep):
    """Story spine check (PRODUCTION_SPEC.md): context, takeaway, continuity, consistency.

    Runs from LINES alone, so run it straight after writing the script, before voices.
    Needs CASE_NO, RULE and SETTING in episode.py. Returns the number of failures."""
    m, L = ep.m, ep.lines
    texts = [ln.text for ln in L]
    fails = []

    def item(group, ok, msg):
        print(f"  [{'PASS' if ok else 'FAIL'}] {group}: {msg}")
        if not ok:
            fails.append(msg)

    def first(prefix, start=0):
        return next((i for i in range(start, len(L)) if texts[i].startswith(prefix)), None)

    rule = getattr(m, "RULE", "")
    case_no = getattr(m, "CASE_NO", None)
    setting = getattr(m, "SETTING", "")
    limit = getattr(m, "SENTENCE_LIMIT", 8)
    words = lambda s: re.findall(r"[A-Za-z']+|\d+", s)
    print("story spine check")
    # 1. context
    t_case = first("Today's case:")
    t_test = first("Let's not guess. Let's test.")
    item("context", texts[0] == "Case open!", "line 0 is \"Case open!\"")
    item("context", len(L) > 2 and any(L[i].who in "OI" for i in (1, 2)),
         "Otto or Ivy states the problem as a fairness or feelings hook in lines 1 to 2")
    item("context", t_case is not None and t_case <= 4, "\"Today's case: ...\" title by line 4")
    item("context", bool(setting), f"SETTING named for the upload copy ({setting or 'missing'})")
    item("context", t_case is not None and t_test is not None and any(
        re.search(r"\b(like|means)\b", texts[i], re.I) for i in range(t_case, t_test)),
        "the word taught is explained (\"... means ...\") or tied to an everyday example (\"It's like ...\") before the test")
    # 2. takeaway
    n_rule = _norm(rule)
    item("takeaway", bool(rule) and len(words(rule)) <= limit,
         f"one RULE sentence within {limit} words: \"{rule}\"")
    hits = [i for i, t in enumerate(texts) if n_rule and n_rule in _norm(t)]
    item("takeaway", len(hits) >= 3, f"RULE said word for word at least 3 times (lines {hits})")
    stamp = getattr(m, "STAMP_LINE", None)
    item("takeaway", bool(hits) and stamp is not None and hits[0] < stamp,
         "RULE is first said while proving it, before \"Case solved!\"")
    r_rem, r_say = first("Remember."), first("Say it with me.")
    item("takeaway", r_rem is not None and n_rule and n_rule in _norm(texts[r_rem]), "\"Remember. <RULE>\"")
    item("takeaway", r_say is not None and n_rule and n_rule in _norm(texts[r_say]), "\"Say it with me. <RULE>\"")
    item("takeaway", getattr(m, "CHILD_TURN", None) == r_say and r_say is not None and L[r_say].gap >= 2.0,
         "CHILD_TURN is the \"Say it with me\" line with at least 2 s for the child")
    # 3. continuity
    folder = os.path.basename(ep.dir)
    num = int(re.match(r"ep(\d+)", folder).group(1)) if re.match(r"ep(\d+)", folder) else None
    item("continuity", case_no is not None and case_no == num, f"CASE_NO {case_no} matches the folder {folder}")
    item("continuity", texts[-1].startswith("Next case:"), "last line is the \"Next case: ...\" teaser")
    if num:
        prev = [d for d in sorted(os.listdir(os.path.dirname(ep.dir))) if d.startswith(f"ep{num - 1:03d}_")]
        pj = os.path.join(os.path.dirname(ep.dir), prev[0], "lines.json") if prev else None
        if pj and os.path.exists(pj):
            tease = json.load(open(pj))["lines"][-1]["text"]
            title = texts[t_case] if t_case is not None else ""
            stop = {"next", "case", "today's", "a", "the", "to", "at", "of", "and", "one", "time", "is", "are"}
            shared = (set(_norm(tease).split()) & set(_norm(title).split())) - stop
            print(f"         last teaser: \"{tease}\" | this title: \"{title}\"")
            item("continuity", bool(shared), "this case picks up the previous episode's teaser (shared words: "
                 f"{', '.join(sorted(shared)) or 'none'}); if the order changed, say so in the report")
    # 4. consistency
    pos = [first(p) for p in LOCKED]
    item("consistency", all(p is not None for p in pos),
         "locked phrases present: " + ", ".join(p for p, i in zip(LOCKED, pos) if i is None) if None in pos
         else "all locked phrases present")
    order = [i for i in pos if i is not None]
    item("consistency", order == sorted(order), "locked phrases in the fixed beat order")
    t_think = first("Pause and think.")
    item("consistency", t_think is not None and L[t_think].gap >= 5.0, "5 s silence after \"Pause and think.\"")
    asks = [i for i in range(len(L)) if L[i].who == "B" and re.search(r"\b(point|show)\b", texts[i], re.I)]
    item("consistency", bool(asks) and t_think is not None and asks[0] < t_think and L[asks[0]].gap >= 3.0,
         "Bramble asks the viewer to point or show, before the A or B, then 3 to 5 s silence")
    item("consistency", stamp is not None and texts[stamp] == "Case solved!", "STAMP_LINE is \"Case solved!\"")
    print(f"story spine: {len(fails)} to fix" if fails else "story spine: all clear")
    return len(fails)


def manifest(ep):
    keep = {}
    if os.path.exists(ep.path("lines.json")):   # keep "wpm" targets for lines whose text is unchanged
        keep = {(x["who"], x["text"]): x["wpm"] for x in json.load(open(ep.path("lines.json")))["lines"] if "wpm" in x}
    data = {"lines": [{"i": i, "who": ln.who, "voice": VOICES[ln.who], "text": ln.text}
                      for i, ln in enumerate(ep.lines)]}
    for x in data["lines"]:
        if (x["who"], x["text"]) in keep:
            x["wpm"] = keep[(x["who"], x["text"])]
    json.dump(data, open(ep.path("lines.json"), "w"), indent=1)
    print(ep.path("lines.json"))


def main():
    ep = Episode(sys.argv[1])
    mode = sys.argv[2]
    if mode == "manifest":
        if story(ep):
            print("manifest written anyway; fix the story spine before voicing")
        return manifest(ep)
    if mode == "story":
        sys.exit(1 if story(ep) else 0)
    ep.load_voices()
    if mode == "audio":
        build_audio(ep)
        for r in ep.rows:
            print(f"{r['start']:6.2f}-{r['end']:6.2f} {r['who']} {r['text']}")
        print("TOTAL", round(ep.total, 2))
    elif mode == "frames":
        print("\n".join(stills(ep, sys.argv[3:])))
    elif mode == "keys":
        keyframes(ep, sys.argv[3:])
    elif mode == "sheet":
        sheet(ep, float(sys.argv[3]) if len(sys.argv) > 3 else 4.0)
    elif mode == "video":
        render_video(ep)
        print(ep.path("short.mp4"))
    elif mode == "cut":
        build_cut(ep)
    elif mode == "check":
        check(ep)
        story(ep)


if __name__ == "__main__":
    main()
