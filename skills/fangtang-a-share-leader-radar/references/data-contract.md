# Fangtang Data Contract

Use this contract to keep Fangtang Radar outputs comparable across TdxClaw,
WindClaw, installed research skills, and public fallbacks.

## Required Header

Every non-trivial analysis should state:

| Field | Requirement |
|---|---|
| Task type | Single stock, multi-stock comparison, stock-pool screening, full-market screening, or sector review |
| Analysis universe | Named stocks, supplied pool, selected sector, or whole-market scope |
| Data dates | Market date, financial reporting date, filing/event cutoff where they differ |
| Source route | Primary and enhancement sources actually used |
| Query mode | Post-market by default; real-time only when used |
| Gaps | Missing, degraded, stale, quota-limited, or proxy-based checks |

## Minimum Evidence By Module

| Module | Minimum evidence before a firm conclusion |
|---|---|
| Market environment | Index or market-trend context plus market participation or short-line ecology evidence |
| Main-line sector | Sector price-strength evidence plus breadth, turnover, candidate structure, or supported theme evidence |
| Initial stock screening | Trading state, liquidity or amount, price-volume strength, and stock/sector context |
| Fundamental analysis | Reported business or financial evidence; label缺口 when only story evidence exists |
| Story analysis | Theme or catalyst context plus verification boundary for disclosed facts |
| Momentum analysis | Price-volume structure plus RPS when available |
| Capital analysis | Amount, turnover, acceptance, or source-labeled capital evidence |

## Relative Strength Contract

- Label direct Tongdaxin RPS as RPS and include the period.
- Label any substitute return comparison as a proxy, not RPS.
- Do not compare RPS values from different口径 without explanation.

## Source Contract

- Name a source only when it was actually used.
- Separate authoritative facts, market data, natural-language search results,
  research commentary, and model diagnosis.
- When data sources disagree, prefer the source closest to the disclosed fact
  or raw market record and state the disagreement if it matters.
- Do not invent a missing field to complete a table.

## Result Contract

Keep the framework result visible:

1. Market condition and its constraint on the analysis.
2. Main-line sector or theme strength.
3. Stock role or shortlist status.
4. Fundamental, story, momentum, and capital findings.
5. Horizontal comparison and candidate layer where applicable.
6. Information gaps and confidence boundary.
