# RPS Extended-Data Map

The user configured these Tongdaxin extended-data slots:

| Slot | Metric | Scope | Source expression | Ranking target |
| --- | --- | --- | --- | --- |
| 1 | `RPS5` | Stock | `EXTRS(5)` | Daily rank |
| 2 | `RPS10` | Stock | `EXTRS(10)` | Daily rank |
| 3 | `RPS20` | Stock | `EXTRS(20)` | Daily rank |
| 4 | `RPS60` | Stock | `EXTRS(60)` | Daily rank |
| 5 | `RPS120` | Stock | `EXTRS(120)` | Daily rank |
| 6 | `RPS250` | Stock | `EXTRS(250)` | Daily rank |
| 7 | `HY_RPS5` | Industry board | `EXTRS(5)` | Daily rank |
| 8 | `HY_RPS10` | Industry board | `EXTRS(10)` | Daily rank |
| 9 | `HY_RPS20` | Industry board | `EXTRS(20)` | Daily rank |
| 10 | `HY_RPS30` | Industry board | `EXTRS(30)` | Daily rank |
| 11 | `HY_RPS60` | Industry board | `EXTRS(60)` | Daily rank |
| 12 | `HY_RPS120` | Industry board | `EXTRS(120)` | Daily rank |

## Local Files

Each slot is stored under the Tongdaxin client data folder:

- Index file: `T0002/extdata/extdata_<slot>.idx`
- Data file: `T0002/extdata/extdata_<slot>.dat`

The index stores fixed-width code entries and record counts. The data file stores
date/value records for each indexed code.

In the tested configuration, the saved daily ranking values span `0` through
`1000`. The query script preserves that raw `stored_value` and also emits
`rps = stored_value / 10`.

## Scope Notes

- Slots `1` through `6` are stock RPS ranking data.
- Slots `7` through `12` are industry-board RPS ranking data from `HYBK`.
- Industry rows use board codes such as `881002`, not stock codes.
- Industry names are resolved from the client's default industry-board list:
  TdxQuant `get_stock_list(market="11", list_type=1)`.
- Direct formula calls to `EXTRS(...)` are useful for diagnostics but return the
  source formula series, not the extended-data rank value stored by these slots.
