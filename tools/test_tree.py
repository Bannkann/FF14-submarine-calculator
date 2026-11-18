# -*- coding: utf-8 -*-
"""自检：递归展开、取整、归因自洽。"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parts_lib import PartIndex
from calc_tree import Calculator, load_graph

fails = []
idx = PartIndex()
graph = load_graph()
calc = Calculator(graph)


def check(cond, msg):
    if not cond:
        fails.append(msg)


def expand_all(code):
    parts = idx.parse_build(code)
    total, branch = {}, {}
    for p in parts:
        for iid, info in calc.expand(p["全名"]).items():
            total[iid] = total.get(iid, 0) + info["总"]
            for key, n in info["分支"].items():
                branch.setdefault(iid, {})[key] = branch.get(iid, {}).get(key, 0) + n
    return parts, total, branch


# 1. 归因必须自洽：每个基础素材的分支之和 == 总数
for code in ("4254", "4254改", "1234", "5555改"):
    _, total, branch = expand_all(code)
    for iid, t in total.items():
        s = sum(branch[iid].values())
        check(s == t, "%s 的 %s 归因不守恒：总 %s 分支 %s" % (code, graph["items"][iid]["名称"], t, s))

# 2. 改装的骨架必须被展开掉，不能留在基础素材里
_, total_mod, _ = expand_all("4254改")
check(not any(n.endswith("骨架") for n in (graph["items"][i]["名称"] for i in total_mod)),
      "4254改 里还有未展开的骨架")

# 3. 普通配装不该出现骨架
_, total_base, _ = expand_all("4254")
check(not any(n.endswith("骨架") for n in (graph["items"][i]["名称"] for i in total_base)),
      "4254 不该出现骨架")

# 4. 取整生效：灵银锭每次产 1、耗灵银矿 4，矿量应等于锭需求量×4
def qty(total, name):
    for iid, n in total.items():
        if graph["items"][iid]["名称"] == name:
            return n
    return None

parts_base = idx.parse_build("4254")
ink_need = sum(m["数量"] for p in parts_base for m in calc.part_direct(p["全名"])
               if m["名称"] == "灵银锭")
ore = qty(total_base, "灵银矿")
check(ink_need > 0, "4254 应需要灵银锭")
check(ore is not None, "基础配装缺少灵银矿")
if ink_need and ore:
    check(ore == ink_need * 4, "灵银矿 %s != 灵银锭 %s ×4" % (ore, ink_need))

# 5. 同一材料跨部件时，必须有多条分支
multi = [iid for iid, b in expand_all("4254改")[2].items() if len(b) > 1]
check(len(multi) > 5, "跨部件共用的材料过少（%d），归因可能没生效" % len(multi))

# 6. 结果可重复（无随机、无状态残留）
a = expand_all("4254改")[1]
b = expand_all("4254改")[1]
check(a == b, "两次计算结果不一致")

print("基础素材种类: 4254=%d, 4254改=%d" % (len(total_base), len(total_mod)))
print("跨部件共用材料: %d 种" % len(multi))
print("失败: %d" % len(fails))
for f in fails:
    print("  FAIL", f)
sys.exit(1 if fails else 0)
