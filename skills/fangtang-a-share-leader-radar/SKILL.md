---
name: fangtang-a-share-leader-radar
description: Analyze A-share market leadership, strong sectors, theme candidates, and individual stocks with the Fangtang A-Share Leader Radar framework. Use for single-stock analysis, multi-stock comparison, stock-pool screening, full-market screening, or sector review with TdxQuant-first routing, Tongdaxin RPS, Wind enhancement, and quota-aware A-share research sources.
---

# Fangtang A-Share Leader Radar

Use the no-data-source framework as the analysis baseline. Keep the framework
stable while selecting data sources by task size, data type, platform
availability, and query budget.

## Workflow

1. Read `references/Fangtang A-Share Leader Radar（无数据源版）v0.8.md`
   before applying the analysis framework.
2. Identify whether the task is single-stock analysis, multi-stock comparison,
   stock-pool screening, full-market screening, or sector review.
3. Read `references/data-routing.md` before choosing sources and
   `references/data-contract.md` before shaping the result. For relative
   strength, prefer `tdx-rps-query`. For data TdxQuant can provide, prefer
   TdxQuant unless the user explicitly chooses a different source.
4. For TdxQuant and RPS details, read
   `references/tdxquant-and-rps-adapter.md`. Treat TdxQuant real-time snapshots
   and quote subscriptions as optional bounded modes, not the default bulk
   screening path.
5. Before using Tonghuashun or Eastmoney Miaoxiang skills, read
   `references/quota-aware-data-sources.md`. Preserve their daily quotas for
   candidate verification, story-side analysis, and research enhancement.
6. When adapting the workflow to TdxClaw or WindClaw, read
   `references/platform-adapters.md`.
7. Follow the framework sequence: market environment, main-line sector,
   initial stock role or screening, detailed stock analysis, horizontal
   comparison, and information gaps.
8. Keep conclusions tied to the available data scope and state missing data,
   degraded sources, and mixed data dates explicitly.

## Source Priorities

- Use `tdx-rps-query` first for stock and Tongdaxin industry-board relative
  strength when it is available.
- Use TdxQuant first for available market data, K-lines, snapshots, stock
  lists, sectors, formulas, and supported financial or F10-style data.
- Use Wind as a professional enhancement source for data gaps, normalized
  financial comparisons, reference material, consensus or research context,
  and WindClaw execution paths.
- Use Tonghuashun and Eastmoney Miaoxiang skills as quota-aware enhancement
  sources. They are useful for theme language, natural-language screening,
  announcements, news, reports, hotspots, industry context, and single-stock
  research, but they are not the default whole-market batch engine.
- Use shared public A-share sources only when the routed source is unavailable,
  the task needs a public filing or public market fact, or the source provides
  a clearly stronger field for the requested check.

## Resources

- `references/Fangtang A-Share Leader Radar（无数据源版）v0.8.md`:
  platform-neutral analysis framework.
- `references/data-routing.md`: source priority rules by task and analysis
  module.
- `references/data-contract.md`: cross-platform data and output口径.
- `references/tdxquant-and-rps-adapter.md`: TdxQuant-first and RPS-first
  execution notes.
- `references/quota-aware-data-sources.md`: Tonghuashun and Eastmoney
  Miaoxiang usage policy.
- `references/platform-adapters.md`: TdxClaw and WindClaw adaptation notes.
- `references/shared-a-share-data-sources.md`: bounded public fallback map
  derived from the A-share data toolkit references.
