#!/usr/bin/env python3
"""
Analyse les logs ARTCB (logs/) — erreurs, tests, API, validations.

Usage:
  python3 scripts/analyze_logs.py
  python3 scripts/analyze_logs.py --log-dir ./logs --output rapports/068_logs_synthese.json
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG_DIR = ROOT / "logs"
PYTEST_PASSED = re.compile(r"(\d+)\s+passed")
PYTEST_FAILED = re.compile(r"(\d+)\s+failed")
ERROR_LINE = re.compile(r"\b(ERROR|CRITICAL|Exception|Traceback)\b", re.I)


def _read_text(path: Path, max_bytes: int = 2_000_000) -> str:
    try:
        data = path.read_bytes()[:max_bytes]
        return data.decode("utf-8", errors="replace")
    except OSError:
        return ""


def _parse_jsonl_api(path: Path) -> dict[str, Any]:
    levels: Counter[str] = Counter()
    modules: Counter[str] = Counter()
    errors: list[str] = []
    lines = 0
    for raw in _read_text(path).splitlines():
        if not raw.strip():
            continue
        lines += 1
        try:
            row = json.loads(raw)
        except json.JSONDecodeError:
            continue
        level = str(row.get("level", "UNKNOWN"))
        levels[level] += 1
        mod = str(row.get("module", "unknown"))
        modules[mod] += 1
        if level in ("ERROR", "CRITICAL"):
            errors.append(str(row.get("message", ""))[:200])
    return {
        "file": path.name,
        "lines": lines,
        "levels": dict(levels),
        "top_modules": modules.most_common(8),
        "errors": errors[:20],
    }


def _parse_pytest_log(path: Path) -> dict[str, Any]:
    text = _read_text(path)
    passed = sum(int(m.group(1)) for m in PYTEST_PASSED.finditer(text))
    failed = sum(int(m.group(1)) for m in PYTEST_FAILED.finditer(text))
    return {
        "file": path.name,
        "passed": passed,
        "failed": failed,
        "ok": failed == 0 and passed > 0,
    }


def _parse_validate_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"file": path.name, "ok": False, "error": "invalid json"}
    steps = data.get("steps", [])
    ok_count = sum(1 for s in steps if s.get("ok"))
    return {
        "file": path.name,
        "steps_total": len(steps),
        "steps_ok": ok_count,
        "ok": ok_count == len(steps) and len(steps) > 0,
        "conclusions": data.get("conclusions", {}),
    }


def _scan_plain_logs(log_dir: Path) -> dict[str, Any]:
    error_hits: list[dict[str, str]] = []
    for path in sorted(log_dir.glob("*.log")):
        for i, line in enumerate(_read_text(path).splitlines(), 1):
            if ERROR_LINE.search(line):
                error_hits.append({"file": path.name, "line": i, "snippet": line[:160]})
                if len(error_hits) >= 50:
                    break
    return {"error_lines": error_hits, "error_count": len(error_hits)}


def analyze_logs(log_dir: Path) -> dict[str, Any]:
    log_dir = log_dir.resolve()
    api_jsonl = sorted(log_dir.glob("*_artcb_api.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    pytest_files = sorted(
        list(log_dir.glob("pytest*.txt")) + list(log_dir.glob("tests_*.log")),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    validate_files = sorted(log_dir.glob("validate_two_nodes*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    demo_files = sorted(log_dir.glob("demo_live*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

    api_reports = [_parse_jsonl_api(p) for p in api_jsonl[:5]]
    pytest_reports = [_parse_pytest_log(p) for p in pytest_files[:8]]
    validate_reports = [_parse_validate_json(p) for p in validate_files[:3]]
    plain = _scan_plain_logs(log_dir)

    latest_pytest = pytest_reports[0] if pytest_reports else None
    latest_validate = validate_reports[0] if validate_reports else None
    total_api_errors = sum(len(r.get("errors", [])) for r in api_reports)

    recommendations: list[str] = []
    if total_api_errors > 0:
        recommendations.append("Revoir les erreurs API dans les JSONL recents.")
    if latest_pytest and not latest_pytest.get("ok"):
        recommendations.append("Corriger les tests en echec (pytest).")
    if latest_validate and not latest_validate.get("ok"):
        recommendations.append("Relancer validate_two_nodes.py --spawn.")
    if plain["error_count"] > 10:
        recommendations.append("Filtrer les fichiers .log avec le plus d'erreurs.")
    if not recommendations:
        recommendations.append("Logs stables — poursuivre monitoring periodique.")

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "log_dir": str(log_dir),
        "summary": {
            "api_jsonl_files": len(api_jsonl),
            "api_error_messages": total_api_errors,
            "latest_pytest": latest_pytest,
            "latest_validate_two_nodes": latest_validate,
            "plain_log_errors": plain["error_count"],
            "demo_runs_indexed": len(demo_files),
        },
        "api_jsonl": api_reports,
        "pytest": pytest_reports,
        "validate_two_nodes": validate_reports,
        "plain_logs": plain,
        "recommendations": recommendations,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyse des logs ARTCB")
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR)
    parser.add_argument("--output", type=Path, default=None, help="Fichier JSON de sortie")
    args = parser.parse_args()

    report = analyze_logs(args.log_dir)
    out = json.dumps(report, ensure_ascii=False, indent=2)
    print(out)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(out + "\n", encoding="utf-8")
        print(f"\nRapport ecrit: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
