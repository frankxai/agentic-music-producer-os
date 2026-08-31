#!/usr/bin/env python3
"""CLI for the composer-first score factory."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from scorelib import compile_score, parse_score_text, score_to_json, validate_score  # noqa: E402


def _catalog_root() -> Path:
    return ROOT / "catalog"


def cmd_init(args: argparse.Namespace) -> int:
    slug = args.slug or _slug(args.title)
    dest = _catalog_root() / slug
    dest.mkdir(parents=True, exist_ok=True)
    score_path = dest / "score.txt"
    if score_path.exists() and not args.force:
        raise SystemExit(f"refusing to overwrite {score_path}; pass --force")
    score_path.write_text(
        (
            f"@title {args.title}\n"
            f"@composer Frank / Agentic Composer OS\n"
            f"@kind {args.kind}\n"
            f"@key {args.key}\n"
            f"@time {args.time}\n"
            f"@tempo {args.tempo}\n"
            f"@thesis {args.thesis or 'WRITE the emotional contract'}\n"
            f"@motif {args.motif or 'WRITE the irreducible cell'}\n"
            f"@form {args.form or 'WRITE the section map'}\n"
            "\n"
            "[Piano]\n"
            "1 RH: A4q F4q D4h\n"
            "1 LH: D3h A2h\n"
        ),
        encoding="utf-8",
    )
    print(dest)
    return 0


def cmd_compile(args: argparse.Namespace) -> int:
    score_path = Path(args.score)
    text = score_path.read_text(encoding="utf-8")
    score = parse_score_text(text)
    out_dir = Path(args.out) if args.out else score_path.parent / "build"
    artifacts = compile_score(score, out_dir, preview=args.preview)
    if args.preview and args.mp3:
        wav = Path(artifacts["preview_wav"])
        mp3 = wav.with_suffix(".mp3")
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise SystemExit("ffmpeg not found; WAV preview exists, MP3 skipped")
        subprocess.run(
            [ffmpeg, "-y", "-i", str(wav), "-codec:a", "libmp3lame", "-b:a", "320k", str(mp3)],
            check=True,
            capture_output=True,
        )
        artifacts["preview_mp3"] = str(mp3)
        manifest_path = Path(artifacts["manifest"])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["artifacts"]["preview_mp3"] = str(mp3)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(artifacts, indent=2))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    score = parse_score_text(Path(args.score).read_text(encoding="utf-8"))
    issues = validate_score(score)
    payload = {
        "title": score.title,
        "ok": not issues,
        "issues": issues,
        "json": score_to_json(score),
    }
    print(json.dumps(payload, indent=2))
    return 0 if not issues else 1


def cmd_catalog(args: argparse.Namespace) -> int:
    rows = []
    root = _catalog_root()
    if root.exists():
        for score_path in sorted(root.glob("*/score.txt")):
            score = parse_score_text(score_path.read_text(encoding="utf-8"))
            rows.append(
                {
                    "slug": score_path.parent.name,
                    "title": score.title,
                    "kind": score.kind,
                    "key": score.key,
                    "tempo": score.tempo,
                    "measures": max(len(part.measures) for part in score.parts),
                    "path": str(score_path),
                }
            )
    print(json.dumps({"count": len(rows), "works": rows, "at": _now()}, indent=2))
    return 0


def _slug(value: str) -> str:
    import re

    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")[:64] or "untitled"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Composer-first score factory")
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init")
    init.add_argument("--title", required=True)
    init.add_argument("--kind", default="piano")
    init.add_argument("--key", default="D minor")
    init.add_argument("--time", default="4/4")
    init.add_argument("--tempo", type=int, default=68)
    init.add_argument("--thesis", default="")
    init.add_argument("--motif", default="")
    init.add_argument("--form", default="")
    init.add_argument("--slug", default="")
    init.add_argument("--force", action="store_true")
    init.set_defaults(func=cmd_init)

    compile_cmd = sub.add_parser("compile")
    compile_cmd.add_argument("score")
    compile_cmd.add_argument("--out")
    compile_cmd.add_argument("--preview", action="store_true")
    compile_cmd.add_argument("--mp3", action="store_true")
    compile_cmd.set_defaults(func=cmd_compile)

    validate = sub.add_parser("validate")
    validate.add_argument("score")
    validate.set_defaults(func=cmd_validate)

    catalog = sub.add_parser("catalog")
    catalog.set_defaults(func=cmd_catalog)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
