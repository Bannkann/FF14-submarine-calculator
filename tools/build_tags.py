# -*- coding: utf-8 -*-
"""从中文数据包推导材料的获取方式标签。

数据来源（data/raw）：
  Item.csv          物品名
  GatheringItem.csv 采集物
  GilShopItem.csv   NPC 商店售卖
  SpecialShop.csv   特殊兑换（军票、虚无界风茄、阿尔基克薰衣草等）

输出：data/tags.json   {物品id: ["可采集", "NPC售卖", ...]}
"""
import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "data", "tags.json")

SEAL_IDS = {20, 21, 22}          # 黑涡团 / 双蛇党 / 恒辉队军票
FUNGUS_ID = 15858                # 虚无界风茄
LAVENDER_ID = 15857              # 阿尔基克薰衣草


def read_csv(name):
    with open(os.path.join(RAW, name), encoding="utf-8-sig", errors="replace", newline="") as f:
        rows = list(csv.reader(f))
    return rows[1], rows[3:]


def col(names, field):
    return names.index(field)


def ints(row, idx):
    out = []
    for i in idx:
        if i < len(row):
            try:
                v = int(row[i])
            except ValueError:
                continue
            if v > 0:
                out.append(v)
    return out


def main():
    tags = {}

    def add(iid, tag):
        tags.setdefault(str(iid), set()).add(tag)

    # 采集
    names, body = read_csv("GatheringItem.csv")
    i_item = col(names, "Item")
    for r in body:
        for iid in ints(r, [i_item]):
            add(iid, "可采集")

    # NPC 商店
    names, body = read_csv("GilShopItem.csv")
    i_item = col(names, "Item")
    for r in body:
        for iid in ints(r, [i_item]):
            add(iid, "NPC售卖")

    # 军票（大国防联军）兑换
    names, body = read_csv("GCScripShopItem.csv")
    i_item = col(names, "Item")
    for r in body:
        for iid in ints(r, [i_item]):
            add(iid, "军票兑换")

    # 特殊兑换：必须按「槽位」一一对应，否则同一商店页里不同商品的货币会串
    names, body = read_csv("SpecialShop.csv")
    n_slots = 60
    recv_a = [names.index("Item{Receive}[%d][0]" % i) for i in range(n_slots)]
    recv_b = [names.index("Item{Receive}[%d][1]" % i) for i in range(n_slots)]
    cost_idx = [[names.index("Item{Cost}[%d][%d]" % (i, c)) for c in range(3)] for i in range(n_slots)]
    for r in body:
        for i in range(n_slots):
            recv = []
            for idx in (recv_a[i], recv_b[i]):
                if idx < len(r) and r[idx].isdigit() and int(r[idx]) > 0:
                    recv.append(int(r[idx]))
            if not recv:
                continue
            costs = set()
            for idx in cost_idx[i]:
                if idx < len(r) and r[idx].isdigit() and int(r[idx]) > 0:
                    costs.add(int(r[idx]))
            labels = []
            if costs & SEAL_IDS:
                labels.append("军票兑换")
            if FUNGUS_ID in costs:
                labels.append("风茄兑换")
            if LAVENDER_ID in costs:
                labels.append("薰衣草兑换")
            if not labels:
                continue
            for iid in recv:
                for lb in labels:
                    add(iid, lb)

    # 限时采集点：采集点 Type 2 / 5 视为限时（传说・秘传）
    n0, b0 = read_csv("GatheringItem.csv")
    i0_item = col(n0, "Item")
    g2i = {}
    for r in b0:
        try:
            gid = int(r[0])
        except ValueError:
            continue
        if i0_item < len(r) and r[i0_item].isdigit():
            g2i[gid] = int(r[i0_item])
    n2, b2 = read_csv("GatheringPointBase.csv")
    base_g = {}
    for r in b2:
        try:
            bid = int(r[0])
        except ValueError:
            continue
        base_g[bid] = [int(x) for x in r[3:11] if x.isdigit() and int(x) > 0]
    n1, b1 = read_csv("GatheringPoint.csv")
    for r in b1:
        try:
            t, b = int(r[1]), int(r[4])
        except (ValueError, IndexError):
            continue
        if t not in (2, 5):
            continue
        for gid in base_g.get(b, []):
            it = g2i.get(gid)
            if it:
                add(it, "限时采集")

    # 潜水艇带取（灰机 wiki 掉落页抓取）
    sub_path = os.path.join(ROOT, "data", "subdrops.json")
    if os.path.exists(sub_path):
        with open(sub_path, encoding="utf-8") as f:
            for iid in json.load(f):
                add(iid, "潜水艇带取")

    # NPC 售价（Item 表 Price{Mid}）
    prices = {}
    n3, b3 = read_csv("Item.csv")
    i3_key = col(n3, "#")
    i3_mid = col(n3, "Price{Mid}")
    for r in b3:
        try:
            iid = int(r[i3_key])
            mid = int(r[i3_mid])
        except (ValueError, IndexError):
            continue
        if mid > 0:
            prices[str(iid)] = mid
    with open(os.path.join(ROOT, "data", "prices.json"), "w", encoding="utf-8") as f:
        json.dump(prices, f)

    # 军票单价（兑换所需军票数）
    seals = {}
    n4, b4 = read_csv("GCScripShopItem.csv")
    i4_item = col(n4, "Item")
    i4_cost = col(n4, "Cost{GCSeals}")
    for r in b4:
        try:
            iid = int(r[i4_item])
            cost = int(r[i4_cost])
        except (ValueError, IndexError):
            continue
        if cost > 0:
            seals[str(iid)] = cost
    with open(os.path.join(ROOT, "data", "seals.json"), "w", encoding="utf-8") as f:
        json.dump(seals, f)

    # 限时的采集物只留一个「限时采集」词条，不再重复标「可采集」
    for k, v in tags.items():
        if "限时采集" in v:
            v.discard("可采集")

    data = {k: sorted(v) for k, v in tags.items()}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    # 统计
    from collections import Counter
    cnt = Counter(t for v in data.values() for t in v)
    print("有标签的物品：%d" % len(data))
    for k, v in cnt.most_common():
        print("  %s: %d" % (k, v))
    print("已写入", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
