"""End-to-end test episode: Australian voices, render, cut and an unlisted test upload."""
import math

import render as R
import scenes13 as S
import scenes14 as S14
from kit import Line, prog, W

LINES = [
    Line("B", "Case open!", gap=0.4),
    Line("O", "Hey! That's not fair!", gap=0.6),
    Line("N", "Is this really half?", gap=1.0),
    Line("B", "Can you point to the middle?", gap=4.0),
    Line("B", "Case solved!", gap=1.5),
    Line("N", "Next case: four pieces. Are they fair?", gap=0.6),
]
STRIP_HIDDEN = {4}
CHILD_TURN = None
STAMP_LINE = 4
OPEN_LINE = 0
CUT = [(0, 2), (4, 5)]


def cues(ep):
    return [("ring", 0.0, ep.e(2) + 0.5, 540, 600, 300, 180),
            ("lens", ep.s(3), ep.e(3) + 3.5, 540, 700, 820, 300, 120, 2.0)]


def foley(ep):
    return [("pop", ep.s(2) - 0.2)]


def poses(ep, T):
    P = {"O": {"expr": "sad"}, "I": {}, "B": {"face": 1, "expr": "think"}}
    if ep.s(3) - 0.2 <= T <= ep.e(3) + 3.5:
        P["B"].update(point=(540, 700), amt=prog(T, ep.s(3), ep.s(3) + 0.5))
    if T >= ep.s(4) - 0.2:
        P["O"]["expr"] = P["B"]["expr"] = "happy"
    return P


def scene(ctx, ep, T):
    # the v13/v14 wide garden, lifted so feet sit above the caption strip
    ctx.save()
    ctx.translate(0, -S14.SHIFT)
    S14.scene_open(ctx, T)
    ctx.restore()
