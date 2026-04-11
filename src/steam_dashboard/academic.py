from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .insights import WEEKDAY_ORDER
from .paths import (
    DEFAULT_ACADEMIC_CUSTOMER_PROFILE,
    DEFAULT_ACADEMIC_DAILY_SALES,
    DEFAULT_ACADEMIC_STORE_ACCESS,
)


SHIFT_ORDER = ["Manha", "Tarde", "Noite"]
SOURCE_OPTIONS = ["Operacao da loja", "Mercado Steam", "Visao integrada"]


@dataclass(frozen=True)
class AcademicSources:
    sales: pd.DataFrame
    customer_profile: pd.DataFrame
    store_access: pd.DataFrame


def load_academic_sources() -> AcademicSources:
    sales = pd.read_csv(DEFAULT_ACADEMIC_DAILY_SALES, parse_dates=["date"])
    customer_profile = pd.read_csv(DEFAULT_ACADEMIC_CUSTOMER_PROFILE)
    store_access = pd.read_csv(DEFAULT_ACADEMIC_STORE_ACCESS)

    sales["weekday"] = pd.Categorical(sales["weekday"], categories=WEEKDAY_ORDER, ordered=True)
    customer_profile["weekday"] = pd.Categorical(customer_profile["weekday"], categories=WEEKDAY_ORDER, ordered=True)
    store_access["weekday"] = pd.Categorical(store_access["weekday"], categories=WEEKDAY_ORDER, ordered=True)
    store_access["shift"] = pd.Categorical(store_access["shift"], categories=SHIFT_ORDER, ordered=True)

    return AcademicSources(sales=sales, customer_profile=customer_profile, store_access=store_access)


def build_sales_calendar_table(sales_df: pd.DataFrame) -> pd.DataFrame:
    ordered = sales_df.sort_values("date").copy()
    ordered["week_index"] = ((ordered["date"].dt.day - 1) // 7) + 1
    ordered["label"] = ordered["date"].dt.day.astype(str).radd("Dia ") + ": " + ordered["units_sold"].astype(int).astype(str)
    calendar = ordered.pivot(index="week_index", columns="weekday", values="label").reindex(columns=WEEKDAY_ORDER)
    calendar.index = [f"Semana {value}" for value in calendar.index]
    return calendar.fillna("-")


def build_academic_insights(sales_df: pd.DataFrame, customer_df: pd.DataFrame, access_df: pd.DataFrame) -> list[dict[str, str]]:
    weekday_sales = sales_df.groupby("weekday", observed=False)["units_sold"].mean().reindex(WEEKDAY_ORDER).dropna()
    best_day = str(weekday_sales.idxmax())
    best_day_value = float(weekday_sales.max())
    worst_day = str(weekday_sales.idxmin())
    worst_day_value = float(weekday_sales.min())

    weekend_units = int(sales_df[sales_df["weekday"].isin(["Sexta", "Sabado"])]["units_sold"].sum())
    total_units = int(sales_df["units_sold"].sum())
    daily_average = float(sales_df["units_sold"].mean())
    weekend_share = (weekend_units / total_units) * 100 if total_units else 0.0

    genre_share = (
        customer_df.groupby("genre", observed=False)["customer_share_pct"]
        .mean()
        .sort_values(ascending=False)
    )
    top_genre = str(genre_share.index[0])
    top_genre_value = float(genre_share.iloc[0])
    top_three_share = float(genre_share.head(3).sum())

    shift_visits = access_df.groupby("shift", observed=False)["visits"].mean().reindex(SHIFT_ORDER).dropna()
    top_shift = str(shift_visits.idxmax())
    top_shift_value = float(shift_visits.max())

    top_window = access_df.sort_values("visits", ascending=False).iloc[0]
    low_window = access_df.sort_values("visits", ascending=True).iloc[0]

    weekend_days = weekday_sales.reindex(["Sexta", "Sabado"]).dropna()
    best_conversion_day = str(weekend_days.idxmax()) if not weekend_days.empty else best_day

    return [
        {
            "group": "Vendas",
            "title": "Dia com maior media de vendas",
            "value": f"{best_day} ({best_day_value:.1f} jogos)",
            "why": f"{best_day} apresenta o melhor desempenho medio de vendas no mes analisado.",
            "action": f"Recomenda-se concentrar campanhas de destaque e bundles em {best_day}.",
        },
        {
            "group": "Vendas",
            "title": "Relacao entre o melhor e o pior dia",
            "value": f"{best_day_value / worst_day_value:.2f}x",
            "why": f"{best_day} vende significativamente mais do que {worst_day}, evidenciando uma operacao com picos bem definidos.",
            "action": f"{worst_day} deve ser tratado como janela prioritaria para acoes de reativacao e ofertas de entrada.",
        },
        {
            "group": "Vendas",
            "title": "Peso de sexta e sabado nas vendas do mes",
            "value": f"{weekend_share:.1f}%",
            "why": "O fim da semana concentra uma parcela relevante da demanda da SteamLoja.",
            "action": "A vitrine principal e o investimento promocional devem ser mais fortes nessa janela.",
        },
        {
            "group": "Vendas",
            "title": "Total vendido e media diaria",
            "value": f"{total_units:,} jogos | media {daily_average:.2f}",
            "why": "Esse numero define a escala da operacao analisada e serve de referencia para metas e comparacoes futuras.",
            "action": "A media diaria deve ser adotada como linha de base para avaliar o desempenho das proximas campanhas.",
        },
        {
            "group": "Clientes",
            "title": "Genero com maior interesse do publico",
            "value": f"{top_genre} ({top_genre_value:.1f}%)",
            "why": "Esse genero aparece como preferencia dominante no perfil semanal de clientes.",
            "action": f"A comunicacao e a curadoria comercial devem dar maior destaque aos jogos de {top_genre}.",
        },
        {
            "group": "Clientes",
            "title": "Participacao conjunta dos generos mais fortes",
            "value": f"{top_three_share:.1f}%",
            "why": "Os tres generos lideres concentram a maior parte do interesse comercial observado na semana.",
            "action": "Catalogo, bundles e anuncios devem priorizar os generos com maior tracao.",
        },
        {
            "group": "Acessos e comportamento",
            "title": "Turno com maior volume de acessos",
            "value": f"{top_shift} ({top_shift_value:.0f} acessos)",
            "why": "O horario noturno concentra mais visitas e tende a reunir maior potencial de conversao.",
            "action": f"As principais atualizacoes de vitrine e comunicacao devem ser programadas para a {top_shift.lower()}.",
        },
        {
            "group": "Acessos e comportamento",
            "title": "Dia e turno de maior trafego",
            "value": f"{top_window['weekday']} / {top_window['shift']}",
            "why": "Essa e a janela de maior exposicao da SteamLoja na semana analisada.",
            "action": "Esse pico deve receber lancamentos, bundles premium e o principal destaque de vitrine.",
        },
        {
            "group": "Acessos e comportamento",
            "title": "Janela de baixa demanda para reativacao",
            "value": f"{low_window['weekday']} / {low_window['shift']}",
            "why": "Esse e o ponto mais fraco de acesso da semana e exige intervencao para reduzir o vale operacional.",
            "action": "Vale testar cupom, oferta leve ou bundle de entrada nesse horario.",
        },
        {
            "group": "Acessos e comportamento",
            "title": "Melhor combinacao comercial do recorte",
            "value": f"{best_conversion_day} + {top_genre} + {top_shift}",
            "why": "A combinacao reune o melhor dia de venda, o genero de maior interesse e o turno de maior trafego.",
            "action": f"A campanha principal da SteamLoja deve ser organizada em {best_conversion_day}, no turno da {top_shift.lower()}, com foco em {top_genre}.",
        },
    ]


def build_market_anchors(games_df: pd.DataFrame) -> dict[str, object]:
    popularity_base = games_df[games_df["peak_ccu"] > 0].copy()
    top_decile_cutoff = popularity_base["peak_ccu"].quantile(0.9) if not popularity_base.empty else 0
    top_decile = popularity_base[popularity_base["peak_ccu"] >= top_decile_cutoff].copy()

    aaa_prices = games_df.loc[games_df["segment"] == "AAA", "price"]
    indie_prices = games_df.loc[games_df["segment"] == "Indie", "price"]
    aaa_median = float(aaa_prices.median()) if not aaa_prices.empty else 0.0
    indie_median = float(indie_prices.median()) if not indie_prices.empty else 0.0
    price_diff = aaa_median - indie_median

    free_share = float(top_decile["is_free"].mean() * 100) if not top_decile.empty else 0.0
    linux_share = float(top_decile["linux"].mean() * 100) if not top_decile.empty else 0.0

    opportunities = (
        games_df[games_df["positive_ratio"].notna()]
        .sort_values(["opportunity_score", "owners_mid"], ascending=[False, False])
        .head(8)[["name", "market_tier", "primary_genre", "price", "opportunity_score", "linux"]]
        .rename(columns={"opportunity_score": "indicador_composto"})
        .to_dict("records")
    )

    return {
        "price_diff": price_diff,
        "free_share_top": free_share,
        "linux_share_top": linux_share,
        "opportunities": opportunities,
        "indicator_formula": (
            "Indicador composto: combina base estimada de owners, aprovacao do publico, engajamento e acessibilidade de preco. "
            "Ele orienta a leitura comercial do catalogo, mas nao substitui avaliacao qualitativa."
        ),
    }


def build_strategy_payload(
    insights: list[dict[str, str]],
    anchors: dict[str, object],
    sales_df: pd.DataFrame,
    customer_df: pd.DataFrame,
    access_df: pd.DataFrame,
) -> dict[str, object]:
    best_day = insights[0]["value"].split(" (")[0]
    low_window = insights[8]["value"]
    best_combo = insights[9]["value"]
    top_genre = insights[4]["value"].split(" (")[0]
    top_shift = insights[6]["value"].split(" (")[0]

    price_diff = float(anchors["price_diff"])
    free_share = float(anchors["free_share_top"])
    linux_share = float(anchors["linux_share_top"])
    revenue_total = float(sales_df["revenue_brl"].sum())

    return {
        "summary": (
            f"A SteamLoja apresenta seu melhor desempenho comercial em {best_day}, maior interesse do publico em {top_genre} "
            f"e pico de visitas no turno da {top_shift.lower()}. O plano proposto busca reduzir o vale de {low_window} sem comprometer a janela mais forte de conversao. "
            f"Como referencia externa, o mercado Steam mostra diferenca de ${price_diff:,.2f} entre AAA e Indie, "
            f"com {free_share:.1f}% de jogos gratuitos entre os titulos mais populares e {linux_share:.1f}% de suporte Linux nesse grupo."
        ),
        "three_months": [
            {
                "do": f"Reforcar a vitrine principal em {best_day}, com foco na combinacao {best_combo}.",
                "because": "Essa e a janela de maior demanda e concentracao de interesse do recorte analisado.",
                "impact": "A medida tende a elevar a conversao sem aumentar significativamente a complexidade operacional.",
            },
            {
                "do": f"Criar uma campanha de reativacao para {low_window}.",
                "because": "Esse e o principal vale semanal de acesso e precisa ser tratado com prioridade.",
                "impact": "A acao reduz ociosidade e melhora a distribuicao das vendas ao longo da semana.",
            },
            {
                "do": "Organizar bundles simples por genero lider e ticket de entrada.",
                "because": "O publico demonstrou preferencia clara por poucos generos centrais.",
                "impact": "Isso tende a acelerar a decisao de compra e simplificar a comunicacao da loja.",
            },
        ],
        "six_months": [
            {
                "do": "Criar rotina mensal de leitura de indicadores e ajuste de calendario promocional.",
                "because": "A operacao precisa transformar dados em decisao recorrente, e nao em analise eventual.",
                "impact": "A iniciativa melhora previsibilidade comercial e disciplina gerencial.",
            },
            {
                "do": "Ampliar a curadoria de jogos alinhados a Linux e SteamOS.",
                "because": "A Valve continua investindo em plataforma aberta e compatibilidade, especialmente apos o Steam Deck.",
                "impact": "Isso posiciona a SteamLoja mais perto das tendencias reais do ecossistema Steam.",
            },
            {
                "do": "Testar campanhas tematicas inspiradas em weekly deals e eventos sazonais.",
                "because": "A divulgacao da Steam se apoia em rituais promocionais recorrentes e de facil comunicacao.",
                "impact": "A medida tende a gerar previsibilidade de audiencia e aumentar lembranca de marca.",
            },
        ],
        "one_year": [
            {
                "do": "Abrir uma frente comercial para hardware, gift cards e acessorios do ecossistema Steam.",
                "because": "A transicao de Steam Machine para Steam Deck mostra que a aderencia vem do ecossistema, nao de um produto isolado.",
                "impact": "A estrategia diversifica receita e fortalece a identidade da SteamLoja.",
            },
            {
                "do": "Evoluir o painel para monitoramento continuo com mais fontes do mercado Steam.",
                "because": "O trabalho atual demonstra valor, mas a maturidade depende de acompanhamento continuo.",
                "impact": "Isso permite planejamento anual com menos intuicao e mais evidencia.",
            },
            {
                "do": "Construir experiencias proprias de divulgacao, como calendario de eventos e recomendacoes editoriais.",
                "because": "A Steam nao depende apenas de preco, mas tambem de descoberta, comunidade e repertorio de vitrine.",
                "impact": "A medida fortalece diferenciacao competitiva e fidelizacao.",
            },
        ],
        "demands": [
            "Aumentar vendas fora do pico de sexta e sabado.",
            "Melhorar o aproveitamento dos horarios com maior trafego.",
            "Ajustar catalogo e comunicacao ao interesse dominante do publico.",
        ],
        "tasks": [
            "Revisar semanalmente vendas, genero preferido e acessos por turno.",
            "Atualizar vitrine e bundles de acordo com o calendario promocional.",
            "Acompanhar evidencias de mercado Steam para validar o posicionamento da SteamLoja.",
        ],
        "priorities": [
            "Alta: ocupar a janela mais forte com campanhas melhores e corrigir o principal vale da semana.",
            "Media: expandir curadoria e comunicacao para o genero lider e para produtos aderentes ao SteamOS.",
            "Baixa: abrir novas frentes de hardware e experiencias editoriais proprias.",
        ],
        "risks": [
            "Risco comercial: campanhas fracas em dias de pico desperdicam a melhor janela de conversao.",
            "Risco operacional: excesso de concentracao no fim da semana pode sobrecarregar suporte e atendimento.",
            "Risco estrategico: ignorar movimentos da Valve em Linux, SteamOS e Steam Deck afasta a loja das tendencias reais do mercado.",
        ],
        "contingencies": [
            "Manter plano promocional alternativo para dias de baixa resposta.",
            "Reforcar suporte nos picos de sexta e sabado.",
            "Revisar trimestralmente o catalogo com base em aderencia ao ecossistema Steam.",
        ],
        "actions": [
            {
                "title": "Campanhas de reativacao na janela fraca",
                "do": f"Ativar bundles leves e cupons em {low_window}.",
                "because": "Esse e o ponto mais fraco da semana em acesso e potencial de venda.",
                "impact": "A tendencia e reduzir o vale operacional e gerar receita incremental.",
            },
            {
                "title": "Vitrine principal no melhor combo comercial",
                "do": f"Concentrar a campanha principal em {best_combo}.",
                "because": "Essa combinacao une o melhor dia, o genero dominante e o turno de maior trafego.",
                "impact": "A expectativa e elevar a conversao nas janelas de maior retorno.",
            },
            {
                "title": "Curadoria alinhada ao ecossistema Valve",
                "do": "Ampliar produtos e comunicacao ligados a Linux, SteamOS e Steam Deck.",
                "because": "A Valve migrou de tentativas isoladas para um ecossistema integrado e hoje colhe resultado com o Steam Deck.",
                "impact": "Isso torna a SteamLoja mais atual, coerente e mais solida para a defesa academica.",
            },
        ],
        "market_connection": (
            "O plano posiciona a SteamLoja como uma empresa ficticia coerente com o mercado real. "
            "Ele aproveita a logica promocional da Steam, observa a forca do free-to-play, reconhece a distancia entre AAA e Indie "
            "e usa suporte Linux como sinal de proximidade com a estrategia de SteamOS e Steam Deck. "
            f"O faturamento observado no mes-base foi de R${revenue_total:,.0f}, o que reforca a necessidade de proteger os dias fortes e recuperar os dias fracos."
        ),
    }


def build_academic_payload(games_df: pd.DataFrame) -> dict[str, object]:
    sources = load_academic_sources()
    insights = build_academic_insights(sources.sales, sources.customer_profile, sources.store_access)
    anchors = build_market_anchors(games_df)
    strategy = build_strategy_payload(insights, anchors, sources.sales, sources.customer_profile, sources.store_access)

    sales_weekday = (
        sources.sales.groupby("weekday", observed=False)["units_sold"]
        .mean()
        .reindex(WEEKDAY_ORDER)
        .dropna()
        .reset_index()
    )
    genre_average = (
        sources.customer_profile.groupby("genre", observed=False)["customer_share_pct"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    access_heatmap = (
        sources.store_access.pivot(index="weekday", columns="shift", values="visits")
        .reindex(index=WEEKDAY_ORDER, columns=SHIFT_ORDER)
    )

    return {
        "sources": sources,
        "sales_calendar": build_sales_calendar_table(sources.sales),
        "sales_weekday": sales_weekday,
        "genre_average": genre_average,
        "access_heatmap": access_heatmap,
        "insights": insights,
        "anchors": anchors,
        "strategy": strategy,
    }
