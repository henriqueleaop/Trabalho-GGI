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


def build_pdf_report(context: dict[str, object]) -> bytes:
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "reportlab nao esta instalado. Rode `python -m pip install -r requirements.txt` para habilitar a exportacao em PDF."
        ) from exc

    insights = context["insights"]
    anchors = context["anchors"]
    strategy = context["strategy"]
    sales_calendar = context["sales_calendar"]
    customer_profile = context["customer_profile_table"]
    store_access = context["store_access_table"]
    methodology_note = context["methodology_note"]
    context_reference = context["context_reference_table"]
    piracy_support = context["piracy_support"]

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

    story = [
        Paragraph("SteamLoja Academica", styles["Title"]),
        Spacer(1, 0.2 * cm),
        Paragraph(
            "Relatorio academico sobre transformacao de dados operacionais em informacao gerencial e planejamento estrategico no contexto da SteamLoja.",
            styles["BodyCopy"],
        ),
        Spacer(1, 0.2 * cm),
        Paragraph("Fase 1: Coleta e Organizacao", styles["SectionTitle"]),
        Paragraph(str(methodology_note), styles["BodyCopy"]),
        Paragraph("Fonte 1: Vendas diarias do mes", styles["Heading4"]),
    ]

    for df in (sales_calendar, customer_profile, store_access):
        table = Table(_table_data(df.reset_index()), repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16202c")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("LEADING", (0, 0), (-1, -1), 10),
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
        story.append(table)
        story.append(Spacer(1, 0.22 * cm))
        if df is sales_calendar:
            story.append(Paragraph("Fonte 2: Perfil de clientes por genero", styles["Heading4"]))
        elif df is customer_profile:
            story.append(Paragraph("Fonte 3: Acessos por turno", styles["Heading4"]))

    story.extend(
        [
            Paragraph("Fontes externas de contexto estrategico", styles["Heading4"]),
        ]
    )
    context_table = Table(_table_data(context_reference.reset_index(drop=True)), repeatRows=1)
    context_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#16202c")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 7.5),
                ("LEADING", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#d5c2ab")),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fffaf3")),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.HexColor("#16202c")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#fffaf3"), colors.HexColor("#f6efe2")]),
            ]
        )
    )
    story.append(context_table)
    story.append(Spacer(1, 0.2 * cm))

    story.extend(
        [
            Spacer(1, 0.15 * cm),
            Paragraph("Fase 2: Processamento e Informacoes", styles["SectionTitle"]),
        ]
    )
    for index, item in enumerate(insights, start=1):
        story.append(
            Paragraph(
                f"<b>{index}. {item['title']}</b>: {item['value']}<br/>{item['why']}<br/><b>Implicacao gerencial:</b> {item['action']}<br/><b>Fonte:</b> {_format_source_suffix(item)}",
                styles["SmallCopy"],
            )
        )

    story.append(Paragraph("Apoio de monetizacao e pirataria", styles["Heading4"]))
    for item in piracy_support:
        story.append(
            Paragraph(
                f"<b>{item['title']}</b>: {item['value']}<br/>{item['why']}<br/><b>Implicacao:</b> {item['action']}<br/><b>Fonte:</b> {item['source_name']} ({item['period']})",
                styles["SmallCopy"],
            )
        )

    story.extend(
        [
            Spacer(1, 0.12 * cm),
            Paragraph("Ancoras de mercado Steam", styles["Heading4"]),
            Paragraph(f"Diferenca de preco mediano entre AAA e Indie: ${anchors['price_diff']:,.2f}", styles["SmallCopy"]),
            Paragraph(f"Participacao de jogos gratis no topo: {anchors['free_share_top']:.1f}%", styles["SmallCopy"]),
            Paragraph(f"Presenca de suporte Linux no topo: {anchors['linux_share_top']:.1f}%", styles["SmallCopy"]),
            Paragraph("Indicador composto de oportunidade", styles["Heading4"]),
            Paragraph(str(anchors["indicator_formula"]), styles["SmallCopy"]),
            Paragraph("Fase 3: Planejamento Estrategico", styles["SectionTitle"]),
            Paragraph("Resumo executivo", styles["Heading4"]),
            Paragraph(str(strategy["summary"]), styles["BodyCopy"]),
        ]
    )

    for title, items in (
        ("Cronograma de 3 meses", strategy["three_months"]),
        ("Cronograma de 6 meses", strategy["six_months"]),
        ("Cronograma de 1 ano", strategy["one_year"]),
    ):
        story.append(Paragraph(title, styles["Heading4"]))
        for item in items:
            story.append(
                Paragraph(
                    f"<b>Fazer isso:</b> {item['do']}<br/><b>Por causa disso:</b> {item['because']}<br/><b>Impacto esperado:</b> {item['impact']}<br/><b>Sustentado por:</b> {item.get('supports', 'Leitura consolidada')}",
                    styles["SmallCopy"],
                )
            )

    story.append(Paragraph("Demandas, prioridades e riscos", styles["Heading4"]))
    for bucket in (
        ("Demandas", strategy["demands"]),
        ("Tarefas", strategy["tasks"]),
        ("Prioridades", strategy["priorities"]),
        ("Riscos", strategy["risks"]),
        ("Contingencias", strategy["contingencies"]),
    ):
        story.append(Paragraph(f"<b>{bucket[0]}:</b> " + "; ".join(bucket[1]), styles["SmallCopy"]))

    story.append(Paragraph("3 acoes estrategicas principais", styles["Heading4"]))
    for item in strategy["actions"]:
        story.append(
            Paragraph(
                f"<b>{item['title']}</b><br/><b>Proposta:</b> {item['do']}<br/><b>Justificativa:</b> {item['because']}<br/><b>Resultado esperado:</b> {item['impact']}",
                styles["SmallCopy"],
            )
        )

    story.extend(
        [
            Paragraph("Conexao com o mercado", styles["Heading4"]),
            Paragraph(str(strategy["market_connection"]), styles["BodyCopy"]),
            Paragraph("Hipotese futura nao priorizada", styles["Heading4"]),
            Paragraph("; ".join(strategy["future_opportunities"]), styles["SmallCopy"]),
            Paragraph("Aderencia as decisoes reais da Steam/Valve", styles["Heading4"]),
            Paragraph(
                "A leitura de Linux e SteamOS aproxima o trabalho da estrategia de plataforma aberta da Valve. "
                "O foco em eventos, ofertas recorrentes e combos reflete a forma como a Steam organiza divulgacao e descoberta. "
                "A referencia a Steam Machine -> Steam Deck reforca o amadurecimento do ecossistema da Valve.",
                styles["BodyCopy"],
            ),
        ]
    )

    doc.build(story)
    return buffer.getvalue()
