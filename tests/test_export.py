import json
import sqlite3
import sys
from pathlib import Path

import pytest

from ff_synctool import export

SCHEMA = """
CREATE TABLE tabs (
    guid TEXT NOT NULL PRIMARY KEY,
    record TEXT NOT NULL,
    last_modified INTEGER NOT NULL
);
"""

SAMPLE_RECORD = {
    "id": "DFKDGhG1_yV-",
    "clientName": "mike's Firefox Developer Edition on Mike-MBP",
    "tabs": [
        {
            "title": "The lethal trifecta for AI agents",
            "urlHistory": ["https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/"],
            "icon": "https://simonwillison.net/favicon.ico",
            "lastUsed": 1750500277,
        }
    ],
}


def _make_db(path: Path, rows: list[tuple[str, str, int]]) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executescript(SCHEMA)
        conn.executemany(
            "INSERT INTO tabs (guid, record, last_modified) VALUES (?, ?, ?)",
            rows,
        )
        conn.commit()
    finally:
        conn.close()


@pytest.fixture
def db_with_one_device(tmp_path: Path) -> Path:
    db = tmp_path / "synced-tabs.sqlite3"
    _make_db(db, [("DFKDGhG1_yV-", json.dumps(SAMPLE_RECORD), 1750500277)])
    return db


@pytest.fixture
def db_with_multiple_devices(tmp_path: Path) -> Path:
    db = tmp_path / "synced-tabs.sqlite3"
    second = {
        "id": "GPWwTxsncVn7",
        "clientName": "phone",
        "tabs": [
            {
                "title": "example",
                "urlHistory": ["https://example.com/"],
                "icon": "",
                "lastUsed": 1750000000,
            }
        ],
    }
    _make_db(
        db,
        [
            ("DFKDGhG1_yV-", json.dumps(SAMPLE_RECORD), 1750500277),
            ("GPWwTxsncVn7", json.dumps(second), 1750000000),
        ],
    )
    return db


class TestLoadSyncedTabs:
    def test_yields_one_dict_per_row(self, db_with_multiple_devices: Path) -> None:
        result = list(export.load_synced_tabs(db_with_multiple_devices))
        assert len(result) == 2

    def test_yields_expected_keys(self, db_with_one_device: Path) -> None:
        (tab,) = list(export.load_synced_tabs(db_with_one_device))
        assert set(tab.keys()) == {"guid", "record", "last_modified"}

    def test_record_is_returned_as_raw_string(self, db_with_one_device: Path) -> None:
        (tab,) = list(export.load_synced_tabs(db_with_one_device))
        assert isinstance(tab["record"], str)
        assert json.loads(tab["record"]) == SAMPLE_RECORD

    def test_empty_table_yields_nothing(self, tmp_path: Path) -> None:
        db = tmp_path / "empty.sqlite3"
        _make_db(db, [])
        assert list(export.load_synced_tabs(db)) == []


class TestMain:
    def test_writes_one_file_per_device(
        self,
        db_with_multiple_devices: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        monkeypatch.chdir(out_dir)
        monkeypatch.setattr(sys, "argv", ["export.py", str(db_with_multiple_devices)])

        export.main()

        written = sorted(p.name for p in out_dir.glob("tab_*.json"))
        assert written == ["tab_DFKDGhG1_yV-.json", "tab_GPWwTxsncVn7.json"]

    def test_written_file_contains_decoded_record(
        self,
        db_with_one_device: Path,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        monkeypatch.chdir(out_dir)
        monkeypatch.setattr(sys, "argv", ["export.py", str(db_with_one_device)])

        export.main()

        written = out_dir / "tab_DFKDGhG1_yV-.json"
        assert json.loads(written.read_text(encoding="utf-8")) == SAMPLE_RECORD
