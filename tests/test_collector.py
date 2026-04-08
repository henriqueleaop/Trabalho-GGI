from datetime import datetime
from pathlib import Path
import csv
import tempfile
import unittest

from src.steam_dashboard.collector import append_snapshot_rows, build_snapshot_rows


class CollectorTests(unittest.TestCase):
    def test_build_snapshot_rows(self):
        targets = [{"appid": "730", "name": "Counter-Strike 2"}]

        def fake_fetcher(appid: str) -> int:
            self.assertEqual(appid, "730")
            return 12345

        rows = build_snapshot_rows(targets, fake_fetcher, captured_at=datetime(2026, 4, 8, 15, 0, 0))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["current_players"], 12345)
        self.assertEqual(rows[0]["weekday"], "Quarta")
        self.assertEqual(rows[0]["hour"], 15)

    def test_append_snapshot_rows_preserves_history(self):
        rows_a = [
            {
                "captured_at": "2026-04-08T15:00:00",
                "captured_date": "2026-04-08",
                "weekday": "Quarta",
                "hour": 15,
                "appid": "730",
                "name": "Counter-Strike 2",
                "current_players": 100,
            }
        ]
        rows_b = [
            {
                "captured_at": "2026-04-08T16:00:00",
                "captured_date": "2026-04-08",
                "weekday": "Quarta",
                "hour": 16,
                "appid": "730",
                "name": "Counter-Strike 2",
                "current_players": 120,
            }
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            history_path = Path(temp_dir) / "ccu_snapshots.csv"
            append_snapshot_rows(history_path, rows_a)
            append_snapshot_rows(history_path, rows_b)

            with history_path.open("r", encoding="utf-8", newline="") as handle:
                loaded = list(csv.DictReader(handle))

        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]["current_players"], "100")
        self.assertEqual(loaded[1]["current_players"], "120")


if __name__ == "__main__":
    unittest.main()
