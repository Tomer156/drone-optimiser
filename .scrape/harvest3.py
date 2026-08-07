import os, sys, re, urllib.request
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
OUT = os.path.dirname(os.path.abspath(__file__))
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

TARGETS = [
    ('geprc_em3215', 'https://geprc.com/product/geprc-em3215-900kv-750kv-motor/'),
    ('geprc_em3110', 'https://geprc.com/product/geprc-em3110-900kv-motor/'),
    ('geprc_speedx2_2809', 'https://geprc.com/product/geprc-speedx2-2809-1280kv-motor/'),
    ('geprc_speedx2_3214', 'https://geprc.com/product/geprc-speedx2-3214-860kv-motor/'),
    ('geprc_em2812', 'https://geprc.com/product/geprc-em2812-900kv-motor/'),
    ('geprc_speedx2_2806', 'https://geprc.com/product/geprc-speedx2-2806-5-1350kv-1760kv-motor/'),
]

COLLECT = """() => [...document.images]
  .map(e => e.currentSrc || e.src || '')
  .filter(u => u.indexOf('uploads') !== -1 && !/logo|icon|avatar/i.test(u))"""

RESIZE = re.compile(r'-\d{3,4}x\d{3,4}(?=\.(?:jpg|jpeg|png|webp)$)', re.I)

with sync_playwright() as p:
    browser = p.chromium.launch()
    # NOTE: setting an explicit user_agent trips GEPRC's WAF (serves an empty page).
    page = browser.new_context(viewport={'width': 1400, 'height': 1000}).new_page()
    for label, url in TARGETS:
        try:
            page.goto(url, timeout=60000, wait_until='domcontentloaded')
            page.wait_for_timeout(3000)
            # some lazy-loaders swap images back to placeholders once scrolled past,
            # so collect after every step rather than only at the end
            urls = list(page.evaluate(COLLECT))
            for _ in range(10):
                page.mouse.wheel(0, 5000)
                page.wait_for_timeout(700)
                urls += page.evaluate(COLLECT)
            urls = list(dict.fromkeys(RESIZE.sub('', u.split('?')[0]) for u in urls))
            got = 0
            for i, u in enumerate(urls):
                ext = os.path.splitext(u)[1] or '.jpg'
                fn = os.path.join(OUT, f'{label}_{i}{ext}')
                if os.path.exists(fn):
                    got += 1
                    continue
                try:
                    req = urllib.request.Request(u, headers={'User-Agent': UA, 'Referer': url})
                    open(fn, 'wb').write(urllib.request.urlopen(req, timeout=45).read())
                    got += 1
                except Exception as e:
                    print(f'   dl fail {i}: {type(e).__name__}')
            print(f'{label}: {len(urls)} urls, {got} files')
        except Exception as e:
            print(f'{label}: FAIL {type(e).__name__} {str(e)[:110]}')
    browser.close()
