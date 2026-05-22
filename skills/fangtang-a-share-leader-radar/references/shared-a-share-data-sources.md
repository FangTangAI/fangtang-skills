# Shared A-Share Data Sources

Use shared public sources as bounded fallbacks or focused supplements. Do not
let a fallback list override the primary Fangtang route.

## Public Source Map

The A-share full-stack toolkit references these useful public paths:

| Need | Public-source examples | Fangtang use |
|---|---|---|
| Public行情 and quote supplements | mootdx, Tencent Finance, Baidu K-line | Fallback行情, K-line, valuation-adjacent quote fields |
| Research and consensus supplements | Eastmoney report APIs, Tonghuashun consensus, iwencai report search | Focused research and expectation checks |
| Theme and signal supplements | Tonghuashun hotspot reason tags, Baidu concept attribution, Eastmoney 龙虎榜 and解禁 data | Story-side and candidate verification |
| Capital and ownership supplements | Eastmoney data center and push2-style资金流 fields | Auxiliary capital and筹码 checks |
| News | Eastmoney news, CLS, market news sources | Timely context, not standalone fact proof |
| Financial and F10 supplements | mootdx finance/F10, Eastmoney basic information, Sina financial statements | Fundamental fallback fields |
| Announcements | cninfo and company filings | Authoritative fact verification |

## Known Guardrails

- Public interfaces can change. State the source and failure mode when a
  fallback fails.
- The toolkit notes that the Tonghuashun industry-board summary path was
  replaced by Eastmoney industry-board ranking after anti-bot behavior changed.
- The toolkit notes that iwencai semantic search requires its authentication
  headers or key flow.
- Theme reason tags and research commentary are not substitutes for disclosed
  company facts.
- Fund-flow labels are source-specific. Treat them as auxiliary evidence beside
  amount, turnover, price-volume behavior, and sector concentration.

## Selection Rule

Use a shared public source when at least one is true:

1. The routed source is unavailable.
2. The user asks for a field that the public source directly exposes better.
3. The analysis needs a public filing, announcement, or public market fact.
4. A focused fallback can resolve a material data gap without expanding the
   query surface materially.
