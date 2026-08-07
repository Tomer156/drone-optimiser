# archive

Nothing here is read by the app or kept in sync. Retained for provenance only.

## Stale exports (superseded 2026-08-07)
- `motor_db.xlsx`, `battery_db.xlsx` — last written 2026-05-15, when the database
  held 44 motors / 660 rows and 209 packs. The live data is now 104 motors /
  1761 rows and 226 packs. These were never regenerated and are 60 motors behind.

## Merged staging files
- `motor_db_new.csv` … `motor_db_new5.csv` — transcription batches, all merged
  into motor_db.json / motor_db.csv / index.html. Verified: every motor in these
  files is present live, except `Hobbywing RTF-3115 900KV` in motor_db_new.csv,
  which was dropped deliberately as a byte-identical duplicate of `RTF-3115 900KV`.

## Superseded working files
- `motor_weights.csv`, `motor_weights.json` — the original 44-motor weight survey.
  Now carried per motor as `weight_g` inside the database (101 of 104 populated).

## Still live, in the repo root
- `index.html` — THE database. The only source the app reads.
- `motor_db.json` / `motor_db.csv`, `battery_db.json` / `battery_db.csv` — mirrors,
  written together by the merge scripts. No build step enforces this; they drift
  if edited individually.
- `motor_candidates.csv`, `motor_candidates_5in.csv`, `battery_candidates_5in.csv`
  — active gap tracking (sources, confidence, what is still missing). Not app data.
