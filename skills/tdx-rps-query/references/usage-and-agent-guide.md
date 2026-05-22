# 通达信 RPS 查询使用说明

## 功能

本 skill 查询通达信扩展数据中已经保存的 RPS 排名值：

- 个股 RPS：`RPS5`、`RPS10`、`RPS20`、`RPS60`、`RPS120`、`RPS250`
- 缺省行业板块 RPS：`HY_RPS5`、`HY_RPS10`、`HY_RPS20`、`HY_RPS30`、`HY_RPS60`、`HY_RPS120`

查询脚本读取 `T0002/extdata/extdata_<slot>.idx` 和
`T0002/extdata/extdata_<slot>.dat`。不要把直接公式调用
`EXTRS(...)` 的结果当成扩展数据排名值。

## 前置条件

1. 通达信扩展数据槽位已经按本 skill 的编号生成并刷新：
   - `1-6` 为个股 RPS
   - `7-12` 为缺省行业板块 RPS
2. 本机能访问通达信数据目录，并存在 `T0002/extdata/extdata_1.idx`
   到 `extdata_12.dat`。
3. 脚本能定位通达信根目录：
   - 优先使用运行中的 `TdxW.exe`
   - 或设置环境变量 `TDX_ROOT`
   - 或命令行传 `--tdx-root <通达信根目录>`
4. 行业名称查询还要求通达信根目录下存在
   `PYPlugins/user/tqcenter.py`，以便读取缺省行业板块名称映射。
5. Python 需要能运行标准库脚本。自动发现运行中的通达信时建议安装
   `psutil`；没有 `psutil` 时直接传 `--tdx-root`。
6. 股票名称和行业名称查询都依赖 `PYPlugins/user/tqcenter.py`。代码查询
   即使没有名称解析也可以直接读扩展数据文件。

## 基本命令

单个个股：

```powershell
python scripts/query_rps_extdata.py --scope stock --code 002371.SZ --metrics RPS5,RPS20
```

逗号分隔股票池：

```powershell
python scripts/query_rps_extdata.py --scope stock --codes 002371,600519,300750 --metrics RPS60,RPS120
```

股票名称、周期别名和宽表：

```powershell
python scripts/query_rps_extdata.py --scope stock --stock-names 贵州茅台,凯格精机,鼎泰高科 --periods 5,20,250 --wide
```

历史值：

```powershell
python scripts/query_rps_extdata.py --scope stock --code 002371 --metrics RPS5 --recent 5
```

行业板块代码：

```powershell
python scripts/query_rps_extdata.py --scope industry --code 881002 --metrics HY_RPS5,HY_RPS30
```

行业板块名称：

```powershell
python scripts/query_rps_extdata.py --scope industry --industry-names 煤炭开采,焦炭加工 --metrics HY_RPS120
```

JSON 输出：

```powershell
python scripts/query_rps_extdata.py --scope stock --codes 002371,600519 --metrics RPS5 --json
```

## 文件输入

文本文件支持一行一个代码，也支持逗号分隔：

```text
002371.SZ
600519,300750
```

CSV 个股代码列支持：

- `code`
- `stock_code`
- `stock_name`

CSV 行业输入列支持：

- `industry_code`
- `industry_name`
- `name`

调用：

```powershell
python scripts/query_rps_extdata.py --scope stock --code-file stocks.csv --metrics RPS5
python scripts/query_rps_extdata.py --scope industry --code-file industries.csv --metrics HY_RPS30
```

## 输出字段

`--json` 时重点读取：

- `rows[].code`：查询代码
- `rows[].name`：行业名称，代码查询时可能为空
- `rows[].metric`：指标名
- `rows[].slot`：扩展数据编号
- `rows[].date`：通达信数据日期
- `rows[].stored_value`：扩展数据文件中的原始排名存储值
- `rows[].rps`：本配置使用的 `stored_value / 10` 值
- `missing`：在某个扩展数据槽位中没有查到的代码和指标
- `resolved_stock_names`：股票名称解析出的股票代码映射
- `resolved_industry_names`：行业名称解析出的板块代码映射

本配置已验证原始排名值按 `0-1000` 存储。跨机器使用时，如果扩展数据
排序配置改变，先核对 `stored_value` 尺度再比较 `rps`。

## Agent 调用约定

Agent 默认使用 `--json`，这样输出可直接解析。

### Agent 任务模板

```text
Use $tdx-rps-query.
Query stock RPS for stock names 凯格精机,鼎泰高科.
Periods: 5,20,250.
Return the data date, rps, stored_value, and missing entries.
Use JSON output from scripts/query_rps_extdata.py.
```

### Agent 命令模板

个股：

```powershell
python <skill-dir>\scripts\query_rps_extdata.py --scope stock --codes <codes> --metrics <RPS metrics> --json
```

股票名称：

```powershell
python <skill-dir>\scripts\query_rps_extdata.py --scope stock --stock-names <exact stock names> --periods <periods> --json
```

行业：

```powershell
python <skill-dir>\scripts\query_rps_extdata.py --scope industry --industry-names <exact Tongdaxin names> --metrics <HY_RPS metrics> --json
```

### Agent 处理规则

1. 个股指标只配 `--scope stock`。
2. `HY_RPS` 指标只配 `--scope industry`。
3. 行业名称必须使用通达信缺省行业板块的精确名称；报错时读取提示后重试。
4. `missing` 非空时向用户说明缺失槽位，不补造结果。
5. 报告日期时使用 `rows[].date`，不要假设数据一定是今天。
6. 需要稳定定位目录时显式传 `--tdx-root`。
7. 对人展示批量结果时可用 `--wide`；机器解析仍用 `--json`。

## 健康检查

检查 12 个扩展数据槽位是否存在、最新日期是否一致：

```powershell
python scripts/query_rps_extdata.py --scope stock --health
python scripts/query_rps_extdata.py --scope stock --health --json
```

`--health` 会返回每个槽位的指标名、文件存在状态、索引代码数、
最新日期和该槽位中最旧的最近日期。

## 验证

执行 smoke test：

```powershell
python scripts/smoke_test_rps_extdata.py --repeat 3
```

它会覆盖：

- 单个代码、重复 `--code`、逗号代码串
- 文本文件和 CSV 文件
- 行业代码和行业名称解析
- JSON 解析
- 缺失代码、指标与 scope 不匹配、缺少输入
