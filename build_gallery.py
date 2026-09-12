#!/usr/bin/env python3
# ICMC 历届主题画廊：从 index.html 抽取各届海报、主题故事、奖牌样式、奖项设置
# 产出 vi.html（部署后经 Vercel cleanUrls 以 icmc.itccc.app/vi 访问）
import re, html as H, datetime

ED = [
    # tag, cn, season, theme, accent, note（官方未发主题故事时用 tasks 概览代替）
    ("3",  "第三届",  "2017",        "火星勘探大挑战",  "#b0713a", ""),
    ("4",  "第四届",  "2018",        "月球基地大挑战",  "#8d8d93", ""),
    ("5",  "第五届",  "2019 上半年", "亚特兰蒂斯传奇",  "#3a8fa0", ""),
    ("6",  "第六届",  "2019 下半年", "海岛探险",        "#5a9e6f", ""),
    ("7",  "第七届",  "2020",        "矿石远征",        "#a05a5a", "疫情年，特别推出远程赛场"),
    ("9",  "第九届",  "2021 上半年", "冰雪奇缘",        "#4a90b8", ""),
    ("10", "第十届",  "2021 下半年", "星际矿场",        "#946e3c", ""),
    ("11", "第十一届", "2022 上半年", "废料星球大冒险",  "#6a67a8", ""),
    ("12", "第十二届", "2022 下半年", "月球基地大冒险",  "#3e8a7e", ""),
    ("13", "第十三届", "2023",        "星际工厂大挑战",  "#b85450", ""),
    ("14", "第十四届", "2023 下半年", "智慧城市大冒险",  "#7a5ca8", ""),
    ("15", "第十五届", "2024 上半年", "宇航基地历险记",  "#e8734a", ""),
    ("16", "第十六届", "2024 下半年", "泰坦星球大冒险",  "#7c5cb0", ""),
    ("17", "第十七届", "2025 上半年", "星际农场奇遇记",  "#3a9d6e", ""),
    ("18", "第十八届", "2025 下半年", "超级港口大挑战",  "#2f7fbf", ""),
    ("19", "第十九届", "2026 上半年", "行星能源大时代",  "#c0405e", ""),
]
TASKS = {  # 无官方主题故事届的任务一览（取自规则页任务标题）
    "6": ["JR组：建造海岛互通桥", "机械组：奇妙的机械臂", "动力组：快速运送能量球", "智能组：智能矿石采集"],
    "7": ["JR组：矿石大运输", "机械组：开启机械栏杆", "动力组：定点投放能量块", "智能组：智能包裹配送"],
    "9": ["JR组：钓鱼小能手", "机械组：安全运送燃料球", "动力组：神奇管道探测器",
          "感控组：远程遥控铲雪车", "智能组：轮胎搬运大挑战"],
}

def edition_seg(html, tag):
    i = html.find('id="e%s"' % tag)
    s = html.rfind('<section', 0, i)
    e = html.find('</section>', i)
    return html[s:e]

def extract(html, tag):
    seg = edition_seg(html, tag)
    art = seg[seg.find('<div class="article">') + 21:]
    cuts = [x for x in (art.find('<div class="taskcard"'), art.find('<div class="seccard"')) if x > 0]
    pre = art[:min(cuts)] if cuts else art
    # 海报：优先前言首图；第10届用主题立绘图（10/02.png）
    poster = re.search(r'<figure><img src="([^"]+)" /></figure>', pre)
    poster = poster.group(1) if poster else ''
    if tag == '10':
        poster = 'images/10/02.png'
    # 故事：前言里非简介、非标题的段落
    paras = re.findall(r'<p[^>]*>([^<]{8,})</p>', pre)
    story = [p for p in paras if not p.startswith('201') and 'ICMC' not in p[:40] and '侵权' not in p]
    # 奖牌图：奖项设立卡片第一图
    medal = re.search(r'奖项设立</h4><figure><img src="([^"]+)"', seg)
    medal = medal.group(1) if medal else ''
    # 奖项列表
    awards = []
    am = re.search(r'奖项设立</h4>([\s\S]*?)</div>', seg)
    if am:
        for m in re.finditer(r'<li>([^<]+)</li>|<p>([^<]+)</p>', am.group(1)):
            txt = m.group(1) or m.group(2)
            if '授予' in txt:
                awards.append(txt)
    return poster, story, medal, awards

def card(tag, cn, season, theme, accent, note, poster, story, medal, awards):
    story_html = ''.join(f'<p class="g-story">{H.escape(p)}</p>' for p in story)
    if not story_html and tag in TASKS:
        story_html = ('<p class="g-story-tip">官方页面未发布主题故事，本届任务：</p>'
                      + '<ul class="g-tasks">' + ''.join(f'<li>{H.escape(x)}</li>' for x in TASKS[tag]) + '</ul>')
    note_html = f'<p class="g-note">❄ {H.escape(note)}</p>' if note else ''
    return f'''
<article class="gcard" style="--accent:{accent}">
  <div class="g-poster"><img src="{poster}" alt="{cn} {theme} 海报" loading="lazy"></div>
  <div class="g-body">
    <div class="g-head">
      <span class="g-badge">{cn}</span>
      <div class="g-title"><h2>{H.escape(theme)}</h2><span class="g-season">{season}</span></div>
      <a class="g-link" href="/#e{tag}">规则详情 →</a>
    </div>
    {note_html}
    <div class="g-cols">
      <div class="g-col">
        <h3 class="g-h"><span class="ic">📖</span>主题故事</h3>
        {story_html or '<p class="g-story-tip">官方页面未发布主题故事。</p>'}
      </div>
      <div class="g-col">
        <h3 class="g-h"><span class="ic">🏅</span>奖牌样式</h3>
        <div class="g-medal"><img src="{medal}" alt="{cn}奖牌与证书" loading="lazy"></div>
      </div>
    </div>
  </div>
</article>'''

def main():
    html = open('index.html', encoding='utf-8').read()
    cards = []
    for tag, cn, season, theme, accent, note in ED:
        poster, story, medal, awards = extract(html, tag)
        assert poster and medal and awards, f'第{tag}届数据缺失: {poster} {medal} {len(awards)}'
        cards.append(card(tag, cn, season, theme, accent, note, poster, story, medal, awards))
        print(f'{tag} ✓ story={len(story)} awards={len(awards)}')
    today = datetime.date.today().strftime('%Y-%m-%d')
    page = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ICMC 历届主题画廊 · 第3–19届</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  body {{ font-family:-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
         background:#f6f6f4; color:#26241f; line-height:1.75; }}
  .top {{ max-width:980px; margin:0 auto; padding:44px 20px 6px; }}
  .top h1 {{ font-size:25px; letter-spacing:1px; }}
  .top h1 a {{ float:right; font-size:14px; font-weight:400; color:#2f7fbf; text-decoration:none; }}
  .top p {{ color:#6b675c; font-size:14px; margin-top:8px; }}
  .gal {{ max-width:980px; margin:20px auto 70px; padding:0 20px; }}
  .gcard {{ background:#fff; border:1px solid #e4e1d9; border-left:5px solid var(--accent);
            border-radius:14px; overflow:hidden; margin:26px 0;
            box-shadow:0 1px 3px rgba(0,0,0,.04); }}
  .g-poster {{ border-bottom:1px solid #eee; background:#fff; }}
  .g-poster img {{ display:block; width:100%; height:auto; max-height:420px; object-fit:cover; object-position:center; }}
  .g-body {{ padding:20px 26px 24px; }}
  .g-head {{ display:flex; align-items:center; gap:12px; flex-wrap:wrap; }}
  .g-badge {{ background:var(--accent); color:#fff; font-size:13px; font-weight:700;
              padding:3px 12px; border-radius:20px; white-space:nowrap; }}
  .g-title h2 {{ font-size:21px; display:inline; }}
  .g-season {{ font-size:13px; color:#8a857a; margin-left:10px; }}
  .g-link {{ margin-left:auto; font-size:13.5px; color:#2f7fbf; text-decoration:none; white-space:nowrap; }}
  .g-note {{ margin-top:10px; font-size:13px; color:#a15c00; background:#fff7e8;
             border:1px solid #f0dcb4; border-radius:8px; padding:6px 12px; display:inline-block; }}
  .g-cols {{ display:grid; grid-template-columns:1.15fr 1fr; gap:26px; margin-top:14px; }}
  @media (max-width:760px) {{ .g-cols {{ grid-template-columns:1fr; }} }}
  .g-medal {{ border:1px solid #e9e6dd; border-radius:10px; overflow:hidden; background:#fafafa;
              text-align:center; }}
  .g-medal img {{ display:block; max-width:100%; height:auto; margin:0 auto; }}
  .g-h {{ font-size:15px; margin-bottom:8px; color:#3a372f; }}
  .g-h .ic {{ margin-right:4px; }}
  .g-story {{ font-size:14.5px; color:#44413a; margin:6px 0; text-align:justify; }}
  .g-story-tip {{ font-size:13.5px; color:#8a857a; margin:6px 0; }}
  .g-tasks {{ list-style:none; margin:4px 0 0 4px; }}
  .g-tasks li {{ font-size:14px; padding-left:16px; position:relative; margin:4px 0; }}
  .g-tasks li::before {{ content:"·"; position:absolute; left:4px; color:var(--accent); font-weight:700; }}
  footer {{ max-width:980px; margin:0 auto 60px; padding:0 20px; font-size:13px; color:#8a857a; }}
</style>
</head>
<body>
<div class="top">
  <h1>ICMC 历届主题画廊 <a href="/">« 返回规则页</a></h1>
  <p>第 3–19 届主题名称、主题故事与奖牌样式一览。图片取自 ICMC 官网各届发布页。整理日期：{today}</p>
</div>
<div class="gal">{''.join(cards)}</div>
<footer>来源：ICMC 官网（www.icmc100.com）。主题名称以官方海报为准；官方未发布主题故事的届次以任务概览代替。</footer>
</body>
</html>'''
    open('vi.html', 'w', encoding='utf-8').write(page)
    print('vi.html', len(page))

if __name__ == '__main__':
    main()
