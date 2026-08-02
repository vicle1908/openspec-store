#!/usr/bin/env node
/*
 * Splice the base64 image manifest into the deck's PLAYER_IMAGES placeholder.
 * Authoring-time only. Idempotent: replaces whatever is between the markers.
 *
 * Reads:  image-manifest.json  (name -> { dataUri, srcUrl, license, author } | null)
 * Writes: the deck HTML, injecting a compact { name: {dataUri,license,author} } object.
 *
 * Usage: node inject-images.mjs
 */

import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const CHANGE_DIR = join(__dirname, "..");
const DECK = join(CHANGE_DIR, "..", "..", "..", "presentations", "efootball-playstyles.html");
const MANIFEST = join(CHANGE_DIR, "image-manifest.json");

const START = "/*__PLAYER_IMAGES__*/";
const END = "/*__END_PLAYER_IMAGES__*/";

const manifest = JSON.parse(readFileSync(MANIFEST, "utf8"));

// Keep only entries that actually have an embedded image; drop nulls (they fall
// back to the deterministic avatar at render time — no need to ship null keys).
const embedded = {};
let count = 0;
for (const [name, rec] of Object.entries(manifest)) {
  if (rec && rec.dataUri) {
    embedded[name] = { dataUri: rec.dataUri, license: rec.license || "", author: rec.author || "Unknown" };
    count++;
  }
}

const json = JSON.stringify(embedded);

let html = readFileSync(DECK, "utf8");
const startIdx = html.indexOf(START);
const endIdx = html.indexOf(END);
if (startIdx === -1 || endIdx === -1) {
  console.error("ERROR: injection markers not found in deck. Aborting.");
  process.exit(1);
}

const before = html.slice(0, startIdx + START.length);
const after = html.slice(endIdx);
html = before + json + after;

writeFileSync(DECK, html);
console.log(`Injected ${count} embedded images into deck (${(json.length / 1024).toFixed(0)}KB of base64).`);
console.log(`Deck size now: ${(html.length / 1024 / 1024).toFixed(2)}MB`);
