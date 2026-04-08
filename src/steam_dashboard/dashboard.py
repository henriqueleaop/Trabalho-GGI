from __future__ import annotations

from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from .data_utils import normalize_appid_frame
from .insights import WEEKDAY_ORDER, build_operational_snapshot, build_report_payload
from .paths import DEFAULT_CCU_HISTORY, DEFAULT_MONITOR_CANDIDATES, DEFAULT_PROCESSED_CSV, DEFAULT_PROCESSED_PARQUET


PALETTE = {
    "bg": "#f5efe4",
    "panel": "#fffaf2",
    "panel_alt": "#f1e8d8",
    "ink": "#18212f",
    "muted": "#526076",
    "border": "#d7c7ab",
    "accent": "#ca5c2c",
    "teal": "#145a64",
    "blue": "#1d4ed8",
    "slate": "#384357",
    "warn": "#8e2f22",
}
TIER_COLORS = {
    "Indie": "#145a64",
    "AAA Premium": "#ca5c2c",
    "Blockbuster F2P": "#1d4ed8",
    "Catalogo Geral": "#384357",
}
CHART_FONT = "Georgia, Cambria, 'Times New Roman', serif"
UI_FONT = "'Segoe UI Variable Text', 'Segoe UI', Tahoma, sans-serif"
FILTER_KEYS = ["segments_filter", "genres_filter", "price_filter", "year_filter", "peak_filter", "platform_filter"]

CARD_STYLE = f"""
<style>
    :root {{
        --bg: {PALETTE["bg"]};
        --panel: {PALETTE["panel"]};
        --panel-alt: {PALETTE["panel_alt"]};
        --ink: {PALETTE["ink"]};
        --muted: {PALETTE["muted"]};
        --border: {PALETTE["border"]};
        --accent: {PALETTE["accent"]};
        --warn: {PALETTE["warn"]};
    }}
    html, body, [class*="css"] {{
        color: var(--ink);
        font-family: {UI_FONT};
    }}
    .stApp {{
        background:
            radial-gradient(circle at 0% 0%, rgba(202, 92, 44, 0.18), transparent 30%),
            radial-gradient(circle at 100% 15%, rgba(20, 90, 100, 0.18), transparent 24%),
            linear-gradient(180deg, #f7f1e6 0%, #f5efe4 48%, #efe5d4 100%);
    }}
    h1, h2, h3, h4, h5, h6, p, label, span, div, li {{
        color: var(--ink);
    }}
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(255,250,242,0.98) 0%, rgba(241,232,216,0.96) 100%);
        border-right: 1px solid rgba(24, 33, 47, 0.08);
    }}
    section[data-testid="stSidebar"] * {{
        color: var(--ink) !important;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.6rem;
        background: rgba(255, 250, 242, 0.65);
        border: 1px solid rgba(24, 33, 47, 0.08);
        border-radius: 999px;
        padding: 0.35rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 999px;
        color: var(--muted) !important;
        font-weight: 600;
        padding: 0.55rem 1rem;
    }}
    .stTabs [aria-selected="true"] {{
        background: var(--ink) !important;
        color: #fff8ef !important;
    }}
    div[data-testid="stMetric"] {{
        background: linear-gradient(180deg, rgba(255,250,242,0.96) 0%, rgba(248,240,226,0.98) 100%);
        border: 1px solid rgba(24, 33, 47, 0.10);
        border-radius: 20px;
        padding: 1rem 1.05rem;
        box-shadow: 0 20px 42px rgba(24, 33, 47, 0.08);
    }}
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] [data-testid="stMetricValue"], div[data-testid="stMetric"] [data-testid="stMetricDelta"] {{
        color: var(--ink) !important;
    }}
    .hero-panel, .surface-card, .context-card, .signal-card, .timeline-card, .info-card, .insight-card {{
        border-radius: 22px;
        border: 1px solid rgba(24, 33, 47, 0.10);
        box-shadow: 0 18px 46px rgba(24, 33, 47, 0.07);
        padding: 1rem 1.1rem;
        margin-bottom: 0.9rem;
    }}
    .hero-panel {{
        background: linear-gradient(135deg, rgba(24,33,47,0.96) 0%, rgba(48,62,83,0.94) 56%, rgba(20,90,100,0.88) 100%);
        color: #fdf7ef !important;
        padding: 1.4rem 1.5rem;
        margin-bottom: 1rem;
    }}
    .hero-panel * {{ color: #fdf7ef !important; }}
    .surface-card, .signal-card, .info-card, .insight-card {{
        background: rgba(255, 250, 242, 0.92);
    }}
    .context-card {{
        background: linear-gradient(180deg, rgba(241,232,216,0.98) 0%, rgba(255,250,242,0.96) 100%);
    }}
    .signal-card {{ border-left: 5px solid var(--accent); }}
    .timeline-card {{
        background: linear-gradient(180deg, rgba(24,33,47,0.96) 0%, rgba(48,62,83,0.96) 100%);
        color: #fff8ef !important;
        min-height: 230px;
    }}
    .timeline-card * {{ color: #fff8ef !important; }}
    .insight-card .eyebrow {{
        color: var(--accent);
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 700;
    }}
    .insight-card .value {{
        font-family: {CHART_FONT};
        font-size: 1.55rem;
        font-weight: 700;
        color: var(--ink);
        margin: 0.2rem 0;
    }}
    .filter-chip {{
        display: inline-flex;
        align-items: center;
        background: rgba(255,250,242,0.90);
        border: 1px solid rgba(24,33,47,0.10);
        border-radius: 999px;
        padding: 0.4rem 0.75rem;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
        font-size: 0.86rem;
        color: var(--ink);
    }}
</style>
"""


@st.cache_data(show_spinner=False)
def load_games_data() -> pd.DataFrame:
    if DEFAULT_PROCESSED_PARQUET.exists():
        df = pd.read_parquet(DEFAULT_PROCESSED_PARQUET)
    elif DEFAULT_PROCESSED_CSV.exists():
        df = pd.read_csv(DEFAULT_PROCESSED_CSV, parse_dates=["release_date"])
    else:
        raise FileNotFoundError("Base processada nao encontrada.")
    return normalize_appid_frame(df)


@st.cache_data(show_spinner=False)
def load_ccu_history() -> pd.DataFrame:
    if not DEFAULT_CCU_HISTORY.exists():
        return pd.DataFrame()
    df = pd.read_csv(DEFAULT_CCU_HISTORY, parse_dates=["captured_at"])
    if df.empty:
        return df
    df = normalize_appid_frame(df)
    df["weekday"] = pd.Categorical(df["weekday"], categories=WEEKDAY_ORDER, ordered=True)
    return df


@st.cache_data(show_spinner=False)
def load_monitor_candidates() -> pd.DataFrame:
    if not DEFAULT_MONITOR_CANDIDATES.exists():
        return pd.DataFrame()
    return normalize_appid_frame(pd.read_csv(DEFAULT_MONITOR_CANDIDATES))


def format_currency(value: float) -> str:
    return f"${value:,.2f}"


def format_number(value: float | int) -> str:
    return f"{value:,.0f}"


def format_window(ccu_df: pd.DataFrame) -> str:
    if ccu_df.empty:
        return "Sem coleta operacional"
    return f"{ccu_df['captured_at'].min().strftime('%d/%m %H:%M')} -> {ccu_df['captured_at'].max().strftime('%d/%m %H:%M')}"


def get_operational_status(ccu_df: pd.DataFrame) -> str:
    if ccu_df.empty:
        return "Sem coleta"
    points = ccu_df["captured_at"].nunique()
    if points < 4:
        return "Leitura preliminar"
    if points < 12:
        return "Leitura inicial confiavel"
    return "Leitura consistente"


def inject_theme() -> None:
    st.markdown(CARD_STYLE, unsafe_allow_html=True)


def apply_chart_style(fig, *, height: int, xaxis_title: str | None = None, yaxis_title: str | None = None) -> None:
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,250,242,0.90)",
        font=dict(family=UI_FONT, color=PALETTE["ink"], size=13),
        title_font=dict(family=CHART_FONT, color=PALETTE["ink"], size=22),
        legend=dict(
            bgcolor="rgba(255,250,242,0.88)",
            bordercolor="rgba(24,33,47,0.08)",
            borderwidth=1,
            font=dict(color=PALETTE["ink"]),
        ),
        margin=dict(l=20, r=20, t=70, b=20),
        hoverlabel=dict(bgcolor="#fffaf2", bordercolor=PALETTE["border"], font=dict(color=PALETTE["ink"], family=UI_FONT)),
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(24,33,47,0.10)", linecolor="rgba(24,33,47,0.20)", tickfont=dict(color=PALETTE["ink"]), title_text=xaxis_title)
    fig.update_yaxes(showgrid=True, gridcolor="rgba(24,33,47,0.08)", linecolor="rgba(24,33,47,0.20)", tickfont=dict(color=PALETTE["ink"]), title_text=yaxis_title)


def render_chart_context(titulo: str, o_que_mostra: str, por_que_importa: str, como_ler: str, limitacao: str | None = None) -> None:
    lines = [
        f"<strong>{titulo}</strong>",
        f"<p><strong>O que mostra:</strong> {o_que_mostra}</p>",
        f"<p><strong>Por que importa:</strong> {por_que_importa}</p>",
        f"<p><strong>Como ler:</strong> {como_ler}</p>",
    ]
    if limitacao:
        lines.append(f"<p><strong>Limitacao:</strong> {limitacao}</p>")
    st.markdown(f"<div class='context-card'>{''.join(lines)}</div>", unsafe_allow_html=True)


def render_surface_card(title: str, body: str) -> None:
    st.markdown(f"<div class='surface-card'><strong>{title}</strong><p>{body}</p></div>", unsafe_allow_html=True)


def render_signal_card(title: str, body: str) -> None:
    st.markdown(f"<div class='signal-card'><strong>{title}</strong><p>{body}</p></div>", unsafe_allow_html=True)


def render_filter_chips(meta: dict[str, object]) -> None:
    labels = [
        f"Segmentos: {meta['segments_label']}",
        f"Generos: {meta['genres_label']}",
        f"Preco: {meta['price_label']}",
        f"Periodo: {meta['years_label']}",
        f"Peak CCU: {meta['peak_label']}",
        f"Plataforma: {meta['platform_label']}",
    ]
    st.markdown("".join(f"<span class='filter-chip'>{label}</span>" for label in labels), unsafe_allow_html=True)


def render_header(games_df: pd.DataFrame, ccu_df: pd.DataFrame) -> None:
    badges = [
        f"{len(games_df):,} jogos processados",
        f"{len(ccu_df):,} snapshots operacionais" if not ccu_df.empty else "Sem snapshots operacionais",
        f"Janela: {format_window(ccu_df)}",
        f"Status: {get_operational_status(ccu_df)}",
    ]
    badges_html = "".join(
        f"<span style='display:inline-flex;align-items:center;background:rgba(255,255,255,0.10);border:1px solid rgba(255,255,255,0.14);border-radius:999px;padding:0.4rem 0.7rem;margin-right:0.45rem;margin-bottom:0.45rem;font-size:0.88rem;'>{badge}</span>"
        for badge in badges
    )
    st.markdown(
        f"""
        <div class="hero-panel">
            <div style="color:#ffd9c7; text-transform:uppercase; letter-spacing:0.08em; font-size:0.82rem; font-weight:700;">Editorial Tech Dashboard</div>
            <h1 style="font-family:{CHART_FONT}; font-size:2.5rem; margin:0.12rem 0 0.45rem 0;">Steam Decision Dashboard</h1>
            <p style="font-size:1.05rem; max-width:920px; line-height:1.55;">
                Um painel desenhado para transformar catalogo, sinais operacionais e leitura estrategica em decisoes claras para o usuario final.
            </p>
            <div>{badges_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def reset_filters() -> None:
    for key in FILTER_KEYS:
        st.session_state.pop(key, None)
    st.rerun()


def build_sidebar_filters(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    st.sidebar.header("Recorte analitico")
    st.sidebar.caption("Refine o escopo do painel e acompanhe como isso muda a historia dos dados.")
    if st.sidebar.button("Resetar filtros", width="stretch"):
        reset_filters()

    segments = sorted(df["segment"].dropna().unique().tolist())
    selected_segments = st.sidebar.multiselect("Segmentos", segments, default=segments, key="segments_filter")
    genres = sorted(df["primary_genre"].dropna().unique().tolist())
    selected_genres = st.sidebar.multiselect("Generos", genres, default=genres, key="genres_filter")
    price_buckets = df["price_bucket"].dropna().unique().tolist()
    selected_buckets = st.sidebar.multiselect("Faixas de preco", price_buckets, default=price_buckets, key="price_filter")
    years = df["release_year"].dropna().astype(int)
    min_year, max_year = int(years.min()), int(years.max())
    selected_years = st.sidebar.slider("Periodo de lancamento", min_year, max_year, (min_year, max_year), key="year_filter")
    peak_threshold = st.sidebar.selectbox("Corte minimo de Peak CCU", [0, 100, 1_000, 10_000, 100_000], index=0, key="peak_filter")
    platform_filter = st.sidebar.selectbox("Plataforma", ["Todas", "Windows", "Mac", "Linux"], index=0, key="platform_filter")

    filtered = df[
        df["segment"].isin(selected_segments)
        & df["primary_genre"].isin(selected_genres)
        & df["price_bucket"].isin(selected_buckets)
        & df["release_year"].between(selected_years[0], selected_years[1])
        & (df["peak_ccu"] >= peak_threshold)
    ].copy()
    if platform_filter != "Todas":
        filtered = filtered[filtered[platform_filter.casefold()]]

    meta = {
        "segments_label": "todos" if len(selected_segments) == len(segments) else f"{len(selected_segments)} selecionados",
        "genres_label": "todos" if len(selected_genres) == len(genres) else f"{len(selected_genres)} selecionados",
        "price_label": "todas" if len(selected_buckets) == len(price_buckets) else ", ".join(selected_buckets[:2]) + ("..." if len(selected_buckets) > 2 else ""),
        "years_label": f"{selected_years[0]} a {selected_years[1]}",
        "peak_label": format_number(peak_threshold),
        "platform_label": platform_filter,
    }
    st.sidebar.caption(f"Jogos no recorte: {len(filtered):,}")
    return filtered, meta


def render_kpis(df: pd.DataFrame) -> None:
    owners_median = float(df["owners_mid"].median()) if not df.empty else 0.0
    price_median = float(df["price"].median()) if not df.empty else 0.0
    free_share = float(df["is_free"].mean() * 100) if not df.empty else 0.0
    age_median = float(df["game_age_years"].median()) if not df.empty else 0.0
    opportunity_median = float(df["opportunity_score"].median()) if not df.empty else 0.0

    metrics = st.columns(5)
    metrics[0].metric("Jogos no recorte", f"{len(df):,}")
    metrics[1].metric("Preco mediano", format_currency(price_median))
    metrics[2].metric("Owners medianos", format_number(owners_median))
    metrics[3].metric("Participacao gratis", f"{free_share:.1f}%")
    metrics[4].metric("Indicador mediano", f"{opportunity_median:.1f}", delta=f"Idade mediana {age_median:.1f} anos")


def render_summary_tab(df: pd.DataFrame, meta: dict[str, object], ccu_df: pd.DataFrame) -> None:
    render_filter_chips(meta)
    render_signal_card(
        "Como usar esta aba",
        "Comece pelos indicadores, valide o recorte ativo e depois leia os graficos como uma historia: composicao do catalogo, tiers de mercado, modelo de preco, evolucao temporal e potencial comercial.",
    )
    render_kpis(df)

    summary_cols = st.columns(3)
    summary_cols[0].markdown(
        f"<div class='info-card'><strong>Tier dominante</strong><p>{df['market_tier'].mode().iloc[0]}</p></div>",
        unsafe_allow_html=True,
    )
    summary_cols[1].markdown(
        f"<div class='info-card'><strong>Janela operacional</strong><p>{format_window(ccu_df)}</p></div>",
        unsafe_allow_html=True,
    )
    summary_cols[2].markdown(
        f"<div class='info-card'><strong>Leitura de dados</strong><p>{get_operational_status(ccu_df)}</p></div>",
        unsafe_allow_html=True,
    )

    render_chart_context(
        "Distribuicao dos generos mais presentes",
        "Mostra quais generos ocupam mais espaco dentro do recorte ativo.",
        "Ajuda a entender se voce esta olhando para um portfolio concentrado ou pulverizado.",
        "Barras maiores indicam maior presenca de jogos daquele genero no recorte selecionado.",
    )
    genre_counts = (
        df[df["primary_genre"] != "Unknown"]["primary_genre"]
        .value_counts()
        .head(12)
        .sort_values(ascending=True)
    )
    fig_genres = px.bar(
        genre_counts,
        x=genre_counts.values,
        y=genre_counts.index,
        orientation="h",
        title="Distribuicao dos generos mais presentes no recorte",
        labels={"x": "Quantidade de jogos", "y": "Genero"},
        color=genre_counts.values,
        color_continuous_scale=["#e6d8bd", "#ca5c2c"],
    )
    fig_genres.update_layout(coloraxis_showscale=False)
    apply_chart_style(fig_genres, height=450, xaxis_title="Quantidade de jogos", yaxis_title="Genero")
    st.plotly_chart(fig_genres, width="stretch")

    col_a, col_b = st.columns(2)
    with col_a:
        render_chart_context(
            "Owners medianos por tier de mercado",
            "Compara a mediana de owners entre os grupos de mercado do painel.",
            "Ajuda a perceber onde a base enxerga massa de usuarios: premium, indie, F2P ou catalogo geral.",
            "Quanto maior a barra, maior a base tipica de owners daquele tier.",
        )
        segment_owners = (
            df.groupby("market_tier", dropna=True)["owners_mid"]
            .median()
            .sort_values(ascending=False)
            .reset_index()
        )
        fig_segment = px.bar(
            segment_owners,
            x="market_tier",
            y="owners_mid",
            title="Owners medianos por tier de mercado",
            color="market_tier",
            color_discrete_map=TIER_COLORS,
        )
        fig_segment.update_layout(showlegend=False)
        apply_chart_style(fig_segment, height=420, xaxis_title="Tier de mercado", yaxis_title="Owners medianos")
        st.plotly_chart(fig_segment, width="stretch")

    with col_b:
        render_chart_context(
            "Participacao de owners por modelo de preco",
            "Divide o recorte entre jogos gratis e pagos usando a mediana de owners.",
            "Mostra se o publico tende a se concentrar mais em produtos free-to-play ou premium.",
            "A fatia maior representa o modelo de preco com maior base tipica de owners.",
        )
        free_paid = (
            df.assign(price_model=df["is_free"].map({True: "Free-to-play", False: "Pago"}))
            .groupby("price_model", dropna=True)["owners_mid"]
            .median()
            .reset_index()
        )
        fig_free_paid = px.pie(
            free_paid,
            names="price_model",
            values="owners_mid",
            title="Participacao de owners por modelo de preco",
            hole=0.58,
            color="price_model",
            color_discrete_map={"Free-to-play": TIER_COLORS["Blockbuster F2P"], "Pago": TIER_COLORS["AAA Premium"]},
        )
        fig_free_paid.update_traces(textfont=dict(color=PALETTE["ink"]))
        apply_chart_style(fig_free_paid, height=420)
        st.plotly_chart(fig_free_paid, width="stretch")

    col_c, col_d = st.columns(2)
    with col_c:
        render_chart_context(
            "Peak CCU medio por ano de lancamento",
            "Plota a media de Peak CCU dos jogos agrupados pelo ano de lancamento.",
            "Ajuda a ver se jogos mais recentes entram em um mercado mais forte ou mais fragmentado.",
            "Picos mais altos em certos anos sugerem janelas de lancamento com maior concentracao de hits.",
        )
        yearly = (
            df.groupby("release_year", dropna=True)
            .agg(jogos=("appid", "count"), peak_medio=("peak_ccu", "mean"))
            .reset_index()
        )
        fig_year = px.line(
            yearly,
            x="release_year",
            y="peak_medio",
            markers=True,
            title="Peak CCU medio por ano de lancamento",
        )
        fig_year.update_traces(line=dict(color=PALETTE["teal"], width=3), marker=dict(size=8, color=PALETTE["accent"]))
        apply_chart_style(fig_year, height=400, xaxis_title="Ano", yaxis_title="Peak CCU medio")
        st.plotly_chart(fig_year, width="stretch")

    with col_d:
        render_chart_context(
            "Jogos com maior potencial comercial no recorte",
            "Ordena os jogos pelo indicador composto de oportunidade, que considera owners, reviews, engajamento e acessibilidade de preco.",
            "Ajuda o usuario final a localizar rapidamente produtos com boa relacao entre alcance, aprovacao e atratividade comercial.",
            "Barras maiores indicam maior potencial relativo dentro do recorte atual.",
            "Esse indicador e heuristico; ele apoia leitura comercial, nao substitui validacao manual.",
        )
        opportunity_df = (
            df[df["positive_ratio"].notna()]
            .sort_values(["opportunity_score", "owners_mid"], ascending=[False, False])
            .head(15)
            .sort_values("opportunity_score", ascending=True)
        )
        fig_opportunity = px.bar(
            opportunity_df,
            x="opportunity_score",
            y="name",
            orientation="h",
            color="market_tier",
            title="Jogos com maior potencial comercial no recorte",
            hover_data={"primary_genre": True, "price": ":.2f", "owners_mid": ":,.0f"},
            color_discrete_map=TIER_COLORS,
        )
        apply_chart_style(fig_opportunity, height=470, xaxis_title="Indicador composto de oportunidade", yaxis_title="Jogo")
        st.plotly_chart(fig_opportunity, width="stretch")


def render_operational_tab(filtered_games: pd.DataFrame, ccu_df: pd.DataFrame, monitor_candidates: pd.DataFrame, meta: dict[str, object]) -> None:
    render_filter_chips(meta)
    if ccu_df.empty:
        render_signal_card(
            "Ainda nao existe historico operacional suficiente",
            "O painel gerencial continua funcional, mas a aba operacional depende de snapshots do coletor. Gere alguns pontos para liberar leitura de horario, dia da semana, variacao e utilizacao frente ao pico historico.",
        )
        st.code(r".\.venv\Scripts\python scripts/collect_ccu.py --mode demo --iterations 4 --interval-seconds 2", language="powershell")
        if not monitor_candidates.empty:
            render_surface_card("Apps monitorados", "Estes sao os jogos que o coletor acompanha para montar a leitura operacional.")
            st.dataframe(monitor_candidates.head(20), width="stretch", hide_index=True)
        return

    scoped = normalize_appid_frame(ccu_df)
    filtered_reference = normalize_appid_frame(filtered_games)
    scoped = scoped[scoped["appid"].isin(filtered_reference["appid"])]
    if scoped.empty:
        render_signal_card(
            "O recorte ativo removeu todos os apps monitorados",
            "Ajuste o recorte ou resete os filtros para voltar a enxergar a camada operacional.",
        )
        return

    points = scoped["captured_at"].nunique()
    render_signal_card(
        "Leitura operacional",
        f"A aba esta analisando {len(scoped):,} snapshots de {scoped['appid'].nunique()} apps em {points} momentos distintos. Estado atual: {get_operational_status(scoped)}.",
    )

    total_series = scoped.groupby("captured_at", dropna=True)["current_players"].sum().reset_index()
    render_chart_context(
        "Jogadores simultaneos totais monitorados",
        "Soma os jogadores atuais dos apps monitorados em cada momento de coleta.",
        "Mostra se o conjunto observado esta esfriando, estabilizando ou acelerando ao longo do tempo.",
        "Subidas indicam aquecimento do ecossistema monitorado; quedas indicam perda de tracao no curto prazo.",
        "Com poucos snapshots, a curva ainda e mais diagnostica do que conclusiva.",
    )
    fig_line = px.line(
        total_series,
        x="captured_at",
        y="current_players",
        markers=True,
        title="Jogadores simultaneos totais no monitoramento",
    )
    fig_line.update_traces(line=dict(color=PALETTE["accent"], width=3), marker=dict(size=8, color=PALETTE["ink"]))
    apply_chart_style(fig_line, height=380, xaxis_title="Momento da coleta", yaxis_title="Jogadores simultaneos")
    st.plotly_chart(fig_line, width="stretch")

    col_a, col_b = st.columns(2)
    with col_a:
        render_chart_context(
            "Heatmap medio por dia e hora",
            "Agrupa a media de jogadores por dia da semana e hora do dia.",
            "Ajuda a detectar janelas operacionais melhores para campanha, comparacao e comunicacao.",
            "Cores mais intensas apontam faixas de maior volume medio no monitoramento.",
            "Se a coleta estiver concentrada em poucas horas ou poucos dias, use o grafico como indicio inicial.",
        )
        heatmap_df = (
            scoped.groupby(["weekday", "hour"], observed=True)["current_players"]
            .mean()
            .reset_index()
            .pivot(index="weekday", columns="hour", values="current_players")
            .reindex(WEEKDAY_ORDER)
        )
        fig_heatmap = go.Figure(
            data=go.Heatmap(
                z=heatmap_df.values,
                x=[f"{int(hour):02d}:00" for hour in heatmap_df.columns],
                y=heatmap_df.index.tolist(),
                colorscale=[[0, "#f0dcc5"], [0.45, "#d87b42"], [1, "#8e2f22"]],
                hovertemplate="Dia=%{y}<br>Hora=%{x}<br>Media=%{z:.0f}<extra></extra>",
                colorbar=dict(title="Media"),
            )
        )
        apply_chart_style(fig_heatmap, height=430, xaxis_title="Hora", yaxis_title="Dia")
        st.plotly_chart(fig_heatmap, width="stretch")

    with col_b:
        first_time = scoped["captured_at"].min()
        latest_time = scoped["captured_at"].max()
        first_snapshot = scoped[scoped["captured_at"] == first_time][["appid", "current_players"]].rename(columns={"current_players": "baseline_players"})
        latest_snapshot = scoped[scoped["captured_at"] == latest_time][["appid", "name", "current_players"]]
        ranking = latest_snapshot.merge(first_snapshot, on="appid", how="left")
        ranking["delta_players"] = ranking["current_players"] - ranking["baseline_players"].fillna(ranking["current_players"])
        render_chart_context(
            "Ranking atual com variacao desde o primeiro snapshot",
            "Ordena os apps pelo volume atual e colore a variacao desde o inicio da janela observada.",
            "Ajuda a ver quem lidera agora e quem esta acelerando ou perdendo tracao.",
            "Barras mais quentes e deltas positivos indicam crescimento no recorte de coleta.",
        )
        fig_rank = px.bar(
            ranking.sort_values("current_players", ascending=False).head(15).sort_values("current_players", ascending=True),
            x="current_players",
            y="name",
            orientation="h",
            color="delta_players",
            title="Apps com maior volume atual e variacao recente",
            color_continuous_scale=["#8e2f22", "#f0dcc5", "#145a64"],
            hover_data={"delta_players": ":,.0f"},
        )
        apply_chart_style(fig_rank, height=430, xaxis_title="Jogadores atuais", yaxis_title="Jogo")
        st.plotly_chart(fig_rank, width="stretch")

    operational_snapshot = build_operational_snapshot(filtered_reference, scoped)
    if operational_snapshot is None or operational_snapshot.empty:
        render_signal_card("Snapshot indisponivel", "Nao foi possivel consolidar a leitura operacional do ultimo momento de coleta.")
        return

    above_peak = operational_snapshot[operational_snapshot["utilization_pct"] > 100]
    if not above_peak.empty:
        render_signal_card(
            "Pico atual acima do historico da base",
            f"{len(above_peak)} jogo(s) estao acima de 100% do pico historico registrado no dataset bruto. Isso sugere base desatualizada para esses titulos, nao erro do coletor.",
        )

    render_chart_context(
        "CCU atual versus pico historico da base",
        "Compara o volume atual de jogadores com o maior pico registrado no dataset processado.",
        "Ajuda o usuario final a entender o quanto cada jogo esta perto do proprio teto historico conhecido.",
        "Barras maiores indicam jogos mais proximos do pico; valores acima de 100% sugerem que o dataset historico ficou defasado.",
    )
    fig_utilization = px.bar(
        operational_snapshot.head(15).sort_values("utilization_pct", ascending=True),
        x="utilization_pct",
        y="name",
        orientation="h",
        color="market_tier",
        title="CCU atual versus pico historico da base",
        hover_data={"current_players": ":,.0f", "peak_ccu": ":,.0f", "peak_status": True},
        color_discrete_map=TIER_COLORS,
    )
    apply_chart_style(fig_utilization, height=430, xaxis_title="% do pico historico", yaxis_title="Jogo")
    st.plotly_chart(fig_utilization, width="stretch")

    render_surface_card(
        "Ultimo snapshot consolidado",
        "Tabela de apoio para leitura operacional imediata, incluindo volume atual, pico historico, utilizacao percentual e interpretacao do status do pico.",
    )
    st.dataframe(
        operational_snapshot[
            ["captured_at", "name", "current_players", "peak_ccu", "utilization_pct", "delta_players", "delta_label", "peak_status", "market_tier"]
        ],
        width="stretch",
        hide_index=True,
    )


def render_managerial_tab(df: pd.DataFrame, meta: dict[str, object]) -> None:
    render_filter_chips(meta)
    render_signal_card(
        "Como ler esta aba",
        "A sequencia abaixo foi montada para responder quatro perguntas: quao maduros sao os hits do recorte, como preco se relaciona com popularidade, quais generos se sustentam melhor e onde o engajamento tende a ficar.",
    )

    top_popularity = df[df["peak_ccu"] > 0].copy()
    cutoff = top_popularity["peak_ccu"].quantile(0.9) if not top_popularity.empty else 0
    top_popularity = top_popularity[top_popularity["peak_ccu"] >= cutoff]

    col_a, col_b = st.columns(2)
    with col_a:
        render_chart_context(
            "Idade dos jogos mais jogados",
            "Distribui a idade dos jogos que estao no topo de popularidade do recorte.",
            "Ajuda a entender se o mercado analisado se apoia em catalogo consolidado ou em hits recentes.",
            "Concentracao em idades baixas sugere renovacao rapida; concentracao em idades altas sugere cauda longa forte.",
        )
        fig_age = px.histogram(
            top_popularity,
            x="game_age_years",
            nbins=24,
            color="segment",
            title="Idade dos jogos mais jogados",
            color_discrete_map={"Indie": TIER_COLORS["Indie"], "AAA": TIER_COLORS["AAA Premium"], "Other": TIER_COLORS["Catalogo Geral"]},
        )
        apply_chart_style(fig_age, height=430, xaxis_title="Idade do jogo (anos)", yaxis_title="Quantidade")
        st.plotly_chart(fig_age, width="stretch")

    with col_b:
        render_chart_context(
            "Preco AAA versus Indie",
            "Compara a distribuicao de preco dos dois segmentos com maior contraste comercial.",
            "Ajuda a ver se o recorte reforca a distancia de posicionamento entre premium e independente.",
            "A caixa mostra mediana, dispersao e extremos de cada segmento.",
        )
        aaa_vs_indie = df[df["segment"].isin(["AAA", "Indie"])]
        fig_price = px.box(
            aaa_vs_indie,
            x="segment",
            y="price",
            color="segment",
            title="Preco AAA versus Indie",
            color_discrete_map={"Indie": TIER_COLORS["Indie"], "AAA": TIER_COLORS["AAA Premium"]},
        )
        apply_chart_style(fig_price, height=430, xaxis_title="Segmento", yaxis_title="Preco")
        st.plotly_chart(fig_price, width="stretch")

    col_c, col_d = st.columns(2)
    with col_c:
        render_chart_context(
            "Preco versus popularidade",
            "Cruza preco, pico de jogadores e base estimada de owners em um unico grafico.",
            "Ajuda a entender se o mercado recompensa preco alto, baixo ou modelos gratis quando o assunto e popularidade.",
            "Cada bolha e um jogo; quanto maior a bolha, maior a base estimada de owners.",
            "O eixo Y esta em escala logaritmica para acomodar grandes diferencas entre jogos pequenos e blockbusters.",
        )
        scatter_df = df[(df["price"] >= 0) & (df["peak_ccu"] > 0)].copy()
        scatter_df["owners_bubble"] = scatter_df["owners_mid"].fillna(0).clip(lower=1)
        fig_scatter = px.scatter(
            scatter_df.head(6000),
            x="price",
            y="peak_ccu",
            size="owners_bubble",
            color="market_tier",
            hover_name="name",
            title="Preco versus popularidade",
            log_y=True,
            color_discrete_map=TIER_COLORS,
        )
        apply_chart_style(fig_scatter, height=450, xaxis_title="Preco", yaxis_title="Peak CCU (escala log)")
        st.plotly_chart(fig_scatter, width="stretch")

    with col_d:
        render_chart_context(
            "Generos com maior owners mediano",
            "Mostra os generos que sustentam maior base tipica de owners, junto da taxa mediana de aprovacao.",
            "Ajuda a identificar combinacoes mais fortes entre alcance e satisfacao do mercado.",
            "Quanto maior a barra, maior a mediana de owners; a cor indica a aprovacao mediana.",
        )
        genre_strength = (
            df[df["primary_genre"] != "Unknown"]
            .groupby("primary_genre", dropna=True)
            .agg(owners_medianos=("owners_mid", "median"), aprovacao=("positive_ratio", "median"))
            .sort_values("owners_medianos", ascending=False)
            .head(12)
            .sort_values("owners_medianos", ascending=True)
        )
        fig_genre_strength = px.bar(
            genre_strength,
            x="owners_medianos",
            y=genre_strength.index,
            orientation="h",
            color="aprovacao",
            title="Generos com maior owners mediano",
            color_continuous_scale=["#f0dcc5", "#ca5c2c", "#145a64"],
        )
        apply_chart_style(fig_genre_strength, height=450, xaxis_title="Owners medianos", yaxis_title="Genero")
        st.plotly_chart(fig_genre_strength, width="stretch")

    render_chart_context(
        "Engajamento por faixa de preco",
        "Compara o playtime mediano entre as faixas de preco do recorte.",
        "Ajuda a ver se o engajamento tipico cresce com premiumizacao ou se se concentra em faixas acessiveis.",
        "Barras maiores indicam mais horas medianas acumuladas pelos jogos daquela faixa.",
    )
    price_engagement = (
        df[df["average_playtime_forever"] > 0]
        .groupby("price_bucket", dropna=True)["average_playtime_forever"]
        .median()
        .reset_index()
    )
    fig_engagement = px.bar(
        price_engagement,
        x="price_bucket",
        y="average_playtime_forever",
        color="average_playtime_forever",
        color_continuous_scale=["#f0dcc5", "#ca5c2c"],
        title="Engajamento mediano por faixa de preco",
    )
    apply_chart_style(fig_engagement, height=380, xaxis_title="Faixa de preco", yaxis_title="Playtime mediano (min)")
    st.plotly_chart(fig_engagement, width="stretch")


def render_insight_cards(insights: list[dict[str, str]]) -> None:
    left_column, right_column = st.columns(2)
    for index, insight in enumerate(insights):
        target_column = left_column if index % 2 == 0 else right_column
        target_column.markdown(
            f"""
            <div class="insight-card">
                <div class="eyebrow">Insight acionavel</div>
                <div style="font-weight:700; font-size:1rem;">{insight['title']}</div>
                <div class="value">{insight['value']}</div>
                <div>{insight['detail']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_strategy_tab(df: pd.DataFrame, ccu_df: pd.DataFrame, meta: dict[str, object]) -> None:
    render_filter_chips(meta)
    payload = build_report_payload(df, ccu_df=ccu_df if not ccu_df.empty else None)
    insights = payload["insights"]
    strategy = payload["strategy"]
    opportunities = payload["top_opportunities"]

    render_signal_card(
        "Como ler esta aba",
        "Aqui o painel deixa de apenas descrever dados e passa a apontar implicacoes. Os insights resumem sinais, e o plano de 3, 6 e 12 meses converte esses sinais em movimentos concretos.",
    )
    render_surface_card("Sintese executiva", strategy["summary"])
    st.subheader("10 informacoes gerenciais")
    render_insight_cards(insights)

    if opportunities:
        render_surface_card(
            "Top oportunidades do recorte",
            "Lista curta de jogos com melhor equilibrio entre alcance, aprovacao, engajamento e acessibilidade comercial dentro do recorte atual.",
        )
        st.dataframe(pd.DataFrame(opportunities), width="stretch", hide_index=True)

    st.subheader("Plano estrategico 3, 6 e 12 meses")
    col_a, col_b, col_c = st.columns(3)
    timelines = [
        ("3 meses", strategy["three_months"]),
        ("6 meses", strategy["six_months"]),
        ("1 ano", strategy["one_year"]),
    ]
    for column, (title, items) in zip((col_a, col_b, col_c), timelines, strict=False):
        items_html = "".join(f"<li>{item}</li>" for item in items)
        column.markdown(
            f"""
            <div class="timeline-card">
                <strong style="font-size:1.15rem;">{title}</strong>
                <ul>{items_html}</ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("Demandas, tarefas e riscos")
    grid_a, grid_b = st.columns(2)
    with grid_a:
        st.markdown("<div class='surface-card'><strong>Demandas</strong><ul>" + "".join(f"<li>{item}</li>" for item in strategy["demands"]) + "</ul></div>", unsafe_allow_html=True)
        st.markdown("<div class='surface-card'><strong>Tarefas</strong><ul>" + "".join(f"<li>{item}</li>" for item in strategy["tasks"]) + "</ul></div>", unsafe_allow_html=True)
        st.markdown("<div class='surface-card'><strong>Prioridades</strong><ul>" + "".join(f"<li>{item}</li>" for item in strategy["priorities"]) + "</ul></div>", unsafe_allow_html=True)
    with grid_b:
        st.markdown("<div class='surface-card'><strong>Riscos</strong><ul>" + "".join(f"<li>{item}</li>" for item in strategy["risks"]) + "</ul></div>", unsafe_allow_html=True)
        st.markdown("<div class='surface-card'><strong>Acoes estrategicas</strong><ul>" + "".join(f"<li>{item}</li>" for item in strategy["actions"]) + "</ul></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='surface-card'><strong>Conexao com o mercado</strong><p>{strategy['market_connection']}</p></div>", unsafe_allow_html=True)


def run_app() -> None:
    st.set_page_config(page_title="Steam Decision Dashboard", layout="wide")
    inject_theme()

    try:
        games_df = load_games_data()
    except FileNotFoundError:
        st.error("Base processada nao encontrada. Rode `python scripts/prepare_dataset.py --input \"D:/Downloads/Copy of games.csv\"` antes de abrir o dashboard.")
        st.stop()

    ccu_df = load_ccu_history()
    monitor_candidates = load_monitor_candidates()
    render_header(games_df, ccu_df)
    filtered_df, filter_meta = build_sidebar_filters(games_df)

    if filtered_df.empty:
        render_signal_card("Nenhum jogo encontrado para o recorte atual", "Ajuste ou resete os filtros para voltar a visualizar os graficos.")
        st.stop()

    tabs = st.tabs(["Resumo", "Operacional", "Gerencial", "Estrategico e Relatorio"])
    with tabs[0]:
        render_summary_tab(filtered_df, filter_meta, ccu_df)
    with tabs[1]:
        render_operational_tab(filtered_df, ccu_df, monitor_candidates, filter_meta)
    with tabs[2]:
        render_managerial_tab(filtered_df, filter_meta)
    with tabs[3]:
        render_strategy_tab(filtered_df, ccu_df, filter_meta)

