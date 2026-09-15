#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_frag20.py — 第20届 ICMC（轨道空间站大冒险）frag 源片段生成
输入: bodyjs/wx20_article.html   微信公众号文章存档（2026-09-15 发布）
输出: frag_20.html              与 frag_15..19 同构的源片段（供 build_v3.py 消费）
      images/20/*.jpg|gif|png   本地化图片（自 tmp_* 重编号为 00..33）

裁剪:
  - 删「ICMC介绍视频」→「参赛对象」前（含视频占位、比赛时间表）
  - 截断「往届赛事回顾」及其后全部（照片/报名详情/咨询/logo）
  - 删装饰数字（01..05 徽章）
保留策略（与 15-19 管线一致）:
  - 指导/主办单位、参赛对象、比赛形式 保留，交由 build_v3.pre_filter 清洗
  - 前言 GIF（idx4）保留，交由 pre_filter 清洗
"""
import re, os, shutil, html as H

WX = 'bodyjs/wx20_article.html'

# ---------- 1. 正文区 ----------
raw = open(WX, encoding='utf-8', errors='replace').read()
S = raw.find('id="js_content"')
E = raw.find('id="js_temp_bottom_area"')
assert S > 0 and E > S, (S, E)
content = raw[raw.find('>', S) + 1:E]
print('正文区长度:', len(content))

# ---------- 2. 图片序列（去重保序） ----------
IMG_RE = r'<(?:img|iframe)\b[^>]*?data-src="([^"]+)"[^>]*?>'
img_seq = []
seen = set()
for m in re.finditer(IMG_RE, content):
    url = m.group(1)
    if url in seen:
        continue
    seen.add(url)
    wm = re.search(r'data-w="(\d+)"', m.group(0))
    img_seq.append((url, int(wm.group(1)) if wm else 0))
print('去重图片数:', len(img_seq))
assert len(img_seq) == 76, '图片序列数不符'

# ---------- 3. 保留映射 ----------
KEEP = {0:'00.jpg', 4:'01.gif', 5:'02.jpg', 7:'03.jpg', 8:'04.gif', 9:'05.jpg', 10:'06.png',
        11:'07.jpg', 12:'08.png', 14:'09.jpg', 15:'10.gif', 16:'11.jpg', 17:'12.png',
        18:'13.png', 19:'14.png', 21:'15.jpg', 22:'16.gif', 23:'17.jpg', 24:'18.png',
        25:'19.png', 27:'20.jpg', 28:'21.gif', 29:'22.jpg', 30:'23.png', 31:'24.png',
        33:'25.jpg', 34:'26.gif', 35:'27.jpg', 36:'28.jpg', 37:'29.png', 38:'30.jpg',
        39:'31.png', 41:'32.gif', 43:'33.jpg'}
assert len(KEEP) == 34
for idx in (1, 3, 42, 44):
    assert img_seq[idx][1] == 600, f'idx{idx} 应为600宽K机器人GIF'
assert 'readtemplate' in img_seq[2][0], 'idx2 应为视频'
for idx in (6, 13, 20, 26, 32, 40):
    assert img_seq[idx][1] == 46, f'idx{idx} 应为46宽装饰球'
assert img_seq[43][1] == 1041 and img_seq[0][1] == 1080
print('图片索引特征校验通过')

url2idx = {}
for k, (u, w) in enumerate(img_seq):
    url2idx.setdefault(u, k)

# ---------- 4. 行提取 ----------
def strip_to_lines(seg):
    seg = re.sub(r'<script[\s\S]*?</script>', '', seg)
    seg = re.sub(r'<style[\s\S]*?</style>', '', seg)
    seg = re.sub(r'<!--[\s\S]*?-->', '', seg)
    seg = re.sub(r'<br\s*/?>', '\n', seg)
    seg = re.sub(r'</(p|section|div|li|h[1-6]|tr|td|table)>', '\n', seg)
    seg = re.sub(r'<[^>]+>', '', seg)
    seg = H.unescape(seg).replace('\xa0', ' ')
    out = []
    for l in seg.split('\n'):
        l = re.sub(r'[ \t]+', ' ', l).strip()
        if not l or l == '▼':
            continue
        out.append(l)
    return out

flows = []
pos = 0
for m in re.finditer(IMG_RE, content):
    for line in strip_to_lines(content[pos:m.start()]):
        flows.append(('t', line))
    flows.append(('i', url2idx[m.group(1)]))
    pos = m.end()
for line in strip_to_lines(content[pos:]):
    flows.append(('t', line))
print('flows 条目数:', len(flows), ' 图片出现:', sum(1 for f in flows if f[0] == 'i'))

# ---------- 5. 裁剪 ----------
def find_text(needle, start=0):
    for k in range(start, len(flows)):
        f = flows[k]
        if f[0] == 't' and f[1] == needle:
            return k
    return -1

def find_contains(sub, start=0):
    for k in range(start, len(flows)):
        f = flows[k]
        if f[0] == 't' and sub in f[1]:
            return k
    return -1

# 5a. 删「ICMC介绍视频」→「参赛对象」前
a = find_text('ICMC介绍视频')
b = find_text('参赛对象', a)
assert a > 0 and b > a, (a, b)
print(f'裁剪5a: 删 {a}..{b-1}（{b-a} 条）')
del flows[a:b]

# 5c. 截断「往届赛事回顾」
wz = find_text('往届赛事回顾')
assert wz > 0
print(f'裁剪5c: 自 {wz} 截断（删 {len(flows)-wz} 条）')
del flows[wz:]

# 5d. 删装饰数字
deco = [f[1] for f in flows if f[0] == 't' and re.fullmatch(r'\d{1,2}', f[1])]
flows = [f for f in flows if not (f[0] == 't' and re.fullmatch(r'\d{1,2}', f[1]))]
print(f'裁剪5d: 删装饰数字 {len(deco)} 条: {deco}')

# 5e. 归一化（对齐 15-19 届文字格式）
def norm_flow(f):
    if f[0] != 't':
        return [f]
    t = f[1]
    # 编程组标题：「编程类 5-14周岁 超级程序员」→「编程组5-14周岁：超级程序员」
    t = t.replace('编程类 5-14周岁 超级程序员', '编程组5-14周岁：超级程序员')
    # 组别标题去「组」后空格：「JR组 3-5岁：」→「JR组3-5岁：」
    t = re.sub(r'^((?:JR|机械|动力|感控|智能)组)\s+', r'\1', t)
    # 奖项块拆行：「选手奖项：特等奖：…」→「【选手】」「特等奖：…」
    if t.startswith('选手奖项：特等奖：'):
        return [('t', '【选手】'), ('t', '特等奖：' + t.split('特等奖：', 1)[1])]
    if t.startswith('教练奖项：优秀教练：'):
        return [('t', '【教练】'), ('t', '优秀教练：' + t.split('优秀教练：', 1)[1])]
    return [('t', t)]

new_flows = []
for f in flows:
    new_flows.extend(norm_flow(f))
flows = new_flows

# ---------- 6. 图片处理 ----------
out_flows, kept = [], []
for f in flows:
    if f[0] == 't':
        out_flows.append(f)
    elif f[1] in KEEP:
        out_flows.append(('i', KEEP[f[1]]))
        kept.append(f[1])
print('保留图片出现:', len(kept), ' 去重:', len(set(kept)))
assert sorted(set(kept)) == sorted(KEEP.keys())

# ---------- 7. 输出 frag_20.html ----------
out = ['<div>']
for f in out_flows:
    if f[0] == 't':
        out.append(f'<p>{H.escape(f[1], quote=False)}</p>')
    else:
        out.append(f'<p><img alt="" src="images/20/{f[1]}" /></p>')
out.append('</div>')
frag = '\n'.join(out)
open('frag_20.html', 'w', encoding='utf-8').write(frag)
print('frag_20.html:', len(frag), '字节,', len(out_flows), '条')

# 校验: frag 内不应再有「比赛时间」「往届」
assert '比赛时间' not in frag, 'frag 残留比赛时间'
assert '往届' not in frag, 'frag 残留往届'

# ---------- 8. 图片本地化 ----------
os.makedirs('images/20', exist_ok=True)
for idx, name in sorted(KEEP.items()):
    url = img_seq[idx][0]
    ext = 'gif' if '_gif/' in url else ('png' if '_png/' in url else 'jpg')
    src = f'images/20/tmp_{idx:02d}.{ext}'
    dst = f'images/20/{name}'
    assert os.path.exists(src), '缺文件: ' + src
    shutil.copy(src, dst)
print('图片复制完成 34 张')

# ---------- 9. 摘要 ----------
print('---- 关键区段打印 ----')
for k, f in enumerate(out_flows):
    s = f[1] if f[0] == 't' else f'[IMG {f[1]}]'
    keep = any(kw in s for kw in ('JR组', '机械组', '动力组', '感控组', '智能组', '编程组',
                                  '总则', '资料下载', '奖项设立', '版权', '赛季主题', '卡卡',
                                  '参赛对象', '比赛形式', '指导单位', '主办单位'))
    if keep:
        print(' ', k, s[:80])
