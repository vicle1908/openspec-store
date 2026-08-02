#!/usr/bin/env node
/*
 * Authoring-time pesdb.net stat-capture pipeline (not shipped runtime).
 *
 * Captures each exemplar's real eFootball 2026 attributes for the peek panel.
 * The peek panel shows ONE representative attribute per bucket (see H.3), so we
 * only transcribe those six (or the five GK attrs) plus overall + card type.
 *
 * Enumeration reality (verified 2026-07-15):
 *   - pesdb's NAME search indexes current-roster players only, so modern
 *     exemplars resolve by `?name=`, but legends do NOT.
 *   - Legends ARE present in the 2026 export and reachable by direct `?id=`
 *     (e.g. Pelé = 88037702764935). We therefore feed legend ids from a
 *     resolved name→id map (LEGEND_IDS) and moderns via name search.
 *
 * Every captured row records the page's game-version string so a 2025 export
 * can never be silently shipped as 2026.
 *
 * Output: pesdb-stats.json  (name -> { id, card, ovr, attrs{}, gameVersion, ok })
 *
 * Usage:
 *   node fetch-pesdb-stats.mjs            # capture all
 *   node fetch-pesdb-stats.mjs --only "Pelé,Rodri"
 */

import { writeFileSync, readFileSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const CHANGE_DIR = join(__dirname, "..");
const OUT = join(CHANGE_DIR, "pesdb-stats.json");

const UA = "tdt-efootball-playstyles-deck/1.0 (educational presentation; contact: local build script)";
const BASE = "https://pesdb.net/efootball/";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// The 44 exemplars split by era. Modern = has a searchable current-roster card.
// Historical = legend/retired, captured from the primary Epic/Legend card by id.
const MODERN = [
  "Erling Haaland", "Harry Kane", "Darwin Núñez", "Olivier Giroud",
  "Karim Benzema", "Kevin De Bruyne", "Bruno Fernandes", "Jude Bellingham",
  "Federico Valverde", "Rodri", "Declan Rice", "Casemiro",
  "Mohamed Salah", "Vinícius Júnior", "Trent Alexander-Arnold", "Virgil van Dijk",
  "Sergio Ramos", "Alphonso Davies", "Kyle Walker", "Achraf Hakimi",
  "Ederson", "Thibaut Courtois",
];

const HISTORICAL = [
  "Filippo Inzaghi", "Gerd Müller", "Didier Drogba", "Teddy Sheringham",
  "Dennis Bergkamp", "Zinedine Zidane", "Francesco Totti", "Frank Lampard",
  "Steven Gerrard", "Andrea Pirlo", "Claude Makélélé", "Roy Keane",
  "Arjen Robben", "Ryan Giggs", "David Beckham", "Franz Beckenbauer",
  "Ronald Koeman", "Roberto Carlos", "Paolo Maldini", "Cafu",
  "Manuel Neuer", "Gianluigi Buffon",
];

const GK = new Set(["Ederson", "Thibaut Courtois", "Manuel Neuer", "Gianluigi Buffon"]);

// Explicit name → pesdb id overrides (eFootball 2026 export), verified via
// web-indexed pesdb id-pages. Used for ANY exemplar, not just legends: legends
// aren't name-searchable, and a few moderns 404 on a hyphen or hit a name
// collision (e.g. "Ederson" the outfielder vs. the Man City keeper). A non-empty
// override id always wins over name search. Loaded from pesdb-legend-ids.json.
const OVERRIDE_IDS = loadIdOverrides();

function loadIdOverrides() {
  const f = join(__dirname, "pesdb-legend-ids.json");
  if (existsSync(f)) {
    const raw = JSON.parse(readFileSync(f, "utf8"));
    const ids = raw.ids || raw; // support both {ids:{}} and flat {}
    // Drop empty-string placeholders (unresolved).
    return Object.fromEntries(Object.entries(ids).filter(([, v]) => v));
  }
  return { "Pelé": "88037702764935" };
}

// GET html with retry + backoff, honouring pesdb's soft rate limit (429 body).
async function hget(url, tries = 6) {
  let delay = 1500;
  for (let attempt = 1; attempt <= tries; attempt++) {
    const res = await fetch(url, { headers: { "User-Agent": UA, "Accept": "text/html" }, redirect: "follow" });
    const body = await res.text();
    const limited = res.status === 429 || /making requests too quickly/i.test(body);
    if (res.ok && !limited) return body;
    if (limited && attempt < tries) { await sleep(delay); delay = Math.min(delay * 2, 30000); continue; }
    if (res.ok) return body;
    if (attempt < tries) { await sleep(delay); delay *= 2; continue; }
    throw new Error(`HTTP ${res.status} for ${url}`);
  }
  throw new Error(`giving up after ${tries} tries: ${url}`);
}

// Parse a pesdb player id-page: attributes are <th>Label:</th><td><span>V</span></td>.
function parsePlayerPage(html) {
  const attrs = {};
  const re = /<th[^>]*>([^<:]+):<\/th>\s*<td[^>]*>(?:<span[^>]*>)?([^<]+)/g;
  let m;
  while ((m = re.exec(html)) !== null) {
    attrs[m[1].trim()] = m[2].trim();
  }
  // Card type: the type box shows the active type; the page <h1>/title carries it.
  // pesdb marks the active card via a highlighted cell; fall back to detecting the
  // set of type labels present and picking the one flagged, else read the meta.
  const gv = (html.match(/exported from the game\s*<[^>]*>?\s*(eFootball\s*20\d\d)/i)
    || html.match(/(eFootball\s*20\d\d)\s*\(Last update/i)
    || [])[1] || "";
  const lastUpdate = (html.match(/Last update:\s*([0-9/]+)/i) || [])[1] || "";
  const cardType = detectCardType(html);
  return { attrs, gameVersion: gv.replace(/\s+/g, " ").trim(), lastUpdate, cardType };
}

// The card image sits in a flip-box; the card-type label is the text node that
// immediately follows the closing </div> of that box, inside the same <td>:
//   …</div></div></div></div>Epic</td>
// This is the authoritative per-card type on a pesdb id-page.
const CARD_TYPES = "Standard|Featured|Epic|Legend|Big Time|Show Time|Highlight|Trending|POTW|Nostalgia|Legendary";
function detectCardType(html) {
  const box = html.match(new RegExp(`</div></div></div></div>\\s*(${CARD_TYPES})\\s*</td>`, "i"));
  if (box) return box[1].trim();
  // Fallback: a card-type keyword sitting alone in a <td> right before the name row.
  const td = html.match(new RegExp(`>\\s*(${CARD_TYPES})\\s*</td>`, "i"));
  return td ? td[1].trim() : "";
}

// Representative attributes per H.3.
const OUTFIELD_KEYS = {
  Fin: "Finishing",
  Dri: "Dribbling",
  LowPass: "Low Pass",
  DefAwr: "Defensive Awareness",
  Speed: "Speed",
  Head: "Heading",
};
const GK_KEYS = {
  GKRef: "GK Reflexes",
  GKrea: "GK Reach",
  GKawr: "GK Awareness",
  GKcat: "GK Catching",
  GKpar: "GK Parrying",
};

function pickAttrs(attrs, isGk) {
  const keys = isGk ? GK_KEYS : OUTFIELD_KEYS;
  const out = {};
  for (const [short, full] of Object.entries(keys)) {
    out[short] = attrs[full] != null ? Number(attrs[full]) : null;
  }
  return out;
}

// Resolve a modern player's Standard/base card id via name search.
// Returns { id, name } of the best current-roster match, or null.
async function resolveModernId(name) {
  const url = BASE + "?name=" + encodeURIComponent(name);
  const html = await hget(url);
  // Search results are rows: <a href="?id=NNN">Display Name</a>
  const rows = [...html.matchAll(/id=(\d+)">([^<]+)<\/a>/g)].map((m) => ({ id: m[1], disp: m[2] }));
  if (!rows.length) return null;
  // Prefer an exact display-name match (case/accent-insensitive), else first row.
  const norm = (s) => s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
  const exact = rows.find((r) => norm(r.disp) === norm(name));
  return exact || rows[0];
}

async function captureById(id, isGk) {
  const html = await hget(BASE + "?id=" + id);
  const { attrs, gameVersion, lastUpdate, cardType } = parsePlayerPage(html);
  const playerName = attrs["Player Name"] || "";
  const ovr = attrs["Overall Rating"] != null ? Number(attrs["Overall Rating"]) : null;
  return {
    id,
    resolvedName: playerName,
    card: cardType,
    ovr,
    attrs: pickAttrs(attrs, isGk),
    gameVersion,
    lastUpdate,
    is2026: /2026/.test(gameVersion),
    ok: /2026/.test(gameVersion) && ovr != null,
  };
}

async function run() {
  const onlyArg = process.argv.indexOf("--only");
  const only = onlyArg > -1 ? new Set(process.argv[onlyArg + 1].split(",").map((s) => s.trim())) : null;

  const prior = existsSync(OUT) ? JSON.parse(readFileSync(OUT, "utf8")) : {};
  const result = { ...prior };

  const targets = [
    ...MODERN.map((n) => ({ name: n, era: "modern" })),
    ...HISTORICAL.map((n) => ({ name: n, era: "historical" })),
  ].filter((t) => (only ? only.has(t.name) : true));

  for (const { name, era } of targets) {
    const isGk = GK.has(name);
    try {
      let id;
      // An explicit override id always wins: it covers every legend (not
      // name-searchable) and the moderns whose plain name search 404s on a
      // hyphen or resolves to a wrong-person name collision (e.g. Ederson).
      const override = OVERRIDE_IDS[name];
      if (override) {
        id = override;
      } else if (era === "modern") {
        const hit = await resolveModernId(name);
        if (!hit) { result[name] = { era, ok: false, note: "no name-search hit" }; console.log(`  ∅ ${name}: no search hit`); await sleep(1800); continue; }
        id = hit.id;
        await sleep(1800);
      } else {
        result[name] = { era, ok: false, note: "no override id (illustrative-only)" };
        console.log(`  ? ${name}: no override id — illustrative-only`);
        continue;
      }
      const row = await captureById(id, isGk);
      result[name] = { era, isGk, ...row };
      const flag = row.ok ? "✓" : (row.is2026 ? "~" : "✗2025?");
      console.log(`  ${flag} ${name}: id=${id} card=${row.card} ovr=${row.ovr} gv="${row.gameVersion}" attrs=${JSON.stringify(row.attrs)}`);
      await sleep(1800);
    } catch (e) {
      result[name] = { era, ok: false, note: e.message };
      console.log(`  ! ${name}: ${e.message}`);
      await sleep(2500);
    }
  }

  writeFileSync(OUT, JSON.stringify(result, null, 2));
  const okCount = Object.values(result).filter((r) => r.ok).length;
  console.log(`\nDone. ok=${okCount}/${Object.keys(result).length} → ${OUT}`);
}

run();
