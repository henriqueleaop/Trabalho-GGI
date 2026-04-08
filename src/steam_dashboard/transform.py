from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import csv
import math
import re
from typing import Iterable


RAW_FIELD_POSITIONS = {
    "appid": 0,
    "name": 1,
    "release_date_raw": 2,
    "estimated_owners_raw": 3,
    "peak_ccu": 4,
    "required_age": 5,
    "price": 6,
    "discount_dlc_count": 7,
    "windows": 17,
    "mac": 18,
    "linux": 19,
    "positive": 23,
    "negative": 24,
    "recommendations": 27,
    "average_playtime_forever": 29,
    "median_playtime_forever": 31,
    "developers": 33,
    "publishers": 34,
    "categories": 35,
    "genres": 36,
    "tags": 37,
}

EXCLUDED_TITLE_TERMS = ("demo", "playtest", "soundtrack")
PRICE_BUCKET_LABELS = [
    "Free",
    "Up to $9.99",
    "$10 to $19.99",
    "$20 to $29.99",
    "$30 to $49.99",
    "$50+",
]
OWNER_PATTERN = re.compile(r"(\d[\d,]*)")


def _require_pandas():
    try:
        import pandas as pd
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "pandas nao esta instalado. Instale as dependencias com `python -m pip install -r requirements.txt`."
        ) from exc
    return pd


def is_missing(value) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))


def parse_owner_range(value: str | int | float | None) -> tuple[int | None, int | None, int | None]:
    if is_missing(value):
        return (None, None, None)

    text = str(value).strip()
    if not text:
        return (None, None, None)

    matches = [int(token.replace(",", "")) for token in OWNER_PATTERN.findall(text)]
    if not matches:
        return (None, None, None)
    if len(matches) == 1:
        return (matches[0], matches[0], matches[0])

    owners_min, owners_max = matches[0], matches[1]
    owners_mid = (owners_min + owners_max) // 2
    return (owners_min, owners_max, owners_mid)


def parse_release_date(value: str | None) -> date | None:
    if is_missing(value):
        return None

    text = str(value).strip()
    if not text:
        return None

    formats = (
        "%b %d, %Y",
        "%B %d, %Y",
        "%b %Y",
        "%B %Y",
        "%Y-%m-%d",
        "%d/%m/%Y",
    )
    for fmt in formats:
        try:
            parsed = datetime.strptime(text, fmt)
            if fmt in ("%b %Y", "%B %Y"):
                return date(parsed.year, parsed.month, 1)
            return parsed.date()
        except ValueError:
            continue
    return None


def should_exclude_title(name: str | None) -> bool:
    if is_missing(name):
        return True
    text = str(name).strip()
    if not text:
        return True
    normalized = text.casefold()
    return any(term in normalized for term in EXCLUDED_TITLE_TERMS)


def price_bucket_for(price: float | int | None) -> str:
    numeric = float(price or 0)
    if numeric <= 0:
        return PRICE_BUCKET_LABELS[0]
    if numeric < 10:
        return PRICE_BUCKET_LABELS[1]
    if numeric < 20:
        return PRICE_BUCKET_LABELS[2]
    if numeric < 30:
        return PRICE_BUCKET_LABELS[3]
    if numeric < 50:
        return PRICE_BUCKET_LABELS[4]
    return PRICE_BUCKET_LABELS[5]


def classify_segment(genres: str | None, price: float | int | None, owners_mid: int | None) -> str:
    genre_text = "" if is_missing(genres) else str(genres).casefold()
    numeric_price = float(price or 0)
    numeric_owners = int(owners_mid or 0)

    if "indie" in genre_text:
        return "Indie"
    if "indie" not in genre_text and numeric_price >= 29.99 and numeric_owners >= 1_000_000:
        return "AAA"
    return "Other"


def classify_market_tier(segment: str | None, price: float | int | None, owners_mid: int | None) -> str:
    numeric_price = float(price or 0)
    numeric_owners = int(owners_mid or 0)
    normalized_segment = str(segment or "Other")

    if normalized_segment == "Indie":
        return "Indie"
    if numeric_price <= 0 and numeric_owners >= 1_000_000:
        return "Blockbuster F2P"
    if normalized_segment == "AAA":
        return "AAA Premium"
    return "Catalogo Geral"


def split_items(value: str | None) -> list[str]:
    if is_missing(value):
        return []
    parts = [part.strip() for part in str(value).split(",")]
    return [part for part in parts if part]


def first_item(items: Iterable[str]) -> str:
    for item in items:
        cleaned = item.strip()
        if cleaned:
            return cleaned
    return "Unknown"


def _load_raw_dataframe(input_path: Path):
    pd = _require_pandas()
    rows: list[dict[str, str]] = []
    max_index = max(RAW_FIELD_POSITIONS.values())

    with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        for row in reader:
            if len(row) <= max_index:
                continue
            rows.append({field: row[position] for field, position in RAW_FIELD_POSITIONS.items()})

    return pd.DataFrame(rows)


def prepare_games_dataframe(input_path: Path):
    pd = _require_pandas()
    df = _load_raw_dataframe(input_path)

    text_columns = ["name", "developers", "publishers", "categories", "genres", "tags"]
    for column in text_columns:
        df[column] = df[column].fillna("").astype(str).str.strip()

    df = df[~df["name"].map(should_exclude_title)].copy()

    df["release_date"] = df["release_date_raw"].map(parse_release_date)
    df = df[df["release_date"].notna()].copy()
    df["release_date"] = pd.to_datetime(df["release_date"])

    owner_values = df["estimated_owners_raw"].map(parse_owner_range)
    df["owners_min"] = [value[0] for value in owner_values]
    df["owners_max"] = [value[1] for value in owner_values]
    df["owners_mid"] = [value[2] for value in owner_values]

    numeric_columns = [
        "appid",
        "peak_ccu",
        "required_age",
        "price",
        "discount_dlc_count",
        "positive",
        "negative",
        "recommendations",
        "average_playtime_forever",
        "median_playtime_forever",
    ]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

    for column in ("windows", "mac", "linux"):
        df[column] = df[column].astype(str).str.casefold().eq("true")

    today = date.today()
    df["release_year"] = df["release_date"].dt.year
    df["game_age_years"] = (
        (today.year - df["release_date"].dt.year)
        - (
            (today.month < df["release_date"].dt.month)
            | (
                (today.month == df["release_date"].dt.month)
                & (today.day < df["release_date"].dt.day)
            )
        ).astype(int)
    ).clip(lower=0)

    total_reviews = df["positive"] + df["negative"]
    df["positive_ratio"] = (df["positive"] / total_reviews).where(total_reviews > 0)
    df["price_bucket"] = df["price"].map(price_bucket_for)
    df["is_free"] = df["price"].le(0)
    df["segment"] = [
        classify_segment(genres, price, owners_mid)
        for genres, price, owners_mid in zip(df["genres"], df["price"], df["owners_mid"], strict=False)
    ]
    df["market_tier"] = [
        classify_market_tier(segment, price, owners_mid)
        for segment, price, owners_mid in zip(df["segment"], df["price"], df["owners_mid"], strict=False)
    ]
    df["primary_genre"] = df["genres"].map(split_items).map(first_item)
    df["primary_category"] = df["categories"].map(split_items).map(first_item)
    df["engagement_hours"] = df["average_playtime_forever"] / 60.0

    review_base = df["positive_ratio"].fillna(0)
    owners_rank = df["owners_mid"].fillna(0).rank(pct=True)
    review_rank = review_base.rank(pct=True)
    engagement_rank = df["engagement_hours"].fillna(0).rank(pct=True)
    paid_affordability = (1 - df["price"].clip(lower=0, upper=60) / 60).clip(lower=0)
    affordability = paid_affordability.where(~df["is_free"], 0.8)
    affordability_rank = affordability.rank(pct=True)
    df["opportunity_score"] = (
        owners_rank * 0.35
        + review_rank * 0.30
        + engagement_rank * 0.20
        + affordability_rank * 0.15
    ) * 100

    final_columns = [
        "appid",
        "name",
        "release_date",
        "release_year",
        "game_age_years",
        "estimated_owners_raw",
        "owners_min",
        "owners_max",
        "owners_mid",
        "peak_ccu",
        "required_age",
        "price",
        "price_bucket",
        "is_free",
        "market_tier",
        "discount_dlc_count",
        "positive",
        "negative",
        "positive_ratio",
        "recommendations",
        "average_playtime_forever",
        "median_playtime_forever",
        "engagement_hours",
        "developers",
        "publishers",
        "categories",
        "primary_category",
        "genres",
        "primary_genre",
        "tags",
        "segment",
        "opportunity_score",
        "windows",
        "mac",
        "linux",
    ]
    return df[final_columns].sort_values(["peak_ccu", "owners_mid"], ascending=[False, False]).reset_index(drop=True)


def sample_monitor_candidates(df, limit: int = 20):
    columns = ["appid", "name", "peak_ccu", "segment", "primary_genre", "price", "owners_mid"]
    return (
        df.sort_values(["peak_ccu", "owners_mid"], ascending=[False, False])[columns]
        .head(limit)
        .reset_index(drop=True)
    )


def write_processed_outputs(df, output_csv: Path, output_parquet: Path | None = None) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)

    if output_parquet is None:
        return

    try:
        df.to_parquet(output_parquet, index=False)
    except Exception:
        pass
