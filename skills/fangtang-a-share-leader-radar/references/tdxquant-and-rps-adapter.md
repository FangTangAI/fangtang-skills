# TdxQuant And RPS Adapter

This adapter keeps Tongdaxin-derived market work consistent across Fangtang
execution environments.

## RPS Rule

Use `tdx-rps-query` first for relative strength when it is available.

| Scope | Preferred metrics |
|---|---|
| Stock short-term strength | `RPS5`, `RPS10`, `RPS20` |
| Stock trend strength | `RPS60`, `RPS120`, `RPS250` |
| Tongdaxin industry short-term strength | `HY_RPS5`, `HY_RPS10`, `HY_RPS20`, `HY_RPS30` |
| Tongdaxin industry trend strength | `HY_RPS60`, `HY_RPS120` |

Rules:

- Read the stored Tongdaxin extended-data ranking through the RPS skill. Do not
  silently replace it with a local涨跌幅 proxy.
- Check RPS data dates and stale slot warnings before using the values in a
  comparison.
- If RPS is unavailable, state that relative strength is degraded and label
  any price-return proxy separately.

## TdxQuant First Route

Use TdxQuant first for data it exposes reliably in the current environment:

- Historical K-line and tick data through `get_market_data`.
- Latest quote snapshot through `get_market_snapshot`.
- Stock, sector, and market lists where available.
- Formula and indicator workflows for batch screen or local Tongdaxin logic.
- Supported financial, F10, professional, or client-side reference fields
  when they satisfy the requested analysis.

Prefer the same TdxQuant date window and复权口径 across compared securities.
Handle suspended names, incomplete history, missing values, and board-specific
code formats explicitly.

## Post-Market Default

Fangtang Radar defaults to post-market analysis unless the user asks for
intraday work.

Use post-market mode for:

- Full-market screening.
- Stock-pool screening.
- Daily market and sector review.
- Multi-stock comparison where a single close-based口径 is required.

## Optional Real-Time Mode

TdxQuant does support real-time work:

- `get_market_snapshot` returns latest行情快照.
- `subscribe_hq` subscribes real-time quote updates.

Keep real-time mode bounded:

- Use snapshots for a single stock or a small shortlist when current price,
 盘口状态, amount, turnover, or limit-price context matters.
- Use subscriptions only when the user asks for monitoring or alert-style
  behavior.
- The TdxQuant reference documents a maximum of 100 subscribed names and
  recommends batching larger subscription work in groups of 50.
- Do not turn the default radar screening flow into a high-frequency monitor.

## Fit With The Framework

| Framework need | TdxQuant/RPS route |
|---|---|
| Market environment | Index trend, turnover, quote breadth proxies, strong-stock ecology where available |
| Main-line sector | Sector lists, sector行情, industry RPS, sector constituents |
| Initial stock screening | Liquidity, trading state, price-volume structure, RPS |
| Momentum analysis | K-line structure, relative strength, breakout or repair behavior |
| Capital analysis | Amount, turnover, volume expansion, price acceptance |
