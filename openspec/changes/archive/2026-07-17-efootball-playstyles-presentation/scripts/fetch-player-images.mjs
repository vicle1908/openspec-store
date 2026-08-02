#!/usr/bin/env node
/*
 * Build-time player-photo pipeline (authoring-time only; not shipped runtime).
 *
 * For each exemplar player:
 *   1. Resolve the player's Wikipedia lead image (pageimages) — reduces
 *      wrong-person risk vs. free-text file search.
 *   2. Read the image's license + author from Commons imageinfo.extmetadata.
 *   3. Filter against a rights-safe license allowlist (CC-BY / CC-BY-SA / CC0 / PD).
 *   4. Download a downscaled thumbnail and base64-encode it.
 *   5. Emit a manifest: name -> { dataUri, srcUrl, license, author } OR null (fallback).
 *
 * Output:
 *   - image-manifest.json  (full: includes base64 data URIs, for embedding)
 *   - image-credits.json   (provenance only: name/license/author/url, human-auditable)
 *
 * Usage: node fetch-player-images.mjs
 */

import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const CHANGE_DIR = join(__dirname, "..");

const UA = "tdt-efootball-playstyles-deck/1.0 (educational presentation; contact: local build script)";
const THUMB_W = 220; // downscale width in px — keeps embedded size small

// Rights-safe license allowlist. We match against the Commons license short-name
// (extmetadata.LicenseShortName) and the machine license id (extmetadata.License).
const SAFE_LICENSE_RE = /(^cc0)|(^cc-by($|-sa))|(public domain)|(^pd)|(^cc pd)/i;
const SAFE_SHORTNAME_RE = /(CC0)|(CC BY(?!-NC))|(Public domain)|(PD)/i;

// The 44 exemplars, grouped so the manifest key is the exact name used in the deck.
const PLAYERS = [
  "Erling Haaland", "Filippo Inzaghi",
  "Harry Kane", "Gerd Müller",
  "Darwin Núñez", "Didier Drogba",
  "Olivier Giroud", "Teddy Sheringham",
  "Karim Benzema", "Dennis Bergkamp",
  "Kevin De Bruyne", "Zinedine Zidane",
  "Bruno Fernandes", "Francesco Totti",
  "Jude Bellingham", "Frank Lampard",
  "Federico Valverde", "Steven Gerrard",
  "Rodri", "Andrea Pirlo",
  "Declan Rice", "Claude Makélélé",
  "Casemiro", "Roy Keane",
  "Mohamed Salah", "Arjen Robben",
  "Vinícius Júnior", "Ryan Giggs",
  "Trent Alexander-Arnold", "David Beckham",
  "Virgil van Dijk", "Franz Beckenbauer",
  "Sergio Ramos", "Ronald Koeman",
  "Alphonso Davies", "Roberto Carlos",
  "Kyle Walker", "Paolo Maldini",
  "Achraf Hakimi", "Cafu",
  "Ederson", "Manuel Neuer",
  "Thibaut Courtois", "Gianluigi Buffon",
];

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// GET with retry + exponential backoff, honouring Retry-After on 429.
async function jget(url, tries = 5) {
  let delay = 800;
  for (let attempt = 1; attempt <= tries; attempt++) {
    const res = await fetch(url, { headers: { "User-Agent": UA, "Accept": "application/json" } });
    if (res.ok) return res.json();
    if (res.status === 429 && attempt < tries) {
      const ra = parseInt(res.headers.get("retry-after") || "0", 10);
      const wait = ra > 0 ? ra * 1000 : delay;
      await sleep(wait); delay *= 2; continue;
    }
    throw new Error(`HTTP ${res.status} for ${url}`);
  }
  throw new Error(`giving up after ${tries} tries: ${url}`);
}

// chunk an array into groups of n
const chunk = (arr, n) => { const out = []; for (let i = 0; i < arr.length; i += n) out.push(arr.slice(i, i + n)); return out; };

// Step 1 (BATCHED): resolve each player's Wikipedia lead-image File: title.
// Wikipedia allows up to 50 titles per query, so 44 players → 1 request.
// Returns Map<player, fileTitle|null> using normalized/redirect back-mapping.
async function leadImageTitles(players) {
  const result = new Map(players.map((p) => [p, null]));
  for (const group of chunk(players, 40)) {
    const url = "https://en.wikipedia.org/w/api.php?action=query&format=json&prop=pageimages"
      + "&piprop=original&redirects=1&titles=" + group.map(encodeURIComponent).join("|");
    const data = await jget(url);
    const q = data?.query || {};
    // Build title → requested-player back-map through normalized + redirects.
    const alias = new Map(); // anyTitle → originalRequestedPlayer
    for (const p of group) alias.set(p, p);
    for (const n of q.normalized || []) if (alias.has(n.from)) alias.set(n.to, alias.get(n.from));
    for (const r of q.redirects || []) if (alias.has(r.from)) alias.set(r.to, alias.get(r.from));
    for (const k of Object.keys(q.pages || {})) {
      const page = q.pages[k];
      const orig = page?.original?.source;
      const player = alias.get(page?.title);
      if (orig && player && result.has(player)) {
        result.set(player, "File:" + decodeURIComponent(orig.split("/").pop()));
      }
    }
    await sleep(400);
  }
  return result;
}

// Step 2+3 (BATCHED): license + author + thumbnail for many Commons file titles.
async function commonsImageInfoBatch(fileTitles) {
  const info = new Map(); // fileTitle → {thumbUrl, descUrl, licenseShort, licenseId, author}
  for (const group of chunk(fileTitles, 40)) {
    const url = "https://commons.wikimedia.org/w/api.php?action=query&format=json"
      + "&prop=imageinfo&iiprop=url|extmetadata&iiurlwidth=" + THUMB_W
      + "&redirects=1&titles=" + group.map(encodeURIComponent).join("|");
    const data = await jget(url);
    const q = data?.query || {};
    const alias = new Map();
    for (const t of group) alias.set(t, t);
    for (const n of q.normalized || []) if (alias.has(n.from)) alias.set(n.to, alias.get(n.from));
    for (const r of q.redirects || []) if (alias.has(r.from)) alias.set(r.to, alias.get(r.from));
    for (const k of Object.keys(q.pages || {})) {
      const page = q.pages[k];
      const ii = page?.imageinfo?.[0];
      const key = alias.get(page?.title) || page?.title;
      if (!ii || !key) continue;
      const em = ii.extmetadata || {};
      info.set(key, {
        thumbUrl: ii.thumburl || null,
        descUrl: ii.descriptionurl || null,
        licenseShort: em.LicenseShortName?.value || "",
        licenseId: em.License?.value || "",
        author: cleanAuthor(em.Artist?.value || ""),
      });
    }
    await sleep(400);
  }
  return info;
}

// Commons Artist HTML often wraps multiple nested spans; naive tag-stripping
// fuses them ("Unknown authorUnknown author"). Replace tags with a space,
// collapse whitespace, then de-dupe an exact doubled phrase.
function cleanAuthor(html) {
  let s = html.replace(/<[^>]+>/g, " ").replace(/&nbsp;/g, " ").replace(/\s+/g, " ").trim();
  if (!s) return "Unknown";
  // collapse "X X" (same phrase repeated back-to-back, optional space)
  const half = s.length % 2 === 0 ? s.slice(0, s.length / 2).trim() : "";
  if (half && half === s.slice(Math.ceil(s.length / 2)).trim()) s = half;
  else {
    const m = s.match(/^(.+?)\s*\1$/); // "abcabc" or "abc abc"
    if (m) s = m[1].trim();
  }
  return s || "Unknown";
}

function isRightsSafe(info) {
  if (!info) return false;
  return SAFE_LICENSE_RE.test(info.licenseId) || SAFE_SHORTNAME_RE.test(info.licenseShort);
}

async function fetchThumbDataUri(thumbUrl, tries = 5) {
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
  const manifest = {};
  const credits = [];
  let ok = 0, fallback = 0;

  // Phase 1: batch-resolve lead-image titles (few API calls, not 44).
  console.log("Phase 1: resolving lead images…");
  const titles = await leadImageTitles(PLAYERS);

  // Phase 2: batch-resolve license/author/thumb for the found titles.
  console.log("Phase 2: resolving license + thumbnails…");
  const uniqTitles = [...new Set([...titles.values()].filter(Boolean))];
  const infoByTitle = await commonsImageInfoBatch(uniqTitles);

  // Phase 3: per-player decide embed vs fallback, download rights-safe thumbs.
  console.log("Phase 3: downloading rights-safe thumbnails…");
  for (const player of PLAYERS) {
    const title = titles.get(player);
    const info = title ? infoByTitle.get(title) : null;
    if (!title || !info) { manifest[player] = null; fallback++; console.log(`  ∅ ${player}: no lead image → fallback`); continue; }
    if (!isRightsSafe(info)) {
      manifest[player] = null; fallback++;
      console.log(`  ✗ ${player}: license "${info.licenseShort || "?"}" not rights-safe → fallback`);
      continue;
    }
    if (!info.thumbUrl) { manifest[player] = null; fallback++; console.log(`  ∅ ${player}: no thumb → fallback`); continue; }
    try {
      const dataUri = await fetchThumbDataUri(info.thumbUrl);
      manifest[player] = { dataUri, srcUrl: info.descUrl, license: info.licenseShort, author: info.author };
      credits.push({ player, license: info.licenseShort, author: info.author, srcUrl: info.descUrl });
      ok++;
      console.log(`  ✓ ${player}: ${info.licenseShort} — ${info.author} (${(dataUri.length/1024).toFixed(0)}KB)`);
    } catch (e) {
      manifest[player] = null; fallback++;
      console.log(`  ! ${player}: ${e.message} → fallback`);
    }
    await sleep(120); // gentle pacing on static image host
  }

  writeFileSync(join(CHANGE_DIR, "image-manifest.json"), JSON.stringify(manifest, null, 2));
  writeFileSync(join(CHANGE_DIR, "image-credits.json"), JSON.stringify(credits, null, 2));
  console.log(`\nDone. embedded=${ok} fallback=${fallback} total=${PLAYERS.length}`);
  console.log(`manifest → image-manifest.json (${(JSON.stringify(manifest).length/1024).toFixed(0)}KB)`);
}

run();
