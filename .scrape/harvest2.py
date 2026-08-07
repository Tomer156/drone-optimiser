"""Pass 2: networkidle-based harvest for JS-lazy sites, full-resolution originals."""
import os, sys, re, urllib.request
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
OUT = os.path.dirname(os.path.abspath(__file__))
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36'

TARGETS = [
    ('geprc_em3215', 'https://geprc.com/product/geprc-em3215-900kv-750kv-motor/'),
    ('geprc_em3110', 'https://geprc.com/product/geprc-em3110-900kv-motor/'),
    ('geprc_speedx2_2809', 'https://geprc.com/product/geprc-speedx2-2809-1280kv-motor/'),
    ('geprc_speedx2_3214', 'https://geprc.com/product/geprc-speedx2-3214-860kv-motor/'),
    ('geprc_em2812', 'https://geprc.com/product/geprc-em2812-900kv-motor/'),
]

JS = """()=>[...document.querySelectorAll('img')]
  .map(e=>({u:e.currentSrc||e.src, w:e.naturalWidth, h:e.naturalHeight}))
  .filter(d=>d.u && !d.u.startsWith('data:'))"""


def full_res(u):
    """Strip WordPress -WxH resize suffix to get the original upload."""
    return re.sub(r'-\d{3,4}x\d{3,4}(?=\.(jpg|jpeg|png|webp)$)', '', u, flags=re.I)


with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_context(user_agent=UA, viewport={'width': 1400, 'height': 1000}).new_page()
    for label, url in TARGETS:
        try:
            pg.goto(url, timeout=60000, wait_until='networkidle')
            for _ in range(10):
                pg.mouse.wheel(0, 5000); pg.wait_for_timeout(600)
            pg.wait_for_timeout(1500)
            imgs = pg.evaluate(JS)
            seen, n = set(), 0
            for d in imgs:
                if d['h'] < 600 or 'logo' in d['u'].lower():
                    continue
                u = full_res(d['u'])
                if u in seen:
                    continue
                seen.add(u)
                ext = os.path.splitext(u.split('?')[0])[1] or '.jpg'
                fn = os.path.join(OUT, f'{label}_{n}{ext}')
                n += 1
                if os.path.exists(fn):
                    continue
                try:
                    req = urllib.request.Request(u, headers={'User-Agent': UA, 'Referer': url})
                    open(fn, 'wb').write(urllib.request.urlopen(req, timeout=45).read())
                except Exception as e:
                    print(f'   dl fail {os.path.basename(fn)}: {type(e).__name__}')
            print(f'{label}: {n} images')
        except Exception as e:
            print(f'{label}: FAIL {type(e).__name__} {str(e)[:110]}')
    b.close()
