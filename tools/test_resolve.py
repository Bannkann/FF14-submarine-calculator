# -*- coding: utf-8 -*-
"""自检：命名口径、单件解析、整条配装。全部通过才继续。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parts_lib import PartIndex, SLOTS

fails = []
idx = PartIndex()


def check(cond, msg):
    if not cond:
        fails.append(msg)


# 1. 40 个部件，每个槽位 10 个
check(len(idx.parts) == 40, "部件数应为 40，实际 %d" % len(idx.parts))

# 2. 每个部件的各种写法都必须落到自己
for p in idx.parts:
    forms = [
        p["全名"], p["简称"], p["全名英文"],
        p["配装字符"] + p["部件"], p["配装字符"] + "-" + p["部件"],
        p["级别名"] + p["部件"],
    ]
    for f in forms:
        got, cands, note = idx.resolve(f)
        check(got is p, "写法 %r 应解析为 %s，实际 %s" % (f, p["全名"], note))

# 3. 只给级别不能瞎猜
for cls, lv, mod in [("1", 1, False), ("4改", 4, True), ("5", 5, False)]:
    got, cands, note = idx.resolve(cls)
    check(got is None and len(cands) == 4, "级别 %r 应返回 4 个候选" % cls)
    check(all(c["级别"] == lv and (c["是否改级"] == "是") == mod for c in cands), "级别 %r 候选不匹配" % cls)

# 4. 配装解析：用户给的例子
build = idx.parse_build("4254")
names = [p["全名"] for p in build]
check(names == ["腔棘鱼级船体", "甲鲎级船尾", "希尔德拉级船首", "腔棘鱼级舰桥"], "4254 解析错误：%s" % names)

build = idx.parse_build("4254改")
names = [p["全名"] for p in build]
check(names == ["腔棘鱼改级船体", "甲鲎改级船尾", "希尔德拉改级船首", "腔棘鱼改级舰桥"], "4254改 解析错误：%s" % names)

# 5. 容错：分隔符、逐位改、回写
check(idx.parse_build("4-2-5-4")[1]["全名"] == "甲鲎级船尾", "分隔符容错失败")
check(idx.parse_build("4 2 5 4")[0]["全名"] == "腔棘鱼级船体", "空格容错失败")
check(idx.parse_build("4改2改5改4改")[0]["全名"] == "腔棘鱼改级船体", "逐位改失败")
mixed = idx.parse_build("4改254")
check([p["是否改级"] for p in mixed] == ["是", "否", "否", "否"], "混合改解析失败")

for text, expect in [("4254", "4254"), ("4254改", "4254改"), ("4-2-5-4", "4254"), ("4改2改5改4改", "4254改")]:
    parts = idx.parse_build(text)
    check(idx.build_str(parts) == expect, "回写失败：%r -> %r，期望 %r" % (text, idx.build_str(parts), expect))

# 6. 非法输入必须报错
for bad in ["425", "42545", "4256", "0254", "abcd", "", "42"]:
    try:
        idx.parse_build(bad)
        fails.append("非法配装 %r 应当报错却通过了" % bad)
    except ValueError:
        pass

print("部件数: %d" % len(idx.parts))
print("失败: %d" % len(fails))
for f in fails:
    print("  FAIL", f)
sys.exit(1 if fails else 0)
