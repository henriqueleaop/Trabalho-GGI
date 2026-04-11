from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pandas as pd

from steam_dashboard.academic import (
    build_academic_insights,
    build_market_anchors,
    build_sales_calendar_table,
    build_strategy_payload,
    load_academic_sources,
)
from steam_dashboard.paths import DEFAULT_PROCESSED_CSV, DEFAULT_PROCESSED_PARQUET


def load_games() -> pd.DataFrame:
    if DEFAULT_PROCESSED_PARQUET.exists():
        return pd.read_parquet(DEFAULT_PROCESSED_PARQUET)
    return pd.read_csv(DEFAULT_PROCESSED_CSV, parse_dates=["release_date"])


def build_markdown(games_df: pd.DataFrame) -> str:
    sources = load_academic_sources()
    insights = build_academic_insights(sources.sales, sources.customer_profile, sources.store_access)
    anchors = build_market_anchors(games_df)
    strategy = build_strategy_payload(insights, anchors, sources.sales, sources.customer_profile, sources.store_access)
    sales_calendar = build_sales_calendar_table(sources.sales)

    sales_calendar_md = "```text\n" + sales_calendar.to_string() + "\n```"
    customer_md = (
        "```text\n"
        + sources.customer_profile.pivot(index="weekday", columns="genre", values="customer_share_pct").to_string()
        + "\n```"
    )
    access_md = (
        "```text\n"
        + sources.store_access.pivot(index="weekday", columns="shift", values="visits").to_string()
        + "\n```"
    )
    insights_md = "\n".join(
        f"{index}. **{item['title']}**: {item['value']} - {item['why']} Acao sugerida: {item['action']}"
        for index, item in enumerate(insights, start=1)
    )
    opportunities_md = "\n".join(
        f"- {item['name']} | {item['market_tier']} | {item['primary_genre']} | ${item['price']:.2f} | indicador {item['indicador_composto']:.1f} | Linux: {'Sim' if item['linux'] else 'Nao'}"
        for item in anchors["opportunities"]
    )
    action_md = "\n".join(
        f"- **{item['title']}**: {item['do']} {item['because']} {item['impact']}"
        for item in strategy["actions"]
    )

    return f"""# SteamLoja Academica

## Introducao

Este relatorio apresenta a SteamLoja como empresa ficticia inspirada no ecossistema Steam. O objetivo e mostrar a passagem de dado bruto para informacao gerencial e, depois, para planejamento estrategico.

## Fase 1: Coleta e Organizacao

Nesta etapa a SteamLoja apenas observa o funcionamento da operacao.

### Fonte 1: Vendas diarias do mes

{sales_calendar_md}

### Fonte 2: Perfil de clientes por genero

{customer_md}

### Fonte 3: Acessos por turno

{access_md}

## Fase 2: Processamento e Insights

### 10 informacoes estrategicas

{insights_md}

### Ancoras de mercado Steam

- Diferenca de preco mediano entre AAA e Indie: ${anchors['price_diff']:,.2f}
- Participacao de jogos gratis no topo: {anchors['free_share_top']:.1f}%
- Presenca de suporte Linux no topo: {anchors['linux_share_top']:.1f}%

### Jogos com maior potencial

{opportunities_md}

### Indicador composto de oportunidade

{anchors['indicator_formula']}

## Fase 3: Planejamento Estrategico

### Resumo executivo

{strategy['summary']}

### Cronograma de 3 meses
""" + "\n".join(
        f"- Fazer isso: {item['do']} Por causa disso: {item['because']} Impacto esperado: {item['impact']}"
        for item in strategy["three_months"]
    ) + """

### Cronograma de 6 meses
""" + "\n".join(
        f"- Fazer isso: {item['do']} Por causa disso: {item['because']} Impacto esperado: {item['impact']}"
        for item in strategy["six_months"]
    ) + """

### Cronograma de 1 ano
""" + "\n".join(
        f"- Fazer isso: {item['do']} Por causa disso: {item['because']} Impacto esperado: {item['impact']}"
        for item in strategy["one_year"]
    ) + f"""

### Demandas e tarefas
{chr(10).join(f"- {item}" for item in strategy["demands"] + strategy["tasks"])}

### Prioridades
{chr(10).join(f"- {item}" for item in strategy["priorities"])}

### Riscos e contingencias
{chr(10).join(f"- {item}" for item in strategy["risks"] + strategy["contingencies"])}

### 3 acoes estrategicas principais
{action_md}

### Conexao com o mercado
{strategy['market_connection']}

## Aderencia as decisoes reais da Steam/Valve

- A leitura de Linux e SteamOS aproxima o trabalho da estrategia de plataforma aberta da Valve.
- O foco em eventos, weekly deals e bundles reflete a forma como a Steam organiza divulgacao e descoberta.
- A referencia a Steam Machine -> Steam Deck reforca que o ecossistema da Valve amadureceu de tentativa isolada para proposta integrada.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera um relatorio academico em Markdown.")
    parser.add_argument("--output", default="output/steam_decision_report.md")
    args = parser.parse_args()

    games_df = load_games()
    markdown = build_markdown(games_df)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
