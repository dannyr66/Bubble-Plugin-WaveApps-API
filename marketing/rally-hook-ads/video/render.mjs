// Render one ad to MP4: drive render.html frame by frame in headless Chromium,
// pipe the frames to ffmpeg and mux the voiceover from tts.py.
// Usage: node render.mjs <ad> [--fps 30] [--still 12.5]
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

// CommonJS require honors NODE_PATH, so a globally installed playwright also resolves
const { chromium } = createRequire(import.meta.url)('playwright');
const here = dirname(fileURLToPath(import.meta.url));
const ad = process.argv[2];
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? Number(process.argv[i + 1]) : d; };
const fps = arg('--fps', 30);
const still = arg('--still', null);
const tl = JSON.parse(readFileSync(join(here, 'out', `${ad}.timeline.json`), 'utf8'));

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 720, height: 1280 }, deviceScaleFactor: 1.5 });
await page.goto(pathToFileURL(join(here, 'render.html')).href);
await page.evaluate(() => document.fonts.ready);
await page.evaluate(t => window.boot(t), tl);

if (still != null) {
  await page.evaluate(t => window.render(t), still);
  await page.screenshot({ path: join(here, 'out', `${ad}-${still}.png`) });
  await browser.close();
  process.exit(0);
}

const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
  '-i', join(here, 'out', `${ad}.wav`), '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p',
  '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', join(here, 'out', `${ad}.mp4`)], { stdio: ['pipe', 'inherit', 'inherit'] });
const frames = Math.ceil(tl.total * fps);
for (let i = 0; i < frames; i++) {
  await page.evaluate(t => window.render(t), i / fps);
  const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % 150 === 0) console.log(`${ad}: frame ${i}/${frames}`);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await browser.close();
console.log(`${ad}: done (${tl.total}s)`);
