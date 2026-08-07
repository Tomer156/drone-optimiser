"""Second pass for pages the naive img-scan missed.

Collects lazy-load attrs (data-src/srcset/data-original), CSS background-image
urls, and <a href> links to images, then reports candidates by URL keyword.
"""
import sys, json
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

MISSES = [
    ('iflight_xing2_3110', 'https://shop.iflight.com/XING2-3110-Cinelifter-Motor-Pro1729'),
    ('iflight_xing2_2306', 'https://shop.iflight.com/XING2-2306-FPV-Motor-Pro1670'),
    ('geprc_em3215', 'https://geprc.com/product/geprc-em3215-900kv-750kv-motor/'),
    ('geprc_speedx2_2809', 'https://geprc.com/product/geprc-speedx2-2809-1280kv-motor/'),
    ('tmotor_v2808', 'https://www.getfpv.com/t-motor-velox-v2808-cinematic-motor-1300kv-1500kv-1950kv.html'),
    ('tmotor_f60prov', 'https://www.getfpv.com/t-motor-f60-pro-v-motor-1750kv-1950kv-2020kv-2550kv.html'),
    ('bh_avenger_v3_22075', 'https://www.brotherhobbystore.com/products/avenger-22075-v3'),
    ('emax_ecoii_2807', 'https://emaxmodel.com/products/emax-ecoii-2807-3-6s-1300kv-1500kv-1700kv-brushless-motor'),
]

JS = """
() => {
  const out = new Set();
  document.querySelectorAll('img').forEach(e => {
    ['src','data-src','data-original','data-lazy','data-echo'].forEach(a => {
      const v = e.getAttribute(a); if (v) out.add(v);
    });
    const ss = e.getAttribute('srcset'); if (ss) ss.split(',').forEach(s => out.add(s.trim().split(' ')[0]));
  });
  document.querySelectorAll('*').forEach(e => {
    const bg = getComputedStyle(e).backgroundImage;
    if (bg && bg !== 'none') { const m = bg.match(/url\\(["']?(.*?)["']?\\)/); if (m) out.add(m[1]); }
  });
  document.querySelectorAll('a[href]').forEach(a => {
    if (/\\.(png|jpe?g|webp)(\\?|$)/i.test(a.href)) out.add(a.href);
  });
  return [...out];
}
"""

KEY = ('test', 'report', 'spec', 'data', 'thrust', 'param', 'chart', 'detail', 'desc')

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_context(viewport={'width': 1400, 'height': 1000}).new_page()
    for label, url in MISSES:
        try:
            pg.goto(url, timeout=45000, wait_until='domcontentloaded')
            pg.wait_for_timeout(2000)
            for _ in range(8):
                pg.mouse.wheel(0, 6000); pg.wait_for_timeout(500)
            # click any tab that might hold specs
            for sel in ['text=Specification', 'text=Specifications', 'text=Details', 'text=Description', 'text=Parameter']:
                try:
                    pg.click(sel, timeout=1200); pg.wait_for_timeout(1200)
                except Exception:
                    pass
            urls = pg.evaluate(JS)
            hot = [u for u in urls if any(k in u.lower() for k in KEY)]
            print(f'--- {label}: {len(urls)} urls, {len(hot)} keyword hits, status={pg.url[:70]}')
            for u in (hot or urls)[:8]:
                print('    ', u[:135])
        except Exception as e:
            print(f'--- {label}: FAIL {type(e).__name__} {str(e)[:110]}')
    b.close()
