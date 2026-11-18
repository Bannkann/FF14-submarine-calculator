# -*- coding: utf-8 -*-
"""生成潜水艇部件对照表。

命名口径（按用户给定的 QA）：
  配装 = 四位数字，依次表示 船体·船尾·船首·舰桥。
  1=鲨鱼级 2=甲鲎级 3=须鲸级 4=腔棘鱼级 5=希尔德拉级
  末尾一个「改」表示四个部件全为改级。
  例：4254 = 腔棘鱼船体 / 甲鲎船尾 / 希尔德拉船首 / 腔棘鱼舰桥
      4254改 = 上述四件全部为改级
"""
import csv
import json
import os

# 级别数字 -> (简称, 英文, 全称前缀)
CLASSES = {
    1: ("鲨鱼", "Shark"),
    2: ("甲鲎", "Unkiu"),
    3: ("须鲸", "Whale"),
    4: ("腔棘鱼", "Coelacanth"),
    5: ("希尔德拉", "Syldra"),
}

# 配装四位的排列顺序
SLOTS = ["船体", "船尾", "船首", "舰桥"]
SLOTS_EN = {"船体": "Hull", "船尾": "Stern", "船首": "Bow", "舰桥": "Bridge"}

rows = []
for pos, slot in enumerate(SLOTS, start=1):
    for level, (cn, en) in CLASSES.items():
        for modified in (False, True):
            if modified:
                char = "%d改" % level
                full = "%s改级%s" % (cn, slot)      # 腔棘鱼改级船体
                short = "%s改%s" % (cn, slot)       # 腔棘鱼改船体
                en_full = "Modified %s-class %s" % (en, SLOTS_EN[slot])
            else:
                char = "%d" % level
                full = "%s级%s" % (cn, slot)
                short = "%s%s" % (cn, slot)
                en_full = "%s-class %s" % (en, SLOTS_EN[slot])
            rows.append({
                "位置": pos,
                "配装字符": char,
                "级别": level,
                "级别名": cn + ("改" if modified else ""),
                "是否改级": "是" if modified else "否",
                "部件": slot,
                "全名": full,
                "简称": short,
                "全名英文": en_full,
            })

out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(out_dir, exist_ok=True)

csv_path = os.path.join(out_dir, "部件对照表.csv")
with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

json_path = os.path.join(out_dir, "parts.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)

print("rows:", len(rows))
print("csv:", csv_path)
print("json:", json_path)
