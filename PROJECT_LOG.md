# Catholic Novenas — project log

A library of 9-day Catholic novenas for family and friends. Each novena has a phone prayer page (light and dark, day-by-day progress) and a print layout in Google Docs. New novenas are made from just an intention with the **novena-maker** skill.

Read this at the start of a work session. Update it at the end when something changed: add a log entry, move finished items out of "Open items".

## Where things live

| What | Where |
|---|---|
| Live library | https://catholic-novenas.netlify.app |
| Repo | `chaviotics/catholic-novenas`, branch `main` |
| Netlify project | `catholic-novenas`: publishes `site/` on every push, no build step on Netlify (run `tools/build.py` and commit `site/`) |
| How to make a novena | `skill/SKILL.md` (the novena-maker skill) |
| Print docs | Google Drive folder "[12] 🙏 Faith". IDs are in `README.md` |
| Original debt novena (v1) | novena-finances.netlify.app, repo `chaviotics/novena-finances`. **Separate and in use. Never change or deploy to it.** |

## Novenas in the library

| Slug | Card title | Intercessors | Status | Print |
|---|---|---|---|---|
| `relief-from-debt` | Relief from Debt and Financial Hardship | St. Joseph, St. Rita of Cascia, St. Jude Thaddeus (Memorare to St. Joseph) | Published | 4 pages, tab "With Intention" |
| `healing` | Healing of the Sick | Our Lady of Lourdes, St. Raphael, St. Camillus de Lellis, St. Bernadette (Marian Memorare) | Published | 4 pages |

## Decisions and rules

- **Scripture:** RSV Catholic Edition, checked word for word against a source (`novenas/<slug>/sources.md`). No version label after references; the RSV-CE permission notice appears once (site footer, print page 1). Stay under 500 verses per work.
- **Numbers:** digits in anything the reader scans (kickers, cards, headings, labels, tips, how-to): "9 days", "Day 3", "10 minutes". Prayers, reflections and steps, which are read aloud, keep words ("these nine days").
- **Saints:** 1–3 per novena, suggested from the intention. Public-domain images in both the app and print. Facts only when certain; quote a saint only with a well-attested line.
- **Faith:** never promise outcomes, no prosperity-gospel framing. Pray for God's will; for healing, also for strength, peace, doctors and caregivers.
- **Print:** 3 pages, 4 at most. Made by copying the template doc and filling it with `tools/print_fill.py`; one tab per doc (the PDF export prints every tab).
- **Link previews:** made by `tools/og.py` from each novena's title, kicker and 2 saints (`"ogSaints": [left, right]` in novena.json so they face inward). Cream background, wine and gold accents; no URL or call to action on the image.
- **Library cards:** title without "Novena for" (the section heading already says it), icon on the left, saints' faces top right, progress line and "Pray" / "Continue Day N" button.
- **Theme and text size** are shared across the whole site (`novenas-mode`, `novenas-scale`); progress is saved per novena (`novena-<slug>`).
- **Offline:** every build regenerates `site/sw.js` with a new version, so phones pick up changes on their next online visit. Never edit `site/sw.js` by hand; change `templates/sw.js`. Fonts live in `site/fonts/` (no Google Fonts on the site; artifact previews still use Google Fonts).
- **Layout:** phone first. 601–1023px: one column with the 9 days in a sticky strip. 1024px and up: sidebar + prayer column. Phones: 9 days in a bottom bar.
- **Workflow:** finish new work as a Claude artifact preview first; commit and push only after approval.
- **Commits:** no Co-Authored-By lines.

## Log

### Earlier sessions
- Built the debt novena: Google Docs print layout and a phone web app on Netlify (novena-finances). Family started praying with v1.
- Made v2 of the debt novena: RSV-CE text, fuller daily Scripture, reflection and prayer, saint images in app and print, 4-page print. Approved.
- Turned the approach into the novena-maker skill.
- Built the library: `novenas/<slug>/novena.json` + `tools/build.py` → `site/`. Moved the debt novena in.
- Made the healing novena with the skill (first real test): Scripture verified, Catholic review applied, print doc at 4 pages.

### 2026-11-20
- Library moved to its own repo and Netlify project so v1 stays untouched.
- Applied feedback: digits instead of number words, no "RSV-CE" after references, new library cards, "How a novena works" in digits, more space at the bottom.
- UI/UX review (scored 7/10 before): all 15 findings fixed. Highlights: card progress states, shared theme and text size, the cross in a novena's top bar returns to the library, larger card text, footer padding actually applied, "&" no longer dropped from day captions.
- Print docs (template, debt v2, healing) updated to match: "9 DAYS OF …" kickers, no "· RSV-CE" on cites, "The 9 Days", "End with an Our Father, a Hail Mary and a Glory Be", "these 9 days" in the tip. Healing print still 4 pages, all text present.
- Skill updated with the digit and reference rules; `print_fill.py` no longer adds the version label.
- Link previews redesigned to read at chat size (`tools/og.py` → `og.jpg`): cream with a gold frame, a big wine title, one short line, 2 saints in arched frames, text kept in the centre square for apps that crop. One per novena plus the library. Fuller og:title and og:description, og:image:alt, and a `?v=` hash on og:image so chat apps refetch. JPEG about 110 KB (WhatsApp often drops images over about 300 KB). Chav tried wine as the background and found it too red; kept the Wine & Gold palette.
- General wording everywhere (Chav): no "with your family" or "family and friends". Tagline is "Pray one day at a time". Debt card says "For anyone…", tip heading "Praying with others", "How a novena works" item 3 is now "Stays on your device". Link descriptions under 125 characters via `ogDescription`. Print docs still say "As a family" in the tip.
- UI/UX review 2 (7.0 → 8.5) and a desktop layout, still phone first. Library: 1080px wide from 760px, cards side by side, "How a novena works" in 3 columns, Text size button. Novena pages from 1024px: sidebar (today card, 3 × 3 day grid, start date, "Today's prayers" list that follows the part on screen) beside a ~66-character prayer column; tablets and phones keep the one-column layout. Phone fixes: shorter hero so "Pray Day N" clears the bottom day bar, no empty prev/next box, `viewport-fit=cover` so the safe-area padding works, "this device" instead of "this phone".
- Round 2 (→ 9.0): `templates/novena.html` styles rewritten as one sectioned stylesheet (checked identical by computed styles at 6 widths, both themes, 2 text sizes; only change: the day card's status line now scales with text size). Laptop hero now opens the prayer column beside the sidebar. Offline mode: `tools/build.py` writes `site/sw.js` from `templates/sw.js` (pages network first with a 4 s fallback to the saved copy; images, fonts, icons saved once). Fonts are self-hosted in `site/fonts/` (latin subset). "Saved on this device, so it opens even without signal" shows once the library is cached.

## Open items

1. **Go live:** link the Netlify project `catholic-novenas` to the repo (branch `main`, build command blank, publish directory `site`), then check catholic-novenas.netlify.app on a phone.
2. **Decide:** should prayers, reflections and steps also use digits? (Now: words.)
3. **Optional:** a personalized print copy of the healing novena with the person's name in place of "N.".
4. **Optional cleanup:** the old `catholic-novenas` branch on the novena-finances repo, and the scratch Google Doc used for image imports (`1P0v5bN3QCc97elk4VFMVbsgMDIxItOIKzT5k9Z97Bys`).
5. **Known v1 bug, left alone on purpose:** the novena-finances app drops "&" from day captions. Fixed in the library.

## Ideas to weigh (not decided)

- When the family finishes their current round, point novena-finances to the library's debt novena so there is one version to maintain.
- A share button on each novena page.
- Next intentions to consider: a family's thanksgiving novena, a novena for a job or vocation decision, one for exams or a new school year.
