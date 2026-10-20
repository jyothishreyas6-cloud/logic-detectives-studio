"""3D-style character rigs for Logic Detectives (v11 on).

Same interface as rig.py (POSE, TALK, install), drawn with soft volume shading:
every body part is lit from the upper left (highlight, base colour, darker rim),
limbs are shaded tubes, and soft contact shadows sit under heads and bodies.

Gesture rules (Shreyas, 20/10/2026):
- Pointing uses an open paw (fingers together, thumb out) aimed at the target,
  or Bramble's magnifying glass. Never a single raised finger.
- Arms rise once, then hold still on the target. No repeated jabs, rubs or snips.
"""
import math

import cairo

import render as R
from render import NOW, SPINE, SPINE_D, FACE, INK, SQ, SQ_T, BELLY, OCHRE, SAGE, blink, breathe, rgb

POSE = {}
TALK = []
TIME_OFFSET = 1.0
LIGHT = (-0.38, -0.48)   # light comes from the upper left


def _mix(c, k):
    """k>0 lighten toward white, k<0 darken toward a warm shadow."""
    r, g, b = rgb(c)
    if k >= 0:
        return (r + (1 - r) * k, g + (1 - g) * k, b + (1 - b) * k)
    k = -k
    return (r * (1 - k) + 0.16 * k, g * (1 - k) + 0.10 * k, b * (1 - k) + 0.08 * k)


def ball(ctx, cx, cy, rx, ry, color, a=1.0, hi=0.30, lo=-0.28, f=1):
    """A shaded, rounded volume: highlight toward the light, darker toward the far rim."""
    lx, ly = LIGHT
    g = cairo.RadialGradient(cx + lx * rx * 0.55, cy + ly * ry * 0.55, 0, cx, cy, max(rx, ry) * 1.05)
    for stop, k in ((0.0, hi), (0.45, hi * 0.25), (0.78, 0.0), (1.0, lo)):
        r, gg, b = _mix(color, k)
        g.add_color_stop_rgba(stop, r, gg, b, a)
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(rx, ry)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()
    ctx.set_source(g)
    ctx.fill()


def gloss(ctx, x, y, r, a=0.55):
    """Small soft specular spot."""
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, 1, 1, 1, a)
    g.add_color_stop_rgba(1, 1, 1, 1, 0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()


def soft_shadow(ctx, x, y, rx, ry, a=0.22):
    g = cairo.RadialGradient(x, y, 0, x, y, 1)
    g.add_color_stop_rgba(0, 0.12, 0.08, 0.05, a)
    g.add_color_stop_rgba(1, 0.12, 0.08, 0.05, 0)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(rx, ry)
    ctx.set_source(cairo.RadialGradient(0, 0, 0, 0, 0, 1))
    pat = cairo.RadialGradient(0, 0, 0, 0, 0, 1)
    pat.add_color_stop_rgba(0, 0.12, 0.08, 0.05, a)
    pat.add_color_stop_rgba(1, 0.12, 0.08, 0.05, 0)
    ctx.set_source(pat)
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()


def ground_shadow(ctx, x, y, w):
    soft_shadow(ctx, x, y + 2, w * 1.1, w * 0.2, 0.28)


def tube(ctx, x0, y0, x1, y1, w, color):
    """A shaded limb: dark underside, base, light top edge."""
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ang = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(ang), math.cos(ang)
    if ny < 0:                      # make (nx, ny) point downward (away from the light)
        nx, ny = -nx, -ny
    for off, k, lw in ((0.18, -0.35, 1.0), (0.0, 0.0, 0.78), (-0.22, 0.32, 0.30)):
        r, g, b = _mix(color, k)
        ctx.set_source_rgb(r, g, b)
        ctx.set_line_width(w * lw)
        ctx.move_to(x0 + nx * w * off, y0 + ny * w * off)
        ctx.line_to(x1 + nx * w * off, y1 + ny * w * off)
        ctx.stroke()


def open_paw(ctx, x, y, r, ang, color):
    """Open paw, fingers together, thumb out: a friendly 'look here' gesture."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    # palm and fingers as one rounded mitten pointing along +x
    ball(ctx, r * 0.55, 0, r * 1.35, r * 0.78, color, hi=0.28, lo=-0.3)
    # finger grooves (three soft lines across the tip, so it reads as four fingers together)
    rr, gg, bb = _mix(color, -0.4)
    ctx.set_source_rgba(rr, gg, bb, 0.55)
    ctx.set_line_width(r * 0.09)
    for k in (-0.32, 0.0, 0.32):
        ctx.move_to(r * 1.25, k * r * 0.95)
        ctx.line_to(r * 1.82, k * r * 0.7)
        ctx.stroke()
    # thumb on the upper side
    ctx.save()
    ctx.translate(r * 0.25, -r * 0.7)
    ctx.rotate(-0.55)
    ball(ctx, r * 0.35, 0, r * 0.55, r * 0.3, color, hi=0.3, lo=-0.3)
    ctx.restore()
    ctx.restore()


def talking(who):
    t = NOW[0] - TIME_OFFSET
    for s, e, w in TALK:
        if w == who and s <= t <= e:
            return 0.35 + 0.65 * abs(math.sin(t * 13.0))
    return 0.0


def _aim(sx, sy, px, py, length):
    dx, dy = px - sx, py - sy
    d = math.hypot(dx, dy) or 1.0
    return sx + dx / d * length, sy + dy / d * length, math.atan2(dy, dx)


MAX_UP = math.radians(48)   # an arm never rises steeper than this above horizontal


def _aim_arm(sx, sy, px, py, length, side=0):
    """Like _aim, but a raised arm stays on a diagonal (never straight up), so the open paw
    reads as 'look over there'."""
    ang = math.atan2(py - sy, px - sx)
    up = -ang if ang < 0 else 0.0          # elevation above horizontal, toward the right
    if ang < 0:
        right = math.cos(ang) >= 0 if side == 0 else side > 0
        elev = min(math.atan2(sy - py, abs(px - sx) + 1e-6), MAX_UP)
        ang = -elev if right else -(math.pi - elev)
    return sx + math.cos(ang) * length, sy + math.sin(ang) * length, ang


def _eye(ctx, x, y, rx, ry, bl, f):
    ball(ctx, x, y, rx, ry * bl, INK, hi=0.18, lo=-0.1)
    if bl > 0.5:
        gloss(ctx, x - rx * 0.3 * f, y - ry * 0.38, rx * 0.55, 0.95)
        ctx.set_source_rgba(1, 1, 1, 0.95)
        ctx.arc(x - rx * 0.25 * f, y - ry * 0.35, rx * 0.26, 0, 2 * math.pi)
        ctx.fill()


# ---------------------------------------------------------------- Bramble
def bramble(ctx, x, y, s, f=1, glass=True, paw_up=0.0, look=0.0, step=None):
    P = POSE.get("B", {})
    f = P.get("face", f)
    glass = P.get("glass", glass)
    x += P.get("dx", 0.0) + 2.5 * s * math.sin(NOW[0] * 0.8)
    y -= P.get("jump", 0.0)
    if P.get("walk") is not None:
        step = P["walk"]
    talk = talking("B")
    nod = 2.2 * s * math.sin(NOW[0] * 9.0) * talk
    ground_shadow(ctx, x + 10 * s * f, y + P.get("jump", 0.0), 95 * s)
    br = breathe(0.3)
    st = math.sin(step) if step is not None else 0.0
    ball(ctx, x - 25 * s * f + 6 * s * st, y - 4 * s - 7 * s * max(0, -st), 17 * s, 8 * s, SPINE_D)
    ball(ctx, x + 30 * s * f - 6 * s * st, y - 4 * s - 7 * s * max(0, st), 17 * s, 8 * s, SPINE_D)
    cx, cy, rx, ry = x - 5 * s * f, y - 55 * s * br, 72 * s, 56 * s * br
    # spines: two staggered rows, each spine shaded from dark root to a lighter tip
    for row, (rk, lnk, off) in enumerate(((1.0, 1.0, 0.0), (0.92, 0.75, 7.5))):
        for i in range(15):
            a0 = 150 + i * 15 + off
            ang = math.radians(a0) if f > 0 else math.radians(180 - a0)
            ln = 21 * s * lnk * (1 + 0.12 * math.sin(NOW[0] * 2.2 + i * 0.8 + row))
            da = math.radians(8)
            bx0, by0 = cx + rx * rk * math.cos(ang), cy + ry * rk * math.sin(ang)
            tx, ty = cx + (rx * rk + ln) * math.cos(ang), cy + (ry * rk + ln) * math.sin(ang)
            g = cairo.LinearGradient(bx0, by0, tx, ty)
            r0, g0, b0 = _mix(SPINE_D, -0.35 if row == 0 else -0.2)
            r1, g1, b1 = _mix(SPINE, 0.22)
            g.add_color_stop_rgb(0, r0, g0, b0)
            g.add_color_stop_rgb(1, r1, g1, b1)
            ctx.set_source(g)
            ctx.move_to(cx + rx * rk * math.cos(ang - da), cy + ry * rk * math.sin(ang - da))
            ctx.line_to(tx, ty)
            ctx.line_to(cx + rx * rk * math.cos(ang + da), cy + ry * rk * math.sin(ang + da))
            ctx.close_path()
            ctx.fill()
    ball(ctx, cx, cy, rx, ry, SPINE, hi=0.22, lo=-0.32)
    if not glass and paw_up > 0.05 and not (P.get("point") and P.get("amt", 0) > 0):
        tube(ctx, cx + 30 * s * f, cy - 35 * s, x + 66 * s * f, y - 24 * s - paw_up * 41 * s, 15 * s, SPINE_D)
    fy = y + nod
    # face: soft occlusion where it meets the body, then shaded muzzle
    soft_shadow(ctx, x + 30 * s * f, fy - 30 * s, 46 * s, 30 * s, 0.25)
    ball(ctx, x + 38 * s * f, fy - 42 * s, 42 * s, 36 * s, FACE, hi=0.35, lo=-0.22)
    ball(ctx, x + 72 * s * f, fy - 52 * s, 30 * s, 22 * s, FACE, hi=0.35, lo=-0.2)
    sniff = 1 + 0.15 * max(0.0, math.sin(NOW[0] * 6.0)) * (1 if (NOW[0] % 5.0) < 1.2 else 0)
    ball(ctx, x + 99 * s * f, fy - 56 * s, 8.5 * s * sniff, 7.5 * s * sniff, INK, hi=0.25)
    gloss(ctx, x + 97 * s * f, fy - 59 * s, 3 * s, 0.7)
    _eye(ctx, x + (62 + 2.5 * look) * s * f, fy - 70 * s, 6.8 * s, 7.8 * s, blink(0.0), f)
    R.ellipse(ctx, x + 40 * s * f, fy - 56 * s, 9 * s, 6 * s, "#E8B49A", 0.55)
    if talk > 0:
        ball(ctx, x + 82 * s * f, fy - 43 * s, 7 * s, (1.5 + 5 * talk) * s, "#5A2E28", hi=0.1)
    else:
        ctx.set_line_width(2.6 * s)
        R.src(ctx, INK)
        if f > 0:
            ctx.arc(x + 80 * s, fy - 47 * s, 9 * s, math.radians(30), math.radians(140))
        else:
            ctx.arc(x - 80 * s, fy - 47 * s, 9 * s, math.radians(40), math.radians(150))
        ctx.stroke()
    # arm: rises once to the target, then holds still
    amt = P.get("amt", 0.0) if P.get("point") else 0.0
    sx, sy = x + 55 * s * f, y - 36 * s
    if glass:
        hx0, hy0 = x + 70 * s * f, y - 28 * s - paw_up * 40 * s
        gx0, gy0 = x + 118 * s * f, y - 95 * s - paw_up * 40 * s
        if amt > 0:
            hx1, hy1, _ = _aim(sx, sy, *P["point"], 46 * s)
            gx1, gy1, _ = _aim(sx, sy, *P["point"], 100 * s)
            hx, hy = hx0 + (hx1 - hx0) * amt, hy0 + (hy1 - hy0) * amt
            gx, gy = gx0 + (gx1 - gx0) * amt, gy0 + (gy1 - gy0) * amt
        else:
            hx, hy, gx, gy = hx0, hy0, gx0, gy0
        d = math.hypot(gx - hx, gy - hy) or 1
        tube(ctx, hx, hy, gx - (gx - hx) / d * 22 * s, gy - (gy - hy) / d * 22 * s, 8 * s, "#9A7350")
        g = cairo.RadialGradient(gx - 7 * s, gy - 8 * s, 0, gx, gy, 22 * s)
        g.add_color_stop_rgba(0, 1, 1, 1, 0.75)
        g.add_color_stop_rgba(0.5, 0.86, 0.92, 0.95, 0.5)
        g.add_color_stop_rgba(1, 0.70, 0.80, 0.86, 0.6)
        ctx.set_source(g)
        ctx.arc(gx, gy, 22 * s, 0, 2 * math.pi)
        ctx.fill()
        ctx.set_line_width(6 * s)
        R.src(ctx, "#8A6440")
        ctx.arc(gx, gy, 22 * s, 0, 2 * math.pi)
        ctx.stroke()
        ctx.set_line_width(2 * s)
        R.src(ctx, "#C9A273")
        ctx.arc(gx, gy, 20 * s, math.radians(200), math.radians(290))
        ctx.stroke()
        ball(ctx, hx, hy, 10 * s, 9 * s, SPINE_D)
    else:
        hx0, hy0 = x + 66 * s * f, y - 24 * s - paw_up * 30 * s
        if amt > 0:
            side = 1 if P["point"][0] >= cx else -1
            bsx, bsy = cx + 42 * s * side, cy - 28 * s
            hx1, hy1, ang = _aim_arm(bsx, bsy, *P["point"], 80 * s, side)
            hx, hy = hx0 + (hx1 - hx0) * amt, hy0 + (hy1 - hy0) * amt
            tube(ctx, bsx, bsy, hx, hy, 15 * s, SPINE_D)
            open_paw(ctx, hx, hy, 14 * s, ang, SPINE_D)
        else:
            if paw_up > 0.05:   # reaching up onto the table (arm drawn behind the face)
                hy0 = y - 24 * s - paw_up * 41 * s
            ball(ctx, hx0, hy0, 11 * s, 9 * s, SPINE_D)


# ---------------------------------------------------------------- squirrels
def squirrel(ctx, x, y, s, scarf, f=1, tilt=0.0, arm_up=0.0, arm_out=0.0, seed=0.0):
    who = "O" if scarf == OCHRE else ("I" if scarf == SAGE else "?")
    P = POSE.get(who, {})
    f = P.get("face", f)
    jump = P.get("jump", 0.0)
    x += P.get("dx", 0.0) + 3.0 * s * math.sin(NOW[0] * 1.1 + seed)
    y0 = y
    y -= jump
    walk = P.get("walk")
    talk = talking(who)
    tilt += (0.05 * math.sin(NOW[0] * 0.9 + seed) + 0.07 * math.sin(NOW[0] * 9.0) * talk
             + P.get("tilt", 0.0))
    ground_shadow(ctx, x, y0, 60 * s * (1 - min(0.4, jump / (200 * s))))
    swish = 0.07 + (0.12 if jump > 0 else 0.0) + 0.05 * talk
    # tail: shaded with a lighter, furry edge
    ctx.save()
    ctx.translate(x - 20 * s * f, y - 30 * s)
    ctx.rotate(swish * math.sin(NOW[0] * (1.5 + 4 * (jump > 0)) + seed) * f)
    ctx.translate(-(x - 20 * s * f), -(y - 30 * s))
    ctx.move_to(x - 30 * s * f, y - 20 * s)
    ctx.curve_to(x - 120 * s * f, y - 40 * s, x - 130 * s * f, y - 190 * s, x - 70 * s * f, y - 230 * s)
    ctx.curve_to(x - 20 * s * f, y - 260 * s, x - 10 * s * f, y - 200 * s, x - 50 * s * f, y - 190 * s)
    ctx.curve_to(x - 80 * s * f, y - 150 * s, x - 60 * s * f, y - 60 * s, x - 10 * s * f, y - 40 * s)
    ctx.close_path()
    tcx, tcy = x - 75 * s * f, y - 140 * s
    g = cairo.RadialGradient(tcx - 25 * s, tcy - 50 * s, 0, tcx, tcy, 140 * s)
    for stop, k in ((0, 0.32), (0.55, 0.0), (1, -0.32)):
        g.add_color_stop_rgb(stop, *_mix(SQ_T, k))
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.set_line_width(5 * s)
    ctx.set_source_rgba(*_mix(SQ_T, 0.4), 0.55)
    ctx.stroke()
    ctx.restore()
    st = math.sin(walk) if walk is not None else 0.0
    ball(ctx, x - 12 * s * f + 5 * s * st, y - 4 * s - 8 * s * max(0, -st), 19 * s, 8 * s, SQ)
    ball(ctx, x + 18 * s * f - 5 * s * st, y - 4 * s - 8 * s * max(0, st), 19 * s, 8 * s, SQ)
    ball(ctx, x, y - 62 * s, 42 * s, 60 * s * breathe(seed), SQ, hi=0.26, lo=-0.3)
    ball(ctx, x + 10 * s * f, y - 54 * s, 24 * s, 40 * s, BELLY, hi=0.3, lo=-0.15)
    # arm target: rises once, then holds
    sx, sy = x + 10 * s * f, y - 88 * s
    ax0 = x + (18 + 30 * arm_out) * s * f
    ay0 = y - (70 + 45 * arm_up) * s
    ax, ay, ang = ax0, ay0, None
    amt = P.get("amt", 0.0) if P.get("point") else 0.0
    if amt > 0:
        ax1, ay1, ang = _aim_arm(sx, sy, *P["point"], 84 * s)
        ax, ay = ax0 + (ax1 - ax0) * amt, ay0 + (ay1 - ay0) * amt
    sc = P.get("scratch", 0.0)
    if sc > 0:   # paw rests on the head (thinking), no rubbing
        bx, by = x - 6 * s * f, y - 176 * s
        ax, ay = ax + (bx - ax) * sc, ay + (by - ay) * sc
    # scarf knot sits under the head
    ball(ctx, x, y - 113 * s, 37 * s, 11 * s, scarf, hi=0.25, lo=-0.3)
    # head
    soft_shadow(ctx, x + 4 * s * f, y - 112 * s, 40 * s, 14 * s, 0.25)
    ctx.save()
    ctx.translate(x + 4 * s * f, y - 118 * s)
    ctx.rotate(tilt * f)
    hx, hy = 0, -32 * s
    twitch = 6 * s if ((NOW[0] + seed * 3.1) % 4.3) < 0.18 else 0.0
    for k, ex in enumerate((-18, 14)):
        tip = twitch if k == 1 else 0.0
        p0 = (hx + (ex - 10) * s * f, hy - 22 * s)
        p1 = (hx + (ex + 2) * s * f + tip * f, hy - 58 * s + tip)
        p2 = (hx + (ex + 12) * s * f, hy - 20 * s)
        g = cairo.LinearGradient(p1[0], p1[1], p0[0], p0[1])
        g.add_color_stop_rgb(0, *_mix(SQ, 0.18 if k else 0.05))
        g.add_color_stop_rgb(1, *_mix(SQ, -0.25))
        ctx.set_source(g)
        ctx.move_to(*p0)
        ctx.line_to(*p1)
        ctx.line_to(*p2)
        ctx.close_path()
        ctx.fill()
        # inner ear
        ctx.move_to(p0[0] * 0.55 + p2[0] * 0.45, p0[1] - 2 * s)
        ctx.line_to(p1[0] * 0.85 + (p0[0] + p2[0]) / 2 * 0.15, p1[1] + 12 * s)
        ctx.line_to(p2[0] * 0.65 + p0[0] * 0.35, p2[1] - 2 * s)
        ctx.close_path()
        ctx.set_source_rgba(*_mix("#E3A88A", 0), 0.7)
        ctx.fill()
    ball(ctx, hx, hy, 38 * s, 34 * s, SQ, hi=0.3, lo=-0.3)
    ball(ctx, hx + 26 * s * f, hy + 8 * s, 18 * s, 14 * s, BELLY, hi=0.35, lo=-0.15)
    ball(ctx, hx + 41 * s * f, hy + 4 * s, 5.5 * s, 5 * s, INK, hi=0.25)
    gloss(ctx, hx + 40 * s * f, hy + 2 * s, 2.2 * s, 0.7)
    _eye(ctx, hx + 14 * s * f, hy - 8 * s, 5.8 * s, 6.8 * s, blink(seed + 0.8), f)
    R.ellipse(ctx, hx + 10 * s * f, hy + 10 * s, 7 * s, 4.5 * s, "#E59C86", 0.45)
    if talk > 0:
        ball(ctx, hx + 30 * s * f, hy + 17 * s, 5 * s, (1.2 + 4.5 * talk) * s, "#5A2E28", hi=0.1)
    elif jump > 0 or amt > 0.5:
        ctx.set_line_width(2.2 * s)
        R.src(ctx, INK)
        ctx.arc(hx + 28 * s * f, hy + 13 * s, 5 * s, 0.2, math.pi - 0.2)
        ctx.stroke()
    ctx.restore()
    # scarf tail
    ctx.save()
    ctx.translate(x - 22 * s * f, y - 110 * s)
    ctx.rotate(0.25 * f + 0.15 * math.sin(NOW[0] * 1.7 + seed) + (0.3 if jump > 0 else 0))
    R.rrect(ctx, -8 * s, 0, 16 * s, 38 * s, 6 * s, scarf)
    R.rrect(ctx, 1 * s, 2 * s, 7 * s, 34 * s, 3 * s, "#000000", 0.14)
    R.rrect(ctx, -6 * s, 3 * s, 4 * s, 30 * s, 2 * s, "#FFFFFF", 0.18)
    ctx.restore()
    # arm last, so a raised arm is never hidden; shaded tube with an open paw
    tube(ctx, sx, sy, ax, ay, 15 * s, SQ)
    if ang is not None and amt > 0.3 and sc < 0.3 and not P.get("closed"):
        open_paw(ctx, ax, ay, 12 * s, ang, "#A9542F")
    else:
        ball(ctx, ax, ay, 9.5 * s, 8.5 * s, "#A9542F")
    return ax, ay


# ---------------------------------------------------------------- garden people
def garden_people(ctx, t, ox, scene):
    """Ivy (kites) and Otto (scissors) behind the table. Otto's scissors follow his paw and,
    when he points, the blades aim at the target and stay still (no snipping)."""
    tilt = 0.0
    if scene == "c":
        tilt = 0.18 * math.sin(R.clamp((t - 0.5) / 2.5) * math.pi / 2) - 0.06 * math.sin(t * 0.8)
    R.kite(ctx, 300 + ox, 640 + 8 * math.sin(t * 0.9), 0.9, "#E7B98C", 0.06 * math.sin(t * 0.7), tail=False)
    R.kite(ctx, 470 + ox, 600 + 8 * math.sin(t * 0.8 + 1), 0.9, "#B9C9DE", -0.05 * math.sin(t * 0.6), tail=False)
    PI = POSE.get("I", {})
    ax, ay = squirrel(ctx, 400 + ox, 1330, 1.25, SAGE, f=1, tilt=tilt, arm_up=1.0, arm_out=0.1, seed=0.7)
    # kite strings come from Ivy's other paw (on her chest) when she is pointing
    if PI.get("point") and PI.get("amt", 0) > 0.05:
        ax, ay = 400 + ox + 22 * 1.25, 1330 - 80 * 1.25
    ctx.set_line_width(2)
    R.src(ctx, "#7A6E62", 0.8)
    ctx.move_to(ax, ay)
    ctx.line_to(300 + ox, 720)
    ctx.move_to(ax, ay)
    ctx.line_to(470 + ox, 680)
    ctx.stroke()
    P = POSE.get("O", {})
    pointing = P.get("point") and P.get("amt", 0) > 0.05
    if pointing:   # Otto points with the scissors themselves, so draw his paw closed
        POSE["O"] = dict(P, closed=True)
    ax2, ay2 = squirrel(ctx, 1000 + ox, 1330, 1.25, OCHRE, f=-1, arm_up=0.3, arm_out=1.0, seed=2.0)
    if pointing:
        px, py = P["point"]
        rot = math.atan2(py - ay2, px - ax2)
        snip = 0.12
    else:
        rot = math.pi + 0.3
        snip = 0.3
    if not P.get("scratch"):
        R.scissors(ctx, ax2, ay2, 0.9, snip, rot=rot)


def install():
    R.bramble = bramble
    R.squirrel = squirrel
    R.garden_people = garden_people
