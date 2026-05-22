#!/usr/bin/env python3
"""Query configured Tongdaxin RPS values from local extended-data files."""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import struct
import sys
from contextlib import redirect_stdout
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


INDEX_RECORD = struct.Struct("<H6s17sI")
DATA_RECORD = struct.Struct("<IIf")

METRICS = {
    "RPS5": ("stock", 1),
    "RPS10": ("stock", 2),
    "RPS20": ("stock", 3),
    "RPS60": ("stock", 4),
    "RPS120": ("stock", 5),
    "RPS250": ("stock", 6),
    "HY_RPS5": ("industry", 7),
    "HY_RPS10": ("industry", 8),
    "HY_RPS20": ("industry", 9),
    "HY_RPS30": ("industry", 10),
    "HY_RPS60": ("industry", 11),
    "HY_RPS120": ("industry", 12),
}
STOCK_PERIODS = {5, 10, 20, 60, 120, 250}
INDUSTRY_PERIODS = {5, 10, 20, 30, 60, 120}
SLOT_LABELS = {slot: label for label, (_, slot) in METRICS.items()}


@dataclass(frozen=True)
class ValueRow:
    code: str
    name: str | None
    scope: str
    metric: str
    slot: int
    date: int
    stored_value: float
    rps: float
    stored_records: int
    indexed_codes: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read Tongdaxin stock or industry RPS ranks from extdata files."
    )
    parser.add_argument("--scope", choices=("stock", "industry"), required=True)
    parser.add_argument(
        "--code",
        action="append",
        default=[],
        help="Six-digit stock or industry-board code. Repeat for multiple codes.",
    )
    parser.add_argument(
        "--codes",
        default="",
        help="Comma-separated stock or industry-board codes.",
    )
    parser.add_argument(
        "--stock-name",
        action="append",
        default=[],
        help="Exact A-share stock name. Repeat for multiple stock names.",
    )
    parser.add_argument(
        "--stock-names",
        default="",
        help="Comma-separated exact A-share stock names.",
    )
    parser.add_argument(
        "--code-file",
        type=Path,
        help="Text or CSV file containing codes. CSV columns may use code, stock_code, or industry_code.",
    )
    parser.add_argument(
        "--industry-name",
        action="append",
        default=[],
        help="Tongdaxin default industry-board name. Repeat for multiple names.",
    )
    parser.add_argument(
        "--industry-names",
        default="",
        help="Comma-separated Tongdaxin default industry-board names.",
    )
    parser.add_argument(
        "--metrics",
        help="Comma-separated metric labels, for example RPS5,RPS20 or HY_RPS10.",
    )
    parser.add_argument(
        "--periods",
        help="Comma-separated RPS periods. Scope maps 250 to RPS250 and 30 to HY_RPS30.",
    )
    parser.add_argument(
        "--recent",
        type=int,
        default=1,
        help="Number of latest records per metric to return. Default: 1.",
    )
    parser.add_argument(
        "--tdx-root",
        type=Path,
        help="Tongdaxin client root or T0002/extdata path.",
    )
    parser.add_argument("--wide", action="store_true", help="Print one row per code/date with metrics as columns.")
    parser.add_argument("--health", action="store_true", help="Inspect configured extdata slot health and exit.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser.parse_args()


def normalize_code(raw_code: str) -> str:
    code = raw_code.strip().upper()
    if "." in code:
        code = code.split(".", 1)[0]
    if len(code) != 6 or not code.isdigit():
        raise ValueError(f"Expected a six-digit Tongdaxin code, got {raw_code!r}.")
    return code


def split_items(raw_items: str) -> list[str]:
    return [item.strip() for item in raw_items.replace("\uff0c", ",").split(",") if item.strip()]


def unique_items(items: Iterable[str]) -> list[str]:
    unique: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item not in seen:
            unique.append(item)
            seen.add(item)
    return unique


def read_text_inputs(path: Path) -> list[str]:
    values: list[str] = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.partition("#")[0].strip()
        if line:
            values.extend(split_items(line))
    return values


def read_csv_inputs(path: Path, scope: str) -> tuple[list[str], list[str], list[str]]:
    codes: list[str] = []
    stock_names: list[str] = []
    names: list[str] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = set(reader.fieldnames or [])
        code_headers = ("code", "stock_code", "industry_code")
        stock_name_headers = ("stock_name",)
        name_headers = ("industry_name", "name")
        if not headers.intersection(code_headers + stock_name_headers + name_headers):
            handle.seek(0)
            plain_reader = csv.reader(handle)
            for row in plain_reader:
                if row and row[0].strip():
                    codes.append(row[0].strip())
            return codes, stock_names, names
        for row in reader:
            for header in code_headers:
                if row.get(header, "").strip():
                    codes.append(row[header].strip())
                    break
            if scope == "stock":
                for header in stock_name_headers:
                    if row.get(header, "").strip():
                        stock_names.append(row[header].strip())
                        break
            if scope == "industry":
                for header in name_headers:
                    if row.get(header, "").strip():
                        names.append(row[header].strip())
                        break
    return codes, stock_names, names


def read_file_inputs(path: Path, scope: str) -> tuple[list[str], list[str], list[str]]:
    path = path.expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Could not find input file {path}.")
    if path.suffix.lower() == ".csv":
        return read_csv_inputs(path, scope)
    return read_text_inputs(path), [], []


def extdata_dir_from_root(path: Path) -> Path:
    path = path.expanduser().resolve()
    candidates = (
        path,
        path / "extdata",
        path / "T0002" / "extdata",
    )
    for candidate in candidates:
        if candidate.is_dir() and (candidate / "extdata_1.idx").exists():
            return candidate
    raise FileNotFoundError(f"Could not find T0002/extdata under {path}.")


def running_tdx_roots() -> Iterable[Path]:
    try:
        import psutil  # type: ignore
    except ImportError:
        return ()

    roots: list[Path] = []
    for proc in psutil.process_iter(["name", "exe"]):
        if (proc.info.get("name") or "").lower() != "tdxw.exe":
            continue
        exe = proc.info.get("exe")
        if exe:
            roots.append(Path(exe).resolve().parent)
    return roots


def find_extdata_dir(explicit_root: Path | None) -> Path:
    if explicit_root:
        return extdata_dir_from_root(explicit_root)

    env_root = os.environ.get("TDX_ROOT")
    if env_root:
        return extdata_dir_from_root(Path(env_root))

    for root in running_tdx_roots():
        try:
            return extdata_dir_from_root(root)
        except FileNotFoundError:
            continue

    raise FileNotFoundError(
        "Could not locate Tongdaxin extdata. Start TdxW.exe, set TDX_ROOT, "
        "or pass --tdx-root."
    )


def client_root_from_extdata(extdata_dir: Path) -> Path:
    return extdata_dir.parent.parent


def load_tq(client_root: Path):
    module_dir = client_root / "PYPlugins" / "user"
    if not (module_dir / "tqcenter.py").exists():
        raise FileNotFoundError(
            f"Industry-name lookup needs PYPlugins/user/tqcenter.py under {client_root}."
        )
    sys.path.insert(0, str(module_dir))
    from tqcenter import tq  # type: ignore

    return tq


def tq_call(extdata_dir: Path, call):
    tq = load_tq(client_root_from_extdata(extdata_dir))
    with redirect_stdout(io.StringIO()):
        tq.initialize(__file__)
        try:
            return call(tq)
        finally:
            tq.close()


def stock_suffix(code: str) -> str:
    if code.startswith(("0", "1", "2", "3")):
        return f"{code}.SZ"
    return f"{code}.SH"


def stock_names_for_codes(extdata_dir: Path, codes: Sequence[str]) -> dict[str, str]:
    if not codes:
        return {}

    def fetch(tq):
        return {
            code: str(tq.get_stock_info(stock_suffix(code), ["Name"]).get("Name", "")).strip()
            for code in codes
        }

    return {code: name for code, name in tq_call(extdata_dir, fetch).items() if name}


def resolve_stock_names(extdata_dir: Path, names: Sequence[str]) -> dict[str, str]:
    if not names:
        return {}

    rows = tq_call(extdata_dir, lambda tq: tq.get_stock_list(market="5", list_type=1))
    by_name: dict[str, list[str]] = {}
    code_to_name: dict[str, str] = {}
    for row in rows:
        code = normalize_code(str(row.get("Code", "")))
        name = str(row.get("Name", "")).strip()
        if name:
            by_name.setdefault(name, []).append(code)
            code_to_name[code] = name

    selected: dict[str, str] = {}
    for name in unique_items(name.strip() for name in names if name.strip()):
        matches = by_name.get(name, [])
        if not matches:
            partial = [item for item in by_name if name in item]
            hint = f" Partial matches: {', '.join(partial[:8])}." if partial else ""
            raise ValueError(f"Unknown Tongdaxin A-share stock name {name!r}.{hint}")
        if len(matches) > 1:
            raise ValueError(f"Stock name {name!r} maps to multiple codes: {', '.join(matches)}.")
        selected[matches[0]] = code_to_name[matches[0]]
    return selected


def resolve_industry_names(extdata_dir: Path, names: Sequence[str]) -> dict[str, str]:
    if not names:
        return {}

    sector_rows = tq_call(extdata_dir, lambda tq: tq.get_stock_list(market="11", list_type=1))

    by_name: dict[str, list[str]] = {}
    code_to_name: dict[str, str] = {}
    for row in sector_rows:
        code = normalize_code(str(row.get("Code", "")))
        name = str(row.get("Name", "")).strip()
        if name:
            by_name.setdefault(name, []).append(code)
            code_to_name[code] = name

    selected: dict[str, str] = {}
    for name in unique_items(name.strip() for name in names if name.strip()):
        matches = by_name.get(name, [])
        if not matches:
            partial = [item for item in by_name if name in item]
            hint = f" Partial matches: {', '.join(partial[:8])}." if partial else ""
            raise ValueError(f"Unknown Tongdaxin default industry name {name!r}.{hint}")
        if len(matches) > 1:
            raise ValueError(f"Industry name {name!r} maps to multiple codes: {', '.join(matches)}.")
        selected[matches[0]] = code_to_name[matches[0]]
    return selected


def metrics_from_periods(scope: str, periods_arg: str | None) -> list[str]:
    if not periods_arg:
        return []
    periods: list[int] = []
    for item in split_items(periods_arg):
        try:
            periods.append(int(item))
        except ValueError as exc:
            raise ValueError(f"Invalid RPS period {item!r}.") from exc
    allowed = STOCK_PERIODS if scope == "stock" else INDUSTRY_PERIODS
    invalid = [str(period) for period in periods if period not in allowed]
    if invalid:
        raise ValueError(f"Periods not available for {scope}: {', '.join(invalid)}.")
    prefix = "RPS" if scope == "stock" else "HY_RPS"
    return [f"{prefix}{period}" for period in periods]


def select_metrics(scope: str, metrics_arg: str | None, periods_arg: str | None) -> list[tuple[str, int]]:
    if metrics_arg and periods_arg:
        raise ValueError("Use either --metrics or --periods, not both.")
    period_labels = metrics_from_periods(scope, periods_arg)
    if metrics_arg:
        labels = [item.strip().upper() for item in metrics_arg.split(",") if item.strip()]
        unknown = [label for label in labels if label not in METRICS]
        if unknown:
            raise ValueError(f"Unknown metrics: {', '.join(unknown)}.")
    elif period_labels:
        labels = period_labels
    else:
        labels = [label for label, (metric_scope, _) in METRICS.items() if metric_scope == scope]

    selected: list[tuple[str, int]] = []
    for label in labels:
        metric_scope, slot = METRICS[label]
        if metric_scope != scope:
            raise ValueError(f"Metric {label} belongs to scope {metric_scope}, not {scope}.")
        selected.append((label, slot))
    return selected


def index_entries(index_path: Path) -> list[tuple[str, int, int]]:
    entries: list[tuple[str, int, int]] = []
    offset = 0
    with index_path.open("rb") as handle:
        while True:
            raw_record = handle.read(INDEX_RECORD.size)
            if not raw_record:
                break
            if len(raw_record) != INDEX_RECORD.size:
                raise ValueError(f"Truncated index record in {index_path}.")
            _, raw_code, _, count = INDEX_RECORD.unpack(raw_record)
            code = raw_code.decode("ascii", errors="ignore").rstrip("\x00")
            entries.append((code, count, offset))
            offset += count * DATA_RECORD.size
    return entries


def slot_health(extdata_dir: Path) -> list[dict[str, object]]:
    health: list[dict[str, object]] = []
    for slot in range(1, 13):
        index_path = extdata_dir / f"extdata_{slot}.idx"
        data_path = extdata_dir / f"extdata_{slot}.dat"
        item: dict[str, object] = {
            "slot": slot,
            "metric": SLOT_LABELS[slot],
            "index_exists": index_path.exists(),
            "data_exists": data_path.exists(),
        }
        if index_path.exists() and data_path.exists():
            entries = index_entries(index_path)
            item["indexed_codes"] = len(entries)
            dates: list[int] = []
            with data_path.open("rb") as handle:
                for _, count, offset in entries:
                    if not count:
                        continue
                    handle.seek(offset + (count - 1) * DATA_RECORD.size)
                    raw_record = handle.read(DATA_RECORD.size)
                    if len(raw_record) == DATA_RECORD.size:
                        date, _, _ = DATA_RECORD.unpack(raw_record)
                        dates.append(date)
            item["latest_date"] = max(dates) if dates else None
            item["oldest_latest_date"] = min(dates) if dates else None
        health.append(item)
    return health


def print_health(health: list[dict[str, object]], extdata_dir: Path) -> None:
    print(f"extdata_dir: {extdata_dir}")
    print("slot  metric     idx  dat  latest    oldest    codes")
    print("----  ---------  ---  ---  --------  --------  -----")
    for item in health:
        print(
            f"{item['slot']:>4}  {str(item['metric']):<9}  "
            f"{'yes' if item['index_exists'] else 'no ':>3}  "
            f"{'yes' if item['data_exists'] else 'no ':>3}  "
            f"{str(item.get('latest_date', '')):<8}  "
            f"{str(item.get('oldest_latest_date', '')):<8}  "
            f"{str(item.get('indexed_codes', '')):>5}"
        )


def read_slot(
    extdata_dir: Path,
    scope: str,
    code: str,
    metric: str,
    slot: int,
    recent: int,
    name: str | None,
) -> list[ValueRow]:
    index_path = extdata_dir / f"extdata_{slot}.idx"
    data_path = extdata_dir / f"extdata_{slot}.dat"
    if not index_path.exists() or not data_path.exists():
        raise FileNotFoundError(f"Missing extdata files for slot {slot}.")

    entries = index_entries(index_path)
    indexed_codes = len(entries)
    match = next((entry for entry in entries if entry[0] == code), None)
    if not match:
        return []

    _, stored_records, offset = match
    rows_to_read = min(recent, stored_records)
    start = offset + (stored_records - rows_to_read) * DATA_RECORD.size
    rows: list[ValueRow] = []
    with data_path.open("rb") as handle:
        handle.seek(start)
        for _ in range(rows_to_read):
            raw_record = handle.read(DATA_RECORD.size)
            if len(raw_record) != DATA_RECORD.size:
                raise ValueError(f"Truncated data record in {data_path}.")
            date, _, stored_value = DATA_RECORD.unpack(raw_record)
            rows.append(
                ValueRow(
                    code=code,
                    name=name,
                    scope=scope,
                    metric=metric,
                    slot=slot,
                    date=date,
                    stored_value=float(stored_value),
                    rps=float(stored_value) / 10,
                    stored_records=stored_records,
                    indexed_codes=indexed_codes,
                )
            )
    return rows


def printable_value(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.6f}".rstrip("0").rstrip(".")


def print_table(rows: list[ValueRow], missing: list[dict[str, object]], extdata_dir: Path) -> None:
    print(f"extdata_dir: {extdata_dir}")
    show_names = any(row.name for row in rows)
    if show_names:
        print("scope     code    name          metric     slot  date        rps  stored  history  indexed")
        print("--------  ------  ------------  ---------  ----  --------  -----  ------  -------  -------")
    else:
        print("scope     code    metric     slot  date        rps  stored  history  indexed")
        print("--------  ------  ---------  ----  --------  -----  ------  -------  -------")
    for row in rows:
        prefix = f"{row.scope:<8}  {row.code:<6}  "
        if show_names:
            prefix += f"{(row.name or ''):<12}  "
        print(
            f"{prefix}{row.metric:<9}  {row.slot:>4}  {row.date:<8}  "
            f"{printable_value(row.rps):>5}  {printable_value(row.stored_value):>6}  "
            f"{row.stored_records:>6}  {row.indexed_codes:>7}"
        )
    for item in missing:
        print(
            f"missing: code={item['code']} metric={item['metric']} "
            f"slot={item['slot']}"
        )


def print_wide(rows: list[ValueRow], metrics: Sequence[tuple[str, int]], missing: list[dict[str, object]], extdata_dir: Path) -> None:
    print(f"extdata_dir: {extdata_dir}")
    metric_labels = [metric for metric, _ in metrics]
    grouped: dict[tuple[str, str | None, int], dict[str, ValueRow]] = {}
    for row in rows:
        grouped.setdefault((row.code, row.name, row.date), {})[row.metric] = row
    print("code    name          date      " + "  ".join(f"{metric:>9}" for metric in metric_labels))
    print("------  ------------  --------  " + "  ".join("-" * 9 for _ in metric_labels))
    for code, name, date in sorted(grouped):
        values = []
        for metric in metric_labels:
            row = grouped[(code, name, date)].get(metric)
            values.append(f"{printable_value(row.rps):>9}" if row else f"{'':>9}")
        print(f"{code:<6}  {(name or ''):<12}  {date:<8}  " + "  ".join(values))
    for item in missing:
        print(f"missing: code={item['code']} metric={item['metric']} slot={item['slot']}")


def main() -> int:
    args = parse_args()
    if args.recent < 1:
        raise ValueError("--recent must be at least 1.")

    extdata_dir = find_extdata_dir(args.tdx_root)
    health = slot_health(extdata_dir) if args.health else []
    if args.health:
        if args.json:
            print(json.dumps({"extdata_dir": str(extdata_dir), "health": health}, ensure_ascii=False, indent=2))
        else:
            print_health(health, extdata_dir)
        return 0

    file_codes: list[str] = []
    file_stock_names: list[str] = []
    file_names: list[str] = []
    if args.code_file:
        file_codes, file_stock_names, file_names = read_file_inputs(args.code_file, args.scope)

    raw_codes = [*args.code, *split_items(args.codes), *file_codes]
    raw_stock_names = [*args.stock_name, *split_items(args.stock_names), *file_stock_names]
    raw_names = [*args.industry_name, *split_items(args.industry_names), *file_names]
    if args.scope != "stock" and raw_stock_names:
        raise ValueError("Stock names require --scope stock.")
    if args.scope != "industry" and raw_names:
        raise ValueError("Industry names require --scope industry.")
    if not raw_codes and not raw_stock_names and not raw_names:
        raise ValueError("Provide codes, stock names, --code-file, or industry names.")

    stock_names = resolve_stock_names(extdata_dir, raw_stock_names)
    industry_names = resolve_industry_names(extdata_dir, raw_names)
    codes = unique_items([*(normalize_code(code) for code in raw_codes), *stock_names, *industry_names])
    display_names = stock_names if args.scope == "stock" else industry_names
    if args.scope == "stock":
        try:
            display_names = {**stock_names_for_codes(extdata_dir, codes), **stock_names}
        except FileNotFoundError:
            display_names = stock_names
    metrics = select_metrics(args.scope, args.metrics, args.periods)
    rows: list[ValueRow] = []
    missing: list[dict[str, object]] = []

    for code in codes:
        for metric, slot in metrics:
            slot_rows = read_slot(
                extdata_dir,
                args.scope,
                code,
                metric,
                slot,
                args.recent,
                display_names.get(code),
            )
            if slot_rows:
                rows.extend(slot_rows)
            else:
                missing.append({"code": code, "metric": metric, "slot": slot})

    if args.json:
        print(
            json.dumps(
                {
                    "extdata_dir": str(extdata_dir),
                    "resolved_stock_names": stock_names,
                    "resolved_industry_names": industry_names,
                    "rows": [asdict(row) for row in rows],
                    "missing": missing,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        if args.wide:
            print_wide(rows, metrics, missing, extdata_dir)
        else:
            print_table(rows, missing, extdata_dir)

    return 1 if missing and not rows else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
