#!/usr/bin/env python3
"""Run repeatable smoke tests for query_rps_extdata.py against local Tongdaxin data."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).with_name("query_rps_extdata.py")
STOCK_CODES = ("002371.SZ", "600519.SH", "300750.SZ")
STOCK_NAMES = ("\u8d35\u5dde\u8305\u53f0", "\u51ef\u683c\u7cbe\u673a", "\u9f0e\u6cf0\u9ad8\u79d1")
INDUSTRY_NAMES = ("\u7164\u70ad\u5f00\u91c7", "\u7126\u70ad\u52a0\u5de5")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke-test Tongdaxin RPS query inputs.")
    parser.add_argument("--tdx-root", type=Path, help="Tongdaxin client root if auto-detection is unavailable.")
    parser.add_argument("--repeat", type=int, default=3, help="Repeat positive query cases. Default: 3.")
    return parser.parse_args()


def run_case(name: str, args: list[str], expected_returncode: int = 0) -> dict:
    command = [sys.executable, str(SCRIPT), *args]
    child_env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=child_env,
    )
    result = {
        "name": name,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }
    if completed.returncode != expected_returncode:
        raise AssertionError(
            f"{name} returned {completed.returncode}, expected {expected_returncode}.\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return result


def json_case(name: str, args: list[str], minimum_rows: int = 1) -> dict:
    result = run_case(name, [*args, "--json"])
    payload = json.loads(result["stdout"])
    if len(payload["rows"]) < minimum_rows:
        raise AssertionError(f"{name} returned {len(payload['rows'])} rows, expected at least {minimum_rows}.")
    if payload["missing"]:
        raise AssertionError(f"{name} returned unexpected missing entries: {payload['missing']}.")
    return payload


def add_root(args: list[str], root: Path | None) -> list[str]:
    return [*args, "--tdx-root", str(root)] if root else args


def positive_cases(root: Path | None, temp_dir: Path) -> None:
    stock_text = temp_dir / "stocks.txt"
    stock_text.write_text(f"{STOCK_CODES[0]},{STOCK_CODES[1]}\n{STOCK_CODES[2]}\n", encoding="utf-8")
    stock_csv = temp_dir / "stocks.csv"
    stock_csv.write_text(f"stock_code\n{STOCK_CODES[0]}\n{STOCK_CODES[1]}\n", encoding="utf-8")
    stock_name_csv = temp_dir / "stock_names.csv"
    stock_name_csv.write_text(f"stock_name\n{STOCK_NAMES[0]}\n{STOCK_NAMES[1]}\n", encoding="utf-8")
    industry_csv = temp_dir / "industries.csv"
    industry_csv.write_text(
        f"industry_name\n{INDUSTRY_NAMES[0]}\n{INDUSTRY_NAMES[1]}\n",
        encoding="utf-8",
    )

    json_case(
        "single-stock-code",
        add_root(["--scope", "stock", "--code", STOCK_CODES[0], "--metrics", "RPS5,RPS20"], root),
        minimum_rows=2,
    )
    json_case(
        "repeated-stock-code",
        add_root(
            [
                "--scope",
                "stock",
                "--code",
                STOCK_CODES[0],
                "--code",
                STOCK_CODES[1],
                "--metrics",
                "RPS60",
            ],
            root,
        ),
        minimum_rows=2,
    )
    json_case(
        "comma-stock-codes",
        add_root(
            ["--scope", "stock", "--codes", f"{STOCK_CODES[0]}\uff0c{STOCK_CODES[1]}", "--metrics", "RPS120"],
            root,
        ),
        minimum_rows=2,
    )
    json_case(
        "text-code-file",
        add_root(["--scope", "stock", "--code-file", str(stock_text), "--metrics", "RPS250"], root),
        minimum_rows=3,
    )
    json_case(
        "csv-code-file",
        add_root(["--scope", "stock", "--code-file", str(stock_csv), "--metrics", "RPS10"], root),
        minimum_rows=2,
    )
    names_payload = json_case(
        "stock-names-periods",
        add_root(
            ["--scope", "stock", "--stock-names", ",".join(STOCK_NAMES), "--periods", "5,250"],
            root,
        ),
        minimum_rows=6,
    )
    if set(names_payload["resolved_stock_names"].values()) != set(STOCK_NAMES):
        raise AssertionError("stock-names did not resolve the expected Tongdaxin stock names.")
    json_case(
        "stock-name-csv",
        add_root(["--scope", "stock", "--code-file", str(stock_name_csv), "--periods", "20"], root),
        minimum_rows=2,
    )
    wide = run_case(
        "wide-stock-output",
        add_root(["--scope", "stock", "--stock-names", ",".join(STOCK_NAMES[:2]), "--periods", "250", "--wide"], root),
    )
    if "RPS250" not in wide["stdout"] or STOCK_NAMES[0] not in wide["stdout"]:
        raise AssertionError("wide-stock-output did not include the expected stock name and metric.")
    json_case(
        "industry-code",
        add_root(["--scope", "industry", "--code", "881002", "--metrics", "HY_RPS5,HY_RPS30"], root),
        minimum_rows=2,
    )
    names_payload = json_case(
        "industry-names",
        add_root(
            [
                "--scope",
                "industry",
                "--industry-names",
                ",".join(INDUSTRY_NAMES),
                "--metrics",
                "HY_RPS120",
            ],
            root,
        ),
        minimum_rows=2,
    )
    if set(names_payload["resolved_industry_names"].values()) != set(INDUSTRY_NAMES):
        raise AssertionError("industry-names did not resolve the expected Tongdaxin industry names.")
    json_case(
        "industry-csv-names",
        add_root(["--scope", "industry", "--code-file", str(industry_csv), "--metrics", "HY_RPS10"], root),
        minimum_rows=2,
    )
    health_payload = run_case("health-json", add_root(["--scope", "stock", "--health", "--json"], root))
    if len(json.loads(health_payload["stdout"])["health"]) != 12:
        raise AssertionError("health-json did not return all configured slots.")


def negative_cases(root: Path | None) -> None:
    run_case(
        "missing-stock-code",
        add_root(["--scope", "stock", "--code", "999999", "--metrics", "RPS5", "--json"], root),
        expected_returncode=1,
    )
    run_case(
        "metric-scope-mismatch",
        add_root(["--scope", "stock", "--code", STOCK_CODES[0], "--metrics", "HY_RPS5"], root),
        expected_returncode=2,
    )
    run_case(
        "missing-input",
        add_root(["--scope", "stock"], root),
        expected_returncode=2,
    )
    run_case(
        "mixed-metrics-periods",
        add_root(["--scope", "stock", "--code", STOCK_CODES[0], "--metrics", "RPS5", "--periods", "5"], root),
        expected_returncode=2,
    )


def main() -> int:
    args = parse_args()
    if args.repeat < 1:
        raise ValueError("--repeat must be at least 1.")
    with tempfile.TemporaryDirectory(prefix="tdx-rps-smoke-") as raw_temp_dir:
        temp_dir = Path(raw_temp_dir)
        for iteration in range(1, args.repeat + 1):
            positive_cases(args.tdx_root, temp_dir)
            print(f"positive iteration {iteration}/{args.repeat}: ok")
        negative_cases(args.tdx_root)
    print("negative cases: ok")
    print("tdx-rps smoke tests: ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"smoke test failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
