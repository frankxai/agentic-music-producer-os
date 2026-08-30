import os
import subprocess
import sys
import tempfile
import unittest
from subprocess import CalledProcessError, CompletedProcess
from pathlib import Path
from unittest.mock import patch

from scripts.install_machine import (
    _replace_tree,
    build_profile_install_command,
    copy_skills,
    discover_skill_dirs,
    ensure_profile_driver_env,
    install_profile,
    resolve_hermes_home,
    stage_profile_payload,
)


MINIMAL_SKILL = """---
name: {name}
description: Test skill.
---
# {name}
"""


class InstallMachineTests(unittest.TestCase):
    def make_repo(self, root: Path) -> Path:
        repo = root / "repo"
        (repo / "skills" / "alpha").mkdir(parents=True)
        (repo / "skills" / "alpha" / "SKILL.md").write_text(
            MINIMAL_SKILL.format(name="alpha"), encoding="utf-8"
        )
        (repo / "skills" / "beta").mkdir(parents=True)
        (repo / "skills" / "beta" / "SKILL.md").write_text(
            MINIMAL_SKILL.format(name="beta"), encoding="utf-8"
        )
        (repo / ".env").write_text("SECRET=never-copy\n", encoding="utf-8")
        (repo / ".git").mkdir()
        return repo

    def test_resolve_hermes_home_prefers_explicit_then_windows_default(self):
        explicit = resolve_hermes_home(
            {"HERMES_HOME": "D:/Hermes/Profile", "LOCALAPPDATA": "C:/Users/test/AppData/Local"},
            platform_name="nt",
        )
        fallback = resolve_hermes_home(
            {"LOCALAPPDATA": "C:/Users/test/AppData/Local"}, platform_name="nt"
        )

        self.assertEqual(explicit, Path("D:/Hermes/Profile"))
        self.assertEqual(fallback, Path("C:/Users/test/AppData/Local/hermes"))

    def test_discover_only_returns_valid_skill_directories(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self.make_repo(Path(tmp))
            (repo / "skills" / "not-a-skill").mkdir()

            found = discover_skill_dirs(repo)

            self.assertEqual([path.name for path in found], ["alpha", "beta"])

    def test_copy_skills_is_idempotent_and_never_copies_repo_secrets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = self.make_repo(root)
            hermes_home = root / "hermes"
            old = hermes_home / "skills" / "alpha"
            old.mkdir(parents=True)
            (old / "stale.txt").write_text("remove me", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "existing unowned skill"):
                copy_skills(repo, hermes_home)

            first = copy_skills(repo, hermes_home, force=True)
            second = copy_skills(repo, hermes_home)

            self.assertEqual(first["installed"], ["alpha", "beta"])
            self.assertEqual(second["installed"], ["alpha", "beta"])
            self.assertFalse((hermes_home / "skills" / "alpha" / "stale.txt").exists())
            self.assertFalse((hermes_home / "skills" / ".env").exists())
            self.assertFalse((hermes_home / "skills" / ".git").exists())

            (old / "SKILL.md").write_text("user customization", encoding="utf-8")
            (repo / "skills" / "alpha" / "SKILL.md").write_text(
                MINIMAL_SKILL.format(name="alpha") + "\nupdated\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "user-modified skill"):
                copy_skills(repo, hermes_home)

    def test_copy_skills_dry_run_does_not_mutate_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = self.make_repo(root)
            hermes_home = root / "hermes"

            receipt = copy_skills(repo, hermes_home, dry_run=True)

            self.assertTrue(receipt["dry_run"])
            self.assertFalse((hermes_home / "skills").exists())

    def test_replace_tree_restores_existing_skill_when_activation_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            destination = root / "skills" / "alpha"
            source.mkdir()
            destination.mkdir(parents=True)
            (source / "SKILL.md").write_text("new", encoding="utf-8")
            (destination / "SKILL.md").write_text("old", encoding="utf-8")

            original_replace = Path.replace

            def fail_staging_activation(path, target):
                if ".install-" in path.name:
                    raise OSError("simulated activation failure")
                return original_replace(path, target)

            with patch.object(Path, "replace", new=fail_staging_activation):
                with self.assertRaisesRegex(OSError, "simulated activation failure"):
                    _replace_tree(source, destination)

            self.assertEqual(
                (destination / "SKILL.md").read_text(encoding="utf-8"),
                "old",
            )

    def test_profile_install_command_uses_supported_local_distribution_path(self):
        command = build_profile_install_command(Path("C:/work/music-os"), "music-producer")

        self.assertEqual(
            command,
            [
                "hermes",
                "profile",
                "install",
                "C:/work/music-os",
                "--name",
                "music-producer",
                "--alias",
                "-y",
            ],
        )

        forced = build_profile_install_command(
            Path("C:/work/music-os"), "music-producer", force=True
        )
        self.assertIn("--force", forced)

    def test_install_profile_surfaces_cli_error(self):
        failure = CalledProcessError(
            1,
            ["hermes", "profile", "install"],
            output="profile stdout",
            stderr="profile stderr",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            (repo / "distribution.yaml").write_text(
                "name: music-producer\ndistribution_owned:\n  - distribution.yaml\n",
                encoding="utf-8",
            )
            with patch("scripts.install_machine.subprocess.run", side_effect=failure):
                with self.assertRaisesRegex(RuntimeError, "profile stderr"):
                    install_profile(
                        repo,
                        "music-producer",
                        hermes_home=root / "hermes",
                        dry_run=False,
                    )

    def test_install_profile_uses_persistent_safe_source_and_scoped_home(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            (repo / "distribution.yaml").write_text(
                "name: music-producer\n"
                "distribution_owned:\n"
                "  - distribution.yaml\n"
                "  - SOUL.md\n",
                encoding="utf-8",
            )
            (repo / "SOUL.md").write_text("safe payload\n", encoding="utf-8")
            (repo / ".git").mkdir()
            hermes_home = root / "isolated-hermes"
            captured = {}

            def fake_run(command, **kwargs):
                source = Path(command[3])
                captured["source"] = source
                captured["env"] = kwargs["env"]
                self.assertTrue((source / "SOUL.md").is_file())
                self.assertFalse((source / ".git").exists())
                return CompletedProcess(command, 0, stdout="installed", stderr="")

            with patch("scripts.install_machine.subprocess.run", side_effect=fake_run):
                receipt = install_profile(
                    repo,
                    "music-producer",
                    hermes_home=hermes_home,
                    dry_run=False,
                )

            self.assertEqual(receipt["status"], "installed")
            self.assertTrue(captured["source"].is_dir())
            self.assertEqual(captured["env"]["HERMES_HOME"], str(hermes_home.resolve()))
            self.assertTrue(str(captured["source"]).startswith(str(hermes_home.resolve())))

    def test_existing_profile_requires_explicit_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            (repo / "distribution.yaml").write_text(
                "name: music-producer\ndistribution_owned:\n  - distribution.yaml\n",
                encoding="utf-8",
            )
            hermes_home = root / "hermes"
            (hermes_home / "profiles" / "music-producer").mkdir(parents=True)

            with self.assertRaisesRegex(RuntimeError, "already exists"):
                install_profile(repo, "music-producer", hermes_home=hermes_home)

    def test_cli_preflights_existing_profile_before_any_skill_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            home = root / "home"
            (repo / "skills" / "example").mkdir(parents=True)
            (repo / "skills" / "example" / "SKILL.md").write_text(
                MINIMAL_SKILL.format(name="example"), encoding="utf-8"
            )
            (repo / "distribution.yaml").write_text(
                "name: example\nversion: 1.0.0\n"
                "distribution_owned:\n  - distribution.yaml\n  - skills\n",
                encoding="utf-8",
            )
            (home / "profiles" / "music-producer").mkdir(parents=True)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).parents[1] / "scripts" / "install_machine.py"),
                    "--repo-root",
                    str(repo),
                    "--hermes-home",
                    str(home),
                    "--install-profile",
                ],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("--force-profile", completed.stderr)
            self.assertFalse((home / "skills" / "example").exists())
            self.assertFalse((home / "local" / "profile-sources").exists())

    def test_stage_profile_payload_excludes_vcs_and_unowned_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "distribution.yaml").write_text(
                "name: music-producer\n"
                "distribution_owned:\n"
                "  - distribution.yaml\n"
                "  - config.yaml\n"
                "  - skills\n",
                encoding="utf-8",
            )
            (repo / "config.yaml").write_text("model: test\n", encoding="utf-8")
            skill_dir = repo / "skills" / "test-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                MINIMAL_SKILL.format(name="test-skill"), encoding="utf-8"
            )
            (repo / ".git").mkdir()
            (repo / ".git" / "config").write_text("private metadata", encoding="utf-8")
            (repo / "notes.tmp").write_text("not owned", encoding="utf-8")
            cache_dir = skill_dir / "__pycache__"
            cache_dir.mkdir()
            (cache_dir / "compiled.pyc").write_bytes(b"cache")

            with stage_profile_payload(repo) as staged:
                self.assertTrue((staged / "distribution.yaml").is_file())
                self.assertTrue((staged / "config.yaml").is_file())
                self.assertTrue((staged / "skills" / "test-skill" / "SKILL.md").is_file())
                self.assertFalse((staged / ".git").exists())
                self.assertFalse((staged / "notes.tmp").exists())
                self.assertFalse(
                    (staged / "skills" / "test-skill" / "__pycache__").exists()
                )

    def test_stage_profile_payload_rejects_nested_secret_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "distribution.yaml").write_text(
                "name: music-producer\n"
                "distribution_owned:\n"
                "  - distribution.yaml\n"
                "  - skills\n",
                encoding="utf-8",
            )
            skill = repo / "skills" / "example"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                MINIMAL_SKILL.format(name="example"), encoding="utf-8"
            )
            (skill / ".ENV").write_text("DO_NOT_COPY=1\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "forbidden user state"):
                with stage_profile_payload(repo):
                    pass

    @unittest.skipUnless(os.name == "nt", "Windows junction test")
    def test_junctions_are_rejected_from_staging_and_skill_mirroring(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            skill = repo / "skills" / "example"
            skill.mkdir(parents=True)
            (repo / "distribution.yaml").write_text(
                "name: music-producer\n"
                "distribution_owned:\n"
                "  - distribution.yaml\n"
                "  - skills\n",
                encoding="utf-8",
            )
            (skill / "SKILL.md").write_text(
                MINIMAL_SKILL.format(name="example"), encoding="utf-8"
            )
            outside = root / "outside"
            outside.mkdir()
            (outside / "private.txt").write_text("outside payload\n", encoding="utf-8")
            junction = skill / "outside-link"
            created = subprocess.run(
                ["cmd.exe", "/c", "mklink", "/J", str(junction), str(outside)],
                capture_output=True,
                text=True,
            )
            if created.returncode != 0:
                self.skipTest(f"could not create junction: {created.stderr or created.stdout}")

            with self.assertRaisesRegex(ValueError, "reparse point"):
                with stage_profile_payload(repo):
                    pass
            with self.assertRaisesRegex(ValueError, "reparse point"):
                copy_skills(repo, root / "hermes", force=True)

    def test_profile_driver_env_is_created_but_never_overwrites_existing_env(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fresh = root / "fresh-profile"
            fresh.mkdir()
            driver = root / "cua-driver.exe"
            driver.write_bytes(b"driver")

            created = ensure_profile_driver_env(fresh, driver)

            self.assertEqual(created["status"], "created")
            env_text = (fresh / ".env").read_text(encoding="utf-8")
            written = next(
                line.split("=", 1)[1]
                for line in env_text.splitlines()
                if line.startswith("HERMES_CUA_DRIVER_CMD=")
            )
            self.assertTrue(os.path.samefile(written, driver))

            existing = root / "existing-profile"
            existing.mkdir()
            (existing / ".env").write_text("SECRET=preserve-me\n", encoding="utf-8")

            skipped = ensure_profile_driver_env(existing, driver)

            self.assertEqual(skipped["status"], "skipped-existing-env")
            self.assertEqual(
                (existing / ".env").read_text(encoding="utf-8"),
                "SECRET=preserve-me\n",
            )


if __name__ == "__main__":
    unittest.main()
