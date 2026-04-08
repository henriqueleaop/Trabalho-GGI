import unittest

from src.steam_dashboard.transform import (
    classify_market_tier,
    classify_segment,
    parse_owner_range,
    parse_release_date,
    price_bucket_for,
    should_exclude_title,
)


class TransformTests(unittest.TestCase):
    def test_parse_owner_range_with_interval(self):
        owners_min, owners_max, owners_mid = parse_owner_range("20,000 - 50,000")
        self.assertEqual(owners_min, 20000)
        self.assertEqual(owners_max, 50000)
        self.assertEqual(owners_mid, 35000)

    def test_parse_owner_range_with_missing_value(self):
        self.assertEqual(parse_owner_range(""), (None, None, None))

    def test_parse_release_date(self):
        parsed = parse_release_date("Aug 1, 2023")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.isoformat(), "2023-08-01")

    def test_should_exclude_title(self):
        self.assertTrue(should_exclude_title("My Great Demo"))
        self.assertFalse(should_exclude_title("My Great Game"))

    def test_price_bucket(self):
        self.assertEqual(price_bucket_for(0), "Free")
        self.assertEqual(price_bucket_for(14.99), "$10 to $19.99")
        self.assertEqual(price_bucket_for(59.99), "$50+")

    def test_classify_segment(self):
        self.assertEqual(classify_segment("Action, Indie", 14.99, 200_000), "Indie")
        self.assertEqual(classify_segment("Action", 59.99, 2_000_000), "AAA")
        self.assertEqual(classify_segment("Action", 19.99, 50_000), "Other")

    def test_classify_market_tier(self):
        self.assertEqual(classify_market_tier("Indie", 14.99, 200_000), "Indie")
        self.assertEqual(classify_market_tier("AAA", 59.99, 2_000_000), "AAA Premium")
        self.assertEqual(classify_market_tier("Other", 0.0, 5_000_000), "Blockbuster F2P")
        self.assertEqual(classify_market_tier("Other", 9.99, 50_000), "Catalogo Geral")


if __name__ == "__main__":
    unittest.main()
