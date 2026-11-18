# -*- coding: utf-8 -*-
"""建配方图：部件层用灰机 wiki（已校验），材料层用中文数据包展开。

为什么分两层：
  部队合建（潜水艇部件）不在 Recipe.csv 里，属于 CompanyCraft 系列表；
  而部件下面的锭/铆钉/墨水等，是普通制作配方，在 Recipe.csv 里。
  所以 40 条部件配方以 wiki 为准，往下的递归用数据包。

输入：data/raw/Item.csv、data/raw/Recipe.csv、data/parts.json、data/recipes.json
输出：data/graph.json
"""
import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "data", "graph.json")


def read_csv(path):
    with open(path, encoding="utf-8-sig", errors="replace", newline="") as f:
        rows = list(csv.reader(f))
    return rows[1], rows[3:]          # 字段名行 / 数据行


def col(names, field):
    for i, n in enumerate(names):
        if n == field:
            return i
    raise KeyError("字段不存在: %s" % field)


def load_items():
    names, body = read_csv(os.path.join(RAW, "Item.csv"))
    i_key, i_name = col(names, "#"), col(names, "Name")
    out = {}
    for r in body:
        if len(r) <= max(i_key, i_name):
            continue
        try:
            iid = int(r[i_key])
        except ValueError:
            continue
        name = r[i_name].strip()
        if iid and name:
            out[iid] = name
    return out


def load_recipes():
    names, body = read_csv(os.path.join(RAW, "Recipe.csv"))
    i_res, i_amt = col(names, "Item{Result}"), col(names, "Amount{Result}")
    pairs = []
    for k in range(8):
        fi, fa = "Item{Ingredient}[%d]" % k, "Amount{Ingredient}[%d]" % k
        if fi in names and fa in names:
            pairs.append((col(names, fi), col(names, fa)))
    out = {}
    for r in body:
        if len(r) <= i_res:
            continue
        try:
            res = int(r[i_res])
        except ValueError:
            continue
        if res <= 0:
            continue
        try:
            amount = max(int(r[i_amt] or 1), 1)
        except ValueError:
            amount = 1
        mats = []
        for i_item, i_amt2 in pairs:
            if len(r) <= max(i_item, i_amt2):
                continue
            try:
                mid, mn = int(r[i_item]), int(r[i_amt2] or 0)
            except ValueError:
                continue
            if mid > 0 and mn > 0:
                mats.append((mid, mn))
        if mats:
            out.setdefault(res, {"产量": amount, "材料": mats})
    return out


def main():
    items = load_items()
    recipes = load_recipes()
    print("数据包：物品 %d，普通配方 %d" % (len(items), len(recipes)))

    with open(os.path.join(ROOT, "data", "parts.json"), encoding="utf-8") as f:
        parts = json.load(f)
    with open(os.path.join(ROOT, "data", "recipes.json"), encoding="utf-8") as f:
        wiki = {r["部件"]: r for r in json.load(f)}

    name2ids = {}
    for iid, name in items.items():
        name2ids.setdefault(name, []).append(iid)

    def resolve(name, prefer_recipe=True):
        ids = name2ids.get(name, [])
        if prefer_recipe:
            with_rec = [i for i in ids if i in recipes]
            if len(with_rec) == 1:
                return with_rec[0]
            if with_rec:
                return with_rec[0]
        return ids[0] if ids else None

    # 部件 id
    part_ids = {}
    unresolved = []
    for p in parts:
        iid = resolve(p["全名"], prefer_recipe=False)
        if iid is None:
            unresolved.append(p["全名"])
        else:
            part_ids[p["全名"]] = iid
    if unresolved:
        print("!! 物品表里找不到：", unresolved)
        return 1

    # 组装图：部件层来自 wiki，材料层来自数据包
    nodes = {}
    ambiguous = []

    def add_node(iid, name, mats, amount=1, src="data", note=""):
        nodes[str(iid)] = {
            "名称": name,
            "产量": amount,
            "材料": [{"id": str(m), "名称": items.get(m, "未知%d" % m), "数量": n} for m, n in mats],
            "来源": src,
            "备注": note,
        }

    for p in parts:
        name = p["全名"]
        pid = part_ids[name]
        wrec = wiki.get(name)
        mats = []
        for m in (wrec["材料"] if wrec else []):
            mid = resolve(m["名称"])
            if mid is None:
                unresolved.append(m["名称"])
                continue
            if len(name2ids.get(m["名称"], [])) > 1:
                ambiguous.append((m["名称"], name2ids[m["名称"]], mid))
            mats.append((mid, m["数量"]))
        add_node(pid, name, mats, 1, "wiki")

    # 骨架：在 NPC 处用同名普通部件 1:1 兑换，所以按「1 个骨架 = 1 个普通部件」继续往下展开
    frame_count = 0
    for p in parts:
        name = p["全名"]
        fid = resolve(name + "骨架", prefer_recipe=False)
        if fid is None:
            continue
        add_node(fid, name + "骨架", [(part_ids[name], 1)], 1, "frame",
                 "兑换自 %s" % name)
        frame_count += 1
    print("骨架节点 %d 个（1:1 兑换自普通部件）" % frame_count)

    # 递归展开材料层
    stack = [int(r["id"]) for node in nodes.values() for r in node["材料"]]
    while stack:
        iid = stack.pop()
        if str(iid) in nodes:
            continue
        rec = recipes.get(iid)
        if rec:
            add_node(iid, items.get(iid, "未知"), rec["材料"], rec["产量"], "data")
            stack.extend(m for m, _ in rec["材料"])
        else:
            add_node(iid, items.get(iid, "未知"), [], 1, "base")

    payload = {"source": "wiki + ffxiv-datamining-cn", "parts": part_ids, "items": nodes}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)

    bases = [v["名称"] for v in nodes.values() if not v["材料"]]
    print("图中物品 %d 个；无配方（基础素材）%d 个" % (len(nodes), len(bases)))
    if ambiguous:
        print("名称有重名、按配方优先择一：%d 处" % len(ambiguous))
        for n, ids, pick in ambiguous[:5]:
            print("   %s -> %s（候选 %s）" % (n, pick, ids))
    print("基础素材示例：", "、".join(bases[:12]))
    print("已写入", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
