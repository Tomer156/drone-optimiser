"""Find a Playwright configuration GetFPV will serve.

Headless Chromium gets a bare 403. Escalate: automation flags off, real headers,
then a headed window, then the installed Chrome channel.
"""
import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')
URL = 'https://www.getfpv.com/t-motor-velox-v2808-cinematic-motor-1300kv-1500kv-1950kv.html'
UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '?1',
}
STEALTH = """() => {
  Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
  Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
  Object.defineProperty(navigator, 'languages', {get: () => ['en-US','en']});
  window.chrome = {runtime: {}};
}"""
ARGS = ['--disable-blink-features=AutomationControlled', '--no-sandbox',
        '--disable-dev-shm-usage', '--start-maximized']


def attempt(name, launch_kw, use_stealth):
    with sync_playwright() as p:
        try:
            b = p.chromium.launch(**launch_kw)
        except Exception as e:
            print(f'{name:<28} launch failed: {type(e).__name__} {str(e)[:70]}')
            return False
        try:
            ctx = b.new_context(user_agent=UA, viewport={'width': 1440, 'height': 900},
                                locale='en-US', timezone_id='America/New_York',
                                extra_http_headers=HEADERS)
            if use_stealth:
                ctx.add_init_script(STEALTH)
            pg = ctx.new_page()
            r = pg.goto(URL, timeout=60000, wait_until='domcontentloaded')
            pg.wait_for_timeout(4000)
            n = pg.evaluate('()=>document.images.length')
            txt = pg.evaluate('()=>document.body.innerText.length')
            print(f'{name:<28} http={r.status} imgs={n} textlen={txt} title={pg.title()[:40]}')
            return r.status == 200 and n > 5
        except Exception as e:
            print(f'{name:<28} FAIL {type(e).__name__} {str(e)[:70]}')
            return False
        finally:
            b.close()


ok = attempt('headless + stealth', dict(headless=True, args=ARGS), True)
if not ok:
    ok = attempt('headed + stealth', dict(headless=False, args=ARGS), True)
if not ok:
    ok = attempt('headed chrome channel', dict(headless=False, channel='chrome', args=ARGS), True)
print('\nRESULT:', 'a working config was found' if ok else 'GetFPV blocked in every config tried')
