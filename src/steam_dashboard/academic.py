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
    raw_sales: pd.DataFrame
    raw_customer_profile: pd.DataFrame
    raw_store_access: pd.DataFrame


def _to_weekday_categorical(frame: pd.DataFrame, column: str = "weekday") -> pd.DataFrame:
    frame[column] = pd.Categorical(frame[column], categories=WEEKDAY_ORDER, ordered=True)
    return frame


def _dominant_daily_campaign(raw_sales: pd.DataFrame) -> pd.DataFrame:
    dominant = (
        raw_sales.groupby(["date", "campaign_type"], observed=False)["gross_revenue_brl"]
        .sum()
        .reset_index()
        .sort_values(["date", "gross_revenue_brl", "campaign_type"], ascending=[True, False, True])
        .drop_duplicates(subset=["date"])
        .rename(columns={"campaign_type": "campaign_type"})
    )
    return dominant[["date", "campaign_type"]]


def aggregate_sales(raw_sales: pd.DataFrame) -> pd.DataFrame:
    sales = (
        raw_sales.groupby("date", observed=False)
        .agg(
            weekday=("weekday", "first"),
            units_sold=("units", "sum"),
            revenue_brl=("gross_revenue_brl", "sum"),
            orders=("order_id", "nunique"),
            average_ticket_brl=("gross_revenue_brl", "mean"),
        )
        .reset_index()
    )
    sales = sales.merge(_dominant_daily_campaign(raw_sales), on="date", how="left")
    sales = _to_weekday_categorical(sales).sort_values("date").reset_index(drop=True)
    return sales


def aggregate_customer_profile(raw_customer_profile: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        raw_customer_profile.groupby(["weekday", "preferred_genre"], observed=False)
        .size()
        .reset_index(name="customer_count")
        .rename(columns={"preferred_genre": "genre"})
    )
    grouped["customer_share_pct"] = (
        grouped["customer_count"]
        / grouped.groupby("weekday", observed=False)["customer_count"].transform("sum")
        * 100
    ).round(2)
    grouped = _to_weekday_categorical(grouped).sort_values(["weekday", "customer_count"], ascending=[True, False])
    return grouped.reset_index(drop=True)


def aggregate_store_access(raw_store_access: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        raw_store_access.groupby(["weekday", "shift"], observed=False)
        .size()
        .reset_index(name="visits")
    )
    grouped = _to_weekday_categorical(grouped)
    grouped["shift"] = pd.Categorical(grouped["shift"], categories=SHIFT_ORDER, ordered=True)
    grouped = grouped.sort_values(["weekday", "shift"]).reset_index(drop=True)
    return grouped


def load_academic_sources() -> AcademicSources:
    raw_sales = pd.read_csv(
        DEFAULT_ACADEMIC_DAILY_SALES,
        parse_dates=["order_ts", "date"],
        dtype={
            "order_id": "string",
            "weekday": "string",
            "country": "string",
            "region": "string",
            "channel": "string",
            "campaign_type": "string",
            "genre": "string",
            "market_segment": "string",
            "product_type": "string",
            "is_bundle": "boolean",
            "is_repeat_customer": "boolean",
        },
    )
    raw_customer_profile = pd.read_csv(
        DEFAULT_ACADEMIC_CUSTOMER_PROFILE,
        parse_dates=["event_ts", "date"],
        dtype={
            "profile_id": "string",
            "weekday": "string",
            "country": "string",
            "platform": "string",
            "acquisition_channel": "string",
            "customer_type": "string",
            "preferred_genre": "string",
            "wishlist_add": "boolean",
            "cart_add": "boolean",
        },
    )
    raw_store_access = pd.read_csv(
        DEFAULT_ACADEMIC_STORE_ACCESS,
        parse_dates=["visit_ts", "date"],
        dtype={
            "session_id": "string",
            "weekday": "string",
            "shift": "string",
            "country": "string",
            "device_type": "string",
            "traffic_source": "string",
            "landing_surface": "string",
            "wishlist_action": "boolean",
            "cart_action": "boolean",
        },
    )

    raw_sales = _to_weekday_categorical(raw_sales)
    raw_customer_profile = _to_weekday_categorical(raw_customer_profile)
    raw_store_access = _to_weekday_categorical(raw_store_access)
    raw_store_access["shift"] = pd.Categorical(raw_store_access["shift"], categories=SHIFT_ORDER, ordered=True)

    return AcademicSources(
        sales=aggregate_sales(raw_sales),
        customer_profile=aggregate_customer_profile(raw_customer_profile),
        store_access=aggregate_store_access(raw_store_access),
        raw_sales=raw_sales,
        raw_customer_profile=raw_customer_profile,
        raw_store_access=raw_store_access,
    )


def build_sales_calendar_table(sales_df: pd.DataFrame) -> pd.DataFrame:
    ordered = sales_df.sort_values("date").copy()
    ordered["week_index"] = ((ordered["date"].dt.day - 1) // 7) + 1
    ordered["label"] = ordered["date"].dt.day.astype(str).radd("Dia ") + ": " + ordered["units_sold"].astype(int).map("{:,}".format)
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
            "value": f"{best_day} ({best_day_value:,.0f} jogos)",
            "why": f"{best_day} concentra a media mais alta de unidades vendidas no mes analisado.",
            "action": f"A janela de {best_day} deve receber o principal destaque promocional da SteamLoja.",
        },
        {
            "group": "Vendas",
            "title": "Relacao entre o melhor e o pior dia",
            "value": f"{best_day_value / worst_day_value:.2f}x",
            "why": f"A diferenca entre {best_day} e {worst_day} confirma uma operacao com picos claros de demanda.",
            "action": f"{worst_day} deve ser tratado como prioridade para campanhas de reativacao e oferta de entrada.",
        },
        {
            "group": "Vendas",
            "title": "Peso de sexta e sabado nas vendas do mes",
            "value": f"{weekend_share:.1f}%",
            "why": "O fechamento da semana concentra parte relevante da conversao total da loja.",
            "action": "Vitrine, bundles e verba promocional precisam estar mais fortes nesse intervalo.",
        },
        {
            "group": "Vendas",
            "title": "Total vendido e media diaria",
            "value": f"{total_units:,} jogos | media {daily_average:,.0f}",
            "why": "Esse volume define a escala da operacao academica e cria uma base comparavel para ciclos futuros.",
            "action": "A media diaria deve ser usada como referencia para metas e avaliacao de campanhas.",
        },
        {
            "group": "Clientes",
            "title": "Genero com maior interesse do publico",
            "value": f"{top_genre} ({top_genre_value:.1f}%)",
            "why": "Esse genero lidera o interesse observado no comportamento semanal dos clientes.",
            "action": f"A curadoria comercial e a comunicacao principal devem priorizar jogos de {top_genre}.",
        },
        {
            "group": "Clientes",
            "title": "Participacao conjunta dos generos mais fortes",
            "value": f"{top_three_share:.1f}%",
            "why": "Os tres generos lideres concentram a maior parte do interesse potencial de compra.",
            "action": "Bundles, colecoes e campanhas tematicas devem partir dos generos mais fortes.",
        },
        {
            "group": "Acessos e comportamento",
            "title": "Turno com maior volume de acessos",
            "value": f"{top_shift} ({top_shift_value:,.0f} acessos)",
            "why": "O fluxo de visitas fica mais intenso nesse turno e amplia o potencial de conversao.",
            "action": f"As atualizacoes centrais de vitrine devem ser publicadas na {top_shift.lower()}.",
        },
        {
            "group": "Acessos e comportamento",
            "title": "Dia e turno de maior trafego",
            "value": f"{top_window['weekday']} / {top_window['shift']}",
            "why": "Essa e a janela de maior exposicao da SteamLoja na semana observada.",
            "action": "Lancamentos, ofertas premium e banners principais devem estrear nesse pico.",
        },
        {
            "group": "Acessos e comportamento",
            "title": "Janela de baixa demanda para reativacao",
            "value": f"{low_window['weekday']} / {low_window['shift']}",
            "why": "Esse ponto concentra o menor fluxo de acesso e representa o principal vale operacional.",
            "action": "Cupom leve, bundle de entrada ou conteudo editorial devem ser testados nesse horario.",
        },
        {
            "group": "Acessos e comportamento",
            "title": "Melhor combinacao comercial do recorte",
            "value": f"{best_conversion_day} + {top_genre} + {top_shift}",
            "why": "A combinacao reune o melhor dia de vendas, o genero dominante e o turno de maior trafego.",
            "action": f"A campanha principal deve ser organizada em {best_conversion_day}, com foco em {top_genre}, no turno da {top_shift.lower()}.",
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


def build_methodology_note(sources: AcademicSources) -> str:
    return (
        "A camada academica foi modelada em grao detalhado e depois consolidada para apresentacao. "
        f"O recorte inclui {len(sources.raw_sales):,} pedidos, {len(sources.raw_customer_profile):,} sinais de perfil de cliente "
        f"e {len(sources.raw_store_access):,} sessoes de acesso, distribuidos por pais, canal, campanha, dispositivo e genero."
    )


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
        "methodology_note": build_methodology_note(sources),
    }
