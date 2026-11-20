---
name: novena-maker
description: Make a new nine-day Catholic novena for an intention (a phone app page in the Catholic Novenas library plus a 4-page Google Docs print layout). Use when the user names an intention for a novena or asks to add one to the library.
---

# Novena maker

From one intention, produce a novena in the **Catholic Novenas** library:

1. `novenas/<slug>/novena.json` and `novenas/<slug>/img/` in the repo
2. A page at `https://catholic-novenas.netlify.app/<slug>/`, with a card on the library home page
3. A Google Doc print layout of 4 pages or fewer, copied from the template doc
4. A short report: saints chosen and why, links, anything to decide

Every novena uses the same prayer structure and design. Only the content changes, so put the effort into the content and the checks.

## 0. Get set up

- **Repo:** `chaviotics/catholic-novenas`. If it doesn't exist yet, the code is on branch `catholic-novenas` of `chaviotics/novena-finances`. Never push to `main` of `novena-finances`: it is the family's live site.
- **Netlify:** site `catholic-novenas` (id `3902d84c-0c49-48e4-a0ed-e1a0c45e5d75`). Never deploy to `novena-finances` unless the user asks.
- **Read first:** `novenas/relief-from-debt/novena.json`. It is the approved example: match its tone, lengths and polish.
- **Tools:** `tools/build.py` (site and artifact), `tools/print_fill.py` (print doc requests), `tools/check_print.py` (print text check), `tools/shots.py` (screenshots). Read each one's docstring before using it.

## 1. Intention → saints

- Restate the intention in one line. Widen it only where that helps the person praying. For healing, that means body and spirit, the doctors and the caregivers. Keep the user's focus first.
- Suggest **1–3 intercessors**, and prefer 3:
  - **A Marian title** that fits the intention, such as Our Lady of Lourdes for the sick or Mary, Help of Christians.
  - **A saint with an established, traditional patronage** for this need.
  - **A saint whose own life mirrors the intention**, for example someone who suffered the same trial.
- Prefer canonized saints with well-known stories, and devotions loved in the Philippines when they fit. Say whether a patronage is traditional or official.
- Check that each saint has a public-domain image (step 5) before you settle on them.
- **If the user is present,** offer the choice with one-line reasons. **If they are unattended,** choose, and explain the choice in the report.
- **Slug:** short and lowercase, like `healing` or `relief-from-debt`. Make `storageKey` = `novena-<slug>`.

## 2. Fixed structure (the template handles it)

Each day runs in this order:

1. Opening Prayer (the same every day)
2. Scripture & Reflection (changes each day)
3. The day's Prayer, ending "(Name your intention.) Amen."
4. Closing Prayer: a litany (a Marian title, then each saint, each with "pray for us"), then the closing prayer, then the Memorare
5. Our Father, Hail Mary, Glory Be
6. Sign of the Cross
7. Today's step

**Memorare rule:** use the Marian Memorare (`"memorare": {"to": "Mary"}`; the builder supplies the text). Use the Memorare to St. Joseph (text in the debt example) only when St. Joseph is one of the intercessors.

## 3. Write `novena.json`

Copy the debt example's shape. Field rules:

| Field | Rule |
|---|---|
| `title` | "Novena for …", up to about 60 characters |
| `barTitle` / `barShort` | Shown in the top bar: up to 28 and up to 14 characters |
| `kicker` | "Nine days of …", up to 45 characters |
| `card` | One sentence for the library card, up to 140 characters |
| `description` | Meta description, up to 160 characters |
| `status` | `"draft"` (page builds, no library card) until the user approves, then `"published"` |
| `order` | Position on the library page |
| `epigraph`, `closingVerse` | RSV-CE, up to about 25 words each: `{"text", "ref"}` |
| `saints[]` | `id` (image file stem), `name`, `dates`, `feast`, `patron`, `bio` (up to 35 words, facts only), `alt` (describes the artwork), `openingRole` |
| `litany[]` | `{"img", "text"}`, Marian title first. `img` is optional and points to `img/<img>_face.jpg` |
| `openingPrayer` | 85–110 words. Addresses the Father, names the burden plainly, names each intercessor with a short role, ends "through Christ our Lord." The template adds "Amen." |
| `closingPrayer` | 25–40 words, addressed to Jesus. The template adds "Amen." |
| `tips` | Keep the debt example's "As a family" text word for word. "Alongside prayer" names the sacraments that fit (Confession, Mass, Anointing of the Sick…) and one prudent action for this intention |
| `icons` | 9 Phosphor "regular" icon names, one per day. They must exist in `tools/icons/`. Add new ones from `@phosphor-icons/core` (npm, assets/regular) |
| `credits` | Image credits: artist, *title*, date, collection, then "Public domain, via Wikimedia Commons." |
| `days[9]` | See below |

Each day has these fields:

- `title`: 2–5 words.
- `ref`: "Book c:v–v" with an en dash, and no "RSV-CE" (the template adds it).
- `verse`: RSV-CE, exact. Put " / " between poetry lines, and keep "LORD" in capitals (it shows in small caps).
- `refl`: paragraph 1, 75–95 words. It is printed. It opens from the verse into the person's life.
- `more`: paragraph 2, 55–75 words, app only. A saint's story, a teaching of the Church (cite CCC numbers only if certain), or a gentle application.
- `prayer`: 70–90 words. Says "we", names at least one intercessor, and stops before "(Name your intention.)".
- `step`: one concrete, doable action, up to 30 words.

**The arc of the days:** start with honest fear or need, then trust, then the specific graces asked for, and end on **Day 9: gratitude and surrender to God's will**. Day 9's step is always "Write down three graces you noticed during these nine days, and thank God for them together." The print layout has a "Graces I have noticed" box after it.

**Voice and faith rules:**
- Write in warm, plain US English, saying "we" for the family. Use the honorific capitals of the example: You, Your, Him.
- **Never promise outcomes.** No "this novena never fails" and no prosperity-gospel framing. Ask boldly, then trust God's will. For healing, also pray for strength, peace, the doctors' skill and the caregivers, and for the grace to unite suffering with Christ, without ever implying that the sick lack faith.
- Rotate the saints across the days so each gets about three days.
- **Only quote a saint with a well-attested line.** Otherwise paraphrase ("St. Pio often told people to pray, hope and not worry").
- Facts about saints must be ones you would stake your name on. If unsure, leave them out.

## 4. Verify every Scripture text (RSV-CE, word for word)

- Fetch each passage, including the epigraph and closing verse, from BibleGateway with WebFetch: `https://www.biblegateway.com/passage/?search=<Book+c:v-v>&version=RSVCE`. Ask for the exact text with no verse numbers, footnote letters or headings.
- Copy punctuation exactly, including "LORD" and "thee/thou" in Psalms. Check the verse range: the passage must not start or end in the middle of a quotation (a dangling quote mark means choose a different range).
- If a fetch looks paraphrased or partial, fetch it again or use a second RSV-CE source. Record what you verified in `novenas/<slug>/sources.md`.
- **Permission limits:** under 500 verses in total, no whole book, under 25% of any book. The required notice is already in the template.

## 5. Images (public domain only)

- Use Wikimedia Commons: paintings, sculpture, mosaics or icons by artists who died more than 100 years ago, and photos of such 2D works. Avoid modern devotional art and recent photographs.
- **Getting the files.** The workspace can't reach Wikimedia, so:
  1. Build the thumbnail URL: `https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{quote(name)}/960px-{quote(name)}`, where `h = md5(name)` and `name` uses underscores.
  2. Insert it with Docs `insertInlineImage` into a scratch tab of any working Doc (add one with `addDocumentTab`).
  3. Export that Doc with Drive `download_file_content`, `exportMimeType: "application/zip"`, and unzip `images/`.
  4. Delete the scratch tab.
- **Crop** with PIL: portrait `img/<id>.jpg` at 480×600 with the face in the upper third, and face `img/<id>_face.jpg` at 112×112, tight on the face. Use JPEG quality 85. For a litany-only image, such as a Marian title that isn't a saint card, make just `<id>_face.jpg`. Look at every crop.
- After deploy, the images are public at `https://catholic-novenas.netlify.app/<slug>/img/<id>.jpg`. Use these URLs for the print portraits.

## 6. Build and check the app

```
python3 tools/build.py                    # site/ (library + all novenas)
python3 tools/build.py --artifact <slug>  # out/<slug>.html, one self-contained file
python3 tools/shots.py <slug>             # phone screenshots, light and dark, into out/shots/
```

- Look at the screenshots: the hero (names should fit on 2 lines), Day 1, a poetry day, Day 9 and the closing.
- Optionally publish `out/<slug>.html` as a Claude artifact so the user can try it before it goes live.

## 7. Print layout (Google Docs, 4 pages or fewer)

- **Template:** Doc `1XUCutiQexpVtGP8w_eaT1nzfjXx3h6Xb-VrQNfrgkkU` ("Novena print template"), tab `t.m63jflj0vk3u`, in the Drive folder "[12] 🙏 Faith". It holds the approved debt layout: Folio pages, two columns from Daily Prayers on, EB Garamond. Never edit it; copy it.
- **Copy it** with Drive `copy_file`, named "<Title> — print". The template has one tab; keep it that way, because the PDF export renders every tab.
- **Fill it** with `tools/print_fill.py`. Read the copy (`read_doc`; the result is saved to a file), run the script on that file plus `novena.json`, and send the batch with `writeControl.requiredRevisionId` set to the read's `revisionId`. The script replaces text paragraph by paragraph, keeping every style. Print gets `refl` only; `more` stays in the app.
- **Portraits:** the script also swaps the three page-1 images for the deployed portrait URLs at 120pt height. For fewer than 3 saints, delete the extra table columns.
- **Check the layout.** Export a PDF (`download_file_content`, `application/pdf`), render it with `pdftoppm -r 80`, and look at every page. The rules:
  - 4 pages or fewer, with Daily Prayers starting page 2.
  - No day heading or title left alone at the bottom of a column.
  - Google Docs ignores "keep with next" inside columns, so fix strands by hand, top-down, re-exporting after each fix:
    - **At a page bottom:** set `pageBreakBefore` on that day's header paragraph.
    - **At a column bottom mid-page:** raise `spaceBelow` on the previous day's Today's-step paragraph, using the smallest value that works (usually 45–75pt). If the previous prayer and step jump to the next column, the value is too big.
- **Text check:** `python3 tools/check_print.py <pdf> <slug>` confirms every title, ref, verse, reflection, prayer and step appears in pages 1–4.

## 8. Review before publishing

- Run a Catholic content review, using the catholic-guide skill or a fresh subagent with no stake in the draft. It checks:
  - doctrine
  - saints' facts and dates
  - no superstition or guarantees
  - fitting sacraments
  - kindness to those who are not cured
  - correct titles
- Fix what holds up, rebuild, and check again.

## 9. Publish

1. Set `"status": "published"`, then run `python3 tools/build.py`.
2. Deploy `site/` to the Netlify site `catholic-novenas` (Netlify MCP `deploy-site`, run from the repo root; `netlify.toml` publishes `site/`).
3. Open the live page to confirm it works.
4. Commit and push. Commit messages carry no Co-Authored-By trailer.

## Report

Keep the report short:
- the saints and why they were chosen
- the live link and the print doc link
- what the reviews changed
- open questions, each with your recommendation
