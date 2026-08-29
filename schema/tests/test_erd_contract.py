from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from schema.scripts.common import schema_model


class ErdContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(
            (ROOT / "schema" / "erd_contract.json").read_text(encoding="utf-8")
        )

    def test_contract_has_expected_shape(self) -> None:
        self.assertEqual(21, len(self.contract["tables"]))
        self.assertEqual(28, len(self.contract["foreign_keys"]))
        self.assertNotIn("Ground_" + "Water_Well", self.contract["tables"])
        self.assertNotIn("Industrial" + "_Type", self.contract["tables"])

    def test_generator_matches_independent_contract(self) -> None:
        expected_tables = {
            table: tuple((name, kind) for name, kind, _ in columns)
            for table, columns in self.contract["tables"].items()
        }
        expected_keys = {
            table: tuple(columns)
            for table, columns in self.contract["primary_keys"].items()
        }
        expected_foreign_keys = {
            (child, tuple(child_columns), parent, tuple(parent_columns))
            for child, child_columns, parent, parent_columns in self.contract["foreign_keys"]
        }
        self.assertEqual(expected_tables, schema_model.TABLES)
        self.assertEqual(expected_keys, schema_model.PRIMARY_KEYS)
        self.assertEqual(expected_foreign_keys, set(schema_model.FOREIGN_KEYS))

    def test_bcnf_headers_match_contract(self) -> None:
        csv_dir = ROOT / "normalization" / "csv" / "BCNF"
        expected_names = set(self.contract["tables"])
        actual_names = {path.stem for path in csv_dir.glob("*.csv") if not path.name.startswith("_")}
        self.assertEqual(expected_names, actual_names)
        for table, columns in self.contract["tables"].items():
            header = (csv_dir / f"{table}.csv").read_text(
                encoding="utf-8-sig"
            ).splitlines()[0].split(",")
            self.assertEqual([column[0] for column in columns], header, table)

    def test_no_retired_domain_in_active_code_or_data(self) -> None:
        needles = ("ground" + "water", "ground_" + "water", "bwdb_" + "gw")
        suffixes = {".py", ".sql", ".json", ".md", ".csv", ".txt"}
        hits: list[str] = []
        for base in (ROOT / "normalization", ROOT / "schema"):
            for path in base.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in suffixes:
                    continue
                if "discarded_do_not_use" in path.parts:
                    continue
                text = path.read_text(encoding="utf-8-sig", errors="ignore").lower()
                if any(needle in text for needle in needles):
                    hits.append(str(path.relative_to(ROOT)))
        self.assertEqual([], hits)


if __name__ == "__main__":
    unittest.main()
