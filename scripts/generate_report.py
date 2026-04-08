from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pandas as pd

from steam_dashboard.insights import build_report_payload
from steam_dashboard.paths import DEFAULT_CCU_HISTORY, DEFAULT_PROCESSED_CSV, DEFAULT_PROCESSED_PARQUET


def load_games():
    if DEFAULT_PROCESSED_PARQUET.exists():
        return pd.read_parquet(DEFAULT_PROCESSED_PARQUET)
    return pd.read_csv(DEFAULT_PROCESSED_CSV, parse_dates=["release_date"])


def load_ccu():
    if not DEFAULT_CCU_HISTORY.exists():
        return pd.DataFrame()
    return pd.read_csv(DEFAULT_CCU_HISTORY, parse_dates=["captured_at"])


def build_markdown(payload: dict, games_df: pd.DataFrame, ccu_df: pd.DataFrame) -> str:
    insights_md = "\n".join(
        f"{index}. **{item['title']}**: {item['value']} - {item['detail']}"
        for index, item in enumerate(payload["insights"], start=1)
    )
    opportunities_md = "\n".join(
        f"- {item['name']} | {item['market_tier']} | {item['primary_genre']} | ${item['price']:.2f} | score {item['opportunity_score']:.1f}"
        for item in payload["top_opportunities"][:10]
    )

    operational_md = "Sem snapshots operacionais."
    snapshot = payload["operational_snapshot"]
    if snapshot is not None and not snapshot.empty:
        lines = []
        for _, row in snapshot.head(10).iterrows():
            lines.append(
                f"- {row['name']}: {int(row['current_players']):,} jogadores agora, {row['utilization_pct']:.1f}% do pico historico."
            )
        operational_md = "\n".join(lines)

    strategy = payload["strategy"]
    return f"""# Steam Decision Report

## Resumo executivo

- Jogos processados: {len(games_df):,}
- Snapshots operacionais: {len(ccu_df):,}
- Pontos unicos de coleta: {ccu_df['captured_at'].nunique() if not ccu_df.empty else 0}
- Sintese: {strategy['summary']}

## 10 informacoes gerenciais

{insights_md}

## Radar de oportunidade

{opportunities_md}

## Monitoramento operacional

{operational_md}

## Estrategia de 3, 6 e 12 meses

### 3 meses
""" + "\n".join(f"- {item}" for item in strategy["three_months"]) + """

### 6 meses
""" + "\n".join(f"- {item}" for item in strategy["six_months"]) + """

### 1 ano
""" + "\n".join(f"- {item}" for item in strategy["one_year"]) + f"""

## Demandas, prioridades e riscos

### Demandas
{chr(10).join(f"- {item}" for item in strategy["demands"])}

### Prioridades
{chr(10).join(f"- {item}" for item in strategy["priorities"])}

### Riscos
{chr(10).join(f"- {item}" for item in strategy["risks"])}
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera um relatorio academico em Markdown.")
    parser.add_argument("--output", default="output/steam_decision_report.md")
    args = parser.parse_args()

    games_df = load_games()
    ccu_df = load_ccu()
    payload = build_report_payload(games_df, ccu_df if not ccu_df.empty else None)
    markdown = build_markdown(payload, games_df, ccu_df)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
