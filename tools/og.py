#!/usr/bin/env python3
"""Make the 1200x630 link-preview images (og.jpg) for the library and each novena.

  python3 tools/og.py            # every novena + the library (site/og.jpg)
  python3 tools/og.py healing    # one novena -> novenas/healing/og.jpg

Run tools/build.py afterwards so the images are copied into site/.

Design for thumbnail size: chat apps show this image 300-500px wide, and WhatsApp
may crop it to a centered square. So the title is huge and stacked inside the
central 600px, and the two saint portraits sit at the edges, where a square crop
loses them harmlessly. No URL or small print: every app already shows the domain.

Portraits: novena.json may set "ogSaints": [left_id, right_id] so each saint faces
inward; otherwise the first and last saints are used.
"""
import asyncio, base64, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shots import font_css  # noqa: E402

# Colors: the site's Wine & Gold palette, on its cream page color (wine as a full background read too red)
CSS = """
*{box-sizing:border-box}html,body{margin:0}
body{width:1200px;height:630px;overflow:hidden;font-family:'Cormorant Garamond',Garamond,Georgia,serif;
  background:radial-gradient(ellipse 75% 95% at 50% 45%,#FFFDF9 0%,#FBF6EC 65%,#F3EADA 100%);color:#6E1F2B;
  border-top:14px solid #94702A}
.frame{position:absolute;inset:34px 22px 22px;border:2px solid #94702A;border-radius:6px}
.frame:after{content:"";position:absolute;inset:8px;border:1px solid rgba(148,112,42,.4);border-radius:3px}
.arch{position:absolute;top:100px;width:236px;height:430px;border-radius:118px 118px 8px 8px;overflow:hidden;
  border:4px solid #94702A;box-shadow:0 0 0 6px rgba(148,112,42,.14),0 12px 30px rgba(60,40,20,.28)}
.arch img{width:100%;height:100%;object-fit:cover}
.l{left:52px}.r{right:52px}
.mid{position:absolute;left:300px;width:600px;top:0;bottom:0;display:flex;flex-direction:column;
  align-items:center;justify-content:center;text-align:center;padding:30px 0 34px}
.cross{color:#6E1F2B;font-size:64px;line-height:1;margin-bottom:6px}
.pre{font-family:'EB Garamond',Georgia,serif;font-weight:600;font-size:34px;letter-spacing:.2em;
  text-transform:uppercase;color:#94702A;margin:6px 0 0}
h1{font-weight:700;font-size:150px;line-height:.9;margin:4px 0 0;letter-spacing:-.005em;color:#6E1F2B;max-width:580px;text-wrap:balance}
.rule{width:120px;height:2px;background:#94702A;margin:26px 0 20px}
.sub{font-style:italic;font-weight:600;font-size:46px;line-height:1.08;color:#4A3F38;margin:0;text-wrap:balance}
"""

# shrink the title until it fits the column in at most 2 lines, then the subtitle if the stack is too tall.
# Run after the web fonts load: measuring with the fallback font gives the wrong widths.
FIT = """async () => {
  await document.fonts.ready;
  const h = document.querySelector('h1'), mid = document.querySelector('.mid'), sub = document.querySelector('.sub');
  let s = 150;
  const lines = () => Math.round(h.getBoundingClientRect().height / (s * 0.9));
  while ((h.scrollWidth > 580 || lines() > 2) && s > 70) { s -= 4; h.style.fontSize = s + 'px'; }
  let t = 46;
  while (mid.scrollHeight > 630 && t > 34) { t -= 2; sub.style.fontSize = t + 'px'; }
}"""


def data(p):
    with open(p, "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()


def card_html(pre, title, sub, left, right):
    """left/right: (image path, CSS object-position)"""
    arch = lambda cls, img: '<div class="arch %s"><img src="%s" style="object-position:%s"></div>' % (cls, data(img[0]), img[1])
    return ("<html><head><meta charset='utf-8'><style>%s%s</style></head><body><div class='frame'></div>%s%s"
            "<div class='mid'><div class='cross'>&#10013;</div>%s<h1>%s</h1><div class='rule'></div>"
            "<p class='sub'>%s</p></div></body></html>") % (
        font_css(), CSS, arch("l", left), arch("r", right),
        "<p class='pre'>%s</p>" % pre if pre else "", title, sub)


async def render(pairs):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = await b.new_page(viewport={"width": 1200, "height": 630})
        for htmlstr, out in pairs:
            await pg.set_content(htmlstr); await pg.evaluate(FIT); await pg.wait_for_timeout(200)
            await pg.screenshot(path=out, type="jpeg", quality=88)
            print("wrote", out)
        await b.close()


def portrait(base, slug, sid, focus):
    return (os.path.join(base, slug, "img", sid + ".jpg"), focus.get(sid, "50% 30%"))


# where each face sits in its 480x600 portrait, so the arch crop keeps it
FOCUS = {"joseph": "62% 30%", "jude": "45% 30%", "rita": "55% 30%",
         "raphael": "55% 20%", "bernadette": "60% 25%", "camillus": "60% 25%"}


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    pairs, lib = [], {}
    base = os.path.join(ROOT, "novenas")
    for slug in sorted(os.listdir(base)):
        p = os.path.join(base, slug, "novena.json")
        if not os.path.exists(p):
            continue
        n = json.load(open(p, encoding="utf-8"))
        ids = n.get("ogSaints") or [n["saints"][0]["id"], n["saints"][-1]["id"]]
        if n.get("status") == "published":
            for sid in ids:
                lib[sid] = portrait(base, slug, sid, FOCUS)
        if only and slug != only:
            continue
        title = n["barTitle"]
        pre, word = ("Novena for", title[len("Novena for "):]) if title.startswith("Novena for ") else ("", title)
        sub = n["kicker"][0].upper() + n["kicker"][1:]
        pairs.append((card_html(pre, word, sub, portrait(base, slug, ids[0], FOCUS), portrait(base, slug, ids[1], FOCUS)),
                      os.path.join(base, slug, "og.jpg")))
    if not only:
        left = lib.get("joseph") or next(iter(lib.values()))
        right = lib.get("raphael") or list(lib.values())[-1]
        pairs.append((card_html("", "Pray a<br>Novena", "Catholic novenas for every intention", left, right),
                      os.path.join(ROOT, "site", "og.jpg")))
    asyncio.run(render(pairs))


if __name__ == "__main__":
    main()
