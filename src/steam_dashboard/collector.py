from __future__ import annotations

from datetime import datetime
from pathlib import Path
import csv
import os
import time
from typing import Callable


STEAM_CURRENT_PLAYERS_URL = "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/"
WEEKDAY_LABELS = {
    0: "Segunda",
    1: "Terca",
    2: "Quarta",
    3: "Quinta",
    4: "Sexta",
    5: "Sabado",
    6: "Domingo",
}


def load_monitor_targets(path: Path, limit: int = 20) -> list[dict[str, str]]:
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [row for row in reader]

    cleaned: list[dict[str, str]] = []
    for row in rows[:limit]:
        appid = str(row.get("appid", "")).strip()
        name = str(row.get("name", "")).strip()
        if not appid or not name:
            continue
        cleaned.append({"appid": appid, "name": name})
    return cleaned


def fetch_current_players(appid: str, api_key: str | None = None, timeout: int = 15) -> int | None:
    try:
        import requests
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "requests nao esta instalado. Instale as dependencias com `python -m pip install -r requirements.txt`."
        ) from exc

    params = {"appid": appid}
    if api_key:
        params["key"] = api_key

    response = requests.get(STEAM_CURRENT_PLAYERS_URL, params=params, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    return int(payload.get("response", {}).get("player_count", 0))


def build_snapshot_rows(
    targets: list[dict[str, str]],
    fetcher: Callable[[str], int | None],
    captured_at: datetime | None = None,
) -> list[dict[str, str | int]]:
    timestamp = captured_at or datetime.now()
    rows: list[dict[str, str | int]] = []

    for target in targets:
        current_players = fetcher(target["appid"])
        if current_players is None:
            continue

        rows.append(
            {
                "captured_at": timestamp.isoformat(timespec="seconds"),
                "captured_date": timestamp.date().isoformat(),
                "weekday": WEEKDAY_LABELS[timestamp.weekday()],
                "hour": timestamp.hour,
                "appid": target["appid"],
                "name": target["name"],
                "current_players": int(current_players),
            }
        )
    return rows


def append_snapshot_rows(history_path: Path, rows: list[dict[str, str | int]]) -> None:
    if not rows:
        return

    history_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["captured_at", "captured_date", "weekday", "hour", "appid", "name", "current_players"]
    file_exists = history_path.exists()

    with history_path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


def run_collector(
    targets: list[dict[str, str]],
    history_path: Path,
    interval_seconds: int,
    iterations: int,
    api_key_env: str = "STEAM_API_KEY",
    fetcher: Callable[[str], int | None] | None = None,
) -> int:
    total_rows = 0
    api_key = os.getenv(api_key_env)

    effective_fetcher = fetcher
    if effective_fetcher is None:
        effective_fetcher = lambda appid: fetch_current_players(appid, api_key=api_key)

    for index in range(iterations):
        rows = build_snapshot_rows(targets=targets, fetcher=effective_fetcher)
        append_snapshot_rows(history_path, rows)
        total_rows += len(rows)

        has_next_iteration = index < iterations - 1
        if has_next_iteration and interval_seconds > 0:
            time.sleep(interval_seconds)

    return total_rows
