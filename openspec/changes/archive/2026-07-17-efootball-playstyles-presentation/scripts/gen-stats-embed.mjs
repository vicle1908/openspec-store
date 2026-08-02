#!/usr/bin/env node
/*
 * Emit the compact PLAYER_STATS object embedded in the deck for the peek panel.
 *
 * Reads pesdb-stats.json (captured by fetch-pesdb-stats.mjs) and writes a
 * trimmed name -> { card, ovr, attrs, era, gk } map to stats-embed.json. The
 * deck's PLAYER_STATS placeholder is filled from this file by inject-stats.mjs.
 *
 * Only rows with ok:true are emitted; illustrative-only exemplars are omitted
 * so the deck's lookup miss cleanly falls back to "Illustrative only".
 *
 * Usage: node gen-stats-embed.mjs
 */

import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const CHANGE_DIR = join(__dirname, "..");
const SRC = join(CHANGE_DIR, "pesdb-stats.json");
const OUT = join(CHANGE_DIR, "stats-embed.json");

const raw = JSON.parse(readFileSync(SRC, "utf8"));
const out = {};
for (const [name, r] of Object.entries(raw)) {
  if (!r || !r.ok) continue;
  out[name] = {
    card: r.card,
    ovr: r.ovr,
    era: r.era,
    gk: !!r.isGk,
    attrs: r.attrs,
  };
}

writeFileSync(OUT, JSON.stringify(out, null, 0));
const n = Object.keys(out).length;
console.log(`Wrote ${n} stat rows → ${OUT} (${(JSON.stringify(out).length / 1024).toFixed(1)}KB)`);
