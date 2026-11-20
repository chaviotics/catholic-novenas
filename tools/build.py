#!/usr/bin/env python3
"""Build the novena library.

  python3 tools/build.py                 # builds site/ (library + every published novena)
  python3 tools/build.py --artifact SLUG # one self-contained HTML file (images inlined) in out/

Each novena lives in novenas/<slug>/ as novena.json plus img/<id>.jpg (portrait, 480x600)
and img/<id>_face.jpg (round avatar, 112x112) for every saint and litany image.
"""
import base64, html, json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_URL = "https://catholic-novenas.netlify.app"
ICON_DIRS = [os.path.join(ROOT, "tools", "icons")]
BASE_ICONS = ["cross", "sun", "moon", "text-aa", "check", "caret-down", "footprints", "hands-praying", "arrow-left", "book-open"]
NUMWORD = {1: "The Intercessor", 2: "The 2 Intercessors", 3: "The 3 Intercessors"}
MARIAN_MEMORARE = ("Remember, O most gracious Virgin Mary, that never was it known that anyone who fled to your protection, "
                   "implored your help, or sought your intercession was left unaided. Inspired by this confidence, I fly unto you, "
                   "O Virgin of virgins, my Mother. To you do I come; before you I stand, sinful and sorrowful. O Mother of the Word "
                   "Incarnate, despise not my petitions, but in your mercy hear and answer me.")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def esc(t):
    return html.escape(t, quote=True)


def icon_symbol(name):
    for d in ICON_DIRS:
        p = os.path.join(d, name + ".svg")
        if os.path.exists(p):
            body = re.search(r"<svg[^>]*>(.*)</svg>", read(p), re.S).group(1).strip()
            return '<symbol id="i-%s" viewBox="0 0 256 256">%s</symbol>' % (name, body)
    raise SystemExit("icon not found: " + name)


def sprite(names):
    seen, out = set(), []
    for n in names:
        if n not in seen:
            seen.add(n); out.append(icon_symbol(n))
    return '<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">' + "".join(out) + "</svg>"


def load_novenas():
    out = []
    base = os.path.join(ROOT, "novenas")
    for slug in sorted(os.listdir(base)):
        p = os.path.join(base, slug, "novena.json")
        if os.path.exists(p):
            n = json.loads(read(p))
            assert n["slug"] == slug, (slug, n["slug"])
            validate(n)
            out.append(n)
    out.sort(key=lambda n: n.get("order", 99))
    return out


def validate(n):
    req = ["slug", "storageKey", "title", "barTitle", "barShort", "kicker", "card", "description", "epigraph",
           "closingVerse", "saints", "litany", "openingPrayer", "closingPrayer", "memorare", "tips", "icons", "credits", "days"]
    miss = [k for k in req if k not in n]
    assert not miss, (n.get("slug"), "missing", miss)
    assert len(n["days"]) == 9 and len(n["icons"]) == 9, n["slug"]
    assert 1 <= len(n["saints"]) <= 3, n["slug"]
    for d in n["days"]:
        for k in ("title", "ref", "verse", "refl", "more", "prayer", "step"):
            assert d.get(k), (n["slug"], d.get("title"), k)
        assert "--" not in d["ref"] and "-" not in d["ref"].split(" ")[-1], ("use an en dash in refs", d["ref"])
    imgdir = os.path.join(ROOT, "novenas", n["slug"], "img")
    for s in n["saints"]:
        for f in (s["id"] + ".jpg", s["id"] + "_face.jpg"):
            assert os.path.exists(os.path.join(imgdir, f)), (n["slug"], "missing image", f)
    for l in n["litany"]:
        if l.get("img"):
            assert os.path.exists(os.path.join(imgdir, l["img"] + "_face.jpg")), (n["slug"], "missing face", l["img"])


def scripture(t):
    """escape, and show the divine name LORD in small caps as the RSV prints it"""
    return esc(t).replace("LORD", '<span class="sc">Lord</span>')


def saint_line(saints):
    names = [esc(s["name"]) for s in saints]
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + " &amp; " + names[-1]


def page(n, mode):
    """mode 'site' -> image files next to the page; mode 'artifact' -> inlined images, no library links."""
    slug = n["slug"]
    imgdir = os.path.join(ROOT, "novenas", slug, "img")

    def src(name):
        if mode == "artifact":
            with open(os.path.join(imgdir, name + ".jpg"), "rb") as f:
                return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()
        return "img/%s.jpg" % name

    faces = "".join('<img src="%s" alt="">' % src(s["id"] + "_face") for s in n["saints"])
    litany = "\n".join(
        '          <p>%s%s, <span class="resp">pray for us.</span></p>' % (
            ('<img class="av" src="%s" alt="">' % src(l["img"] + "_face")) if l.get("img") else "", esc(l["text"]))
        for l in n["litany"])
    saints = "\n".join(
        '      <article class="saint"><img class="portrait" src="%s" alt="%s" width="92" height="115"><div><h3>%s</h3>'
        '<p class="meta">%s · %s</p><p class="pat">%s</p><p>%s</p></div></article>' % (
            src(s["id"]), esc(s["alt"]), esc(s["name"]), esc(s["dates"]), esc(s["feast"]), esc(s["patron"]), esc(s["bio"]))
        for s in n["saints"])
    tips = "\n".join('      <div class="tip"><h3>%s</h3><p>%s</p></div>' % (esc(t["h"]), t["p"]) for t in n["tips"])
    mem = n["memorare"]
    mem_text = MARIAN_MEMORARE if mem.get("to") == "Mary" and not mem.get("text") else mem["text"]
    mem_title = "Memorare" if mem.get("to") == "Mary" else "Memorare to " + mem["to"]
    how_mem = "<strong>Memorare</strong>" + ("" if mem.get("to") == "Mary" else " to " + esc(mem["to"]))

    url = "%s/%s/" % (SITE_URL, slug)
    if mode == "site":
        head = "\n".join([
            '<meta name="description" content="%s">' % esc(n["description"]),
            '<meta name="theme-color" content="#FFFDF9" media="(prefers-color-scheme: light)">',
            '<meta name="theme-color" content="#0E1524" media="(prefers-color-scheme: dark)">',
            '<meta property="og:type" content="website">',
            '<meta property="og:site_name" content="Catholic Novenas">',
            '<meta property="og:url" content="%s">' % url,
            '<meta property="og:title" content="%s">' % esc(og_title(n)),
            '<meta property="og:description" content="%s">' % esc(n["description"]),
            '<meta property="og:image" content="%sog.jpg?v=%s">' % (url, og_ver(os.path.join(ROOT, "novenas", slug, "og.jpg"))),
            '<meta property="og:image:alt" content="%s">' % esc(n["barTitle"] + ": " + n["kicker"]),
            '<meta property="og:image:type" content="image/jpeg">',
            '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">',
            '<meta name="twitter:card" content="summary_large_image">',
            '<link rel="canonical" href="%s">' % url,
            '<link rel="icon" href="../favicon.svg" type="image/svg+xml">',
            '<link rel="apple-touch-icon" href="../apple-touch-icon.png">',
            '<link rel="manifest" href="../manifest.webmanifest">',
        ])
        back = ('    <a class="back" href="../index.html"><svg class="i" aria-hidden="true" focusable="false"><use href="#i-arrow-left"/></svg>'
                'All novenas</a>\n')
        foot = '<p class="more"><a href="../index.html">More novenas</a></p>\n'
        title_tag = esc(n["barTitle"])
        home = ('href="../index.html" aria-label="All novenas"', '<svg class="i back-ic" aria-hidden="true" focusable="false"><use href="#i-arrow-left"/></svg>')
    else:
        home = ('href="#top" aria-label="Back to top"', "")
        head, back, foot, title_tag = "", "", "", esc(n["barTitle"])
        home = ('href="#top" aria-label="Back to top"', "")

    vals = {
        "TITLE_TAG": title_tag, "HEAD_META": head, "BAR_TITLE": esc(n["barTitle"]), "BAR_SHORT": esc(n["barShort"]),
        "BACK_LINK": back, "FOOT_LINK": foot, "HOME_ATTRS": home[0], "HOME_ARROW": home[1], "KICKER": esc(n["kicker"]), "TITLE": esc(n["title"]),
        "SAINT_LINE": saint_line(n["saints"]), "EPI_TEXT": scripture(n["epigraph"]["text"]), "EPI_REF": esc(n["epigraph"]["ref"]),
        "FACES": faces, "DAY1_TITLE": esc(n["days"][0]["title"]), "OPENING_PRAYER": esc(n["openingPrayer"]),
        "INTENT_PH": esc(n.get("intentionPlaceholder", "Write the intention you are praying for.")),
        "LITANY": litany, "CLOSING_PRAYER": esc(n["closingPrayer"]), "MEMORARE_TITLE": esc(mem_title),
        "MEMORARE_TEXT": esc(mem_text), "HOW_MEMORARE": how_mem, "TIPS": tips,
        "SAINTS_HEAD": NUMWORD[len(n["saints"])], "SAINTS": saints, "CLOSE_TEXT": scripture(n["closingVerse"]["text"]),
        "CLOSE_REF": esc(n["closingVerse"]["ref"]), "CREDITS": n["credits"],
        "ICONS": json.dumps(n["icons"]), "KEY": json.dumps(n["storageKey"] + ("-artifact" if mode == "artifact" else "")),
        "DAYS": json.dumps(n["days"], ensure_ascii=False),
        "SPRITE": sprite(BASE_ICONS + n["icons"]),
    }
    t = read(os.path.join(ROOT, "templates", "novena.html"))
    for k, v in vals.items():
        t = t.replace("{{%s}}" % k, v)
    left = re.findall(r"\{\{[A-Z0-9_]+\}\}", t)
    assert not left, left
    return t


def og_title(n):
    """a fuller link-preview title: add the site name when it still fits in 60 characters"""
    t = n["title"] + " | Catholic Novenas"
    return t if len(t) <= 60 else n["title"]


def og_ver(path):
    """short content hash, so chat apps fetch a changed og.jpg instead of their cached copy"""
    import hashlib
    if not os.path.exists(path):
        return "0"
    with open(path, "rb") as f:
        return hashlib.sha1(f.read()).hexdigest()[:8]


def library(novenas):
    t = read(os.path.join(ROOT, "templates", "library.html"))
    cards, icons = [], []
    for n in novenas:
        if n.get("status") != "published":
            continue
        icons.append(n.get("icon", "cross"))
        faces = "".join('<img src="%s/img/%s_face.jpg" alt="" width="36" height="36">' % (n["slug"], s["id"]) for s in n["saints"])
        title = n.get("cardTitle") or re.sub(r"^Novena for (the )?", "", n["title"])
        names = ['<span class="nb">%s</span>' % esc(x["name"]) for x in n["saints"]]
        through = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " &amp;&nbsp;" + names[-1]
        blurb = re.sub(r"(\d) ", r"\1&nbsp;", esc(n["card"]))
        sl = n["slug"]
        cards.append(
            '<li class="card" data-key="%s"><a href="%s/index.html" aria-labelledby="t-%s p-%s">'
            '<div class="top"><span class="ic" aria-hidden="true"><svg class="i"><use href="#i-%s"/></svg></span>'
            '<div class="faces" aria-hidden="true">%s</div></div>'
            '<h3 id="t-%s">%s</h3><p class="through">through %s</p>'
            '<p class="blurb">%s</p>'
            '<div class="foot"><p class="prog" id="p-%s"></p>'
            '<span class="go" aria-hidden="true"><span>Pray</span><svg class="i"><use href="#i-arrow-right"/></svg></span></div></a></li>' % (
                esc(n["storageKey"]), sl, sl, sl, n.get("icon", "cross"), faces, sl, esc(title), through, blurb, sl))
    t = t.replace("{{CARDS}}", "\n".join(cards))
    t = t.replace("{{OG_VER}}", og_ver(os.path.join(ROOT, "site", "og.jpg")))
    t = t.replace("{{SPRITE}}", sprite(["cross", "sun", "moon", "text-aa", "arrow-right", "hands-praying", "calendar-check", "users"] + icons))
    left = re.findall(r"\{\{[A-Z0-9_]+\}\}", t)
    assert not left, left
    return t


def build_site():
    novenas = load_novenas()
    site = os.path.join(ROOT, "site")
    for n in novenas:
        d = os.path.join(site, n["slug"])
        if os.path.isdir(d):
            shutil.rmtree(d)
        if n.get("status") not in ("published", "draft"):
            continue
        os.makedirs(os.path.join(d, "img"))
        for f in os.listdir(os.path.join(ROOT, "novenas", n["slug"], "img")):
            shutil.copy(os.path.join(ROOT, "novenas", n["slug"], "img", f), os.path.join(d, "img", f))
        og = os.path.join(ROOT, "novenas", n["slug"], "og.jpg")
        if os.path.exists(og):
            shutil.copy(og, os.path.join(d, "og.jpg"))
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(page(n, "site"))
        print("built", n["slug"], n.get("status"))
    with open(os.path.join(site, "index.html"), "w", encoding="utf-8") as f:
        f.write(library(novenas))
    print("built library with", sum(1 for n in novenas if n.get("status") == "published"), "published novenas")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--artifact":
        n = [x for x in load_novenas() if x["slug"] == sys.argv[2]][0]
        os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
        p = os.path.join(ROOT, "out", n["slug"] + ".html")
        with open(p, "w", encoding="utf-8") as f:
            f.write(page(n, "artifact"))
        print(p, os.path.getsize(p) // 1024, "KB")
    else:
        build_site()
