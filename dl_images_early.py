#!/usr/bin/env python3
"""下载第3-14届图片到 images/{n}/ 并生成 frag_{n}.html（src 本地化、统一引号）"""
import re, os, sys, subprocess

FILES = {
    '3': ('frag_raw_1.html', '25111'),
    '4': ('/tmp/rendered_2.js', '253311'),
    '5': ('/tmp/rendered_3.js', '826152'),
    '6': ('frag_raw_4.html', '1575287'),
    '7': ('frag_raw_5.html', '432441'),
    '9': ('frag_raw_6.html', '2373207'),
    '10': ('frag_raw_7.html', '1901340'),
    '11': ('frag_raw_8.html', '2457727'),
    '12': ('frag_raw_9.html', '4359913'),
    '13': ('frag_raw_10.html', '5599566'),
    '14': ('frag_raw_13.html', '6380953'),
}

def norm(s):
    # document.write 残留转义统一化
    s = s.replace('\\"', '"').replace("\\/", '/')
    s = s.replace('\\r\\n', '\n').replace('\\n', '\n')
    return s

UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def dl(url, out):
    if url.startswith('//'): url = 'https:' + url
    r = subprocess.run(['curl', '-s', '-o', out, '--max-time', '40', '-x', 'http://127.0.0.1:6152',
                        '-A', UA, '-e', 'http://www.icmc100.com/', url, '-w', '%{http_code}'],
                       capture_output=True, text=True)
    return r.stdout.strip()

ok = fail = 0
for n, (path, pid) in sorted(FILES.items(), key=lambda x: int(x[0])):
    s = norm(open(path, encoding='utf-8', errors='replace').read())
    os.makedirs(f'images/{n}', exist_ok=True)
    seen = {}
    def repl(m):
        global ok, fail
        tag, src = m.group(0), m.group(1)
        # 跳过 spacer
        if 'width="1"' in tag or '15653837.gif' in src:
            return ''
        key = src
        if key in seen:
            local = seen[key]
        else:
            ext = os.path.splitext(src.split('?')[0])[1].lower() or '.jpg'
            if ext not in ('.jpg', '.jpeg', '.png', '.gif', '.webp'): ext = '.jpg'
            idx = len(seen) + 1
            local = f'images/{n}/{idx:02d}{ext}'
            code = dl(src, local)
            if code == '200':
                ok += 1
            else:
                fail += 1
                print(f'  FAIL {n} #{idx}: {code} {src[:80]}')
            seen[key] = local
        return f'<img src="{local}" />'
    s2 = re.sub(r'<img[^>]*?src="([^"]+)"[^>]*>', repl, s)
    open(f'frag_{n}.html', 'w', encoding='utf-8').write(s2)
    print(f'第{n}届: {len(seen)} 张图 -> frag_{n}.html ({len(s2)})')
print(f'DONE ok={ok} fail={fail}')
