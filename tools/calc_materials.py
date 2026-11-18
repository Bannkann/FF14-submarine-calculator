# -*- coding: utf-8 -*-
"""潜水艇配装材料计算器。

用法：
  python calc_materials.py 4254
  python calc_materials.py 4254改
  python calc_materials.py 4254改 3355 --expand-frames
  python calc_materials.py 4254改 --csv 输出.csv

数据来源：data/parts.json（部件全名）+ data/recipes.json（灰机 wiki 合建配方）。
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parts_lib import PartIndex, SLOTS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECIPES = os.path.join(ROOT, "data", "recipes.json")


def load_recipes():
    with open(RECIPES, encoding="utf-8") as f:
        return {r["部件"]: r for r in json.load(f)}


def frame_base(name):
    """骨架名 -> 普通部件名：腔棘鱼级船体骨架 -> 腔棘鱼级船体"""
    return name[:-2] if name.endswith("骨架") else None


def collect(parts, recipes, expand_frames=False):
    """返回 (每件明细, 汇总 dict, 缺配方的部件列表)"""
    detail = []
    total = {}
    missing = []
    for p in parts:
        name = p["全名"]
        rec = recipes.get(name)
        if not rec:
            missing.append(name)
            detail.append((p, None, []))
            continue
        lines = []
        for m in rec["材料"]:
            mat, qty = m["名称"], m["数量"]
            base = frame_base(mat)
            if expand_frames and base and base in recipes:
                for b in recipes[base]["材料"]:
                    lines.append((b["名称"], b["数量"] * qty, "由 %s 展开" % base))
                    total[b["名称"]] = total.get(b["名称"], 0) + b["数量"] * qty
            else:
                note = "可用 %s 1:1 兑换" % base if base else ""
                lines.append((mat, qty, note))
                total[mat] = total.get(mat, 0) + qty
        detail.append((p, rec, lines))
    return detail, total, missing


def render(builds, detail, total, missing):
    out = []
    codes = ", ".join(builds)
    out.append("配装 " + codes)
    for p in [d[0] for d in detail]:
        out.append("  %-4s %s" % (p["配装字符"], p["全名"]))
    out.append("")

    designs = []
    for p, rec, lines in detail:
        if rec and rec["解锁设计图"]:
            designs.append(rec["解锁设计图"])
    if designs:
        uniq = sorted(set(designs))
        out.append("需要设计图：" + "、".join(uniq))
        out.append("")

    for p, rec, lines in detail:
        head = "[%s] %s" % (p["配装字符"], p["全名"])
        if rec and rec["解锁设计图"]:
            head += "    " + rec["解锁设计图"]
        out.append(head)
        for mat, qty, note in lines:
            out.append("    %-14s ×%-3d %s" % (mat, qty, note))
        if rec is None:
            out.append("    （缺配方，请先跑 scrape_recipes.py --missing）")
        out.append("")

    out.append("合计 %d 种材料：" % len(total))
    for mat, qty in sorted(total.items(), key=lambda kv: (-kv[1], kv[0])):
        out.append("  %-14s ×%d" % (mat, qty))
    if missing:
        out.append("")
        out.append("缺配方： " + "、".join(missing))
    return "\n".join(out)


def main(argv):
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("builds", nargs="+", help="配装号，如 4254 / 4254改")
    ap.add_argument("--expand-frames", action="store_true",
                    help="把改级的「骨架」展开成对应普通部件的材料")
    ap.add_argument("--csv", help="把汇总写到 csv")
    args = ap.parse_args(argv)

    idx = PartIndex()
    recipes = load_recipes()

    parts = []
    for code in args.builds:
        try:
            parts.extend(idx.parse_build(code))
        except ValueError as exc:
            print("错误：%s" % exc, file=sys.stderr)
            return 2

    detail, total, missing = collect(parts, recipes, args.expand_frames)
    print(render(args.builds, detail, total, missing))

    if args.csv:
        import csv
        with open(args.csv, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["材料", "数量"])
            for mat, qty in sorted(total.items(), key=lambda kv: (-kv[1], kv[0])):
                w.writerow([mat, qty])
        print("\n已写入 " + args.csv)

    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
