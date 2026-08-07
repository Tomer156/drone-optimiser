"""Harvest vendor datasheet images (thrust tables) from FPV motor product pages.

Playwright loads each page, scrolls to trigger lazy-loading, then keeps any image
big enough to be a spec/test-report sheet. Files land in .scrape/<label>_<n>.<ext>.
Re-runs skip anything already on disk.
"""
import os, sys, json, urllib.request, urllib.parse
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
OUT = os.path.dirname(os.path.abspath(__file__))
MIN_H, MIN_W = 700, 450          # a datasheet sheet is tall and wide
MAX_PER_PAGE = 4

TARGETS = [
    # --- iFlight (7-10") ---
    ('iflight_xing2_3110', 'https://shop.iflight.com/XING2-3110-Cinelifter-Motor-Pro1729'),
    ('iflight_xing2_3314', 'https://shop.iflight.com/XING2-3314-Cinelifter-Motor-Pro2034'),
    ('iflight_xing_e_3314', 'https://shop.iflight.com/XING-E-3314-Cinelifter-Motor-Pro2137'),
    ('iflight_nidici_3115', 'https://shop.iflight.com/NIDICI-3115-FPV-Motor-Pro2317'),
    ('iflight_nidici_2807', 'https://shop.iflight.com/NIDICI-cat381/NIDICI-2807-FPV-Motor-Pro2314'),
    # --- iFlight (5") ---
    ('iflight_xing_e_pro_2207', 'https://shop.iflight.com/xing-e-pro-2207-2-6s-fpv-nextgen-motor-pro874'),
    ('iflight_xing2_2306', 'https://shop.iflight.com/XING2-2306-FPV-Motor-Pro1670'),
    # --- GEPRC ---
    ('geprc_em3110', 'https://geprc.com/product/geprc-em3110-900kv-motor/'),
    ('geprc_em3215', 'https://geprc.com/product/geprc-em3215-900kv-750kv-motor/'),
    ('geprc_speedx2_2809', 'https://geprc.com/product/geprc-speedx2-2809-1280kv-motor/'),
    ('geprc_speedx2_3214', 'https://geprc.com/product/geprc-speedx2-3214-860kv-motor/'),
    # --- MAD ---
    ('mad_bsc2812', 'https://store.mad-motor.com/products/mad-2812-drone-motor'),
    ('mad_bsc2810', 'https://store.mad-motor.com/products/mad-bsc-2810-fpv-drone-motor'),
    ('mad_bsc3115', 'https://store.mad-motor.com/products/mad-3115-drone-motor'),
    # --- EMAX ---
    ('emax_ecoii_2814', 'https://emaxmodel.com/products/emax-ecoii-2814-3-6s-730kv-830kv-brushless-motor-for-rc-drone-fpv-racing'),
    ('emax_ecoii_2807', 'https://emaxmodel.com/products/emax-ecoii-2807-3-6s-1300kv-1500kv-1700kv-brushless-motor'),
    # --- T-Motor via GetFPV ---
    ('tmotor_v2808', 'https://www.getfpv.com/t-motor-velox-v2808-cinematic-motor-1300kv-1500kv-1950kv.html'),
    ('tmotor_v3115', 'https://www.getfpv.com/t-motor-velox-v3115-motor-400kv-640kv-900kv.html'),
    ('tmotor_f60prov', 'https://www.getfpv.com/t-motor-f60-pro-v-motor-1750kv-1950kv-2020kv-2550kv.html'),
    ('tmotor_v2306v3', 'https://www.getfpv.com/t-motor-velox-v2306-v3-motor-1500kv-1750kv-1950kv-2550kv.html'),
    # --- others ---
    ('foxeer_bh3115', 'https://www.foxeer.com/foxeer-black-hornet-3115-900kv-fpv-motor-g-573'),
    ('foxeer_bh3210', 'https://www.foxeer.com/foxeer-black-hornet-3210-900kv-motor-g-522'),
    ('axisflying_ae2207v2', 'https://www.axisflying.com/products/5inch-brushless-economic-fpv-motor-ae2207-v2'),
    ('bh_avenger_v3_22075', 'https://www.brotherhobbystore.com/products/avenger-22075-v3'),
    ('rcinpower_gtsv2_2207', 'https://www.getfpv.com/rcinpower-gts-v2-2207-plus-motor-1860kv-2500kv-2750kv.html'),
    ('hobbywing_xrotor_2812', 'https://www.hobbywing.com/en/products/xrotor2812'),
]

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'


def fetch(label, url, page):
    page.goto(url, timeout=45000, wait_until='domcontentloaded')
    page.wait_for_timeout(2500)
    for _ in range(6):                       # scroll to force lazy loads
        page.mouse.wheel(0, 6000)
        page.wait_for_timeout(700)
    page.wait_for_timeout(1500)
    imgs = page.eval_on_selector_all(
        'img', 'els=>els.map(e=>({u:e.currentSrc||e.src,w:e.naturalWidth,h:e.naturalHeight}))')
    cand = [d for d in imgs if d['u'] and d['h'] >= MIN_H and d['w'] >= MIN_W]
    seen, uniq = set(), []
    for d in sorted(cand, key=lambda d: -(d['h'] * d['w'])):
        base = d['u'].split('?')[0]
        if base in seen:
            continue
        seen.add(base)
        uniq.append(d)
    saved = []
    for i, d in enumerate(uniq[:MAX_PER_PAGE]):
        ext = os.path.splitext(d['u'].split('?')[0])[1].lower()
        if ext not in ('.png', '.jpg', '.jpeg', '.webp'):
            ext = '.png'
        fn = os.path.join(OUT, f'{label}_{i}{ext}')
        if os.path.exists(fn):
            saved.append((fn, d['w'], d['h'], 'cached'))
            continue
        try:
            req = urllib.request.Request(d['u'], headers={'User-Agent': UA, 'Referer': url})
            blob = urllib.request.urlopen(req, timeout=45).read()
            open(fn, 'wb').write(blob)
            saved.append((fn, d['w'], d['h'], f'{len(blob)//1024}KB'))
        except Exception as e:
            saved.append((fn, d['w'], d['h'], f'ERR {type(e).__name__}'))
    return saved


results = {}
with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(user_agent=UA, viewport={'width': 1400, 'height': 1000})
    page = ctx.new_page()
    for label, url in TARGETS:
        try:
            got = fetch(label, url, page)
            results[label] = [{'file': os.path.basename(f), 'w': w, 'h': h, 'status': s} for f, w, h, s in got]
            print(f'{label}: {len(got)} images ' + ', '.join(f'{os.path.basename(f)}({w}x{h},{s})' for f, w, h, s in got))
        except Exception as e:
            results[label] = [{'error': f'{type(e).__name__}: {str(e)[:120]}'}]
            print(f'{label}: FAIL {type(e).__name__} {str(e)[:120]}')
    browser.close()

json.dump(results, open(os.path.join(OUT, 'harvest_index.json'), 'w'), indent=1)
print('\nindex ->', os.path.join(OUT, 'harvest_index.json'))
