// Downscale and re-encode the generated artwork.
//
// The generator returns 2K PNGs at 5-10 MB each, which is far too heavy to put
// behind a hero. These are photographic plates shown desaturated under a dark
// wash, so a progressive JPEG at a sensible width is indistinguishable and
// roughly fifty times smaller.
//
//     node scripts/optimize-images.mjs
//
// Requires sharp. Skips silently if the source PNGs are not present.

import { readdir, stat, unlink } from "node:fs/promises";
import path from "node:path";
import sharp from "sharp";

const DIR = path.join(process.cwd(), "assets", "img");
const MAX_WIDTH = 1920;
const QUALITY = 74;

const files = await readdir(DIR).catch(() => []);
const pngs = files.filter((f) => f.endsWith(".png"));

if (!pngs.length) {
  console.log("optimize-images: no PNGs to process");
  process.exit(0);
}

for (const file of pngs) {
  const src = path.join(DIR, file);
  const dest = src.replace(/\.png$/, ".jpg");
  const before = (await stat(src)).size;

  await sharp(src)
    .resize({ width: MAX_WIDTH, withoutEnlargement: true })
    .jpeg({ quality: QUALITY, progressive: true, mozjpeg: true })
    .toFile(dest);

  const after = (await stat(dest)).size;
  await unlink(src);
  console.log(
    `  ${file} -> ${path.basename(dest)}  ` +
    `${(before / 1e6).toFixed(1)}MB -> ${(after / 1e3).toFixed(0)}KB`
  );
}
