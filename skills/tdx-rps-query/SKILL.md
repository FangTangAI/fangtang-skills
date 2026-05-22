---
name: tdx-rps-query
description: Query Tongdaxin RPS relative-strength ranking data for A-share stocks and industry boards from the user's configured extended-data slots. Use when Codex needs Tongdaxin stock RPS5/RPS10/RPS20/RPS60/RPS120/RPS250 values, industry-board HY_RPS5/HY_RPS10/HY_RPS20/HY_RPS30/HY_RPS60/HY_RPS120 values, RPS history from local extdata files, or a repeatable RPS lookup workflow that can run in Codex, OpenClaw, or Claude Desktop.
---

# Tongdaxin RPS Query

Read the ranked values already stored by Tongdaxin extended data. Do not replace
them with a direct `EXTRS(...)` formula result when the user asks for RPS data:
the configured extended-data slots store the post-ranking values.

## Workflow

1. Confirm that the running Tongdaxin client has refreshed the configured
   extended-data slots and that `T0002/extdata` contains `extdata_1` through
   `extdata_12`.
2. Use `scripts/query_rps_extdata.py` for the lookup.
3. Use `--scope stock` for A-share stock codes and `--scope industry` for
   Tongdaxin `HYBK` industry-board codes such as `881002`.
4. Return the metric label, slot number, data date, stored rank value, and
   `rps` value emitted by the script.
5. State when the lookup used stale files, missing codes, or a slot that has not
   been refreshed.

## Quick Commands

Query all configured stock RPS slots for one stock:

```powershell
python scripts/query_rps_extdata.py --scope stock --code 002371.SZ
```

Query recent stock RPS history for selected periods:

```powershell
python scripts/query_rps_extdata.py --scope stock --code 002371 --metrics RPS5,RPS20,RPS120 --recent 5
```

Query a comma-separated stock pool:

```powershell
python scripts/query_rps_extdata.py --scope stock --codes 002371,600519,300750 --metrics RPS5,RPS20
```

Query exact stock names and period aliases:

```powershell
python scripts/query_rps_extdata.py --scope stock --stock-names 贵州茅台,凯格精机 --periods 20,250 --wide
```

Query codes from a text or CSV file:

```powershell
python scripts/query_rps_extdata.py --scope stock --code-file stocks.csv --metrics RPS60,RPS120
```

Query industry-board RPS slots:

```powershell
python scripts/query_rps_extdata.py --scope industry --code 881002 --json
```

Resolve Tongdaxin default industry names before querying `HY_RPS`:

```powershell
python scripts/query_rps_extdata.py --scope industry --industry-names 煤炭开采,焦炭加工 --metrics HY_RPS5,HY_RPS30
```

Check configured slot health:

```powershell
python scripts/query_rps_extdata.py --scope stock --health --json
```

Point the script at a client root when Tongdaxin is not running:

```powershell
python scripts/query_rps_extdata.py --tdx-root C:\Software\new_tdx_mock --scope stock --code 600519.SH
```

## Inputs

- Accept stock codes with or without suffixes, for example `600519`,
  `600519.SH`, and `000001.SZ`.
- Accept exact A-share stock names through `--stock-name`, `--stock-names`,
  or CSV `stock_name`.
- Accept repeated `--code`, comma-separated `--codes`, and `--code-file`.
- For `--code-file`, read `.txt` values separated by lines or commas. Read
  `.csv` code columns named `code`, `stock_code`, or `industry_code`; if no
  known header exists, use the first column as codes.
- Use a six-digit Tongdaxin industry-board code for `HY_RPS` lookups. If the
  user gives an industry name, pass `--industry-name` or `--industry-names`.
  A CSV industry file may use `industry_name` or `name`.
- Resolve names against the running client's default industry-board list from
  TdxQuant `get_stock_list(market="11", list_type=1)`. Use exact Tongdaxin
  industry names; partial names are returned only as error hints.
- Use `--recent N` when the user asks for history rather than only the latest
  value.
- Use `--metrics` to limit the query to named metrics from the configured map.
- Use `--periods` as the shorter period form. Do not combine `--periods` and
  `--metrics`.
- Use `--wide` for a user-facing one-row-per-code table. Prefer `--json` for
  Agent workflows.

## Output Rules

- Treat `stored_value` as the raw Tongdaxin extended-data ranking value.
- For this configuration, the daily ranking files store values on a `0-1000`
  scale. The script also returns `rps = stored_value / 10` on the usual
  `0-100` RPS scale.
- If a different extended-data ranking configuration is used, verify the stored
  scale before comparing `rps` across machines.
- Include the slot number and date so the result can be checked against the
  Tongdaxin client.
- If a code is absent from a slot, report that slot as missing rather than
  inventing a value.

## Resources

- `scripts/query_rps_extdata.py`: read the binary `extdata_*.idx` and
  `extdata_*.dat` files for the configured RPS slots.
- `scripts/smoke_test_rps_extdata.py`: run repeated positive and negative
  checks against local Tongdaxin extdata.
- `references/rps-extdata-map.md`: slot mapping, file mapping, and query notes.
- `references/usage-and-agent-guide.md`: prerequisites, file formats, JSON
  fields, and Agent command templates.
