# Generated concept videos

Fully generated 1080×1920 ad concepts: animated Rally screens, on-screen text, word-by-word captions and an AI voiceover. No filmed footage. They show how the hooks play; they aren't final ads.

| File | Hook | Length |
|---|---|---|
| `out/circumstance.mp4` | 1 · Circumstance | 34s |
| `out/realreason.mp4` | 2 · Real reason | 36s |
| `out/receipt.mp4` | 4 · Receipt (recreated screen recording) | 31s |

The price tag and proof drop ads are left out until we have Rally's real price and real numbers.

## How it works

1. `ads.json` holds each spoken line. `tts.py` voices them with the open-source Kokoro TTS model (voice `am_michael`) and writes `out/<ad>.wav` plus a timeline of when each line starts and ends.
2. `render.html` builds each scene and animates it against that timeline. `render.mjs` steps through it frame by frame in headless Chromium and pipes the frames to ffmpeg with the voiceover.

## Re-running

```sh
pip install kokoro-onnx soundfile
# kokoro-v1.0.int8.onnx (saved as kokoro.onnx) and voices-v1.0.bin from
# https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
python3 tts.py /path/to/model_dir            # all ads, or name some: circumstance receipt
node render.mjs circumstance                 # needs playwright + ffmpeg
node render.mjs circumstance --still 12.5    # single PNG frame for checking layout
```

To swap in a real presenter later, replace the voiceover with the recorded audio and re-run `tts.py`'s timing step on it, or cut the filmed footage in over the generated scenes.
