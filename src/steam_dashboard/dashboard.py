from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from .academic import (
    SHIFT_ORDER,
    SOURCE_OPTIONS,
    build_academic_insights,
    build_methodology_note,
    build_market_anchors,
    build_sales_calendar_table,
    build_strategy_payload,
    load_academic_sources,
)
from .insights import WEEKDAY_ORDER
from .paths import DEFAULT_PROCESSED_CSV, DEFAULT_PROCESSED_PARQUET
from .reporting import build_pdf_report, build_report_context


PALETTE = {
    "bg": "#f3ede4",
    "panel": "#fffdf9",
    "panel_alt": "#f6efe2",
    "surface": "#fffaf3",
    "surface_alt": "#f2e7d6",
    "ink": "#16202c",
    "text_secondary": "#49576b",
    "text_soft": "#6a788b",
    "text_inverse": "#fff9f1",
    "border": "#d5c2ab",
    "accent": "#bb582b",
    "teal": "#125b67",
    "blue": "#2456d3",
    "gold": "#aa7a28",
    "success": "#25664c",
    "warn": "#8a2f23",
}
UI_FONT = "'Segoe UI Variable Text', 'Segoe UI', Tahoma, sans-serif"
DISPLAY_FONT = "Georgia, Cambria, 'Times New Roman', serif"
FILTER_KEYS = ["source_mode", "segment_filter", "genre_filter", "price_filter", "platform_filter"]

THEME = f"""
<style>
    :root {{
        --bg: {PALETTE["bg"]};
        --panel: {PALETTE["panel"]};
        --panel-alt: {PALETTE["panel_alt"]};
        --surface: {PALETTE["surface"]};
        --surface-alt: {PALETTE["surface_alt"]};
        --text-primary: {PALETTE["ink"]};
        --text-secondary: {PALETTE["text_secondary"]};
        --text-soft: {PALETTE["text_soft"]};
        --text-inverse: {PALETTE["text_inverse"]};
        --border: {PALETTE["border"]};
        --accent: {PALETTE["accent"]};
        --teal: {PALETTE["teal"]};
        --blue: {PALETTE["blue"]};
        --gold: {PALETTE["gold"]};
        --success: {PALETTE["success"]};
        --warn: {PALETTE["warn"]};
    }}
    html, body, [class*="css"] {{
        color: var(--text-primary);
        font-family: {UI_FONT};
    }}
    .stApp {{
        background:
            radial-gradient(circle at 12% 0%, rgba(187,88,43,0.10), transparent 28%),
            radial-gradient(circle at 100% 8%, rgba(18,91,103,0.10), transparent 24%),
            linear-gradient(180deg, #faf5ee 0%, #f3ede4 52%, #eadfce 100%);
    }}
    .stApp, .stApp p, .stApp li, .stApp label, .stApp span, .stApp div {{
        color: var(--text-primary);
    }}
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(255,253,249,0.98) 0%, rgba(246,239,226,0.99) 100%);
        border-right: 1px solid rgba(22,32,44,0.10);
    }}
    section[data-testid="stSidebar"] * {{
        color: var(--text-primary) !important;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
        background: rgba(255,253,249,0.78);
        border: 1px solid rgba(22,32,44,0.08);
        border-radius: 999px;
        padding: 0.35rem;
        margin-bottom: 0.9rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 999px;
        color: var(--text-secondary) !important;
        font-weight: 700;
        padding: 0.62rem 1rem;
    }}
    .stTabs [data-baseweb="tab"] *, .stTabs [data-baseweb="tab"] p, .stTabs [data-baseweb="tab"] span, .stTabs [data-baseweb="tab"] div {{
        color: var(--text-secondary) !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: var(--text-primary) !important;
        color: var(--text-inverse) !important;
        box-shadow: inset 0 -2px 0 rgba(255,255,255,0.04);
    }}
    .stTabs [aria-selected="true"] *,
    .stTabs [aria-selected="true"] p,
    .stTabs [aria-selected="true"] span,
    .stTabs [aria-selected="true"] div,
    .stTabs [aria-selected="true"] button {{
        color: var(--text-inverse) !important;
        fill: var(--text-inverse) !important;
    }}
    .block-card, .hero-panel, .surface-card, .signal-card, .context-card, .metric-card, .insight-card, .timeline-card, .side-card {{
        border-radius: 24px;
        padding: 1.05rem 1.15rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(22,32,44,0.09);
        box-shadow: 0 14px 36px rgba(22,32,44,0.06);
    }}
    .hero-panel {{
        background: linear-gradient(135deg, rgba(23,32,43,0.96) 0%, rgba(44,57,77,0.96) 52%, rgba(21,93,104,0.90) 100%);
        color: var(--text-inverse) !important;
        padding: 1.2rem 1.3rem;
    }}
    .hero-panel * {{
        color: var(--text-inverse) !important;
    }}
    .surface-card, .signal-card, .context-card, .metric-card, .insight-card, .side-card {{
        background: linear-gradient(180deg, rgba(255,250,243,0.98) 0%, rgba(250,245,236,0.96) 100%);
    }}
    .surface-card, .surface-card *,
    .signal-card, .signal-card *,
    .context-card, .context-card *,
    .metric-card, .metric-card *,
    .insight-card, .insight-card *,
    .side-card, .side-card * {{
        color: var(--text-primary) !important;
    }}
    .signal-card {{
        border-left: 5px solid var(--accent);
    }}
    .context-card {{
        background: linear-gradient(180deg, rgba(242,231,214,0.98) 0%, rgba(255,250,243,0.98) 100%);
    }}
    .side-card {{
        padding: 0.9rem 0.95rem;
        box-shadow: 0 10px 24px rgba(22,32,44,0.05);
    }}
    .card-kicker {{
        color: var(--accent) !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-size: 0.77rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
    }}
    .card-title {{
        color: var(--text-primary) !important;
        font-size: 1.05rem;
        font-weight: 800;
        line-height: 1.32;
        margin-bottom: 0.35rem;
    }}
    .card-subtitle {{
        color: var(--text-secondary) !important;
        font-size: 0.94rem;
        line-height: 1.55;
        max-width: 72ch;
        margin-bottom: 0.1rem;
    }}
    .card-body {{
        color: var(--text-secondary) !important;
        font-size: 0.95rem;
        line-height: 1.6;
        max-width: 72ch;
        margin: 0.18rem 0;
    }}
    .card-body strong {{
        color: var(--text-primary) !important;
        font-weight: 700;
    }}
    .card-list, .card-list li {{
        color: var(--text-secondary) !important;
        line-height: 1.55;
    }}
    .phase-section {{
        margin-bottom: 1.4rem;
    }}
    .metric-card .label {{
        color: var(--text-soft) !important;
        font-size: 0.83rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 700;
    }}
    .metric-card .value {{
        color: var(--text-primary) !important;
        font-family: {DISPLAY_FONT};
        font-size: 1.55rem;
        font-weight: 700;
        margin-top: 0.15rem;
    }}
    .insight-card .group {{
        color: var(--accent) !important;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 700;
    }}
    .insight-card .title {{
        color: var(--text-primary) !important;
        font-size: 1rem;
        font-weight: 700;
        margin-top: 0.2rem;
        line-height: 1.35;
    }}
    .insight-card .value {{
        color: var(--text-primary) !important;
        font-family: {DISPLAY_FONT};
        font-size: 1.45rem;
        font-weight: 700;
        margin: 0.2rem 0 0.35rem 0;
    }}
    .timeline-card {{
        background: linear-gradient(180deg, rgba(23,32,43,0.96) 0%, rgba(44,57,77,0.96) 100%);
        color: var(--text-inverse) !important;
        min-height: 310px;
        padding: 1.15rem 1.2rem;
    }}
    .timeline-card * {{
        color: var(--text-inverse) !important;
    }}
    .timeline-card p {{
        line-height: 1.55;
    }}
    .chip {{
        display: inline-flex;
        align-items: center;
        background: rgba(255,250,243,0.94);
        border: 1px solid rgba(22,32,44,0.10);
        border-radius: 999px;
        padding: 0.34rem 0.68rem;
        margin-right: 0.4rem;
        margin-bottom: 0.35rem;
        font-size: 0.82rem;
        color: var(--text-primary);
    }}
    div[data-testid="stMetric"] {{
        background: linear-gradient(180deg, rgba(255,250,243,0.98) 0%, rgba(247,240,230,0.98) 100%);
        border: 1px solid rgba(22,32,44,0.10);
        border-radius: 24px;
        padding: 0.9rem 0.95rem;
        box-shadow: 0 10px 28px rgba(22,32,44,0.05);
    }}
    div[data-testid="stMetric"] * {{
        color: var(--text-primary) !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button {{
        width: 100%;
        min-height: 2.5rem;
        background: var(--text-primary) !important;
        color: var(--text-inverse) !important;
        border: 1px solid rgba(22,32,44,0.16) !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        box-shadow: 0 6px 16px rgba(22,32,44,0.10);
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button *,
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button p,
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button span,
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button div {{
        color: var(--text-inverse) !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {{
        background: #202a37 !important;
        color: var(--text-inverse) !important;
        border-color: #202a37 !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover * {{
        color: var(--text-inverse) !important;
    }}
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:active,
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:focus,
    section[data-testid="stSidebar"] div[data-testid="stButton"] > button:focus-visible {{
        background: #111923 !important;
        color: var(--text-inverse) !important;
        border-color: #111923 !important;
        box-shadow: 0 0 0 2px rgba(187,88,43,0.18) !important;
        outline: none !important;
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] > label {{
        background: transparent;
        border-radius: 999px;
        padding: 0.18rem 0.25rem;
        transition: background-color 120ms ease;
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {{
        background: rgba(22,32,44,0.05);
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] label,
    section[data-testid="stSidebar"] div[role="radiogroup"] label * {{
        color: var(--text-primary) !important;
        fill: var(--text-primary) !important;
    }}
    section[data-testid="stSidebar"] div[role="radiogroup"] input:checked + div,
    section[data-testid="stSidebar"] div[role="radiogroup"] input:checked + div *,
    section[data-testid="stSidebar"] div[role="radiogroup"] input:checked ~ div,
    section[data-testid="stSidebar"] div[role="radiogroup"] input:checked ~ div * {{
        color: var(--text-primary) !important;
    }}
    section[data-testid="stSidebar"] [data-baseweb="radio"] div[aria-checked="true"] {{
        color: var(--accent) !important;
    }}
    section[data-testid="stSidebar"] [data-baseweb="radio"] svg {{
        fill: currentColor !important;
    }}
    [data-testid="stExpander"] {{
        border: 1px solid rgba(22,32,44,0.10);
        border-radius: 20px;
        background: rgba(255,250,243,0.92);
        overflow: hidden;
    }}
    [data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {{
        color: var(--text-primary) !important;
        font-weight: 700 !important;
    }}
    [data-testid="stExpander"] > details > div {{
        padding-top: 0.35rem;
    }}
    [data-baseweb="select"] *, [data-baseweb="popover"] *, [data-baseweb="input"] *, [data-baseweb="radio"] * {{
        color: var(--text-primary) !important;
    }}
    div[data-testid="stDataFrame"] {{
        border: 1px solid rgba(22,32,44,0.10);
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 10px 28px rgba(22,32,44,0.04);
    }}
    div[data-testid="stDataFrame"] * {{
        color: var(--text-primary) !important;
    }}
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown strong, .stMarkdown em {{
        color: var(--text-primary);
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: var(--text-primary) !important;
        letter-spacing: -0.02em;
    }}
    .stCaption, [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * {{
        color: var(--text-secondary) !important;
    }}
</style>
"""


@st.cache_data(show_spinner=False)
def load_games_data() -> pd.DataFrame:
    if DEFAULT_PROCESSED_PARQUET.exists():
        return pd.read_parquet(DEFAULT_PROCESSED_PARQUET)
    if DEFAULT_PROCESSED_CSV.exists():
        return pd.read_csv(DEFAULT_PROCESSED_CSV, parse_dates=["release_date"])
    raise FileNotFoundError("Base processada nao encontrada.")


@st.cache_data(show_spinner=False)
def load_store_sources() -> dict[str, object]:
    sources = load_academic_sources()
    return {
        "sales": sources.sales,
        "customer_profile": sources.customer_profile,
        "store_access": sources.store_access,
        "sales_calendar": build_sales_calendar_table(sources.sales),
        "methodology_note": build_methodology_note(sources),
    }


def format_currency(value: float) -> str:
    return f"R${value:,.0f}".replace(",", ".")


def format_percent(value: float) -> str:
    return f"{value:.1f}%"


def inject_theme() -> None:
    st.markdown(THEME, unsafe_allow_html=True)


def apply_chart_style(fig, *, height: int, xaxis_title: str | None = None, yaxis_title: str | None = None) -> None:
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,250,243,0.92)",
        font=dict(family=UI_FONT, color=PALETTE["ink"], size=13),
        title_font=dict(family=DISPLAY_FONT, color=PALETTE["ink"], size=22),
        legend=dict(
            bgcolor="rgba(255,250,243,0.90)",
            bordercolor="rgba(23,32,43,0.08)",
            borderwidth=1,
            font=dict(color=PALETTE["ink"]),
        ),
        margin=dict(l=20, r=20, t=70, b=20),
        hoverlabel=dict(bgcolor="#fffaf3", bordercolor=PALETTE["border"], font=dict(color=PALETTE["ink"], family=UI_FONT)),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(23,32,43,0.10)",
        linecolor="rgba(23,32,43,0.18)",
        tickfont=dict(color=PALETTE["ink"]),
        title_text=xaxis_title,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(23,32,43,0.08)",
        linecolor="rgba(23,32,43,0.18)",
        tickfont=dict(color=PALETTE["ink"]),
        title_text=yaxis_title,
    )


def render_context_box(title: str, happened: str, matters: str, action: str) -> None:
    st.markdown(
        (
            "<div class='context-card'>"
            "<div class='card-kicker'>Leitura do bloco</div>"
            f"<div class='card-title'>{title}</div>"
            f"<p class='card-body'><strong>O que este bloco mostra:</strong> {happened}</p>"
            f"<p class='card-body'><strong>Por que isso importa:</strong> {matters}</p>"
            f"<p class='card-body'><strong>Como isso apoia a decisao:</strong> {action}</p>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_signal_card(title: str, body: str) -> None:
    st.markdown(
        (
            "<div class='signal-card'>"
            "<div class='card-kicker'>Leitura principal</div>"
            f"<div class='card-title'>{title}</div>"
            f"<p class='card-body'>{body}</p>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_surface_card(title: str, body: str) -> None:
    st.markdown(
        (
            "<div class='surface-card'>"
            "<div class='card-kicker'>Resumo</div>"
            f"<div class='card-title'>{title}</div>"
            f"<p class='card-body'>{body}</p>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_metric_cards(cards: list[tuple[str, str]]) -> None:
    columns = st.columns(len(cards))
    for column, (label, value) in zip(columns, cards, strict=False):
        column.markdown(
            f"<div class='metric-card'><div class='label'>{label}</div><div class='value'>{value}</div></div>",
            unsafe_allow_html=True,
        )


def render_chips(items: list[str]) -> None:
    st.markdown("".join(f"<span class='chip'>{item}</span>" for item in items), unsafe_allow_html=True)


def reset_filters() -> None:
    for key in FILTER_KEYS:
        st.session_state.pop(key, None)
    st.rerun()


def build_sidebar(games_df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    st.sidebar.markdown(
        (
            "<div class='side-card'>"
            "<div class='card-kicker'>Apresentacao</div>"
            "<div class='card-title'>Visao do trabalho</div>"
            "<p class='card-body'>Na Fase 1, o painel organiza os dados brutos da SteamLoja. "
            "Na Fase 2, esses dados se transformam em informacoes gerenciais. "
            "Na Fase 3, os resultados sustentam um plano de acao com prioridades, riscos e horizonte de execucao.</p>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        (
            "<div class='side-card'>"
            "<div class='card-kicker'>Base do estudo</div>"
            "<div class='card-title'>Recorte da analise</div>"
            "<p class='card-body'>Empresa ficticia: SteamLoja. "
            "Periodo-base: marco de 2026. "
            "A leitura combina dados operacionais simulados da loja com sinais reais do mercado Steam.</p>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    source_mode = st.sidebar.radio("Fonte ativa", SOURCE_OPTIONS, index=2, key="source_mode")
    if st.sidebar.button("Resetar visao", width="stretch"):
        reset_filters()

    with st.sidebar.expander("Analise avancada"):
        st.caption("Esses filtros afetam apenas a camada de apoio do mercado Steam.")
        segments = sorted(games_df["segment"].dropna().unique().tolist())
        selected_segments = st.multiselect("Segmento", segments, default=segments, key="segment_filter")

        genres = sorted(games_df["primary_genre"].dropna().unique().tolist())
        selected_genres = st.multiselect("Genero", genres, default=genres, key="genre_filter")

        price_buckets = games_df["price_bucket"].dropna().unique().tolist()
        selected_buckets = st.multiselect("Faixa de preco", price_buckets, default=price_buckets, key="price_filter")

        platform = st.selectbox("Plataforma", ["Todas", "Windows", "Mac", "Linux"], index=0, key="platform_filter")

    filtered_games = games_df[
        games_df["segment"].isin(st.session_state.get("segment_filter", segments))
        & games_df["primary_genre"].isin(st.session_state.get("genre_filter", genres))
        & games_df["price_bucket"].isin(st.session_state.get("price_filter", price_buckets))
    ].copy()

    platform = st.session_state.get("platform_filter", "Todas")
    if platform != "Todas":
        filtered_games = filtered_games[filtered_games[platform.casefold()]]

    st.sidebar.caption(f"Jogos no apoio de mercado: {len(filtered_games):,}")
    return filtered_games, source_mode


def render_header(sales_df: pd.DataFrame, games_df: pd.DataFrame, source_mode: str) -> None:
    period = f"{sales_df['date'].min().strftime('%d/%m/%Y')} a {sales_df['date'].max().strftime('%d/%m/%Y')}"
    chips = [
        "SteamLoja",
        "Dados -> analise -> plano",
        f"Periodo base: {period}",
        f"Fonte ativa: {source_mode}",
        f"Base de mercado: {len(games_df):,} jogos",
    ]
    chips_html = "".join(
        f"<span class='chip' style='background:rgba(255,255,255,0.10);color:{PALETTE['text_inverse']};border-color:rgba(255,255,255,0.16);'>{item}</span>"
        for item in chips
    )
    st.markdown(
        f"""
        <div class="hero-panel">
            <div style="color:#ffd9c6; text-transform:uppercase; letter-spacing:0.08em; font-size:0.82rem; font-weight:700;">Trabalho de Gestao e Governanca da Informacao</div>
            <h1 style="font-family:{DISPLAY_FONT}; font-size:2.35rem; margin:0.05rem 0 0.3rem 0;">SteamLoja Academica</h1>
            <p style="font-size:1rem; max-width:860px; line-height:1.58; opacity:0.96;">
                Este painel demonstra como dados operacionais de uma loja ficticia inspirada no ecossistema Steam
                podem ser organizados, interpretados e convertidos em decisoes gerenciais e estrategicas de forma clara e defensavel.
            </p>
            <div>{chips_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_phase_one(store_sources: dict[str, object], source_mode: str) -> None:
    sales_df = store_sources["sales"]
    customer_df = store_sources["customer_profile"]
    access_df = store_sources["store_access"]
    methodology_note = store_sources.get("methodology_note")

    render_signal_card(
        "Fase 1: leitura operacional da SteamLoja",
        "Nesta etapa, a proposta e apresentar a operacao sem interpretacao estrategica. O foco esta em organizar as fontes e identificar padroes basicos de vendas, interesse do publico e fluxo de acesso.",
    )
    if source_mode == "Mercado Steam":
        render_surface_card(
            "Leitura de apoio",
            "Mesmo quando a camada de mercado esta ativa, a Fase 1 permanece centrada na operacao da SteamLoja, porque ela constitui a base do estudo academico.",
        )

    render_metric_cards(
        [
            ("Vendas no mes", f"{int(sales_df['units_sold'].sum()):,} jogos"),
            ("Faturamento no mes", format_currency(float(sales_df["revenue_brl"].sum()))),
            ("Genero mais forte", customer_df.groupby("genre", observed=False)["customer_share_pct"].mean().sort_values(ascending=False).index[0]),
            ("Turno com mais acessos", access_df.groupby("shift", observed=False)["visits"].mean().sort_values(ascending=False).index[0]),
        ]
    )
    if methodology_note:
        render_surface_card("Metodologia da base ficticia", methodology_note)

    st.markdown("<div class='phase-section'></div>", unsafe_allow_html=True)
    left, right = st.columns([1.1, 1.2])
    with left:
        render_context_box(
            "Fonte 1: vendas diarias do mes",
            "Apresenta a quantidade de jogos vendidos em cada dia do mes-base.",
            "Permite identificar picos de demanda, quedas recorrentes e diferencas de desempenho entre os dias da semana.",
            "Serve de base para definir calendario promocional, reforco de vitrine e acoes de reativacao.",
        )
        st.dataframe(store_sources["sales_calendar"], width="stretch")
    with right:
        fig_sales = px.bar(
            sales_df,
            x="date",
            y="units_sold",
            color="campaign_type",
            title="Vendas diarias da SteamLoja no mes base",
            color_discrete_sequence=[PALETTE["accent"], PALETTE["teal"], PALETTE["blue"], PALETTE["gold"], PALETTE["warn"]],
        )
        apply_chart_style(fig_sales, height=430, xaxis_title="Data", yaxis_title="Jogos vendidos")
        st.plotly_chart(fig_sales, width="stretch")

    st.markdown("<div class='phase-section'></div>", unsafe_allow_html=True)
    left, right = st.columns([1, 1.1])
    with left:
        profile_average = (
            customer_df.groupby("genre", observed=False)["customer_share_pct"]
            .mean()
            .sort_values(ascending=True)
            .reset_index()
        )
        fig_profile = px.bar(
            profile_average,
            x="customer_share_pct",
            y="genre",
            orientation="h",
            title="Perfil medio de clientes por genero",
            color="customer_share_pct",
            color_continuous_scale=["#e6d7bf", PALETTE["accent"], PALETTE["teal"]],
        )
        apply_chart_style(fig_profile, height=410, xaxis_title="% medio de clientes", yaxis_title="Genero")
        st.plotly_chart(fig_profile, width="stretch")
    with right:
        render_context_box(
            "Fonte 2: perfil de clientes por genero",
            "Mostra quais generos concentram maior interesse do publico ao longo da semana.",
            "Ajuda a entender o perfil da demanda e a ajustar curadoria, comunicacao e composicao de bundles.",
            "Orienta quais categorias merecem mais destaque comercial e editorial.",
        )
        weekly_profile = customer_df.pivot(index="weekday", columns="genre", values="customer_share_pct").reindex(WEEKDAY_ORDER)
        st.dataframe(weekly_profile, width="stretch")

    st.markdown("<div class='phase-section'></div>", unsafe_allow_html=True)
    left, right = st.columns([1, 1.1])
    with left:
        render_context_box(
            "Fonte 3: acessos por turno",
            "Apresenta o volume de visitas da loja por turno ao longo da semana.",
            "Essa leitura ajuda a localizar os momentos de maior exposicao e os vales de menor tracao.",
            "Apoia a definicao de horario para campanhas principais, atualizacao de vitrine e acoes de recuperacao.",
        )
        access_table = access_df.pivot(index="weekday", columns="shift", values="visits").reindex(index=WEEKDAY_ORDER, columns=SHIFT_ORDER)
        st.dataframe(access_table, width="stretch")
    with right:
        heatmap = access_df.pivot(index="weekday", columns="shift", values="visits").reindex(index=WEEKDAY_ORDER, columns=SHIFT_ORDER)
        fig_heatmap = go.Figure(
            data=go.Heatmap(
                z=heatmap.values,
                x=heatmap.columns.tolist(),
                y=heatmap.index.tolist(),
                colorscale=[[0, "#efe3d0"], [0.5, "#d97841"], [1, "#8a2f23"]],
                hovertemplate="Dia=%{y}<br>Turno=%{x}<br>Acessos=%{z}<extra></extra>",
                colorbar=dict(title="Acessos"),
            )
        )
        fig_heatmap.update_layout(title="Acessos da loja por dia e turno")
        apply_chart_style(fig_heatmap, height=410, xaxis_title="Turno", yaxis_title="Dia")
        st.plotly_chart(fig_heatmap, width="stretch")


def render_insight_cards(insights: list[dict[str, str]]) -> None:
    columns = st.columns(2)
    for index, insight in enumerate(insights):
        columns[index % 2].markdown(
            (
                "<div class='insight-card'>"
                f"<div class='group'>{insight['group']}</div>"
                f"<div class='title'>{insight['title']}</div>"
                f"<div class='value'>{insight['value']}</div>"
                f"<p class='card-body'><strong>Por que isso importa:</strong> {insight['why']}</p>"
                f"<p class='card-body'><strong>Implicacao gerencial:</strong> {insight['action']}</p>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )


def render_market_anchor_cards(anchors: dict[str, object]) -> None:
    render_metric_cards(
        [
            ("Diferenca AAA vs Indie", f"${anchors['price_diff']:,.2f}"),
            ("Jogos gratis no topo", format_percent(float(anchors["free_share_top"]))),
            ("Suporte Linux no topo", format_percent(float(anchors["linux_share_top"]))),
        ]
    )
    render_context_box(
        "Ancoras de mercado Steam",
        "Esses tres sinais conectam a operacao da SteamLoja ao comportamento real do ecossistema Steam.",
        "Eles reforcam que o planejamento considera preco, modelo free-to-play e aderencia a Linux e SteamOS.",
        "Fortalecem a argumentacao do trabalho ao aproximar a proposta academica de movimentos concretos do mercado.",
    )


def render_phase_two(store_sources: dict[str, object], filtered_games: pd.DataFrame, source_mode: str) -> tuple[list[dict[str, str]], dict[str, object], dict[str, object]]:
    insights = build_academic_insights(store_sources["sales"], store_sources["customer_profile"], store_sources["store_access"])
    anchors = build_market_anchors(filtered_games)
    strategy = build_strategy_payload(insights, anchors, store_sources["sales"], store_sources["customer_profile"], store_sources["store_access"])

    render_signal_card(
        "Fase 2: transformacao dos dados em informacao gerencial",
        "Nesta fase, a analise deixa de apenas descrever a operacao e passa a destacar relacoes, prioridades e oportunidades de decisao que podem ser defendidas com clareza.",
    )
    grouped_labels = ["10 informacoes gerenciais", "Vendas, clientes e acessos", f"Fonte ativa: {source_mode}"]
    render_chips(grouped_labels)
    render_insight_cards(insights)

    col_a, col_b = st.columns(2)
    with col_a:
        sales_weekday = (
            store_sources["sales"].groupby("weekday", observed=False)["units_sold"]
            .mean()
            .reindex(WEEKDAY_ORDER)
            .dropna()
            .reset_index()
        )
        fig_sales_weekday = px.bar(
            sales_weekday,
            x="weekday",
            y="units_sold",
            title="Media de vendas por dia da semana",
            color="units_sold",
            color_continuous_scale=["#efe3d0", PALETTE["accent"]],
        )
        apply_chart_style(fig_sales_weekday, height=380, xaxis_title="Dia", yaxis_title="Jogos vendidos")
        st.plotly_chart(fig_sales_weekday, width="stretch")
    with col_b:
        genre_average = (
            store_sources["customer_profile"].groupby("genre", observed=False)["customer_share_pct"]
            .mean()
            .sort_values(ascending=True)
            .reset_index()
        )
        fig_genre = px.bar(
            genre_average,
            x="customer_share_pct",
            y="genre",
            orientation="h",
            title="Media de interesse por genero",
            color="customer_share_pct",
            color_continuous_scale=["#efe3d0", PALETTE["teal"]],
        )
        apply_chart_style(fig_genre, height=380, xaxis_title="% medio", yaxis_title="Genero")
        st.plotly_chart(fig_genre, width="stretch")

    access_heatmap = store_sources["store_access"].pivot(index="weekday", columns="shift", values="visits").reindex(index=WEEKDAY_ORDER, columns=SHIFT_ORDER)
    fig_access = go.Figure(
        data=go.Heatmap(
            z=access_heatmap.values,
            x=access_heatmap.columns.tolist(),
            y=access_heatmap.index.tolist(),
            colorscale=[[0, "#efe3d0"], [0.45, "#d97841"], [1, "#155d68"]],
            hovertemplate="Dia=%{y}<br>Turno=%{x}<br>Acessos=%{z}<extra></extra>",
            colorbar=dict(title="Acessos"),
        )
    )
    fig_access.update_layout(title="Comportamento de acessos por dia e turno")
    apply_chart_style(fig_access, height=380, xaxis_title="Turno", yaxis_title="Dia")
    st.plotly_chart(fig_access, width="stretch")

    if source_mode != "Operacao da loja":
        st.subheader("Ancoras de mercado Steam")
        render_market_anchor_cards(anchors)
        render_surface_card("Indicador composto de oportunidade", str(anchors["indicator_formula"]))
        top_games = pd.DataFrame(anchors["opportunities"])
        top_games["linux"] = top_games["linux"].map({True: "Sim", False: "Nao"})
        st.dataframe(top_games, width="stretch", hide_index=True)

    return insights, anchors, strategy


def render_timeline_column(title: str, items: list[dict[str, str]]) -> None:
    body = "".join(
        f"<p><strong>Fazer isso:</strong> {item['do']}</p><p><strong>Por causa disso:</strong> {item['because']}</p><p><strong>Impacto esperado:</strong> {item['impact']}</p><hr style='border-color:rgba(255,255,255,0.14); margin:0.85rem 0;'/>"
        for item in items
    )
    st.markdown(
        f"<div class='timeline-card'><strong style='font-size:1.15rem;'>{title}</strong>{body}</div>",
        unsafe_allow_html=True,
    )


def render_phase_three(store_sources: dict[str, object], strategy: dict[str, object], source_mode: str) -> None:
    render_signal_card(
        "Fase 3: planejamento estrategico",
        "Nesta fase, os sinais da operacao e do mercado sao convertidos em um plano de acao com horizonte de 3 meses, 6 meses e 1 ano, incluindo prioridades, riscos e conexao com o setor.",
    )
    render_surface_card("Resumo executivo", str(strategy["summary"]))
    render_chips([f"Fonte ativa: {source_mode}", "Planejamento academico", "Empresa ficticia alinhada ao mercado real"])

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        render_timeline_column("Cronograma de 3 meses", strategy["three_months"])
    with col_b:
        render_timeline_column("Cronograma de 6 meses", strategy["six_months"])
    with col_c:
        render_timeline_column("Cronograma de 1 ano", strategy["one_year"])

    grid_a, grid_b = st.columns(2)
    with grid_a:
        st.markdown(
            "<div class='surface-card'><div class='card-kicker'>Organizacao</div><div class='card-title'>Demandas e tarefas</div><ul class='card-list'>"
            + "".join(f"<li>{item}</li>" for item in strategy["demands"] + strategy["tasks"])
            + "</ul></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='surface-card'><div class='card-kicker'>Ordem de ataque</div><div class='card-title'>Prioridades</div><ul class='card-list'>"
            + "".join(f"<li>{item}</li>" for item in strategy["priorities"])
            + "</ul></div>",
            unsafe_allow_html=True,
        )
    with grid_b:
        st.markdown(
            "<div class='surface-card'><div class='card-kicker'>Controle</div><div class='card-title'>Riscos e contingencias</div><ul class='card-list'>"
            + "".join(f"<li>{item}</li>" for item in strategy["risks"] + strategy["contingencies"])
            + "</ul></div>",
            unsafe_allow_html=True,
        )

    st.subheader("3 acoes estrategicas principais")
    for action in strategy["actions"]:
        st.markdown(
            (
                "<div class='surface-card'>"
                "<div class='card-kicker'>Acao principal</div>"
                f"<div class='card-title'>{action['title']}</div>"
                f"<p class='card-body'><strong>Proposta:</strong> {action['do']}</p>"
                f"<p class='card-body'><strong>Justificativa:</strong> {action['because']}</p>"
                f"<p class='card-body'><strong>Resultado esperado:</strong> {action['impact']}</p>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

    render_surface_card("Conexao com o mercado", str(strategy["market_connection"]))


def render_export_controls(games_df: pd.DataFrame) -> None:
    context = build_report_context(games_df)
    try:
        pdf_bytes = build_pdf_report(context)
    except RuntimeError as exc:
        render_signal_card("Exportacao em PDF indisponivel", str(exc))
        return

    st.download_button(
        "Baixar relatorio em PDF",
        data=pdf_bytes,
        file_name="steamloja_academica.pdf",
        mime="application/pdf",
        width="stretch",
    )


def run_app() -> None:
    st.set_page_config(page_title="SteamLoja Academica", layout="wide")
    inject_theme()

    try:
        games_df = load_games_data()
        store_sources = load_store_sources()
    except FileNotFoundError:
        st.error("Base necessaria nao encontrada. Rode a preparacao do projeto antes de abrir o painel.")
        st.stop()

    filtered_games, source_mode = build_sidebar(games_df)
    if filtered_games.empty:
        render_signal_card("Sem jogos no apoio de mercado", "Ajuste os filtros avancados para voltar a ver as ancoras de mercado Steam.")
        st.stop()

    render_header(store_sources["sales"], filtered_games, source_mode)

    tabs = st.tabs(
        [
            "Fase 1: Coleta e Organizacao",
            "Fase 2: Processamento e Insights",
            "Fase 3: Planejamento Estrategico",
        ]
    )
    with tabs[0]:
        render_phase_one(store_sources, source_mode)
    with tabs[1]:
        insights, anchors, strategy = render_phase_two(store_sources, filtered_games, source_mode)
    with tabs[2]:
        strategy = build_strategy_payload(
            build_academic_insights(store_sources["sales"], store_sources["customer_profile"], store_sources["store_access"]),
            build_market_anchors(filtered_games),
            store_sources["sales"],
            store_sources["customer_profile"],
            store_sources["store_access"],
        )
        render_export_controls(filtered_games)
        render_phase_three(store_sources, strategy, source_mode)
