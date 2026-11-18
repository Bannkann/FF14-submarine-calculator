# -*- coding: utf-8 -*-
"""把数据 + 模板打包成一个单文件网页：dist/潜水艇材料计算器.html

交付物要求：双击即用、零外部依赖、断网可用、可直接发给朋友。
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "dist")
OUT = os.path.join(OUT_DIR, "潜水艇材料计算器.html")


def load(name):
    with open(os.path.join(ROOT, "data", name), encoding="utf-8") as f:
        return json.load(f)


TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>潜水艇材料计算器</title>
<style>
:root{
  --bg:#f6f7f9; --panel:#fff; --line:#e5e8ec; --text:#1f2329; --muted:#7b838d;
  --accent:#2f6fed; --accent-soft:#eaf1ff; --warn:#c2410c;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
  font:13.5px/1.5 -apple-system,"Segoe UI","Microsoft YaHei",sans-serif}
header{display:flex;align-items:center;gap:12px;flex-wrap:wrap;
  padding:11px 18px;background:var(--panel);border-bottom:1px solid var(--line);
  position:sticky;top:0;z-index:5}
h1{font-size:15.5px;margin:0;font-weight:600}
#code{font:600 15px/1 ui-monospace,Consolas,monospace;color:var(--accent);
  background:var(--accent-soft);padding:6px 10px;border-radius:6px}
.grow{flex:1}
button{font:inherit;cursor:pointer;border:1px solid var(--line);background:#fff;
  color:var(--text);padding:6px 12px;border-radius:7px}
button:hover{border-color:#c8cfd8}
button.primary{background:var(--accent);border-color:var(--accent);color:#fff}
button.primary:hover{background:#2a63d4}

main{display:flex;gap:14px;padding:14px 18px;align-items:flex-start}
aside{width:272px;flex:none;background:var(--panel);border:1px solid var(--line);
  border-radius:10px;padding:12px}
.slot{display:flex;align-items:center;gap:6px;margin-bottom:8px}
.slot .lb{width:34px;flex:none;font-size:12.5px;color:var(--muted)}
.slot select{font:inherit;font-size:12px;padding:5px 5px;
  border:1px solid var(--line);border-radius:6px;background:#fff;color:var(--text);min-width:0}
.slot select.part{flex:1}
.slot select.qty{width:54px;flex:none}
.design{margin-top:4px;padding-top:10px;border-top:1px dashed var(--line);
  font-size:12px;color:var(--muted);line-height:1.9}
.design b{color:var(--text);font-weight:600}

section.panel{flex:1;min-width:0;background:var(--panel);border:1px solid var(--line);
  border-radius:10px;overflow:hidden}
.sum{display:flex;gap:16px;flex-wrap:wrap;align-items:center;
  padding:8px 14px;border-bottom:1px solid var(--line);background:#fbfcfd;
  font-size:12.5px;color:var(--muted)}
.sum b{color:var(--text);font:600 13.5px/1 ui-monospace,monospace}
.sum .miss b{color:var(--warn)}

.board{display:grid;grid-template-columns:repeat(4,minmax(200px,1fr));
  overflow-x:auto;align-items:stretch}
.col{padding:10px 12px 16px;min-width:0;border-left:1px solid var(--line)}
.col:first-child{border-left:none;padding-left:14px}
.col h2{font-size:12px;margin:0 0 7px;font-weight:600;color:var(--muted);
  letter-spacing:.3px;display:flex;justify-content:space-between;align-items:center;gap:6px}
.col h2 label{display:flex;align-items:center;gap:5px;cursor:pointer;font-weight:600}
.col h2 span{font-weight:400;color:#a8afb8}
.list{display:flex;flex-direction:column}
.row{display:flex;gap:5px;align-items:center;padding:3px 4px;border-radius:5px;
  font-size:12.5px}
.row:hover{background:#f7f9fb}
.row .nm{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.row .qt{font:600 12px/1 ui-monospace,monospace;color:var(--accent);white-space:nowrap}
.row.enough .nm,.row.enough .qt{color:#b9c0c8;text-decoration:line-through}
.row.crystal .nm{color:#0e7490}
.ownwrap{position:relative;width:52px;flex:none;display:inline-block}
.own{width:100%;font:11px/1 ui-monospace,monospace;text-align:right;
  padding:2px 3px;border:1px solid var(--line);border-radius:4px;background:#fff;color:var(--text)}
.own:focus{outline:none;border-color:var(--accent)}
.ownwrap.is-max .own{color:transparent}
.ownwrap.is-max .own:focus{color:var(--text)}
.tick{display:none;position:absolute;left:7px;top:50%;transform:translateY(-50%);
  color:var(--accent);font:700 13px/1 sans-serif;pointer-events:none}
.ownwrap.is-max .tick{display:block}
.ownwrap.is-max .own:focus ~ .tick{display:none}
.note{font-size:11px;color:#98a1ab;line-height:1.5;padding:0 4px 2px 57px}
.note div{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.note .short{color:var(--warn)}
.xgroup{margin-bottom:5px}
.xtoggle{width:100%;text-align:left;cursor:pointer;font:inherit;font-size:11.5px;
  color:#0e7490;background:#f4fbfc;border:1px dashed #cfe6ea;border-radius:5px;
  padding:4px 7px}
.xtoggle:hover{background:#eaf7f9}
.xgroup.closed .xbody{display:none}
.exch{font:600 9.5px/1 -apple-system,"Microsoft YaHei",sans-serif;color:#fff;
  background:#0e7490;padding:3px 4px;border-radius:3px;margin-right:4px;flex:none}
.tag{font:600 10px/1 ui-monospace,monospace;color:#fff;background:#94a3b8;
  padding:3px 4px;border-radius:4px;margin-right:4px}
.tag.mod{background:#8b5cf6}
.empty{color:#b6bcc4;font-size:12px;padding:8px 4px}
footer{padding:8px 18px 22px;color:var(--muted);font-size:12px}
@media (max-width:1200px){ .board{grid-template-columns:repeat(2,minmax(200px,1fr))}
  .col:nth-child(3){border-left:none} }
@media (max-width:760px){
  main{flex-direction:column} aside{width:100%}
  .board{grid-template-columns:1fr}
  .col{border-left:none;border-top:1px solid var(--line)}
}
</style>
</head>
<body>
<header>
  <h1>潜水艇材料计算器</h1>
  <span id="code">—</span>
  <span class="grow"></span>
  <button id="copy">复制缺料清单</button>
  <button id="csv" class="primary">导出 CSV</button>
</header>

<main>
  <aside id="slots"></aside>
  <section class="panel">
    <div class="sum" id="sum"></div>
    <div class="board">
      <div class="col"><h2><label><input type="checkbox" id="all0">配件队列</label><span id="c0"></span></h2><div class="list" id="l0"></div></div>
      <div class="col"><h2><label><input type="checkbox" id="all1">计算队列</label><span id="c1"></span></h2><div class="list" id="l1"></div></div>
      <div class="col"><h2><label><input type="checkbox" id="all2">直接素材</label><span id="c2"></span></h2><div class="list" id="l2"></div></div>
      <div class="col"><h2><label><input type="checkbox" id="all3">基础素材</label><span id="c3"></span></h2><div class="list" id="l3"></div></div>
    </div>
  </section>
</main>

<footer id="foot"></footer>

<script id="core">
const DATA = __DATA__;

const PART_IDS = DATA.partIds;
const ITEMS = DATA.items;

function itemOf(id){ return ITEMS[String(id)]; }

// 水晶 / 碎晶 / 晶簇
function isCrystal(name){ return /水晶|碎晶|晶簇/.test(name); }

// 获取方式标签
const TAG_SHORT = {
  'NPC售卖': 'NPC',
  '军票兑换': '军票',
  '可采集': '采集',
  '潜水艇带取': '潜艇',
  '风茄兑换': '风茄',
  '薰衣草兑换': '薰衣草',
  '限时采集': '限时采集',
  '制作': '制作'
};
function sealCost(id){ return (DATA.seals && DATA.seals[String(id)]) || 0; }
function tagsOf(id){ return (DATA.tags && DATA.tags[String(id)]) || []; }
function tagHtml(id){
  return tagsOf(id).map(function(t){
    var label = TAG_SHORT[t] || t;
    var title = t;
    if(t === 'NPC售卖' && DATA.prices && DATA.prices[String(id)]){
      label += ' ' + DATA.prices[String(id)] + 'G';
      title = t + '：' + DATA.prices[String(id)] + ' 金币';
    }
    return '<span class="chip ' + (TAG_CLASS[t] || '') + '" title="' + title + '">' +
           label + '</span>';
  }).join('');
}
const TAG_CLASS = {
  'NPC售卖': 'c-npc', '军票兑换': 'c-seal', '可采集': 'c-gather',
  '潜水艇带取': 'c-sub', '风茄兑换': 'c-ex1', '薰衣草兑换': 'c-ex2',
  '限时采集': 'c-time', '制作': 'c-craft'
};

/**
 * 完全按参考站的层级：
 *   计算队列 = 部件直接材料中「需要制作」的那些（第 1 层，有配方的）
 *   直接素材 = 制作上面那些所需的材料（第 2 层，全部）
 *   基础素材 = 各层中所有「无配方」原料的累计
 *
 * 同一个原料可能同时出现在直接素材和基础素材（参考站也是如此，数字不同）。
 * 排序统一按物品 ID 升序。
 */
function compute(selections, owned){
  owned = owned || {};
  const queue = {};
  const direct = {};
  const base = {};
  const remain = {};

  function consume(id, qty){
    const k = String(id);
    const raw = Number(owned[k]);
    if(remain[k] === undefined) remain[k] = raw === -1 ? -1 : Math.max(0, Math.floor(raw || 0));
    let used;
    if(remain[k] === -1){
      used = qty;
    }else{
      used = Math.min(remain[k], qty);
      remain[k] -= used;
    }
    return {used: used, deficit: qty - used};
  }

  function add(map, id, name, need, used, parentName, parentIsFrame){
    const k = String(id);
    if(!map[k]) map[k] = {id:k, name:name, need:0, have:0, parents:{}, verbs:{}};
    const e = map[k];
    e.need += need;
    e.have += used;
    if(parentName){
      e.parents[parentName] = (e.parents[parentName] || 0) + need;
      e.verbs[parentName] = parentIsFrame ? '兑换' : '制作';
    }
    return e;
  }

  function isCraftable(node){ return !!(node && node.材料 && node.材料.length); }

  function craftsOf(node, deficit){
    const y = Math.max(node.产量 || 1, 1);
    return Math.ceil(deficit / y);
  }

  // 第 2 层及更深：只有原料进基础素材，其余继续往下拆
  function deep(id, qty, parentName, parentIsFrame){
    const node = itemOf(id);
    if(!node) return;
    const c = consume(id, qty);
    if(!isCraftable(node)){
      add(base, id, node.名称, qty, c.used, parentName, parentIsFrame);
      return;
    }
    if(c.deficit <= 0) return;
    const isFrame = node.来源 === 'frame';
    const n = craftsOf(node, c.deficit);
    for(const m of node.材料){
      deep(m.id, n * m.数量, node.名称, isFrame);
    }
  }

  // 第 2 层：全部进直接素材；原料同时进基础素材
  function level2(id, qty, parentName, parentIsFrame){
    const node = itemOf(id);
    if(!node) return;
    const c = consume(id, qty);
    add(direct, id, node.名称, qty, c.used, parentName, parentIsFrame);

    if(!isCraftable(node)){
      add(base, id, node.名称, qty, c.used, parentName, parentIsFrame);
      return;
    }
    if(c.deficit <= 0) return;
    const isFrame = node.来源 === 'frame';
    const n = craftsOf(node, c.deficit);
    for(const m of node.材料){
      deep(m.id, n * m.数量, node.名称, isFrame);
    }
  }

  for(const s of selections){
    if(!s) continue;
    const pid = PART_IDS[s.name];
    const node = itemOf(pid);
    if(!node) continue;
    const c = consume(pid, s.qty);
    if(c.deficit <= 0) continue;
    const n = craftsOf(node, c.deficit);
    // 第 1 层
    for(const m of (node.材料 || [])){
      const mNode = itemOf(m.id);
      const need = n * m.数量;
      const mc = consume(m.id, need);
      if(isCraftable(mNode)){
        add(queue, m.id, mNode.名称, need, mc.used, node.名称, false);
        if(mc.deficit > 0){
          const mn = craftsOf(mNode, mc.deficit);
          for(const x of mNode.材料){
            level2(x.id, mn * x.数量, mNode.名称, mNode.来源 === 'frame');
          }
        }
      }else{
        add(base, m.id, mNode.名称, need, mc.used, node.名称, false);
      }
    }
  }

  return {queue:queue, direct:direct, base:base};
}

function toList(map){
  return Object.keys(map).map(k=>{
    const e = map[k];
    e.deficit = Math.max(0, e.need - e.have);
    return e;
  });
}

// 排序：水晶类置顶，其余按「配方树就近」的全局序号（构建时算好，换部件也不会重排）
function bySeq(list, crystalFirst){
  return list.slice().sort((a,b)=>{
    if(crystalFirst){
      const ca = isCrystal(a.name), cb = isCrystal(b.name);
      if(ca !== cb) return ca ? -1 : 1;
    }
    const sa = ITEMS[a.id] ? ITEMS[a.id].seq : 9e9;
    const sb = ITEMS[b.id] ? ITEMS[b.id].seq : 9e9;
    return sa - sb;
  });
}

// 备注只记上一层：「其中 n 个用于制作/兑换 Y」
function noteLines(item){
  return Object.keys(item.parents || {})
    .map(p=>[p, item.parents[p]])
    .sort((a,b)=> b[1]-a[1])
    .map(([p, n]) => '其中 ' + n + ' 个用于' +
      ((item.verbs && item.verbs[p]) || '制作') + ' ' + p);
}

// 四位：无 = 0；四件都是改级才加「改」
function buildCode(selections){
  let digits = '', any = false, allMod = true;
  for(const s of selections){
    if(!s){ digits += '0'; continue; }
    const p = DATA.parts.find(x=>x.全名===s.name);
    digits += String(p.级别);
    any = true;
    if(p.是否改级 !== '是') allMod = false;
  }
  return any ? digits + (allMod ? '改' : '') : '—';
}
</script>

<script>
(function(){
  const SLOTS = ['船体','船尾','船首','舰桥'];
  const SEL = {}, QTY = {};
  const owned = {};        // id -> 数量；-1 = 管够
  let last = null;

  // ---------- 左侧：部位 + 数量 ----------
  const aside = document.getElementById('slots');

  // 常用套装：选中后自动填四个部位
  const presetRow = document.createElement('div');
  presetRow.className = 'slot preset-row';
  const pLabel = document.createElement('span');
  pLabel.className = 'lb';
  pLabel.textContent = '套装';
  const pSel = document.createElement('select');
  pSel.className = 'part';
  const pCustom = document.createElement('option');
  pCustom.value = '-1';
  pCustom.textContent = '— 自定义 —';
  pSel.appendChild(pCustom);
  (DATA.presets || []).forEach(function(p, i){
    const o = document.createElement('option');
    o.value = String(i);
    o.textContent = p.名称;
    pSel.appendChild(o);
  });
  const pQty = document.createElement('select');
  pQty.className = 'qty';
  for(let i=1;i<=5;i++){
    const o = document.createElement('option');
    o.value = String(i);
    o.textContent = '×' + i;
    pQty.appendChild(o);
  }
  presetRow.appendChild(pLabel);
  presetRow.appendChild(pSel);
  presetRow.appendChild(pQty);
  aside.appendChild(presetRow);

  for(const slot of SLOTS){
    const row = document.createElement('div');
    row.className = 'slot';
    const lb = document.createElement('span');
    lb.className = 'lb';
    lb.textContent = slot;

    const sel = document.createElement('select');
    sel.className = 'part';
    const none = document.createElement('option');
    none.value = '';
    none.textContent = '— 无 —';
    sel.appendChild(none);
    const group = DATA.parts.filter(p=>p.部件===slot)
      .sort((a,b)=> a.级别 - b.级别 || (a.是否改级==='是') - (b.是否改级==='是'));
    for(const p of group){
      const o = document.createElement('option');
      o.value = p.全名;
      o.textContent = p.配装字符 + '  ' + p.全名;
      sel.appendChild(o);
    }
    sel.value = '';

    const qty = document.createElement('select');
    qty.className = 'qty';
    for(let i=1;i<=5;i++){
      const o = document.createElement('option');
      o.value = String(i);
      o.textContent = '×' + i;
      qty.appendChild(o);
    }
    sel.addEventListener('change', render);
    qty.addEventListener('change', render);
    row.appendChild(lb); row.appendChild(sel); row.appendChild(qty);
    aside.appendChild(row);
    SEL[slot] = sel; QTY[slot] = qty;
  }
  pSel.addEventListener('change', function(){
    const idx = parseInt(pSel.value, 10);
    if (isNaN(idx) || idx < 0) return;
    const preset = (DATA.presets || [])[idx];
    if (!preset) return;
    SLOTS.forEach(function(slot, i){
      const name = preset.选择[i];
      SEL[slot].value = name || '';
      QTY[slot].value = pQty.value;
    });
    render();
  });

  pQty.addEventListener('change', function(){
    SLOTS.forEach(function(slot){ QTY[slot].value = pQty.value; });
    render();
  });

  const designBox = document.createElement('div');
  designBox.className = 'design';
  aside.appendChild(designBox);

  function selections(){
    return SLOTS.map(slot=>{
      if(!SEL[slot].value) return null;
      return {name: SEL[slot].value, qty: parseInt(QTY[slot].value, 10) || 1, slot: slot};
    });
  }
  function partInfo(name){ return DATA.parts.find(x=>x.全名===name); }

  // ---------- 渲染 ----------
  function render(){
    const sel = selections();
    const code = buildCode(sel);
    document.getElementById('code').textContent = code;

    const designs = new Set();
    for(const s of sel){
      if(!s) continue;
      const rec = DATA.recipes[s.name];
      if(rec && rec.解锁设计图) designs.add(rec.解锁设计图);
    }
    const filled = sel.filter(Boolean).length;
    designBox.innerHTML = filled
      ? '已选 <b>' + filled + '</b> / 4 个部位<br>需要设计图：<b>' +
        [...designs].sort().join('、') + '</b>'
      : '四个部位都是「无」，选一个再看看';

    last = compute(sel, owned);
    const lists = {
      queue: bySeq(toList(last.queue), true),
      direct: bySeq(toList(last.direct), true),
      base: bySeq(toList(last.base), true)
    };

    const every = lists.queue.concat(lists.direct, lists.base);
    const miss = every.filter(x=>x.deficit > 0);
    const missSum = miss.reduce((s,x)=>s+x.deficit,0);
    const totalQty = sel.reduce((s,x)=> s + (x ? x.qty : 0), 0);
    document.getElementById('sum').innerHTML =
      '配装 <b>' + code + '</b>　' +
      (totalQty > 1 ? '共 <b>' + totalQty + '</b> 件　' : '') +
      '直接素材 <b>' + lists.direct.length + '</b> 种 / 原料 <b>' + lists.base.length + '</b> 种　' +
      '<span class="miss">还缺 <b>' + miss.length + '</b> 种 / <b>' + missSum + '</b> 件</span>';

    renderParts(sel);
    fillList('l1', lists.queue, 'c1', true, true);
    fillList('l2', lists.direct, 'c2', true, true);
    fillList('l3', lists.base, 'c3', true, true);

    bindAll('all0', sel.filter(Boolean).map(s=>DATA.partIds[s.name]));
    bindAll('all1', lists.queue.map(x=>x.id));
    bindAll('all2', lists.direct.map(x=>x.id));
    bindAll('all3', lists.base.map(x=>x.id));
  }

  // 表头全选：勾上 = 全部「管够」，取消 = 全部清零
  function bindAll(boxId, ids){
    const box = document.getElementById(boxId);
    if(!box) return;
    box.checked = ids.length > 0 && ids.every(id=>owned[id] === -1);
    box.onchange = function(){
      if(box.checked) ids.forEach(id=>{ owned[id] = -1; });
      else ids.forEach(id=>{ delete owned[id]; });
      render();
    };
  }

  function ownInput(id, have){
    const maxed = have === -1;
    return '<span class="ownwrap' + (maxed ? ' is-max' : '') + '">' +
           '<input class="own" type="number" step="1" data-own="' + id + '"' +
           ' value="' + (maxed ? '' : (have > 0 ? have : '')) + '"' +
           ' placeholder="0" title="填 0 后点 ↓ 或直接填 -1 = 管够（√）">' +
           '<span class="tick">√</span></span>';
  }

  function renderParts(sel){
    const box = document.getElementById('l0');
    let html = '';
    for(const s of sel){
      if(!s){ continue; }
      const p = partInfo(s.name);
      const pid = DATA.partIds[s.name];
      const have = owned[String(pid)];
      const done = have === -1 || have >= s.qty;
      const cls = p.是否改级 === '是' ? 'tag mod' : 'tag';
      html += '<div class="row' + (done ? ' enough' : '') + '">' +
              ownInput(pid, have || 0) +
              '<span class="nm"><span class="' + cls + '">' + p.配装字符 + '</span>' +
              s.slot + ' ' + s.name.replace(/级船|改级船/, '') + '</span>' +
              '<span class="qt">×' + s.qty + '</span></div>';
    }
    box.innerHTML = html || '<div class="empty">未选择部件</div>';
    bindOwn(box);
    document.getElementById('c0').textContent = sel.filter(Boolean).length + ' 件';
  }

  // 计算队列：部件本身 + 需要合成几次
  function renderQueue(parts){
    const box = document.getElementById('l1');
    let html = '';
    for(const p of parts){
      const done = p.deficit <= 0;
      html += '<div class="row' + (done ? ' enough' : '') + '">' +
              '<span class="nm" title="' + p.name + '">' + p.name + '</span>' +
              '<span class="qt">×' + p.need + '</span></div>';
      if(p.crafts > 1){
        html += '<div class="note"><div>需合成 ' + p.crafts + ' 次</div></div>';
      }
    }
    box.innerHTML = html || '<div class="empty">未选择部件</div>';
    document.getElementById('c1').textContent = parts.length ? parts.length + ' 件' : '';
  }

  function fillList(boxId, list, countId, withNote, groupSpecial){
    const box = document.getElementById(boxId);
    const sealItems = [], xs = [], rest = [];
    for(const it of list){
      if(groupSpecial && sealCost(it.id) > 0) sealItems.push(it);
      else if(groupSpecial && isCrystal(it.name)) xs.push(it);
      else rest.push(it);
    }

    const rowHtml = it => {
      const crystal = isCrystal(it.name);
      const done = it.deficit <= 0;
      const ownVal = owned[it.id] === undefined ? 0 : owned[it.id];
      let html = '<div class="row' + (done ? ' enough' : '') + (crystal ? ' crystal' : '') + '">' +
                 ownInput(it.id, ownVal) +
                 '<span class="nm" title="' + it.name + '">' + it.name + '</span>' +
                 tagHtml(it.id) +
                 '<span class="qt">×' + it.need + '</span></div>';
      if(withNote){
        const node = ITEMS[it.id];
        const extra = (node && node.备注) ? ['（' + node.备注 + '）'] : [];
        const lines = crystal ? extra : extra.concat(noteLines(it));
        const short = it.deficit > 0 && it.have > 0
          ? '<div class="short">还缺 ' + it.deficit + ' 个</div>' : '';
        if(lines.length || short){
          html += '<div class="note">' + short +
                  lines.map(l=>'<div title="' + l + '">' + l + '</div>').join('') +
                  '</div>';
        }
      }
      return html;
    };

    function groupHtml(items, title){
      return '<div class="xgroup closed"><button class="xtoggle" type="button">▸ ' + title +
             '</button><div class="xbody">' + items.map(rowHtml).join('') + '</div></div>';
    }

    let html = '';
    if(sealItems.length){
      const seals = sealItems.reduce((s,x)=> s + sealCost(x.id) * x.need, 0);
      html += groupHtml(sealItems, '军票兑换 · ' + sealItems.length + ' 种 · 共 ' + seals + ' 军票');
    }
    if(xs.length){
      html += groupHtml(xs, '水晶 / 碎晶 / 晶簇 · ' + xs.length + ' 种');
    }
    html += rest.map(rowHtml).join('');

    box.innerHTML = html || '<div class="empty">无</div>';

    box.querySelectorAll('.xtoggle').forEach(function(btn){
      btn.onclick = function(){
        const grp = btn.parentNode;
        const closed = grp.classList.toggle('closed');
        btn.textContent = (closed ? '▸ ' : '▾ ') + btn.textContent.slice(2);
      };
    });

    bindOwn(box);
    document.getElementById(countId).textContent = list.length ? list.length + ' 种' : '';
  }

  function bindOwn(box){
    box.querySelectorAll('input[data-own]').forEach(inp=>{
      const id = inp.dataset.own;
      function apply(raw){
        raw = String(raw == null ? inp.value : raw).trim();
        let v;
        if(raw === '') v = 0;
        else if(raw === '-1') v = -1;            // ↓ 从 0 再点一下就是最大值
        else v = Math.max(0, Math.floor(Number(raw) || 0));
        if(v === -1 || v > 0) owned[id] = v; else delete owned[id];
        render();
      }
      // 箭头点出 -1 时立刻生效；打字过程中不打断
      inp.oninput = function(){ if(String(inp.value).trim() === '-1') apply('-1'); };
      inp.onchange = function(){ apply(); };
      inp.onfocus = function(){ this.select(); };
    });
  }

  // ---------- 交互 ----------
  document.getElementById('copy').addEventListener('click', ()=>{
    const sel = selections();
    const list = bySeq(toList(compute(sel, owned).base), true).filter(x=>x.deficit > 0);
    const lines = ['配装 ' + buildCode(sel) + ' 缺料清单', ''];
    for(const x of list) lines.push(x.name + ' ×' + x.deficit);
    navigator.clipboard.writeText(lines.join('\n')).then(
      ()=>{ document.getElementById('foot').textContent = '已复制 ' + list.length + ' 种缺料'; },
      ()=>{ document.getElementById('foot').textContent = '复制失败，请手动选择文本'; });
  });

  document.getElementById('csv').addEventListener('click', ()=>{
    const sel = selections();
    const res = compute(sel, owned);
    const rows = [['材料','需要','已有','还缺','获取方式','备注']];
    const baseList = bySeq(toList(res.base));
    const baseIds = {};
    baseList.forEach(x=>{ baseIds[x.id] = true; });
    const push = list => {
      for(const x of list){
        const note = isCrystal(x.name) ? '' : noteLines(x).join('；');
        rows.push([x.name, x.need, x.have === x.need ? '管够' : x.have, x.deficit, '', note]);
      }
    };
    push(baseList);
    push(bySeq(toList(res.queue), false));
    push(bySeq(toList(res.direct), false).filter(x=>!baseIds[x.id]));
    const csv = rows.map(r=>r.map(c=>'"' + String(c).replace(/"/g,'""') + '"').join(',')).join('\r\n');
    const blob = new Blob(['\ufeff' + csv], {type:'text/csv;charset=utf-8'});
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = '潜水艇材料_' + buildCode(sel) + '.csv';
    a.click();
    setTimeout(()=>URL.revokeObjectURL(a.href), 1000);
  });

  document.getElementById('foot').textContent =
    '标签：NPC = NPC售卖（带价格），军票 = 军票兑换，采集 = 可采集，限时 = 限时采集点，' +
    '潜艇 = 潜水艇带取，风茄 / 薰衣草 = 对应兑换，制作 = 需要制作　|　' +
    '「已有」填数量：填 0 后再点 ↓ 或直接填 -1 即为管够（√）；表头勾选 = 整列管够　|　' +
    '获取方式数据待接入　|　生成时间 ' + DATA.buildTime;
  render();
})();
</script>
</body>
</html>
"""


def global_order(graph, parts):
    """全局排序：按部件顺序（1、1改、2、2改…）对配方树做深度优先遍历，
    每个物品取首次出现的序号。这样任何配装下，相关性近的材料都挨在一起，
    且顺序与「当前选了哪些部件」无关。
    """
    items = graph["items"]
    part_ids = graph["parts"]
    order = {}
    counter = [0]

    def walk(iid):
        key = str(iid)
        if key in order:
            return
        order[key] = counter[0]
        counter[0] += 1
        node = items.get(key)
        if not node:
            return
        for m in node["材料"]:
            walk(m["id"])

    for p in parts:
        pid = part_ids.get(p["全名"])
        if pid:
            walk(pid)
    return order


def main():
    import time
    parts = load("parts.json")
    graph = load("graph.json")
    recipes = load("recipes.json")

    order = global_order(graph, parts)
    for iid, node in graph["items"].items():
        node["seq"] = order.get(iid, 999999)

    tags_all = load("tags.json") if os.path.exists(os.path.join(ROOT, "data", "tags.json")) else {}
    tags = {k: v for k, v in tags_all.items() if k in graph["items"]}
    # 有配方的物品补一个「制作」标签
    for iid, node in graph["items"].items():
        if node.get("材料"):
            tags.setdefault(iid, [])
            if "制作" not in tags[iid]:
                tags[iid].append("制作")
    prices_all = load("prices.json") if os.path.exists(os.path.join(ROOT, "data", "prices.json")) else {}
    prices = {k: v for k, v in prices_all.items() if k in graph["items"]}
    data = {
        "parts": parts,
        "partIds": graph["parts"],
        "items": graph["items"],
        "tags": tags,
        "prices": prices,
        "seals": {k: v for k, v in (load("seals.json") if os.path.exists(os.path.join(ROOT, "data", "seals.json")) else {}).items() if k in graph["items"]},
        "presets": load("presets.json") if os.path.exists(os.path.join(ROOT, "data", "presets.json")) else [],
        "recipes": {r["部件"]: r for r in recipes},
        "buildTime": time.strftime("%Y-%m-%d %H:%M"),
    }
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    payload = payload.replace("</", "<\\/")

    html = TEMPLATE.replace("__DATA__", payload)
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print("生成 %s（%.1f KB）" % (OUT, os.path.getsize(OUT) / 1024.0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
