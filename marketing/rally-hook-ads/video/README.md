# Generated concept videos

Fully generated 1080×1920 ad concepts: animated Rally screens, on-screen text, word-by-word captions and an AI voiceover. No filmed footage. They show how the hooks play; they aren't final ads. Styled in the Rally new look: navy and cream, sky accents, Bricolage Grotesque, Schibsted Grotesk and IBM Plex Mono.

| File | Hook | Length |
|---|---|---|
| `out/circumstance.mp4` | 1 · Circumstance | 34s |
| `out/realreason.mp4` | 2 · Real reason | 36s |
| `out/receipt.mp4` | 4 · Receipt (recreated screen recording) | 31s |
| `out/pricetag.mp4` | 3 · Price tag ($10 per confirmed booking, to be confirmed) | 25s |
| `out/proofdrop.mp4` | 5 · Proof drop (real numbers: 619 bookings in 2026, 9 brands) | 28s |
| `out/gametruck.mp4` | 1b · Circumstance, game truck operators | 40s |
| `out/lasertag.mp4` | 1c · Circumstance, laser tag (per-guest waivers) | 40s |
| `out/bubbles.mp4` | 1d · Circumstance, bubble shows (female voice `af_heart`) | 37s |

The proof drop count comes from the PA Fun Company Rally account: bookings confirmed, in progress or completed from Jan 1 to Oct 21, 2026.

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
