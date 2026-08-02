#!/usr/bin/env node
/*
 * Re-encode the hi-res portrait manifest to hold the deck's size budget (task 9.9).
 *
 * The Commons `iiurlwidth` lever alone does not bound bytes: some sources return
 * their native (narrower) file, and a few high-detail JPEGs stay heavy at any
 * width. This pass decodes each embedded portrait, re-encodes it with macOS
 * `sips` at a hard max-width and a fixed JPEG quality, and re-embeds it — which
 * targets the byte outliers (Pirlo, Gerrard) directly instead of chasing width.
 *
 * In place: rewrites image-manifest-hires.json with the smaller data URIs.
 *
 * Usage: node normalize-hires.mjs
 */

import { readFileSync, writeFileSync, mkdtempSync, rmSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { tmpdir } from "node:os";

const __dirname = dirname(fileURLToPath(import.meta.url));
const CHANGE_DIR = join(__dirname, "..");
const MANIFEST = join(CHANGE_DIR, "image-manifest-hires.json");

const MAX_W = 360;     // hard width cap in px
const QUALITY = 68;    // JPEG quality (0–100); 68 is visibly clean on a projector

const manifest = JSON.parse(readFileSync(MANIFEST, "utf8"));
const tmp = mkdtempSync(join(tmpdir(), "hires-"));

let before = 0, after = 0, n = 0;
for (const [name, rec] of Object.entries(manifest)) {
  if (!rec || !rec.dataUri) continue;
  const m = rec.dataUri.match(/^data:([^;]+);base64,(.+)$/);
  if (!m) continue;
  const buf = Buffer.from(m[2], "base64");
  before += buf.length;
  const inF = join(tmp, "in.img");
  const outF = join(tmp, "out.jpg");
  writeFileSync(inF, buf);
  // sips: resize to max width (keeps aspect), force JPEG at QUALITY.
  execFileSync("sips", ["-s", "format", "jpeg", "-s", "formatOptions", String(QUALITY),
    "-Z", String(MAX_W), inF, "--out", outF], { stdio: "ignore" });
  const outBuf = readFileSync(outF);
  after += outBuf.length;
  manifest[name] = { dataUri: `data:image/jpeg;base64,${outBuf.toString("base64")}` };
  n++;
}

rmSync(tmp, { recursive: true, force: true });
writeFileSync(MANIFEST, JSON.stringify(manifest));
console.log(`Normalized ${n} portraits: ${(before / 1024 / 1024).toFixed(2)}MB → ${(after / 1024 / 1024).toFixed(2)}MB`);
console.log(`Manifest file now: ${(JSON.stringify(manifest).length / 1024 / 1024).toFixed(2)}MB`);
