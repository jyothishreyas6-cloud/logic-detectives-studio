"""Livelier character rigs for Logic Detectives (used from v10 on).

Drop-in replacements for render.bramble, render.squirrel and render.garden_people.
They read two module-level tables, set once per frame by the video script:

  POSE[who] -> dict for 'O' (Otto), 'I' (Ivy), 'B' (Bramble):
      point=(x, y)  target in the scene's own drawing coordinates
      amt=0..1      how far the arm is raised toward the target
      dx            sideways walk offset;  walk=phase (radians) while walking
      jump          pixels off the ground;  scratch=0..1 (paw to head)
      face=+1/-1    facing override;  tilt  extra head tilt
  TALK -> list of (start, end, who) for the spoken lines; mouths move during them.

Idle life is always on: weight shifting, head sway, ear and nose twitches, spine ripple.
"""
import math

import cairo

import render as R
from render import (ellipse, rrect, src, NOW, SPINE, SPINE_D, FACE, INK, SQ, SQ_T, BELLY,
                    OCHRE, SAGE, blink, breathe, shadow)

POSE = {}
TALK = []
TIME_OFFSET = 1.0   # NOW = video time + this (see v6.IDLE0)


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


def _paw(ctx, x, y, r, ang=None, finger=0.0):
    ellipse(ctx, x, y, r, r * 0.88, SPINE_D if r < 0 else None or SPINE_D)
    if finger > 0 and ang is not None:
        ctx.set_line_width(r * 0.7)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        src(ctx, SPINE_D)
        ctx.move_to(x, y)
        ctx.line_to(x + math.cos(ang) * r * 1.9 * finger, y + math.sin(ang) * r * 1.9 * finger)
        ctx.stroke()


# ---------------------------------------------------------------- Bramble
def bramble(ctx, x, y, s, f=1, glass=True, paw_up=0.0, look=0.0, step=None):
    P = POSE.get("B", {})
    f = P.get("face", f)
    x += P.get("dx", 0.0) + 2.5 * s * math.sin(NOW[0] * 0.8)
    y -= P.get("jump", 0.0)
    if P.get("walk") is not None:
        step = P["walk"]
    talk = talking("B")
    nod = 2.2 * s * math.sin(NOW[0] * 9.0) * talk
    shadow(ctx, x + 20 * s * f, y + P.get("jump", 0.0), 95 * s)
    br = breathe(0.3)
    st = math.sin(step) if step is not None else 0.0
    ellipse(ctx, x - 25 * s * f + 6 * s * st, y - 4 * s - 7 * s * max(0, -st), 16 * s, 7 * s, SPINE_D)
    ellipse(ctx, x + 30 * s * f - 6 * s * st, y - 4 * s - 7 * s * max(0, st), 16 * s, 7 * s, SPINE_D)
    cx, cy, rx, ry = x - 5 * s * f, y - 55 * s * br, 72 * s, 56 * s * br
    src(ctx, SPINE_D)
    for i in range(15):
        ang = math.radians(150 + i * 15) if f > 0 else math.radians(30 - i * 15)
        ln = 20 * s * (1 + 0.12 * math.sin(NOW[0] * 2.2 + i * 0.8))   # spines ripple
        da = math.radians(9)
        ctx.move_to(cx + rx * math.cos(ang - da), cy + ry * math.sin(ang - da))
        ctx.line_to(cx + (rx + ln) * math.cos(ang), cy + (ry + ln) * math.sin(ang))
        ctx.line_to(cx + rx * math.cos(ang + da), cy + ry * math.sin(ang + da))
        ctx.close_path()
        ctx.fill()
    ellipse(ctx, cx, cy, rx, ry, SPINE)
    fy = y + nod
    ellipse(ctx, x + 38 * s * f, fy - 42 * s, 42 * s, 36 * s, FACE)
    ellipse(ctx, x + 72 * s * f, fy - 52 * s, 30 * s, 22 * s, FACE)
    sniff = 1 + 0.15 * max(0.0, math.sin(NOW[0] * 6.0)) * (1 if (NOW[0] % 5.0) < 1.2 else 0)
    ellipse(ctx, x + 99 * s * f, fy - 56 * s, 8 * s * sniff, 7 * s * sniff, INK)
    bl = blink(0.0)
    ex, ey = x + (62 + 2.5 * look) * s * f, fy - 70 * s
    ellipse(ctx, ex, ey, 6.5 * s, 7.5 * s * bl, INK)
    if bl > 0.5:
        ellipse(ctx, ex + 2 * s * f, ey - 2.5 * s, 2.2 * s, 2.2 * s, "#FFFFFF")
    ellipse(ctx, x + 40 * s * f, fy - 56 * s, 9 * s, 6 * s, "#E8C2A8", 0.6)
    if talk > 0:
        ellipse(ctx, x + 82 * s * f, fy - 43 * s, 7 * s, (1.5 + 5 * talk) * s, "#5A2E28")
    else:
        ctx.set_line_width(2.6 * s)
        src(ctx, INK)
        if f > 0:
            ctx.arc(x + 80 * s, fy - 47 * s, 9 * s, math.radians(30), math.radians(140))
        else:
            ctx.arc(x - 80 * s, fy - 47 * s, 9 * s, math.radians(40), math.radians(150))
        ctx.stroke()
    # arm: points at a target when posed, otherwise the classic pose
    amt = P.get("amt", 0.0) if P.get("point") else 0.0
    sx, sy = x + 55 * s * f, y - 36 * s
    if glass:
        hx0, hy0 = x + 70 * s * f, y - 28 * s - paw_up * 40 * s
        gx0, gy0 = x + 118 * s * f, y - 95 * s - paw_up * 40 * s
        if amt > 0:
            hx1, hy1, ang = _aim(sx, sy, *P["point"], 42 * s)
            gx1, gy1, _ = _aim(sx, sy, *P["point"], 92 * s)
            hx, hy = hx0 + (hx1 - hx0) * amt, hy0 + (hy1 - hy0) * amt
            gx, gy = gx0 + (gx1 - gx0) * amt, gy0 + (gy1 - gy0) * amt
        else:
            hx, hy, gx, gy = hx0, hy0, gx0, gy0
        ctx.set_line_width(7 * s)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        src(ctx, "#9A7350")
        ctx.move_to(hx, hy)
        d = math.hypot(gx - hx, gy - hy) or 1
        ctx.line_to(gx - (gx - hx) / d * 22 * s, gy - (gy - hy) / d * 22 * s)
        ctx.stroke()
        ellipse(ctx, gx, gy, 22 * s, 22 * s, "#DCEAF0", 0.55)
        ctx.set_line_width(5 * s)
        src(ctx, "#9A7350")
        ctx.arc(gx, gy, 22 * s, 0, 2 * math.pi)
        ctx.stroke()
        ellipse(ctx, hx, hy, 9 * s, 8 * s, SPINE_D)
    else:
        hx0, hy0 = x + 66 * s * f, y - 24 * s - paw_up * 30 * s
        if amt > 0:
            side = 1 if P["point"][0] >= cx else -1
            bsx, bsy = cx + 42 * s * side, cy - 28 * s
            reach = 84 * s * (1 + 0.05 * math.sin(NOW[0] * 5.0))
            hx1, hy1, ang = _aim(bsx, bsy, *P["point"], reach)
            hx, hy = hx0 + (hx1 - hx0) * amt, hy0 + (hy1 - hy0) * amt
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.set_line_width(17 * s)
            src(ctx, "#5E4632")
            ctx.move_to(bsx, bsy)
            ctx.line_to(hx, hy)
            ctx.stroke()
            ctx.set_line_width(12 * s)
            src(ctx, SPINE_D)
            ctx.move_to(bsx, bsy)
            ctx.line_to(hx, hy)
            ctx.stroke()
            _paw(ctx, hx, hy, 10 * s, ang, finger=amt)
        else:
            ellipse(ctx, hx0, hy0, 10 * s, 8 * s, SPINE_D)


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
    shadow(ctx, x, y0, 60 * s * (1 - min(0.4, jump / (200 * s))))
    swish = 0.07 + (0.12 if jump > 0 else 0.0) + 0.05 * talk
    ctx.save()
    ctx.translate(x - 20 * s * f, y - 30 * s)
    ctx.rotate(swish * math.sin(NOW[0] * (1.5 + 4 * (jump > 0)) + seed) * f)
    ctx.translate(-(x - 20 * s * f), -(y - 30 * s))
    src(ctx, SQ_T)
    ctx.move_to(x - 30 * s * f, y - 20 * s)
    ctx.curve_to(x - 120 * s * f, y - 40 * s, x - 130 * s * f, y - 190 * s, x - 70 * s * f, y - 230 * s)
    ctx.curve_to(x - 20 * s * f, y - 260 * s, x - 10 * s * f, y - 200 * s, x - 50 * s * f, y - 190 * s)
    ctx.curve_to(x - 80 * s * f, y - 150 * s, x - 60 * s * f, y - 60 * s, x - 10 * s * f, y - 40 * s)
    ctx.close_path()
    ctx.fill()
    ctx.restore()
    st = math.sin(walk) if walk is not None else 0.0
    ellipse(ctx, x - 12 * s * f + 5 * s * st, y - 4 * s - 8 * s * max(0, -st), 18 * s, 7 * s, SQ)
    ellipse(ctx, x + 18 * s * f - 5 * s * st, y - 4 * s - 8 * s * max(0, st), 18 * s, 7 * s, SQ)
    ellipse(ctx, x, y - 62 * s, 42 * s, 60 * s * breathe(seed), SQ)
    ellipse(ctx, x + 10 * s * f, y - 54 * s, 24 * s, 40 * s, BELLY)
    # arm
    sx, sy = x + 10 * s * f, y - 88 * s
    ax0 = x + (18 + 30 * arm_out) * s * f
    ay0 = y - (70 + 45 * arm_up) * s
    ax, ay, ang = ax0, ay0, None
    amt = P.get("amt", 0.0) if P.get("point") else 0.0
    if amt > 0:
        ax1, ay1, ang = _aim(sx, sy, *P["point"], 86 * s * (1 + 0.05 * math.sin(NOW[0] * 5.0 + seed)))
        ax, ay = ax0 + (ax1 - ax0) * amt, ay0 + (ay1 - ay0) * amt
    sc = P.get("scratch", 0.0)
    if sc > 0:
        bx, by = x - 6 * s * f, y - 178 * s + 4 * s * math.sin(NOW[0] * 14)
        ax, ay = ax + (bx - ax) * sc, ay + (by - ay) * sc
    # head
    ctx.save()
    ctx.translate(x + 4 * s * f, y - 118 * s)
    ctx.rotate(tilt * f)
    hx, hy = 0, -32 * s
    twitch = 6 * s if ((NOW[0] + seed * 3.1) % 4.3) < 0.18 else 0.0
    src(ctx, SQ)
    for k, ex in enumerate((-18, 14)):
        tip = twitch if k == 1 else 0.0
        ctx.move_to(hx + (ex - 10) * s * f, hy - 22 * s)
        ctx.line_to(hx + (ex + 2) * s * f + tip * f, hy - 58 * s + tip)
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
    if talk > 0:
        ellipse(ctx, hx + 30 * s * f, hy + 17 * s, 5 * s, (1.2 + 4.5 * talk) * s, "#5A2E28")
    elif jump > 0 or P.get("amt", 0) > 0.5:
        ctx.set_line_width(2.2 * s)
        src(ctx, INK)
        ctx.arc(hx + 28 * s * f, hy + 13 * s, 5 * s, 0.2, math.pi - 0.2)
        ctx.stroke()
    ctx.restore()
    # arm (drawn after the head so a raised arm stays visible), outlined against the body
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    if amt > 0.05 or sc > 0.05:
        ctx.set_line_width(19 * s)
        src(ctx, "#8A4426")
        ctx.move_to(sx, sy)
        ctx.line_to(ax, ay)
        ctx.stroke()
    ctx.set_line_width(14 * s)
    src(ctx, SQ)
    ctx.move_to(sx, sy)
    ctx.line_to(ax, ay)
    ctx.stroke()
    # paw (with a pointing finger when aiming)
    ellipse(ctx, ax, ay, 9 * s, 8 * s, "#A9542F")
    if ang is not None and amt > 0.3:
        ctx.set_line_width(6 * s)
        src(ctx, "#A9542F")
        ctx.move_to(ax, ay)
        ctx.line_to(ax + math.cos(ang) * 15 * s * amt, ay + math.sin(ang) * 15 * s * amt)
        ctx.stroke()
    rrect(ctx, x - 34 * s, y - 122 * s, 70 * s, 18 * s, 8 * s, scarf)
    ctx.save()
    ctx.translate(x - 22 * s * f, y - 110 * s)
    ctx.rotate(0.25 * f + 0.15 * math.sin(NOW[0] * 1.7 + seed) + (0.3 if jump > 0 else 0))
    rrect(ctx, -8 * s, 0, 16 * s, 38 * s, 6 * s, scarf)
    ctx.restore()
    return ax, ay


# ---------------------------------------------------------------- garden people
def garden_people(ctx, t, ox, scene):
    """Ivy (kites) and Otto (scissors) behind the table. Otto's scissors follow his paw and,
    when he points, the blades aim straight at his target."""
    tilt = 0.0
    if scene == "c":
        tilt = 0.18 * math.sin(R.clamp((t - 0.5) / 2.5) * math.pi / 2) - 0.06 * math.sin(t * 0.8)
    R.kite(ctx, 300 + ox, 640 + 8 * math.sin(t * 0.9), 0.9, "#E7B98C", 0.06 * math.sin(t * 0.7), tail=False)
    R.kite(ctx, 470 + ox, 600 + 8 * math.sin(t * 0.8 + 1), 0.9, "#B9C9DE", -0.05 * math.sin(t * 0.6), tail=False)
    ax, ay = squirrel(ctx, 400 + ox, 1330, 1.25, SAGE, f=1, tilt=tilt, arm_up=1.0, arm_out=0.1, seed=0.7)
    ctx.set_line_width(2)
    src(ctx, "#7A6E62", 0.8)
    ctx.move_to(ax, ay)
    ctx.line_to(300 + ox, 720)
    ctx.move_to(ax, ay)
    ctx.line_to(470 + ox, 680)
    ctx.stroke()
    P = POSE.get("O", {})
    ax2, ay2 = squirrel(ctx, 1000 + ox, 1330, 1.25, OCHRE, f=-1, arm_up=0.3, arm_out=1.0, seed=2.0)
    if P.get("point") and P.get("amt", 0) > 0.05 and not P.get("no_scissors"):
        px, py = P["point"]
        rot = math.atan2(py - ay2, px - ax2)
        snip = 0.15 + 0.45 * abs(math.sin(t * 2.6))
    else:
        rot = math.pi + 0.3
        snip = 0.35
    if not P.get("scratch"):
        R.scissors(ctx, ax2, ay2, 0.9, snip, rot=rot)


def install():
    R.bramble = bramble
    R.squirrel = squirrel
    R.garden_people = garden_people
