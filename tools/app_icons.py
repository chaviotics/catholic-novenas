#!/usr/bin/env python3
"""App icons: the "9 days" mark (wine cross inside a ring of 9 gold segments, one per day) on cream.

Writes into site/:
  favicon.svg            tab icon; switches to navy and pale gold when the browser is in dark mode
  favicon.ico            16, 32 and 48 px, for browsers and crawlers that ask for /favicon.ico
  apple-touch-icon.png   180 px, square (iOS rounds the corners)
  icon-192.png, icon-512.png
  icon-maskable-512.png  the mark at 80% so Android's circle or squircle crop never cuts the ring

Run once after changing the design (python3 tools/app_icons.py), then tools/build.py.
PNGs are drawn by Chromium through Playwright: Python Playwright if installed, otherwise Node's.
No name or initials in the icon, so it survives a rename.
"""
import io, json, math, os, shutil, subprocess, sys, tempfile

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")

LIGHT = {"bg": "#FFFDF9", "cross": "#6E1F2B", "gold": "#94702A"}   # cream, wine, gold
DARK = {"bg": "#0E1524", "cross": "#EBCF95", "gold": "#C9A45A"}    # the site's dark theme


def cross(cx=32, y0=16.5, y1=47.5, bar=7.5, arm=21, cy=23.5):
    """Latin cross path in a 64 x 64 box; cy is the top of the crossbar"""
    a = arm / 2 - bar / 2
    return ("M{} {}h{}v{}h{}v{}h-{}v{}h-{}v-{}h-{}v-{}h{}z"
            .format(cx - bar / 2, y0, bar, cy - y0, a, bar, a, y1 - cy - bar, bar, y1 - cy - bar, a, bar, a))


def ring(r=25, gap=14):
    """9 arcs, a gap centred at the top, each 40 degrees minus the gap"""
    def p(deg):
        t = math.radians(deg)
        return "{:.2f} {:.2f}".format(32 + r * math.cos(t), 32 + r * math.sin(t))
    out = []
    for i in range(9):
        a0 = -90 + i * 40 + gap / 2
        out.append("M{}A{} {} 0 0 1 {}".format(p(a0), r, r, p(a0 + 40 - gap)))
    return "".join(out)


def mark(c=None):
    """the ring and the cross; colours inline (c) or from the favicon's classes (None)"""
    g = ' stroke="%s"' % c["gold"] if c else ' class="g"'
    x = ' fill="%s"' % c["cross"] if c else ' class="c"'
    return ('<path%s fill="none" stroke-width="4" stroke-linecap="round" d="%s"/><path%s d="%s"/>'
            % (g, ring(), x, cross()))


def svg(c, rx=0, scale=1.0, size=None):
    t = 32 * (1 - scale)
    wh = ' width="%d" height="%d"' % (size, size) if size else ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"%s><rect width="64" height="64" rx="%s" fill="%s"/>'
            '<g transform="translate(%s %s) scale(%s)">%s</g></svg>' % (wh, rx, c["bg"], t, t, scale, mark(c)))


def favicon_svg():
    css = (".b{fill:%s}.g{stroke:%s}.c{fill:%s}"
           "@media (prefers-color-scheme:dark){.b{fill:%s}.g{stroke:%s}.c{fill:%s}}"
           % (LIGHT["bg"], LIGHT["gold"], LIGHT["cross"], DARK["bg"], DARK["gold"], DARK["cross"]))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><style>%s</style>'
            '<rect class="b" width="64" height="64" rx="14"/>%s</svg>\n' % (css, mark()))


# name -> (svg, pixel size, transparent corners?)
def pngs():
    return {
        "apple-touch-icon.png": (svg(LIGHT), 180),
        "icon-192.png": (svg(LIGHT), 192),
        "icon-512.png": (svg(LIGHT), 512),
        "icon-maskable-512.png": (svg(LIGHT, scale=0.8), 512),
        "ico-16.png": (svg(LIGHT, rx=14), 16),
        "ico-32.png": (svg(LIGHT, rx=14), 32),
        "ico-48.png": (svg(LIGHT, rx=14), 48),
    }


NODE = r"""
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const jobs=JSON.parse(fs.readFileSync(process.argv[1],'utf8'));const b=await chromium.launch();
for(const [out,svg,size] of jobs){const p=await b.newPage({viewport:{width:size,height:size}});
await p.setContent('<html><body style="margin:0;background:transparent">'+svg.replace('<svg ','<svg width="'+size+'" height="'+size+'" style="display:block" ')+'</body></html>');
await p.screenshot({path:out,omitBackground:true});await p.close();}await b.close();})();
"""


def render(jobs):
    """jobs: [(out_path, svg, size)] -> PNG files, drawn by Chromium"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sync_playwright = None
    if sync_playwright:
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            for out, s, size in jobs:
                p = b.new_page(viewport={"width": size, "height": size})
                p.set_content('<html><body style="margin:0;background:transparent">%s</body></html>'
                              % s.replace("<svg ", '<svg width="%d" height="%d" style="display:block" ' % (size, size), 1))
                p.screenshot(path=out, omit_background=True)
                p.close()
            b.close()
        return
    if not shutil.which("node"):
        raise SystemExit("needs Playwright (Python) or Node with playwright")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(jobs, f)
    try:
        subprocess.run(["node", "-e", NODE, f.name], check=True)
    finally:
        os.unlink(f.name)


def main():
    with open(os.path.join(SITE, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(favicon_svg())
    tmp = tempfile.mkdtemp()
    jobs = [(os.path.join(tmp, n), s, size) for n, (s, size) in pngs().items()]
    render(jobs)
    for n in pngs():
        src = os.path.join(tmp, n)
        if n.startswith("ico-"):
            continue
        im = Image.open(src).convert("RGB")  # home-screen icons: no transparency (iOS fills it with black)
        im.save(os.path.join(SITE, n), optimize=True)
        print("wrote", n, os.path.getsize(os.path.join(SITE, n)), "bytes")
    icos = [Image.open(os.path.join(tmp, "ico-%d.png" % s)).convert("RGBA") for s in (16, 32, 48)]
    icos[-1].save(os.path.join(SITE, "favicon.ico"), sizes=[(16, 16), (32, 32), (48, 48)], append_images=icos[:-1])
    print("wrote favicon.ico", os.path.getsize(os.path.join(SITE, "favicon.ico")), "bytes")
    shutil.rmtree(tmp)


if __name__ == "__main__":
    main()
