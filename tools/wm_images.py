#!/usr/bin/env python3
"""Get Wikimedia Commons images into the workspace (the sandbox can't reach Wikimedia directly).

Step 1: print Docs requests that insert the images into a scratch tab:
  python3 tools/wm_images.py requests <tabId> "File_one.jpg" "File two.jpg" ... [--width 800]
  -> send with Docs update_doc (insertInlineImage needs URLs Google can fetch; Wikimedia thumbs work).
     Thumbs can't be wider than the original; use a smaller --width if a request fails.

Step 2: export that Doc with Drive download_file_content, exportMimeType "application/zip", then:
  python3 tools/wm_images.py unzip <export.zip> <outdir>
  -> writes the images in insertion order as 01.jpg, 02.jpg, ... (matching the files you passed)

Step 3: delete the scratch tab (deleteTab) and crop with PIL:
  portrait 480x600 (img/<id>.jpg), face 112x112 (img/<id>_face.jpg), JPEG quality 85.
"""
import hashlib, json, os, re, sys, urllib.parse, zipfile


def thumb(name, width=800):
    name = name.replace(" ", "_")
    if name.lower().startswith("file:"):
        name = name[5:]
    h = hashlib.md5(name.encode("utf-8")).hexdigest()
    q = urllib.parse.quote(name)
    return "https://upload.wikimedia.org/wikipedia/commons/thumb/%s/%s/%s/%dpx-%s" % (h[0], h[:2], q, width, q)


def requests(tab, names, width):
    reqs = []
    for n in names:
        reqs.append({"insertText": {"endOfSegmentLocation": {"tabId": tab}, "text": "\n" + n + "\n"}})
        reqs.append({"insertInlineImage": {"endOfSegmentLocation": {"tabId": tab}, "uri": thumb(n, width),
                                           "objectSize": {"width": {"magnitude": 200, "unit": "PT"}}}})
    return reqs


def unzip(zpath, outdir):
    os.makedirs(outdir, exist_ok=True)
    z = zipfile.ZipFile(zpath)
    html = [n for n in z.namelist() if n.endswith(".html")][0]
    page = z.read(html).decode("utf-8", "replace")
    order = re.findall(r'src="(images/[^"]+)"', page)
    seen = []
    for o in order:
        if o not in seen:
            seen.append(o)
    for i, o in enumerate(seen, 1):
        data = z.read(o)
        ext = os.path.splitext(o)[1] or ".jpg"
        with open(os.path.join(outdir, "%02d%s" % (i, ext)), "wb") as f:
            f.write(data)
        print("%02d%s" % (i, ext), len(data) // 1024, "KB", o)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "requests":
        w = 800
        if "--width" in a:
            k = a.index("--width"); w = int(a[k + 1]); del a[k:k + 2]
        print(json.dumps(requests(a[1], a[2:], w), ensure_ascii=False))
    elif a and a[0] == "unzip":
        unzip(a[1], a[2])
    elif a and a[0] == "url":
        for n in a[1:]:
            print(thumb(n))
    else:
        print(__doc__)
