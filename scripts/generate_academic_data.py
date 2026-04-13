from __future__ import annotations

import argparse
import csv
import random
from bisect import bisect
from datetime import date, datetime, time, timedelta
from pathlib import Path


WEEKDAY_ORDER = ["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo"]
WEEKDAY_MAP = {
    0: "Segunda",
    1: "Terca",
    2: "Quarta",
    3: "Quinta",
    4: "Sexta",
    5: "Sabado",
    6: "Domingo",
}
SHIFT_WINDOWS = {
    "Manha": (8, 11),
    "Tarde": (12, 17),
    "Noite": (18, 23),
}
COUNTRIES = [
    ("Brasil", "America do Sul", 0.31),
    ("Estados Unidos", "America do Norte", 0.22),
    ("Alemanha", "Europa", 0.09),
    ("Reino Unido", "Europa", 0.08),
    ("Argentina", "America do Sul", 0.11),
    ("Mexico", "America do Norte", 0.08),
    ("Turquia", "Europa/Asia", 0.06),
    ("Canada", "America do Norte", 0.05),
]


class WeightedSampler:
    def __init__(self, entries: list[tuple[str, float]]) -> None:
        self.values = [value for value, _ in entries]
        total = 0.0
        self.thresholds: list[float] = []
        for _, weight in entries:
            total += weight
            self.thresholds.append(total)
        self.total = total

    def pick(self, rng: random.Random) -> str:
        return self.values[bisect(self.thresholds, rng.random() * self.total)]


COUNTRY_SAMPLER = WeightedSampler([(country, weight) for country, _, weight in COUNTRIES])
REGION_BY_COUNTRY = {country: region for country, region, _ in COUNTRIES}


def weekday_name(day: date) -> str:
    return WEEKDAY_MAP[day.weekday()]


def weighted_sampler(entries: list[tuple[str, float]]) -> WeightedSampler:
    return WeightedSampler(entries)


def build_order_timestamp(rng: random.Random, base_date: date, shift: str) -> datetime:
    hour_start, hour_end = SHIFT_WINDOWS[shift]
    hour = rng.randint(hour_start, hour_end)
    minute = rng.randint(0, 59)
    second = rng.randint(0, 59)
    return datetime.combine(base_date, time(hour=hour, minute=minute, second=second))


def daily_sales_volume(day: date, rng: random.Random) -> int:
    baseline = {
        "Segunda": 5200,
        "Terca": 4600,
        "Quarta": 5600,
        "Quinta": 5100,
        "Sexta": 8800,
        "Sabado": 10300,
        "Domingo": 3900,
    }[weekday_name(day)]
    multiplier = 1.0
    if day.day in {5, 6, 7, 8}:
        multiplier *= 1.07
    if day.day in {19, 20, 21, 22}:
        multiplier *= 1.12
    if day.day in {27, 28}:
        multiplier *= 1.05
    if day.day in {14, 15}:
        multiplier *= 0.97
    volatility = max(0.92, min(1.08, rng.gauss(1.0, 0.035)))
    return int(round(baseline * multiplier * volatility))


def customer_profile_volume(day: date, rng: random.Random) -> int:
    baseline = {
        "Segunda": 15000,
        "Terca": 13800,
        "Quarta": 16000,
        "Quinta": 14800,
        "Sexta": 18400,
        "Sabado": 19600,
        "Domingo": 13200,
    }[weekday_name(day)]
    volatility = max(0.93, min(1.07, rng.gauss(1.0, 0.03)))
    return int(round(baseline * volatility))


def access_volume(weekday: str, shift: str, rng: random.Random) -> int:
    baseline = {
        ("Segunda", "Manha"): 3600,
        ("Segunda", "Tarde"): 5200,
        ("Segunda", "Noite"): 7600,
        ("Terca", "Manha"): 3200,
        ("Terca", "Tarde"): 5000,
        ("Terca", "Noite"): 7200,
        ("Quarta", "Manha"): 3900,
        ("Quarta", "Tarde"): 5600,
        ("Quarta", "Noite"): 8100,
        ("Quinta", "Manha"): 3500,
        ("Quinta", "Tarde"): 5400,
        ("Quinta", "Noite"): 7900,
        ("Sexta", "Manha"): 5000,
        ("Sexta", "Tarde"): 7700,
        ("Sexta", "Noite"): 12100,
        ("Sabado", "Manha"): 5400,
        ("Sabado", "Tarde"): 8600,
        ("Sabado", "Noite"): 13600,
        ("Domingo", "Manha"): 2800,
        ("Domingo", "Tarde"): 4600,
        ("Domingo", "Noite"): 6400,
    }[(weekday, shift)]
    volatility = max(0.92, min(1.08, rng.gauss(1.0, 0.025)))
    return int(round(baseline * volatility))


def sales_campaign_sampler(weekday: str) -> WeightedSampler:
    if weekday == "Terca":
        return weighted_sampler(
            [
                ("Midweek Deal", 0.38),
                ("Organico", 0.24),
                ("Bundle", 0.16),
                ("Publisher Sale", 0.12),
                ("Creator Campaign", 0.10),
            ]
        )
    if weekday in {"Sexta", "Sabado"}:
        return weighted_sampler(
            [
                ("Weekend Spotlight", 0.42),
                ("Organico", 0.18),
                ("Bundle", 0.14),
                ("Publisher Sale", 0.14),
                ("Creator Campaign", 0.12),
            ]
        )
    if weekday == "Quinta":
        return weighted_sampler(
            [
                ("Organico", 0.24),
                ("Bundle", 0.27),
                ("Publisher Sale", 0.22),
                ("Creator Campaign", 0.14),
                ("Midweek Deal", 0.13),
            ]
        )
    if weekday == "Domingo":
        return weighted_sampler(
            [
                ("Organico", 0.32),
                ("Creator Campaign", 0.26),
                ("Bundle", 0.16),
                ("Weekend Spotlight", 0.16),
                ("Publisher Sale", 0.10),
            ]
        )
    return weighted_sampler(
        [
            ("Organico", 0.36),
            ("Bundle", 0.18),
            ("Publisher Sale", 0.16),
            ("Creator Campaign", 0.14),
            ("Weekend Spotlight", 0.08),
            ("Midweek Deal", 0.08),
        ]
    )


def genre_sampler(weekday: str) -> WeightedSampler:
    weekend_boost = 0.03 if weekday in {"Sexta", "Sabado"} else 0.0
    return weighted_sampler(
        [
            ("Action", 0.28 + weekend_boost),
            ("RPG", 0.18),
            ("Indie", 0.15),
            ("Strategy", 0.11),
            ("Simulation", 0.10),
            ("Sports", 0.08),
            ("Co-op", 0.10 - weekend_boost / 2),
        ]
    )


def customer_genre_sampler(weekday: str, channel: str) -> WeightedSampler:
    weights = {
        "Action": 0.27,
        "RPG": 0.20,
        "Indie": 0.16,
        "Strategy": 0.11,
        "Simulation": 0.10,
        "Sports": 0.07,
        "Co-op": 0.09,
    }
    if weekday in {"Sexta", "Sabado"}:
        weights["Action"] += 0.03
        weights["Co-op"] += 0.02
        weights["Indie"] -= 0.01
    if channel in {"Community", "Creator"}:
        weights["Indie"] += 0.03
        weights["Co-op"] += 0.01
        weights["Action"] -= 0.02
    if channel in {"CRM", "Direct"}:
        weights["RPG"] += 0.02
        weights["Strategy"] += 0.01
    return weighted_sampler(list(weights.items()))


def sales_shift_sampler(weekday: str) -> WeightedSampler:
    if weekday in {"Sexta", "Sabado"}:
        return weighted_sampler([("Manha", 0.14), ("Tarde", 0.31), ("Noite", 0.55)])
    if weekday == "Domingo":
        return weighted_sampler([("Manha", 0.18), ("Tarde", 0.34), ("Noite", 0.48)])
    return weighted_sampler([("Manha", 0.17), ("Tarde", 0.33), ("Noite", 0.50)])


def access_shift_probability(weekday: str, shift: str) -> tuple[float, float]:
    wishlist_base = {
        "Manha": 0.07,
        "Tarde": 0.10,
        "Noite": 0.13,
    }[shift]
    cart_base = {
        "Manha": 0.025,
        "Tarde": 0.040,
        "Noite": 0.060,
    }[shift]
    if weekday in {"Sexta", "Sabado"}:
        wishlist_base += 0.02
        cart_base += 0.015
    return wishlist_base, cart_base


def price_profile(market_segment: str, product_type: str, genre: str, rng: random.Random) -> float:
    base = {
        ("AAA", "Game Key"): (159, 269),
        ("AAA", "Deluxe Edition"): (239, 369),
        ("AAA", "Bundle"): (189, 299),
        ("AA", "Game Key"): (79, 169),
        ("AA", "Bundle"): (119, 219),
        ("Indie", "Game Key"): (22, 74),
        ("Indie", "Bundle"): (49, 139),
        ("Live Service", "Starter Pack"): (24, 119),
        ("Live Service", "DLC"): (18, 68),
    }.get((market_segment, product_type), (39, 119))
    genre_multiplier = {
        "Action": 1.08,
        "RPG": 1.04,
        "Indie": 0.90,
        "Strategy": 0.98,
        "Simulation": 1.00,
        "Sports": 1.02,
        "Co-op": 0.96,
    }[genre]
    return round(rng.uniform(*base) * genre_multiplier, 2)


def discount_for_campaign(campaign_type: str, rng: random.Random) -> float:
    bounds = {
        "Organico": (0, 8),
        "Midweek Deal": (14, 28),
        "Bundle": (18, 34),
        "Weekend Spotlight": (20, 38),
        "Publisher Sale": (24, 46),
        "Creator Campaign": (10, 22),
    }[campaign_type]
    return round(rng.uniform(*bounds), 2)


def write_daily_sales(path: Path, seed: int) -> int:
    rng = random.Random(seed)
    start = date(2026, 3, 1)
    end = date(2026, 3, 31)
    order_counter = 0

    channels = weighted_sampler(
        [
            ("Direct", 0.28),
            ("Organic Search", 0.19),
            ("Community", 0.16),
            ("Creator", 0.14),
            ("CRM", 0.13),
            ("Paid Social", 0.10),
        ]
    )
    segment_sampler = weighted_sampler(
        [("AAA", 0.34), ("AA", 0.22), ("Indie", 0.24), ("Live Service", 0.20)]
    )

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "order_id",
                "order_ts",
                "date",
                "weekday",
                "country",
                "region",
                "channel",
                "campaign_type",
                "genre",
                "market_segment",
                "product_type",
                "units",
                "unit_price_brl",
                "discount_pct",
                "gross_revenue_brl",
                "is_bundle",
                "is_repeat_customer",
            ]
        )
        current = start
        while current <= end:
            weekday = weekday_name(current)
            campaign_sampler = sales_campaign_sampler(weekday)
            day_genre_sampler = genre_sampler(weekday)
            shift_sampler = sales_shift_sampler(weekday)
            volume = daily_sales_volume(current, rng)

            for _ in range(volume):
                order_counter += 1
                country = COUNTRY_SAMPLER.pick(rng)
                region = REGION_BY_COUNTRY[country]
                channel = channels.pick(rng)
                campaign = campaign_sampler.pick(rng)
                genre = day_genre_sampler.pick(rng)
                market_segment = segment_sampler.pick(rng)

                if market_segment == "AAA":
                    product_sampler = weighted_sampler(
                        [("Game Key", 0.56), ("Deluxe Edition", 0.20), ("Bundle", 0.24)]
                    )
                elif market_segment == "AA":
                    product_sampler = weighted_sampler([("Game Key", 0.68), ("Bundle", 0.32)])
                elif market_segment == "Indie":
                    product_sampler = weighted_sampler([("Game Key", 0.72), ("Bundle", 0.28)])
                else:
                    product_sampler = weighted_sampler([("Starter Pack", 0.55), ("DLC", 0.45)])

                product_type = product_sampler.pick(rng)
                units = 1
                if product_type == "Bundle" and rng.random() < 0.18:
                    units = 2
                if product_type == "DLC" and rng.random() < 0.08:
                    units = 2

                list_price = price_profile(market_segment, product_type, genre, rng)
                discount_pct = discount_for_campaign(campaign, rng)
                gross_revenue = round(units * list_price * (1 - discount_pct / 100), 2)
                is_bundle = product_type == "Bundle"
                repeat_rate = 0.57 if channel in {"Direct", "CRM", "Community"} else 0.39
                if country in {"Brasil", "Estados Unidos"}:
                    repeat_rate += 0.03
                order_ts = build_order_timestamp(rng, current, shift_sampler.pick(rng))

                writer.writerow(
                    [
                        f"ORD-{order_counter:07d}",
                        order_ts.isoformat(sep=" "),
                        current.isoformat(),
                        weekday,
                        country,
                        region,
                        channel,
                        campaign,
                        genre,
                        market_segment,
                        product_type,
                        units,
                        f"{list_price:.2f}",
                        f"{discount_pct:.2f}",
                        f"{gross_revenue:.2f}",
                        str(is_bundle),
                        str(rng.random() < repeat_rate),
                    ]
                )

            current += timedelta(days=1)
    return order_counter


def write_customer_profile(path: Path, seed: int) -> int:
    rng = random.Random(seed)
    start = date(2026, 3, 2)
    countries = COUNTRY_SAMPLER
    platform_sampler = weighted_sampler(
        [
            ("Windows", 0.57),
            ("Steam Deck", 0.14),
            ("Linux", 0.10),
            ("Mac", 0.07),
            ("Web", 0.12),
        ]
    )
    acquisition_sampler = weighted_sampler(
        [
            ("Direct", 0.22),
            ("Organic Search", 0.20),
            ("Community", 0.18),
            ("Creator", 0.14),
            ("CRM", 0.14),
            ("Paid Social", 0.12),
        ]
    )
    customer_type_sampler = weighted_sampler(
        [
            ("Novo", 0.36),
            ("Recorrente", 0.34),
            ("Reativado", 0.19),
            ("VIP", 0.11),
        ]
    )

    profile_counter = 0
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "profile_id",
                "event_ts",
                "date",
                "weekday",
                "country",
                "platform",
                "acquisition_channel",
                "customer_type",
                "preferred_genre",
                "wishlist_add",
                "cart_add",
                "purchase_intent_score",
            ]
        )
        for offset in range(7):
            current = start + timedelta(days=offset)
            weekday = weekday_name(current)
            volume = customer_profile_volume(current, rng)

            for _ in range(volume):
                profile_counter += 1
                channel = acquisition_sampler.pick(rng)
                customer_type = customer_type_sampler.pick(rng)
                genre = customer_genre_sampler(weekday, channel).pick(rng)
                platform = platform_sampler.pick(rng)
                country = countries.pick(rng)

                base_score = {
                    "Novo": 52,
                    "Recorrente": 68,
                    "Reativado": 61,
                    "VIP": 79,
                }[customer_type]
                if genre in {"Action", "RPG"}:
                    base_score += 4
                if genre == "Indie":
                    base_score -= 2
                if channel in {"Direct", "CRM", "Community"}:
                    base_score += 4
                if platform == "Steam Deck":
                    base_score += 3
                score = max(15, min(98, round(rng.gauss(base_score, 12), 1)))
                wishlist_add = rng.random() < min(0.78, score / 100)
                cart_threshold = 0.16 + max(score - 50, 0) / 130
                cart_add = rng.random() < min(0.72, cart_threshold)
                event_ts = build_order_timestamp(
                    rng,
                    current,
                    weighted_sampler([("Manha", 0.23), ("Tarde", 0.33), ("Noite", 0.44)]).pick(rng),
                )

                writer.writerow(
                    [
                        f"CPF-{profile_counter:07d}",
                        event_ts.isoformat(sep=" "),
                        current.isoformat(),
                        weekday,
                        country,
                        platform,
                        channel,
                        customer_type,
                        genre,
                        str(wishlist_add),
                        str(cart_add),
                        f"{score:.1f}",
                    ]
                )
    return profile_counter


def write_store_access(path: Path, seed: int) -> int:
    rng = random.Random(seed)
    start = date(2026, 3, 2)
    device_sampler = weighted_sampler(
        [
            ("Desktop", 0.47),
            ("Mobile", 0.34),
            ("Steam Deck", 0.11),
            ("Tablet", 0.08),
        ]
    )
    traffic_sampler = weighted_sampler(
        [
            ("Direct", 0.24),
            ("Organic Search", 0.19),
            ("Community", 0.18),
            ("Sale Banner", 0.14),
            ("Creator", 0.13),
            ("CRM", 0.12),
        ]
    )
    landing_sampler = weighted_sampler(
        [
            ("Home", 0.34),
            ("Sale Landing", 0.22),
            ("Search", 0.16),
            ("Discovery Queue", 0.12),
            ("Publisher Page", 0.08),
            ("Bundle Page", 0.08),
        ]
    )

    session_counter = 0
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "session_id",
                "visit_ts",
                "date",
                "weekday",
                "shift",
                "country",
                "device_type",
                "traffic_source",
                "landing_surface",
                "session_minutes",
                "pages_viewed",
                "wishlist_action",
                "cart_action",
            ]
        )
        for offset in range(7):
            current = start + timedelta(days=offset)
            weekday = weekday_name(current)
            for shift in ("Manha", "Tarde", "Noite"):
                volume = access_volume(weekday, shift, rng)
                wishlist_rate, cart_rate = access_shift_probability(weekday, shift)
                for _ in range(volume):
                    session_counter += 1
                    country = COUNTRY_SAMPLER.pick(rng)
                    device = device_sampler.pick(rng)
                    traffic = traffic_sampler.pick(rng)
                    landing = landing_sampler.pick(rng)
                    visit_ts = build_order_timestamp(rng, current, shift)

                    base_minutes = {"Manha": 5.2, "Tarde": 6.4, "Noite": 7.8}[shift]
                    if device == "Desktop":
                        base_minutes += 1.1
                    if device == "Mobile":
                        base_minutes -= 0.9
                    if traffic in {"Community", "Creator"}:
                        base_minutes += 0.8
                    session_minutes = max(1.0, round(rng.gauss(base_minutes, 2.1), 1))

                    page_base = 4.2 + session_minutes / 2.2
                    if landing in {"Sale Landing", "Bundle Page"}:
                        page_base += 1.0
                    pages_viewed = max(1, int(round(rng.gauss(page_base, 1.7))))

                    wishlist_prob = wishlist_rate + (0.03 if traffic in {"Community", "Creator"} else 0.0)
                    cart_prob = cart_rate + (0.02 if device == "Desktop" else 0.0) - (0.01 if device == "Mobile" else 0.0)
                    writer.writerow(
                        [
                            f"SES-{session_counter:07d}",
                            visit_ts.isoformat(sep=" "),
                            current.isoformat(),
                            weekday,
                            shift,
                            country,
                            device,
                            traffic,
                            landing,
                            f"{session_minutes:.1f}",
                            pages_viewed,
                            str(rng.random() < wishlist_prob),
                            str(rng.random() < cart_prob),
                        ]
                    )
    return session_counter


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera bases academicas detalhadas da SteamLoja.")
    parser.add_argument("--seed", type=int, default=202603, help="Seed deterministica para reproducao.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/academic"),
        help="Diretorio de saida para os CSVs academicos.",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    sales_rows = write_daily_sales(args.output_dir / "daily_sales_month.csv", args.seed)
    customer_rows = write_customer_profile(args.output_dir / "customer_genre_profile_week.csv", args.seed + 101)
    access_rows = write_store_access(args.output_dir / "store_access_shift_week.csv", args.seed + 202)

    print(f"daily_sales_month.csv: {sales_rows:,} linhas")
    print(f"customer_genre_profile_week.csv: {customer_rows:,} linhas")
    print(f"store_access_shift_week.csv: {access_rows:,} linhas")


if __name__ == "__main__":
    main()
