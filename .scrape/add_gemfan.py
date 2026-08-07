"""Gemfan Vannystyle 5136 prop test @22.2V - three 2207 motors, 15-90% in 5% steps.

The sheet is prop-centric: it gives current, thrust and T.E.1 (g/W) but no power
column, and no RPM. Power is reconstructed as 22.2V x current (the sheet states a
fixed 22.2V, so no sag is modelled). Efficiency is stored as thrust/power so the
row is internally consistent; rows where the printed T.E.1 disagrees are flagged.
"""
import json, csv, sys
sys.stdout.reconfigure(encoding='utf-8')
DB = r'C:\Users\tomer\Documents\Github\drone-optimizer'
V = 22.2
PROP, MODEL = '5.1x3.6x3', 'Gemfan Vannystyle 5136'
THR = [15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90]

MOTORS = {
 'XNOVA 2207 2050KV': {
   'a':[0.70,1.46,2.68,4.28,6.24,9.11,10.76,12.53,14.71,16.65,19.53,23.49,27.75,31.75,36.90,46.06],
   't':[55,125,180,275,454,554,663,784,860,942,1072,1154,1316,1488,1584,1736],
   'e':[2.63,3.84,2.98,2.94,3.34,2.76,2.78,2.84,2.63,2.56,2.47,2.22,2.14,2.12,1.94,1.70]},
 'T-Motor 2207 1910KV': {
   'a':[0.39,0.77,1.31,2.06,2.97,4.06,5.04,6.74,8.58,10.53,12.84,15.44,18.69,21.85,25.32,29.60],
   't':[43,78,140,213,288,350,411,533,652,745,831,988,1145,1202,1315,1514],
   'e':[5.04,4.81,4.80,4.78,4.42,3.88,3.67,3.56,3.43,3.21,2.91,2.89,2.76,2.49,2.34,2.31]},
 '3B 2207 1950KV': {
   'a':[0.66,1.16,1.92,3.27,4.38,6.01,7.83,9.96,12.51,15.89,19.05,23.13,26.49,31.86,36.82,41.84],
   't':[63,115,158,246,392,497,556,686,841,950,1088,1254,1373,1461,1636,1820],
   'e':[4.30,4.63,3.70,3.39,4.08,3.73,3.22,3.11,3.05,2.69,2.58,2.44,2.34,2.07,2.00,1.97]},
}

db = json.load(open(f'{DB}/motor_db.json', encoding='utf-8'))
flags, added = [], 0
for name, d in MOTORS.items():
    if name in db:
        print(f'SKIP {name} - already present'); continue
    rows = []
    for thr, a, t, e in zip(THR, d['a'], d['t'], d['e']):
        p = round(V * a, 2)
        calc = t / p
        if abs(calc - e) / e > 0.05:
            flags.append((name, thr, a, t, round(calc, 2), e))
        rows.append({'prop': PROP, 'prop_model': MODEL, 'throttle': float(thr), 'thrust_g': float(t),
                     'voltage_v': V, 'current_a': a, 'power_w': p,
                     'efficiency': round(calc, 3), 'rpm': None})
    db[name] = {'name': name, 'avg_voltage': V, 'props': [PROP], 'weight_g': None, 'data': rows}
    added += 1

print(f'added {added} motors, {added*len(THR)} rows')
print(f'\nrows where the sheet\'s printed T.E.1 disagrees with thrust/power by >5%:')
for f in flags:
    print(f'   {f[0]} @{f[1]}%  {f[2]}A {f[3]}g -> computed {f[4]} g/W, sheet says {f[5]}')

json.dump(db, open(f'{DB}/motor_db.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
FIELDS = ['motor_name','avg_voltage_v','prop','prop_model','throttle_pct','thrust_g',
          'voltage_v','current_a','power_w','efficiency_gw','rpm']
with open(f'{DB}/motor_db.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f); w.writerow(FIELDS)
    for n, m in db.items():
        for r in m['data']:
            w.writerow([n, m['avg_voltage'], r['prop'], r.get('prop_model',''), r['throttle'],
                        r['thrust_g'], r['voltage_v'], r['current_a'], r['power_w'],
                        r['efficiency'], r['rpm']])
h = open(f'{DB}/index.html', encoding='utf-8').read()
i, j = h.index('const MOTOR_DB = '), h.index('const BATTERY_DB')
h = h[:i] + 'const MOTOR_DB = ' + json.dumps(db, ensure_ascii=False, separators=(',', ':')) + ';\n' + h[j:]
open(f'{DB}/index.html', 'w', encoding='utf-8', newline='').write(h)
print(f'\nMOTOR_DB: {len(db)} motors / {sum(len(m["data"]) for m in db.values())} rows')
print('motors without weight_g:', [k for k, v in db.items() if not v.get('weight_g')])
EOF = None
