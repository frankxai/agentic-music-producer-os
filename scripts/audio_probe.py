#!/usr/bin/env python3
"""Objective measurement of a generated take.

Claude cannot hear audio. This script replaces guessing with measurement so that
first-listen review is evidence-based and `music-taste-review`'s prohibition on
unverified acoustic claims can actually be honored.

Requires ffmpeg and ffprobe on PATH. No Python dependencies beyond the stdlib.

    python scripts/audio_probe.py TAKE.mp3
    python scripts/audio_probe.py TAKE.mp3 --session runs/2026-08-07-title --take 1
    python scripts/audio_probe.py TAKE.mp3 --transcribe --lyrics runs/.../lyrics.md

Transcription is opt-in and requires a local ASR. It is the highest-value check
available after generation: pronunciation is decided at generation time and cannot
be repaired by extend, replace-section, or remaster.
"""

from __future__ import annotations

import argparse
import array
import json
import math
import shutil
import statistics
import subprocess
import sys
from pathlib import Path

WINDOW_SECONDS = 0.5
PROBE_RATE = 8000
SILENCE_DBFS = -50.0


def _need(binary: str) -> str:
    path = shutil.which(binary)
    if not path:
        sys.exit(f"{binary} not found on PATH. Install ffmpeg and retry.")
    return path


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def probe_container(path: Path) -> dict:
    _need("ffprobe")
    out = _run([
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", str(path),
    ])
    if out.returncode != 0:
        sys.exit(f"ffprobe failed: {out.stderr.strip()}")
    data = json.loads(out.stdout)
    audio = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), {})
    fmt = data.get("format", {})
    return {
        "duration_s": round(float(fmt.get("duration", 0.0)), 2),
        "codec": audio.get("codec_name"),
        "sample_rate_hz": int(audio.get("sample_rate", 0) or 0),
        "channels": audio.get("channels"),
        "bit_rate_kbps": round(int(fmt.get("bit_rate", 0) or 0) / 1000) or None,
        "size_bytes": int(fmt.get("size", 0) or 0),
    }


def measure_loudness(path: Path) -> dict:
    """EBU R128 pass. Values are what a mastering engineer would quote."""
    _need("ffmpeg")
    out = _run([
        "ffmpeg", "-nostats", "-hide_banner", "-i", str(path),
        "-af", "loudnorm=print_format=json", "-f", "null", "-",
    ])
    text = out.stderr
    start = text.rfind("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return {"error": "loudnorm produced no JSON block"}
    try:
        raw = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return {"error": "loudnorm JSON was unparseable"}

    def num(key: str) -> float | None:
        try:
            return round(float(raw[key]), 2)
        except (KeyError, TypeError, ValueError):
            return None

    return {
        "integrated_lufs": num("input_i"),
        "true_peak_dbtp": num("input_tp"),
        "loudness_range_lu": num("input_lra"),
        "threshold_lufs": num("input_thresh"),
    }


def energy_curve(path: Path) -> tuple[list[float], list[float]]:
    """RMS per window, in dBFS, from a decoded mono downsample."""
    _need("ffmpeg")
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1",
         "-ar", str(PROBE_RATE), "-f", "s16le", "-"],
        capture_output=True, check=False,
    )
    if out.returncode != 0:
        sys.exit(f"decode failed: {out.stderr.decode(errors='replace').strip()}")

    samples = array.array("h")
    samples.frombytes(out.stdout[: len(out.stdout) // 2 * 2])
    if not samples:
        sys.exit("decoded zero samples")

    step = int(PROBE_RATE * WINDOW_SECONDS)
    rms_db: list[float] = []
    times: list[float] = []
    for i in range(0, len(samples) - step + 1, step):
        chunk = samples[i:i + step]
        mean_sq = sum(s * s for s in chunk) / len(chunk)
        rms = mean_sq ** 0.5 / 32768.0
        rms_db.append(round(20 * math.log10(rms), 2) if rms > 0 else -120.0)
        times.append(round(i / PROBE_RATE, 2))
    return times, rms_db


def analyze_shape(times: list[float], rms_db: list[float]) -> dict:
    loud = [v for v in rms_db if v > SILENCE_DBFS]
    floor = min(rms_db)
    ceiling = max(rms_db)
    span = (ceiling - floor) or 1.0

    scaled = [round((v - floor) / span * 10, 1) for v in rms_db]

    lead = 0
    for v in rms_db:
        if v > SILENCE_DBFS:
            break
        lead += 1
    trail = 0
    for v in reversed(rms_db):
        if v > SILENCE_DBFS:
            break
        trail += 1

    gaps = []
    run = 0
    for idx, v in enumerate(rms_db):
        if v <= SILENCE_DBFS:
            run += 1
        else:
            if run >= 2:
                gaps.append({
                    "start_s": times[idx - run],
                    "duration_s": round(run * WINDOW_SECONDS, 2),
                })
            run = 0

    jumps = []
    for i in range(1, len(scaled)):
        delta = scaled[i] - scaled[i - 1]
        if abs(delta) >= 2.0:
            jumps.append({"at_s": times[i], "delta": round(delta, 1)})
    jumps.sort(key=lambda j: abs(j["delta"]), reverse=True)

    peak_idx = scaled.index(max(scaled))
    return {
        "energy_curve_0_10": scaled,
        "window_seconds": WINDOW_SECONDS,
        "leading_silence_s": round(lead * WINDOW_SECONDS, 2),
        "trailing_silence_s": round(trail * WINDOW_SECONDS, 2),
        "internal_silences": gaps[:10],
        "largest_energy_changes": jumps[:8],
        "peak_energy_at_s": times[peak_idx],
        "median_rms_dbfs": round(statistics.median(loud), 2) if loud else None,
        "dynamic_span_db": round(span, 2),
    }


def transcribe(path: Path) -> dict:
    """Opt-in. Tries faster-whisper via uvx, then a whisper CLI."""
    if shutil.which("uvx"):
        out = _run(["uvx", "--from", "faster-whisper", "faster-whisper",
                    str(path), "--output_format", "txt", "--output_dir", str(path.parent)])
        candidate = path.with_suffix(".txt")
        if out.returncode == 0 and candidate.exists():
            return {"engine": "faster-whisper", "text": candidate.read_text(encoding="utf-8").strip()}
    if shutil.which("whisper"):
        out = _run(["whisper", str(path), "--output_format", "txt",
                    "--output_dir", str(path.parent)])
        candidate = path.with_suffix(".txt")
        if out.returncode == 0 and candidate.exists():
            return {"engine": "whisper", "text": candidate.read_text(encoding="utf-8").strip()}
    return {
        "engine": None,
        "error": "no local ASR found",
        "hint": "install one, e.g. `uv tool install faster-whisper`, then rerun with --transcribe",
    }


def render_markdown(report: dict) -> str:
    c, l, s = report["container"], report["loudness"], report["shape"]
    lines = [
        f"# Audio probe — {report['file']}",
        "",
        "Measured, not heard. Judgment is the operator's.",
        "",
        "## Container",
        f"- duration: {c['duration_s']} s",
        f"- codec / rate / channels: {c['codec']} / {c['sample_rate_hz']} Hz / {c['channels']}",
        f"- bitrate: {c['bit_rate_kbps']} kbps",
        "",
        "## Loudness (EBU R128)",
        f"- integrated: {l.get('integrated_lufs')} LUFS",
        f"- true peak: {l.get('true_peak_dbtp')} dBTP",
        f"- loudness range: {l.get('loudness_range_lu')} LU",
        "",
        "## Shape",
        f"- leading silence: {s['leading_silence_s']} s",
        f"- trailing silence: {s['trailing_silence_s']} s",
        f"- peak energy at: {s['peak_energy_at_s']} s",
        f"- dynamic span: {s['dynamic_span_db']} dB",
        f"- internal silences: {len(s['internal_silences'])}",
        "",
        "### Section-boundary candidates",
    ]
    if s["largest_energy_changes"]:
        lines += [f"- {j['at_s']} s — energy {j['delta']:+.1f}"
                  for j in s["largest_energy_changes"]]
    else:
        lines.append("- none above threshold: the take is dynamically flat")

    flags = report["flags"]
    lines += ["", "## Flags"]
    lines += [f"- {f}" for f in flags] if flags else ["- none"]

    if report.get("transcript", {}).get("text"):
        lines += ["", "## Transcript", "", "```text", report["transcript"]["text"], "```", "",
                  "Diff this against `lyrics.md`. Any mismatch on a hook word is unrecoverable "
                  "in this take and requires regeneration, not repair."]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audio", type=Path)
    ap.add_argument("--session", type=Path, help="session dir to write probe artifacts into")
    ap.add_argument("--take", type=int, default=1)
    ap.add_argument("--transcribe", action="store_true", help="run local ASR (opt-in)")
    ap.add_argument("--lyrics", type=Path, help="lyrics file to note alongside the transcript")
    args = ap.parse_args()

    if not args.audio.exists():
        sys.exit(f"not found: {args.audio}")

    container = probe_container(args.audio)
    loudness = measure_loudness(args.audio)
    times, rms_db = energy_curve(args.audio)
    shape = analyze_shape(times, rms_db)

    flags: list[str] = []
    tp = loudness.get("true_peak_dbtp")
    if tp is not None and tp > -0.1:
        flags.append(f"true peak {tp} dBTP — inter-sample clipping likely on lossy playback")
    if shape["leading_silence_s"] >= 2.0:
        flags.append(f"{shape['leading_silence_s']} s of dead air before the first sound")
    if shape["trailing_silence_s"] >= 3.0:
        flags.append(f"{shape['trailing_silence_s']} s of trailing silence — trim before release")
    if shape["dynamic_span_db"] < 12:
        flags.append(f"dynamic span only {shape['dynamic_span_db']} dB — the arc may be flat")
    lra = loudness.get("loudness_range_lu")
    if lra is not None and lra < 3:
        flags.append(f"loudness range {lra} LU — heavily compressed, little section contrast")
    if container["duration_s"] < 30:
        flags.append("under 30 s — likely a truncated or failed generation")

    report = {
        "file": str(args.audio),
        "take": args.take,
        "container": container,
        "loudness": loudness,
        "shape": shape,
        "flags": flags,
    }
    if args.transcribe:
        report["transcript"] = transcribe(args.audio)
        if args.lyrics:
            report["transcript"]["compare_against"] = str(args.lyrics)

    markdown = render_markdown(report)
    if args.session:
        args.session.mkdir(parents=True, exist_ok=True)
        (args.session / f"probe-take-{args.take}.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8")
        (args.session / f"probe-take-{args.take}.md").write_text(markdown, encoding="utf-8")
        print(f"wrote {args.session / f'probe-take-{args.take}.md'}")
    print(markdown)


if __name__ == "__main__":
    main()
