#!/usr/bin/env python3
"""Lyria 3 generation lane. Never invents audio. Never prints secrets."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))


def _key_present() -> bool:
    return bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))


def cmd_status(_args: argparse.Namespace) -> int:
    print(
        json.dumps(
            {
                "provider": "google-lyria-3",
                "models": ["lyria-3-clip-preview", "lyria-3-pro-preview"],
                "key_present": _key_present(),
                "ready": _key_present(),
                "note": "Lyria emits audio, not MusicXML. Compile the score first.",
            },
            indent=2,
        )
    )
    return 0


def cmd_packet(args: argparse.Namespace) -> int:
    prompt_path = Path(args.prompt)
    if not prompt_path.exists():
        raise SystemExit(f"missing prompt: {prompt_path}")
    packet = {
        "model": args.model,
        "input": prompt_path.read_text(encoding="utf-8"),
        "response_format": {"type": "audio"} if args.wav else None,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_prompt": str(prompt_path),
    }
    out = Path(args.out) if args.out else prompt_path.with_name("lyria-packet.json")
    out.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    print(out)
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    if not args.authorize:
        raise SystemExit("refusing: pass --authorize after an explicit generate instruction")
    if not _key_present():
        raise SystemExit(
            "GEMINI_API_KEY / GOOGLE_API_KEY not present in this process. "
            "Load from Infisical/registry; do not paste the key into chat."
        )
    try:
        from google import genai  # type: ignore
    except Exception as exc:  # pragma: no cover - environment specific
        raise SystemExit(f"google-genai import failed: {exc}") from exc

    prompt = Path(args.prompt).read_text(encoding="utf-8")
    client = genai.Client()
    kwargs = {"model": args.model, "input": prompt}
    if args.wav:
        kwargs["response_format"] = {"type": "audio"}
    interaction = client.interactions.create(**kwargs)
    audio = getattr(interaction, "output_audio", None)
    text = getattr(interaction, "output_text", None)
    if audio is None:
        raise SystemExit("Lyria returned no audio; not fabricating a file")
    import base64

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = "wav" if args.wav else "mp3"
    audio_path = out_dir / f"lyria-take.{ext}"
    audio_path.write_bytes(base64.b64decode(audio.data))
    receipt = {
        "model": args.model,
        "audio": str(audio_path),
        "bytes": audio_path.stat().st_size,
        "lyrics_or_structure": text,
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "note": "Generative performance, not score-accurate. Keep MusicXML as canon.",
    }
    (out_dir / "lyria-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"audio": str(audio_path), "receipt": str(out_dir / "lyria-receipt.json")}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Lyria 3 lane")
    sub = parser.add_subparsers(dest="command", required=True)
    status = sub.add_parser("status")
    status.set_defaults(func=cmd_status)
    packet = sub.add_parser("packet")
    packet.add_argument("prompt")
    packet.add_argument("--model", default="lyria-3-pro-preview")
    packet.add_argument("--wav", action="store_true")
    packet.add_argument("--out")
    packet.set_defaults(func=cmd_packet)
    generate = sub.add_parser("generate")
    generate.add_argument("prompt")
    generate.add_argument("--model", default="lyria-3-clip-preview")
    generate.add_argument("--out", required=True)
    generate.add_argument("--wav", action="store_true")
    generate.add_argument("--authorize", action="store_true")
    generate.set_defaults(func=cmd_generate)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
