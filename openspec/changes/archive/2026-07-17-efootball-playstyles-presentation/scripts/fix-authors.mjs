#!/usr/bin/env node
/*
 * One-shot fixup: re-clean author strings already written to the manifest and
 * credits JSON (fixes the "Unknown authorUnknown author" doubled-span bug)
 * without re-fetching from the network. Same logic as fetch-player-images.mjs
 * cleanAuthor(). Run from the change dir.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const CHANGE_DIR = join(__dirname, "..");

function cleanAuthor(s0) {
  let s = String(s0 || "").replace(/\s+/g, " ").trim();
  if (!s) return "Unknown";
  const half = s.length % 2 === 0 ? s.slice(0, s.length / 2).trim() : "";
  if (half && half === s.slice(Math.ceil(s.length / 2)).trim()) s = half;
  else {
    const m = s.match(/^(.+?)\s*\1$/);
    if (m) s = m[1].trim();
  }
  return s || "Unknown";
}

const manPath = join(CHANGE_DIR, "image-manifest.json");
const credPath = join(CHANGE_DIR, "image-credits.json");

const manifest = JSON.parse(readFileSync(manPath, "utf8"));
const credits = JSON.parse(readFileSync(credPath, "utf8"));

let fixed = 0;
for (const name of Object.keys(manifest)) {
  const rec = manifest[name];
  if (rec && rec.author) {
    const c = cleanAuthor(rec.author);
    if (c !== rec.author) { rec.author = c; fixed++; }
  }
}
for (const c of credits) {
  if (c.author) c.author = cleanAuthor(c.author);
}

writeFileSync(manPath, JSON.stringify(manifest, null, 2));
writeFileSync(credPath, JSON.stringify(credits, null, 2));
console.log(`Re-cleaned authors. Fixed ${fixed} manifest entries.`);
