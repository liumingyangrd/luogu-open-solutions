#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从洛谷档案馆 API 拉取「当前允许提交题解」的题目，重新生成 index.html。

用法：
    python update_data.py

数据源：https://www.luogu.ac.cn （第三方洛谷存档站，开源：lga-team/luogu-archive）
说明：洛谷会对题解过多的题目关闭题解提交通道，本仓库只收录通道仍开放的题目。
"""
import json
import urllib.parse
import urllib.request

API = "https://www.luogu.ac.cn/api/v1/problem/list"
TIERS = ["普及", "普及+/提高-", "提高", "提高+/省选-", "省选/NOI-", "NOI/NOI+/CTS", "暂无评定"]
COLOR = {
    "普及": ("#E8A33D", "#fff"),
    "普及+/提高-": ("#5BA85B", "#fff"),
    "提高": ("#3E9BB5", "#fff"),
    "提高+/省选-": ("#4A6FB5", "#fff"),
    "省选/NOI-": ("#7B5CB8", "#fff"),
    "NOI/NOI+/CTS": ("#3B3B3B", "#fff"),
    "暂无评定": ("#8A8A8A", "#fff"),
}

TPL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>洛谷「可发题解」题目速查</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: "PingFang SC", "Microsoft YaHei", "Segoe UI", sans-serif; background: #f5f6f8; color: #2a2f36; line-height: 1.55; }
  .wrap { max-width: 1080px; margin: 0 auto; padding: 28px 20px 60px; }
  header h1 { font-size: 24px; font-weight: 700; }
  header .sub { color: #6b7280; font-size: 13.5px; margin-top: 6px; }
  .cards { display: flex; flex-wrap: wrap; gap: 10px; margin: 18px 0 6px; }
  .card { background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 10px 14px; min-width: 108px; }
  .card .n { font-size: 20px; font-weight: 700; }
  .card .l { font-size: 12px; color: #6b7280; }
  .toolbar { position: sticky; top: 0; background: #f5f6f8; padding: 14px 0 10px; z-index: 5; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
  .search { flex: 1 1 260px; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; background: #fff; }
  .chips { display: flex; flex-wrap: wrap; gap: 6px; margin: 4px 0 12px; }
  .chip { border: 1px solid #d1d5db; background: #fff; border-radius: 999px; padding: 4px 12px; font-size: 13px; cursor: pointer; color: #374151; }
  .chip b { font-weight: 600; }
  .chip.active { background: #2f6fdb; border-color: #2f6fdb; color: #fff; }
  .chip.active b { color: #fff; }
  .count { font-size: 13px; color: #6b7280; margin-bottom: 8px; }
  table { width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; overflow: hidden; font-size: 13.5px; }
  th { text-align: left; background: #fafbfc; border-bottom: 1px solid #e5e7eb; padding: 8px 10px; font-size: 12.5px; color: #6b7280; font-weight: 600; white-space: nowrap; }
  td { border-bottom: 1px solid #f0f1f3; padding: 7px 10px; vertical-align: top; }
  tr:last-child td { border-bottom: none; }
  tr.hidden { display: none; }
  a { color: #2f6fdb; text-decoration: none; }
  a:hover { text-decoration: underline; }
  .pidcell { white-space: nowrap; font-weight: 600; width: 92px; }
  .titlecell { min-width: 220px; }
  .titlecell a { color: inherit; }
  .titlecell a:hover { color: #2f6fdb; text-decoration: underline; }
  .diff { display: inline-block; border-radius: 6px; padding: 1px 8px; font-size: 12px; white-space: nowrap; }
  .tagcell { width: 300px; }
  .tag { display: inline-block; background: #f1f3f5; color: #5b6470; border-radius: 5px; padding: 0 6px; font-size: 11.5px; margin: 0 3px 3px 0; white-space: nowrap; }
  .note { background: #fff8e6; border: 1px solid #f3e2a8; border-radius: 10px; padding: 12px 14px; font-size: 13px; color: #7a5d00; margin: 16px 0; }
  .src { background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px 16px; font-size: 13px; margin-top: 18px; }
  .src code { background: #f1f3f5; border-radius: 5px; padding: 1px 6px; font-size: 12px; word-break: break-all; }
  .src li { margin: 5px 0 5px 18px; }
  @media (max-width: 720px) { .tagcell { display: none; } }
</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>洛谷「可发题解」题目速查</h1>
  <div class="sub">数据来源：<a href="https://www.luogu.ac.cn" target="_blank" rel="noopener">洛谷档案馆</a>（luogu.ac.cn，第三方洛谷存档站） · 快照时间：__SNAP__ · 共 __TOTAL__ 道题的题解提交通道当前为开放状态</div>
</header>
<div class="cards">__CARDS__</div>
<div class="note">
  说明：洛谷对题解过多的题目会关闭题解提交通道（提示「不能提交该题题解」），只有仍开放的题目才能发题解。本页数据为离线快照（档案馆目录全量抓取于 __CRAWLED__，各题状态按难度分档持续轮询），可能与洛谷实时状态有短暂出入；以题目页实际显示为准。「入门 / 普及-」两档当前没有收录到开放题解的题目。
</div>
<div class="toolbar">
  <input id="q" class="search" type="text" placeholder="搜索题号 / 标题 / 标签，如 P1000、线段树、DP…">
</div>
<div class="chips">__CHIPS__</div>
<div class="count" id="count"></div>
<table>
  <thead><tr><th>题号</th><th>标题</th><th>难度</th><th>标签</th></tr></thead>
  <tbody id="tb">__ROWS__</tbody>
</table>
<div class="src">
  <b>查看实时数据 / 持续关注：</b>
  <ul>
    <li>洛谷档案馆主页：<a href="https://www.luogu.ac.cn" target="_blank" rel="noopener">https://www.luogu.ac.cn</a>（站内「题目库」页即「允许提交题解的题目」列表，可按难度分档查看；目前新版前端尚未上线该页，可先用下方 API）</li>
    <li>总览 API：<code>https://www.luogu.ac.cn/api/v1/problem/list?preview_limit=20</code></li>
    <li>单档全量 API：<code>https://www.luogu.ac.cn/api/v1/problem/list/by-difficulty?difficulty=省选/NOI-</code>（URL 编码后传入，如 <code>%E7%9C%81%E9%80%89/NOI-</code>）</li>
    <li>项目开源：<a href="https://github.com/lga-team/luogu-archive" target="_blank" rel="noopener">github.com/lga-team/luogu-archive</a></li>
  </ul>
</div>
</div>
<script>
var tier = "__all", kw = "";
var chips = document.querySelectorAll(".chip");
var rows = Array.prototype.slice.call(document.querySelectorAll("#tb tr"));
var countEl = document.getElementById("count");
function apply() {
  var n = 0;
  rows.forEach(function(r) {
    var ok = (tier === "__all" || r.getAttribute("data-tier") === tier) &&
             (kw === "" || r.getAttribute("data-search").indexOf(kw) !== -1);
    r.classList.toggle("hidden", !ok);
    if (ok) n++;
  });
  countEl.textContent = "当前显示 " + n + " 道";
}
chips.forEach(function(c) {
  c.addEventListener("click", function() {
    chips.forEach(function(x) { x.classList.remove("active"); });
    c.classList.add("active");
    tier = c.getAttribute("data-tier");
    apply();
  });
});
document.getElementById("q").addEventListener("input", function(e) {
  kw = e.target.value.trim().toLowerCase();
  apply();
});
apply();
</script>
</body>
</html>
"""


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "luogu-open-solutions/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    from datetime import datetime

    crawled = "未知"
    try:
        c = get_json("https://www.luogu.ac.cn/api/v1/last-crawled?type=problem_catalog")
        crawled = (c.get("last_crawled_at") or "未知")[:10]
    except Exception:
        pass

    tiers = {}
    for t in TIERS:
        enc = urllib.parse.quote(t, safe="")  # 注意 safe=""，"/" 也必须编码，否则接口返回空
        d = get_json(f"{API}/by-difficulty?difficulty={enc}")
        tiers[t] = d if isinstance(d, list) else d.get("items", [])
        print(f"{t}: {len(tiers[t])} 道")

    total = sum(len(v) for v in tiers.values())
    snap = datetime.now().strftime("%Y-%m-%d %H:%M")

    rows = []
    for t in TIERS:
        bg, fg = COLOR[t]
        for p in tiers[t]:
            tags = p.get("tags") or []
            tag_html = "".join(f'<span class="tag">{x}</span>' for x in tags[:6])
            s = (p["pid"] + " " + p["title"] + " " + " ".join(map(str, tags))).lower().replace('"', "&quot;")
            rows.append(
                f'<tr data-tier="{t}" data-search="{s}">'
                f'<td class="pidcell"><a href="https://www.luogu.com.cn/problem/{p["pid"]}" target="_blank" rel="noopener">{p["pid"]}</a></td>'
                f'<td class="titlecell"><a href="https://www.luogu.com.cn/problem/{p["pid"]}" target="_blank" rel="noopener">{p["title"]}</a></td>'
                f'<td><span class="diff" style="background:{bg};color:{fg}">{t}</span></td>'
                f'<td class="tagcell">{tag_html}</td></tr>'
            )

    chips = [f'<button class="chip active" data-tier="__all">全部 <b>{total}</b></button>']
    for t in TIERS:
        chips.append(f'<button class="chip" data-tier="{t}">{t} <b>{len(tiers[t])}</b></button>')

    cards = [f'<div class="card"><div class="n">{total}</div><div class="l">合计</div></div>']
    for t in TIERS:
        bg, _ = COLOR[t]
        cards.append(f'<div class="card"><div class="n" style="color:{bg}">{len(tiers[t])}</div><div class="l">{t}</div></div>')

    html = (TPL.replace("__SNAP__", snap).replace("__TOTAL__", str(total))
            .replace("__CRAWLED__", crawled)
            .replace("__CARDS__", "".join(cards)).replace("__CHIPS__", "".join(chips))
            .replace("__ROWS__", "\n".join(rows)))

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"已生成 index.html：共 {total} 道可发题解的题目（快照 {snap}）")


if __name__ == "__main__":
    main()
