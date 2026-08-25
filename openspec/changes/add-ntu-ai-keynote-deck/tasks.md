## 1. Assets & Fonts

- [ ] 1.1 Download Be Vietnam Pro woff2 files (weights 400/600/800, `vietnamese` subset) via google-webfonts-helper into `~/Developer/ntu-keynote/assets/fonts/` and verify each file is a valid WOFF2 (`file` reports "Web Open Font Format") and renders Vietnamese diacritics (open a test HTML with "Tiếng Việt ậ ộ ữ ề" using the local @font-face)
- [ ] 1.2 Verify the existing `~/Developer/ntu-keynote/assets/ntu-logo.png` is intact (1304×512, transparent) and confirm no re-download is needed

## 2. Deck Skeleton

- [ ] 2.1 Create `~/Developer/ntu-keynote/index.html` with the fixed 1280×720 stage, CSS transform scaling handler (design D2), NTU palette variables (D5), local @font-face declarations (D6), and 17 empty `<section class="slide">` elements; verify by opening in Safari and resizing the window — stage stays 16:9, letterboxed, centered
- [ ] 2.2 Implement navigation JS (design D3): ArrowRight/Space/PageDown/click = next, ArrowLeft/PageUp = previous, Home/End = first/last, with a slide counter indicator; verify each key and click advances correctly and clicks are ignored while notes overlay is open
- [ ] 2.3 Implement speaker-notes overlay (design D4): `S` toggles a semi-transparent panel reading each slide's notes, with a visible "notes ON" badge; verify toggle works and overlay never appears in print output

## 3. Content — Act 1 (slides 1–5, ~3 min)

- [ ] 3.1 Write slide 1 (title: theme, speaker name/credentials, NTU logo + alumni line) and slide 2 (hook: two show-of-hands questions + "khoảng cách giữa hai cánh tay"); verify Vietnamese diacritics render correctly with bundled font
- [ ] 3.2 Write slide 3 ($15.7T PwC, with animated counter per D7) and verify the counter animates on slide activation and replays on revisit
- [ ] 3.3 Write slide 4 (agentic shift: Gartner 0%→15% decisions by 2028, <1%→33% enterprise software) and slide 5 (Vietnam: Nghị quyết 57 top-3 ASEAN, Google $79.3B ≈ 12% GDP by 2030); verify source attribution lines are present on both

## 4. Content — Act 2 (slides 6–14, ~5–7 min)

- [ ] 4.1 Write slide 6 (iceberg pivot) and slide 7 (95% MIT stat with slam-in animation per D7, $30–40B invested); verify the slam-in keyframe fires on activation and the MIT source line is present
- [ ] 4.2 Write slide 8 (Gartner 40% agentic cancellations by 2027 + "không phải lỗi công nghệ — lỗi cách làm") and slide 9 (personal transition: "3 năm qua tôi đi qua đúng 3 tầng này")
- [ ] 4.3 Write slides 10–12 (the 3 layers: ChatGPT web training → in-house LLM on Nvidia for CSKH/call center → multi-agent agentic), each with its lesson line; slide 11 uses qualitative framing with a marked placeholder slot for optional first-party metrics
- [ ] 4.4 Write slide 13 ("5% còn lại làm gì khác?" — 4 points, headline: start with repetitive processes consuming the most manual effort) and slide 14 (people & jobs: WEF 170M/92M/net +78M, 39% skills transformed, "giải phóng chứ không thay thế" framing); verify all four statistics carry source lines

## 5. Content — Act 3 (slides 15–17, ~3 min)

- [ ] 5.1 Write slide 15 (3 leadership mindsets for living with AI in uncertainty) and slide 16 (3 roundtable questions, each anchored to a seeded statistic: 95% → execution/ROI, jobs → people, 40% → agentic/Vietnam)
- [ ] 5.2 Write slide 17 (handoff to roundtable) and verify the three questions on slide 16 match the statistics seeded in slides 7, 8, and 14

## 6. Speaker Notes & Timing

- [ ] 6.1 Add `data-notes` timing cues to all 17 slides (cumulative timestamps for the 10–15 min budget: ~3:00 pivot, ~7:00 layer 3, ~12:00 questions) plus delivery reminders for the hook and handoff; verify by toggling the notes overlay and walking all slides

## 7. Print Fallback & Final Verification

- [ ] 7.1 Add `@media print` stylesheet (D8): one slide per page, notes hidden, animations frozen at final state, `print-color-adjust: exact`; verify by printing to PDF from Safari and checking 17 pages with dark backgrounds intact
- [ ] 7.2 Full rehearsal check: open `index.html` from a copied folder in a different location (simulating USB), navigate all 17 slides via keyboard and click, confirm no console errors, no network requests (Safari Network tab empty), and fonts/logo load from relative paths
