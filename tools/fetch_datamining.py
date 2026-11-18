# -*- coding: utf-8 -*-
"""下载中文数据包（ffxiv-datamining-cn）里本项目需要的 CSV。

首次使用、或想更新数据时跑一次即可：
    python tools/fetch_datamining.py
已存在的文件会跳过；加 --force 可强制重新下载。
"""
import os
import sys
import urllib.request

BASE = "https://raw.githubusercontent.com/thewakingsands/ffxiv-datamining-cn/master/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
UA = "FF14-sub-calc/1.0 (personal tool)"

# 这些表分别在哪些脚本里用到
FILES = [
    "Item.csv",              # build_graph / build_tags（名称、NPC 售价）
    "Recipe.csv",            # build_graph（普通制作配方）
    "GatheringItem.csv",     # build_tags（可采集）
    "GatheringPoint.csv",    # build_tags（限时采集点）
    "GatheringPointBase.csv",
    "GilShopItem.csv",       # build_tags（NPC 商店）
    "GCScripShopItem.csv",   # build_tags（军票兑换）
    "SpecialShop.csv",       # build_tags（风茄 / 薰衣草兑换）
]


def main(argv):
    force = "--force" in argv
    os.makedirs(RAW, exist_ok=True)
    for name in FILES:
        path = os.path.join(RAW, name)
        if os.path.exists(path) and not force:
            print("跳过 %s（已存在，%.1f MB）" % (name, os.path.getsize(path) / 1048576))
            continue
        url = BASE + name
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        data = urllib.request.urlopen(req, timeout=180).read()
        with open(path, "wb") as f:
            f.write(data)
        print("下载 %s（%.1f MB）" % (name, len(data) / 1048576))
    print("完成，数据在 %s" % RAW)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
