// Render any flagship template frame by frame to PNGs. card.ts, generalised:
//   - ALPHA=1 keeps the page background transparent (callouts, the stage cover)
//   - waits for every <img> (the from / to stills) before the first frame
//   - STILL=1 writes one frame (0000.png) and stops: the stage cover
// Run from the dev-browser directory, as card.ts is (demo-video gfx does this for you):
//   CARD_URL="file://<skill>/gfx/part.html?<query>" LEN=3.8 OUT=<dir> [W=1600 H=900] [ALPHA=1] [STILL=1] [CARD_PAGE=gfx] npx tsx tmp/gfx.ts
import { connect } from "@/client.js";
import { mkdirSync, rmSync } from "fs";

const OUT = process.env.OUT!, LEN = parseFloat(process.env.LEN || "1"), FPS = 30;
const NAME = process.env.CARD_PAGE || "gfx", ALPHA = !!process.env.ALPHA;
rmSync(OUT, { recursive: true, force: true }); mkdirSync(OUT, { recursive: true });
const client = await connect("http://localhost:9222");
const page = await client.page(NAME);
await page.setViewportSize({ width: parseInt(process.env.W || "1920"), height: parseInt(process.env.H || "1080") });
await page.goto(process.env.CARD_URL!);
await page.evaluate(() => document.fonts.ready);
await page.evaluate(() => Promise.all(Array.from(document.images).map((i) => (i.complete ? null : new Promise((r) => { i.onload = i.onerror = r; })))));
await page.waitForTimeout(500);
const n = process.env.STILL ? 1 : Math.round(LEN * FPS);
for (let i = 0; i < n; i++) {
  const t = (i / FPS) * 1000;
  await page.evaluate((t) => { for (const a of document.getAnimations()) { a.pause(); a.currentTime = t; } }, t);
  await page.screenshot({ path: `${OUT}/${String(i).padStart(4, "0")}.png`, omitBackground: ALPHA });
}
console.log("frames", n);
if (NAME !== "gfx") await client.close(NAME).catch(() => {});
await client.disconnect();
