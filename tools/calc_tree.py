# -*- coding: utf-8 -*-
"""潜水艇配装材料计算：递归展开 + 逐层取整 + 用量归因。

口径（与用户确认）：
  - 每一层按 ceil(需要量 / 每次产量) 向上取整到整次合成
  - 材料分两层：直接素材（部件配方的一级材料）、基础素材（拆到无配方原料）
  - 每个基础素材按「部件 → 中间材料」归因，分支之和单独显示
  - 允许「未归因余量」，正常情况下应为 0
"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parts_lib import PartIndex

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH = os.path.join(ROOT, "data", "graph.json")


def load_graph():
    with open(GRAPH, encoding="utf-8") as f:
        return json.load(f)


class Calculator(object):
    def __init__(self, graph):
        self.items = graph["items"]
        self.part_ids = graph["parts"]

    def expand(self, part_name, need=1):
        """返回该部件下的基础素材归因：{id: {'总': n, '分支': {(部件, 路径): n}}}"""
        acc = {}
        seen_path = []

        def walk(iid, qty, path):
            node = self.items.get(str(iid))
            if node is None:
                return
            mats = node["材料"]
            if not mats:
                slot = acc.setdefault(str(iid), {"名称": node["名称"], "总": 0, "分支": {}})
                slot["总"] += qty
                key = (part_name, tuple(path))
                slot["分支"][key] = slot["分支"].get(key, 0) + qty
                return
            yield_ = max(int(node.get("产量") or 1), 1)
            crafts = int(math.ceil(float(qty) / yield_))
            if iid in seen_path:          # 防环
                return
            seen_path.append(iid)
            for m in mats:
                walk(m["id"], crafts * int(m["数量"]), path + [node["名称"]])
            seen_path.pop()

        pid = self.part_ids.get(part_name)
        if pid is None:
            return {}
        walk(pid, need, [])
        return acc

    def part_direct(self, part_name):
        """部件的一级材料（直接素材），不做展开"""
        pid = self.part_ids.get(part_name)
        node = self.items.get(str(pid))
        return node["材料"] if node else []


def fmt_num(n):
    return str(int(n)) if float(n).is_integer() else ("%.2f" % n)


def render(builds, parts, calc):
    lines = []
    lines.append("配装 %s" % " ".join(builds))
    for p in parts:
        lines.append("  %-4s %s" % (p["配装字符"], p["全名"]))
    lines.append("")

    # 直接素材
    lines.append("■ 直接素材")
    for p in parts:
        mats = calc.part_direct(p["全名"])
        lines.append("  [%s] %s" % (p["配装字符"], p["全名"]))
        for m in mats:
            lines.append("      %-14s ×%d" % (m["名称"], m["数量"]))
        if not mats:
            lines.append("      （无配方数据）")
    lines.append("")

    # 基础素材 + 归因
    totals = {}
    branches = {}
    names = {}
    for p in parts:
        acc = calc.expand(p["全名"])
        for iid, info in acc.items():
            totals[iid] = totals.get(iid, 0) + info["总"]
            names[iid] = info["名称"]
            b = branches.setdefault(iid, {})
            for key, n in info["分支"].items():
                b[key] = b.get(key, 0) + n

    lines.append("■ 基础素材（%d 种）" % len(totals))
    for iid, total in sorted(totals.items(), key=lambda kv: (-kv[1], names[kv[0]])):
        lines.append("  %-16s ×%s" % (names[iid], fmt_num(total)))
        bs = branches[iid]
        s = sum(bs.values())
        for (part_name, path), n in sorted(bs.items(), key=lambda kv: -kv[1]):
            chain = " → ".join(path) if path else part_name
            lines.append("      ├ %-6s %s" % (fmt_num(n), chain))
        if s != total:
            lines.append("      └ 未归因 %s" % fmt_num(total - s))
    lines.append("")
    lines.append("合计基础素材 %d 种，总件数 %s" % (len(totals), fmt_num(sum(totals.values()))))
    return "\n".join(lines)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("builds", nargs="+")
    ap.add_argument("--csv", help="导出汇总 csv")
    args = ap.parse_args(argv)

    idx = PartIndex()
    graph = load_graph()
    calc = Calculator(graph)

    parts = []
    for code in args.builds:
        try:
            parts.extend(idx.parse_build(code))
        except ValueError as exc:
            print("错误：%s" % exc, file=sys.stderr)
            return 2

    print(render(args.builds, parts, calc))

    if args.csv:
        import csv
        totals = {}
        for p in parts:
            for iid, info in calc.expand(p["全名"]).items():
                totals[iid] = totals.get(iid, 0) + info["总"]
                info["名称"] = info["名称"]
        with open(args.csv, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["材料", "数量"])
            for iid, n in sorted(totals.items(), key=lambda kv: -kv[1]):
                w.writerow([graph["items"][iid]["名称"], n])
        print("\n已写入 " + args.csv)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
