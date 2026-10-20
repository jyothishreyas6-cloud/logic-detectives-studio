"""Make the Australian voices for every episode that has lines.json but no lines/ yet.

Runs in the GitHub Action (secret GOOGLE_TTS_API_KEY). Google Cloud Text-to-Speech,
Chirp 3 HD voices, en-AU. Writes episodes/<ep>/lines/lNN.wav (24 kHz, 16-bit mono).

    python3 tools/tts_google.py            # all pending episodes
    python3 tools/tts_google.py --samples  # one sample per cast voice -> voice_samples/
"""
import base64
import re
import subprocess
import wave
import glob
import json
import os
import sys
import urllib.request

KEY = os.environ["GOOGLE_TTS_API_KEY"]
API = "https://texttospeech.googleapis.com/v1"
# role -> (preferred Chirp 3 HD voice names in order, speaking rate)
CAST = {
    "narrator": (["Sulafat", "Vindemiatrix", "Achernar", "Aoede"], 0.85),
    "bramble": (["Sadaltager", "Schedar", "Charon", "Iapetus"], 0.88),
    "otto": (["Puck", "Fenrir", "Achird"], 0.92),
    "ivy": (["Leda", "Kore", "Aoede", "Zephyr"], 0.9),
}


def call(path, body=None):
    req = urllib.request.Request(f"{API}/{path}{'&' if '?' in path else '?'}key={KEY}",
                                 data=json.dumps(body).encode() if body else None,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def pick_voices():
    names = {v["name"] for v in call("voices?languageCode=en-AU").get("voices", [])}
    chosen = {}
    for role, (prefs, rate) in CAST.items():
        for p in prefs:
            name = f"en-AU-Chirp3-HD-{p}"
            if name in names:
                chosen[role] = (name, rate)
                break
        else:
            raise SystemExit(f"no en-AU Chirp 3 HD voice found for {role}; available: {sorted(names)[:40]}")
    return chosen


def synth(text, voice, rate, out):
    body = {"input": {"text": text},
            "voice": {"languageCode": "en-AU", "name": voice},
            "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 24000, "speakingRate": rate}}
    try:
        data = call("text:synthesize", body)
    except urllib.error.HTTPError as e:   # some voices may not accept speakingRate
        if e.code == 400:
            body["audioConfig"].pop("speakingRate")
            data = call("text:synthesize", body)
        else:
            raise
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "wb") as fh:
        fh.write(base64.b64decode(data["audioContent"]))   # LINEAR16 comes with a WAV header


TARGET_WPM = {"narrator": 140, "bramble": 140, "otto": 155, "ivy": 150}


def speech_seconds(path):
    """Length of the speech without the leading and trailing silence."""
    with wave.open(path) as w:
        n, sr = w.getnframes(), w.getframerate()
        data = w.readframes(n)
    import array
    a = array.array("h", data)
    thr = 300
    idx = [i for i in range(0, len(a), 120) if abs(a[i]) > thr]
    if not idx:
        return n / sr
    return (idx[-1] - idx[0]) / sr


def slow_to_target(path, text, role, target=None):
    """Time-stretch (pitch kept) so the line is no faster than the target words per minute."""
    words = len(re.findall(r"[A-Za-z']+|\d+", text))
    dur = speech_seconds(path)
    wpm = words / max(dur, 0.2) * 60
    tgt = target or TARGET_WPM[role]
    if wpm <= tgt * 1.03:
        return wpm, wpm
    factor = max(0.6, tgt / wpm)
    tmp = path + ".tmp.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", path, "-filter:a", f"atempo={factor:.3f}",
                    "-ar", "24000", "-ac", "1", tmp], check=True)
    os.replace(tmp, path)
    return wpm, wpm * factor


def main():
    voices = pick_voices()
    print("cast:", voices)
    if "--samples" in sys.argv or not os.path.exists("voice_samples"):
        for role, (name, rate) in voices.items():
            synth(f"G'day! I'm the {role} of Logic Detectives. Let's not guess. Let's test.", name, rate,
                  f"voice_samples/{role}.wav")
        if "--samples" in sys.argv:
            return
    for lj in sorted(glob.glob("episodes/*/lines.json")):
        ep = os.path.dirname(lj)
        lines = json.load(open(lj))["lines"]
        todo = [ln for ln in lines if not os.path.exists(f"{ep}/lines/l{ln['i']:02d}.wav")]
        for ln in todo:
            name, rate = voices[ln["voice"]]
            rate = ln.get("rate", rate)
            out = f"{ep}/lines/l{ln['i']:02d}.wav"
            synth(ln["text"], name, rate, out)
            before, after = slow_to_target(out, ln["text"], ln["voice"], ln.get("wpm"))
            print(ep, ln["i"], name, f"{before:.0f}->{after:.0f} wpm", ln["text"])
        json.dump({k: v[0] for k, v in voices.items()}, open(f"{ep}/voices_used.json", "w"), indent=1)


if __name__ == "__main__":
    main()
