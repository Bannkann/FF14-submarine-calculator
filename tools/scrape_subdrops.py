# -*- coding: utf-8 -*-
"""抓取灰机 wiki 的潜水艇掉落页，收集「潜水艇带取」的物品。

页数很少（7 个海域），每次请求间隔 2 秒以上，避免给对方造成压力。
输出：data/subdrops.json  [itemId, ...]
"""
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scrape_recipes as sr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "subdrops.json")

SEAS = ["溺没海", "灰海", "翠浪海", "妖歌海", "紫礁海", "南苍茫洋", "北洋"]


def main():
    ids = set()
    for i, sea in enumerate(SEAS, 1):
        title = "部队潜水艇/掉落/" + sea
        try:
            html = sr.fetch_html(title)
        except Exception as exc:
            print("[%d/%d] %s FAIL %s" % (i, len(SEAS), sea, exc))
            continue
        found = set(int(x) for x in re.findall(r'data-name="(\d+)"', html))
        ids |= found
        print("[%d/%d] %s -> %d 个物品" % (i, len(SEAS), sea, len(found)))
        time.sleep(2.0)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(sorted(ids), f)
    print("合计 %d 个物品 -> %s" % (len(ids), OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
