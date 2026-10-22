"""Synthesize the voiceover for each ad and write a timeline the renderer follows.

Usage: python3 tts.py <kokoro_model_dir> [ad ...]
Writes out/<ad>.wav and out/<ad>.timeline.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

LEAD = 0.25   # silence before the first line
GAP = 0.30    # default pause between lines
TAIL = 2.4    # hold on the end card after the last line

here = Path(__file__).resolve().parent
cfg = json.loads((here / "ads.json").read_text())
model_dir = Path(sys.argv[1])
wanted = sys.argv[2:] or list(cfg["ads"])
kokoro = Kokoro(str(model_dir / "kokoro.onnx"), str(model_dir / "voices.bin"))

for key in wanted:
    ad = cfg["ads"][key]
    sr = 24000
    parts = [np.zeros(int(LEAD * sr), dtype=np.float32)]
    t = LEAD
    segments = []
    for seg in ad["segments"]:
        audio, sr = kokoro.create(seg.get("say", seg["cap"]), voice=ad.get("voice", cfg["voice"]), speed=cfg["speed"], lang="en-us")
        audio = np.asarray(audio, dtype=np.float32)
        # trim leading/trailing near-silence so caption timing tracks the words
        loud = np.where(np.abs(audio) > 0.01)[0]
        if len(loud):
            audio = audio[max(0, loud[0] - 240): loud[-1] + 2400]
        dur = len(audio) / sr
        segments.append({"id": seg["id"], "cap": seg["cap"], "s": round(t, 3), "e": round(t + dur, 3)})
        gap = seg.get("gap", GAP)
        parts += [audio, np.zeros(int(gap * sr), dtype=np.float32)]
        t += dur + gap
    parts.append(np.zeros(int(TAIL * sr), dtype=np.float32))
    total = t + TAIL
    out = here / "out"
    out.mkdir(exist_ok=True)
    sf.write(out / f"{key}.wav", np.concatenate(parts), sr)
    (out / f"{key}.timeline.json").write_text(json.dumps(
        {"ad": key, "title": ad["title"], "sticker": ad["sticker"], "total": round(total, 3), "segments": segments}, indent=2))
    print(f"{key}: {total:.1f}s, {len(segments)} lines")
