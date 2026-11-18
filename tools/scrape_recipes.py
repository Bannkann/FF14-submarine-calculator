# -*- coding: utf-8 -*-
"""从灰机 wiki 抓取 40 个潜水艇部件的「部队合建配方」。

数据页：https://ff14.huijiwiki.com/wiki/部队潜水艇
物品页：https://ff14.huijiwiki.com/wiki/物品:<部件全名>

只读公开页面，走 api.php 的 parse 接口拿渲染后的 HTML，再解析配方表。
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

import lxml.html

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
API = "https://ff14.huijiwiki.com/api.php"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = os.path.join(ROOT, "data", "parts.json")
OUT = os.path.join(ROOT, "data", "recipes.json")


def fetch_html(title, attempts=4):
    q = urllib.parse.urlencode({
        "action": "parse",
        "page": title,
        "prop": "text",
        "format": "json",
        "formatversion": "2",
    })
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(API + "?" + q, headers={
                "User-Agent": UA,
                "Accept": "*/*",
                "Referer": "https://ff14.huijiwiki.com/",
            })
            raw = urllib.request.urlopen(req, timeout=30).read()
            payload = json.loads(raw.decode("utf-8"))
            return payload["parse"]["text"]
        except Exception as exc:
            last = exc
            time.sleep(1.5 * (i + 1))
    raise last


def parse_recipe(html, name):
    doc = lxml.html.fromstring(html)
    tables = doc.xpath('//table[contains(@class,"item-craft-table")]')
    if not tables:
        return None
    table = tables[0]
    text = table.text_content()

    design = None
    m = re.search(r"解锁设计图\s*(潜水艇设计图\s*\d+)", re.sub(r"\s+", " ", text))
    if m:
        design = re.sub(r"\s+", "", m.group(1))

    steps = None
    m = re.search(r"步骤数\s*(\d+)", re.sub(r"\s+", " ", text))
    if m:
        steps = int(m.group(1))

    materials = []
    seen = set()
    for num_span in table.xpath('.//span[contains(@class,"item-number")]'):
        li = num_span
        while li is not None and li.tag != "li":
            li = li.getparent()
        if li is None:
            continue
        q = re.search(r"(\d+)", num_span.text_content())
        if not q:
            continue
        names = li.xpath('.//span[@class="item-name"]')
        if not names:
            continue
        mat = names[0].text_content().strip()
        # 跳过行首的成品自身
        if mat == name:
            continue
        if mat in seen:
            continue
        seen.add(mat)
        materials.append({"名称": mat, "数量": int(q.group(1))})
    return {"部件": name, "解锁设计图": design, "步骤数": steps, "材料": materials}


def main(argv):
    with open(PARTS, encoding="utf-8") as f:
        parts = json.load(f)

    missing_mode = "--missing" in argv
    only = None if missing_mode else (argv[0] if argv else None)
    results = {}
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            results = {r["部件"]: r for r in json.load(f)}

    targets = [p["全名"] for p in parts]
    if missing_mode:
        targets = [t for t in targets if t not in results]
    elif only:
        targets = [t for t in targets if only in t]

    for i, name in enumerate(targets, 1):
        try:
            html = fetch_html("物品:" + name)
            rec = parse_recipe(html, name)
        except Exception as exc:  # 网络/解析失败要显式报告，不静默跳过
            print("[%d/%d] FAIL %s: %s: %s" % (i, len(targets), name, type(exc).__name__, exc))
            continue
        if not rec or not rec["材料"]:
            print("[%d/%d] EMPTY %s" % (i, len(targets), name))
            continue
        results[name] = rec
        print("[%d/%d] %s  设计图=%s  材料%d项: %s" % (
            i, len(targets), name, rec["解锁设计图"], len(rec["材料"]),
            " ".join("%s×%d" % (m["名称"], m["数量"]) for m in rec["材料"])))
        time.sleep(1.1)

    ordered = [results[p["全名"]] for p in parts if p["全名"] in results]
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(ordered, f, ensure_ascii=False, indent=2)
    print("\n保存 %d 条 -> %s" % (len(ordered), OUT))
    missing = [p["全名"] for p in parts if p["全名"] not in results]
    if missing:
        print("缺失 %d 条: %s" % (len(missing), ", ".join(missing)))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
