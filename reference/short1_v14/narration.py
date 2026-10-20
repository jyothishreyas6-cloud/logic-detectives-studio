"""Build the narration + soft pad audio for Short 1 'Is This Really Half?'.

Each line is spoken separately with espeak-ng and placed at its target time
(pushed later if the previous line runs long), then mixed over a quiet pad.
Writes audio.wav (75 s) and timings.json (actual start/end of each line).
"""
import json
import subprocess
import wave
import numpy as np

SR = 24000
LINE_DIR = "/mnt/user-data/uploads/Videos/Logic Detectives/kokoro/short1_lines"
TOTAL = 77.0

LINES = [
    (0.5, "Is this really half?"),
    (3.6, "Otto and Ivy have one ribbon, and two kites."),
    (7.4, "Otto wants to cut it in half, right here, at his mark."),
    (12.4, "But Ivy wonders."),
    (14.8, "If the mark is not in the middle, one tail will be longer."),
    (20.4, "Bramble says, let's not guess. Let's test."),
    (25.0, "What could we do?"),
    (28.6, "He brings one end to meet the other end."),
    (32.8, "Ends together."),
    (34.8, "And the fold shows the middle."),
    (40.4, "Look."),
    (41.8, "The fold is here."),
    (44.0, "Otto's mark is over there."),
    (48.4, "Otto cuts at the fold."),
    (50.8, "Now lay the pieces side by side."),
    (54.8, "Same length."),
    (58.4, "Two pieces, exactly the same size."),
    (62.0, "That is what half means."),
    (66.3, "And next door, Mabel's garden has four pieces."),
    (69.8, "Are they fair? That's our next case."),
    (74.6, "Is this really half?"),
]


def speak(i):
    """Load Kokoro (af_heart) line i, peak-normalised, silence trimmed."""
    with wave.open(f"{LINE_DIR}/line{i:02d}.wav") as w:
        assert w.getframerate() == SR, w.getframerate()
        raw = w.readframes(w.getnframes())
        width = w.getsampwidth()
    data = (np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0) if width == 2 \
        else np.frombuffer(raw, dtype=np.float32)
    nz = np.where(np.abs(data) > 0.005)[0]
    data = data[max(0, nz[0] - 240): nz[-1] + 1200] if len(nz) else data
    return data / (np.max(np.abs(data)) + 1e-9) * 0.8


def soft(x):
    """Gentle low-pass to take the edge off the synthetic voice."""
    k = np.ones(5) / 5
    return np.convolve(x, k, mode="same")


def pad_track(n):
    t = np.arange(n) / SR
    out = np.zeros(n, dtype=np.float32)
    # two slow alternating chords (C major add 9 and A minor 7), very quiet
    chords = [[130.81, 196.0, 261.63, 293.66], [110.0, 164.81, 220.0, 261.63]]
    seg = 8.0
    for i, start in enumerate(np.arange(0, TOTAL, seg)):
        freqs = chords[i % 2]
        a, b = int(start * SR), min(n, int((start + seg + 2) * SR))
        tt = t[a:b] - start
        env = np.clip(tt / 2.5, 0, 1) * np.clip((seg + 2 - tt) / 2.5, 0, 1)
        tone = sum(np.sin(2 * np.pi * f * tt) for f in freqs) / len(freqs)
        trem = 0.85 + 0.15 * np.sin(2 * np.pi * 0.2 * tt)
        out[a:b] += (tone * env * trem).astype(np.float32)
    return out * 0.035


def _env(n_s, attack, decay):
    t = np.arange(n_s) / SR
    return np.minimum(t / attack, 1.0) * np.exp(-t / decay)


def chime(f0=880.0, dur=1.6):
    n_s = int(dur * SR)
    t = np.arange(n_s) / SR
    tone = np.sin(2 * np.pi * f0 * t) + 0.5 * np.sin(2 * np.pi * f0 * 1.5 * t) + 0.25 * np.sin(2 * np.pi * f0 * 2 * t)
    return tone * _env(n_s, 0.01, 0.45) * 0.10


def snip():
    n_s = int(0.08 * SR)
    rng = np.random.default_rng(1)
    noise = rng.standard_normal(n_s)
    noise = np.diff(noise, prepend=0)  # brighter, scissor-like
    return noise * _env(n_s, 0.002, 0.018) * 0.12


def step():
    n_s = int(0.12 * SR)
    t = np.arange(n_s) / SR
    return np.sin(2 * np.pi * 110 * t) * _env(n_s, 0.004, 0.03) * 0.10


def whoosh(dur=1.4):
    n_s = int(dur * SR)
    rng = np.random.default_rng(2)
    noise = np.convolve(rng.standard_normal(n_s), np.ones(40) / 40, mode="same")
    env = np.sin(np.linspace(0, np.pi, n_s)) ** 2
    return noise * env * 0.12


def pop():
    n_s = int(0.15 * SR)
    t = np.arange(n_s) / SR
    f = 500 + 900 * t / 0.15
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n_s, 0.003, 0.04) * 0.08


def sfx_track(n):
    out = np.zeros(n, dtype=np.float32)

    def put(clip, at):
        a = int(at * SR)
        b = min(n, a + len(clip))
        out[a:b] += clip[: b - a].astype(np.float32)

    for k in range(9):                 # Bramble's soft footsteps walking in
        put(step(), 20.3 + k * 0.33)
    put(pop(), 25.0)                    # thought bubble
    put(chime(660, 1.4), 28.0)          # pause-and-think ring completes
    put(chime(880), 34.9)               # the fold shows the middle
    put(snip(), 48.9)
    put(snip(), 49.15)                  # snip snip
    put(chime(988), 54.9)               # same length
    put(whoosh(), 57.9)                 # kites lift
    put(chime(1175, 2.0), 62.1)         # that is what half means
    put(chime(784), 0.45)               # gentle hook
    return out


def main():
    n = int(TOTAL * SR)
    voice = np.zeros(n, dtype=np.float32)
    timings = []
    prev_end = 0.0
    for i, (target, text) in enumerate(LINES):
        clip = speak(i)
        start = max(target, prev_end + 0.35)
        a = int(start * SR)
        b = min(n, a + len(clip))
        voice[a:b] += clip[: b - a]
        end = b / SR
        timings.append({"text": text, "target": target, "start": round(start, 2), "end": round(end, 2)})
        prev_end = end
    mix = voice + pad_track(n) + sfx_track(n)
    # fade in/out
    f = int(0.4 * SR)
    mix[:f] *= np.linspace(0, 1, f)
    mix[-f:] *= np.linspace(1, 0, f)
    mix = np.clip(mix, -1, 1)
    with wave.open("audio.wav", "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    json.dump(timings, open("timings.json", "w"), indent=1)
    for tm in timings:
        drift = tm["start"] - tm["target"]
        print(f"{tm['start']:6.2f}-{tm['end']:6.2f} (+{drift:.2f}) {tm['text']}")


if __name__ == "__main__":
    main()
