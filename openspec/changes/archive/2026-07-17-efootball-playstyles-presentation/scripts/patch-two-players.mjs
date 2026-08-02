#!/usr/bin/env node
/*
 * Patch the two players whose plain-name Wikipedia lookup returned no lead image
 * (Rodri, Ederson) using their explicit disambiguated article titles. Merges the
 * results into the existing image-manifest.json / image-credits.json.
 *
 * Usage: node patch-two-players.mjs
 */

import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const CHANGE_DIR = join(__dirname, "..");

const UA = "tdt-efootball-playstyles-deck/1.0 (educational presentation; contact: local build script)";
const THUMB_W = 220;
const SAFE_LICENSE_RE = /(^cc0)|(^cc-by($|-sa))|(public domain)|(^pd)|(^cc pd)/i;
const SAFE_SHORTNAME_RE = /(CC0)|(CC BY(?!-NC))|(Public domain)|(PD)/i;

// player (as keyed in the deck) → explicit Wikipedia article title
const OVERRIDES = {
  "Rodri": "Rodri (footballer, born 1996)",
  "Ederson": "Ederson (footballer, born 1993)",
};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

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

async function leadImageTitle(articleTitle) {
  const url = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages"
    + "&piprop=original&redirects=1&titles=" + encodeURIComponent(articleTitle);
  const data = await jget(url);
  const pages = data?.query?.pages || {};
  for (const k of Object.keys(pages)) {
    const orig = pages[k]?.original?.source;
    if (orig) return "File:" + decodeURIComponent(orig.split("/").pop());
  }
  return null;
}

async function commonsImageInfo(fileTitle) {
  const url = "https://commons.wikimedia.org/w/api.php?action=query&format=json"
    + "&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=" + THUMB_W
    + "&redirects=1&titles=" + encodeURIComponent(fileTitle);
  const data = await jget(url);
  const pages = data?.query?.pages || {};
  for (const k of Object.keys(pages)) {
    const ii = pages[k]?.imageinfo?.[0];
    if (!ii) continue;
    const em = ii.extmetadata || {};
    const artistRaw = em.Artist?.value || "";
    return {
      thumbUrl: ii.thumburl || null,
      descUrl: ii.descriptionurl || null,
      licenseShort: em.LicenseShortName?.value || "",
      licenseId: em.License?.value || "",
      author: artistRaw.replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim() || "Unknown",
    };
  }
  return null;
}

function isRightsSafe(info) {
  if (!info) return false;
  return SAFE_LICENSE_RE.test(info.licenseId) || SAFE_SHORTNAME_RE.test(info.licenseShort);
}

async function fetchThumbDataUri(thumbUrl) {
  const res = await fetch(thumbUrl, { headers: { "User-Agent": UA } });
  if (!res.ok) throw new Error(`thumb HTTP ${res.status}`);
  const buf = Buffer.from(await res.arrayBuffer());
  const ct = res.headers.get("content-type") || "image/jpeg";
  return `data:${ct};base64,${buf.toString("base64")}`;
}

async function run() {
  const manifest = JSON.parse(readFileSync(join(CHANGE_DIR, "image-manifest.json"), "utf8"));
  const credits = JSON.parse(readFileSync(join(CHANGE_DIR, "image-credits.json"), "utf8"));

  for (const [player, articleTitle] of Object.entries(OVERRIDES)) {
    try {
      const title = await leadImageTitle(articleTitle);
      if (!title) { console.log(`  ∅ ${player}: still no lead image`); continue; }
      const info = await commonsImageInfo(title);
      if (!isRightsSafe(info)) { console.log(`  ✗ ${player}: "${info?.licenseShort}" not rights-safe`); continue; }
      if (!info.thumbUrl) { console.log(`  ∅ ${player}: no thumb`); continue; }
      const dataUri = await fetchThumbDataUri(info.thumbUrl);
      manifest[player] = { dataUri, srcUrl: info.descUrl, license: info.licenseShort, author: info.author };
      // replace any existing credit row for this player, then add
      const idx = credits.findIndex((c) => c.player === player);
      const row = { player, license: info.licenseShort, author: info.author, srcUrl: info.descUrl };
      if (idx >= 0) credits[idx] = row; else credits.push(row);
      console.log(`  ✓ ${player}: ${info.licenseShort} — ${info.author} (${(dataUri.length/1024).toFixed(0)}KB)`);
    } catch (e) {
      console.log(`  ! ${player}: ${e.message}`);
    }
    await sleep(300);
  }

  writeFileSync(join(CHANGE_DIR, "image-manifest.json"), JSON.stringify(manifest, null, 2));
  writeFileSync(join(CHANGE_DIR, "image-credits.json"), JSON.stringify(credits, null, 2));
  const embedded = Object.values(manifest).filter(Boolean).length;
  console.log(`\nPatched. total embedded now = ${embedded}/${Object.keys(manifest).length}`);
}

run();
