# RCDB Open Issues Triage

Repo: [JeffersonLab/rcdb](https://github.com/JeffersonLab/rcdb) · Triaged against current `main` (version `2.2.10`) on 2026-06-16.
Open issues fetched via the public GitHub API, ordered oldest → newest (35 issues; PR #123 excluded).

**Legend** — Status: `relevant` (still reproducible / actionable in current code), `not relevant` (fixed or obsolete), `data-gap` (request to add/fix *data*, not code — flagged and skipped per instructions), `enhancement` (new feature, not a bug).

## Summary table

| Issue | Status | Difficulty / Risk | One-liner |
|---|---|---|---|
| [#22](https://github.com/JeffersonLab/rcdb/issues/22) | FIXED ✅ | — | Verified: `uv run rcdb select "'ha' in d"` runs clean (exit 0) where `d` is `None`/absent for some runs |
| [#27](https://github.com/JeffersonLab/rcdb/issues/27) | not relevant | — | CLI `sel`/`select` rewritten; `.extend()` bug gone |
| [#28](https://github.com/JeffersonLab/rcdb/issues/28) | relevant | Easy / Low | Web `per_page = run_max - run_min` off-by-one for small ranges |
| [#38](https://github.com/JeffersonLab/rcdb/issues/38) | data-gap | — | Backfill `evio_*` for 2016 runs |
| [#40](https://github.com/JeffersonLab/rcdb/issues/40) | data-gap | — | Wrong end time for run 11363 |
| [#42](https://github.com/JeffersonLab/rcdb/issues/42) | enhancement | Med / Med | Post-run "offline comments" field |
| [#44](https://github.com/JeffersonLab/rcdb/issues/44) | data-gap / enh | — | Store more DAQ config files |
| [#46](https://github.com/JeffersonLab/rcdb/issues/46) | needs-info | Low | C++ build warnings; `rcdb.h` doesn't exist, attachment gone |
| [#47](https://github.com/JeffersonLab/rcdb/issues/47) | enhancement | Med / Low | JSON query API for the web site |
| [#49](https://github.com/JeffersonLab/rcdb/issues/49) | not relevant | — | CI exists (GitHub Actions) |
| [#50](https://github.com/JeffersonLab/rcdb/issues/50) | enhancement | Med / Low | RCDB → ROOT export |
| [#56](https://github.com/JeffersonLab/rcdb/issues/56) | enhancement | Med / Med | Index/speed up common queries |
| [#57](https://github.com/JeffersonLab/rcdb/issues/57) | enhancement | Med / Med | Run-dependent aliases |
| [#60](https://github.com/JeffersonLab/rcdb/issues/60) | data-gap / enh | — | Archive rocps1/rocps2 FADC configs |
| [#62](https://github.com/JeffersonLab/rcdb/issues/62) | partially relevant | Med / Med | C++ SQLite still behind `-DRCDB_SQLITE` compile flag |
| [#72](https://github.com/JeffersonLab/rcdb/issues/72) | data-gap | — | Broken data, run 40968 |
| [#78](https://github.com/JeffersonLab/rcdb/issues/78) | data-gap | — | Broken file links, runs 30787/30788 |
| [#83](https://github.com/JeffersonLab/rcdb/issues/83) | data-gap | — | Missing entries, run 61445 |
| [#84](https://github.com/JeffersonLab/rcdb/issues/84) | FIXED ✅ | — | Verified: `uv run rcdb select "'ZZZ' in d"` → empty result, exit 0; residual is data only |
| [#86](https://github.com/JeffersonLab/rcdb/issues/86) | enhancement | Med / Low | Process/tooling for community data fixes |
| [#90](https://github.com/JeffersonLab/rcdb/issues/90) | relevant | Easy / Low | C++ `ToTime()` reads `int_column` for Time → epoch 1970 |
| [#93](https://github.com/JeffersonLab/rcdb/issues/93) | data-gap / enh | — | Record prestart time |
| [#96](https://github.com/JeffersonLab/rcdb/issues/96) | FIXED (local) ✅ | — | Friendly hint/redirect for run number/range in the query box + `None`-result guard; no 500 path left |
| [#98](https://github.com/JeffersonLab/rcdb/issues/98) | data-gap | — | `evio_files_count` wrong for spring-2020 runs |
| [#99](https://github.com/JeffersonLab/rcdb/issues/99) | FIXED (local) ✅ | — | Schema-mismatch error now tells the user to run `rcdb db update` (or upgrade RCDB) |
| [#100](https://github.com/JeffersonLab/rcdb/issues/100) | not relevant | — | `rcdb db update` command exists |
| [#101](https://github.com/JeffersonLab/rcdb/issues/101) | relevant | Med / Med | Java `toTime()` returns date-less `java.sql.Time` |
| [#103](https://github.com/JeffersonLab/rcdb/issues/103) | not relevant | — | Already python3 / v2.x tagged |
| [#108](https://github.com/JeffersonLab/rcdb/issues/108) | not relevant | — | GitHub Actions tests set up |
| [#115](https://github.com/JeffersonLab/rcdb/issues/115) | not relevant | — | `rcdb_web` moved into `rcdb` (`python/rcdb/web`) |
| [#118](https://github.com/JeffersonLab/rcdb/issues/118) | FIXED ✅ | — | Verified: `select_values(['a','b'], '', run_min=1, run_max=9)` returns rows, no bind-param error |
| [#120](https://github.com/JeffersonLab/rcdb/issues/120) | relevant | Med / Low | Bundled rapidjson 1.1.0 memcpy warning |
| [#121](https://github.com/JeffersonLab/rcdb/issues/121) | mostly done | Low | ECAL added to active parser |
| [#122](https://github.com/JeffersonLab/rcdb/issues/122) | relevant | Easy / Low | C++ SQLite hard-requires `files_have_runs` table (PR #123 open) |

---

## Tracking checklist

`- [x]` = resolved / done / closeable (no code action). `- [ ]` = still open / actionable.

**Resolved or closeable (verified or confirmed in code):**
- [x] [#22](https://github.com/JeffersonLab/rcdb/issues/22) — `X in cond` no longer crashes (verified via `uv run rcdb select`)
- [x] [#27](https://github.com/JeffersonLab/rcdb/issues/27) — CLI `.extend()` bug gone after rewrite
- [x] [#49](https://github.com/JeffersonLab/rcdb/issues/49) — CI exists (GitHub Actions)
- [x] [#84](https://github.com/JeffersonLab/rcdb/issues/84) — same fix as #22 (verified); residual is data only
- [x] [#100](https://github.com/JeffersonLab/rcdb/issues/100) — `rcdb db update` command exists
- [x] [#103](https://github.com/JeffersonLab/rcdb/issues/103) — already python3, v2.x tagged
- [x] [#108](https://github.com/JeffersonLab/rcdb/issues/108) — GitHub Actions tests set up
- [x] [#115](https://github.com/JeffersonLab/rcdb/issues/115) — `rcdb_web` now lives in `rcdb` package
- [x] [#118](https://github.com/JeffersonLab/rcdb/issues/118) — `select_values` run_min/run_max binds correctly (verified)
- [x] [#121](https://github.com/JeffersonLab/rcdb/issues/121) — ECAL present in active parser (legacy parser cleanup optional)
- [x] [#96](https://github.com/JeffersonLab/rcdb/issues/96) — **FIXED (local):** friendly hint/redirect for a run number/range in the query box, plus a `None`-result guard closing the whole 500 class; verified
- [x] [#99](https://github.com/JeffersonLab/rcdb/issues/99) — **FIXED (local):** schema-mismatch error now tells the user to run `rcdb db update`; verified

**Actionable code fixes (easy / low-risk):**
- [ ] [#28](https://github.com/JeffersonLab/rcdb/issues/28) — web `per_page` off-by-one (`+ 1`)
- [ ] [#90](https://github.com/JeffersonLab/rcdb/issues/90) — C++ `int_column` → `time_column` for Time
- [ ] [#122](https://github.com/JeffersonLab/rcdb/issues/122) — tolerate missing `files_have_runs` (merge/refine PR #123)
- [ ] [#31](https://github.com/JeffersonLab/rcdb/issues/31) — add CLI to show run start/end/length

**Actionable but larger / API-touching:**
- [ ] [#62](https://github.com/JeffersonLab/rcdb/issues/62) — C++ SQLite behind compile flag (build-contract change)
- [ ] [#101](https://github.com/JeffersonLab/rcdb/issues/101) — Java `toTime()` returns date-less `java.sql.Time` (public API)
- [ ] [#120](https://github.com/JeffersonLab/rcdb/issues/120) — bump vendored rapidjson (memcpy warning)
- [ ] [#46](https://github.com/JeffersonLab/rcdb/issues/46) — C++ build warnings; needs current output (overlaps #120)

**Enhancements (new features):**
- [ ] [#42](https://github.com/JeffersonLab/rcdb/issues/42) — post-run offline comments field
- [ ] [#47](https://github.com/JeffersonLab/rcdb/issues/47) — JSON query API
- [ ] [#50](https://github.com/JeffersonLab/rcdb/issues/50) — RCDB → ROOT export
- [ ] [#56](https://github.com/JeffersonLab/rcdb/issues/56) — index/speed up common queries
- [ ] [#57](https://github.com/JeffersonLab/rcdb/issues/57) — run-dependent aliases
- [ ] [#86](https://github.com/JeffersonLab/rcdb/issues/86) — tooling/process for community data fixes

**Data-gaps (flagged; not code — fix in DB/ops):**
- [ ] [#38](https://github.com/JeffersonLab/rcdb/issues/38) — backfill `evio_*` for 2016 runs
- [ ] [#40](https://github.com/JeffersonLab/rcdb/issues/40) — wrong end time, run 11363
- [ ] [#44](https://github.com/JeffersonLab/rcdb/issues/44) — store more DAQ config files
- [ ] [#60](https://github.com/JeffersonLab/rcdb/issues/60) — archive rocps1/rocps2 FADC configs
- [ ] [#72](https://github.com/JeffersonLab/rcdb/issues/72) — broken data, run 40968
- [ ] [#78](https://github.com/JeffersonLab/rcdb/issues/78) — broken file links, runs 30787/30788
- [ ] [#83](https://github.com/JeffersonLab/rcdb/issues/83) — missing entries, run 61445
- [ ] [#93](https://github.com/JeffersonLab/rcdb/issues/93) — record prestart time
- [ ] [#98](https://github.com/JeffersonLab/rcdb/issues/98) — `evio_files_count` wrong, spring-2020 runs

---

## Details

### [#22 — NoneType in search string](https://github.com/JeffersonLab/rcdb/issues/22)
**Status: FIXED / not relevant (verified).**
`select_runs` builds an **inner join** (`python/rcdb/provider.py:948-955`), so runs that simply lack the condition are excluded from the evaluated set — the original 2016 crash case no longer occurs. A `None` only reaches the per-run `eval` if a condition *row exists with a NULL stored value*, and `'X' in None` raising there is normal Python: `radiator_type and 'RETR' in radiator_type` is the expected idiom. Even then the website doesn't 500 — the `/search` route wraps `select_runs` in try/except and shows a friendly `"Error in performing request: ..."` flash + redirect (`web/modules/runs.py:237-240`), the exact message in the original issue.

**Verification (2026-06-16)** — driven through the real `rcdb select` CLI entrypoint via `uv`. Seeded a SQLite DB whose string condition `d` is `None`/absent for runs 2 & 3 (the `radiator_type` analog):

```console
$ cd python
$ env RCDB_CONNECTION="sqlite:////tmp/rcdb_triage.sqlite" uv run rcdb db init --add-tests   # (confirmed)
$ env RCDB_CONNECTION="sqlite:////tmp/rcdb_triage.sqlite" uv run rcdb select "'ha' in d"
┏━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ run_num ┃ event_count ┃ run_config ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1       │ None        │ None       │
└─────────┴─────────────┴────────────┘
$ echo $status
0
```

Exit **0**, returned run 1 (`haha`), runs 2/3 (no `d` condition) silently excluded — **no `NoneType` / `QueryEvaluationError`**. By design; no code change warranted.

### [#27 — rcdb sel doesn't work](https://github.com/JeffersonLab/rcdb/issues/27)
**Status: not relevant (fixed).**
The traceback was `["run_num"].extend(...)` returning `None`. The CLI was rewritten; `python/rcdb/cli/select.py:40-43` builds args correctly and no longer relies on `.extend()`'s return value. Not reproducible.

### [#28 — Web error for short run-ranges](https://github.com/JeffersonLab/rcdb/issues/28)
**Status: relevant (changed) · Difficulty: easy · Risk: low.**
The old hard error is gone, but `python/rcdb/web/modules/runs.py:56` sets `per_page = run_max - run_min` (off by one for an inclusive range). For 11590–11600 (11 runs) `per_page=10` → the last run is dropped; for a single-run range `per_page=0` → `Pagination` yields 0 pages and an empty slice (`pagination.py:13,29`). Fix: `per_page = run_max - run_min + 1`. Self-contained.

### [#31 — Get date/time of a run on the command line](https://github.com/JeffersonLab/rcdb/issues/31)
**Status: relevant · Difficulty: easy · Risk: low.**
Condition names exist (`run_start_time`, `run_end_time`, `run_length` in `python/rcdb/__init__.py:94-96`) and start/end are also `Run` columns (`started`/`finished` in `model.py`), but there's no dedicated CLI command and start/end live on the `Run` object rather than as conditions, so `rcdb select` doesn't surface them cleanly. Easy enhancement (add to `cli/info.py` or a `run` subcommand). Low risk.

### [#38 — Filling out evio_last_file / evio_files_count](https://github.com/JeffersonLab/rcdb/issues/38)
**Status: data-gap.** Backfill request for 2016 runs. Flagged; no code action.

### [#40 — Wrong run end time for Run 11363](https://github.com/JeffersonLab/rcdb/issues/40)
**Status: data-gap.** Single bad value. Flagged.

### [#42 — Offline comments](https://github.com/JeffersonLab/rcdb/issues/42)
**Status: enhancement · Difficulty: medium · Risk: medium.**
Requests a writable post-run comment field. Can be modeled as a condition or a new column; touches schema + web + write path, so non-trivial. Not a data-gap because it needs a new mechanism.

### [#44 — Store more configuration files](https://github.com/JeffersonLab/rcdb/issues/44)
**Status: data-gap / enhancement.** Archiving covers FADC250 `*_COM_DIR/_USER_DIR` files via `python/halld_rcdb/roc_config_finder.py` / `python/daq/update_roc.py`; "more files" is mostly an ops/coverage request. Flagged.

### [#46 — Warnings when including rcdb.h](https://github.com/JeffersonLab/rcdb/issues/46)
**Status: needs-info.** There is no `rcdb.h`; the public header is `cpp/include/RCDB/Connection.h`. The original `rcdb_warnings.txt` attachment is the only specifics and is stale (2016). Likely overlaps with #120. Recommend closing or asking for current output.

### [#47 — JS/JSON API for querying RCDB](https://github.com/JeffersonLab/rcdb/issues/47)
**Status: enhancement · Difficulty: medium · Risk: low.**
The web app has only HTML routes plus an elog proxy (`python/rcdb/web/modules/runs.py`); no JSON query endpoint exists. Could wrap `select_values` in a `jsonify` route. Additive, low risk.

### [#49 — CI for RCDB?](https://github.com/JeffersonLab/rcdb/issues/49)
**Status: not relevant (done).** `.github/workflows/` has python-tests, python-examples, cpp-tests, cpp-examples, cli-smoke, lint-pyflakes, documentation. Closeable.

### [#50 — RCDB 2 ROOT](https://github.com/JeffersonLab/rcdb/issues/50)
**Status: enhancement · Difficulty: medium · Risk: low.** No ROOT export today. New optional feature (needs ROOT dependency); additive.

### [#56 — Indexing common queries](https://github.com/JeffersonLab/rcdb/issues/56)
**Status: enhancement · Difficulty: medium · Risk: medium.** Performance work; alias queries (`@is_production`) are evaluated in Python per-run (`provider.py` select loop), so real speedups touch the query model / schema indexes. Risk to query semantics — careful work.

### [#57 — Run dependence for condition queries](https://github.com/JeffersonLab/rcdb/issues/57)
**Status: enhancement · Difficulty: medium · Risk: medium.** Wants run-range-dependent aliases. Aliases live in `python/rcdb/alias.py` as static expressions; adding run-dependence changes alias semantics (shared by CLI/web/API).

### [#60 — Add DAC settings ROCPS1 ROCPS2](https://github.com/JeffersonLab/rcdb/issues/60)
**Status: data-gap / enhancement.** No `rocps1/rocps2` handling in `roc_config_finder.py`; the PS section exists but those specific FADC files aren't discovered. Adding patterns is a small parser change but is fundamentally about capturing more data. Flagged.

### [#62 — Using RCDB with an SQLite file (C++)](https://github.com/JeffersonLab/rcdb/issues/62)
**Status: partially relevant · Difficulty: medium · Risk: medium.**
SQLite support is still gated behind `#ifdef RCDB_SQLITE` (`cpp/include/RCDB/Connection.h`), so downstream code (mcsmear) must be compiled with `-DRCDB_SQLITE` — the core complaint persists. The original v0.02 compile error is obsolete. Making SQLite always-on would change the build/link contract for all C++ consumers (medium risk). Overlaps with #122.

### [#72 — GlueX run 40968 is broken](https://github.com/JeffersonLab/rcdb/issues/72)
**Status: data-gap.** Bad/empty rtvs json for one run. Flagged.

### [#78 — Problems with GlueX runs 30787/30788](https://github.com/JeffersonLab/rcdb/issues/78)
**Status: data-gap.** Broken file links in data. Flagged.

### [#83 — Lots of entries missing for run 61445](https://github.com/JeffersonLab/rcdb/issues/83)
**Status: data-gap.** Missing per-run data. Flagged.

### [#84 — 'EMPTY' in target_type crashes for 50000-59999](https://github.com/JeffersonLab/rcdb/issues/84)
**Status: FIXED / not relevant (verified).** Same mechanism as #22, verified through the `rcdb select` CLI via `uv` (no-match analog of `'EMPTY' in target_type`):

```console
$ env RCDB_CONNECTION="sqlite:////tmp/rcdb_triage.sqlite" uv run rcdb select "'ZZZ' in d"
┏━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ run_num ┃ event_count ┃ run_config ┃
┡━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
└─────────┴─────────────┴────────────┘
$ echo $status
0
```

Exit **0**, empty table, no crash. The range-dependent behaviour in the original report was a data artifact (some 50000-59999 runs carrying a NULL-valued `target_type` row vs. absent rows in 40000-49999); the query idiom `target_type and 'EMPTY' in target_type` covers it and the website degrades gracefully. No code fix needed — any remaining concern is data only.

### [#86 — Having the community fix RCDB data errors](https://github.com/JeffersonLab/rcdb/issues/86)
**Status: enhancement (process) · Difficulty: medium · Risk: low.** Asks for tooling/instructions to let users correct data. Docs + a guarded edit path; not a single code fix.

### [#90 — ToTime() in C++ returns epoch 1970](https://github.com/JeffersonLab/rcdb/issues/90)
**Status: relevant (confirmed bug) · Difficulty: easy · Risk: low.**
For `ValueTypes::Time`, the providers null-check `time_column` (5) but then read `int_column` (3): `cpp/include/RCDB/SqLiteProvider.h:116-119` and `:210-213`, and `MySqlProvider.h:140-142` (`stoul(row[int_column])`). The int value is null/0 for a time condition → `from_time_t(0)` → 1970. Fix: read `time_column`. Localized; low risk (currently always-wrong for time conditions).

### [#93 — Request for prestart time](https://github.com/JeffersonLab/rcdb/issues/93)
**Status: data-gap / enhancement.** Needs a new value recorded at fill time (CODA parser). Flagged.

### [#96 — Error in top search field](https://github.com/JeffersonLab/rcdb/issues/96)
**Status: FIXED (local) — friendly redirect + `None` guard; no remaining 500 path.**
A bare run number/range typed into the **query box** (the right `q` box; e.g. `GET /runs/search?q=2-3`) genuinely still broke: `select_runs` returns `None` for a name-less query, then `len(result.runs)` throws `AttributeError` *after* the handler's `try/except`, so it was uncaught → 500. This matches the original 2022 wording ("put in the top-right box… should go in the left box"). The pre-existing two-box layout (`rr` left / `q` right, `web/templates/layouts/base.html:82-83,99`) and the empty-query redirect did **not** cover this case.

**Fix** (`web/modules/runs.py`), two complementary guards:
1. Before treating the text as a condition query, detect a bare run number/range via the existing `_parse_run_range` helper; if matched, flash a hint that run numbers/ranges go in the left box and redirect to the runs they meant (range view or single-run info).
2. After `select_runs`, guard against it returning `None` (which it does for *any* query that references no known condition — e.g. a name-less expression like `2+3`): flash a friendly hint and redirect instead of falling through to `len(result.runs)`. This closes the whole `AttributeError` → 500 class, not just the bare run/range case.

Valid condition queries are untouched. Also tidied an orphaned `# Create pagination` comment stranded after a `return` in the `except` block.

**Verification (2026-06-16)** — Flask test client against a seeded SQLite DB, with the fix applied:

```console
$ GET /runs/search?q=2-3    -> HTTP 302  Location='/runs/2-3'      # bare range  (was 500)
$ GET /runs/search?q=2      -> HTTP 302  Location='/runs/info/2'   # bare run    (was 500)
$ GET /runs/search?q=2+3    -> HTTP 302  Location='/runs/'         # name-less expr → None guard (was 500)
$ GET /runs/search?q=a > 1  -> HTTP 200                            # real query still works
$ GET /runs/search?rr=2-3   -> HTTP 302  Location='/runs/2-3'      # original rr path still works
```

`unittest` suite: 56 passed; `pyflakes` clean.

### [#98 — evio_files_count wrong for spring 2020 runs](https://github.com/JeffersonLab/rcdb/issues/98)
**Status: data-gap.** Counts off by ~2 for many runs (likely a fill-time miscount). Flagged; if a systematic parser bug is suspected it could become a code fix, but as reported it's a data discrepancy.

### [#99 — Better error reporting on SQL schema mismatch](https://github.com/JeffersonLab/rcdb/issues/99)
**Status: FIXED (local).**
Previously `provider.py` raised `SqlSchemaVersionError` with only "version X != Y" and no guidance. **Fix** (`python/rcdb/provider.py:122-134`): the message now appends an actionable hint — if the DB schema is *older*, "Run 'rcdb db update' to migrate the database to the current schema"; if *newer*, "Update your RCDB installation to match the database." Same exception type, no API change.

**Verification (2026-06-16):** seeded an in-memory DB stamped with `SQL_SCHEMA_VERSION - 1` and exercised the check → message reads: *"SQL schema version doesn't match. Retrieved DB version is 1, required version is 2. The database schema is older than this RCDB version. Run 'rcdb db update' to migrate the database to the current schema."* `unittest` suite: 56 passed (incl. `test_sql_schema_version.py`); `pyflakes` clean.

### [#100 — rcdb db update command](https://github.com/JeffersonLab/rcdb/issues/100)
**Status: not relevant (done).** `rcdb db update` exists (`python/rcdb/cli/db.py:87-156`, v1→v2 migration). Closeable; pairs with #99.

### [#101 — Trouble accessing dates via Java API](https://github.com/JeffersonLab/rcdb/issues/101)
**Status: relevant · Difficulty: medium · Risk: medium.**
`toTime()` in `java/src/org/rcdb/model.kt:180-186` returns `java.sql.Time` (time-of-day only; no date), backed by a `java.sql.Time` field (~line 93). Fixing means returning a date-bearing type (`Timestamp`/`LocalDateTime`) — a **public Java API signature change** (medium risk for existing callers). Consider an additive `toDateTime()`.

### [#103 — Request for new tagged release](https://github.com/JeffersonLab/rcdb/issues/103)
**Status: not relevant (done).** Code is python3-only (`pyproject.toml` `requires-python = ">=3.9"`), version `2.2.10`, with v2.x tags present. Closeable.

### [#108 — Setup GitHub Actions automated tests](https://github.com/JeffersonLab/rcdb/issues/108)
**Status: not relevant (done).** Test workflows exist under `.github/workflows/`. Closeable (dup of #49).

### [#115 — Move rcdb_web to rcdb library](https://github.com/JeffersonLab/rcdb/issues/115)
**Status: not relevant (done).** The web app now lives at `python/rcdb/web/` (blueprints under `web/modules/`), inside the `rcdb` package. Closeable.

### [#118 — select_values example in the wiki crashes](https://github.com/JeffersonLab/rcdb/issues/118)
**Status: FIXED (verified).**
The SQLAlchemy "value required for bind parameter 'run_min'" error came from unbound params. Current `select_values` builds `WHERE runs.number >= :run_min AND <= :run_max` and passes `{"run_min": run_min, "run_max": run_max}` to `execute` (`python/rcdb/provider.py:~1103,1135-1142`). **Verification (2026-06-16):** `db.select_values(['a','b'], '', run_min=1, run_max=9)` on the seeded DB returned 6 rows with no bind-parameter error (a `None` value in one row was handled fine).

### [#120 — memcpy warning copying C++ objects (rapidjson)](https://github.com/JeffersonLab/rcdb/issues/120)
**Status: relevant · Difficulty: medium · Risk: low-medium.**
Warning originates in **bundled** rapidjson 1.1.0 (2015) `cpp/include/rapidjson/document.h` `SetObjectRaw` (`std::memcpy` over non-trivial members). Fix = bump the vendored rapidjson to a current release. Mechanical but a vendored-dependency swap (test C++ build/examples after). Will eventually become a hard error on newer compilers.

### [#121 — Add ECAL to DAQ config](https://github.com/JeffersonLab/rcdb/issues/121)
**Status: mostly done · Difficulty: low.**
The **active** parser (`python/halld_rcdb/run_config_parser.py`) lists `ECAL`, and `roc_config_finder.py` handles `ecal_fadc250` files. The **legacy** file the issue links to, `python/rcdb/halld_daq_config_parser.py:10-23`, still lacks ECAL — but it's only referenced by a test, not the live pipeline. Effectively addressed; optionally drop/sync the legacy parser. Low risk.

### [#122 — C++ SQLite fails for CLAS12 (no table `files_have_runs`)](https://github.com/JeffersonLab/rcdb/issues/122)
**Status: relevant · Difficulty: easy · Risk: low (PR #123 open).**
`SqLiteProvider` queries `files_have_runs` unconditionally in `_getFileQuery` / `_getFileNamesQuery` (`cpp/include/RCDB/SqLiteProvider.h:23-35`), so a DB lacking that table throws on file lookups. Fix is to tolerate a missing table (guard/empty-result). **PR [#123](https://github.com/JeffersonLab/rcdb/pull/123) already targets this** — review/merge rather than re-implement. (Aside spotted: `GetFileNames()` builds `_getFileNamesQuery` but appears to execute `_getFileQuery` near line 160 — worth confirming while in this code.)

---

## Quick-win cluster (easy + low-risk, no API/subsystem repercussions)
- **#90** — change `int_column` → `time_column` for `ValueTypes::Time` in both C++ providers.
- **#122** — merge/refine PR #123.
- **#28** — `per_page` off-by-one (`+ 1`).
- **#99** — ✅ FIXED (local): schema-mismatch message now points to `rcdb db update`.
- **#96** — ✅ FIXED (local): friendly hint/redirect for a run number/range in the query box + `None`-result guard (no 500 path left).
- **#100 / #103 / #108 / #115 / #49** — already implemented; can be closed.
