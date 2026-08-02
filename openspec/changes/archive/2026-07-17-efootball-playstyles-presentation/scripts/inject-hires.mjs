#!/usr/bin/env node
/*
 * Splice the normalized hi-res portrait manifest into the deck's PLAYER_HIRES
 * placeholder. Authoring-time only. Idempotent: replaces whatever is between
 * the markers.
 *
 * Reads:  image-manifest-hires.json  (name -> { dataUri })
 * Writes: the deck HTML, injecting a compact { name: dataUri } object (the peek
 *         panel only needs the data URI; license/author already ship via
 *         PLAYER_IMAGES for the credits slide).
 *
 * Usage: node inject-hires.mjs
 */

import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const CHANGE_DIR = join(__dirname, "..");
const DECK = join(CHANGE_DIR, "..", "..", "..", "presentations", "efootball-playstyles.html");
const MANIFEST = join(CHANGE_DIR, "image-manifest-hires.json");

const START = "/*__PLAYER_HIRES__*/";
const END = "/*__END_PLAYER_HIRES__*/";

const manifest = JSON.parse(readFileSync(MANIFEST, "utf8"));

// Flatten to name -> dataUri; drop any empty entries.
const flat = {};
let count = 0;
for (const [name, rec] of Object.entries(manifest)) {
  if (rec && rec.dataUri) {
    flat[name] = rec.dataUri;
    count++;
  }
}

const json = JSON.stringify(flat);

let html = readFileSync(DECK, "utf8");
const startIdx = html.indexOf(START);
const endIdx = html.indexOf(END);
if (startIdx === -1 || endIdx === -1) {
  console.error("ERROR: PLAYER_HIRES markers not found in deck. Aborting.");
  process.exit(1);
}

const before = html.slice(0, startIdx + START.length);
const after = html.slice(endIdx);
html = before + json + after;

writeFileSync(DECK, html);
console.log(`Injected ${count} hi-res portraits into deck (${(json.length / 1024 / 1024).toFixed(2)}MB).`);
console.log(`Deck size now: ${(html.length / 1024 / 1024).toFixed(2)}MB`);
