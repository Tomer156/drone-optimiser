# archive

Nothing here is read by the app. Retained for provenance only.

## Removed 2026-08-08

Nine files were deleted after each was checked against the live database rather than
assumed stale. Every one is still in git history if it is ever wanted back.

- `motor_db_new.csv` … `motor_db_new5.csv` — 1,077 transcription rows. Matched on
  motor + throttle + thrust + current: **every row is present live**, except 28 rows for
  `Hobbywing RTF-3115 900KV`, which is a duplicate of the live `RTF-3115 900KV` down to
  all 28 rows and all four props.
- `motor_weights.csv` / `motor_weights.json` — the original 44-motor weight survey.
  **Zero rows carried anything live lacks.** The three motors still missing `weight_g`
  (`XNOVA 2207 2050KV`, `T-Motor 2207 1910KV`, `3B 2207 1950KV`) were never in it.
- `motor_db.xlsx` — 40 motor names, **all present live**.
- `battery_db.xlsx` — 201 SKUs, **all present live**.

## Still live, in the repo root

- `motor_db.json` / `motor_db.csv`, `battery_db.json` / `battery_db.csv` — the source of
  truth. Written together by the merge scripts; no build step enforces that, so they
  drift if edited individually.
- `db.json` — generated from those for the Cloudflare KV upload. Not committed: it is
  the copy the app no longer ships, and publishing it would undo the point of moving it.
- `motor_candidates.csv`, `motor_candidates_5in.csv`, `battery_candidates_5in.csv` —
  active gap tracking (sources, confidence, what is still missing). Not app data.
- `.scrape/` — the manufacturer screenshots every bench row was read from, and the
  scripts that read them. This is the provenance of the whole database.
