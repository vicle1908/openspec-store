#!/usr/bin/env node
/*
 * Generate the H.4 captured-values markdown tables from pesdb-stats.json so the
 * data-reference table never drifts from the actual capture. Prints three tables:
 * outfield rows, GK rows, and the illustrative-only gaps. Run:
 *   node gen-h4-tables.mjs
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __dirname = dirname(fileURLToPath(import.meta.url));
const data = JSON.parse(readFileSync(join(__dirname, "..", "pesdb-stats.json"), "utf8"));

// Section-E order (style order), name → era, so tables read in deck order.
const ORDER = [
  "Erling Haaland", "Filippo Inzaghi", "Harry Kane", "Gerd Müller",
  "Darwin Núñez", "Didier Drogba", "Olivier Giroud", "Teddy Sheringham",
  "Karim Benzema", "Dennis Bergkamp", "Kevin De Bruyne", "Zinedine Zidane",
  "Bruno Fernandes", "Francesco Totti", "Jude Bellingham", "Frank Lampard",
  "Federico Valverde", "Steven Gerrard", "Rodri", "Andrea Pirlo",
  "Declan Rice", "Claude Makélélé", "Casemiro", "Roy Keane",
  "Mohamed Salah", "Arjen Robben", "Vinícius Júnior", "Ryan Giggs",
  "Trent Alexander-Arnold", "David Beckham", "Virgil van Dijk", "Franz Beckenbauer",
  "Sergio Ramos", "Ronald Koeman", "Alphonso Davies", "Roberto Carlos",
  "Kyle Walker", "Paolo Maldini", "Achraf Hakimi", "Cafu",
  "Ederson", "Manuel Neuer", "Thibaut Courtois", "Gianluigi Buffon",
];

const outfield = [], gk = [], gaps = [];
for (const name of ORDER) {
  const r = data[name];
  if (!r || !r.ok) { gaps.push(name); continue; }
  const a = r.attrs;
  if (r.isGk) {
    gk.push(`| ${name} | ${r.card} | ${r.ovr} | ${a.GKRef} | ${a.GKrea} | ${a.GKawr} | ${a.GKcat} | ${a.GKpar} | ${r.id} |`);
  } else {
    outfield.push(`| ${name} | ${r.card} | ${r.ovr} | ${a.Fin} | ${a.Dri} | ${a.LowPass} | ${a.DefAwr} | ${a.Speed} | ${a.Head} | ${r.id} |`);
  }
}

console.log("### Outfield rows\n");
console.log("| Player | Card | OVR | Fin | Dri | LowPass | DefAwr | Speed | Head | pesdb id |");
console.log("|--------|------|:---:|:---:|:---:|:-------:|:------:|:-----:|:----:|----------|");
console.log(outfield.join("\n"));
console.log(`\n(${outfield.length} outfield rows)\n`);

console.log("### Goalkeeper rows\n");
console.log("| Player | Card | OVR | GKRef | GKrea | GKawr | GKcat | GKpar | pesdb id |");
console.log("|--------|------|:---:|:-----:|:-----:|:-----:|:-----:|:-----:|----------|");
console.log(gk.join("\n"));
console.log(`\n(${gk.length} GK rows)\n`);

console.log("### Illustrative-only (no clean 2026 card)\n");
console.log(gaps.map((n) => `- ${n}`).join("\n"));
console.log(`\n(${gaps.length} gaps)`);
console.log(`\nTOTAL captured: ${outfield.length + gk.length}/44`);
