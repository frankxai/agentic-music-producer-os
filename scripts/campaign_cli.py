#!/usr/bin/env python3
"""Offline campaign planning and allowlisted draft-pack export; no provider calls."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACK_FILES = (
    "scripts/campaign_cli.py",
    "docs/business-os/README.md",
    "docs/business-os/CAMPAIGN-STRATEGIES.md",
    "docs/business-os/RESEARCH-AND-LEARNING.md",
    "docs/business-os/TOOLS-AND-COSTS.md",
    "docs/business-os/AGENT-EXECUTION.md",
    "docs/business-os/CUSTOMER-EDITION.md",
    "docs/business-os/WORKSHEETS.md",
    "docs/business-os/NOTION-SCHEMA.sql",
    "docs/business-os/CHANGELOG.md",
    "docs/business-os/campaign.example.json",
    "docs/business-os/tool-quotes.json",
    "docs/business-os/template.manifest.json",
)
CATEGORIES = {"subscriptions", "production", "visuals", "distribution", "marketing", "reasoning", "reserve"}
STRATEGIES = {"single_ladder", "world_album", "performance_catalog", "scene_test", "sync_library"}


def money(value: object, label: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError(f"{label}: expected a finite non-negative number")
    return Decimal(str(value))


def count(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{label}: expected a non-negative integer")
    return value


def rounded(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def validate(plan: dict) -> None:
    if not isinstance(plan, dict) or plan.get("schema_version") != 1:
        raise ValueError("unsupported campaign schema")
    for key in ("campaign_id", "artist", "listener_promise", "primary_channel", "strategy_reason"):
        if not isinstance(plan.get(key), str) or not plan[key].strip():
            raise ValueError(f"missing {key}")
    if plan.get("production_mode") not in {"human", "hybrid", "generated"}:
        raise ValueError("production_mode must be human, hybrid or generated")
    if plan.get("strategy") not in STRATEGIES:
        raise ValueError("unknown campaign strategy")
    if plan.get("currency") != "EUR":
        raise ValueError("cost inputs must be EUR; retain foreign invoices and conversion outside this planner")
    money(plan.get("budget_cap_eur"), "budget_cap_eur")
    if plan.get("target_release_date") is not None:
        date.fromisoformat(plan["target_release_date"])
    costs = plan.get("costs")
    if not isinstance(costs, list) or not costs:
        raise ValueError("costs must contain planning allowances")
    identifiers = set()
    for item in costs:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"].strip():
            raise ValueError("cost requires a stable id")
        if item["id"] in identifiers:
            raise ValueError("duplicate cost id")
        identifiers.add(item["id"])
        if item.get("category") not in CATEGORIES:
            raise ValueError("unknown cost category")
        money(item.get("planned_eur"), item["id"])
        if item.get("actual_eur") is not None:
            money(item["actual_eur"], item["id"] + " actual")
    limits = plan.get("provider_limits")
    if not isinstance(limits, dict):
        raise ValueError("provider_limits required")
    for key in ("planned_credits", "planned_downloads"):
        count(limits.get(key), key)
    for key in ("remaining_credits", "remaining_downloads"):
        if limits.get(key) is not None:
            count(limits[key], key)
    for exp in plan.get("experiments", []):
        if not isinstance(exp, dict) or not exp.get("id") or not exp.get("hypothesis") or not exp.get("decision_rule"):
            raise ValueError("experiment requires id, hypothesis and decision_rule")
        money(exp.get("spend_cap_eur"), "experiment spend cap")
        observations = exp.get("observations")
        if observations is not None:
            if not isinstance(observations, dict) or not observations.get("source") or not observations.get("window"):
                raise ValueError("observations require source and window")
            num = count(observations.get("numerator"), "numerator")
            den = count(observations.get("denominator"), "denominator")
            if num > den:
                raise ValueError("numerator exceeds denominator")
    experiment_ids = [e["id"] for e in plan.get("experiments", [])]
    if len(set(experiment_ids)) != len(experiment_ids):
        raise ValueError("duplicate experiment id")
    marketing = sum((money(c["planned_eur"], c["id"]) for c in costs if c["category"] == "marketing"), Decimal(0))
    if sum((money(e["spend_cap_eur"], e["id"]) for e in plan.get("experiments", [])), Decimal(0)) > marketing:
        raise ValueError("experiment caps exceed the marketing allowance")


def report(plan: dict) -> dict:
    validate(plan)
    planned = sum((money(x["planned_eur"], x["id"]) for x in plan["costs"]), Decimal(0))
    known_actual = sum((money(x["actual_eur"], x["id"]) for x in plan["costs"] if x.get("actual_eur") is not None), Decimal(0))
    unknown = [x["id"] for x in plan["costs"] if x.get("actual_eur") is None]
    cap = money(plan["budget_cap_eur"], "cap")
    blockers = []
    if planned > cap:
        blockers.append("planned allowances exceed campaign cap")
    if known_actual > cap:
        blockers.append("known actual spend exceeds campaign cap")
    limits = plan["provider_limits"]
    for resource in ("credits", "downloads"):
        remaining = limits.get("remaining_" + resource)
        if remaining is None:
            blockers.append(f"remaining provider {resource} not observed")
        elif limits["planned_" + resource] > remaining:
            blockers.append(f"planned {resource} exceed observed remaining balance")
    experiments = []
    for exp in plan.get("experiments", []):
        obs = exp.get("observations")
        experiments.append({"id": exp["id"], "rate": None if obs is None or obs["denominator"] == 0 else obs["numerator"] / obs["denominator"], "denominator": None if obs is None else obs["denominator"], "decision_rule": exp["decision_rule"], "causal_claim": False})
    tasks = []
    if plan.get("target_release_date"):
        day = date.fromisoformat(plan["target_release_date"])
        for offset, task in ((-28, "internal delivery target"), (-21, "verify correct artist mapping"), (-14, "freeze approved launch assets"), (-7, "latest planned editorial pitch"), (0, "verify live destinations"), (7, "first campaign review"), (28, "mature-window review and template change proposal")):
            tasks.append({"proposed_date": (day + timedelta(days=offset)).isoformat(), "task": task})
    return {"campaign_id": plan["campaign_id"], "plan_sha256": hashlib.sha256(json.dumps(plan, sort_keys=True, allow_nan=False).encode()).hexdigest(), "planned_cash_eur": rounded(planned), "known_actual_cash_eur": rounded(known_actual), "actual_total_eur": None if unknown else rounded(known_actual), "unreconciled_cost_ids": unknown, "unallocated_cap_eur": rounded(cap - planned), "planning_blockers": blockers, "experiments": experiments, "proposed_calendar": tasks, "calendar_scheduled": False, "execution_authorized": False, "rights_verified": False, "publication_authorized": False}


def build_pack(output: Path, root: Path = ROOT) -> dict:
    """Export only fixed generic files; never accepts an artist dataset or copies a tree."""
    root = root.resolve()
    payload = {}
    for rel in PACK_FILES:
        path = root / rel
        if any(parent.is_symlink() for parent in (path, *path.parents) if parent != root and root in parent.parents) or root not in path.resolve().parents or not path.is_file():
            raise ValueError(f"missing or unsafe pack source: {rel}")
        payload[rel] = path.read_bytes()
    output = output.absolute()
    if output.suffix != ".zip":
        raise ValueError("output must be a .zip")
    # Exclusive creation protects existing customer exports; build contents before touching output.
    manifest = {"version": "0.1.0", "status": "draft_not_commercially_released", "license_state": "decision_required", "files": {k: hashlib.sha256(v).hexdigest() for k, v in payload.items()}, "contains_artist_catalog": False}
    with output.open("xb") as handle:
        try:
            with zipfile.ZipFile(handle, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
                for rel, data in sorted(payload.items()):
                    info = zipfile.ZipInfo(rel, date_time=(2026, 10, 9, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    bundle.writestr(info, data)
                bundle.writestr("PACK-RECEIPT.json", json.dumps(manifest, indent=2, sort_keys=True))
        except Exception:
            handle.close()
            output.unlink(missing_ok=True)
            raise
    return {"path": str(output), "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), **manifest}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("report")
    plan.add_argument("plan", type=Path)
    pack = sub.add_parser("build-pack")
    pack.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        result = report(json.loads(args.plan.read_text(encoding="utf-8"))) if args.command == "report" else build_pack(args.output)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f"error: {exc}\n")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
