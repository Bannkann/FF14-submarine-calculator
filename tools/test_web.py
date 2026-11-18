# -*- coding: utf-8 -*-
"""自检：三栏含义与参考站一致，且与 Python 引擎的原料总量对得上。"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calc_tree import Calculator, load_graph

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "dist", "潜水艇材料计算器.html")
NODE = os.environ.get("NODE_BIN") or shutil.which("node")
if not NODE:
    raise SystemExit("找不到 node：请安装 Node.js，或设置环境变量 NODE_BIN 指向 node 可执行文件")

BUILD = [
    {"name": "腔棘鱼改级船体", "qty": 1, "slot": "船体"},
    {"name": "甲鲎改级船尾", "qty": 1, "slot": "船尾"},
    {"name": "希尔德拉改级船首", "qty": 1, "slot": "船首"},
    {"name": "腔棘鱼改级舰桥", "qty": 1, "slot": "舰桥"},
]

BUILD2 = [
    {"name": "腔棘鱼改级船体", "qty": 2, "slot": "船体"},
    {"name": "甲鲎改级船尾", "qty": 1, "slot": "船尾"},
    None,
    {"name": "腔棘鱼改级舰桥", "qty": 1, "slot": "舰桥"},
]


def html_core(path):
    with open(path, encoding="utf-8") as f:
        s = f.read()
    m = re.search(r'<script id="core">(.*?)</script>', s, re.S)
    if not m:
        raise SystemExit("找不到 core 脚本")
    return m.group(1)


def run_node(js):
    fd, path = tempfile.mkstemp(suffix=".js")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(js)
        out = subprocess.run([NODE, path], capture_output=True, text=True, encoding="utf-8")
        if out.returncode != 0:
            raise SystemExit("node 运行失败:\n" + out.stderr[:2000])
        return out.stdout.strip()
    finally:
        os.unlink(path)


def main():
    core = html_core(HTML)
    harness = core + """
const parts = %s;
const parts2 = %s;
const r = compute(parts, {});
const nm = m => bySeq(toList(m));
const craftable = x => { const n = ITEMS[x.id]; return !!(n && n.材料 && n.材料.length); };
function needOf(name, res){
  const hit = nm(res.base).filter(x=>x.name === name)[0];
  return hit ? hit.need : null;
}
const orderA = nm(r.base).map(x=>x.name);
const orderB = nm(compute(parts2, {}).base).map(x=>x.name);
const frame = nm(r.queue).filter(x=>x.name === "腔棘鱼级船体骨架")[0];
console.log(JSON.stringify({
  code: buildCode(parts), code2: buildCode(parts2),
  qCount: nm(r.queue).length, dCount: nm(r.direct).length, bCount: nm(r.base).length,
  queueNotCraftable: nm(r.queue).filter(x=>!craftable(x)).map(x=>x.name),
  baseCraftable: nm(r.base).filter(craftable).map(x=>x.name),
  base: nm(r.base).map(x=>[x.name, x.need]),
  directCount: nm(r.direct).length,
  adjacent: (function(){ const A=orderA.indexOf("灵银矿"), B=orderA.indexOf("灵银沙"); return A>=0 && B>=0 && Math.abs(A-B)===1; })(),
  orderA: orderA, orderB: orderB,
  frameRemark: frame ? (ITEMS[frame.id].备注 || "") : "",
  frameNote: frame ? noteLines(frame)[0] : "",
  ore: needOf("灵银矿", r),
  oreHalf: needOf("灵银矿", compute(parts, {"12519":100})),
  oreFull: needOf("灵银矿", compute(parts, {"12519":-1}))
}));
""" % (json.dumps(BUILD, ensure_ascii=False), json.dumps(BUILD2, ensure_ascii=False))

    got = json.loads(run_node(harness))

    calc = Calculator(load_graph())
    leaves = {}
    for s in BUILD:
        for info in calc.expand(s["name"]).values():
            leaves[info["名称"]] = leaves.get(info["名称"], 0) + info["总"] * s["qty"]

    fails = []
    if got["code"] != "4254改":
        fails.append("配装号算错：%s" % got["code"])
    if got["code2"] != "4204改":
        fails.append("带「无」的配装号算错：%s" % got["code2"])

    # 计算队列里只能有「需要制作」的物品
    if got["queueNotCraftable"]:
        fails.append("计算队列出现了无配方物品：%s" % got["queueNotCraftable"][:5])
    # 基础素材里不能有半成品
    if got["baseCraftable"]:
        fails.append("基础素材出现了半成品：%s" % got["baseCraftable"][:5])

    # 基础素材的总量必须和 Python 引擎的原料合计一致
    js_base = dict(got["base"])
    if got["bCount"] != len(leaves):
        fails.append("原料种类不一致：js %d / py %d" % (got["bCount"], len(leaves)))
    for name, n in leaves.items():
        if js_base.get(name) != n:
            fails.append("%s：js %s / py %s" % (name, js_base.get(name), n))

    if None in (got["ore"], got["oreHalf"], got["oreFull"]):
        fails.append("找不到灵银矿")
    elif not (got["oreFull"] < got["oreHalf"] < got["ore"]):
        fails.append("差额计算不对：%s / %s / %s" % (got["ore"], got["oreHalf"], got["oreFull"]))

    a, b2 = got["orderA"], got["orderB"]
    common = set(a) & set(b2)
    if [n for n in a if n in common] != [n for n in b2 if n in common]:
        fails.append("换部件后顺序变了")

    if not got["adjacent"]:
        fails.append("灵银矿与灵银沙没有相邻，就近排序失效")
    if "兑换" not in got["frameRemark"]:
        fails.append("骨架没标注兑换来源：%s" % got["frameRemark"])

    print("计算队列 %d / 直接素材 %d / 基础素材 %d"
          % (got["qCount"], got["dCount"], got["bCount"]))
    print("灵银矿：全无 %s / 已有100 %s / 管够 %s"
          % (got["ore"], got["oreHalf"], got["oreFull"]))
    print("失败: %d" % len(fails))
    for f in fails:
        print("  FAIL", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
