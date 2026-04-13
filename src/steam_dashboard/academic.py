from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .context_sources import ContextSources, build_external_insights, load_context_sources
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


def build_operational_insights(sales_df: pd.DataFrame, customer_df: pd.DataFrame, access_df: pd.DataFrame) -> list[dict[str, str]]:
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

    operational_source = {"source_name": "Operacao SteamLoja", "source_url": "", "period": "Mar/2026"}
    return [
        {
            "group": "Vendas",
            "title": "Dia com maior media de vendas",
            "value": f"{best_day} ({best_day_value:,.0f} jogos)",
            "why": f"{best_day} concentra a media mais alta de unidades vendidas no mes analisado.",
            "action": f"A janela de {best_day} deve receber o principal destaque promocional da SteamLoja.",
            **operational_source,
        },
        {
            "group": "Vendas",
            "title": "Relacao entre o melhor e o pior dia",
            "value": f"{best_day_value / worst_day_value:.2f}x",
            "why": f"A diferenca entre {best_day} e {worst_day} confirma uma operacao com picos claros de demanda.",
            "action": f"{worst_day} deve ser tratado como prioridade para campanhas de reativacao e oferta de entrada.",
            **operational_source,
        },
        {
            "group": "Vendas",
            "title": "Peso de sexta e sabado nas vendas do mes",
            "value": f"{weekend_share:.1f}%",
            "why": "O fechamento da semana concentra parte relevante da conversao total da loja.",
            "action": "Vitrine, combos promocionais e verba de divulgacao precisam estar mais fortes nesse intervalo.",
            **operational_source,
        },
        {
            "group": "Vendas",
            "title": "Total vendido e media diaria",
            "value": f"{total_units:,} jogos | media {daily_average:,.0f}",
            "why": "Esse volume define a escala da operacao academica e cria uma base comparavel para ciclos futuros.",
            "action": "A media diaria deve ser usada como referencia para metas e avaliacao de campanhas.",
            **operational_source,
        },
        {
            "group": "Clientes",
            "title": "Genero com maior interesse do publico",
            "value": f"{top_genre} ({top_genre_value:.1f}%)",
            "why": "Esse genero lidera o interesse observado no comportamento semanal dos clientes.",
            "action": f"A curadoria comercial e a comunicacao principal devem priorizar jogos de {top_genre}.",
            **operational_source,
        },
        {
            "group": "Clientes",
            "title": "Participacao conjunta dos generos mais fortes",
            "value": f"{top_three_share:.1f}%",
            "why": "Os tres generos lideres concentram a maior parte do interesse potencial de compra.",
            "action": "Combos, colecoes e campanhas tematicas devem partir dos generos mais fortes.",
            **operational_source,
        },
        {
            "group": "Acessos e comportamento",
            "title": "Turno com maior volume de acessos",
            "value": f"{top_shift} ({top_shift_value:,.0f} acessos)",
            "why": "O fluxo de visitas fica mais intenso nesse turno e amplia o potencial de conversao.",
            "action": f"As atualizacoes centrais de vitrine devem ser publicadas na {top_shift.lower()}.",
            **operational_source,
        },
        {
            "group": "Acessos e comportamento",
            "title": "Dia e turno de maior trafego",
            "value": f"{top_window['weekday']} / {top_window['shift']}",
            "why": "Essa e a janela de maior exposicao da SteamLoja na semana observada.",
            "action": "Lancamentos, ofertas premium e banners principais devem estrear nesse pico.",
            **operational_source,
        },
        {
            "group": "Acessos e comportamento",
            "title": "Janela de baixa demanda para reativacao",
            "value": f"{low_window['weekday']} / {low_window['shift']}",
            "why": "Esse ponto concentra o menor fluxo de acesso e representa o principal vale operacional.",
            "action": "Cupom leve, combo de entrada ou conteudo editorial devem ser testados nesse horario.",
            **operational_source,
        },
        {
            "group": "Acessos e comportamento",
            "title": "Melhor combinacao comercial do recorte",
            "value": f"{best_conversion_day} + {top_genre} + {top_shift}",
            "why": "A combinacao reune o melhor dia de vendas, o genero dominante e o turno de maior trafego.",
            "action": f"A campanha principal deve ser organizada em {best_conversion_day}, com foco em {top_genre}, no turno da {top_shift.lower()}.",
            **operational_source,
        },
    ]


def build_academic_insights(
    sales_df: pd.DataFrame,
    customer_df: pd.DataFrame,
    access_df: pd.DataFrame,
    context_sources: ContextSources | None = None,
) -> list[dict[str, str]]:
    context_sources = context_sources or load_context_sources()
    return build_operational_insights(sales_df, customer_df, access_df) + build_external_insights(context_sources)


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
            "Indicador composto: junta tamanho estimado do publico, aprovacao dos jogadores, engajamento e facilidade de compra pelo preco. "
            "Ele ajuda a comparar jogos, mas nao substitui uma avaliacao humana do catalogo."
        ),
    }


def build_strategy_payload(
    insights: list[dict[str, str]],
    anchors: dict[str, object],
    sales_df: pd.DataFrame,
    customer_df: pd.DataFrame,
    access_df: pd.DataFrame,
    context_sources: ContextSources | None = None,
) -> dict[str, object]:
    context_sources = context_sources or load_context_sources()
    best_day = insights[0]["value"].split(" (")[0]
    low_window = insights[8]["value"]
    best_combo = insights[9]["value"]
    top_genre = insights[4]["value"].split(" (")[0]
    top_shift = insights[6]["value"].split(" (")[0]

    price_diff = float(anchors["price_diff"])
    free_share = float(anchors["free_share_top"])
    linux_share = float(anchors["linux_share_top"])
    revenue_total = float(sales_df["revenue_brl"].sum())

    linux_shift = context_sources.platform_shift.loc[context_sources.platform_shift["metric"] == "Participacao do Linux na Steam", "value"].iloc[0]
    windows_shift = context_sources.platform_shift.loc[context_sources.platform_shift["metric"] == "Participacao do Windows na Steam", "value"].iloc[0]
    steamos_share = context_sources.platform_shift.loc[
        context_sources.platform_shift["metric"] == "Participacao do SteamOS Holo entre usuarios Linux da Steam", "value"
    ].iloc[0]
    removable_apps = context_sources.windows_friction.loc[
        context_sources.windows_friction["metric"] == "Aplicativos preinstalados configuraveis para remocao por politica no Windows 11 25H2", "value"
    ].iloc[0]
    consumer_dram = context_sources.hardware_cost_pressure.loc[
        context_sources.hardware_cost_pressure["metric"] == "Consumer DRAM no 2Q26", "value"
    ].iloc[0]
    conventional_dram = context_sources.hardware_cost_pressure.loc[
        context_sources.hardware_cost_pressure["metric"] == "Conventional DRAM no 2Q26", "value"
    ].iloc[0]
    nand = context_sources.hardware_cost_pressure.loc[
        context_sources.hardware_cost_pressure["metric"] == "NAND Flash no 2Q26", "value"
    ].iloc[0]
    steam_hardware = context_sources.hardware_cost_pressure.loc[
        context_sources.hardware_cost_pressure["metric"] == "Steam Deck recondicionado e Steam Machine listados na loja oficial", "value"
    ].iloc[0]

    return {
        "summary": (
            f"A SteamLoja segue com seu pico comercial em {best_day}, interesse dominante em {top_genre} e maior trafego no turno da {top_shift.lower()}. "
            f"A diferenca agora e que o plano de medio e longo prazo passa a se apoiar em sinais externos mais fortes: Linux chegou a {linux_shift} na Steam, "
            f"Windows caiu para {windows_shift}, SteamOS Holo ja representa {steamos_share} do recorte Linux e o Windows 11 25H2 preve remocao de {removable_apps}. "
            f"No hardware, a pressao de memoria para consumidor ({consumer_dram}), memoria comum ({conventional_dram}) e armazenamento NAND ({nand}) se combina com uma entrada oficial mais acessivel ({steam_hardware}) e reforca a importancia de combos e hardware proprio. "
            f"Como referencia de mercado, AAA e Indie mantem distancia mediana de ${price_diff:,.2f}, com {free_share:.1f}% de jogos gratuitos entre os titulos mais populares e {linux_share:.1f}% de suporte Linux nesse grupo."
        ),
        "three_months": [
            {
                "do": f"Reforcar a vitrine principal em {best_day}, com foco na combinacao {best_combo}.",
                "because": "Essa e a janela de maior demanda e concentracao de interesse do recorte analisado.",
                "impact": "A medida tende a elevar a conversao sem aumentar significativamente a complexidade operacional.",
                "supports": "Infos 1, 8 e 10",
            },
            {
                "do": f"Criar uma campanha de reativacao para {low_window}.",
                "because": "Esse e o principal vale semanal de acesso e precisa ser tratado com prioridade.",
                "impact": "A acao reduz ociosidade e melhora a distribuicao das vendas ao longo da semana.",
                "supports": "Infos 2 e 9",
            },
            {
                "do": "Organizar combos simples com o genero mais procurado e preco de entrada acessivel.",
                "because": "O publico demonstrou preferencia clara por poucos generos centrais.",
                "impact": "Isso tende a acelerar a decisao de compra e simplificar a comunicacao da loja.",
                "supports": "Infos 5 e 6",
            },
        ],
        "six_months": [
            {
                "do": "Investir na divulgacao do SteamOS com uma frente editorial e comercial chamada Pronto para SteamOS.",
                "because": "A migracao de base para Linux e o peso crescente do SteamOS Holo mostram que o ecossistema da Valve ja tem tracao real fora do Windows.",
                "impact": "A SteamLoja passa a capturar mais usuarios dentro do ecossistema Steam, com maior recorrencia e menor dependencia de plataformas concorrentes.",
                "supports": "Infos 11 e 12",
            },
            {
                "do": "Criar colecoes, filtros e campanhas para Steam Deck, Steam Machine e jogos prontos para SteamOS dentro da loja.",
                "because": "Quando a experiencia Windows exige simplificacao oficial e a busca por plataformas focadas em jogo aumenta, uma curadoria guiada por compatibilidade ganha valor comercial.",
                "impact": "Isso melhora conversao, reduz duvida de compra e reforca a identidade da SteamLoja como extensao do ecossistema Valve.",
                "supports": "Infos 12 e 13",
            },
            {
                "do": "Padronizar a comunicacao da loja em torno de praticidade, biblioteca unificada e experiencia mais limpa do que o PC gamer tradicional.",
                "because": "O recorte de plataforma mostra evasao relativa do Windows e abre espaco para posicionar SteamOS como ambiente mais focado em jogo.",
                "impact": "A marca da SteamLoja ganha um discurso mais coerente com a direcao atual da Valve e com a defesa academica.",
                "supports": "Infos 11, 12 e 13",
            },
        ],
        "one_year": [
            {
                "do": "Montar combos de hardware proprio com Steam Deck, futura linha Steam Machine, credito de loja, cartoes-presente e acessorios.",
                "because": "A alta de memoria e armazenamento pressiona o custo do PC tradicional, enquanto a loja oficial da Steam ja combina entrada acessivel via equipamento recondicionado com expansao da linha de hardware.",
                "impact": "A SteamLoja passa a vender entrada no ecossistema, e nao apenas software, elevando receita por cliente e fidelizacao.",
                "supports": "Info 14",
            },
            {
                "do": "Criar uma politica de acesso ao hardware com parcelamento, equipamentos recondicionados e combos de entrada.",
                "because": "Acessibilidade de hardware se torna argumento central num mercado em que DRAM e NAND pressionam o preco final do consumidor.",
                "impact": "A loja amplia alcance sem depender de aumento direto da taxa da plataforma, o que deixa a estrategia mais defensavel.",
                "supports": "Info 14",
            },
            {
                "do": "Subsidiar parte do hardware com o lucro gerado por quem entra e continua comprando no ecossistema, e nao por uma assinatura centralizada.",
                "because": "Os dados observados sustentam melhor a captura por hardware, sistema e biblioteca do que uma mudanca abrupta para um modelo de assinatura parecido com o Game Pass.",
                "impact": "A SteamLoja preserva coerencia com a estrategia Valve e evita conflito prematuro entre assinatura, margem e venda unitaria.",
                "supports": "Info 14 + apoio de pirataria",
            },
        ],
        "demands": [
            "Aumentar vendas fora do pico de sexta e sabado.",
            "Transformar o crescimento de Linux e SteamOS em argumentacao comercial real da loja.",
            "Construir uma frente de hardware proprio acessivel sem depender de aumento de taxa como principal alavanca.",
        ],
        "tasks": [
            "Revisar semanalmente vendas, genero preferido e acessos por turno.",
            "Atualizar vitrine e combos de acordo com o calendario promocional e com a colecao Pronto para SteamOS.",
            "Acompanhar mensalmente sinais de plataforma, custo de hardware e monetizacao para ajustar a estrategia.",
        ],
        "priorities": [
            "Alta: ocupar a janela mais forte da semana e corrigir o principal vale operacional.",
            "Media: transformar SteamOS e compatibilidade com hardware Valve em pilar visivel de selecao e divulgacao.",
            "Baixa: avaliar assinatura apenas como oportunidade futura, depois da consolidacao do ecossistema.",
        ],
        "risks": [
            "Risco comercial: insistir apenas em promocao de software e perder a onda de captura por ecossistema SteamOS e hardware.",
            "Risco operacional: comunicar hardware proprio sem politica clara de preco, combo comercial e reposicao.",
            "Risco estrategico: tentar forcar assinatura cedo demais e gerar conflito com a logica atual de ecossistema da Valve.",
        ],
        "contingencies": [
            "Manter plano promocional alternativo para dias de baixa resposta.",
            "Trabalhar hardware com combos de entrada, equipamentos recondicionados e parcelamento antes de discutir expansao agressiva.",
            "Revisar trimestralmente o discurso de SteamOS e hardware com base em sinais reais de plataforma e custo.",
        ],
        "actions": [
            {
                "title": "Campanhas de reativacao na janela fraca",
                "do": f"Ativar combos leves e cupons em {low_window}.",
                "because": "Esse e o ponto mais fraco da semana em acesso e potencial de venda.",
                "impact": "A tendencia e reduzir o vale operacional e gerar receita incremental.",
                "supports": "Infos 2 e 9",
            },
            {
                "title": "Divulgacao estruturada do SteamOS",
                "do": "Lancar colecoes Pronto para SteamOS e guias simples de migracao para Steam Deck e Steam Machine.",
                "because": "Linux cresceu na Steam, SteamOS Holo ganhou peso dentro desse recorte e o Windows passou a sinalizar mais atrito de experiencia.",
                "impact": "A SteamLoja fortalece captura de usuario dentro do ecossistema Valve e melhora a coerencia do plano de medio prazo.",
                "supports": "Infos 11, 12 e 13",
            },
            {
                "title": "Hardware proprio com acesso comercial mais inteligente",
                "do": "Estruturar combos de Steam Deck e futura Steam Machine com credito de loja, acessorios e opcao de entrada acessivel.",
                "because": "Memoria e armazenamento ficaram mais caros, e a loja oficial da Steam ja sinaliza uma escada comercial que vai do equipamento recondicionado ao hardware novo.",
                "impact": "A SteamLoja passa a capturar valor por ecossistema completo, e nao apenas por venda pontual de software.",
                "supports": "Info 14",
            },
        ],
        "future_opportunities": [
            "Uma assinatura parecida com o Game Pass fica como hipotese futura, nao como eixo principal do plano.",
            "Ela so deve ser reconsiderada depois que a base de hardware e a colecao Pronto para SteamOS estiverem mais maduras.",
        ],
        "market_connection": (
            "O plano posiciona a SteamLoja como uma empresa ficticia coerente com o mercado real. "
            "No curto prazo, ele protege as melhores janelas de conversao da operacao. No medio prazo, transforma a migracao para Linux e o crescimento do SteamOS em argumento comercial concreto. "
            "No longo prazo, usa a pressao de custo em hardware e a ampliacao do catalogo Steam para defender combos, acessibilidade e captura por ecossistema. "
            f"O faturamento observado no mes-base foi de R${revenue_total:,.0f}, o que reforca a necessidade de ligar operacao, plataforma e hardware em uma mesma narrativa estrategica."
        ),
    }


def build_methodology_note(sources: AcademicSources, context_sources: ContextSources | None = None) -> str:
    context_sources = context_sources or load_context_sources()
    external_rows = sum(
        len(frame)
        for frame in (
            context_sources.platform_shift,
            context_sources.windows_friction,
            context_sources.hardware_cost_pressure,
            context_sources.piracy_pressure,
        )
    )
    return (
        "A camada academica foi modelada em grao detalhado e depois consolidada para apresentacao. "
        f"O recorte inclui {len(sources.raw_sales):,} pedidos, {len(sources.raw_customer_profile):,} sinais de perfil de cliente "
        f"e {len(sources.raw_store_access):,} sessoes de acesso, distribuidos por pais, canal, campanha, dispositivo e genero. "
        f"Somam-se a isso {external_rows} leituras externas reais sobre plataforma, Windows, custo de hardware e pirataria para sustentar o planejamento de medio e longo prazo."
    )


def build_academic_payload(games_df: pd.DataFrame) -> dict[str, object]:
    sources = load_academic_sources()
    context_sources = load_context_sources()
    insights = build_academic_insights(sources.sales, sources.customer_profile, sources.store_access, context_sources)
    anchors = build_market_anchors(games_df)
    strategy = build_strategy_payload(insights, anchors, sources.sales, sources.customer_profile, sources.store_access, context_sources)

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
        "context_sources": context_sources,
        "sales_calendar": build_sales_calendar_table(sources.sales),
        "sales_weekday": sales_weekday,
        "genre_average": genre_average,
        "access_heatmap": access_heatmap,
        "insights": insights,
        "anchors": anchors,
        "strategy": strategy,
        "methodology_note": build_methodology_note(sources, context_sources),
    }
