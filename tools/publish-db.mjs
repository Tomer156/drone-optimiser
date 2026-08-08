#!/usr/bin/env node
// Rebuild db.json from the repo mirrors and push it to Cloudflare KV.
//
//   node tools/publish-db.mjs              rebuild, check, upload, verify
//   node tools/publish-db.mjs --dry-run    rebuild and check only, no upload
//
// Run this after any database edit. Nothing else enforces it: the mirrors are the source of
// truth, db.json is generated, and the site serves whatever is in KV. Edit a mirror without
// running this and the repo looks current while the site serves yesterday's data.
import { readFileSync, writeFileSync, statSync } from 'node:fs';
import { execSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const DRY = process.argv.includes('--dry-run');
const read = f => JSON.parse(readFileSync(join(ROOT, f), 'utf8'));
const die = m => { console.error('\n  FAILED  ' + m + '\n'); process.exit(1); };

console.log('rebuilding db.json from the mirrors');
const motors = read('motor_db.json');
const batteries = read('battery_db.json');

// ── checks, because an upload is not reversible in any useful sense ────────────────────────────
const motorNames = Object.keys(motors);
if (motorNames.length < 50) die(`only ${motorNames.length} motors; the mirror looks truncated`);
if (!Array.isArray(batteries) || batteries.length < 100) die(`only ${batteries?.length} packs; the mirror looks truncated`);

let rows = 0;
const empty = [];
for (const [name, m] of Object.entries(motors)) {
  const d = m?.data;
  if (!Array.isArray(d) || d.length === 0) empty.push(name);
  else rows += d.length;
  if (!Array.isArray(m?.props) || m.props.length === 0) empty.push(name + ' (no props)');
}
if (empty.length) die(`${empty.length} motors carry no usable data: ${empty.slice(0, 5).join(', ')}`);

const usable = batteries.filter(b => b.weight_g > 0 && b.discharge_c > 0).length;
if (usable === 0) die('no pack has both a weight and a C-rating; the app would have nothing to fit');

// The CSV and JSON mirrors are written together by the merge scripts and nothing enforces that.
// A row-count mismatch means one was edited alone, and uploading would publish whichever the
// JSON happens to hold.
const csvRows = readFileSync(join(ROOT, 'motor_db.csv'), 'utf8').trim().split(/\r?\n/).length - 1;
if (csvRows !== rows) {
  die(`motor_db.csv has ${csvRows} rows, motor_db.json has ${rows}. The mirrors have drifted; ` +
      `reconcile them before publishing.`);
}

console.log(`  ${motorNames.length} motors, ${rows} measurement rows, ${batteries.length} packs ` +
            `(${usable} usable), csv agrees`);

// ── write ─────────────────────────────────────────────────────────────────────────────────────
const out = join(ROOT, 'db.json');
writeFileSync(out, JSON.stringify({ motors, batteries }), 'utf8');
const kb = (statSync(out).size / 1024).toFixed(1);
console.log(`  db.json written, ${kb} KB`);

if (DRY) { console.log('\ndry run: nothing uploaded\n'); process.exit(0); }

// ── upload ────────────────────────────────────────────────────────────────────────────────────
// --remote matters: without it wrangler writes to local storage and the Worker reads an empty
// namespace while every command reports success.
console.log('uploading to KV (key: db)');
// Through a shell: since Node 20, execFile refuses to run a .cmd directly on Windows, which is
// what npx is there. The arguments are fixed strings, so there is nothing here to quote around.
const run = args => execSync('npx ' + args.join(' '),
  { cwd: join(ROOT, 'worker'), encoding: 'utf8', stdio: ['ignore', 'pipe', 'inherit'] });

try {
  run(['wrangler', 'kv', 'key', 'put', 'db', '--binding=DB', '--path=../db.json', '--remote']);
} catch (e) {
  die('wrangler upload failed (' + (e.message || e) + '). ' +
      'If this is a fresh machine, run `npx wrangler login` in worker/ first.');
}

// ── verify what actually landed, rather than trusting the exit code ────────────────────────────
const back = run(['wrangler', 'kv', 'key', 'get', 'db', '--binding=DB', '--remote', '--text']);
let parsed;
try { parsed = JSON.parse(back); } catch { die('KV returned something that is not JSON'); }
const gotMotors = Object.keys(parsed.motors || {}).length;
const gotPacks = (parsed.batteries || []).length;
if (gotMotors !== motorNames.length || gotPacks !== batteries.length) {
  die(`KV holds ${gotMotors} motors / ${gotPacks} packs, expected ${motorNames.length} / ${batteries.length}`);
}
console.log(`  KV confirmed: ${gotMotors} motors, ${gotPacks} packs`);
console.log('\ndone. The site serves this on its next load; there is no cache to clear.\n');
