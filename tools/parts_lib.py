# -*- coding: utf-8 -*-
"""潜水艇部件与配装解析。

命名口径：
  配装 = 四位数字，依次为 船体·船尾·船首·舰桥
  1=鲨鱼 2=甲鲎 3=须鲸 4=腔棘鱼 5=希尔德拉
  末尾「改」= 四件全部改级；也兼容逐位写「改」（如 4改254）

  4254   -> 腔棘鱼船体 / 甲鲎船尾 / 希尔德拉船首 / 腔棘鱼舰桥
  4254改 -> 上述四件全部改为改级
"""
import json
import os
import re

_DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "parts.json")

SLOTS = ["船体", "船尾", "船首", "舰桥"]
SLOT_SHORT = {"船体": "体", "船尾": "尾", "船首": "首", "舰桥": "桥"}
CLASS_NAMES = {1: "鲨鱼", 2: "甲鲎", 3: "须鲸", 4: "腔棘鱼", 5: "希尔德拉"}
LEVELS = set(CLASS_NAMES)

_SLOT_ALIASES = {
    "船体": "船体", "体": "船体", "hull": "船体",
    "船尾": "船尾", "尾": "船尾", "stern": "船尾",
    "船首": "船首", "首": "船首", "bow": "船首",
    "舰桥": "舰桥", "桥": "舰桥", "bridge": "舰桥",
}


def load_parts(path=_DATA):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _norm(s):
    if s is None:
        return ""
    s = str(s).strip().lower()
    s = s.replace("－", "-").replace("—", "-").replace("—", "-")
    s = re.sub(r"[\s、,，/|\-]+", "", s)
    s = s.replace("級", "级")
    return s


class PartIndex(object):
    def __init__(self, parts=None):
        self.parts = parts if parts is not None else load_parts()
        self.by_key = {}
        self.by_alias = {}
        for p in self.parts:
            self.by_key[(p["级别"], p["是否改级"] == "是", p["部件"])] = p
            for a in self._aliases(p):
                self.by_alias.setdefault(_norm(a), []).append(p)

    @staticmethod
    def _aliases(p):
        cn = p["级别名"]              # 腔棘鱼 / 腔棘鱼改
        slot = p["部件"]
        short = SLOT_SHORT[slot]
        char = p["配装字符"]           # 4 / 4改
        L = p["级别"]
        out = [
            p["全名"], p["简称"], p["全名英文"],
            char + slot, char + "-" + slot, char + short,
            cn + slot, cn + "级" + slot, cn + "级" + slot.replace("船", ""),
            cn + short, char + short,
        ]
        seen, uniq = set(), []
        for a in out:
            k = _norm(a)
            if k and k not in seen:
                seen.add(k)
                uniq.append(a)
        return uniq

    # ---------- 单个部件 ----------
    def resolve(self, text):
        """返回 (part|None, 候选, 说明)。"""
        t = _norm(text)
        if not t:
            return None, [], "空输入"
        hits = self.by_alias.get(t)
        if hits:
            if len(hits) == 1:
                return hits[0], hits, "精确匹配"
            return None, hits, "命中 %d 个候选" % len(hits)
        cls = self._match_class_only(t)
        if cls:
            return None, cls, "只给了级别，四槽全部命中"
        return None, [], "无法识别"

    def _match_class_only(self, t):
        m = re.match(r"^([1-5])(改?)$", t)
        if not m:
            return []
        lv, mod = int(m.group(1)), m.group(2) == "改"
        return [p for p in self.parts if p["级别"] == lv and (p["是否改级"] == "是") == mod]

    # ---------- 整条配装 ----------
    def parse_build(self, text):
        """把 4254 / 4254改 / 4改254 解析成 4 个部件（船体·船尾·船首·舰桥）。"""
        t = _norm(text)
        if not t:
            raise ValueError("空配装")
        tokens = re.findall(r"([1-5])(改?)", t)
        if "".join(a + b for a, b in tokens) != t or not tokens:
            raise ValueError("无法解析配装：%r（只允许数字 1-5 和「改」）" % text)
        if len(tokens) != 4:
            raise ValueError("配装必须是四位（船体·船尾·船首·舰桥），你给了 %d 位：%r" % (len(tokens), text))

        flags = [tok[1] == "改" for tok in tokens]
        # 标准写法：只有末位带「改」= 四件全改
        if flags[3] and not any(flags[:3]):
            flags = [True, True, True, True]

        out = []
        for (num, _), flag, slot in zip(tokens, flags, SLOTS):
            p = self.by_key.get((int(num), flag, slot))
            if p is None:
                raise ValueError("找不到部件：级别 %s / %s / %s" % (num, "改级" if flag else "普通", slot))
            out.append(p)
        return out

    def build_str(self, parts):
        """4 个部件 -> '4254' 或 '4254改'（全改时用后缀写法）。"""
        if len(parts) != 4:
            raise ValueError("需要 4 个部件")
        digits = []
        mods = []
        for p, slot in zip(parts, SLOTS):
            if p["部件"] != slot:
                raise ValueError("部件顺序不对：应为 %s，实际 %s" % (slot, p["部件"]))
            digits.append(str(p["级别"]))
            mods.append(p["是否改级"] == "是")
        base = "".join(digits)
        return base + "改" if all(mods) else "".join(
            d + ("改" if m else "") for d, m in zip(digits, mods)
        )


def fmt(p):
    return "%s\t%s\t%s" % (p["配装字符"], p["部件"], p["全名"])


def main(argv):
    idx = PartIndex()
    if not argv:
        print(__doc__)
        return 1
    for arg in argv:
        part, cands, note = idx.resolve(arg)
        if part:
            print("%-24s -> %s" % (arg, fmt(part)))
            continue
        try:
            build = idx.parse_build(arg)
        except ValueError:
            build = None
        if build:
            print("%-24s -> 配装 %s" % (arg, idx.build_str(build)))
            for b in build:
                print("    %s" % fmt(b))
            continue
        if cands:
            print("%-24s -> %s（%s）" % (arg, note, " / ".join(fmt(c) for c in cands)))
        else:
            print("%-24s -> 无法识别" % arg)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))
