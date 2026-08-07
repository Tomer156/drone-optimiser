"""Ingest T-Motor / T-HOBBY vendor .xls exports (really HTML tables).

testParameter_*.xls  -> per-prop, per-KV throttle sweeps -> motor_db schema rows
basicParameter_*.xls -> per-KV weight / idle / peak / max power

The test table is ragged: 'Propeller' and 'Type' (KV) appear only on the first
row of each block, so both are carried forward.
"""
import re, sys, csv, os, glob
from html.parser import HTMLParser

sys.stdout.reconfigure(encoding='utf-8')
OUT = r'C:\Users\tomer\Documents\Github\drone-optimizer\motor_db_new2.csv'

JOBS = [
    ('T-Motor F60 Pro V 2207.5', 'F60PROV'),
    ('T-Motor Velox V2306 V3', 'V2306 V3'),
]
SRC = r'C:\Users\tomer\Downloads'


class T(HTMLParser):
    def __init__(self):
        super().__init__(); self.rows = []; self.cell = None; self.row = None
    def handle_starttag(self, tag, attrs):
        if tag == 'tr': self.row = []
        elif tag in ('td', 'th'): self.cell = []
    def handle_endtag(self, tag):
        if tag == 'tr' and self.row is not None:
            self.rows.append(self.row); self.row = None
        elif tag in ('td', 'th') and self.cell is not None:
            if self.row is not None:
                self.row.append(re.sub(r'\s+', ' ', ''.join(self.cell)).strip())
            self.cell = None
    def handle_data(self, d):
        if self.cell is not None: self.cell.append(d)


def rows_of(path):
    p = T(); p.feed(open(path, encoding='utf-8-sig', errors='replace').read())
    return [r for r in p.rows if any(c for c in r)]


def find(pattern, kind):
    hits = [f for f in glob.glob(os.path.join(SRC, f'{kind}*.xls')) if pattern in f]
    hits = [f for f in hits if '(1)' not in f] or hits          # skip browser duplicates
    if not hits:
        raise FileNotFoundError(f'{kind} file matching {pattern!r}')
    return hits[0]


NUM = re.compile(r'-?\d+(?:\.\d+)?')
KVRE = re.compile(r'^(?:KV(\d{3,4})|(\d{3,4})KV)$', re.I)  # vendor uses both orders
THR = re.compile(r'^(\d{1,3})%$')


def parse_basic(path):
    spec, cur = {}, None
    for r in rows_of(path):
        for i in range(0, len(r) - 1, 2):
            k, v = r[i].strip(), r[i + 1].strip()
            if not k:
                continue
            if k == 'KV' and KVRE.match(v):
                m = KVRE.match(v); cur = int(m.group(1) or m.group(2)); spec[cur] = {}
            elif cur is not None:
                spec[cur][k] = v
    return spec


def parse_test(path):
    out, prop, kv = [], None, None
    for r in rows_of(path):
        if r and r[0].lower().startswith('propeller'):
            continue
        cells = list(r)
        # a block's first row carries the prop name; a KV row carries the KV
        if cells and not THR.match(cells[0]) and not KVRE.match(cells[0]):
            prop = cells[0]; cells = cells[1:]
        if cells and KVRE.match(cells[0]):
            m = KVRE.match(cells[0]); kv = int(m.group(1) or m.group(2)); cells = cells[1:]
        if not cells or not THR.match(cells[0]):
            continue
        thr = int(THR.match(cells[0]).group(1))
        nums = [float(x) for x in cells[1:] if NUM.fullmatch(x)]
        if len(nums) < 6:
            continue
        volts, amps, rpm, thrust, watts, eff = nums[:6]
        out.append(dict(kv=kv, prop=prop, throttle_pct=thr, voltage_v=volts, current_a=amps,
                        rpm=int(rpm), thrust_g=thrust, power_w=watts, efficiency_gw=eff))
    return out


allrows = []
for name, pattern in JOBS:
    spec = parse_basic(find(pattern, 'basicParameter'))
    test = parse_test(find(pattern, 'testParameter'))
    print(f'--- {name}')
    for kv, s in spec.items():
        print(f'    {kv}KV  weight={s.get("Weight (Incl. Cable)")}  idle={s.get("Idle Current(10V)")}  '
              f'maxP={s.get("Max. Power(10s)")}  peak={s.get("Peak Current(10s)")}')
    props = sorted({r['prop'] for r in test if r['prop']})
    kvs = sorted({r['kv'] for r in test})
    print(f'    test rows: {len(test)} | props={props} | KVs={kvs}')

    badE = [r for r in test if abs(r['thrust_g'] / r['power_w'] - r['efficiency_gw']) > 0.03]
    badP = [r for r in test if abs(r['voltage_v'] * r['current_a'] - r['power_w']) / r['power_w'] > 0.04]
    print(f'    checks: efficiency mismatches={len(badE)}  V*I-vs-power mismatches={len(badP)}')

    for r in test:
        allrows.append(dict(motor_name=f'{name} {r["kv"]}KV', avg_voltage_v=r['voltage_v'],
                            prop=r['prop'], throttle_pct=r['throttle_pct'], thrust_g=r['thrust_g'],
                            voltage_v=r['voltage_v'], current_a=r['current_a'], power_w=r['power_w'],
                            efficiency_gw=r['efficiency_gw'], rpm=r['rpm']))

with open(OUT, 'a', newline='', encoding='utf-8') as f:
    csv.DictWriter(f, fieldnames=list(allrows[0].keys())).writerows(allrows)
print(f'\nappended {len(allrows)} rows -> {os.path.basename(OUT)}')
