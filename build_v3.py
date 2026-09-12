#!/usr/bin/env python3
# ICMC 规则页 v3：按行重建语义化结构（标准列表 + 圆角标签 + 任务卡片 + 组别筛选）
import re, json, html as H

META = [
    dict(tag="3", cn="第三届", season="2017", theme="火星勘探大挑战",
         url="http://www.icmc100.com/newsinfo/25111.html", pub="2017-11",
         doc="", accent="#b0713a"),
    dict(tag="4", cn="第四届", season="2018", theme="登陆月球",
         url="http://www.icmc100.com/newsinfo/253311.html", pub="2018-05",
         doc="", accent="#8d8d93"),
    dict(tag="5", cn="第五届", season="2019 上半年", theme="亚特兰蒂斯传奇",
         url="http://www.icmc100.com/newsinfo/826152.html", pub="2019-04",
         doc="", accent="#3a8fa0"),
    dict(tag="6", cn="第六届", season="2019 下半年", theme="海岛探险",
         url="http://www.icmc100.com/newsinfo/1575287.html", pub="2019-10",
         doc="", accent="#5a9e6f"),
    dict(tag="7", cn="第七届", season="2020", theme="矿石远征",
         url="http://www.icmc100.com/newsinfo/432441.html", pub="2020-07",
         doc="", accent="#a05a5a",
         note="疫情年，第七届特别推出远程赛：机构内搭建远程赛场，裁判视频连线一对一裁决"),
    dict(tag="9", cn="第九届", season="2021 上半年", theme="冰雪奇缘",
         url="http://www.icmc100.com/newsinfo/2373207.html", pub="2021-03",
         doc="", accent="#4a90b8"),
    dict(tag="10", cn="第十届", season="2021 下半年", theme="星际矿场",
         url="http://www.icmc100.com/newsinfo/1901340.html", pub="2021-09",
         doc="", accent="#946e3c"),
    dict(tag="11", cn="第十一届", season="2022 上半年", theme="废料星球大冒险",
         url="http://www.icmc100.com/newsinfo/2457727.html", pub="2022-03",
         doc="", accent="#6a67a8"),
    dict(tag="12", cn="第十二届", season="2022 下半年", theme="月球基地大冒险",
         url="http://www.icmc100.com/newsinfo/4359913.html", pub="2022-09",
         doc="", accent="#3e8a7e"),
    dict(tag="13", cn="第十三届", season="2023", theme="星际工厂大挑战",
         url="http://www.icmc100.com/newsinfo/5599566.html", pub="2023-03",
         doc="", accent="#b85450"),
    dict(tag="14", cn="第十四届", season="2023 下半年", theme="巅峰挑战",
         url="http://www.icmc100.com/newsinfo/6380953.html", pub="2023-09",
         doc="", accent="#7a5ca8"),
    dict(tag="15", cn="第十五届", season="2024 上半年", theme="宇航基地历险记",
         url="http://www.icmc100.com/newsinfo/6877243.html", pub="2024-03-01",
         doc="http://cs.icmc100.com/maker15.zip", accent="#e8734a"),
    dict(tag="16", cn="第十六届", season="2024 下半年", theme="泰坦星球大冒险",
         url="http://www.icmc100.com/newsinfo/7565856.html", pub="2024-09-10",
         doc="http://cs.icmc100.com/maker16.zip", accent="#7c5cb0",
         note="官网此页正文小节标题误写为「2024第十五届比赛项目」，实为第十六届规则（发布日期可证）"),
    dict(tag="17", cn="第十七届", season="2025 上半年", theme="星际农场奇遇记",
         url="http://www.icmc100.com/newsinfo/8080171.html", pub="2025-02",
         doc="http://cs.icmc100.com/maker17.zip", accent="#3a9d6e"),
    dict(tag="18", cn="第十八届", season="2025 下半年", theme="超级港口大挑战",
         url="http://www.icmc100.com/newsinfo/8740757.html", pub="2025-09",
         doc="http://cs.icmc100.com/maker18.zip", accent="#2f7fbf"),
    dict(tag="19", cn="第十九届", season="2026 上半年", theme="行星能源大时代",
         url="http://www.icmc100.com/newsinfo/8987054.html", pub="2026-03-10",
         doc="http://cs.icmc100.com/maker19.zip", accent="#c0405e"),
]

LABELS = ['任务背景','参赛对象','材料范围','场地器材','赛场准备','比赛过程','比赛分值',
          '评分总则','评分细则','项目分组','比赛形式','指导单位','主办单位','任务说明',
          '奖项设置','奖项设立','报名方式','比赛要求']
SUBITEMS = ['年龄','形式','赛时','比赛形式']
SEC_HEADS = ['机器人赛项总则','赛事总则','编程赛总则','编程组评选总则','奖项设立','资料下载']
SKIP_LINES = {'GENERAL RULES OF EVENTS','Data download','GENERAL RULES OF EVENTS '}
# 第3-7届标题带 ICMC- 前缀或中文序号
TASK_RE = re.compile(r'^[一二三四五六\d]*[、.．]?\s*(?:ICMC-)?(?:JR|机械|动力|感控|智能)组\s*\d+-\d+')
GRP_RE  = re.compile(r'^(Scratch|Python|C\+\+)\s*(幼儿组|儿童组|少儿组|少年组)[：:]?$')
AWARD_RE = re.compile(r'^(特等奖|一等奖|二等奖|三等奖|优秀教练|精英教练)[：:]')
PROG_RE = re.compile(r'^(?:[一二三四五六\d]*[、.．]?\s*)?(?:ICMC-)?编程组\s*\d+-\d+')

# ===== 第3-14届（早期届）专用 =====
EARLY_TAGS = {'3','4','5','6','7','9','10','11','12','13','14'}
KICK_RE2  = re.compile(r'^\d{4}(?:ICMC)?第[一二三四五六七八九十]+届比赛项目$')
THEME_RE  = re.compile(r'^\d{4}ICMC.{0,10}主题[：:]')
ORG_RE    = re.compile(r'^(?:指导单位|主办单位|承办单位|协办单位|比赛地点|比赛时间|参赛对象|比赛形式|报名时间)[：:]?.*$')
DECO_RE   = re.compile(r'^(?:[“”"]+|\d|\d{4})$')   # 装饰：引号 / 单个序号 / 年份

def early_tail_cut(lines):
    """行级截断：从「赛场设置」或「往届赛事回顾」起全部丢弃
    （连带清掉 往届图集 / 赛事&报名详情 / 日程费用联系人 / 组委落款）
    截断后再从尾部剥掉残留的装饰行（孤立序号等）"""
    for k, l in enumerate(lines):
        if l in ('赛场设置', '往届赛事回顾'):
            lines = lines[:k]
            break
    while lines and (DECO_RE.match(lines[-1]) or lines[-1] in (
            '奖项设立', '【选手】', '【教练】')):
        lines.pop()
    return lines

def early_preamble(lines):
    """前言区行级清洗（对齐 15-19 届标准：海报 + 简介 + kicker + 主题图 + 故事）：
    - 丢：指导/主办/承办/比赛地点/比赛时间/参赛对象/比赛形式 及其内容行
    - 丢：装饰引号、单个序号、孤立年份
    - 丢：组织类图片（非首图、且不在主题标题后的图）
    - 丢：前言区 gif（与 15-19 届 pre_filter 行为一致）
    - 留：首图海报、届次简介、KICK/主题标题、主题海报、故事背景"""
    first = len(lines)
    for i, l in enumerate(lines):
        if TASK_RE.match(l) or PROG_RE.match(l) or l in SEC_HEADS:
            first = i
            break
    out, org, seen_img, theme_seen = [], False, 0, False
    for i, l in enumerate(lines):
        if i >= first:
            out.append(l)
            continue
        if l.startswith('@@IMG|'):
            if l.endswith('.gif@@'):
                continue
            seen_img += 1
            if seen_img == 1 or theme_seen:
                out.append(l)
            continue
        if KICK_RE2.match(l) or THEME_RE.match(l):
            org = False
            theme_seen = True
            out.append(l)
            continue
        if ORG_RE.match(l):
            org = True
            continue
        if org or DECO_RE.match(l):
            continue
        out.append(l)
    return out

def to_lines(frag):
    frag = frag.replace('\\r\\n','\n').replace('\\n','\n').replace('\\"','"').replace('\\/','/')
    frag = re.sub(r'<script[\s\S]*?</script>','',frag)
    frag = re.sub(r'<style[\s\S]*?</style>','',frag)
    frag = re.sub(r'<!--[\s\S]*?-->','',frag)
    # 图片占位
    frag = re.sub(r'<img[^>]*?src="([^"]+)"[^>]*>', lambda m: f'\n@@IMG|{m.group(1)}@@\n', frag)
    frag = re.sub(r'<br\s*/?>','\n',frag)
    frag = re.sub(r'</(p|section|div|li|h[1-6]|tr|td|table)>','\n',frag)
    frag = re.sub(r'<[^>]+>','',frag)
    frag = H.unescape(frag).replace('\xa0',' ')
    out=[]
    for l in frag.split('\n'):
        l=re.sub(r'[ \t]+',' ',l).strip()
        if not l or l=='▼': continue
        if l in SKIP_LINES or l.startswith('GENERAL RULES'): continue
        # 合并行内的 “。2、” 拆开
        l = re.sub(r'(?<=[。；;])\s*(?=\d+、)', '\n', l)
        for part in l.split('\n'):
            part=part.strip()
            if part: out.append(part)
    return out

def strip_num(t):
    return re.sub(r'^[一二三四五六\d]*[、.．]?\s*(?:ICMC-)?', '', t)

def clean_head(t):
    """卡片标题规范化：去掉序号与 ICMC- 前缀，合并分行的任务名"""
    return re.sub(r'^[一二三四五六\d]*[、.．]?\s*(?:ICMC-)?', '', t)

def classify(unit, ctx, imgs):
    """返回渲染用的 html 片段或 None"""
    if unit.startswith('@@IMG|'):
        src = unit[6:-2]
        return ('IMG', src, '')
    t = unit
    # 跳过标题下的英文副标 / 版权声明等
    if t.startswith('（') and t.endswith('）') and ('示意' in t or '参考图' in t and False):
        return None
    # 卡片边界
    if TASK_RE.match(t) or PROG_RE.match(t):
        # 「ICMC-JR组3-4周岁：」冒号结尾 => 任务名在下一行，由 build() 合并
        return ('HEAD', 'task', clean_head(t))
    if t in SEC_HEADS:
        return ('HEAD', 'sec', t)
    # 小标签（含内容拆分）
    m = re.match(r'^(' + '|'.join(LABELS) + r')[：:]\s*(.*)$', t, re.S)
    if m:
        name, rest = m.group(1), m.group(2).strip()
        if name in ('指导单位','主办单位'):
            return ('ORG', name, rest)
        if name in SUBITEMS and rest:
            return ('SUB', name, rest)
        if rest:
            return ('LBL', name, rest)
        return ('LBL', name, '')
    # 届次项目标题
    if re.match(r'^\d{4}第[一二三四五六七八九十]+届比赛项目$', t) or KICK_RE2.match(t):
        return ('KICK', t, '')
    # 无冒号的独立小标签
    if t in LABELS:
        return ('LBL', t, '')
    # 子项 年龄/形式/赛时（无冒号内容形式）
    m2 = re.match(r'^(' + '|'.join(SUBITEMS) + r')[：:]\s*(.+)$', t)
    if m2:
        return ('SUB', m2.group(1), m2.group(2).strip())
    # 编程组分组名
    if GRP_RE.match(t):
        return ('GRP', t.rstrip('：:'), '')
    # 【选手】【教练】
    if re.match(r'^【.+(选手|教练|奖项)】$', t):
        return ('GRP', t.strip('【】'), '')
    if AWARD_RE.match(t):
        return ('SUB', '奖', t)
    # 编号规则
    if re.match(r'^\d+、', t):
        return ('OLI', strip_num(t), '')
    # 说明/图题
    if t.startswith('《') and t.endswith('》'):
        return ('CAP', t, '')
    if re.match(r'^【.+】$', t):
        return ('NOTE', t, '')
    if t.startswith('（') and t.endswith('）'):
        return ('HINT', t, '')
    if t.endswith('：') and len(t) <= 12:
        return ('LBL', t.rstrip('：:'), '')
    return ('P', t, '')

def render(lines):
    units=[]
    for l in lines:
        r = classify(l, None, None)
        if r is None: continue
        units.append(r)
    # 合并：ol / ul / grp
    out=[]; i=0
    while i < len(units):
        u=units[i]
        if u[0]=='OLI':
            items=[]; j=i
            while j<len(units) and units[j][0]=='OLI':
                items.append(units[j][1]); j+=1
            out.append('<ol>' + ''.join(f'<li>{x}</li>' for x in items) + '</ol>')
            i=j; continue
        if u[0]=='SUB':
            items=[]; j=i
            while j<len(units) and units[j][0]=='SUB':
                items.append(units[j][2] if units[j][1]=='奖' else f'{units[j][1]}：{units[j][2]}')
                j+=1
            out.append('<ul class="sub">' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>')
            i=j; continue
        if u[0]=='GRP':
            name=u[1]
            # 收集紧随的 sub 列表
            body=''; j=i+1
            subs=[]
            while j<len(units) and units[j][0]=='SUB':
                subs.append(units[j][2] if units[j][1]=='奖' else f'{units[j][1]}：{units[j][2]}')
                j+=1
            if subs:
                body='<ul class="sub">'+''.join(f'<li>{x}</li>' for x in subs)+'</ul>'
            out.append(f'<div class="pg"><div class="pgname">{name}</div>{body}</div>')
            i=j; continue
        k=u[0]
        if k=='HEAD':
            out.append(('HEAD', u[1], u[2]))
        elif k=='LBL':
            if u[2]:
                out.append(f'<h5 class="lbl">{u[1]}</h5><p>{u[2]}</p>')
            else:
                out.append(f'<h5 class="lbl">{u[1]}</h5>')
        elif k=='OLI':
            pass
        elif k=='P':
            out.append(f'<p>{u[1]}</p>')
        elif k=='CAP':
            out.append(f'<p class="cap">{u[1]}</p>')
        elif k=='NOTE':
            out.append(f'<p class="note-line">{u[1]}</p>')
        elif k=='HINT':
            out.append(f'<p class="hint">{u[1]}</p>')
        elif k=='IMG':
            out.append(f'<figure><img src="{u[1]}" /></figure>')
        elif k=='ORG':
            body = u[2]
            nxt = units[i+1] if i+1 < len(units) else None
            if nxt and nxt[0]=='P' and len(nxt[1]) < 26 and not re.match(r'^\d', nxt[1]):
                body += '<br>' + nxt[1]
                i += 1
            out.append(f'<p class="org"><b>{u[1]}：</b>{body}</p>')
        elif k=='KICK':
            out.append(f'<h2 class="proj">{u[1]}</h2>')
        i+=1
    return out

def pre_filter(pre):
    """开头区精简：去重复的指导/主办单位、参赛对象、比赛形式，以及共用的旋转机器人 GIF"""
    pre = re.sub(r'<p class="org">.*?</p>', '', pre, flags=re.S)
    pre = re.sub(r'<h5 class="lbl">(?:参赛对象|比赛形式)</h5>\s*(?:<p>[^<]*</p>)?', '', pre)
    pre = re.sub(r'<figure><img src="[^"]+\.gif"\s*/></figure>', '', pre)
    return pre

def group_of(title, kind):
    """按卡片标题判定组别标签"""
    t = title
    if kind == 'task':
        if t.startswith('编程组'): return 'prog'
        for key, g in (('JR组','jr'), ('机械组','mech'), ('动力组','power'),
                       ('感控组','ctrl'), ('智能组','smart')):
            if key in t: return g
        return 'all'
    # seccard：总则/奖项跟随组别
    if '编程赛总则' in t: return 'prog'
    if '赛项总则' in t: return 'robot'
    return 'all'   # 赛事总则/奖项设立/资料下载

def build(tag, raw=None):
    """raw: 指定源片段文件名；默认 frag_{tag}.html（15-19届为抓取原件，3-14届为本地化产物）"""
    frag = open(raw or f'frag_{tag}.html', encoding='utf-8').read()
    if tag in EARLY_TAGS:
        # 早期届（3-14）：行级截断尾部 + 前言清洗（15-19 届保持原「比赛时间删块 + pre_filter」逻辑）
        lines = early_tail_cut(to_lines(frag))
        lines = early_preamble(lines)
        # 过滤全篇残留的小节编号装饰行（官网原页的 1/2/3 小节序号）
        lines = [l for l in lines if not re.match(r'^\d{1,2}$', l)]
        units = render(lines)
    else:
        # 删除比赛时间块
        i = frag.find('比赛时间')
        if i > 0:
            start = frag.rfind('<p', 0, i)
            j = frag.find('参赛对象', i)
            if j > 0:
                end = frag.rfind('<p', 0, j)
                frag = frag[:start] + frag[end:]
        lines = to_lines(frag)
        units = render(lines)
    # 预处理：第3-6届「XXX组N-M周岁：」+ 下一行任务名 => 合并为一行标题
    merged = []
    i = 0
    while i < len(units):
        u = units[i]
        if (isinstance(u, tuple) and u[0] == 'HEAD' and u[1] == 'task'
                and u[2].endswith('：')
                and i + 1 < len(units) and isinstance(units[i+1], tuple)
                and units[i+1][0] == 'P' and '：' not in units[i+1][1]
                and len(units[i+1][1]) < 30):
            merged.append(('HEAD', 'task', u[2] + units[i+1][1]))
            i += 2
        else:
            merged.append(u)
            i += 1
    units = merged
    # 组装卡片
    html_parts=[]; preamble=[]; cur=None; seq=0; chips=[]
    for u in units:
        if isinstance(u, tuple) and u[0]=='HEAD':
            seq+=1
            if cur: html_parts.append(cur)
            cls = 'taskcard' if u[1]=='task' else 'seccard'
            hid = f't{tag}-{seq}'
            htag = 'h3' if u[1]=='task' else 'h4'
            hcls = 'task' if u[1]=='task' else 'sec'
            if u[1]=='task': chips.append((hid, u[2]))
            grp = group_of(u[2], u[1])
            cur = (f'<div class="{cls}" data-group="{grp}">'
                   f'<{htag} class="{hcls}" id="{hid}">{u[2]}</{htag}>')
        else:
            if cur: cur += u
            else: preamble.append(u)
    if cur: html_parts.append(cur+'</div>')
    # 收尾：给每个未闭合的卡片补 </div>
    fixed=[]
    for p in html_parts:
        if not p.endswith('</div>'):
            p += '</div>'
        fixed.append(p)
    return pre_filter(''.join(preamble)), ''.join(fixed), chips

def main():
    allsec=[]
    for m in META:
        pre, body, chips = build(m['tag'])
        open(f'frag3_{m["tag"]}.html','w',encoding='utf-8').write(pre+body)
        chipnav=''.join(f'<a href="#{cid}">{txt}</a>' for cid,txt in chips)
        note=f'<p class="note">⚠️ {m["note"]}</p>' if m.get("note") else ""
        allsec.append(f'''
<section class="edition" id="e{m['tag']}" style="--accent:{m['accent']}">
  <header class="ed-head">
    <div class="ed-title"><span class="badge">{m['cn']}</span><h2>{m['theme']}</h2></div>
    <div class="ed-meta">
      <span><b>赛季</b>{m['season']}</span>
      <span><b>发布</b>{m['pub']}</span>
      <span><b>规则原文</b><a href="{m['url']}" target="_blank" rel="noopener">{m['url']} ↗</a></span>
      {f'<span><b>技术文档</b><a href="{m["doc"]}" target="_blank" rel="noopener">maker{m["tag"]}.zip ↗</a></span>' if m.get('doc') else ''}
    </div>
    <div class="chips">{chipnav}</div>
    {note}
  </header>
  <div class="article">{pre}{body}</div>
</section>''')
        print(m['tag'], 'cards:', len(chips))
    tabs=''.join(f'<a href="#e{m["tag"]}" class="tab-e" data-tag="{m["tag"]}" style="--accent:{m["accent"]}"><b>{m["tag"]}</b><small>{m["season"]}</small></a>' for m in META)
    groups=[('all','全部'),('jr','JR组'),('mech','机械组'),('power','动力组'),
            ('ctrl','感控组'),('smart','智能组'),('prog','编程组')]
    gbtns=''.join(f'<button class="gbtn" data-g="{g}">{n}</button>' for g,n in groups)
    html=f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ICMC 第3–19届任务规则 · 带图版</title>
<style>
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  body {{ font-family:-apple-system,"PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
         background:#f6f6f4; color:#26241f; line-height:1.75; }}
  .top {{ max-width:880px; margin:0 auto; padding:48px 20px 8px; }}
  .top h1 {{ font-size:26px; letter-spacing:1px; }}
  .top p {{ color:#6b675c; font-size:14px; margin-top:10px; }}
  nav.tabs {{ position:sticky; top:0; z-index:50; display:flex; gap:8px; flex-wrap:wrap;
              background:rgba(246,246,244,.94); backdrop-filter:blur(8px);
              padding:12px 20px; border-bottom:1px solid #e4e1d9; }}
  nav.tabs a {{ flex:1 1 48px; text-align:center; text-decoration:none; color:#3a372f;
                background:#fff; border:1px solid #e4e1d9; border-top:3px solid var(--accent);
                border-radius:8px; padding:8px 6px; font-size:15px; font-weight:600; }}
  nav.tabs a b {{ font-size:17px; }}
  nav.tabs a small {{ display:block; font-weight:400; font-size:10.5px; color:#8a857a; margin-top:2px; }}
  @media (max-width:900px) {{ nav.tabs a small {{ display:none; }} }}
  .filterbar {{ position:sticky; top:76px; z-index:49; max-width:880px; margin:0 auto;
                display:flex; gap:8px; flex-wrap:wrap; align-items:center;
                padding:10px 20px; background:rgba(246,246,244,.94); backdrop-filter:blur(8px);
                border-bottom:1px solid #e4e1d9; }}
  .filterbar .flabel {{ font-size:13px; color:#8a857a; font-weight:600; margin-right:2px; }}
  .gbtn {{ font-family:inherit; font-size:13px; font-weight:600; color:#3a372f;
           background:#fff; border:1px solid #e4e1d9; border-radius:18px;
           padding:5px 14px; cursor:pointer; transition:all .15s; }}
  .gbtn:hover {{ border-color:#b8b2a2; }}
  .gbtn.on {{ background:#26241f; color:#fff; border-color:#26241f; }}
  section.edition {{ max-width:880px; margin:28px auto 72px; padding:0 20px; scroll-margin-top:130px; }}
  .ed-head {{ background:#fff; border:1px solid #e4e1d9; border-left:5px solid var(--accent);
              border-radius:12px; padding:18px 22px; margin-bottom:22px; }}
  .ed-head .ed-meta, .ed-head .chips {{ display:none; }}
  body.filter-on .ed-head .ed-meta, body.filter-on .ed-head .chips {{ display:flex; }}
  .ed-title {{ display:flex; align-items:center; gap:12px; flex-wrap:wrap; }}
  .badge {{ background:var(--accent); color:#fff; font-size:13px; font-weight:700;
            padding:3px 12px; border-radius:20px; white-space:nowrap; }}
  .ed-title h2 {{ font-size:22px; }}
  .ed-meta {{ display:flex; flex-wrap:wrap; gap:6px 22px; margin-top:10px; font-size:13px; color:#55524a; }}
  .ed-meta b {{ color:#8a857a; font-weight:600; margin-right:6px; }}
  .ed-meta a {{ color:#2f7fbf; word-break:break-all; }}
  .chips {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:14px; }}
  .chips a {{ font-size:12px; color:#3a372f; text-decoration:none; background:#f4f2ec;
              border:1px solid #e4e1d9; border-radius:16px; padding:3px 12px; }}
  .chips a:hover {{ background:var(--accent); color:#fff; border-color:var(--accent); }}
  .note {{ margin-top:10px; font-size:13px; color:#a15c00; background:#fff7e8;
           border:1px solid #f0dcb4; border-radius:8px; padding:8px 12px; }}
  .article {{ background:#fff; border:1px solid #e4e1d9; border-radius:12px; padding:30px 32px; }}
  .article p {{ font-size:15px; margin:6px 0; }}
  .article img, .ged img {{ max-width:100%; height:auto; display:block; margin:14px auto;
                  border-radius:8px; border:1px solid #eee; }}
  .article figure, .ged figure {{ margin:12px 0; max-width:100%; }}
  .article figure img, .ged figure img {{ box-sizing:border-box; }}
  .article a {{ color:#2f7fbf; }}
  .taskcard {{ border:1px solid #e9e6dd; border-left:4px solid var(--accent);
               border-radius:10px; background:#fcfbf8; padding:18px 20px; margin:26px 0; }}
  .taskcard h3.task {{ font-size:17px; color:var(--accent); scroll-margin-top:110px;
                       padding-bottom:8px; border-bottom:1px dashed #e0dcd0; margin-bottom:10px; }}
  .seccard {{ border:1px solid #e9e6dd; border-radius:10px; background:#f4f3ef;
              padding:16px 20px; margin:26px 0; }}
  .seccard h4.sec {{ font-size:16px; scroll-margin-top:110px;
                     padding-bottom:8px; border-bottom:1px dashed #d8d4c8; margin-bottom:10px; }}
  h5.lbl {{ display:inline-block; font-size:13px; font-weight:700; color:#fff;
            background:var(--accent, #8a857a); border-radius:8px; padding:3px 12px;
            margin:16px 0 4px; line-height:1.5; }}
  .seccard h5.lbl {{ background:#6b675c; }}
  ol {{ margin:8px 0 8px 22px; }}
  ol li {{ font-size:14.5px; margin:5px 0; padding-left:2px; }}
  ol li::marker {{ color:var(--accent); font-weight:700; }}
  .seccard ol li::marker {{ color:#6b675c; }}
  ul.sub {{ list-style:none; margin:6px 0 6px 4px; }}
  ul.sub li {{ font-size:14.5px; padding-left:16px; position:relative; margin:3px 0; }}
  ul.sub li::before {{ content:"·"; position:absolute; left:4px; color:var(--accent); font-weight:700; }}
  .seccard ul.sub li::before {{ color:#6b675c; }}
  .pg {{ border:1px dashed #e2ded2; border-radius:8px; background:#fff; padding:8px 14px; margin:10px 0; }}
  .pg .pgname {{ font-size:14px; font-weight:700; color:#3a372f; }}
  .pg ul.sub {{ margin:4px 0 2px; }}
  p.cap {{ text-align:center; font-size:13px; color:#8a857a; margin:0 0 12px; }}
  h2.proj {{ font-size:19px; margin:26px 0 6px; padding-left:12px; border-left:5px solid var(--accent); }}
  p.org {{ font-size:14px; color:#55524a; margin:2px 0; }}
  p.org b {{ color:#26241f; }}
  p.hint {{ font-size:13px; color:#8a857a; }}
  p.note-line {{ display:inline-block; font-size:13px; color:#a15c00; background:#fff7e8;
                 border:1px solid #f0dcb4; border-radius:6px; padding:5px 12px; margin:10px 0; }}
  /* ===== 组别筛选 ===== */
  body.filter-on .edition .article > *:not(.taskcard):not(.seccard) {{ display:none; }}
  body.filter-on .edition {{ display:none; }}
  .gresults {{ max-width:880px; margin:22px auto 60px; padding:0 20px; display:none; }}
  body.filter-on .gresults {{ display:block; }}
  .ged {{ margin:0 auto 34px; scroll-margin-top:150px; }}
  .ged .ged-head {{ display:flex; align-items:center; gap:12px; flex-wrap:wrap;
                    padding:0 4px 10px; border-bottom:2px solid var(--accent); margin-bottom:16px; }}
  .ged .ged-head h2 {{ font-size:20px; }}
  .ged .ged-head .ged-season {{ font-size:13px; color:#8a857a; }}
  .ged .ged-head a.ged-src {{ font-size:12.5px; color:#2f7fbf; text-decoration:none;
                              white-space:nowrap; margin-left:auto; }}
  .ged .taskcard, .ged .seccard {{ margin:18px 0; }}
  .ged-empty {{ text-align:center; color:#8a857a; padding:40px 0; }}
  body.filter-on footer, body.filter-on .totop {{ display:none; }}
  footer {{ max-width:880px; margin:0 auto 60px; padding:0 20px; font-size:13px; color:#8a857a; }}
  .totop {{ position:fixed; right:18px; bottom:18px; width:42px; height:42px; border-radius:50%;
            background:#26241f; color:#fff; text-align:center; line-height:42px; text-decoration:none;
            font-size:18px; opacity:.75; }}
  @media (max-width:640px) {{ .article {{ padding:18px 16px; }} .top h1 {{ font-size:21px; }}
    .taskcard,.seccard {{ padding:14px 14px; }}
    .filterbar {{ top:64px; padding:8px 12px; }} .gbtn {{ padding:4px 10px; font-size:12px; }} }}
</style>
</head>
<body>
<div class="top">
  <h1>ICMC 国际机器人创客大赛 · 第三届至第十九届任务规则</h1>
  <p>内容与图片取自 ICMC 官网各届赛项发布页（www.icmc100.com），聚焦规则本身：任务背景、场地器材、比赛过程与计分。赛程时间表与报名联系方式等无关信息已略去。整理日期：2026-09-11。</p>
</div>
<nav class="tabs">{tabs}</nav>
<div class="filterbar"><span class="flabel">按组别筛选</span>{gbtns}</div>
{''.join(allsec)}
<div class="gresults" id="gresults"></div>
<footer>
  <p>来源：ICMC 官网「最新动态」栏目，各届规则页链接见每届标题卡。图片已本地化（images/ 目录），任务动画为官网原 GIF。</p>
</footer>
<a class="totop" href="#">↑</a>
<script>
(function() {{
  var GROUPS = {{ jr:'JR组', mech:'机械组', power:'动力组', ctrl:'感控组',
                 smart:'智能组', prog:'编程组' }};
  var EDITIONS = __META_JS__;
  var bar = document.querySelector('.filterbar');
  var gres = document.getElementById('gresults');
  var btns = bar.querySelectorAll('.gbtn');

  function clearFilter() {{
    document.body.classList.remove('filter-on');
    gres.innerHTML = '';
    btns.forEach(function(b) {{ b.classList.remove('on'); }});
    if (location.hash.indexOf('#g-') === 0)
      history.replaceState(null, '', location.pathname + location.search);
  }}

  function applyFilter(g) {{
    document.body.classList.add('filter-on');
    gres.innerHTML = '';
    btns.forEach(function(b) {{ b.classList.toggle('on', b.dataset.g === g); }});
    // 机器人组同时附带「机器人赛项总则」；编程组附带「编程赛总则」
    var extra = (g === 'prog') ? ['prog'] : ['robot'];
    var selectors = [g].concat(extra).map(function(x) {{
      return '.article [data-group="' + x + '"]';
    }});
    var shown = 0;
    EDITIONS.forEach(function(m) {{
      var src = document.querySelector('.edition#e' + m.tag);
      if (!src) return;
      var cards = src.querySelectorAll(selectors.join(','));
      if (!cards.length) return;
      shown++;
      var box = document.createElement('section');
      box.className = 'ged';
      box.id = 'g-' + g + '-' + m.tag;
      box.style.setProperty('--accent', m.accent);
      var head = document.createElement('div');
      head.className = 'ged-head';
      head.innerHTML = '<span class="badge">' + m.cn + '</span>'
        + '<h2>' + m.theme + '</h2>'
        + '<span class="ged-season">' + m.season + '</span>'
        + '<a class="ged-src" href="' + m.url + '" target="_blank" rel="noopener">规则原文 ↗</a>';
      box.appendChild(head);
      cards.forEach(function(c) {{
        var clone = c.cloneNode(true);          // 克隆而非移动，原始内容保留
        clone.removeAttribute('id');
        clone.querySelectorAll('[id]').forEach(function(x) {{ x.removeAttribute('id'); }});
        box.appendChild(clone);
      }});
      gres.appendChild(box);
    }});
    if (!shown)
      gres.innerHTML = '<p class="ged-empty">该组别暂无内容</p>';
  }}

  btns.forEach(function(b) {{
    b.addEventListener('click', function() {{
      if (b.dataset.g === 'all') {{ clearFilter(); window.scrollTo({{top:0}}); return; }}
      applyFilter(b.dataset.g);
      window.scrollTo({{top:0}});
    }});
  }});

  // 届次 tab 跳转：筛选态 → 跳到结果区对应届分组；普通态 → 原届次区块
  document.querySelectorAll('nav.tabs a.tab-e').forEach(function(a) {{
    a.addEventListener('click', function(ev) {{
      var tag = a.dataset.tag;
      if (document.body.classList.contains('filter-on')) {{
        ev.preventDefault();
        var active = bar.querySelector('.gbtn.on');
        var g = active ? active.dataset.g : null;
        if (g && g !== 'all') {{
          var target = document.getElementById('g-' + g + '-' + tag);
          if (target) target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }}
      }}
      // 普通态走默认锚点 #e<tag>
    }});
  }});

  if (location.hash.indexOf('#g-') === 0) {{
    var g = location.hash.slice(3);
    if (GROUPS[g]) applyFilter(g);
  }}
}})();
</script>
</body>
</html>'''
    meta_js = json.dumps([dict(tag=m['tag'], cn=m['cn'], theme=m['theme'],
                               season=m['season'], url=m['url'], accent=m['accent'])
                          for m in META], ensure_ascii=False)
    html = html.replace('__META_JS__', meta_js)
    open('index.html','w',encoding='utf-8').write(html)
    print('index.html', len(html))

if __name__=='__main__':
    main()
