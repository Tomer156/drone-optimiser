"""Harvest the remaining reachable motors. Tries several candidate URLs per motor
and keeps the first that serves real product images. No explicit UA (several
vendors' WAFs reject one); collects after every scroll (lazy-loaders unload).
"""
import os, sys, re, urllib.request, urllib.parse
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
OUT = os.path.dirname(os.path.abspath(__file__))
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

TARGETS = {
    'iflight_xing2_2306': [
        'https://shop.iflight.com/XING2-2306-1755KV-2555KV-FPV-Motor-Pro1670',
        'https://shop.iflight.com/index.php?route=product/search&search=XING2%202306',
    ],
    'flywoo_nin_23065': [
        'https://flywoo.net/products/nin-2306-5-fpv-motor',
        'https://flywoo.net/search?q=NIN+2306.5',
    ],
    'emax_ecoii_2807': [
        'https://emaxmodel.com/products/emax-eco-ii-series-2807-3-6s-1300kv-1500kv-1700kv-brushless-motor-for-rc-drone-fpv-racing',
        'https://emaxmodel.com/search?q=ECO+II+2807',
    ],
    'emax_pro_2810': [
        'https://emaxmodel.com/products/emax-pro-series-2810-brushless-motor-950kv-1150kv',
        'https://emaxmodel.com/search?q=Pro+2810',
    ],
    'xnova_3220sk': [
        'https://rotorvillage.ca/xnova-3220-700kv-cinelifter-sk-series-1pc/',
        'https://rotorvillage.ca/?s=xnova+3220',
    ],
    'rcinpower_gts3215': [
        'https://www.unmannedtechshop.co.uk/products/rcinpower-gts-3215-brushless-fpv-drone-motor',
        'https://www.unmannedtechshop.co.uk/?s=GTS+3215',
    ],
}

COLLECT = """() => [...document.images]
  .map(e => ({u: e.currentSrc || e.src || '', w: e.naturalWidth, h: e.naturalHeight}))
  .filter(d => d.u && !d.u.startsWith('data:') && !/logo|icon|avatar|payment|flag|badge|sprite/i.test(d.u))"""

RESIZE = re.compile(r'_\d{3,4}x\d{0,4}(?=\.(?:jpg|jpeg|png|webp))'
                    r'|-\d{3,4}x\d{3,4}(?=\.(?:jpg|jpeg|png|webp)$)', re.I)


def grab(page, url):
    r = page.goto(url, timeout=60000, wait_until='domcontentloaded')
    page.wait_for_timeout(3000)
    found = list(page.evaluate(COLLECT))
    for _ in range(10):
        page.mouse.wheel(0, 5000)
        page.wait_for_timeout(650)
        found += page.evaluate(COLLECT)
    seen, keep = set(), []
    for d in sorted(found, key=lambda d: -(d['w'] * d['h'])):
        u = RESIZE.sub('', d['u'].split('?')[0])
        if u in seen or d['h'] < 600:
            continue
        seen.add(u)
        keep.append(u)
    return r.status, keep


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_context(viewport={'width': 1400, 'height': 1100}).new_page()
    for label, urls in TARGETS.items():
        got = []
        for url in urls:
            try:
                status, keep = grab(page, url)
                print(f'{label}: {url[:70]} -> http={status}, {len(keep)} big imgs')
                if keep:
                    got = keep
                    break
            except Exception as e:
                print(f'{label}: {url[:70]} -> FAIL {type(e).__name__} {str(e)[:60]}')
        n = 0
        for i, u in enumerate(got[:6]):
            ext = os.path.splitext(u)[1] or '.jpg'
            fn = os.path.join(OUT, f'{label}_{i}{ext}')
            if os.path.exists(fn):
                n += 1
                continue
            try:
                req = urllib.request.Request(u if u.startswith('http') else 'https:' + u,
                                             headers={'User-Agent': UA})
                open(fn, 'wb').write(urllib.request.urlopen(req, timeout=45).read())
                n += 1
            except Exception as e:
                print(f'    dl fail {i}: {type(e).__name__}')
        print(f'    saved {n}')
    browser.close()
