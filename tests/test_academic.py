import unittest

import pandas as pd

from src.steam_dashboard.academic import (
    build_academic_insights,
    build_market_anchors,
    build_methodology_note,
    build_strategy_payload,
    load_academic_sources,
)
from src.steam_dashboard.reporting import build_pdf_report, build_report_context


class AcademicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = load_academic_sources()

    def test_load_academic_sources(self):
        sources = self.sources

        self.assertGreater(len(sources.raw_sales), 100_000)
        self.assertGreater(len(sources.raw_customer_profile), 100_000)
        self.assertGreater(len(sources.raw_store_access), 100_000)

        self.assertEqual(len(sources.sales), 31)
        self.assertGreaterEqual(len(sources.customer_profile), 35)
        self.assertEqual(len(sources.store_access), 21)

        self.assertIn("units_sold", sources.sales.columns)
        self.assertIn("customer_share_pct", sources.customer_profile.columns)
        self.assertIn("visits", sources.store_access.columns)

        self.assertIn("order_id", sources.raw_sales.columns)
        self.assertIn("preferred_genre", sources.raw_customer_profile.columns)
        self.assertIn("session_id", sources.raw_store_access.columns)

    def test_business_coherence_of_academic_sources(self):
        sources = self.sources
        weekday_sales = (
            sources.sales.groupby("weekday", observed=False)["units_sold"]
            .mean()
            .to_dict()
        )
        shift_visits = (
            sources.store_access.groupby("shift", observed=False)["visits"]
            .mean()
            .to_dict()
        )
        genre_share = (
            sources.customer_profile.groupby("genre", observed=False)["customer_share_pct"]
            .mean()
            .sort_values(ascending=False)
        )

        self.assertGreater(weekday_sales["Sexta"], weekday_sales["Segunda"])
        self.assertGreater(weekday_sales["Sabado"], weekday_sales["Terca"])
        self.assertGreater(shift_visits["Noite"], shift_visits["Manha"])
        self.assertEqual(str(genre_share.index[0]), "Action")
        self.assertNotAlmostEqual(
            float(
                sources.customer_profile.loc[sources.customer_profile["weekday"] == "Segunda", "customer_share_pct"].max()
            ),
            float(
                sources.customer_profile.loc[sources.customer_profile["weekday"] == "Sabado", "customer_share_pct"].max()
            ),
        )

        reconstructed_revenue = (
            sources.raw_sales["units"]
            * sources.raw_sales["unit_price_brl"]
            * (1 - sources.raw_sales["discount_pct"] / 100)
        ).round(2)
        revenue_diff = (reconstructed_revenue - sources.raw_sales["gross_revenue_brl"].round(2)).abs().max()
        self.assertLessEqual(float(revenue_diff), 0.011)

    def test_build_academic_insights(self):
        sources = self.sources
        insights = build_academic_insights(sources.sales, sources.customer_profile, sources.store_access)

        self.assertEqual(len(insights), 10)
        self.assertTrue(insights[0]["value"].startswith("Sabado (") or insights[0]["value"].startswith("Sexta ("))
        self.assertIn("Action", insights[4]["value"])
        self.assertIn("Noite", insights[6]["value"])
        self.assertIn("/", insights[7]["value"])
        self.assertIn("/", insights[8]["value"])
        self.assertIn(" + ", insights[9]["value"])

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
        sources = self.sources
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

    def test_methodology_note(self):
        note = build_methodology_note(self.sources)

        self.assertIn("grao detalhado", note)
        self.assertIn("pedidos", note)
        self.assertIn("sessoes", note)

    def test_build_pdf_report(self):
        try:
            import reportlab  # noqa: F401
        except ModuleNotFoundError:
            self.skipTest("reportlab nao instalado")

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

        pdf_bytes = build_pdf_report(build_report_context(games_df))

        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertGreater(len(pdf_bytes), 1000)


if __name__ == "__main__":
    unittest.main()
