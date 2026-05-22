# Quota-Aware Data Sources

When they are installed, Tonghuashun skills and Eastmoney Miaoxiang skills can
materially improve Fangtang Radar, but they are not unlimited batch endpoints.

## Policy

- Treat Tonghuashun and Eastmoney Miaoxiang as quota-limited enhancement
  sources.
- The user noted Tonghuashun free usage is limited to about 100 calls per day.
- Eastmoney Miaoxiang also has usage limits. Do not spend calls repeatedly on
  overlapping searches.
- Preserve quota for candidate verification, story analysis, filings, research,
  hotspot context, and focused natural-language screening.
- Prefer one query that answers a focused question over several broad
  exploratory calls.

## Default Call Modes

| Mode | Use case | Behavior |
|---|---|---|
| Saver | Full-market screening and daily review | Avoid quota-limited calls during broad screening; use at most focused candidate or hotspot checks |
| Standard | Single-stock analysis and small comparisons | Query the missing high-value theme, filing, research, hotspot, or company context |
| Deep | User explicitly asks for deep research | Use more research and diagnosis calls, still avoid duplicate source overlap |

Default to saver mode for screening and standard mode for analysis.

## Tonghuashun Fit

Use Tonghuashun first when the missing information is closely tied to A-share
market language:

- Concept and theme labels.
- Hotspot reasons and event-side explanation.
- Wencai-style A-share or board natural-language screening.
- Announcements, news, reports, events, financial queries, and company
  operating context for a shortlisted stock.

Relevant Tonghuashun skill groups may include行情数据查询, 问财选A股,
问财选板块, 行业数据查询, 财务数据查询, 事件数据查询, 新闻搜索,
公告搜索, 研报搜索, 机构研究与评级查询, 公司经营数据查询, and
公司股东股本查询.

Do not use Tonghuashun to逐股补全 story fields for an unfiltered whole-market
universe.

## Eastmoney Miaoxiang Fit

Use Eastmoney Miaoxiang when the task benefits from focused research synthesis
or natural-language exploration:

- Hotspot discovery and market search.
- Industry and stock follow-up context.
- Comparable-company framing.
- Earnings commentary and first-coverage style background.
- Small-set financial or screening enhancement.
- Auxiliary single-stock diagnosis.

Relevant Eastmoney Miaoxiang skill groups may include热点发现, 金融数据,
智能选股, 市场搜索, 行业研究, 行业/个股跟踪, 业绩点评, 可比公司,
首次覆盖, and 综合诊股.

Treat diagnostic or commentary outputs as auxiliary evidence. Fangtang Radar
must still form its own market, sector, role, fundamental, story, momentum,
and capital analysis.

## Query Budget Rules

- Before using a quota-limited source, state internally what missing field or
  missing check the call should resolve.
- Reuse an earlier answer when the same stock, date, and question are already
  covered.
- For a large screen, query shortlisted sectors before shortlisted stocks when
  one sector-level call can explain many candidates.
- Stop quota expansion when the result changes color but not the analysis
  conclusion.
