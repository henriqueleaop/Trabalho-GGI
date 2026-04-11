import unittest

import pandas as pd

from src.steam_dashboard.academic import (
    build_academic_insights,
    build_market_anchors,
    build_strategy_payload,
    load_academic_sources,
)


class AcademicTests(unittest.TestCase):
    def test_load_academic_sources(self):
        sources = load_academic_sources()

        self.assertEqual(len(sources.sales), 31)
        self.assertEqual(len(sources.customer_profile), 35)
        self.assertEqual(len(sources.store_access), 21)
        self.assertIn("units_sold", sources.sales.columns)
        self.assertIn("customer_share_pct", sources.customer_profile.columns)
        self.assertIn("visits", sources.store_access.columns)

    def test_build_academic_insights(self):
        sources = load_academic_sources()
        insights = build_academic_insights(sources.sales, sources.customer_profile, sources.store_access)

        self.assertEqual(len(insights), 10)
        self.assertEqual(insights[0]["value"], "Sexta (93.0 jogos)")
        self.assertEqual(insights[4]["value"], "Action (44.0%)")
        self.assertEqual(insights[7]["value"], "Sabado / Noite")
        self.assertEqual(insights[8]["value"], "Domingo / Manha")
        self.assertEqual(insights[9]["value"], "Sexta + Action + Noite")

    def test_build_market_anchors_and_strategy(self):
        games_df = pd.DataFrame(
            {
                "segment": ["AAA", "Indie", "Other", "Other"],
                "price": [39.99, 4.99, 0.0, 0.0],
                "peak_ccu": [120000, 9000, 180000, 160000],
                "is_free": [False, False, True, True],
                "linux": [True, False, True, False],
                "positive_ratio": [0.9, 0.95, 0.8, 0.78],
                "opportunity_score": [78.0, 88.5, 81.0, 72.0],
                "owners_mid": [2_000_000, 200_000, 5_000_000, 3_000_000],
                "name": ["AAA Game", "Indie Game", "F2P One", "F2P Two"],
                "market_tier": ["AAA Premium", "Indie", "Blockbuster F2P", "Blockbuster F2P"],
                "primary_genre": ["Action", "Indie", "Action", "Action"],
            }
        )
        sources = load_academic_sources()
        insights = build_academic_insights(sources.sales, sources.customer_profile, sources.store_access)
        anchors = build_market_anchors(games_df)
        strategy = build_strategy_payload(insights, anchors, sources.sales, sources.customer_profile, sources.store_access)

        self.assertAlmostEqual(anchors["price_diff"], 35.0)
        self.assertIn("Indicador composto", anchors["indicator_formula"])
        self.assertEqual(len(strategy["three_months"]), 3)
        self.assertEqual(len(strategy["six_months"]), 3)
        self.assertEqual(len(strategy["one_year"]), 3)
        self.assertEqual(len(strategy["actions"]), 3)
        self.assertIn("SteamLoja", strategy["summary"])


if __name__ == "__main__":
    unittest.main()
