#!/usr/bin/env python3
"""Install Agentic Music Producer OS into Hermes without copying secrets."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
import tempfile
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Mapping

FORBIDDEN_NAMES = {
    ".env",
    "auth.json",
    "state.db",
    "state.db-shm",
    "state.db-wal",
    ".git",
    ".hg",
    ".svn",
    ".jj",
    "sessions",
    "memories",
    "logs",
}
WINDOWS_RESERVED_NAMES = {
    "aux",
    "clock$",
    "con",
    "nul",
    "prn",
    *(f"com{number}" for number in range(1, 10)),
    *(f"lpt{number}" for number in range(1, 10)),
}


def _distribution_owned(repo_root: Path) -> list[str]:
    manifest = repo_root / "distribution.yaml"
    if not manifest.is_file():
        raise ValueError(f"Missing distribution manifest: {manifest}")

    owned: list[str] = []
    in_owned = False
    for raw_line in manifest.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if raw_line.startswith(("distribution_owned:", "distribution-owned:")):
            in_owned = True
            continue
        if in_owned and raw_line.startswith("  - "):
            owned.append(stripped[2:].strip().strip("'\""))
            continue
        if in_owned and stripped and not raw_line.startswith(" "):
            break

    if "distribution.yaml" not in owned:
        owned.insert(0, "distribution.yaml")
    return owned


def _ignore_profile_runtime(_directory: str, names: list[str]) -> list[str]:
    return [
        name
        for name in names
        if name in {"__pycache__", ".pytest_cache"}
        or name.endswith((".pyc", ".pyo"))
    ]


def _is_reparse_point(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        attributes = getattr(path.lstat(), "st_file_attributes", 0)
    except FileNotFoundError:
        return False
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def _validate_component(path: Path, label: str) -> None:
    if _is_reparse_point(path):
        raise ValueError(f"{label} contains a symlink or reparse point: {path}")
    if path.name.casefold() in FORBIDDEN_NAMES:
        raise ValueError(f"{label} contains forbidden user state: {path}")
    if os.name == "nt":
        name = path.name.rstrip(" .")
        stem = name.split(".", 1)[0].casefold()
        if ":" in name or stem in WINDOWS_RESERVED_NAMES:
            raise ValueError(f"{label} contains an unsafe Windows path: {path}")


def _validated_tree(root: Path, label: str) -> list[Path]:
    """Return a contained tree without traversing links, junctions, or reparse points."""

    root = Path(root)
    _validate_component(root, label)
    root_resolved = root.resolve(strict=True)
    found = [root]
    pending = [root]
    while pending:
        current = pending.pop()
        if not current.is_dir():
            continue
        with os.scandir(current) as entries:
            for entry in entries:
                path = Path(entry.path)
                _validate_component(path, label)
                try:
                    path.resolve(strict=True).relative_to(root_resolved)
                except ValueError as exc:
                    raise ValueError(f"{label} escapes its source root: {path}") from exc
                found.append(path)
                if entry.is_dir(follow_symlinks=False):
                    pending.append(path)
    return found


@contextmanager
def stage_profile_payload(repo_root: Path):
    """Stage only distribution-owned top-level entries for Hermes install."""

    repo_root = repo_root.resolve()
    with tempfile.TemporaryDirectory(prefix="music_producer_profile_") as tmp:
        staged = Path(tmp)
        for name in _distribution_owned(repo_root):
            rel = Path(name)
            if rel.is_absolute() or len(rel.parts) != 1 or name in {".", ".."}:
                raise ValueError(f"Unsafe distribution-owned path: {name}")
            source = repo_root / rel
            if not source.exists():
                raise ValueError(f"Distribution-owned path is missing: {source}")
            _validated_tree(source, "Distribution-owned path")

            destination = staged / rel
            if source.is_dir():
                shutil.copytree(source, destination, ignore=_ignore_profile_runtime)
            else:
                shutil.copy2(source, destination)
        yield staged


def resolve_hermes_home(
    environment: Mapping[str, str] | None = None,
    platform_name: str | None = None,
) -> Path:
    environment = environment or os.environ
    explicit = environment.get("HERMES_HOME")
    if explicit:
        return Path(explicit)
    platform_name = platform_name or os.name
    if platform_name == "nt":
        local_app_data = environment.get("LOCALAPPDATA")
        if not local_app_data:
            raise RuntimeError("LOCALAPPDATA is required to resolve Hermes home on Windows")
        return Path(local_app_data) / "hermes"
    return Path(environment.get("HOME", str(Path.home()))) / ".hermes"


def _frontmatter_name(skill_file: Path) -> str:
    text = skill_file.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValueError(f"missing YAML frontmatter: {skill_file}")
    for line in text.splitlines()[1:]:
        if line.strip() == "---":
            break
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip('"\'')
    raise ValueError(f"missing frontmatter name: {skill_file}")


def discover_skill_dirs(repo_root: Path) -> list[Path]:
    skills_root = Path(repo_root) / "skills"
    if not skills_root.is_dir():
        return []
    found: list[Path] = []
    for candidate in sorted(skills_root.iterdir(), key=lambda path: path.name.casefold()):
        skill_file = candidate / "SKILL.md"
        if candidate.is_dir() and skill_file.is_file():
            name = _frontmatter_name(skill_file)
            if name != candidate.name:
                raise ValueError(
                    f"skill frontmatter name '{name}' does not match directory '{candidate.name}'"
                )
            found.append(candidate)
    return found


def _validate_skill_tree(skill_dir: Path) -> None:
    _validated_tree(skill_dir, "Skill payload")


def _tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    root = Path(root)
    paths = _validated_tree(root, "Skill payload")
    for path in sorted(paths[1:], key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0dir\0" if path.is_dir() else b"\0file\0")
        if path.is_file():
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(chunk)
    return digest.hexdigest()


def _skill_ledger_path(hermes_home: Path) -> Path:
    return Path(hermes_home) / "local" / "music-producer-os" / "skill-install.json"


def _read_skill_ledger(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise RuntimeError(f"invalid skill installation ledger: {path}") from exc
    skills = payload.get("skills")
    if not isinstance(skills, dict) or not all(
        isinstance(name, str) and isinstance(value, str) for name, value in skills.items()
    ):
        raise RuntimeError(f"invalid skill installation ledger: {path}")
    return skills


def _write_skill_ledger(path: Path, skills: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps({"schema_version": 1, "skills": skills}, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _replace_tree(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = destination.parent / f".{destination.name}.install-{uuid.uuid4().hex}"
    backup = destination.parent / f".{destination.name}.backup-{uuid.uuid4().hex}"
    shutil.copytree(source, staging)
    try:
        if destination.exists():
            destination.replace(backup)
        staging.replace(destination)
        if backup.exists():
            shutil.rmtree(backup)
    except Exception:
        if backup.exists():
            if destination.exists():
                shutil.rmtree(destination, ignore_errors=True)
            backup.replace(destination)
        raise
    finally:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        if backup.exists():
            shutil.rmtree(backup, ignore_errors=True)


def copy_skills(
    repo_root: Path,
    hermes_home: Path,
    dry_run: bool = False,
    force: bool = False,
) -> dict:
    repo_root = Path(repo_root)
    hermes_home = Path(hermes_home)
    skills = discover_skill_dirs(repo_root)
    ledger_path = _skill_ledger_path(hermes_home)
    ledger = _read_skill_ledger(ledger_path)
    installed: list[str] = []
    actions: dict[str, str] = {}
    plans: list[tuple[Path, Path, str]] = []

    for skill_dir in skills:
        _validate_skill_tree(skill_dir)
        name = skill_dir.name
        destination = hermes_home / "skills" / name
        source_hash = _tree_hash(skill_dir)
        installed.append(name)
        action = "install"
        if destination.exists():
            destination_hash = _tree_hash(destination)
            previous_hash = ledger.get(name)
            if destination_hash == source_hash:
                action = "unchanged"
            elif previous_hash is None and not force:
                raise RuntimeError(
                    f"existing unowned skill would be replaced: {destination}; "
                    "rerun with --force-skills"
                )
            elif previous_hash != destination_hash and not force:
                raise RuntimeError(
                    f"user-modified skill would be replaced: {destination}; "
                    "rerun with --force-skills"
                )
            else:
                action = "update"
        actions[name] = action
        plans.append((skill_dir, destination, source_hash))

    if not dry_run:
        for skill_dir, destination, source_hash in plans:
            if actions[skill_dir.name] != "unchanged":
                _replace_tree(skill_dir, destination)
            ledger[skill_dir.name] = source_hash
        _write_skill_ledger(ledger_path, ledger)

    return {
        "status": "dry-run" if dry_run else "installed",
        "dry_run": dry_run,
        "hermes_home": str(hermes_home),
        "installed": installed,
        "actions": actions,
        "force": force,
    }


def discover_cua_driver(environment: Mapping[str, str] | None = None) -> Path | None:
    environment = environment or os.environ
    explicit = environment.get("HERMES_CUA_DRIVER_CMD")
    if explicit and Path(explicit).is_file():
        return Path(explicit)

    discovered = shutil.which("cua-driver")
    if discovered:
        return Path(discovered)

    local_app_data = environment.get("LOCALAPPDATA")
    if local_app_data:
        standard = (
            Path(local_app_data)
            / "Programs"
            / "Cua"
            / "cua-driver"
            / "bin"
            / "cua-driver.exe"
        )
        if standard.is_file():
            return standard
    return None


def ensure_profile_driver_env(profile_dir: Path, driver: Path) -> dict:
    """Create a non-secret profile .env only when the user has no .env yet."""

    profile_dir = Path(profile_dir)
    driver = Path(driver)
    if not driver.is_file():
        raise FileNotFoundError(f"cua-driver not found: {driver}")
    env_file = profile_dir / ".env"
    if env_file.exists():
        return {"status": "skipped-existing-env", "path": str(env_file)}

    profile_dir.mkdir(parents=True, exist_ok=True)
    env_file.write_text(
        "# Local non-secret computer-use binary override.\n"
        f"HERMES_CUA_DRIVER_CMD={driver.resolve().as_posix()}\n",
        encoding="utf-8",
    )
    return {"status": "created", "path": str(env_file)}


def build_profile_install_command(
    repo_root: Path,
    profile_name: str,
    force: bool = False,
) -> list[str]:
    if not profile_name or any(character not in "abcdefghijklmnopqrstuvwxyz0123456789-" for character in profile_name):
        raise ValueError("profile_name must use lowercase letters, digits, or hyphens")
    command = [
        "hermes",
        "profile",
        "install",
        Path(repo_root).as_posix(),
        "--name",
        profile_name,
        "--alias",
    ]
    if force:
        command.append("--force")
    command.append("-y")
    return command


def install_profile(
    repo_root: Path,
    profile_name: str,
    hermes_home: Path | None = None,
    dry_run: bool = False,
    force: bool = False,
) -> dict:
    hermes_home = Path(hermes_home or resolve_hermes_home()).resolve()
    profile_dir = hermes_home / "profiles" / profile_name
    safe_source = hermes_home / "local" / "profile-sources" / profile_name
    exists = profile_dir.exists()
    if exists and not force and not dry_run:
        raise RuntimeError(
            f"profile already exists: {profile_dir}; rerun with --force-profile "
            "after reviewing the dry run"
        )
    command = build_profile_install_command(safe_source, profile_name, force=force)
    if dry_run:
        return {
            "status": "dry-run",
            "command": command,
            "safe_source": str(safe_source),
            "profile_exists": exists,
            "requires_force": exists and not force,
        }

    with stage_profile_payload(repo_root) as staged:
        _replace_tree(staged, safe_source)
        environment = os.environ.copy()
        environment["HERMES_HOME"] = str(hermes_home)
        try:
            completed = subprocess.run(
                command,
                check=True,
                text=True,
                capture_output=True,
                env=environment,
            )
        except subprocess.CalledProcessError as exc:
            details = (exc.stderr or exc.stdout or str(exc)).strip()
            raise RuntimeError(f"Hermes profile installation failed: {details}") from exc

    return {
        "status": "installed",
        "command": command,
        "safe_source": str(safe_source),
        "stdout": completed.stdout.strip(),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repository root containing distribution.yaml and skills/",
    )
    parser.add_argument("--hermes-home", type=Path)
    parser.add_argument("--profile-name", default="music-producer")
    parser.add_argument("--install-profile", action="store_true")
    parser.add_argument("--force-profile", action="store_true")
    parser.add_argument("--force-skills", action="store_true")
    parser.add_argument("--no-mirror-default", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = _parser().parse_args()
    repo_root = args.repo_root.resolve()
    if not (repo_root / "distribution.yaml").is_file():
        raise FileNotFoundError(f"distribution.yaml not found at {repo_root}")
    receipt: dict[str, object] = {"repo_root": str(repo_root)}
    hermes_home = args.hermes_home or resolve_hermes_home()

    skill_preview = None
    if not args.no_mirror_default:
        skill_preview = copy_skills(
            repo_root,
            hermes_home,
            dry_run=True,
            force=args.force_skills,
        )

    profile_preview = None
    if args.install_profile:
        profile_preview = install_profile(
            repo_root,
            args.profile_name,
            hermes_home=hermes_home,
            dry_run=True,
            force=args.force_profile,
        )
        if profile_preview["requires_force"] and not args.dry_run:
            raise RuntimeError(
                f"profile already exists: {hermes_home / 'profiles' / args.profile_name}; "
                "rerun with --force-profile after reviewing the dry run"
            )

    if args.dry_run:
        if skill_preview is not None:
            receipt["default_skills"] = skill_preview
        if profile_preview is not None:
            driver = discover_cua_driver()
            if driver:
                profile_preview["computer_use_env"] = {
                    "status": "dry-run",
                    "driver": str(driver),
                }
            receipt["profile"] = profile_preview
        print(json.dumps(receipt, ensure_ascii=False))
        return 0

    if args.install_profile:
        profile_receipt = install_profile(
            repo_root,
            args.profile_name,
            hermes_home=hermes_home,
            dry_run=False,
            force=args.force_profile,
        )
        driver = discover_cua_driver()
        if driver:
            profile_receipt["computer_use_env"] = ensure_profile_driver_env(
                hermes_home / "profiles" / args.profile_name,
                driver,
            )
        else:
            profile_receipt["computer_use_env"] = {"status": "driver-not-found"}
        receipt["profile"] = profile_receipt

    if not args.no_mirror_default:
        receipt["default_skills"] = copy_skills(
            repo_root,
            hermes_home,
            dry_run=False,
            force=args.force_skills,
        )
    print(json.dumps(receipt, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
