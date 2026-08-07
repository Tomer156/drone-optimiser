"""Harvest the AOS-RC 5in-freestyle recommended motors from vendor pages.

Uses the browser's own UA (an explicit one trips several WAFs) and collects
after every scroll step (lazy-loaders unload images once scrolled past).
GetFPV/BrotherHobby 403 headless Chromium, so prefer manufacturer or
drone-fpv-racer / fpvstorerc / unmannedtech mirrors.
"""
import os, sys, re, urllib.request
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
OUT = os.path.dirname(os.path.abspath(__file__))

TARGETS = [
    ('aos_supernova_2207', 'https://fpvstorerc.com/products/rcinpower-aos-supernova-2207-1980kv-brushless-fpv-drone-motor'),
    ('emax_ecoii_2004', 'https://emax-usa.com/products/eco-ii-2004-brushless-motor-choose-kv'),
    ('emax_ecoii_2207', 'https://emax-usa.com/products/eco-ii-2207-brushless-motor-1700kv-1900kv-2400kv'),
    ('flyfish_flash_2004', 'https://www.flyfish-rc.com/products/flash-2004-1800kv-2900kv-fpv-motor'),
    ('flyfish_flash_2207', 'https://www.flyfish-rc.com/products/flash-2207-motor-black'),
    ('rcinpower_2104t', 'https://newbeedrone.com/products/rcinpower-gts-v3-2104-1800kv-3000kv-m2-mount-motor'),
    ('rcinpower_smoox_2306plus', 'https://fpvstorerc.com/products/rcinpower-smoox-gts-v2-2306-plus-brushless-motor'),
    ('rcinpower_wasp_major', 'https://fpvstorerc.com/products/rcinpower-wasp-major-22-6-6-5-1860kv-2020kv-brushless-motor'),
    ('tmotor_pacer_p2207v3', 'https://www.drone-fpv-racer.com/en/pacer-p2207-v3-2-1750-kv-motor-by-t-motor-11433.html'),
    ('tmotor_veloce_v22075v2', 'https://www.drone-fpv-racer.com/en/t-motor-velox-v22075-v2-1750kv-7574.html'),
    ('tmotor_velox_v3_2207', 'https://fpvstorerc.com/products/tmotor-velox-v3-0-2207-brushless-motor'),
    ('tmotor_velox_v3_2207_ut', 'https://www.unmannedtechshop.co.uk/product/t-motor-velox-v3-2207-brushless-fpv-motor/'),
]

COLLECT = """() => [...document.images]
  .map(e => ({u: e.currentSrc || e.src || '', w: e.naturalWidth, h: e.naturalHeight}))
  .filter(d => d.u && !/logo|icon|avatar|payment|badge|flag/i.test(d.u))"""

RESIZE = re.compile(r'_\d{3,4}x\d{0,4}(?=\.(?:jpg|jpeg|png|webp))|-\d{3,4}x\d{3,4}(?=\.(?:jpg|jpeg|png|webp)$)', re.I)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_context(viewport={'width': 1400, 'height': 1100}).new_page()
    for label, url in TARGETS:
        try:
            r = page.goto(url, timeout=60000, wait_until='domcontentloaded')
            page.wait_for_timeout(3000)
            found = list(page.evaluate(COLLECT))
            for _ in range(10):
                page.mouse.wheel(0, 5000)
                page.wait_for_timeout(700)
                found += page.evaluate(COLLECT)
            big, seen = [], set()
            for d in found:
                u = RESIZE.sub('', d['u'].split('?')[0])
                if u in seen or (d['h'] and d['h'] < 700):
                    continue
                seen.add(u)
                big.append(u)
            got = 0
            for i, u in enumerate(big[:6]):
                ext = os.path.splitext(u)[1] or '.jpg'
                fn = os.path.join(OUT, f'{label}_{i}{ext}')
                if os.path.exists(fn):
                    got += 1
                    continue
                try:
                    req = urllib.request.Request(u if u.startswith('http') else 'https:' + u,
                                                 headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                                                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                                                          'Referer': url})
                    open(fn, 'wb').write(urllib.request.urlopen(req, timeout=45).read())
                    got += 1
                except Exception as e:
                    print(f'   dl fail {i}: {type(e).__name__}')
            print(f'{label}: http={r.status} {len(big)} big imgs, {got} saved')
        except Exception as e:
            print(f'{label}: FAIL {type(e).__name__} {str(e)[:100]}')
    browser.close()
