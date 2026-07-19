# 🎶 Bansuri Sur — Flute Sargam Trainer

A tiny, self-contained web app that listens to your flute through the microphone
and gives you a **green** light when your **Sa Re Ga Ma** swara is in tune and a
**red** light when it's off.

No build step, no server, no dependencies — it's a single HTML file.

## How to use

1. Open `index.html` in a modern browser (Chrome, Edge, Firefox, or Safari).
   - Easiest: double-click the file, or drag it into a browser tab.
   - For best mic support, serve it over `http://localhost` or `https://`
     (e.g. `python3 -m http.server` inside this folder, then open
     <http://localhost:8000/flute-lessons/>).
2. Pick **Your Sa** — the base note of your bansuri (a common C flute → `C4` or `C5`).
3. Choose a tuning tolerance (Strict / Normal / Beginner).
4. Click **▶ Start listening** and allow microphone access.
5. Play — the big light turns 🟢 when you hit a true swara, 🔴 when you're flat/sharp.

## Two modes

- **Free play** — hold any note; it tells you the nearest swara (Sa, Re, Ga, Ma,
  Pa, Dha, Ni) and whether you're in tune, with a live ±50-cent needle.
- **Sargam lesson (Sa → Sa)** — it walks you through the ascending scale. Hold
  each highlighted swara steady until it locks green, then it advances to the next.
  Complete all eight (Sa Re Ga Ma Pa Dha Ni Sa′) to finish the lesson.

## How it works

- Uses the **Web Audio API** (`getUserMedia` + `AnalyserNode`) to capture mic audio.
- Detects pitch with an **autocorrelation** algorithm plus parabolic interpolation
  for sub-sample accuracy.
- Maps the detected frequency to the nearest sargam swara relative to your chosen
  Sa (shuddha / Bilawal-thaat swaras), and compares the deviation in **cents**
  against your tolerance to decide green vs. red.

## Privacy

Everything runs locally in your browser. Audio is analyzed in real time and
**never recorded, saved, or uploaded**.

## Notes

- Sargam here is relative to your selected Sa, so it works for any key of flute —
  just set **Your Sa** to match your instrument.
- Currently uses the seven shuddha (natural) swaras. Komal/tivra variants could be
  added later for full raga practice.
