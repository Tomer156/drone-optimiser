"""Split prop into a uniform geometry string + a separate vendor model column.

  prop        ->  "D.DxP.PxB"   diameter and pitch to 1dp, blade count integer
  prop_model  ->  vendor code, verbatim ("HQ EthiX S4", "T5143S-3", ...) or ''

Blade count is only written when the source states it (an explicit xN / *N in the
string, or a -N / *N suffix in the vendor code). Where no source states it the
blade field is '?' and the prop is listed at the end for a decision - guessing it
would silently change thrust interpretation.
"""
import json, csv, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
DB = r'C:\Users\tomer\Documents\Github\drone-optimizer'

d1 = lambda x: f'{float(x):.1f}'

# vendor codes that carry their own geometry; blade count from the -N / xN suffix
CODE = {
    'C7.5X4.6X3':  ('7.5', '4.6', '3'),
    'F5146-3':     ('5.1', '4.6', '3'),
    'GF7042-2':    ('7.0', '4.2', '2'),
    'T5143S-3':    ('5.1', '4.3', '3'),
    'T5147-3':     ('5.1', '4.7', '3'),
    'T6143-3':     ('6.1', '4.3', '3'),
    'GF 51466-3':  ('5.1', '4.7', '3'),
    'GF51466-3':   ('5.1', '4.7', '3'),
    # D76 / D90 are millimetre diameters (76mm = 3.0in, 90mm = 3.5in); the sheet
    # gives no pitch. My earlier rows mis-recorded the mm figure as pitch.
    'D76':         ('3.0', '?',  '?'),
    'D90':         ('3.5', '?',  '?'),
    # P49436: T-Motor code, pitch not decodable with confidence (4.94x3.6 or 4.9x4.36)
    'P49436-3':    ('4.9', '?',  '3'),
}

GEOM3 = re.compile(r'^(\d+(?:\.\d+)?)[x*](\d+(?:\.\d+)?)[x*](\d)\b\s*(.*)$', re.I)
GEOM2 = re.compile(r'^(\d+(?:\.\d+)?)[x*](\d+(?:\.\d+)?)\s*(.*)$', re.I)
VOLT  = re.compile(r'@\d+V$')


def split(p):
    """-> (prop, prop_model)"""
    raw = p.strip()
    model = ''
    # the original DB encoded a test voltage into the prop string; that belongs
    # in voltage_v, which every row already carries, so drop it
    raw = VOLT.sub('', raw).strip()

    m = GEOM3.match(raw)
    if m:
        dia, pitch, bl, rest = m.groups()
        return f'{d1(dia)}x{d1(pitch)}x{bl}', rest.strip()

    m = GEOM2.match(raw)
    if m:
        dia, pitch, rest = m.groups()
        rest = rest.strip()
        bl = '?'
        sfx = re.search(r'[-*](\d)$', rest)
        if sfx:
            bl = sfx.group(1)
        return f'{d1(dia)}x{d1(pitch)}x{bl}', rest

    # no geometry in the string - resolve from the vendor code
    key = re.sub(r'^T-HOBBY\s+', '', raw).strip()
    for code, (dia, pitch, bl) in CODE.items():
        if key.upper() == code.upper() or key.upper().endswith(code.upper()):
            p_ = d1(pitch) if pitch != '?' else '?'
            return f'{d1(dia)}x{p_}x{bl}', key
    return f'?x?x?', raw


db = json.load(open(f'{DB}/motor_db.json', encoding='utf-8'))
mapping, unresolved = {}, collections.Counter()
for m in db.values():
    for r in m['data']:
        old = r['prop']
        if old not in mapping:
            mapping[old] = split(old)
        prop, model = mapping[old]
        r['prop'], r['prop_model'] = prop, model
        if '?' in prop:
            unresolved[(prop, model)] += 1
    # rebuild the props list in the same normalised form, order preserved
    seen = []
    for r in m['data']:
        if r['prop'] not in seen:
            seen.append(r['prop'])
    m['props'] = seen

print(f'{len(mapping)} distinct prop strings normalised\n')
print('SAMPLE:')
for old, (new, mod) in list(sorted(mapping.items()))[:10]:
    print(f'  {old!r:<32} -> {new:<14} model={mod!r}')

print(f'\nUNRESOLVED ({sum(unresolved.values())} rows, {len(unresolved)} props):')
for (p, mod), n in sorted(unresolved.items(), key=lambda kv: -kv[1]):
    print(f'  {p:<12} model={mod!r:<26} {n} rows')

json.dump(db, open(f'{DB}/motor_db.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# csv gains a prop_model column
FIELDS = ['motor_name','avg_voltage_v','prop','prop_model','throttle_pct','thrust_g',
          'voltage_v','current_a','power_w','efficiency_gw','rpm']
with open(f'{DB}/motor_db.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(FIELDS)
    for name, m in db.items():
        for r in m['data']:
            w.writerow([name, m['avg_voltage'], r['prop'], r['prop_model'], r['throttle'],
                        r['thrust_g'], r['voltage_v'], r['current_a'], r['power_w'],
                        r['efficiency'], r['rpm']])

h = open(f'{DB}/index.html', encoding='utf-8').read()
i, j = h.index('const MOTOR_DB = '), h.index('const BATTERY_DB')
h = h[:i] + 'const MOTOR_DB = ' + json.dumps(db, ensure_ascii=False, separators=(',', ':')) + ';\n' + h[j:]
open(f'{DB}/index.html', 'w', encoding='utf-8', newline='').write(h)
print(f'\nwritten: {len(db)} motors / {sum(len(m["data"]) for m in db.values())} rows')
