#!/usr/bin/env python3
"""Bounded album-level Create budget and run telemetry ledger."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-") or "untitled-album"


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def _load(manifest_path: Path) -> tuple[Path, dict[str, Any]]:
    path = Path(manifest_path)
    if not path.is_file():
        raise FileNotFoundError(f"missing album manifest: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 2:
        raise ValueError("unsupported album manifest schema")
    return path, payload


def migrate_album(manifest_path: Path) -> dict[str, Any]:
    """Explicitly upgrade a legacy v1 ledger without inventing observed Create evidence.

    Version 1 recorded zero-Create status telemetry without the source/action fields
    now required by v2.  That safe subset can be normalized.  A v1 entry claiming an
    observed Create cannot be migrated because it lacks the binding fields required
    to make the observation trustworthy; preserve it and require manual review.
    """
    path = Path(manifest_path)
    if not path.is_file():
        raise FileNotFoundError(f"missing album manifest: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    version = payload.get("schema_version")
    if version == 2:
        return {"status": "already_current", "manifest_path": str(path), "manifest": payload}
    if version != 1:
        raise ValueError("only legacy album manifest schema v1 can be migrated")

    budget = payload.get("create_budget")
    reservations = payload.get("reservations")
    telemetry = payload.get("telemetry")
    if not isinstance(budget, dict) or not isinstance(reservations, list) or not isinstance(telemetry, list):
        raise ValueError("legacy album manifest has invalid budget, reservations, or telemetry")
    try:
        maximum = int(budget["maximum"])
        reserved = int(budget["reserved"])
        observed = int(budget["observed"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("legacy album manifest has invalid Create budget values") from exc
    if not 1 <= maximum <= 10 or not 0 <= observed <= reserved <= maximum:
        raise ValueError("legacy album manifest Create budget is out of bounds")
    if reserved != len(reservations):
        raise ValueError("legacy album reservation count does not match its Create budget")

    normalized_reservations: list[dict[str, Any]] = []
    track_ids: set[str] = set()
    for reservation in reservations:
        if not isinstance(reservation, dict):
            raise ValueError("legacy album reservation must be an object")
        track_id = str(reservation.get("track_id", "")).strip()
        run_id = str(reservation.get("run_id", "")).strip()
        if not track_id or not run_id or track_id in track_ids:
            raise ValueError("legacy album reservation has a missing or duplicate track/run identity")
        track_ids.add(track_id)
        normalized_reservations.append({**reservation, "track_id": track_id, "run_id": run_id, "observed_create_action_id": None})

    normalized_telemetry: list[dict[str, Any]] = []
    legacy_observed_tracks: set[str] = set()
    for index, receipt in enumerate(telemetry, start=1):
        if not isinstance(receipt, dict):
            raise ValueError("legacy album telemetry receipt must be an object")
        required = {"track_id", "role", "provider_model", "actual_usage", "unavailable_reason", "create_actions", "takes_observed", "stage"}
        missing = sorted(required - set(receipt))
        if missing:
            raise ValueError("legacy telemetry is missing fields: " + ", ".join(missing))
        track_id = str(receipt["track_id"]).strip()
        creates, takes = int(receipt["create_actions"]), int(receipt["takes_observed"])
        if track_id not in track_ids or creates not in {0, 1} or not 0 <= takes <= 2:
            raise ValueError("legacy telemetry has invalid track or Create/take count")
        if creates == 1 or takes != 0:
            legacy_observed_tracks.add(track_id)
        normalized_telemetry.append(
            {
                **receipt,
                "track_id": track_id,
                "create_action_id": None,
                "source_receipt_ref": f"legacy-schema-v1:{path.name}#telemetry:{index}",
            }
        )
    if observed or legacy_observed_tracks:
        raise RuntimeError(
            "legacy observed Create telemetry cannot be migrated without an action ID and source receipt reference"
        )

    payload["schema_version"] = 2
    payload["reservations"] = normalized_reservations
    payload["telemetry"] = normalized_telemetry
    payload.setdefault("migrations", []).append(
        {"from_schema": 1, "to_schema": 2, "migrated_at": _timestamp(), "observed_creates_migrated": 0}
    )
    _write(path, payload)
    return {"status": "migrated", "manifest_path": str(path), "manifest": payload}


def initialize_album(workspace: Path, title: str, maximum_create_actions: int = 10) -> dict[str, Any]:
    if not title.strip():
        raise ValueError("album title must not be empty")
    if maximum_create_actions < 1 or maximum_create_actions > 10:
        raise ValueError("maximum Create budget must be between 1 and 10")
    root = Path(workspace) / "albums" / _slugify(title)
    manifest_path = root / "album-manifest.json"
    if manifest_path.exists():
        raise FileExistsError(f"album manifest already exists: {manifest_path}")
    payload = {
        "schema_version": 2,
        "title": title.strip(),
        "created_at": _timestamp(),
        "create_budget": {"maximum": maximum_create_actions, "reserved": 0, "observed": 0},
        "reservations": [],
        "telemetry": [],
        "publication_authorized": False,
    }
    _write(manifest_path, payload)
    return {"status": "created", "manifest_path": str(manifest_path), "manifest": payload}


def reserve_create(manifest_path: Path, track_id: str, run_id: str) -> dict[str, Any]:
    path, payload = _load(manifest_path)
    normalized_track, normalized_run = track_id.strip(), run_id.strip()
    if not normalized_track or not normalized_run:
        raise ValueError("track_id and run_id must not be empty")
    reservations = payload["reservations"]
    if any(item["track_id"] == normalized_track for item in reservations):
        raise RuntimeError("track already has a Create reservation")
    budget = payload["create_budget"]
    if budget["reserved"] >= budget["maximum"]:
        raise RuntimeError("album maximum Create budget is exhausted")
    receipt = {
        "track_id": normalized_track,
        "run_id": normalized_run,
        "reserved_at": _timestamp(),
        "status": "reserved",
        "observed_create_action_id": None,
    }
    reservations.append(receipt)
    budget["reserved"] += 1
    _write(path, payload)
    return {**receipt, "reserved_count": budget["reserved"], "maximum": budget["maximum"]}


def record_album_telemetry(manifest_path: Path, track_id: str, telemetry: dict[str, Any]) -> dict[str, Any]:
    path, payload = _load(manifest_path)
    normalized_track = track_id.strip()
    reservation = next((item for item in payload["reservations"] if item["track_id"] == normalized_track), None)
    if reservation is None:
        raise RuntimeError("track requires a Create reservation before telemetry")
    required = {
        "role",
        "provider_model",
        "actual_usage",
        "unavailable_reason",
        "create_actions",
        "takes_observed",
        "stage",
        "create_action_id",
        "source_receipt_ref",
    }
    missing = sorted(required - set(telemetry))
    if missing:
        raise ValueError(f"telemetry missing fields: {', '.join(missing)}")
    if telemetry["actual_usage"] is not None and telemetry["unavailable_reason"]:
        raise ValueError("telemetry cannot claim both actual usage and an unavailable reason")
    if telemetry["actual_usage"] is None and not str(telemetry["unavailable_reason"]).strip():
        raise ValueError("missing actual usage requires an unavailable reason")
    if int(telemetry["create_actions"]) not in {0, 1}:
        raise ValueError("each reserved track can record zero or one Create action")
    if int(telemetry["takes_observed"]) < 0 or int(telemetry["takes_observed"]) > 2:
        raise ValueError("takes_observed must be between 0 and 2")
    if not str(telemetry["stage"]).strip():
        raise ValueError("telemetry stage must not be empty")
    action_id = telemetry["create_action_id"]
    source_ref = str(telemetry["source_receipt_ref"]).strip()
    if int(telemetry["create_actions"]) == 1:
        if not isinstance(action_id, str) or not action_id.strip() or not source_ref:
            raise ValueError("an observed Create requires create_action_id and source_receipt_ref")
        if reservation.get("observed_create_action_id") is not None:
            raise RuntimeError("track already has an observed Create action")
        reservation["observed_create_action_id"] = action_id.strip()
        reservation["observed_at"] = _timestamp()
        reservation["status"] = "create_observed"
    elif action_id is not None or telemetry["takes_observed"] != 0:
        raise ValueError("zero-Create telemetry must use create_action_id null and takes_observed 0")
    receipt = {"track_id": normalized_track, **telemetry, "recorded_at": _timestamp()}
    payload["telemetry"].append(receipt)
    payload["create_budget"]["observed"] = sum(
        1 for item in payload["reservations"] if item.get("observed_create_action_id") is not None
    )
    if payload["create_budget"]["observed"] > payload["create_budget"]["maximum"]:
        raise RuntimeError("observed Create actions exceed album maximum")
    _write(path, payload)
    return receipt


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("--workspace", type=Path, required=True)
    init.add_argument("--title", required=True)
    init.add_argument("--maximum-create-actions", type=int, default=10)
    migrate = commands.add_parser("migrate", help="Explicitly upgrade a safe legacy v1 ledger to v2")
    migrate.add_argument("manifest_path", type=Path)
    reserve = commands.add_parser("reserve-create")
    reserve.add_argument("manifest_path", type=Path)
    reserve.add_argument("--track-id", required=True)
    reserve.add_argument("--run-id", required=True)
    telemetry = commands.add_parser("record-telemetry")
    telemetry.add_argument("manifest_path", type=Path)
    telemetry.add_argument("--track-id", required=True)
    telemetry.add_argument("--telemetry-json", required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "init":
        result = initialize_album(args.workspace, args.title, args.maximum_create_actions)
    elif args.command == "migrate":
        result = migrate_album(args.manifest_path)
    elif args.command == "reserve-create":
        result = reserve_create(args.manifest_path, args.track_id, args.run_id)
    else:
        payload = json.loads(args.telemetry_json)
        if not isinstance(payload, dict):
            raise ValueError("--telemetry-json must be an object")
        result = record_album_telemetry(args.manifest_path, args.track_id, payload)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
