from __future__ import annotations

import pandas as pd


def normalize_appid_series(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    return numeric.astype("Int64").astype("string")


def normalize_appid_frame(df: pd.DataFrame, column: str = "appid") -> pd.DataFrame:
    normalized = df.copy()
    if column in normalized.columns:
        normalized[column] = normalize_appid_series(normalized[column])
    return normalized
