#!/usr/bin/env python3
"""Phone screenshots of the built site, light and dark, for a visual check.

  python3 tools/shots.py              # library home page
  python3 tools/shots.py healing      # one novena: hero, day 1, a poetry day, day 9, intercessors, close

Needs Playwright (pip install playwright) and Google Chrome at /usr/bin/google-chrome.
Google Fonts may be unreachable in a sandbox, so local copies are injected when present:
  npm i --prefix /home/claude/fontpkg @expo-google-fonts/eb-garamond @expo-google-fonts/cormorant-garamond
Writes PNGs to out/shots/ and prints any page errors.
"""
import asyncio, functools, http.server, json, os, sys, threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out", "shots")
F = "file:///home/claude/fontpkg/node_modules/@expo-google-fonts/"
FACES = [("Cormorant Garamond", 700, "normal", "cormorant-garamond/700Bold/CormorantGaramond_700Bold.ttf"),
         ("Cormorant Garamond", 600, "normal", "cormorant-garamond/600SemiBold/CormorantGaramond_600SemiBold.ttf"),
         ("Cormorant Garamond", 500, "italic", "cormorant-garamond/500Medium_Italic/CormorantGaramond_500Medium_Italic.ttf"),
         ("EB Garamond", 400, "normal", "eb-garamond/400Regular/EBGaramond_400Regular.ttf"),
         ("EB Garamond", 400, "italic", "eb-garamond/400Regular_Italic/EBGaramond_400Regular_Italic.ttf"),
         ("EB Garamond", 600, "normal", "eb-garamond/600SemiBold/EBGaramond_600SemiBold.ttf")]


def font_css():
    out = []
    for fam, w, st, path in FACES:
        if os.path.exists(F.replace("file://", "") + path):
            out.append("@font-face{font-family:'%s';font-weight:%d;font-style:%s;src:url('%s%s')}" % (fam, w, st, F, path))
    return "".join(out)


def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    h = functools.partial(Quiet, directory=os.path.join(ROOT, "site"))
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    return s


async def main(slug):
    from playwright.async_api import async_playwright
    os.makedirs(OUT, exist_ok=True)
    srv = serve(); base = "http://127.0.0.1:%d/" % srv.server_port
    css = font_css(); errs = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--allow-file-access-from-files"])
        for scheme in ("light", "dark"):
            pg = await b.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=2, color_scheme=scheme)
            pg.on("pageerror", lambda e: errs.append(str(e)))
            url = base + (slug + "/" if slug else "")
            await pg.goto(url); await pg.add_style_tag(content=css); await pg.wait_for_timeout(700)
            tag = (slug or "library") + "_" + scheme
            await pg.screenshot(path=os.path.join(OUT, tag + "_0top.png"))
            if not slug:
                await pg.evaluate("document.querySelector('.cards').scrollIntoView({block:'start'})"); await pg.evaluate("window.scrollBy(0,-70)")
                await pg.wait_for_timeout(200); await pg.screenshot(path=os.path.join(OUT, tag + "_1cards.png"))
                await pg.screenshot(path=os.path.join(OUT, tag + "_full.png"), full_page=True)
                continue
            days = json.loads(await pg.evaluate("JSON.stringify(Array.from(document.querySelectorAll('#track button')).length)"))
            poetry = None
            n = json.load(open(os.path.join(ROOT, "novenas", slug, "novena.json"), encoding="utf-8"))
            for i, d in enumerate(n["days"], 1):
                if " / " in d["verse"]:
                    poetry = i; break
            for label, day in (("1day1", 1), ("2poetry", poetry), ("3day9", 9)):
                if not day:
                    continue
                await pg.evaluate("document.querySelectorAll('#track button')[%d].click()" % (day - 1))
                await pg.evaluate("document.getElementById('dTitle').scrollIntoView({block:'start'})"); await pg.evaluate("window.scrollBy(0,-110)")
                await pg.wait_for_timeout(250); await pg.screenshot(path=os.path.join(OUT, "%s_%s.png" % (tag, label)))
            for label, sel in (("4litany", ".litany"), ("5saints", ".saints"), ("6close", ".close")):
                await pg.evaluate("document.querySelector('%s').scrollIntoView({block:'start'})" % sel); await pg.evaluate("window.scrollBy(0,-90)")
                await pg.wait_for_timeout(250); await pg.screenshot(path=os.path.join(OUT, "%s_%s.png" % (tag, label)))
        await b.close()
    srv.shutdown()
    print("shots in", OUT, "| page errors:", errs or "none")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else ""))
