"""Regression tests for the setup launcher entry points."""

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]

PROJECT_MODULE_CALL = re.compile(r"-m (schema\.[a-z][a-z0-9_.]*|normalization\.[a-z][a-z0-9_.]*)")


def tracked_files() -> set[str]:
    listing = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    return {line.strip() for line in listing.splitlines() if line.strip()}


def launcher_module_calls() -> set[str]:
    calls: set[str] = set()
    for name in ("setup_linux.sh", "setup_windows.bat"):
        launcher = (ROOT / name).read_text(encoding="utf-8")
        calls.update(PROJECT_MODULE_CALL.findall(launcher))
    return calls


class LauncherEntrypointTest(unittest.TestCase):
    def test_launchers_only_run_committed_modules(self) -> None:
        if not (ROOT / ".git").exists():
            self.skipTest("Git metadata unavailable in an exported source archive")
        tracked = tracked_files()
        modules = launcher_module_calls()
        self.assertTrue(modules, "no project module invocations found in the launchers")
        for module in sorted(modules):
            relative = ROOT.joinpath(*module.split(".")).with_suffix(".py")
            self.assertIn(
                relative.relative_to(ROOT).as_posix(),
                tracked,
                f"launcher runs untracked module {module!r}; "
                f"{relative.relative_to(ROOT).as_posix()} is not committed",
            )



if __name__ == "__main__":
    unittest.main()
