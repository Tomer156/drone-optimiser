"""Find how T-Motor / T-HOBBY expose their basicParameter/testParameter .xls files."""
import sys, re, json
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

PAGES = [
    ('pacer_v3_2207',  'https://shop.tmotor.com/products/fpv-brushless-motor-2207-v3'),
    ('f60_pro_v',      'https://shop.tmotor.com/products/f60-pro-v-2207-5-fpv-motor'),
    ('velox_v2306_v3', 'https://shop.tmotor.com/products/velox-v2306-v3-motor'),
    ('tmotor_search',  'https://shop.tmotor.com/collections/fpv-motor'),
]

HUNT = """() => {
  const out = [];
  document.querySelectorAll('a[href]').forEach(a => {
    if (/\\.xls|parameter|download/i.test(a.href + ' ' + a.textContent))
      out.push({t: (a.textContent||'').trim().slice(0,40), h: a.href});
  });
  document.querySelectorAll('[onclick],[data-url],[data-href],[data-file]').forEach(e => {
    ['onclick','data-url','data-href','data-file'].forEach(k => {
      const v = e.getAttribute(k);
      if (v && /xls|parameter/i.test(v)) out.push({t: k, h: v.slice(0,160)});
    });
  });
  return out;
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 1400, 'height': 1000})
    page = ctx.new_page()
    seen = []
    page.on('request', lambda r: seen.append(r.url) if re.search(r'\.xls|parameter', r.url, re.I) else None)
    for label, url in PAGES:
        try:
            r = page.goto(url, timeout=45000, wait_until='domcontentloaded')
            page.wait_for_timeout(3000)
            for _ in range(5):
                page.mouse.wheel(0, 5000); page.wait_for_timeout(500)
            hits = page.evaluate(HUNT)
            print(f'--- {label}: http={r.status} title={page.title()[:45]} | {len(hits)} candidate links')
            for h in hits[:8]:
                print(f'     {h["t"][:36]:<38} {h["h"][:110]}')
        except Exception as e:
            print(f'--- {label}: FAIL {type(e).__name__} {str(e)[:90]}')
    if seen:
        print('\nnetwork requests matching xls/parameter:')
        for u in dict.fromkeys(seen):
            print('   ', u[:150])
    b.close()
