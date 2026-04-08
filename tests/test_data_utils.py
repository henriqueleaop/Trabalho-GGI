from datetime import datetime
import unittest

import pandas as pd

from src.steam_dashboard.data_utils import normalize_appid_frame, normalize_appid_series
from src.steam_dashboard.insights import build_operational_snapshot


class DataUtilsTests(unittest.TestCase):
    def test_normalize_appid_series_is_idempotent(self):
        series = pd.Series([730, "570", None, "invalid"])
        normalized = normalize_appid_series(series)

        self.assertEqual(str(normalized.dtype), "string")
        self.assertEqual(normalized.iloc[0], "730")
        self.assertEqual(normalized.iloc[1], "570")
        self.assertTrue(pd.isna(normalized.iloc[2]))
        self.assertTrue(pd.isna(normalized.iloc[3]))

    def test_build_operational_snapshot_accepts_mixed_appid_types(self):
        games_df = pd.DataFrame(
            {
                "appid": [730, 570],
                "peak_ccu": [1000, 500],
                "market_tier": ["Blockbuster F2P", "Blockbuster F2P"],
                "segment": ["Other", "Other"],
            }
        )
        ccu_df = pd.DataFrame(
            {
                "captured_at": [datetime(2026, 4, 8, 18, 0), datetime(2026, 4, 8, 18, 0), datetime(2026, 4, 8, 19, 0), datetime(2026, 4, 8, 19, 0)],
                "appid": ["730", "570", 730, 570],
                "name": ["Counter-Strike 2", "Dota 2", "Counter-Strike 2", "Dota 2"],
                "current_players": [900, 450, 1100, 400],
            }
        )

        snapshot = build_operational_snapshot(games_df, ccu_df)

        self.assertEqual(len(snapshot), 2)
        self.assertEqual(snapshot.iloc[0]["appid"], "730")
        self.assertEqual(snapshot.iloc[0]["peak_status"], "Acima do pico historico da base")
        self.assertEqual(snapshot.iloc[1]["delta_label"], "Caindo")


if __name__ == "__main__":
    unittest.main()
