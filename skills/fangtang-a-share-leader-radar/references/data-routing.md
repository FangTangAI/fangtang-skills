# Fangtang Data Routing

Use this routing layer after identifying the analysis task and before querying
sources. Keep the analysis framework independent from the data adapter.

## Routing Principles

1. Prefer a stable local or platform-native source for batch work.
2. Prefer a single relative-strength口径. Use `tdx-rps-query` first for stock
   RPS and Tongdaxin industry-board RPS when available.
3. Prefer TdxQuant for data it can provide. This includes market data, K-lines,
   latest snapshots, stock and sector lists, formula workflows, and supported
   financial or F10-style fields.
4. Use quota-limited sources after the candidate set has narrowed unless the
   user explicitly requests a deep lookup.
5. Separate market strength from story heat. A hot concept is not a strong
   sector until price, breadth, turnover, and candidate structure support it.
6. Report the data date, data source, analysis universe, degraded fields, and
   major information gaps.

## Task Routing

| Task | Default route | Enhancement route |
|---|---|---|
| Full-market screening | TdxQuant batch data plus `tdx-rps-query` | Use Tonghuashun, Eastmoney Miaoxiang, Wind, or public sources only after a candidate set exists |
| Stock-pool screening | TdxQuant and RPS over the supplied pool | Verify shortlisted stories, filings, research, and industry context with bounded enhancement calls |
| Single-stock analysis | TdxQuant, RPS, sector context | Add Tonghuashun, Eastmoney Miaoxiang, Wind, filings, and public context as needed |
| Multi-stock comparison | One consistent TdxQuant and RPS口径 across names | Add comparable-company, theme, research, and filing checks only for the comparison set |
| Sector review | TdxQuant sector data and industry RPS | Use theme/hotspot and industry-research sources to explain the move |

## Module Routing

| Framework module | Primary data route | Bounded enhancement |
|---|---|---|
| Market environment | TdxQuant index, breadth, turnover, strong-stock ecology where available | Wind and public market facts for missing fields |
| Main-line sector | TdxQuant sector behavior plus `tdx-rps-query` industry RPS | Tonghuashun theme language, Eastmoney hotspot or industry context, Wind research |
| Initial stock screening | TdxQuant batch行情, trend, turnover, liquidity, trading state plus stock RPS | Do not spend quota-limited calls on every unfiltered stock |
| Fundamental analysis | TdxQuant-supported fields first | Wind normalized financials and reference material; Tonghuashun or Eastmoney only for focused gaps |
| Story analysis | Candidate-sector and candidate-stock context | Tonghuashun first for A-share theme language when budget permits; filings and authoritative facts for verification |
| Momentum analysis | TdxQuant price-volume structure plus RPS | Wind only when local data is unavailable or a standardized comparison is needed |
| Capital analysis | TdxQuant turnover, volume, amount, and price acceptance first | Source-specific flow labels only as auxiliary evidence |

## Data-Type Priority

| Data type | Priority |
|---|---|
| Stock and industry relative strength | `tdx-rps-query` first |
| Market data, K-lines, snapshots, trading state | TdxQuant first |
| Formula or batch screen over A shares | TdxQuant first |
| Financial normalization, consensus, research reference | Wind when it adds a stronger normalized or professional field |
| Concepts, themes, hotspot reasons | Tonghuashun first when quota and scale allow |
| Hotspot discovery, research synthesis, industry and stock follow-up | Eastmoney Miaoxiang or Wind as enhancement |
| Announcements and disclosed facts | Filing source or company disclosure before commentary |
| Public fallback fields | Public toolkit sources after routed sources fail or when they expose the needed field directly |

## Scale Rules

- Whole-market and large-pool screening must complete without depending on
  quota-limited natural-language sources.
- Candidate verification may spend quota on the smallest useful set.
- Single-stock and small comparison tasks may use richer enhancement calls, but
  should still avoid duplicate searches across overlapping sources.
- If source availability changes, degrade by data type. Do not replace the
  whole framework with a new platform-specific process.
