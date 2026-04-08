from __future__ import annotations

from typing import Any

from .data_utils import normalize_appid_frame


WEEKDAY_ORDER = ["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo"]


def _coerce_value(value, fallback: str = "Sem dados") -> str:
    if value is None:
        return fallback
    return str(value)


def _describe_age_popularity_relation(correlation: float | None) -> str:
    if correlation is None:
        return "Nao ha dados suficientes para medir a relacao entre idade e popularidade."

    absolute = abs(correlation)
    if absolute < 0.1:
        strength = "muito fraca"
    elif absolute < 0.3:
        strength = "fraca"
    elif absolute < 0.5:
        strength = "moderada"
    else:
        strength = "forte"

    direction = "positiva" if correlation > 0 else "negativa"
    return f"A correlacao e {direction} e {strength} ({correlation:.2f}), sugerindo {'ganho' if correlation > 0 else 'perda'} de popularidade com o envelhecimento."


def _default_operational_insight(title: str) -> dict[str, str]:
    return {
        "title": title,
        "value": "Aguardando coleta",
        "detail": "Execute o coletor para alimentar a visao operacional por hora e dia da semana.",
    }


def build_operational_snapshot(games_df, ccu_df):
    if ccu_df is None or ccu_df.empty:
        return None

    normalized_games = normalize_appid_frame(games_df[["appid", "peak_ccu", "market_tier", "segment"]])
    normalized_ccu = normalize_appid_frame(ccu_df)

    latest_time = normalized_ccu["captured_at"].max()
    latest_snapshot = normalized_ccu[normalized_ccu["captured_at"] == latest_time].copy()
    if latest_snapshot.empty:
        return None

    merged = latest_snapshot.merge(normalized_games, on="appid", how="left")
    merged["peak_ccu"] = merged["peak_ccu"].fillna(0)
    merged["utilization_pct"] = ((merged["current_players"] / merged["peak_ccu"].replace(0, float("nan"))) * 100).fillna(0)
    merged["peak_status"] = merged["utilization_pct"].apply(
        lambda value: "Acima do pico historico da base" if value > 100 else "Dentro do pico historico"
    )

    if normalized_ccu["captured_at"].nunique() >= 2:
        first_time = normalized_ccu["captured_at"].min()
        first_snapshot = normalized_ccu[normalized_ccu["captured_at"] == first_time][["appid", "current_players"]].rename(
            columns={"current_players": "baseline_players"}
        )
        merged = merged.merge(first_snapshot, on="appid", how="left")
        merged["delta_players"] = merged["current_players"] - merged["baseline_players"].fillna(merged["current_players"])
    else:
        merged["delta_players"] = 0
    merged["delta_label"] = merged["delta_players"].apply(lambda value: "Subindo" if value > 0 else "Caindo" if value < 0 else "Estavel")

    return merged.sort_values(["current_players", "utilization_pct"], ascending=[False, False]).reset_index(drop=True)


def generate_insights(games_df, ccu_df=None) -> list[dict[str, str]]:
    insights: list[dict[str, str]] = []

    if ccu_df is not None and not ccu_df.empty:
        hour_series = ccu_df.groupby("hour", dropna=True)["current_players"].mean().sort_values(ascending=False)
        if not hour_series.empty:
            best_hour = int(hour_series.index[0])
            insights.append(
                {
                    "title": "Hora de maior movimento",
                    "value": f"{best_hour:02d}:00",
                    "detail": f"Media de {hour_series.iloc[0]:,.0f} jogadores simultaneos entre os apps monitorados.",
                }
            )

        weekday_series = (
            ccu_df.groupby("weekday", dropna=True, observed=False)["current_players"]
            .mean()
            .reindex(WEEKDAY_ORDER)
            .dropna()
            .sort_values(ascending=False)
        )
        if not weekday_series.empty:
            insights.append(
                {
                    "title": "Dia da semana de maior movimento",
                    "value": str(weekday_series.index[0]),
                    "detail": f"Media de {weekday_series.iloc[0]:,.0f} jogadores por snapshot.",
                }
            )

        app_series = ccu_df.groupby("name", dropna=True)["current_players"].mean().sort_values(ascending=False)
        if not app_series.empty:
            insights.append(
                {
                    "title": "App com maior CCU medio monitorado",
                    "value": str(app_series.index[0]),
                    "detail": f"CCU medio de {app_series.iloc[0]:,.0f} jogadores no periodo coletado.",
                }
            )
    else:
        insights.extend(
            [
                _default_operational_insight("Hora de maior movimento"),
                _default_operational_insight("Dia da semana de maior movimento"),
                _default_operational_insight("App com maior CCU medio monitorado"),
            ]
        )

    popularity_base = games_df[games_df["peak_ccu"] > 0].copy()
    top_decile = popularity_base[popularity_base["peak_ccu"] >= popularity_base["peak_ccu"].quantile(0.9)]
    top_decile = top_decile if not top_decile.empty else popularity_base

    median_age = float(top_decile["game_age_years"].median()) if not top_decile.empty else 0.0
    insights.append(
        {
            "title": "Idade mediana do top 10% em popularidade",
            "value": f"{median_age:.1f} anos",
            "detail": "Usa Peak CCU para definir os jogos mais populares da base.",
        }
    )

    aaa_prices = games_df.loc[games_df["segment"] == "AAA", "price"]
    indie_prices = games_df.loc[games_df["segment"] == "Indie", "price"]
    aaa_median = float(aaa_prices.median()) if not aaa_prices.empty else 0.0
    indie_median = float(indie_prices.median()) if not indie_prices.empty else 0.0
    insights.append(
        {
            "title": "Diferenca de preco mediano AAA vs Indie",
            "value": f"${aaa_median - indie_median:,.2f}",
            "detail": f"AAA mediano em ${aaa_median:,.2f} e Indie mediano em ${indie_median:,.2f}.",
        }
    )

    free_share_top = float(top_decile["is_free"].mean() * 100) if not top_decile.empty else 0.0
    insights.append(
        {
            "title": "Participacao de jogos gratis no topo",
            "value": f"{free_share_top:.1f}%",
            "detail": "Percentual de jogos free-to-play dentro do top 10% por Peak CCU.",
        }
    )

    genre_stats = (
        games_df[games_df["primary_genre"] != "Unknown"]
        .groupby("primary_genre", dropna=True)
        .agg(owners_median=("owners_mid", "median"), games=("appid", "count"))
    )
    genre_owners = genre_stats[genre_stats["games"] >= 25].sort_values(["owners_median", "games"], ascending=[False, False])
    if genre_owners.empty:
        genre_owners = genre_stats.sort_values(["owners_median", "games"], ascending=[False, False])
    best_genre = _coerce_value(genre_owners.index[0] if not genre_owners.empty else None)
    best_genre_value = float(genre_owners.iloc[0]["owners_median"]) if not genre_owners.empty else 0.0
    insights.append(
        {
            "title": "Genero com maior owners mediano",
            "value": best_genre,
            "detail": f"Owners medianos em {best_genre_value:,.0f} usuarios estimados.",
        }
    )

    engagement_df = games_df[games_df["average_playtime_forever"] > 0]
    bucket_engagement = (
        engagement_df.groupby("price_bucket", dropna=True)["average_playtime_forever"]
        .median()
        .sort_values(ascending=False)
    )
    best_bucket = _coerce_value(bucket_engagement.index[0] if not bucket_engagement.empty else None)
    best_bucket_minutes = float(bucket_engagement.iloc[0]) if not bucket_engagement.empty else 0.0
    insights.append(
        {
            "title": "Faixa de preco com melhor engajamento",
            "value": best_bucket,
            "detail": f"Mediana de {best_bucket_minutes / 60.0:,.1f} horas de jogo acumuladas.",
        }
    )

    segment_reviews = (
        games_df[games_df["positive_ratio"].notna()]
        .groupby("segment", dropna=True)["positive_ratio"]
        .median()
        .sort_values(ascending=False)
    )
    best_segment = _coerce_value(segment_reviews.index[0] if not segment_reviews.empty else None)
    best_segment_ratio = float(segment_reviews.iloc[0] * 100) if not segment_reviews.empty else 0.0
    insights.append(
        {
            "title": "Segmento com melhor taxa de reviews positivas",
            "value": best_segment,
            "detail": f"Mediana de aprovacao em {best_segment_ratio:.1f}%.",
        }
    )

    correlation_df = games_df[(games_df["game_age_years"] >= 0) & (games_df["peak_ccu"] > 0)][
        ["game_age_years", "peak_ccu"]
    ].dropna()
    correlation = None
    if len(correlation_df) >= 3:
        ranked_age = correlation_df["game_age_years"].rank(method="average")
        ranked_peak = correlation_df["peak_ccu"].rank(method="average")
        correlation = float(ranked_age.corr(ranked_peak, method="pearson"))
    insights.append(
        {
            "title": "Leitura da relacao entre idade e popularidade",
            "value": f"{correlation:.2f}" if correlation is not None else "Sem dados",
            "detail": _describe_age_popularity_relation(correlation),
        }
    )

    return insights[:10]


def build_report_payload(games_df, ccu_df=None) -> dict[str, Any]:
    insights = generate_insights(games_df, ccu_df=ccu_df)
    strategy = build_strategy(games_df, ccu_df=ccu_df)
    operational_snapshot = build_operational_snapshot(games_df, ccu_df)

    top_opportunities = (
        games_df[
            games_df["positive_ratio"].notna()
            & (games_df["positive"] >= 50)
            & (games_df["owners_mid"] >= 20_000)
        ]
        .sort_values(["opportunity_score", "owners_mid"], ascending=[False, False])
        .head(10)[["name", "market_tier", "primary_genre", "price", "opportunity_score"]]
        .to_dict("records")
    )

    return {
        "insights": insights,
        "strategy": strategy,
        "operational_snapshot": operational_snapshot,
        "top_opportunities": top_opportunities,
    }


def build_strategy(games_df, ccu_df=None) -> dict[str, Any]:
    top_genre_stats = (
        games_df[games_df["primary_genre"] != "Unknown"]
        .groupby("primary_genre")["owners_mid"]
        .agg(["median", "count"])
    )
    top_genre_filtered = top_genre_stats[top_genre_stats["count"] >= 25].sort_values(["median", "count"], ascending=[False, False])
    if top_genre_filtered.empty:
        top_genre_filtered = top_genre_stats.sort_values(["median", "count"], ascending=[False, False])
    top_genre = str(top_genre_filtered.index[0]) if not top_genre_filtered.empty else "generos lideres"

    top_segment_series = games_df.groupby("segment")["peak_ccu"].median().sort_values(ascending=False)
    top_segment = str(top_segment_series.index[0]) if not top_segment_series.empty else "segmentos lideres"

    if ccu_df is not None and not ccu_df.empty:
        best_hour = int(ccu_df.groupby("hour")["current_players"].mean().sort_values(ascending=False).index[0])
        best_weekday = str(
            ccu_df.groupby("weekday", observed=False)["current_players"].mean().reindex(WEEKDAY_ORDER).dropna().sort_values(ascending=False).index[0]
        )
        operational_hint = f"Concentrar testes de campanha em {best_weekday} e no bloco de {best_hour:02d}:00."
    else:
        operational_hint = "Expandir a janela de coleta para consolidar padroes de horario e dia da semana."

    return {
        "summary": f"A base aponta vantagem competitiva em {top_genre} e boa tracao em {top_segment}. {operational_hint}",
        "three_months": [
            "Concluir a coleta de CCU para formar uma linha de base semanal.",
            "Priorizar benchmarking de preco e posicionamento entre AAA e Indie.",
            "Construir um calendario de acompanhamento dos generos com maior owners mediano.",
        ],
        "six_months": [
            "Criar alertas para movimentos de preco e mudancas de popularidade nos apps monitorados.",
            "Transformar os 10 insights em um rito mensal de recomendacao para clientes.",
            "Refinar segmentacao comercial por genero, preco e modelo free-to-play.",
        ],
        "one_year": [
            "Evoluir o dashboard para uma esteira continua de inteligencia competitiva.",
            "Adicionar mais fontes operacionais da Steam para detectar sinais de mercado mais cedo.",
            "Escalar a consultoria para comparativos por portfolio, publisher e janela de lancamento.",
        ],
        "demands": [
            "Melhorar a leitura de demanda por horario e dia da semana.",
            "Reduzir risco de posicionamento errado de preco.",
            "Aumentar precisao na escolha de generos e segmentos mais atrativos.",
        ],
        "tasks": [
            "Rodar a preparacao do CSV sempre que houver nova base.",
            "Executar o coletor em ciclos horarios durante o periodo de analise.",
            "Revisar semanalmente os graficos gerenciais e os insights do relatorio.",
        ],
        "priorities": [
            "Alta: manter a coleta operacional sem lacunas.",
            "Media: revisar comparativos de preco e owners por segmento.",
            "Baixa: ampliar novas fontes e automacoes de exportacao.",
        ],
        "risks": [
            "Amostra operacional curta pode distorcer leitura de horario e dia.",
            "Mudancas de catalogo e precificacao podem envelhecer o dataset bruto.",
            "Dependencia de endpoint externo pode gerar janelas sem snapshot.",
        ],
        "actions": [
            "Ajustar monitoramento recorrente dos titulos mais relevantes.",
            "Orientar estrategia comercial por faixa de preco e segmento.",
            "Usar os generos lideres como referencia de oportunidade de mercado.",
        ],
        "market_connection": (
            "O plano conecta desempenho operacional real com leitura de portfolio, "
            "permitindo transformar dados de popularidade, preco e owners em decisoes de mercado."
        ),
    }
