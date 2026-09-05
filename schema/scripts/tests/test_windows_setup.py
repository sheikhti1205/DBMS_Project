from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class WindowsSetupTest(unittest.TestCase):
    def test_default_environment_avoids_store_virtualized_local_app_data(self) -> None:
        launcher = (ROOT / "setup_windows.bat").read_text(encoding="utf-8")
        self.assertIn(
            'if not defined BYTEFORGE_ENV set "BYTEFORGE_ENV=%USERPROFILE%\\.byteforge\\dbms_project\\venv"',
            launcher,
        )
        self.assertNotIn(
            'set "BYTEFORGE_ENV=%LOCALAPPDATA%\\ByteForge\\DBMS_Project\\venv"',
            launcher,
        )

    def test_development_doc_uses_the_same_windows_environment(self) -> None:
        development = (ROOT / "docs" / "DEVELOPMENT.md").read_text(encoding="utf-8")
        self.assertIn("$env:USERPROFILE\\.byteforge\\dbms_project\\venv", development)
        self.assertNotIn("$env:LOCALAPPDATA\\ByteForge", development)


if __name__ == "__main__":
    unittest.main()
