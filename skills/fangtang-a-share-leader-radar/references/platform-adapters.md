# Platform Adapters

Keep one Fangtang Radar framework. Adapt the source route to the execution
platform without forking the analysis logic.

## TdxClaw

Use the Tongdaxin route as the default:

1. Prefer TdxQuant and available TdxClaw Tongdaxin tools for market data,
   sector data, K-lines, quotes, local formulas, F10, and batch screening.
2. Prefer `tdx-rps-query` for stock and Tongdaxin industry-board relative
   strength.
3. Use quota-aware Tonghuashun or Eastmoney Miaoxiang skills for stories,
   concept language, hotspot context, reports, announcements, and focused
   natural-language screening only after the scale rule allows it.
4. Use public A-share fallback fields when Tongdaxin-side or installed skills
   do not expose the required field.

The older TdxClaw Fangtang draft is useful for concrete Tongdaxin tool mapping,
but its process should follow this skill's framework and routing rules.

## WindClaw

Use the same framework with Wind as an enhancement and fallback platform:

1. Still prefer `tdx-rps-query` for RPS when it is available.
2. Still prefer TdxQuant for data TdxQuant can provide when the environment has
   access to it.
3. Use Wind for normalized financial comparisons, professional reference
   content, research context, Wind-side data access, and fields unavailable or
   weaker in the Tongdaxin route.
4. Keep Wind web or document searches focused. Prefer authoritative filing or
   company facts when a conclusion depends on a disclosed event.

The WindClaw variant should not silently redefine relative strength or replace
the A-share screening底座 merely because Wind tools exist.

## Cross-Platform Output Contract

Every platform output should preserve:

- Task type and analysis universe.
- Data date and mixed-date warnings.
- Source route used for market, sector, stock, RPS, financial, story, and
  capital checks.
- Data gaps and downgraded proxies.
- The framework result: market condition, main-line sector strength, stock
  role, four-side analysis, horizontal comparison where applicable, and
  confidence boundary.
