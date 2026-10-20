"""Make the Australian voices for every episode that has lines.json but no lines/ yet.

Runs in the GitHub Action (secret GOOGLE_TTS_API_KEY). Google Cloud Text-to-Speech,
Chirp 3 HD voices, en-AU. Writes episodes/<ep>/lines/lNN.wav (24 kHz, 16-bit mono).

    python3 tools/tts_google.py            # all pending episodes
    python3 tools/tts_google.py --samples  # one sample per cast voice -> voice_samples/
"""
import base64
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
            synth(ln["text"], name, rate, f"{ep}/lines/l{ln['i']:02d}.wav")
            print(ep, ln["i"], name, ln["text"])
        json.dump({k: v[0] for k, v in voices.items()}, open(f"{ep}/voices_used.json", "w"), indent=1)


if __name__ == "__main__":
    main()
