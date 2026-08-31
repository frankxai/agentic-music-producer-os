#!/usr/bin/env python3
"""Deterministic score compiler: compact DSL -> MusicXML, MIDI, ABC, sheets, tabs."""

from __future__ import annotations

import json
import math
import re
import struct
import wave
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

PITCH_CLASS = {
    "C": 0,
    "C#": 1,
    "DB": 1,
    "D": 2,
    "D#": 3,
    "EB": 3,
    "E": 4,
    "FB": 4,
    "E#": 5,
    "F": 5,
    "F#": 6,
    "GB": 6,
    "G": 7,
    "G#": 8,
    "AB": 8,
    "A": 9,
    "A#": 10,
    "BB": 10,
    "B": 11,
    "CB": 11,
    "B#": 0,
}
STEP_ALTER = {
    "C": ("C", 0),
    "C#": ("C", 1),
    "DB": ("D", -1),
    "D": ("D", 0),
    "D#": ("D", 1),
    "EB": ("E", -1),
    "E": ("E", 0),
    "FB": ("F", -1),
    "E#": ("F", 1),
    "F": ("F", 0),
    "F#": ("F", 1),
    "GB": ("G", -1),
    "G": ("G", 0),
    "G#": ("G", 1),
    "AB": ("A", -1),
    "A": ("A", 0),
    "A#": ("A", 1),
    "BB": ("B", -1),
    "B": ("B", 0),
    "CB": ("C", -1),
    "B#": ("C", 1),
}
DURATION_DIVS = {"w": 16, "h": 8, "q": 4, "e": 2, "s": 1, "x": 1}
DURATION_TYPE = {
    16: "whole",
    8: "half",
    4: "quarter",
    2: "eighth",
    1: "16th",
}
ABC_LEN = {16: "1", 8: "2", 4: "4", 2: "8", 1: "16"}
GUITAR_OPEN = [("E", 4, 64), ("B", 3, 59), ("G", 3, 55), ("D", 3, 50), ("A", 2, 45), ("E", 2, 40)]
TICKS_PER_Q = 480
DIVISIONS = 4
NOTE_RE = re.compile(
    r"(?P<rest>r)|(?P<chord>\[[^\]]+\])|(?P<pitch>[A-Ga-g](?:[#bB])?\d)",
)
TOKEN_RE = re.compile(
    r"(?:r|\[[^\]]+\]|[A-Ga-g](?:[#bB])?\d)(?P<dur>[whqesx])(?P<dot>\.?)(?P<vel>v\d{1,3})?"
)
HEADER_RE = re.compile(r"^@(?P<key>[A-Za-z0-9_-]+)\s+(?P<value>.+?)\s*$")
PART_RE = re.compile(r"^\[(?P<name>[^\]]+)\]\s*$")
VOICE_RE = re.compile(
    r"^(?P<num>\d+)\s+(?P<voice>RH|LH|P|V1|V2|VA|VC|GTR)\s*:\s*(?P<body>.+)$",
    re.IGNORECASE,
)


@dataclass
class NoteEvent:
    pitches: list[str]
    divisions: int
    dotted: bool
    velocity: int
    rest: bool = False

    @property
    def ticks(self) -> int:
        value = (self.divisions * TICKS_PER_Q) // DIVISIONS
        if self.dotted:
            value = int(value * 1.5)
        return value

    @property
    def xml_duration(self) -> int:
        value = self.divisions
        if self.dotted:
            value = int(value * 1.5)
        return value


@dataclass
class Measure:
    number: int
    voices: dict[str, list[NoteEvent]] = field(default_factory=dict)


@dataclass
class Part:
    name: str
    instrument: str
    measures: list[Measure] = field(default_factory=list)

    def measure(self, number: int) -> Measure:
        for item in self.measures:
            if item.number == number:
                return item
        measure = Measure(number=number)
        self.measures.append(measure)
        self.measures.sort(key=lambda item: item.number)
        return measure


@dataclass
class Score:
    title: str
    composer: str
    kind: str
    key: str
    time: str
    tempo: int
    thesis: str
    motif: str
    form: str
    parts: list[Part] = field(default_factory=list)

    def part(self, name: str, instrument: str | None = None) -> Part:
        for item in self.parts:
            if item.name == name:
                return item
        part = Part(name=name, instrument=instrument or name.lower())
        self.parts.append(part)
        return part


def midi_number(pitch: str) -> int:
    match = re.fullmatch(r"([A-Ga-g])([#bB]?)(\d)", pitch)
    if not match:
        raise ValueError(f"invalid pitch: {pitch}")
    letter, accidental, octave = match.group(1).upper(), match.group(2), int(match.group(3))
    token = letter + accidental.upper().replace("B", "B")
    if accidental == "b":
        token = letter + "B"
    elif accidental == "#":
        token = letter + "#"
    else:
        token = letter
    return 12 * (octave + 1) + PITCH_CLASS[token]


def normalize_pitch(pitch: str) -> str:
    match = re.fullmatch(r"([A-Ga-g])([#bB]?)(\d)", pitch)
    if not match:
        raise ValueError(f"invalid pitch: {pitch}")
    letter = match.group(1).upper()
    accidental = match.group(2)
    octave = match.group(3)
    if accidental == "b":
        accidental = "b"
    return f"{letter}{accidental}{octave}"


def parse_note_token(token: str, default_velocity: int = 72) -> NoteEvent:
    match = TOKEN_RE.fullmatch(token.strip())
    if not match:
        raise ValueError(f"invalid note token: {token}")
    duration = DURATION_DIVS[match.group("dur")]
    dotted = bool(match.group("dot"))
    velocity = default_velocity
    if match.group("vel"):
        velocity = max(1, min(127, int(match.group("vel")[1:])))
    body = token.strip()
    if body.startswith("r"):
        return NoteEvent(pitches=[], divisions=duration, dotted=dotted, velocity=velocity, rest=True)
    if body.startswith("["):
        inner = body[1 : body.index("]")]
        pitches = [normalize_pitch(item) for item in re.findall(r"[A-Ga-g](?:[#bB])?\d", inner)]
        if not pitches:
            raise ValueError(f"empty chord: {token}")
        return NoteEvent(pitches=pitches, divisions=duration, dotted=dotted, velocity=velocity)
    pitch_match = NOTE_RE.match(body)
    if not pitch_match or not pitch_match.group("pitch"):
        raise ValueError(f"invalid note token: {token}")
    return NoteEvent(
        pitches=[normalize_pitch(pitch_match.group("pitch"))],
        divisions=duration,
        dotted=dotted,
        velocity=velocity,
    )


def parse_voice_body(body: str, default_velocity: int = 72) -> list[NoteEvent]:
    tokens = [item for item in body.replace("|", " ").split() if item]
    return [parse_note_token(token, default_velocity=default_velocity) for token in tokens]


def parse_score_text(text: str) -> Score:
    headers: dict[str, str] = {}
    score = Score(
        title="Untitled",
        composer="Frank / Agentic Composer OS",
        kind="piano",
        key="C major",
        time="4/4",
        tempo=80,
        thesis="",
        motif="",
        form="",
        parts=[],
    )
    current_part: Part | None = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        header = HEADER_RE.match(line)
        if header:
            headers[header.group("key").casefold()] = header.group("value").strip()
            continue
        part_match = PART_RE.match(line)
        if part_match:
            name = part_match.group("name").strip()
            instrument = name.lower()
            if "piano" in instrument:
                instrument = "piano"
            elif "guitar" in instrument:
                instrument = "guitar"
            elif "violin" in instrument:
                instrument = "violin"
            elif "viola" in instrument:
                instrument = "viola"
            elif "cello" in instrument:
                instrument = "cello"
            current_part = score.part(name, instrument)
            continue
        voice_match = VOICE_RE.match(line)
        if voice_match:
            if current_part is None:
                current_part = score.part("Piano", "piano")
            number = int(voice_match.group("num"))
            voice = voice_match.group("voice").upper()
            events = parse_voice_body(voice_match.group("body"))
            current_part.measure(number).voices[voice] = events
            continue
        raise ValueError(f"unrecognized score line: {line}")

    score.title = headers.get("title", score.title)
    score.composer = headers.get("composer", score.composer)
    score.kind = headers.get("kind", score.kind)
    score.key = headers.get("key", score.key)
    score.time = headers.get("time", score.time)
    score.tempo = int(headers.get("tempo", str(score.tempo)))
    score.thesis = headers.get("thesis", "")
    score.motif = headers.get("motif", "")
    score.form = headers.get("form", "")
    if not score.parts:
        raise ValueError("score has no parts")
    return score


def beats_per_measure(time_sig: str) -> int:
    beats, unit = time_sig.split("/")
    return int(beats) * (DIVISIONS * 4 // int(unit))


def validate_score(score: Score) -> list[str]:
    issues: list[str] = []
    expected = beats_per_measure(score.time)
    if not score.motif:
        issues.append("missing motif")
    if not score.thesis:
        issues.append("missing thesis")
    if score.tempo < 40 or score.tempo > 220:
        issues.append(f"implausible tempo: {score.tempo}")
    for part in score.parts:
        if not part.measures:
            issues.append(f"{part.name}: no measures")
        numbers = [measure.number for measure in part.measures]
        if numbers != list(range(1, len(numbers) + 1)):
            issues.append(f"{part.name}: measures must be contiguous from 1")
        for measure in part.measures:
            if not measure.voices:
                issues.append(f"{part.name} m{measure.number}: empty")
            for voice, events in measure.voices.items():
                total = sum(event.xml_duration for event in events)
                if total != expected:
                    issues.append(
                        f"{part.name} m{measure.number} {voice}: duration {total} != {expected}"
                    )
    return issues


def key_fifths(key: str) -> tuple[int, str]:
    table = {
        "c major": (0, "major"),
        "a minor": (0, "minor"),
        "g major": (1, "major"),
        "e minor": (1, "minor"),
        "d major": (2, "major"),
        "b minor": (2, "minor"),
        "a major": (3, "major"),
        "f# minor": (3, "minor"),
        "f major": (-1, "major"),
        "d minor": (-1, "minor"),
        "bb major": (-2, "major"),
        "g minor": (-2, "minor"),
        "eb major": (-3, "major"),
        "c minor": (-3, "minor"),
    }
    return table.get(key.casefold(), (0, "major" if "major" in key.casefold() else "minor"))


def _vlq(value: int) -> bytes:
    buffer = [value & 0x7F]
    value >>= 7
    while value:
        buffer.append(0x80 | (value & 0x7F))
        value >>= 7
    return bytes(reversed(buffer))


def write_midi(score: Score, path: Path) -> Path:
    tracks = [_tempo_track(score.tempo)]
    channel = 0
    for part in score.parts:
        tracks.append(_part_track(part, channel, program=_program_for(part.instrument)))
        channel = min(15, channel + 1)
    payload = b"MThd" + struct.pack(">IHHH", 6, 1, len(tracks), TICKS_PER_Q)
    for track in tracks:
        payload += b"MTrk" + struct.pack(">I", len(track)) + track
    path.write_bytes(payload)
    return path


def _tempo_track(bpm: int) -> bytes:
    mpq = int(60_000_000 / bpm)
    events = _vlq(0) + b"\xff\x51\x03" + struct.pack(">I", mpq)[1:]
    events += _vlq(0) + b"\xff\x2f\x00"
    return events


def _program_for(instrument: str) -> int:
    mapping = {
        "piano": 0,
        "guitar": 24,
        "violin": 40,
        "viola": 41,
        "cello": 42,
        "strings": 48,
    }
    return mapping.get(instrument, 0)


def _part_track(part: Part, channel: int, program: int) -> bytes:
    events: list[tuple[int, bytes]] = [(0, bytes([0xC0 | channel, program]))]
    cursor = 0
    for measure in part.measures:
        voice_events: list[tuple[int, bytes]] = []
        for events_in_voice in measure.voices.values():
            offset = cursor
            for event in events_in_voice:
                if not event.rest:
                    for pitch in event.pitches:
                        note = midi_number(pitch)
                        voice_events.append((offset, bytes([0x90 | channel, note, event.velocity])))
                        voice_events.append(
                            (offset + event.ticks, bytes([0x80 | channel, note, 0]))
                        )
                offset += event.ticks
        cursor = max([cursor] + [tick for tick, _ in voice_events], default=cursor)
        events.extend(voice_events)
    events.sort(key=lambda item: (item[0], item[1][0] & 0xF0))
    blob = b""
    last = 0
    for tick, data in events:
        blob += _vlq(max(0, tick - last)) + data
        last = tick
    blob += _vlq(0) + b"\xff\x2f\x00"
    return blob


def write_musicxml(score: Score, path: Path) -> Path:
    fifths, mode = key_fifths(score.key)
    beats, beat_type = score.time.split("/")
    parts_xml = []
    list_xml = []
    for index, part in enumerate(score.parts, start=1):
        pid = f"P{index}"
        list_xml.append(
            f'    <score-part id="{pid}"><part-name>{escape(part.name)}</part-name></score-part>'
        )
        measures = []
        for measure in part.measures:
            attrs = ""
            if measure.number == 1:
                attrs = f"""      <attributes>
        <divisions>{DIVISIONS}</divisions>
        <key><fifths>{fifths}</fifths><mode>{mode}</mode></key>
        <time><beats>{beats}</beats><beat-type>{beat_type}</beat-type></time>
        <clef><sign>{"F" if part.instrument in {"cello"} else "G"}</sign><line>{"4" if part.instrument in {"cello"} else "2"}</line></clef>
      </attributes>"""
            notes_xml = []
            voices = list(measure.voices.items())
            for voice_index, (voice_name, events) in enumerate(voices):
                if voice_index:
                    notes_xml.append("      <backup><duration>{}</duration></backup>".format(beats_per_measure(score.time)))
                voice_id = 1 if voice_name == "RH" else 2 if voice_name == "LH" else voice_index + 1
                staff = 1
                if voice_name == "LH":
                    staff = 2
                for event in events:
                    notes_xml.append(_musicxml_event(event, voice_id, staff, part.instrument))
            if "LH" in measure.voices and measure.number == 1:
                attrs = attrs.replace(
                    "</clef>",
                    '</clef>\n        <staves>2</staves>\n        <clef number="1"><sign>G</sign><line>2</line></clef>\n        <clef number="2"><sign>F</sign><line>4</line></clef>',
                    1,
                ) if "<staves>" not in attrs else attrs
                if "<staves>" not in attrs:
                    attrs = attrs.replace(
                        "</attributes>",
                        "        <staves>2</staves>\n      </attributes>",
                    )
            measures.append(
                f'    <measure number="{measure.number}">\n{attrs}\n' + "\n".join(notes_xml) + "\n    </measure>"
            )
        parts_xml.append(f'  <part id="{pid}">\n' + "\n".join(measures) + "\n  </part>")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <work><work-title>{escape(score.title)}</work-title></work>
  <identification><creator type="composer">{escape(score.composer)}</creator></identification>
  <part-list>
{chr(10).join(list_xml)}
  </part-list>
{chr(10).join(parts_xml)}
</score-partwise>
"""
    path.write_text(xml, encoding="utf-8")
    return path


def _musicxml_event(event: NoteEvent, voice: int, staff: int, instrument: str) -> str:
    if event.rest:
        return (
            f'      <note><rest/>'
            f"<duration>{event.xml_duration}</duration>"
            f"<voice>{voice}</voice>"
            f"<type>{DURATION_TYPE[event.divisions]}</type>"
            f'{"<dot/>" if event.dotted else ""}'
            f"<staff>{staff}</staff></note>"
        )
    chunks = []
    for index, pitch in enumerate(event.pitches):
        step, alter = _step_alter(pitch)
        octave = pitch[-1]
        chord = "<chord/>" if index else ""
        chunks.append(
            f"      <note>{chord}<pitch><step>{step}</step>"
            f"{f'<alter>{alter}</alter>' if alter else ''}"
            f"<octave>{octave}</octave></pitch>"
            f"<duration>{event.xml_duration}</duration>"
            f"<voice>{voice}</voice><type>{DURATION_TYPE[event.divisions]}</type>"
            f'{"<dot/>" if event.dotted else ""}<staff>{staff}</staff></note>'
        )
    return "\n".join(chunks)


def _step_alter(pitch: str) -> tuple[str, int]:
    match = re.fullmatch(r"([A-G])([#b]?)(\d)", normalize_pitch(pitch))
    if not match:
        raise ValueError(f"invalid pitch: {pitch}")
    token = match.group(1) + match.group(2).upper().replace("B", "B")
    if match.group(2) == "b":
        token = match.group(1) + "B"
    elif match.group(2) == "#":
        token = match.group(1) + "#"
    else:
        token = match.group(1)
    return STEP_ALTER[token]


def write_abc(score: Score, path: Path) -> Path:
    fifths, mode = key_fifths(score.key)
    key_name = score.key.replace(" minor", "m").replace(" major", "")
    lines = [
        "%abc-2.1",
        f"T:{score.title}",
        f"C:{score.composer}",
        f"M:{score.time}",
        f"Q:1/4={score.tempo}",
        f"K:{key_name}",
        f"R:{score.kind}",
        f"N:motif {score.motif}",
    ]
    melody = _lead_events(score)
    rendered = []
    for event in melody:
        rendered.append(_abc_event(event))
    lines.append(" ".join(rendered))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _abc_event(event: NoteEvent) -> str:
    length = ABC_LEN[event.divisions] + ("." if event.dotted else "")
    if event.rest:
        return f"z{length}"
    notes = "".join(_abc_pitch(pitch) for pitch in event.pitches)
    if len(event.pitches) > 1:
        return f"[{notes}]{length}"
    return f"{notes}{length}"


def _abc_pitch(pitch: str) -> str:
    step, alter = _step_alter(pitch)
    octave = int(pitch[-1])
    accidental = "^" if alter == 1 else "_" if alter == -1 else ""
    if octave >= 5:
        body = step.lower() + "'" * (octave - 5)
    else:
        body = step.upper() + "," * (4 - octave)
    return accidental + body


def _lead_events(score: Score) -> list[NoteEvent]:
    part = score.parts[0]
    events: list[NoteEvent] = []
    for measure in part.measures:
        if "RH" in measure.voices:
            events.extend(measure.voices["RH"])
        elif "P" in measure.voices:
            events.extend(measure.voices["P"])
        else:
            first = next(iter(measure.voices.values()))
            events.extend(first)
    return events


def guitar_position(midi: int) -> tuple[int, int]:
    candidates = []
    for string_index, (_name, _oct, open_midi) in enumerate(GUITAR_OPEN):
        fret = midi - open_midi
        if 0 <= fret <= 19:
            score = abs(fret - 5) + string_index * 0.15
            candidates.append((score, string_index, fret))
    if not candidates:
        return 0, max(0, midi - GUITAR_OPEN[0][2])
    _score, string_index, fret = min(candidates)
    return string_index, fret


def write_guitar_tab(score: Score, path: Path) -> Path:
    events = _lead_events(score)
    strings = [["-"] * max(1, sum(2 if event.rest else 3 for event in events)) for _ in range(6)]
    cursor = 0
    for event in events:
        width = 3 if not event.rest else 2
        if not event.rest:
            midi = midi_number(event.pitches[0])
            string_index, fret = guitar_position(midi)
            token = str(fret)
            strings[string_index][cursor : cursor + len(token)] = list(token)
        cursor += width
    names = ["e", "B", "G", "D", "A", "E"]
    lines = [
        f"{score.title} — electric/acoustic guitar tab",
        f"{score.key} · {score.time} · q={score.tempo} · melody reduction",
        f"Motif: {score.motif}",
        "Standard tuning",
        "",
    ]
    for name, row in zip(names, strings):
        lines.append(f"{name}|{''.join(row)}")
    lines.append("")
    lines.append("This is a melody reduction for practice, not a full arrangement.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_piano_sheet(score: Score, path: Path) -> Path:
    lines = [
        score.title,
        f"{score.composer}",
        f"{score.key} · {score.time} · q={score.tempo} · {score.kind}",
        f"Thesis: {score.thesis}",
        f"Motif: {score.motif}",
        f"Form: {score.form}",
        "",
        "Playable piano reduction. Import the MusicXML into MuseScore 4 for publication engraving.",
        "",
    ]
    piano = next((part for part in score.parts if part.instrument == "piano"), score.parts[0])
    for measure in piano.measures:
        rh = _voice_text(measure.voices.get("RH") or measure.voices.get("P") or [])
        lh = _voice_text(measure.voices.get("LH") or [])
        lines.append(f"m{measure.number:02d}  RH  {rh}")
        if lh:
            lines.append(f"     LH  {lh}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _voice_text(events: list[NoteEvent]) -> str:
    chunks = []
    for event in events:
        if event.rest:
            token = "r"
        else:
            token = "+".join(event.pitches)
        dur = {16: "w", 8: "h", 4: "q", 2: "e", 1: "s"}[event.divisions]
        if event.dotted:
            dur += "."
        chunks.append(f"{token}:{dur}")
    return "  ".join(chunks)


def write_lyria_prompt(score: Score, path: Path) -> Path:
    bars = max(len(part.measures) for part in score.parts)
    seconds = int(round((bars * 4 * 60) / score.tempo))
    prompt = f"""Instrumental only, no vocals. Original concert work, not a song cover.
Title: {score.title}.
{score.kind}; {score.key}; {score.time}; {score.tempo} BPM.
Emotional contract: {score.thesis}
Core motif: {score.motif}
Form: {score.form}
Duration about {seconds} seconds.
Focal instruments: {", ".join(part.name for part in score.parts)}.
Play as a human performance with breath, rubato, and dynamic shape. Do not add drums unless the kind is dance. Do not add lyrics. End authored, not faded by accident.
[0:00 - 0:12] Expose the motif quietly.
Middle third: develop and raise pressure without losing the motif.
Final third: return the motif changed, then stop with intention.
"""
    path.write_text(prompt.strip() + "\n", encoding="utf-8")
    return path


def write_suno_bridge(score: Score, path: Path) -> Path:
    text = f"""TITLE: {score.title}

MODE: Custom Mode on. Instrumental on.

STYLE:
{score.kind}; {score.thesis}; {score.tempo} BPM {score.time} in {score.key}; focal {", ".join(part.name for part in score.parts)}; instrumental, no vocals; motif {score.motif}; form {score.form}; intimate opening, earned lift, authored ending; dry center, human dynamic shape.

EXCLUDE STYLES:
vocals, choir, named-artist imitation, trap hats, festival drop, long cinematic trailer intro, abrupt cut

LYRICS:
instrumental, no vocals

NOTE:
This is a promotional/performance packet derived from the score canon. The MusicXML/MIDI remain the work. One Create action only after taste review.
"""
    path.write_text(text, encoding="utf-8")
    return path


def render_preview_wav(score: Score, path: Path, sample_rate: int = 22050) -> Path:
    seconds_per_tick = 60.0 / (score.tempo * TICKS_PER_Q)
    events: list[tuple[float, float, int, int]] = []
    for part in score.parts:
        for voice_name in {name for measure in part.measures for name in measure.voices}:
            tick = 0
            for measure in part.measures:
                for event in measure.voices.get(voice_name, []):
                    start = tick * seconds_per_tick
                    end = (tick + event.ticks) * seconds_per_tick
                    if not event.rest:
                        for pitch in event.pitches:
                            events.append((start, end, midi_number(pitch), event.velocity))
                    tick += event.ticks
    duration = max((end for _s, end, _n, _v in events), default=1.0) + 1.2
    n_samples = int(duration * sample_rate)
    left = [0.0] * n_samples
    right = [0.0] * n_samples
    for start, end, note, velocity in events:
        freq = 440.0 * (2 ** ((note - 69) / 12))
        amp = (velocity / 127.0) * 0.18
        start_i = int(start * sample_rate)
        end_i = min(n_samples, int((end + 0.35) * sample_rate))
        length = max(1, end_i - start_i)
        pan = -0.2 if note < 60 else 0.15
        for i in range(length):
            t = i / sample_rate
            env = math.exp(-t * 2.8) * (1.0 - math.exp(-t * 90.0))
            sample = 0.0
            for harmonic, weight in ((1, 1.0), (2, 0.35), (3, 0.16), (4, 0.08), (6, 0.04)):
                sample += weight * math.sin(2 * math.pi * freq * harmonic * t)
            value = amp * env * sample
            idx = start_i + i
            left[idx] += value * (1 - pan)
            right[idx] += value * (1 + pan)
    peak = max(1e-9, max(abs(x) for x in left + right))
    scale = 0.92 / peak
    frames = bytearray()
    for l_s, r_s in zip(left, right):
        frames += struct.pack(
            "<hh",
            max(-32767, min(32767, int(l_s * scale * 32767))),
            max(-32767, min(32767, int(r_s * scale * 32767))),
        )
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(bytes(frames))
    return path


def compile_score(score: Score, out_dir: Path, preview: bool = False) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    issues = validate_score(score)
    if issues:
        raise ValueError("score failed validation:\n- " + "\n- ".join(issues))
    artifacts = {
        "musicxml": write_musicxml(score, out_dir / f"{_slug(score.title)}.musicxml"),
        "midi": write_midi(score, out_dir / f"{_slug(score.title)}.mid"),
        "abc": write_abc(score, out_dir / f"{_slug(score.title)}.abc"),
        "piano_sheet": write_piano_sheet(score, out_dir / f"{_slug(score.title)}.piano.txt"),
        "guitar_tab": write_guitar_tab(score, out_dir / f"{_slug(score.title)}.tab.txt"),
        "lyria_prompt": write_lyria_prompt(score, out_dir / "lyria-prompt.md"),
        "suno_bridge": write_suno_bridge(score, out_dir / "suno-bridge.md"),
    }
    manifest = {
        "title": score.title,
        "composer": score.composer,
        "kind": score.kind,
        "key": score.key,
        "time": score.time,
        "tempo": score.tempo,
        "thesis": score.thesis,
        "motif": score.motif,
        "form": score.form,
        "parts": [part.name for part in score.parts],
        "measures": max(len(part.measures) for part in score.parts),
        "artifacts": {key: str(value) for key, value in artifacts.items()},
    }
    if preview:
        wav = render_preview_wav(score, out_dir / f"{_slug(score.title)}.preview.wav")
        artifacts["preview_wav"] = wav
        manifest["artifacts"]["preview_wav"] = str(wav)
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    artifacts["manifest"] = out_dir / "manifest.json"
    return {key: str(value) for key, value in artifacts.items()}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")[:64] or "untitled"


def score_to_json(score: Score) -> dict[str, Any]:
    return {
        "title": score.title,
        "composer": score.composer,
        "kind": score.kind,
        "key": score.key,
        "time": score.time,
        "tempo": score.tempo,
        "thesis": score.thesis,
        "motif": score.motif,
        "form": score.form,
        "parts": [
            {
                "name": part.name,
                "instrument": part.instrument,
                "measures": [
                    {
                        "n": measure.number,
                        "voices": {
                            voice: [
                                {
                                    "pitches": event.pitches,
                                    "dur": event.divisions,
                                    "dot": event.dotted,
                                    "v": event.velocity,
                                    "rest": event.rest,
                                }
                                for event in events
                            ]
                            for voice, events in measure.voices.items()
                        },
                    }
                    for measure in part.measures
                ],
            }
            for part in score.parts
        ],
    }
