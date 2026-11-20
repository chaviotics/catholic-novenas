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
- **Share button:** shares only the novena's public link (`share()` in `tools/build.py`: URL, title, one short message), never the page's own address, so the day, intention and progress never travel. Touch screens open the phone's share sheet; computers copy the link ("Link copied"). It sits in the top bar on every size (icon only on phones) and as "Share this novena" at the end of each day's prayer. Not in the hero (on small phones it pushes "Pray Day N" under the day bar) and not on library cards (each card is one link).
- **Footer:** one footer on every page from `site_footer()` in `tools/build.py` (All novenas · About · Privacy, credits, the RSV notice except on Privacy), ending with "To God be the glory". Change it there, not in the templates. No privacy line in the footer (Chav): that reassurance lives under the intention box, in the library's "Stays on your device" step and on the Privacy page. The footer shows a warning only when the browser cannot save.
- **Credit and contact:** About says the site is made by Chav, a personal project and not an official Church publication. Corrections and questions go to hey.there.chav@gmail.com (Chav's public contact address for the site; approved by Chav for publishing). Never publish any other address.
- **AI and review disclosure:** About says the new prayers were written with the help of AI and have no priest review or imprimatur yet. Change that line only when a review has actually happened.
- **Privacy:** no cookies, analytics scripts or third-party requests in the browser; fonts and pictures self-hosted. Netlify's server logs do count visits (Observability, on by default; IP address, page, browser type), and the Privacy page says so under "Visits and hosting" (Chav). Don't claim "no tracking" or "no analytics" without that qualifier. `netlify.toml` sets a Content-Security-Policy that allows only the site's own files, so anything external (fonts, scripts, embeds) needs a CSP change and a Privacy page update.
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
- **4 new novenas** (written with the skill, each with its own Catholic review applied, Scripture verified, public-domain saint images): Passing an Exam (St. Joseph of Cupertino, St. Thomas Aquinas, Our Lady Seat of Wisdom; "new school year" folded in), Work and Livelihood (job, better work or one's own business; St. Joseph, St. Cajetan, St. Homobonus, Our Mother of Perpetual Help; honest work and fair dealing, never wealth), A Desperate or Impossible Case (St. Jude, St. Rita, Our Lady Undoer of Knots without an image; crisis helpline link in the tip), and the Gift of Knowledge (for a friend of Chav's drawn to mysticism and "the laws of the universe": St. Augustine, St. Albert the Great, St. Hildegard, Our Lady of Good Counsel; first drafted as "Wisdom and Understanding", refocused on knowledge at Chav's request). Image sources are in each folder's `images.md`.
- **Browsing:** every novena.json now has `category` (one of `CATEGORIES` in `tools/build.py`) and `keywords` (include Tagalog terms). The library shows category pills once 4+ novenas are published (each pill has a shareable `#category` link) and a search box above the cards once 10+ are published (`SEARCH_MIN`). `python3 tools/build.py --search` forces the search box on for previews; commit the default build. Search lives on the library page, not in the top bar.
- Novena pages: the "through the intercession of" saint line wraps between names, never inside one (fixed sideways scrolling on iPhone with 3 long names).
- Link previews: `tools/og.py` needs Python Playwright, which this workspace lacks; the og images for the new novenas were rendered with Node Playwright using the same HTML.
- About page (`/about/`, `templates/about.html`, images and sources in `pages/about/`, built by `about()` in `tools/build.py`): what a novena is, where it began, how to pray, "Not a formula", why we ask the saints (worship God alone; CCC 956, 2683, 2132, 970), "Unlikely saints" (Paul, Augustine, Bartolo Longo, Camillus, Aquinas, Joseph of Cupertino) and every intercessor. Scripture verified (`pages/about/sources.md`); independent Catholic review applied. Navigation: "About" text link in the library top bar beside Text and Dark; novena pages keep their bar and link About in the footer. Library: "Common questions" accordion under "How a novena works" (2 novenas at once, missing a day, praying to saints, guarantees). Approved by Chav.

- **Share button** on every novena page (Chav): Web Share API on touch screens (WhatsApp, Messenger, texts), copy link with a "Link copied" note on computers, URL shown in the note if copying is blocked. Message: "Sharing this novena with you: <title>. 9 days of prayer, one day at a time." Top bar on every size plus "Share this novena" under the day buttons at the end of each day. Phosphor `paper-plane-tilt` icon. Tested on 3 phone sizes, tablet and desktop, light and dark; checked that a typed intention, a marked day and a `#day-3` link never reach the shared text. Approved by Chav.

- **Full UI/UX/IA audit** (Chav): screenshots of every page at 360, 390, 768, 1024, 1440 and 1920px, light, dark and largest text; 3 parallel reviews (phone, tablet/desktop, structure and accessibility) plus axe-core and Playwright behaviour checks. Scored 7.3 before. Fixed:
  - **One footer on every page** (`site_footer()` + `FOOTER_CSS` in `tools/build.py`): All novenas · About · Privacy, the offline note, a warning shown only when the browser cannot save, that page's credits, the RSV notice (not on Privacy, which quotes no Scripture), and a closing line "To God be the glory" between 2 short gold rules. Novena credits moved out of `<main>`.
  - **Privacy page** (`/privacy/`, `templates/privacy.html`, `privacy()`): what is kept and where, what is not done (no ads, analytics, tracking or cookies; fonts and pictures self-hosted), the offline copy, Share, Netlify hosting logs, and a two-tap "Clear my data on this device" button (removes every `novena-*` and `novenas-*` key, nothing else).
  - **About this site** section at the end of About: made by Chav, corrections and questions by email (hey.there.chav@gmail.com, also the Privacy page contact), a personal project and not an official Church publication; which prayers are traditional; the new prayers were written with the help of AI, aim to be faithful, have not been reviewed by a priest and carry no imprimatur; "Found a mistake?" links to GitHub issues for now.
  - Novena pages: desktop closing verse moved into the prayer column (the sticky sidebar used to run over it and the credits); sidebar fits 1024x768 and largest text; phone bar reads "← ✝ All novenas" (title shows from 601px; the link is only the arrow and cross there); hero cross hidden on phones so "Pray Day N" clears the day bar at 360px; a rubric "Where you see N., say the name…" on novenas that use N.; a first visit says "Begin on any day…" instead of "0 of 9"; Reset appears only once there is progress and reads "Begin a new round" after Day 9; "Mark Day N as prayed" is filled; after marking today's day, "Come back tomorrow for Day N+1."; secondary text follows the text-size setting (day buttons and controls capped at 1.15); saint stories run under the portrait on phones; litany line with no picture gets a quiet cross ring; opaque top bar; focus moves to the prayer heading after "Pray Day N" and prev/next; step names are h3 headings; skip link; text-size popover closes when focus leaves it; browser bar colour follows the Light/Dark toggle; `<title>` includes "| Catholic Novenas"; small gold numbers use `--gold-text` (AA).
  - Library: a novena in progress moves to the top, and its card names the same day the page opens ("Continue Day 3", "Pray Day 3", "Done for today"); 3 cards a row from 1200px; "Common questions" as heading-left, answers-right from 960px; "Learn more" outside the heading with a 44px target; skip link; theme and text size still work when storage is blocked.
  - About: first section's heading rule spans the page, "This site" jump link, smaller Angelus at 768px.
  - Offline: visits with `?fbclid=…` are cached under the plain address; offline, `/healing` (no slash) and unknown pages fall back to the saved copy or the library.
  - `netlify.toml`: a Content-Security-Policy that allows only the site's own files (checked locally: no violations on any page). Manifest: `id`, `scope`, `lang`. Debt novena's intention placeholder no longer says "your family". Helpline link is `noopener noreferrer`.
  - axe-core WCAG 2.2 AA: clean on every page (before: footer links outside a landmark on novena pages).
- **Footer and Privacy follow-ups** (Chav): footer privacy line removed (warning kept for browsers that cannot save); About credit "made by Chav" with hey.there.chav@gmail.com for corrections and questions; Privacy page "Visits and hosting" now says Netlify logs each request (time, page, referring site, browser type, IP address) and we see only totals; "No accounts, ads or cookies" replaces "…or tracking" in the Privacy page's description and link preview.

## Open items

1. **Go live:** link the Netlify project `catholic-novenas` to the repo (branch `main`, build command blank, publish directory `site`), then check catholic-novenas.netlify.app on a phone.
2. **Decide:** should prayers, reflections and steps also use digits? (Now: words.)
3. **Optional:** a personalized print copy of the healing novena with the person's name in place of "N.".
4. **Optional cleanup:** the old `catholic-novenas` branch on the novena-finances repo, and the scratch Google Doc used for image imports (`1P0v5bN3QCc97elk4VFMVbsgMDIxItOIKzT5k9Z97Bys`).
5. **Known v1 bug, left alone on purpose:** the novena-finances app drops "&" from day captions. Fixed in the library.

## Ideas to weigh (not decided)

- From the audit: a priest review of the new prayers (then update the About disclosure), an "add to calendar" reminder for the 9 days, novenas timed to feast days.
- When the family finishes their current round, point novena-finances to the library's debt novena so there is one version to maintain.
- Next intentions to consider: see the roadmap doc (https://claude.ai/artifact/Nuhwhpne8JEqxcwkwA9nDA). Print docs for the 4 new novenas are still to make.
