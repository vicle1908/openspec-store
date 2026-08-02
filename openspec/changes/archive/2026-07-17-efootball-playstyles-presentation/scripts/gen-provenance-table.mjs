#!/usr/bin/env node
/*
 * Generate the section-G provenance table (data-reference.md) from the
 * image manifest. Authoring-time tooling; not shipped runtime.
 *
 * Era (modern/historical) is derived from the deck's exemplar pairing:
 * each style lists `mod` (modern) then `his` (historical).
 */
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const CHANGE_DIR = join(__dirname, "..");

const manifest = JSON.parse(readFileSync(join(CHANGE_DIR, "image-manifest.json"), "utf8"));

// modern/historical pairing, matching the deck data model order.
const PAIRS = [
  ["Erling Haaland", "Filippo Inzaghi"],
  ["Harry Kane", "Gerd Müller"],
  ["Darwin Núñez", "Didier Drogba"],
  ["Olivier Giroud", "Teddy Sheringham"],
  ["Karim Benzema", "Dennis Bergkamp"],
  ["Kevin De Bruyne", "Zinedine Zidane"],
  ["Bruno Fernandes", "Francesco Totti"],
  ["Jude Bellingham", "Frank Lampard"],
  ["Federico Valverde", "Steven Gerrard"],
  ["Rodri", "Andrea Pirlo"],
  ["Declan Rice", "Claude Makélélé"],
  ["Casemiro", "Roy Keane"],
  ["Mohamed Salah", "Arjen Robben"],
  ["Vinícius Júnior", "Ryan Giggs"],
  ["Trent Alexander-Arnold", "David Beckham"],
  ["Virgil van Dijk", "Franz Beckenbauer"],
  ["Sergio Ramos", "Ronald Koeman"],
  ["Alphonso Davies", "Roberto Carlos"],
  ["Kyle Walker", "Paolo Maldini"],
  ["Achraf Hakimi", "Cafu"],
  ["Ederson", "Manuel Neuer"],
  ["Thibaut Courtois", "Gianluigi Buffon"],
];

const era = new Map();
for (const [mod, his] of PAIRS) { era.set(mod, "modern"); era.set(his, "historical"); }

// preserve deck order: iterate pairs, modern then historical
const order = [];
for (const [mod, his] of PAIRS) { order.push(mod); order.push(his); }

const esc = (s) => String(s || "").replace(/\|/g, "\\|");

const rows = order.map((name) => {
  const rec = manifest[name];
  if (rec && rec.dataUri) {
    const file = rec.srcUrl ? rec.srcUrl.split("/").pop() : "";
    const link = rec.srcUrl ? `[${esc(file)}](${rec.srcUrl})` : "—";
    return `| ${esc(name)} | ${era.get(name)} | embedded | ${esc(rec.license)} | ${esc(rec.author)} | ${link} |`;
  }
  return `| ${esc(name)} | ${era.get(name)} | avatar | — | — | _(deterministic fallback)_ |`;
});

const embedded = order.filter((n) => manifest[n] && manifest[n].dataUri).length;
const fallback = order.length - embedded;

const table = `### Provenance manifest (generated)

Generated from \`image-manifest.json\` by \`scripts/gen-provenance-table.mjs\`.
Coverage: **${embedded}/${order.length} embedded** rights-safe photos, ${fallback} deterministic avatar fallback(s).

| Player | Era | Result | License | Author | Source |
|--------|-----|--------|---------|--------|--------|
${rows.join("\n")}

> The live manifest with exact source URLs and base64 data is written to
> \`image-manifest.json\` in the change dir when the fetch script runs. The deck's
> credits slide is generated from the same manifest so on-slide attribution and
> this reference never drift.`;

const ref = readFileSync(join(CHANGE_DIR, "data-reference.md"), "utf8");
const start = ref.indexOf("### Provenance manifest (generated)");
if (start === -1) { console.error("anchor not found"); process.exit(1); }
const updated = ref.slice(0, start) + table + "\n";
writeFileSync(join(CHANGE_DIR, "data-reference.md"), updated);
console.log(`Wrote provenance table: ${embedded} embedded, ${fallback} fallback.`);
