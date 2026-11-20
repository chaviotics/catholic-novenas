#!/usr/bin/env python3
"""Make the 1200x630 link-preview images (og.png) for the library and each novena.

  python3 tools/og.py            # every novena + the library (site/og.png)
  python3 tools/og.py healing    # one novena -> novenas/healing/og.png

Run tools/build.py afterwards so the images are copied into site/.
"""
import asyncio, base64, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from shots import font_css  # noqa: E402

CSS = """
*{box-sizing:border-box}html,body{margin:0}
body{width:1200px;height:630px;background:#FFFDF9;font-family:'EB Garamond',Georgia,serif;color:#2A2521;display:flex;align-items:center;justify-content:center}
.card{width:1200px;height:630px;border-top:14px solid #94702A;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:40px 90px}
.cross{color:#6E1F2B;font-size:44px;line-height:1}
.kick{margin:14px 0 0;font-size:22px;letter-spacing:.16em;font-weight:600;color:#94702A;text-transform:uppercase}
h1{font-family:'Cormorant Garamond',Garamond,serif;font-weight:700;color:#6E1F2B;font-size:76px;line-height:1.02;margin:14px 0 14px;text-wrap:balance}
.sub{font-family:'Cormorant Garamond',Garamond,serif;font-style:italic;font-weight:500;font-size:32px;color:#675E57;margin:0}
.faces{display:flex;justify-content:center;margin-top:28px}
.faces img{width:96px;height:96px;border-radius:50%;object-fit:cover;border:4px solid #FFFDF9;margin:0 -8px;box-shadow:0 0 0 2px #9C8B70}
.site{position:absolute;bottom:26px;left:0;right:0;font-size:20px;letter-spacing:.14em;color:#675E57;text-transform:uppercase}
"""


def data(p):
    with open(p, "rb") as f:
        return "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()


def card_html(kick, title, sub, faces):
    imgs = "".join('<img src="%s">' % data(f) for f in faces)
    return ("<html><head><style>%s%s</style></head><body><div class='card'><div class='cross'>&#10013;</div>"
            "<p class='kick'>%s</p><h1>%s</h1><p class='sub'>%s</p><div class='faces'>%s</div>"
            "<div class='site'>catholic-novenas.netlify.app</div></div></body></html>") % (font_css(), CSS, kick, title, sub, imgs)


async def render(pairs):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = await b.new_page(viewport={"width": 1200, "height": 630})
        for htmlstr, out in pairs:
            await pg.set_content(htmlstr); await pg.wait_for_timeout(400)
            await pg.screenshot(path=out)
            print("wrote", out)
        await b.close()


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    pairs, all_faces = [], []
    base = os.path.join(ROOT, "novenas")
    for slug in sorted(os.listdir(base)):
        p = os.path.join(base, slug, "novena.json")
        if not os.path.exists(p):
            continue
        n = json.load(open(p, encoding="utf-8"))
        faces = [os.path.join(base, slug, "img", s["id"] + "_face.jpg") for s in n["saints"]]
        if n.get("status") == "published":
            all_faces += faces
        if only and slug != only:
            continue
        names = [s["name"] for s in n["saints"]]
        sub = "through " + (names[0] if len(names) == 1 else ", ".join(names[:-1]) + " &amp; " + names[-1])
        pairs.append((card_html(n["kicker"], n["barTitle"], sub, faces), os.path.join(base, slug, "og.png")))
    if not only:
        pairs.append((card_html("9 days of prayer", "Catholic Novenas",
                                "Pray with your family, one day at a time", all_faces[:6]), os.path.join(ROOT, "site", "og.png")))
    asyncio.run(render(pairs))


if __name__ == "__main__":
    main()
