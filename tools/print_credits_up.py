#!/usr/bin/env python3
"""One-time layout change: move the Scripture notice and image credits from the end of the print Doc
to the bottom of page 1 (under the intention box), and tidy the ending (no rule under the closing verse,
slightly tighter "Graces" lines). This frees about 70pt on page 4.

  python3 tools/print_credits_up.py <read_doc.json> <tabId>  > requests.json
The current template already has this layout; it is kept for documents copied from an older template.
"""
import json, sys

def main(path, tab):
    d = json.load(open(path, encoding="utf-8")); d = d.get("content", d)
    t = [x for x in d["tabs"] if x["tabProperties"]["tabId"] == tab][0]["documentTab"]
    paras = []
    def walk(els):
        for el in els:
            if "paragraph" in el: paras.append(el)
            elif "table" in el:
                for r in el["table"]["tableRows"]:
                    for c in r["tableCells"]: walk(c["content"])
    walk(t["body"]["content"])
    pt = lambda p: "".join(e.get("textRun", {}).get("content", "") if "textRun" in e else "￼" for e in p["paragraph"]["elements"])
    last = lambda pre: [p for p in paras if pt(p).startswith(pre)][-1]
    u16 = lambda s: len(s.encode("utf-16-le")) // 2
    R = lambda a, b: {"startIndex": a, "endIndex": b, "tabId": tab}
    notice, cred, dp = last("Scripture quotations are from"), last("Images"), last("Daily Prayers")
    assert notice["startIndex"] > dp["startIndex"], "credits already moved"
    cite = paras[paras.index(notice) - 1]
    clos = paras[paras.index(cite) - 2]
    lines = [p for p in paras if pt(p) in (" \n", " \n") and p["startIndex"] > dp["startIndex"]][-3:]
    RULE = {"red": 0.56078434, "green": 0.50980395, "blue": 0.4392157}; GOLD = {"red": 0.5803922, "green": 0.4392157, "blue": 0.16470589}
    MUTED = {"red": 0.4039, "green": 0.3686, "blue": 0.3412}
    zero = lambda c: {"width": {"magnitude": 0, "unit": "PT"}, "color": {"color": {"rgbColor": c}}, "padding": {"magnitude": 0, "unit": "PT"}, "dashStyle": "SOLID"}
    # keep the credit runs (italics) by copying them as segments
    segs = [(e["textRun"]["content"].rstrip("\n"), bool(e["textRun"].get("textStyle", {}).get("italic"))) for e in cred["paragraph"]["elements"] if "textRun" in e]
    NOTICE = pt(notice).rstrip("\n"); CRED = "".join(s for s, _ in segs)
    reqs = [
        {"deleteContentRange": {"range": R(cite["endIndex"] - 1, cred["endIndex"] - 1)}},
        {"updateParagraphStyle": {"range": R(cite["startIndex"], cite["startIndex"] + 1), "paragraphStyle": {"spaceAbove": {"magnitude": 0, "unit": "PT"}, "spaceBelow": {"magnitude": 4, "unit": "PT"}, "alignment": "CENTER"}, "fields": "spaceAbove,spaceBelow,alignment"}},
        {"updateTextStyle": {"range": R(cite["startIndex"], cite["endIndex"] - 1), "textStyle": {"fontSize": {"magnitude": 8, "unit": "PT"}}, "fields": "fontSize"}},
        {"updateParagraphStyle": {"range": R(clos["startIndex"], clos["startIndex"] + 1), "paragraphStyle": {"borderBottom": zero(RULE), "borderBetween": zero(RULE), "spaceAbove": {"magnitude": 14, "unit": "PT"}, "spaceBelow": {"magnitude": 0, "unit": "PT"}}, "fields": "borderBottom,borderBetween,spaceAbove,spaceBelow"}},
    ]
    for p in lines:
        reqs.append({"updateParagraphStyle": {"range": R(p["startIndex"], p["startIndex"] + 1), "paragraphStyle": {"spaceAbove": {"magnitude": 10, "unit": "PT"}}, "fields": "spaceAbove"}})
    at = dp["startIndex"]
    reqs.append({"insertText": {"location": {"index": at, "tabId": tab}, "text": NOTICE + "\n" + CRED + "\n"}})
    a1, b1 = at, at + u16(NOTICE) + 1; a2, b2 = b1, b1 + u16(CRED) + 1
    ps = {"pageBreakBefore": False, "borderBottom": zero(GOLD), "borderTop": zero(GOLD), "alignment": "CENTER", "spaceBelow": {"magnitude": 0, "unit": "PT"},
          "keepWithNext": False, "indentStart": {"magnitude": 36, "unit": "PT"}, "indentEnd": {"magnitude": 36, "unit": "PT"},
          "indentFirstLine": {"magnitude": 36, "unit": "PT"}, "lineSpacing": 100, "namedStyleType": "NORMAL_TEXT"}
    reqs += [
        {"updateParagraphStyle": {"range": R(a1, b2), "paragraphStyle": ps, "fields": ",".join(ps)}},
        {"updateParagraphStyle": {"range": R(a1, b1), "paragraphStyle": {"spaceAbove": {"magnitude": 22, "unit": "PT"}}, "fields": "spaceAbove"}},
        {"updateParagraphStyle": {"range": R(a2, b2), "paragraphStyle": {"spaceAbove": {"magnitude": 4, "unit": "PT"}}, "fields": "spaceAbove"}},
        {"updateTextStyle": {"range": R(a1, b2 - 1), "textStyle": {"fontSize": {"magnitude": 7.5, "unit": "PT"}, "bold": False, "italic": False, "smallCaps": False, "foregroundColor": {"color": {"rgbColor": MUTED}}, "weightedFontFamily": {"fontFamily": "EB Garamond", "weight": 400}}, "fields": "fontSize,bold,italic,smallCaps,foregroundColor,weightedFontFamily"}},
    ]
    pos = a2
    for s, it in segs:
        if it:
            reqs.append({"updateTextStyle": {"range": R(pos, pos + u16(s)), "textStyle": {"italic": True}, "fields": "italic"}})
        pos += u16(s)
    json.dump({"revisionId": d["revisionId"], "requests": reqs}, sys.stdout, ensure_ascii=False)

if __name__ == "__main__":
    main(*sys.argv[1:])
