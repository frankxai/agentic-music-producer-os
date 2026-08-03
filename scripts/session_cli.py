#!/usr/bin/env python3
"""Create and verify durable music-production session records."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

VALID_KINDS = {"song", "meditation", "instrumental"}
REVIEW_AXIS_NAMES = (
    "emotional_thesis",
    "originality",
    "imagery_specificity",
    "prosody_singability",
    "section_contrast",
    "hook_strength",
    "arrangement_fidelity",
    "release_readiness",
)
PRODUCTION_ARTIFACTS = {
    "composition-map.md": ("tempo", "tonal", "form", "energy", "negative", "ending"),
    "vocal-casting.md": ("no-clone",),
    "audiovisual-hook-board.md": ("lyric nucleus", "drop/reveal nucleus", "atmosphere nucleus"),
}
DOWNLOAD_DECISIONS = {"KEEP", "ITERATE", "CUT"}
RELEASE_DECISIONS = {"RETAIN", "REJECT"}
PRIVATE_RIGHTS_STATES = {"private_unpublished", "rights_hold"}
EMPTY_MARKERS = {"", "todo", "tbd", "[todo]", "<!-- write here -->"}
IMITATION_PATTERNS = (
    r"\bin the style of\b",
    r"\bsounds? like\b",
    r"\b(?:clone|copy|imitate)\b.{0,24}\bvoice\b",
    r"\bvoice of\b",
)
MEDITATION_VETO_PATTERNS = (
    r"\bhold your breath\b",
    r"\b(?:heal|release)(?:s|ing)? (?:your )?trauma\b",
    r"\breset(?:s|ting)? (?:your |the )?nervous system\b",
    r"\brepair(?:s|ing)? (?:your )?dna\b",
    r"\bthis frequency heal(?:s|ing)?\b",
    r"\byou are safe\b",
    r"\byou will (?:now )?feel calm\b",
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug[:64] or "untitled"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact_hashes(session_dir: Path, kind: str) -> dict[str, str]:
    names = [
        "brief.md",
        "style-prompt.md",
        "review.md",
        "composition-map.md",
        "vocal-casting.md",
        "audiovisual-hook-board.md",
    ]
    if kind == "song":
        names.append("lyrics.md")
    elif kind == "meditation":
        names.append("script.md")
    return {
        name: _sha256_text((session_dir / name).read_text(encoding="utf-8"))
        for name in names
    }


def _append_event(
    manifest: dict[str, Any], event_type: str, payload: dict[str, Any], at: str
) -> dict[str, Any]:
    events = manifest.setdefault("events", [])
    if not isinstance(events, list):
        raise ValueError("manifest events must be a list")
    previous_hash = str(events[-1].get("event_hash", "")) if events else ""
    material = {
        "sequence": len(events) + 1,
        "type": event_type,
        "at": at,
        "previous_hash": previous_hash,
        "payload": payload,
    }
    event = {**material, "event_hash": _sha256_text(json.dumps(material, sort_keys=True))}
    events.append(event)
    return event


def _verify_event_chain(manifest: dict[str, Any]) -> None:
    events = manifest.get("events", [])
    if not isinstance(events, list):
        raise ValueError("manifest events must be a list")
    previous_hash = ""
    for sequence, event in enumerate(events, start=1):
        material = {
            "sequence": sequence,
            "type": event.get("type"),
            "at": event.get("at"),
            "previous_hash": previous_hash,
            "payload": event.get("payload"),
        }
        expected_hash = _sha256_text(json.dumps(material, sort_keys=True))
        if event.get("event_hash") != expected_hash:
            raise RuntimeError("local event log integrity check failed")
        previous_hash = expected_hash


def _load_manifest(session_dir: Path) -> tuple[Path, dict[str, Any]]:
    manifest_path = Path(session_dir) / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"missing manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _verify_event_chain(manifest)
    return manifest_path, manifest


def _timestamp(now: datetime | None = None) -> str:
    value = now or _utc_now()
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def _require_ready(session_dir: Path) -> None:
    readiness = validate_session(session_dir)
    if not readiness["ready_for_suno"]:
        raise RuntimeError(
            "session is not ready for Suno: "
            + "; ".join([*readiness["missing"], *readiness["errors"]])
        )


def _authorization_for(manifest: dict[str, Any], authorization_id: str) -> dict[str, Any]:
    authorizations = manifest.setdefault("create_authorizations", [])
    if not isinstance(authorizations, list):
        raise ValueError("manifest create_authorizations must be a list")
    authorization = next(
        (item for item in authorizations if str(item.get("id", "")).strip() == authorization_id),
        None,
    )
    if authorization is None:
        raise RuntimeError("Create authorization is missing")
    return authorization


def _require_authorization_preflight(
    session_dir: Path, manifest: dict[str, Any], authorization_id: str
) -> dict[str, Any]:
    authorization = _authorization_for(manifest, authorization_id)
    if authorization.get("status") != "preflighted":
        raise RuntimeError("Create authorization must be preflighted before one Create submission")
    if authorization.get("artifact_hashes") != _artifact_hashes(session_dir, manifest["kind"]):
        raise RuntimeError("Create authorization artifact hashes no longer match the reviewed run")
    return authorization


def _next_session_dir(workspace: Path, title: str, now: datetime) -> Path:
    day_dir = workspace / "runs" / now.strftime("%Y-%m-%d")
    base = f"{now.strftime('%H%M%S')}-{_slugify(title)}"
    candidate = day_dir / base
    suffix = 2
    while candidate.exists():
        candidate = day_dir / f"{base}-{suffix:02d}"
        suffix += 1
    return candidate


def initialize_session(
    workspace: Path,
    title: str,
    kind: str,
    brief: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Initialize one production session without inventing creative content."""
    if kind not in VALID_KINDS:
        raise ValueError(f"kind must be one of: {', '.join(sorted(VALID_KINDS))}")
    if not title.strip():
        raise ValueError("title must not be empty")
    if not brief.strip():
        raise ValueError("brief must not be empty")

    created_at = now or _utc_now()
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    created_at = created_at.astimezone(timezone.utc)
    session_dir = _next_session_dir(Path(workspace), title, created_at)
    session_dir.mkdir(parents=True, exist_ok=False)

    manifest = {
        "schema_version": 5,
        "id": session_dir.name,
        "title": title.strip(),
        "kind": kind,
        "status": "draft",
        "created_at": created_at.astimezone(timezone.utc).isoformat(),
        "create_authorizations": [],
        "create_actions": [],
        "download_authorizations": [],
        "downloads": [],
        "listening_receipts": [],
        "technical_qa": [],
        "release_gates": [],
        "voice_observation": None,
        "telemetry": [],
        "events": [],
        "generations": [],
    }
    _write_json(session_dir / "manifest.json", manifest)
    (session_dir / "brief.md").write_text(brief.strip() + "\n", encoding="utf-8")
    if kind == "song":
        (session_dir / "lyrics.md").write_text("", encoding="utf-8")
    elif kind == "meditation":
        (session_dir / "script.md").write_text("", encoding="utf-8")
    (session_dir / "style-prompt.md").write_text("", encoding="utf-8")
    (session_dir / "review.md").write_text("", encoding="utf-8")
    (session_dir / "composition-map.md").write_text("", encoding="utf-8")
    (session_dir / "vocal-casting.md").write_text("", encoding="utf-8")
    (session_dir / "audiovisual-hook-board.md").write_text("", encoding="utf-8")

    return {"status": "created", "session_dir": str(session_dir), "manifest": manifest}


def _has_real_content(path: Path) -> bool:
    if not path.is_file():
        return False
    normalized = path.read_text(encoding="utf-8").strip().casefold()
    return normalized not in EMPTY_MARKERS


def validate_session(session_dir: Path) -> dict[str, Any]:
    """Validate that a session has enough authored material for Suno Custom Mode."""
    session_dir = Path(session_dir)
    manifest_path = session_dir / "manifest.json"
    missing: list[str] = []
    errors: list[str] = []

    if not manifest_path.is_file():
        return {
            "status": "invalid",
            "session_dir": str(session_dir),
            "ready_for_suno": False,
            "missing": ["manifest.json"],
            "errors": [],
        }

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {
            "status": "invalid",
            "session_dir": str(session_dir),
            "ready_for_suno": False,
            "missing": [],
            "errors": [f"manifest.json is invalid JSON: {exc}"],
        }

    kind = manifest.get("kind")
    if kind not in VALID_KINDS:
        errors.append("manifest kind is invalid")
    if not _has_real_content(session_dir / "brief.md"):
        missing.append("brief.md")
    style_path = session_dir / "style-prompt.md"
    if not _has_real_content(style_path):
        missing.append("style-prompt.md")
    else:
        style_prompt = style_path.read_text(encoding="utf-8")
        if any(re.search(pattern, style_prompt, flags=re.IGNORECASE) for pattern in IMITATION_PATTERNS):
            errors.append("style prompt contains imitation language")
    if kind == "song" and not _has_real_content(session_dir / "lyrics.md"):
        missing.append("lyrics.md")
    if kind == "meditation":
        script_path = session_dir / "script.md"
        if not _has_real_content(script_path):
            missing.append("script.md")
        else:
            script = script_path.read_text(encoding="utf-8")
            if any(
                re.search(pattern, script, flags=re.IGNORECASE)
                for pattern in MEDITATION_VETO_PATTERNS
            ):
                errors.append("meditation script contains a safety or medical-claim veto")

    for artifact_name, required_fragments in PRODUCTION_ARTIFACTS.items():
        artifact_path = session_dir / artifact_name
        if not _has_real_content(artifact_path):
            missing.append(artifact_name)
            continue
        normalized_artifact = artifact_path.read_text(encoding="utf-8").casefold()
        missing_fragments = [fragment for fragment in required_fragments if fragment not in normalized_artifact]
        if missing_fragments:
            errors.append(
                f"{artifact_name} is missing required contract fields: {', '.join(missing_fragments)}"
            )

    review_path = session_dir / "review.md"
    if not _has_real_content(review_path):
        missing.append("review.md")
    else:
        review = review_path.read_text(encoding="utf-8")
        if not re.search(r"^VERDICT:\s*PASS\s*$", review, flags=re.MULTILINE | re.IGNORECASE):
            errors.append("review verdict must be PASS")
        score_match = re.search(r"^SCORE:\s*(\d{1,3})/100\s*$", review, flags=re.MULTILINE | re.IGNORECASE)
        if score_match is None:
            errors.append("review must include SCORE: N/100")
        else:
            score = int(score_match.group(1))
            minimum_score = 90 if kind == "meditation" else 85
            if score > 100:
                errors.append("review score must not exceed 100/100")
            elif score < minimum_score:
                errors.append(f"review score must be at least {minimum_score}/100")
        if not re.search(
            r"^HARD VETOES:\s*none\s*$",
            review,
            flags=re.MULTILINE | re.IGNORECASE,
        ):
            errors.append("review must declare HARD VETOES: none")
        axis_pattern = re.compile(
            r"^AXIS:\s*([a-z_]+)\s+(\d{1,2}(?:\.\d+)?)/10\s*\|\s*EVIDENCE:\s*(\S.+?)\s*$",
            flags=re.MULTILINE | re.IGNORECASE,
        )
        matches = list(axis_pattern.finditer(review))
        axis_names = [match.group(1).casefold() for match in matches]
        if len(axis_names) != len(set(axis_names)):
            errors.append("review must not repeat an axis")
        required_axes = tuple(
            "guidance_pacing" if axis == "hook_strength" and kind == "meditation" else axis
            for axis in REVIEW_AXIS_NAMES
        )
        unexpected_axes = sorted(set(axis_names) - set(required_axes))
        if unexpected_axes:
            errors.append("review contains an unrecognized axis")
        scored_axes = {
            match.group(1).casefold(): (float(match.group(2)), match.group(3).strip())
            for match in matches
        }
        missing_axes = [axis for axis in required_axes if axis not in scored_axes]
        if missing_axes:
            errors.append("review must score every required axis")
        for axis in required_axes:
            if axis in scored_axes and not 7.5 <= scored_axes[axis][0] <= 10:
                errors.append(f"review axis {axis} must be between 7.5 and 10/10")

    ready = not missing and not errors
    return {
        "status": "ready" if ready else "incomplete",
        "session_dir": str(session_dir),
        "ready_for_suno": ready,
        "missing": missing,
        "errors": errors,
    }


def _suno_generation_id(value: str) -> str | None:
    parsed = urlparse(value)
    host = (parsed.hostname or "").casefold()
    segments = [segment for segment in parsed.path.split("/") if segment]
    if (
        parsed.scheme != "https"
        or not (host == "suno.com" or host.endswith(".suno.com"))
        or len(segments) != 2
        or segments[0].casefold() not in {"song", "s"}
    ):
        return None
    return segments[1]


def authorize_create(
    session_dir: Path,
    authorization_id: str,
    operator_ref: str,
    expires_at: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Create a single-use, local tamper-evident authorization receipt.

    ``operator_ref`` is an auditable controller reference. It is not a substitute
    for a gateway-signed approval; callers must label its trust scope honestly.
    """
    normalized_id = authorization_id.strip()
    normalized_operator_ref = operator_ref.strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,127}", normalized_id):
        raise ValueError("authorization_id must be 3-128 safe characters")
    if not normalized_operator_ref:
        raise ValueError("operator_ref must not be empty")
    try:
        expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("expires_at must be ISO-8601") from exc
    if expiry.tzinfo is None:
        raise ValueError("expires_at must include a timezone")
    timestamp = _timestamp(now)
    if expiry.astimezone(timezone.utc) <= datetime.fromisoformat(timestamp):
        raise ValueError("expires_at must be in the future")

    session_dir = Path(session_dir)
    _require_ready(session_dir)
    manifest_path, manifest = _load_manifest(session_dir)
    authorizations = manifest.setdefault("create_authorizations", [])
    if any(item.get("id") == normalized_id for item in authorizations):
        raise ValueError(f"Create authorization already exists: {normalized_id}")
    receipt = {
        "id": normalized_id,
        "operator_ref": normalized_operator_ref,
        "trust_scope": "local-audit-record",
        "allowed_operation": "create",
        "action_budget": 1,
        "expires_at": expiry.astimezone(timezone.utc).isoformat(),
        "artifact_hashes": _artifact_hashes(session_dir, manifest["kind"]),
        "status": "authorized",
        "consumed_at": None,
    }
    authorizations.append(receipt)
    _append_event(manifest, "create_authorized", {"authorization_id": normalized_id}, timestamp)
    _write_json(manifest_path, manifest)
    return receipt


def record_browser_preflight(
    session_dir: Path,
    authorization_id: str,
    model_label: str,
    mode: str,
    ui_evidence_ref: str,
    ui_evidence_sha256: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Bind one authorization to an observed, redacted browser preflight."""
    normalized_model = model_label.strip()
    normalized_mode = mode.strip().casefold()
    normalized_ref = ui_evidence_ref.strip()
    normalized_hash = ui_evidence_sha256.strip().casefold()
    if not normalized_model:
        raise ValueError("model_label must not be empty")
    if normalized_mode != "custom":
        raise ValueError("mode must be custom")
    if not normalized_ref:
        raise ValueError("ui_evidence_ref must not be empty")
    if not re.fullmatch(r"[0-9a-f]{64}", normalized_hash):
        raise ValueError("ui_evidence_sha256 must be a SHA-256 hex digest")

    session_dir = Path(session_dir)
    _require_ready(session_dir)
    manifest_path, manifest = _load_manifest(session_dir)
    authorization = _authorization_for(manifest, authorization_id.strip())
    if manifest["kind"] == "song" and not (
        isinstance(manifest.get("voice_observation"), dict)
        and manifest["voice_observation"].get("state") == "selected"
    ):
        raise RuntimeError("vocal song requires observed Voice/Persona selection before preflight")
    if authorization.get("status") != "authorized":
        raise RuntimeError("Create authorization is not available for preflight")
    if authorization.get("artifact_hashes") != _artifact_hashes(session_dir, manifest["kind"]):
        raise RuntimeError("Create authorization artifact hashes no longer match the reviewed run")
    if datetime.fromisoformat(str(authorization["expires_at"])) <= datetime.fromisoformat(_timestamp(now)):
        raise RuntimeError("Create authorization has expired")
    timestamp = _timestamp(now)
    authorization.update(
        {
            "status": "preflighted",
            "preflight": {
                "model_label": normalized_model,
                "mode": normalized_mode,
                "ui_evidence_ref": normalized_ref,
                "ui_evidence_sha256": normalized_hash,
                "observed_at": timestamp,
            },
        }
    )
    _append_event(manifest, "browser_preflighted", {"authorization_id": authorization_id.strip()}, timestamp)
    _write_json(manifest_path, manifest)
    return authorization


def record_create_submission(
    session_dir: Path, authorization_id: str, now: datetime | None = None
) -> dict[str, Any]:
    """Consume a preflighted authorization immediately after the single Create click."""
    session_dir = Path(session_dir)
    manifest_path, manifest = _load_manifest(session_dir)
    authorization = _require_authorization_preflight(session_dir, manifest, authorization_id.strip())
    if datetime.fromisoformat(str(authorization["expires_at"])) <= datetime.fromisoformat(_timestamp(now)):
        raise RuntimeError("Create authorization has expired")
    timestamp = _timestamp(now)
    authorization["status"] = "submitted"
    authorization["consumed_at"] = timestamp
    create_actions = manifest.setdefault("create_actions", [])
    create_actions.append(
        {
            "id": authorization_id.strip(),
            "authorization_id": authorization_id.strip(),
            "model_label": authorization["preflight"]["model_label"],
            "mode": "custom",
            "create_click_count": 1,
            "status": "awaiting_results",
            "submitted_at": timestamp,
        }
    )
    _append_event(manifest, "create_submitted", {"authorization_id": authorization_id.strip()}, timestamp)
    _write_json(manifest_path, manifest)
    return create_actions[-1]


def record_generation(
    session_dir: Path,
    url: str,
    generation_id: str,
    take: int,
    note: str,
    create_action_id: str,
    model_label: str,
    take_title: str,
    mode: str = "custom",
    additional_action_authorized: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Record a generation only after a real Suno URL/ID is available."""
    normalized_id = generation_id.strip()
    normalized_action_id = create_action_id.strip()
    normalized_model = model_label.strip()
    normalized_take_title = take_title.strip()
    normalized_mode = mode.strip().casefold()
    url_id = _suno_generation_id(url)
    if url_id is None:
        raise ValueError("url must be a real https://suno.com/song/<id> generation URL")
    if not normalized_id:
        raise ValueError("generation_id must not be empty")
    if not normalized_action_id:
        raise ValueError("create_action_id must not be empty")
    if not normalized_model:
        raise ValueError("model_label must not be empty")
    if not normalized_take_title:
        raise ValueError("take_title must not be empty")
    if normalized_mode != "custom":
        raise ValueError("mode must be custom")
    if take < 1:
        raise ValueError("take must be at least 1")
    if url_id != normalized_id:
        raise ValueError("generation_id must match the final segment of the Suno URL")

    session_dir = Path(session_dir)
    _require_ready(session_dir)
    manifest_path, manifest = _load_manifest(session_dir)
    authorization = _authorization_for(manifest, normalized_action_id)
    if authorization.get("status") != "submitted":
        raise RuntimeError("Create authorization must be consumed by a recorded Create submission")
    if authorization.get("artifact_hashes") != _artifact_hashes(session_dir, manifest["kind"]):
        raise RuntimeError("Create authorization artifact hashes no longer match the reviewed run")
    if additional_action_authorized:
        raise ValueError("additional-action Boolean is not a valid Create authorization")
    generations = manifest.setdefault("generations", [])
    create_actions = manifest.setdefault("create_actions", [])
    if not isinstance(generations, list) or not isinstance(create_actions, list):
        raise ValueError("manifest generation receipt fields must be lists")
    if any(str(item.get("id", "")).strip() == normalized_id for item in generations):
        raise ValueError(f"generation already recorded: {normalized_id}")
    if any(item.get("url") == url for item in generations):
        raise ValueError(f"generation URL already recorded: {url}")
    if any(item.get("take") == take for item in generations):
        raise ValueError(f"take already recorded: {take}")

    recorded_at_text = _timestamp(now)
    create_action = next(
        (
            action
            for action in create_actions
            if str(action.get("id", "")).strip() == normalized_action_id
        ),
        None,
    )
    if create_action is None:
        raise RuntimeError("Create submission is missing for this authorization")
    if int(create_action.get("completed_take_count", 0)) >= 2:
        raise RuntimeError("Create action already has its maximum two observed takes")
    if (
        create_action.get("model_label") != normalized_model
        or create_action.get("mode") != normalized_mode
        or authorization["preflight"]["model_label"] != normalized_model
    ):
        raise ValueError("Create action model or mode does not match its preflight")

    generations.append(
        {
            "id": normalized_id,
            "title": normalized_take_title,
            "url": url,
            "take": take,
            "create_action_id": normalized_action_id,
            "note": note.strip(),
            "recorded_at": recorded_at_text,
        }
    )
    create_action["completed_take_count"] = int(
        create_action.get("completed_take_count", 0)
    ) + 1
    create_action.setdefault("take_ids", []).append(normalized_id)
    create_action["status"] = "partial" if create_action["completed_take_count"] < 2 else "completed"
    manifest["status"] = "generated_partial" if create_action["status"] == "partial" else "generated"
    _append_event(
        manifest,
        "generation_observed",
        {
            "authorization_id": normalized_action_id,
            "generation_id": normalized_id,
            "take": take,
            "action_status": create_action["status"],
        },
        recorded_at_text,
    )
    _write_json(manifest_path, manifest)
    return {
        "status": "recorded",
        "session_dir": str(session_dir),
        "generation_count": len(generations),
        "create_action_count": len(create_actions),
        "create_action": create_action,
        "generation": generations[-1],
    }


def _generation_for(manifest: dict[str, Any], take_id: str) -> dict[str, Any]:
    generation = next(
        (item for item in manifest.get("generations", []) if str(item.get("id", "")) == take_id),
        None,
    )
    if generation is None:
        raise RuntimeError("observed generation is missing for this take")
    return generation


def record_voice_observation(
    session_dir: Path,
    state: str,
    label: str,
    observed_details: str,
    options_observed: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Record visible Voice/Persona options before one vocal selection."""
    normalized_state = state.strip().casefold()
    if normalized_state not in {"selected", "unresolved", "not_applicable"}:
        raise ValueError("voice state must be selected, unresolved, or not_applicable")
    if not label.strip() or not observed_details.strip() or not options_observed.strip():
        raise ValueError("voice label, observed details, and visible options must not be empty")
    if normalized_state == "selected" and label.casefold() not in options_observed.casefold():
        raise ValueError("selected Voice/Persona label must appear in the visible options observation")
    manifest_path, manifest = _load_manifest(Path(session_dir))
    if manifest["kind"] == "song" and normalized_state != "selected":
        raise RuntimeError("vocal song requires an observed selected Voice/Persona before Create")
    receipt = {
        "state": normalized_state,
        "label": label.strip(),
        "observed_details": observed_details.strip(),
        "options_observed": options_observed.strip(),
        "recorded_at": _timestamp(now),
        "trust_scope": "visible-ui-observation",
    }
    manifest["voice_observation"] = receipt
    _append_event(manifest, "voice_observed", {"state": normalized_state, "label": label.strip()}, receipt["recorded_at"])
    _write_json(manifest_path, manifest)
    return receipt


def authorize_download(
    session_dir: Path, authorization_id: str, take_id: str, operator_ref: str, expires_at: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Authorize one local asset capture for one observed take; no browser action occurs here."""
    normalized_id, normalized_take, normalized_ref = authorization_id.strip(), take_id.strip(), operator_ref.strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,127}", normalized_id):
        raise ValueError("authorization_id must be 3-128 safe characters")
    if not normalized_ref:
        raise ValueError("operator_ref must not be empty")
    expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    if expiry.tzinfo is None or expiry.astimezone(timezone.utc) <= (now or _utc_now()).astimezone(timezone.utc):
        raise ValueError("expires_at must be a future ISO-8601 value with timezone")
    manifest_path, manifest = _load_manifest(Path(session_dir))
    generation = _generation_for(manifest, normalized_take)
    authorizations = manifest.setdefault("download_authorizations", [])
    if any(item.get("id") == normalized_id for item in authorizations):
        raise ValueError(f"download authorization already exists: {normalized_id}")
    if any(item.get("take_id") == normalized_take and item.get("status") != "consumed" for item in authorizations):
        raise RuntimeError("take already has an active download authorization")
    receipt = {
        "id": normalized_id,
        "take_id": normalized_take,
        "source_url": generation["url"],
        "operator_ref": normalized_ref,
        "expires_at": expiry.astimezone(timezone.utc).isoformat(),
        "status": "authorized",
        "trust_scope": "local-audit-record",
    }
    authorizations.append(receipt)
    _append_event(manifest, "download_authorized", {"authorization_id": normalized_id, "take_id": normalized_take}, _timestamp(now))
    _write_json(manifest_path, manifest)
    return receipt


def record_download(session_dir: Path, take_id: str, asset_path: Path, release_root: Path, now: datetime | None = None) -> dict[str, Any]:
    """Bind one locally present file to an explicit per-take download authorization."""
    source = Path(asset_path).resolve()
    root = Path(release_root).resolve()
    try:
        source.relative_to(root)
    except ValueError as exc:
        raise ValueError("asset_path must be under the explicit release_root") from exc
    if not source.is_file() or source.is_symlink():
        raise ValueError("asset_path must be a regular existing file")
    manifest_path, manifest = _load_manifest(Path(session_dir))
    _generation_for(manifest, take_id.strip())
    authorization = next(
        (item for item in manifest.get("download_authorizations", []) if item.get("take_id") == take_id.strip() and item.get("status") == "authorized"),
        None,
    )
    if authorization is None:
        raise RuntimeError("download authorization is missing for this take")
    if datetime.fromisoformat(authorization["expires_at"]) <= datetime.fromisoformat(_timestamp(now)):
        raise RuntimeError("download authorization has expired")
    downloads = manifest.setdefault("downloads", [])
    if any(item.get("take_id") == take_id.strip() for item in downloads):
        raise RuntimeError("take already has a download receipt")
    receipt = {
        "take_id": take_id.strip(), "authorization_id": authorization["id"], "source_url": authorization["source_url"],
        "local_path": str(source), "sha256": _sha256_file(source), "bytes": source.stat().st_size,
        "format": source.suffix.casefold().lstrip("."), "downloaded_at": _timestamp(now),
    }
    downloads.append(receipt)
    authorization["status"] = "consumed"
    manifest["status"] = "downloaded"
    _append_event(manifest, "download_recorded", {"take_id": take_id.strip(), "sha256": receipt["sha256"]}, receipt["downloaded_at"])
    _write_json(manifest_path, manifest)
    return receipt


def record_listening(
    session_dir: Path, take_id: str, playback_method: str, reviewer: str, decision: str, notes: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Record a human/agent playback attestation; this API does not claim playback by itself."""
    normalized_decision = decision.strip().upper()
    if normalized_decision not in DOWNLOAD_DECISIONS:
        raise ValueError("listening decision must be KEEP, ITERATE, or CUT")
    if not playback_method.strip() or not reviewer.strip() or not notes.strip():
        raise ValueError("playback_method, reviewer, and notes must not be empty")
    manifest_path, manifest = _load_manifest(Path(session_dir))
    if not any(item.get("take_id") == take_id.strip() for item in manifest.get("downloads", [])):
        raise RuntimeError("a local download receipt is required before a listening receipt")
    receipts = manifest.setdefault("listening_receipts", [])
    if any(item.get("take_id") == take_id.strip() for item in receipts):
        raise RuntimeError("take already has a listening receipt")
    receipt = {"take_id": take_id.strip(), "playback_method": playback_method.strip(), "reviewer": reviewer.strip(), "decision": normalized_decision, "notes": notes.strip(), "listened_at": _timestamp(now), "truth_scope": "declared-actual-playback"}
    receipts.append(receipt)
    manifest["status"] = "listened"
    _append_event(manifest, "listening_recorded", {"take_id": take_id.strip(), "decision": normalized_decision}, receipt["listened_at"])
    _write_json(manifest_path, manifest)
    return receipt


def record_technical_qa(session_dir: Path, take_id: str, evidence: dict[str, Any], status: str, now: datetime | None = None) -> dict[str, Any]:
    """Attach tool-derived technical evidence after a KEEP listening receipt; never invents analysis."""
    normalized_status = status.strip().upper()
    if normalized_status not in {"PASS", "FAIL"} or not evidence:
        raise ValueError("technical QA needs non-empty evidence and PASS or FAIL status")
    manifest_path, manifest = _load_manifest(Path(session_dir))
    listening = next((item for item in manifest.get("listening_receipts", []) if item.get("take_id") == take_id.strip()), None)
    if listening is None:
        raise RuntimeError("listening receipt is required before technical QA")
    if listening.get("decision") != "KEEP":
        raise RuntimeError("only a KEEP listening decision can advance to technical QA")
    required_evidence = {"tool", "command", "asset_sha256"}
    missing_evidence = sorted(required_evidence - set(evidence))
    if missing_evidence:
        raise ValueError(
            "technical QA evidence is missing required fields: " + ", ".join(missing_evidence)
        )
    download = next(
        (item for item in manifest.get("downloads", []) if item.get("take_id") == take_id.strip()),
        None,
    )
    if download is None or evidence["asset_sha256"] != download["sha256"]:
        raise ValueError("technical QA asset_sha256 must match the recorded downloaded asset")
    receipts = manifest.setdefault("technical_qa", [])
    if any(item.get("take_id") == take_id.strip() for item in receipts):
        raise RuntimeError("take already has a technical QA receipt")
    receipt = {"take_id": take_id.strip(), "status": normalized_status, "evidence": evidence, "analyzed_at": _timestamp(now), "truth_scope": "tool-derived-evidence"}
    receipts.append(receipt)
    if normalized_status == "PASS":
        manifest["status"] = "qa_passed"
    _append_event(manifest, "technical_qa_recorded", {"take_id": take_id.strip(), "status": normalized_status}, receipt["analyzed_at"])
    _write_json(manifest_path, manifest)
    return receipt


def record_release_gate(
    session_dir: Path,
    take_id: str,
    release_root: Path,
    decision: str,
    rights_state: str,
    evidence: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Record a private DAM/rights retention decision after real listening and QA.

    This is an asset-retention gate, never publication authorization. It binds the
    current on-disk bytes to the earlier download receipt and rejects a mutated file.
    """
    normalized_take = take_id.strip()
    normalized_decision = decision.strip().upper()
    normalized_rights = rights_state.strip().casefold()
    if normalized_decision not in RELEASE_DECISIONS:
        raise ValueError("release decision must be RETAIN or REJECT")
    if normalized_rights not in PRIVATE_RIGHTS_STATES:
        raise ValueError("rights_state must be private_unpublished or rights_hold")
    if not evidence.strip():
        raise ValueError("release gate evidence must not be empty")
    manifest_path, manifest = _load_manifest(Path(session_dir))
    download = next(
        (item for item in manifest.get("downloads", []) if item.get("take_id") == normalized_take),
        None,
    )
    if download is None:
        raise RuntimeError("download receipt is required before the release gate")
    release_path = Path(download["local_path"]).resolve()
    root = Path(release_root).resolve()
    try:
        release_path.relative_to(root)
    except ValueError as exc:
        raise ValueError("recorded asset must remain under the explicit release_root") from exc
    if not release_path.is_file() or _sha256_file(release_path) != download["sha256"]:
        raise RuntimeError("recorded asset bytes no longer match the download receipt")
    gates = manifest.setdefault("release_gates", [])
    if any(item.get("take_id") == normalized_take for item in gates):
        raise RuntimeError("take already has a release gate receipt")
    if normalized_decision == "RETAIN":
        if normalized_rights != "private_unpublished":
            raise RuntimeError("RETAIN requires rights_state private_unpublished")
        qa = next(
            (item for item in manifest.get("technical_qa", []) if item.get("take_id") == normalized_take),
            None,
        )
        if qa is None or qa.get("status") != "PASS":
            raise RuntimeError("RETAIN requires a PASS technical QA receipt")
    timestamp = _timestamp(now)
    receipt = {
        "take_id": normalized_take,
        "decision": normalized_decision,
        "rights_state": normalized_rights,
        "release_root": str(root),
        "local_path": str(release_path),
        "sha256": download["sha256"],
        "evidence": evidence.strip(),
        "publication_authorized": False,
        "recorded_at": timestamp,
    }
    gates.append(receipt)
    manifest["status"] = "retained_private" if normalized_decision == "RETAIN" else "rejected"
    _append_event(
        manifest,
        "release_gate_recorded",
        {"take_id": normalized_take, "decision": normalized_decision, "rights_state": normalized_rights},
        timestamp,
    )
    _write_json(manifest_path, manifest)
    return receipt


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="Create a new production session")
    init.add_argument("--workspace", type=Path, default=Path.home() / "agentic-music-producer-os")
    init.add_argument("--title", required=True)
    init.add_argument("--kind", choices=sorted(VALID_KINDS), required=True)
    init.add_argument("--brief", required=True)

    validate = commands.add_parser("validate", help="Validate a session for Suno")
    validate.add_argument("session_dir", type=Path)

    authorize = commands.add_parser("authorize-create", help="Record one local Create authorization")
    authorize.add_argument("session_dir", type=Path)
    authorize.add_argument("--authorization-id", required=True)
    authorize.add_argument("--operator-ref", required=True)
    authorize.add_argument("--expires-at", required=True)

    preflight = commands.add_parser("preflight", help="Record observed Suno Custom-mode preflight")
    preflight.add_argument("session_dir", type=Path)
    preflight.add_argument("--authorization-id", required=True)
    preflight.add_argument("--model-label", required=True)
    preflight.add_argument("--mode", default="custom", choices=["custom"])
    preflight.add_argument("--ui-evidence-ref", required=True)
    preflight.add_argument("--ui-evidence-sha256", required=True)

    submit = commands.add_parser("record-submit", help="Consume authorization after one observed Create click")
    submit.add_argument("session_dir", type=Path)
    submit.add_argument("--authorization-id", required=True)

    record = commands.add_parser("record", help="Record a Suno take after an authorized observed Create")
    record.add_argument("session_dir", type=Path)
    record.add_argument("--url", required=True)
    record.add_argument("--id", dest="generation_id", required=True)
    record.add_argument("--take", type=int, required=True)
    record.add_argument("--note", default="")
    record.add_argument("--action-id", dest="create_action_id", required=True)
    record.add_argument("--model-label", required=True)
    record.add_argument("--take-title", required=True)
    record.add_argument("--mode", default="custom", choices=["custom"])

    voice = commands.add_parser("record-voice", help="Record observed Suno Voice/Persona selection facts")
    voice.add_argument("session_dir", type=Path)
    voice.add_argument("--state", required=True, choices=["selected", "unresolved", "not_applicable"])
    voice.add_argument("--label", required=True)
    voice.add_argument("--observed-details", required=True)
    voice.add_argument("--options-observed", required=True)

    download_authorize = commands.add_parser("authorize-download", help="Authorize one local capture for one observed take")
    download_authorize.add_argument("session_dir", type=Path)
    download_authorize.add_argument("--authorization-id", required=True)
    download_authorize.add_argument("--take-id", required=True)
    download_authorize.add_argument("--operator-ref", required=True)
    download_authorize.add_argument("--expires-at", required=True)

    download = commands.add_parser("record-download", help="Record one authorized local asset capture")
    download.add_argument("session_dir", type=Path)
    download.add_argument("--take-id", required=True)
    download.add_argument("--asset-path", type=Path, required=True)
    download.add_argument("--release-root", type=Path, required=True)

    listening = commands.add_parser("record-listening", help="Record a real playback receipt")
    listening.add_argument("session_dir", type=Path)
    listening.add_argument("--take-id", required=True)
    listening.add_argument("--playback-method", required=True)
    listening.add_argument("--reviewer", required=True)
    listening.add_argument("--decision", required=True, choices=sorted(DOWNLOAD_DECISIONS))
    listening.add_argument("--notes", required=True)

    qa = commands.add_parser("record-technical-qa", help="Record tool-derived technical QA after KEEP listening")
    qa.add_argument("session_dir", type=Path)
    qa.add_argument("--take-id", required=True)
    qa.add_argument("--status", required=True, choices=["PASS", "FAIL"])
    qa.add_argument("--evidence-json", required=True)

    release = commands.add_parser("record-release-gate", help="Record private DAM/rights retention after QA")
    release.add_argument("session_dir", type=Path)
    release.add_argument("--take-id", required=True)
    release.add_argument("--release-root", type=Path, required=True)
    release.add_argument("--decision", required=True, choices=sorted(RELEASE_DECISIONS))
    release.add_argument("--rights-state", required=True, choices=sorted(PRIVATE_RIGHTS_STATES))
    release.add_argument("--evidence", required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "init":
        result = initialize_session(args.workspace, args.title, args.kind, args.brief)
    elif args.command == "validate":
        result = validate_session(args.session_dir)
    elif args.command == "authorize-create":
        result = authorize_create(
            args.session_dir, args.authorization_id, args.operator_ref, args.expires_at
        )
    elif args.command == "preflight":
        result = record_browser_preflight(
            args.session_dir,
            args.authorization_id,
            args.model_label,
            args.mode,
            args.ui_evidence_ref,
            args.ui_evidence_sha256,
        )
    elif args.command == "record-submit":
        result = record_create_submission(args.session_dir, args.authorization_id)
    elif args.command == "record":
        result = record_generation(
            args.session_dir,
            args.url,
            args.generation_id,
            args.take,
            args.note,
            args.create_action_id,
            args.model_label,
            args.take_title,
            args.mode,
        )
    elif args.command == "record-voice":
        result = record_voice_observation(
            args.session_dir,
            args.state,
            args.label,
            args.observed_details,
            args.options_observed,
        )
    elif args.command == "authorize-download":
        result = authorize_download(
            args.session_dir, args.authorization_id, args.take_id, args.operator_ref, args.expires_at
        )
    elif args.command == "record-download":
        result = record_download(args.session_dir, args.take_id, args.asset_path, args.release_root)
    elif args.command == "record-listening":
        result = record_listening(
            args.session_dir, args.take_id, args.playback_method, args.reviewer, args.decision, args.notes
        )
    elif args.command == "record-technical-qa":
        try:
            evidence = json.loads(args.evidence_json)
        except json.JSONDecodeError as exc:
            raise ValueError("--evidence-json must be valid JSON") from exc
        if not isinstance(evidence, dict):
            raise ValueError("--evidence-json must decode to an object")
        result = record_technical_qa(args.session_dir, args.take_id, evidence, args.status)
    else:
        result = record_release_gate(
            args.session_dir,
            args.take_id,
            args.release_root,
            args.decision,
            args.rights_state,
            args.evidence,
        )
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result.get("status") not in {"invalid", "incomplete"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
