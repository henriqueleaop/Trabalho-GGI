from __future__ import annotations

from io import BytesIO

import pandas as pd

from .academic import (
    build_academic_insights,
    build_market_anchors,
    build_methodology_note,
    build_sales_calendar_table,
    build_strategy_payload,
    load_academic_sources,
)
from .context_sources import build_context_reference_table, build_piracy_support, load_context_sources


def build_report_context(games_df: pd.DataFrame) -> dict[str, object]:
    sources = load_academic_sources()
    context_sources = load_context_sources()
    insights = build_academic_insights(sources.sales, sources.customer_profile, sources.store_access, context_sources)
    anchors = build_market_anchors(games_df)
    strategy = build_strategy_payload(insights, anchors, sources.sales, sources.customer_profile, sources.store_access, context_sources)
    sales_calendar = build_sales_calendar_table(sources.sales)
    customer_profile = sources.customer_profile.pivot(index="weekday", columns="genre", values="customer_share_pct")
    store_access = sources.store_access.pivot(index="weekday", columns="shift", values="visits")

    return {
        "sources": sources,
        "context_sources": context_sources,
        "insights": insights,
        "anchors": anchors,
        "strategy": strategy,
        "sales_calendar": sales_calendar,
        "customer_profile_table": customer_profile,
        "store_access_table": store_access,
        "methodology_note": build_methodology_note(sources, context_sources),
        "context_reference_table": build_context_reference_table(context_sources),
        "piracy_support": build_piracy_support(context_sources),
    }


def _format_source_suffix(item: dict[str, object]) -> str:
    source_name = str(item.get("source_name", "")).strip()
    period = str(item.get("period", "")).strip()
    if source_name and period:
        return f"{source_name} ({period})"
    return source_name or period


def build_markdown_report(context: dict[str, object]) -> str:
    insights = context["insights"]
    anchors = context["anchors"]
    strategy = context["strategy"]
    sales_calendar = context["sales_calendar"]
    customer_profile = context["customer_profile_table"]
    store_access = context["store_access_table"]
    methodology_note = context["methodology_note"]
    context_reference = context["context_reference_table"]
    piracy_support = context["piracy_support"]

    sales_calendar_md = "```text\n" + sales_calendar.to_string() + "\n```"
    customer_md = "```text\n" + customer_profile.to_string() + "\n```"
    access_md = "```text\n" + store_access.to_string() + "\n```"
    context_md = "```text\n" + context_reference.to_string(index=False) + "\n```"
    insights_md = "\n".join(
        f"{index}. **{item['title']}**: {item['value']} - {item['why']} Acao sugerida: {item['action']} Fonte: {_format_source_suffix(item)}"
        for index, item in enumerate(insights, start=1)
    )
    piracy_md = "\n".join(
        f"- **{item['title']}**: {item['value']} - {item['why']} Implicacao: {item['action']} Fonte: {item['source_name']} ({item['period']})"
        for item in piracy_support
    )
    opportunities_md = "\n".join(
        f"- {item['name']} | {item['market_tier']} | {item['primary_genre']} | ${item['price']:.2f} | indicador {item['indicador_composto']:.1f} | Linux: {'Sim' if item['linux'] else 'Nao'}"
        for item in anchors["opportunities"]
    )
    action_md = "\n".join(
        f"- **{item['title']}**: {item['do']} {item['because']} {item['impact']} Sustentado por: {item.get('supports', 'Leitura consolidada')}"
        for item in strategy["actions"]
    )

    return f"""# SteamLoja Academica

## Introducao

Este relatorio apresenta a SteamLoja como empresa ficticia inspirada no ecossistema Steam. O objetivo e mostrar a passagem de dado bruto para informacao gerencial e, depois, para planejamento estrategico.

## Fase 1: Coleta e Organizacao

Nesta etapa a SteamLoja apenas observa o funcionamento da operacao.

### Nota de metodologia

{methodology_note}

### Fonte 1: Vendas diarias do mes

{sales_calendar_md}

### Fonte 2: Perfil de clientes por genero

{customer_md}

### Fonte 3: Acessos por turno

{access_md}

### Fontes externas de contexto estrategico

{context_md}

## Fase 2: Processamento e Informacoes

### 14 informacoes estrategicas

{insights_md}

### Apoio de monetizacao e pirataria

{piracy_md}

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
        f"- Fazer isso: {item['do']} Por causa disso: {item['because']} Impacto esperado: {item['impact']} Sustentado por: {item.get('supports', 'Leitura consolidada')}"
        for item in strategy["three_months"]
    ) + """

### Cronograma de 6 meses
""" + "\n".join(
        f"- Fazer isso: {item['do']} Por causa disso: {item['because']} Impacto esperado: {item['impact']} Sustentado por: {item.get('supports', 'Leitura consolidada')}"
        for item in strategy["six_months"]
    ) + """

### Cronograma de 1 ano
""" + "\n".join(
        f"- Fazer isso: {item['do']} Por causa disso: {item['because']} Impacto esperado: {item['impact']} Sustentado por: {item.get('supports', 'Leitura consolidada')}"
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

### Hipotese futura nao priorizada
{chr(10).join(f"- {item}" for item in strategy["future_opportunities"])}

## Aderencia as decisoes reais da Steam/Valve

- A leitura de Linux e SteamOS aproxima o trabalho da estrategia de plataforma aberta da Valve.
- O foco em eventos, ofertas recorrentes e combos reflete a forma como a Steam organiza divulgacao e descoberta.
- A referencia a Steam Machine -> Steam Deck reforca que o ecossistema da Valve amadureceu de tentativa isolada para proposta integrada.
"""


def _table_data(df: pd.DataFrame) -> list[list[str]]:
    header = [str(df.index.name or "")] + [str(column) for column in df.columns]
    rows = [[str(index)] + [str(value) for value in row] for index, row in df.iterrows()]
    return [header] + rows


def _group_insights_by_category(insights: list[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for item in insights:
        grouped.setdefault(str(item["group"]), []).append(item)
    return grouped


def build_pdf_report(context: dict[str, object]) -> bytes:
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "reportlab nao esta instalado. Rode `python -m pip install -r requirements.txt` para habilitar a exportacao em PDF."
        ) from exc

    sources = context["sources"]
    insights = context["insights"]
    anchors = context["anchors"]
    strategy = context["strategy"]
    sales_calendar = context["sales_calendar"]
    customer_profile = context["customer_profile_table"]
    store_access = context["store_access_table"]
    methodology_note = context["methodology_note"]
    context_sources = context["context_sources"]
    piracy_support = context["piracy_support"]
    grouped_insights = _group_insights_by_category(insights)

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=18,
            textColor=colors.HexColor("#16202c"),
            spaceBefore=8,
            spaceAfter=8,
            alignment=TA_LEFT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverKicker",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#bb582b"),
            spaceAfter=10,
            alignment=TA_LEFT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=28,
            textColor=colors.HexColor("#16202c"),
            spaceAfter=10,
            alignment=TA_LEFT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubsectionTitle",
            parent=styles["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#16202c"),
            spaceBefore=6,
            spaceAfter=6,
            alignment=TA_LEFT,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CardTitle",
            parent=styles["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=10.5,
            leading=13,
            textColor=colors.HexColor("#16202c"),
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyCopy",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=15,
            textColor=colors.HexColor("#49576b"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallCopy",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#49576b"),
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="TinyCopy",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#49576b"),
            spaceAfter=3,
        )
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.6 * cm,
        leftMargin=1.6 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.4 * cm,
        title="SteamLoja Academica",
    )

    def make_table(df: pd.DataFrame, col_widths: list[float] | None = None, font_size: float = 8.0):
        table = Table(_table_data(df.reset_index()), repeatRows=1, colWidths=col_widths)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16202c")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), font_size),
                    ("LEADING", (0, 0), (-1, -1), font_size + 2),
                    ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d5c2ab")),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fffaf3")),
                    ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#16202c")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#fffaf3"), colors.HexColor("#f6efe2")]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return table

    def make_card(title: str, body: str, width: float):
        content = [
            Paragraph(title, styles["CardTitle"]),
            Paragraph(body, styles["SmallCopy"]),
        ]
        card = Table([[content]], colWidths=[width])
        card.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fffaf3")),
                    ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#d5c2ab")),
                    ("INNERPADDING", (0, 0), (-1, -1), 0),
                    ("LEFTPADDING", (0, 0), (-1, -1), 9),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        return card

    def make_info_table(title: str, description: str, df: pd.DataFrame, col_widths: list[float], font_size: float = 7.4):
        return [
            Paragraph(title, styles["SubsectionTitle"]),
            Paragraph(description, styles["BodyCopy"]),
            make_table(df, col_widths=col_widths, font_size=font_size),
            Spacer(1, 0.28 * cm),
        ]

    sales_table = sales_calendar.reset_index()
    customer_table = customer_profile.reset_index()
    access_table = store_access.reset_index()

    sales_metrics = [
        ("Vendas no mes", f"{int(sources.sales['units_sold'].sum()):,} jogos"),
        ("Faturamento do mes", f"R${float(sources.sales['revenue_brl'].sum()):,.0f}"),
        ("Genero de maior interesse", str(sources.customer_profile.groupby("genre", observed=False)["customer_share_pct"].mean().sort_values(ascending=False).index[0])),
        ("Turno de maior acesso", str(sources.store_access.groupby("shift", observed=False)["visits"].mean().sort_values(ascending=False).index[0])),
    ]
    metric_row = Table(
        [[Paragraph(f"<b>{label}</b><br/>{value}", styles["SmallCopy"]) for label, value in sales_metrics[:2]],
         [Paragraph(f"<b>{label}</b><br/>{value}", styles["SmallCopy"]) for label, value in sales_metrics[2:]]],
        colWidths=[doc.width / 2 - 0.2 * cm, doc.width / 2 - 0.2 * cm],
    )
    metric_row.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fffaf3")),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#d5c2ab")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#eadfce")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )

    external_cards = [
        make_card(
            "Migracao de plataforma",
            "Linux chegou a 5,33% da base Steam em marco de 2026, enquanto o Windows caiu para 92,33%. Dentro do grupo Linux, o SteamOS Holo ja representa 24,48%.",
            doc.width / 2 - 0.25 * cm,
        ),
        make_card(
            "Atrito com Windows",
            "O Windows 11 25H2 ja permite remover 26 aplicativos preinstalados por politica e a funcao Recall fica desabilitada por padrao em computadores gerenciados.",
            doc.width / 2 - 0.25 * cm,
        ),
        make_card(
            "Custo de hardware",
            "Memoria e armazenamento seguem pressionados em 2026, ao mesmo tempo em que a loja oficial mostra Steam Deck recondicionado como porta de entrada mais acessivel.",
            doc.width / 2 - 0.25 * cm,
        ),
        make_card(
            "Monetizacao e pirataria",
            "A pirataria ainda e massiva em escala global, e o impacto economico do crack e mais forte no comeco da vida comercial do jogo.",
            doc.width / 2 - 0.25 * cm,
        ),
    ]
    external_grid = Table(
        [[external_cards[0], external_cards[1]], [external_cards[2], external_cards[3]]],
        colWidths=[doc.width / 2 - 0.15 * cm, doc.width / 2 - 0.15 * cm],
        rowHeights=None,
    )
    external_grid.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))

    story = [
        Paragraph("TRABALHO DE GESTAO E GOVERNANCA DA INFORMACAO", styles["CoverKicker"]),
        Paragraph("SteamLoja Academica", styles["CoverTitle"]),
        Paragraph(
            "Apresentacao do trabalho sobre como dados operacionais de uma loja ficticia inspirada no ecossistema Steam podem virar informacoes gerenciais e sustentar decisoes estrategicas.",
            styles["BodyCopy"],
        ),
        Spacer(1, 0.25 * cm),
        metric_row,
        Spacer(1, 0.3 * cm),
        Paragraph(
            "Objetivo central: mostrar a passagem de dado bruto para leitura gerencial e, depois, para um plano de acao de 3 meses, 6 meses e 1 ano.",
            styles["BodyCopy"],
        ),
        Paragraph(
            "Base utilizada: operacao ficticia da SteamLoja combinada com sinais reais sobre SteamOS, Windows, custo de hardware e monetizacao.",
            styles["BodyCopy"],
        ),
        PageBreak(),
        Paragraph("Fase 1: Coleta e Organizacao", styles["SectionTitle"]),
        Paragraph(
            "Nesta etapa, a SteamLoja observa o funcionamento da operacao e organiza as fontes que depois serao transformadas em informacoes de apoio a decisao.",
            styles["BodyCopy"],
        ),
        Paragraph(str(methodology_note), styles["BodyCopy"]),
        Spacer(1, 0.12 * cm),
    ]

    story.extend(
        make_info_table(
            "Fonte 1: Vendas diarias do mes",
            "Tabela base das vendas por dia. Ela mostra o ritmo bruto da loja e ajuda a localizar picos e vales da operacao.",
            sales_table,
            [2.2 * cm] + [1.55 * cm] * 7,
            6.5,
        )
    )
    story.extend(
        make_info_table(
            "Fonte 2: Perfil de clientes por genero",
            "Tabela base do interesse do publico por genero ao longo da semana.",
            customer_table,
            [2.4 * cm] + [1.4 * cm] * 7,
            6.7,
        )
    )
    story.extend(
        make_info_table(
            "Fonte 3: Acessos por turno",
            "Tabela base dos acessos da loja por turno. Ela ajuda a localizar as janelas de maior exposicao.",
            access_table,
            [2.8 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm],
            8.0,
        )
    )
    story.extend(
        [
            Paragraph("Fontes externas de contexto estrategico", styles["SubsectionTitle"]),
            Paragraph(
                "Essas leituras externas nao substituem a operacao da loja. Elas servem para deixar o planejamento de medio e longo prazo menos refutavel.",
                styles["BodyCopy"],
            ),
            external_grid,
            PageBreak(),
            Paragraph("Fase 2: Processamento e Informacoes", styles["SectionTitle"]),
            Paragraph(
                "A partir das fontes da Fase 1, a SteamLoja transforma observacoes em 14 informacoes estrategicas: 10 internas da operacao e 4 externas de contexto.",
                styles["BodyCopy"],
            ),
        ]
    )

    for group_name, group_items in grouped_insights.items():
        story.append(Paragraph(group_name, styles["SubsectionTitle"]))
        for index, item in enumerate(group_items, start=1):
            story.append(
                Paragraph(
                    f"<b>{item['title']}</b><br/><b>Valor:</b> {item['value']}<br/><b>Por que isso importa:</b> {item['why']}<br/><b>O que fazer com isso:</b> {item['action']}<br/><b>Fonte:</b> {_format_source_suffix(item)}",
                    styles["SmallCopy"],
                )
            )
        story.append(Spacer(1, 0.08 * cm))

    story.extend(
        [
            Paragraph("Apoio complementar: monetizacao e pirataria", styles["SubsectionTitle"]),
        ]
    )
    for item in piracy_support:
        story.append(
            Paragraph(
                f"<b>{item['title']}</b><br/><b>Valor:</b> {item['value']}<br/><b>Leitura:</b> {item['why']}<br/><b>Uso no trabalho:</b> {item['action']}",
                styles["SmallCopy"],
            )
        )

    story.extend(
        [
            Spacer(1, 0.1 * cm),
            Paragraph("Ancoras de mercado Steam", styles["SubsectionTitle"]),
            Paragraph(f"Diferenca de preco mediano entre AAA e Indie: ${anchors['price_diff']:,.2f}", styles["SmallCopy"]),
            Paragraph(f"Participacao de jogos gratis no topo: {anchors['free_share_top']:.1f}%", styles["SmallCopy"]),
            Paragraph(f"Presenca de suporte Linux no topo: {anchors['linux_share_top']:.1f}%", styles["SmallCopy"]),
            Paragraph("Indicador composto de oportunidade", styles["SubsectionTitle"]),
            Paragraph(str(anchors["indicator_formula"]), styles["SmallCopy"]),
            PageBreak(),
            Paragraph("Fase 3: Planejamento Estrategico", styles["SectionTitle"]),
            Paragraph("Resumo executivo", styles["SubsectionTitle"]),
            Paragraph(str(strategy["summary"]), styles["BodyCopy"]),
        ]
    )

    for title, items in (
        ("Cronograma de 3 meses", strategy["three_months"]),
        ("Cronograma de 6 meses", strategy["six_months"]),
        ("Cronograma de 1 ano", strategy["one_year"]),
    ):
        story.append(Paragraph(title, styles["SubsectionTitle"]))
        for item in items:
            story.append(
                Paragraph(
                    f"<b>Fazer isso:</b> {item['do']}<br/><b>Por causa disso:</b> {item['because']}<br/><b>Impacto esperado:</b> {item['impact']}<br/><b>Base da decisao:</b> {item.get('supports', 'Leitura consolidada')}",
                    styles["SmallCopy"],
                )
            )

    story.extend(
        [
            Paragraph("Demandas e tarefas", styles["SubsectionTitle"]),
            Paragraph("Demandas: " + "; ".join(strategy["demands"]), styles["SmallCopy"]),
            Paragraph("Tarefas: " + "; ".join(strategy["tasks"]), styles["SmallCopy"]),
            Paragraph("Prioridades", styles["SubsectionTitle"]),
            Paragraph("; ".join(strategy["priorities"]), styles["SmallCopy"]),
            Paragraph("Riscos e contingencias", styles["SubsectionTitle"]),
            Paragraph("Riscos: " + "; ".join(strategy["risks"]), styles["SmallCopy"]),
            Paragraph("Contingencias: " + "; ".join(strategy["contingencies"]), styles["SmallCopy"]),
            Paragraph("3 acoes estrategicas principais", styles["SubsectionTitle"]),
        ]
    )
    for item in strategy["actions"]:
        story.append(
            Paragraph(
                f"<b>{item['title']}</b><br/><b>Proposta:</b> {item['do']}<br/><b>Justificativa:</b> {item['because']}<br/><b>Resultado esperado:</b> {item['impact']}",
                styles["SmallCopy"],
            )
        )

    story.extend(
        [
            Paragraph("Conexao com o mercado", styles["SubsectionTitle"]),
            Paragraph(str(strategy["market_connection"]), styles["BodyCopy"]),
            Paragraph("Hipotese futura nao priorizada", styles["SubsectionTitle"]),
            Paragraph("; ".join(strategy["future_opportunities"]), styles["SmallCopy"]),
            Paragraph("Aderencia as decisoes reais da Steam/Valve", styles["SubsectionTitle"]),
            Paragraph(
                "O trabalho se conecta ao mercado real ao usar sinais da propria Steam, do Windows e do custo de hardware para justificar o plano. "
                "Assim, o planejamento deixa de ser apenas opiniao e passa a ficar apoiado em fatos observaveis.",
                styles["BodyCopy"],
            ),
        ]
    )

    doc.build(story)
    return buffer.getvalue()
