#!/usr/bin/env node
/*
 * Hi-res portrait tier for the interactive peek panel (task 9.3).
 *
 * Reuses the already-cleared Commons sources recorded in image-manifest.json
 * (each entry's srcUrl is a Commons File: page whose license was vetted by the
 * thumbnail pass), and re-fetches ONLY those files at a larger width. No new
 * license decisions are made here: if a name isn't already an embedded,
 * rights-safe thumbnail, it is skipped (its chip keeps the deterministic avatar
 * and the peek panel shows the thumbnail-or-avatar it already has).
 *
 * Output: image-manifest-hires.json  (name -> { dataUri } )
 *
 * Usage: node fetch-player-images-hires.mjs
 */

import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const CHANGE_DIR = join(__dirname, "..");
const SRC = join(CHANGE_DIR, "image-manifest.json");
const OUT = join(CHANGE_DIR, "image-manifest-hires.json");

const UA = "tdt-efootball-playstyles-deck/1.0 (educational presentation; contact: local build script)";
const HIRES_W = 400; // peek-panel portrait width in px (kept modest to hold the
                     // single-file deck within its ~5–6MB offline budget)

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Recover the Commons "File:Name.ext" title from a File: page URL.
function fileTitleFromSrc(srcUrl) {
  if (!srcUrl) return null;
  const m = srcUrl.match(/\/wiki\/(File:.+)$/);
  if (!m) return null;
  return "File:" + decodeURIComponent(m[1].slice("File:".length));
}

async function jget(url, tries = 5) {
  let delay = 800;
  for (let attempt = 1; attempt <= tries; attempt++) {
    const res = await fetch(url, { headers: { "User-Agent": UA, "Accept": "application/json" } });
    if (res.ok) return res.json();
    if (res.status === 429 && attempt < tries) {
      const ra = parseInt(res.headers.get("retry-after") || "0", 10);
      await sleep(ra > 0 ? ra * 1000 : delay); delay *= 2; continue;
    }
    throw new Error(`HTTP ${res.status} for ${url}`);
  }
  throw new Error(`giving up: ${url}`);
}

async function hiresThumbUrl(fileTitle) {
  const url = "https://commons.wikimedia.org/w/api.php?action=query&format=json"
    + "&prop=imageinfo&iiprop=url&iiurlwidth=" + HIRES_W
    + "&redirects=1&titles=" + encodeURIComponent(fileTitle);
  const data = await jget(url);
  const pages = data?.query?.pages || {};
  for (const k of Object.keys(pages)) {
    const ii = pages[k]?.imageinfo?.[0];
    if (ii?.thumburl) return ii.thumburl;
  }
  return null;
}

async function fetchDataUri(thumbUrl, tries = 5) {
  let delay = 800;
  for (let attempt = 1; attempt <= tries; attempt++) {
    const res = await fetch(thumbUrl, { headers: { "User-Agent": UA } });
    if (res.ok) {
      const buf = Buffer.from(await res.arrayBuffer());
      const ct = res.headers.get("content-type") || "image/jpeg";
      return `data:${ct};base64,${buf.toString("base64")}`;
    }
    if (res.status === 429 && attempt < tries) {
      const ra = parseInt(res.headers.get("retry-after") || "0", 10);
      await sleep(ra > 0 ? ra * 1000 : delay); delay *= 2; continue;
    }
    throw new Error(`thumb HTTP ${res.status}`);
  }
  throw new Error(`thumb giving up: ${thumbUrl}`);
}

async function run() {
  const manifest = JSON.parse(readFileSync(SRC, "utf8"));
  const out = {};
  let ok = 0, skip = 0;
  for (const [name, rec] of Object.entries(manifest)) {
    if (!rec || !rec.dataUri || !rec.srcUrl) { skip++; continue; }
    const title = fileTitleFromSrc(rec.srcUrl);
    if (!title) { skip++; console.log(`  ∅ ${name}: no file title from srcUrl`); continue; }
    try {
      const thumb = await hiresThumbUrl(title);
      if (!thumb) { skip++; console.log(`  ∅ ${name}: no hi-res thumb`); continue; }
      out[name] = { dataUri: await fetchDataUri(thumb) };
      ok++;
      console.log(`  ✓ ${name}: ${(out[name].dataUri.length / 1024).toFixed(0)}KB`);
    } catch (e) {
      skip++;
      console.log(`  ! ${name}: ${e.message}`);
    }
    await sleep(150);
  }
  writeFileSync(OUT, JSON.stringify(out));
  console.log(`\nDone. hi-res=${ok} skip=${skip} → ${OUT} (${(JSON.stringify(out).length / 1024).toFixed(0)}KB)`);
}

run();
