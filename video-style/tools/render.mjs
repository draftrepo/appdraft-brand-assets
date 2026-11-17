// Standalone preview renderer. Seeks animations exactly the way the skill's card.ts does
// (pause every animation, set currentTime, screenshot), but launches its own headless
// Chromium so it never touches the shared dev-browser server.
//   node render.mjs <file-or-url> <out_dir> <len_seconds> [--alpha] [--times 0.5,1.2] [--scale 2] [--w 1920 --h 1080] [--prefix name]
// Without --times it writes every frame (0000.png ...) at 30 fps, like card.ts.
import { createRequire } from "module";
import { mkdirSync } from "fs";
const require = createRequire(process.env.DEV_BROWSER ? process.env.DEV_BROWSER + "/" : process.env.HOME + "/.claude/skills/dev-browser/");
const { chromium } = require("playwright");
const [url, out, lenS, ...rest] = process.argv.slice(2);
const opt = (k, d) => { const i = rest.indexOf("--" + k); return i < 0 ? d : rest[i + 1]; };
const alpha = rest.includes("--alpha"), FPS = 30, LEN = parseFloat(lenS);
const W = parseInt(opt("w", "1920")), H = parseInt(opt("h", "1080")), prefix = opt("prefix", "");
mkdirSync(out, { recursive: true });
const browser = await chromium.launch();
const page = await (await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: parseFloat(opt("scale", "1")) })).newPage();
page.on("console", (m) => { if (m.type() === "error") console.error("page:", m.text()); });
await page.goto(url.startsWith("file:") || url.startsWith("http") ? url : "file://" + url);
await page.evaluate(() => document.fonts.ready);
await page.evaluate(() => Promise.all([...document.images].map((i) => i.complete ? 0 : new Promise((r) => { i.onload = i.onerror = r; }))));
await page.waitForTimeout(300);
const times = opt("times", null);
const list = times ? times.split(",").map(parseFloat) : Array.from({ length: Math.round(LEN * FPS) }, (_, i) => i / FPS);
for (const [i, t] of list.entries()) {
  await page.evaluate((t) => { for (const a of document.getAnimations()) { a.pause(); a.currentTime = t; } }, t * 1000);
  const name = times ? `${prefix}${t.toFixed(2)}s.png` : `${String(i).padStart(4, "0")}.png`;
  await page.screenshot({ path: `${out}/${name}`, omitBackground: alpha });
}
console.log("frames", list.length, out);
await browser.close();
