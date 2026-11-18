# -*- coding: utf-8 -*-
"""自检：配方数据完整性 + 材料汇总守恒。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parts_lib import PartIndex
from calc_materials import load_recipes, collect

fails = []
idx = PartIndex()
recipes = load_recipes()


def check(cond, msg):
    if not cond:
        fails.append(msg)


# 1. 40 个部件全有配方，材料数与数量都合法
check(len(recipes) == 40, "配方数应为 40，实际 %d" % len(recipes))
for name, rec in recipes.items():
    mats = rec["材料"]
    check(len(mats) >= 8, "%s 材料只有 %d 项，像没抓全" % (name, len(mats)))
    check(all(isinstance(m["数量"], int) and m["数量"] > 0 for m in mats), "%s 有非法数量" % name)
    check(len({m["名称"] for m in mats}) == len(mats), "%s 材料有重复项" % name)
    check(rec["解锁设计图"] is not None, "%s 缺设计图字段" % name)

# 2. 改级一律走设计图6，普通级按级别走 1-5
for p in idx.parts:
    rec = recipes[p["全名"]]
    if p["是否改级"] == "是":
        check(rec["解锁设计图"] == "潜水艇设计图6", "%s 应为设计图6" % p["全名"])
    else:
        want = "潜水艇设计图%d" % p["级别"]
        check(rec["解锁设计图"] == want, "%s 应为 %s，实际 %s" % (p["全名"], want, rec["解锁设计图"]))

# 3. 4254 是普通配装，汇总里不应出现骨架
_, total, missing = collect(idx.parse_build("4254"), recipes)
check(not missing, "4254 缺配方: %s" % missing)
check(not any("骨架" in k for k in total), "4254 不该出现骨架")

# 4. 4254改 恰好 4 个骨架
_, total, missing = collect(idx.parse_build("4254改"), recipes)
check(not missing, "4254改 缺配方: %s" % missing)
frames = [k for k in total if k.endswith("骨架")]
check(len(frames) == 4, "4254改 骨架数应为 4，实际 %d" % len(frames))

# 5. 汇总守恒：每件材料的汇总数量 >= 它在任一部件里的数量
for code in ("4254", "4254改", "1234", "5555"):
    parts = idx.parse_build(code)
    detail, total, _ = collect(parts, recipes)
    for p, rec, lines in detail:
        for mat, qty, _note in lines:
            check(total[mat] >= qty, "%s 的 %s 汇总小于单件数量" % (code, mat))

# 6. expand-frames 展开后不含骨架，且材料种类更多
_, total_raw, _ = collect(idx.parse_build("4254改"), recipes)
_, total_exp, _ = collect(idx.parse_build("4254改"), recipes, expand_frames=True)
check(not any(k.endswith("骨架") for k in total_exp), "展开后不应再有骨架")
check(len(total_exp) > len(total_raw), "展开后材料种类应增加")

print("配方数: %d" % len(recipes))
print("失败: %d" % len(fails))
for f in fails:
    print("  FAIL", f)
sys.exit(1 if fails else 0)
