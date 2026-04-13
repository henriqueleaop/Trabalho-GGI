from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .paths import (
    DEFAULT_CONTEXT_HARDWARE_COST,
    DEFAULT_CONTEXT_PIRACY,
    DEFAULT_CONTEXT_PLATFORM_SHIFT,
    DEFAULT_CONTEXT_WINDOWS_FRICTION,
)


@dataclass(frozen=True)
class ContextSources:
    platform_shift: pd.DataFrame
    windows_friction: pd.DataFrame
    hardware_cost_pressure: pd.DataFrame
    piracy_pressure: pd.DataFrame


def _read_context_csv(path) -> pd.DataFrame:
    return pd.read_csv(path, dtype="string").fillna("")


def load_context_sources() -> ContextSources:
    return ContextSources(
        platform_shift=_read_context_csv(DEFAULT_CONTEXT_PLATFORM_SHIFT),
        windows_friction=_read_context_csv(DEFAULT_CONTEXT_WINDOWS_FRICTION),
        hardware_cost_pressure=_read_context_csv(DEFAULT_CONTEXT_HARDWARE_COST),
        piracy_pressure=_read_context_csv(DEFAULT_CONTEXT_PIRACY),
    )


def _metric_row(frame: pd.DataFrame, metric: str) -> pd.Series:
    return frame.loc[frame["metric"] == metric].iloc[0]


def build_context_overview_cards(context: ContextSources) -> list[dict[str, str]]:
    windows = _metric_row(context.platform_shift, "Participacao do Windows na Steam")
    linux = _metric_row(context.platform_shift, "Participacao do Linux na Steam")
    steamos = _metric_row(context.platform_shift, "Participacao do SteamOS Holo entre usuarios Linux da Steam")
    removable_apps = _metric_row(context.windows_friction, "Apps inbox configuraveis para remocao por politica no Windows 11 25H2")
    recall = _metric_row(context.windows_friction, "Recall em dispositivos gerenciados")
    consumer_dram = _metric_row(context.hardware_cost_pressure, "Consumer DRAM no 2Q26")
    nand = _metric_row(context.hardware_cost_pressure, "NAND Flash no 2Q26")
    steam_hardware = _metric_row(context.hardware_cost_pressure, "Steam Deck refurbished e Steam Machine listados na loja oficial")
    software_piracy = _metric_row(context.piracy_pressure, "Visitas globais a sites de pirataria de software")
    crack_first_week = _metric_row(context.piracy_pressure, "Perda media de receita com crack na primeira semana")

    return [
        {
            "title": "Fonte 4: migracao de plataforma",
            "body": (
                f"Em {linux['period']}, Linux chegou a {linux['value']} na base Steam e Windows caiu para {windows['value']}. "
                f"Dentro do recorte Linux, SteamOS Holo ja representa {steamos['value']}."
            ),
            "decision": "Esse conjunto sustenta iniciativas de divulgacao do SteamOS e de captura do usuario pelo ecossistema Valve.",
            "source_name": "Valve / Steam Hardware & Software Survey",
            "source_url": str(linux["source_url"]),
            "period": str(linux["period"]),
        },
        {
            "title": "Fonte 5: atrito com Windows",
            "body": (
                f"O Windows 11 25H2 ja permite remover {removable_apps['value']} por politica, "
                f"e o Recall fica {recall['value'].lower()} em dispositivos gerenciados."
            ),
            "decision": "A experiencia Windows virou tema de controle e simplificacao, abrindo espaco para uma plataforma focada em jogos.",
            "source_name": "Microsoft Learn",
            "source_url": str(removable_apps["source_url"]),
            "period": "2026",
        },
        {
            "title": "Fonte 6: custo de hardware",
            "body": (
                f"TrendForce projeta consumer DRAM em {consumer_dram['value']} e NAND em {nand['value']}. "
                f"Na loja oficial, o Steam Deck refurbished aparece com entrada em US$279 e a Steam Machine segue como coming soon."
            ),
            "decision": "Os sinais apontam para a necessidade de hardware proprio com politica comercial controlada e bundles mais inteligentes.",
            "source_name": "TrendForce + Steam Store",
            "source_url": str(steam_hardware["source_url"]),
            "period": "Mar/Abr 2026",
        },
        {
            "title": "Fonte 7: monetizacao e pirataria",
            "body": (
                f"A MUSO registrou {software_piracy['value']} visitas a pirataria de software em 2024, "
                f"enquanto cracks na primeira semana podem custar {crack_first_week['value']} de receita."
            ),
            "decision": "Isso reforca a importancia de capturar o usuario por conveniencia, biblioteca e hardware oficial, e nao apenas por DRM.",
            "source_name": "MUSO + Entertainment Computing",
            "source_url": str(software_piracy["source_url"]),
            "period": "2024-2025",
        },
    ]


def build_external_insights(context: ContextSources) -> list[dict[str, str]]:
    windows = _metric_row(context.platform_shift, "Participacao do Windows na Steam")
    linux = _metric_row(context.platform_shift, "Participacao do Linux na Steam")
    steamos = _metric_row(context.platform_shift, "Participacao do SteamOS Holo entre usuarios Linux da Steam")
    removable_apps = _metric_row(context.windows_friction, "Apps inbox configuraveis para remocao por politica no Windows 11 25H2")
    conventional_dram = _metric_row(context.hardware_cost_pressure, "Conventional DRAM no 2Q26")
    nand = _metric_row(context.hardware_cost_pressure, "NAND Flash no 2Q26")
    steam_hardware = _metric_row(context.hardware_cost_pressure, "Steam Deck refurbished e Steam Machine listados na loja oficial")

    return [
        {
            "group": "Mudanca de plataforma",
            "title": "Linux ganhou espaco enquanto Windows recuou na Steam",
            "value": f"Linux {linux['value']} | Windows {windows['value']}",
            "why": "A troca simultanea de participacao mostra que existe uma migracao relevante para fora do Windows dentro da base Steam.",
            "action": "Esse sinal justifica colocar SteamOS no centro da estrategia de medio prazo da SteamLoja.",
            "source_name": str(linux["source_name"]),
            "source_url": str(linux["source_url"]),
            "period": str(linux["period"]),
        },
        {
            "group": "Mudanca de plataforma",
            "title": "SteamOS Holo ja lidera o recorte Linux da Steam",
            "value": str(steamos["value"]),
            "why": "SteamOS Holo aparece como a distribuicao mais representativa no recorte Linux, mostrando tracao do ambiente controlado da Valve.",
            "action": "A SteamLoja pode defender colecoes e comunicacao SteamOS Ready com base em uma base instalada real.",
            "source_name": str(steamos["source_name"]),
            "source_url": str(steamos["source_url"]),
            "period": str(steamos["period"]),
        },
        {
            "group": "Atrito com Windows",
            "title": "Windows 11 25H2 reconhece a necessidade de enxugar a experiencia padrao",
            "value": f"{removable_apps['value']} removiveis por politica",
            "why": "A propria Microsoft criou uma politica especifica para remover apps inbox, o que mostra que simplificacao e controle viraram demanda concreta.",
            "action": "Esse dado sustenta a narrativa de que SteamOS entrega uma experiencia mais focada em jogo e menos carregada de atritos.",
            "source_name": str(removable_apps["source_name"]),
            "source_url": str(removable_apps["source_url"]),
            "period": str(removable_apps["period"]),
        },
        {
            "group": "Hardware e ecossistema",
            "title": "Memoria, storage e a vitrine oficial de hardware reforcam o valor de um ecossistema proprio e acessivel",
            "value": f"DRAM {conventional_dram['value']} | NAND {nand['value']}",
            "why": "A pressao de custo em memoria e armazenamento convive com uma estrategia oficial de entrada acessivel via Steam Deck refurbished e com Steam Machine listada como proximo passo do portfolio.",
            "action": "O plano de 1 ano deve priorizar bundle de hardware, financiamento leve e captura por ecossistema em vez de depender de aumento de taxa da loja.",
            "source_name": "TrendForce + Steam Store hardware catalog",
            "source_url": str(steam_hardware["source_url"]),
            "period": "Mar/Abr 2026",
        },
    ]


def build_piracy_support(context: ContextSources) -> list[dict[str, str]]:
    software_piracy = _metric_row(context.piracy_pressure, "Visitas globais a sites de pirataria de software")
    total_piracy = _metric_row(context.piracy_pressure, "Visitas globais totais a sites de pirataria")
    crack_first_week = _metric_row(context.piracy_pressure, "Perda media de receita com crack na primeira semana")
    crack_twelve_weeks = _metric_row(context.piracy_pressure, "Perda media apos 12 semanas sem crack")

    return [
        {
            "title": "Pirataria continua grande, mesmo em queda",
            "value": f"{software_piracy['value']} em software | {total_piracy['value']} no total",
            "why": "A demanda por acesso informal continua massiva em escala global, ainda que categorias maduras de acesso legal estejam reduzindo parte das visitas.",
            "action": "A SteamLoja deve competir por conveniencia e acesso integrado ao ecossistema, nao so por repressao.",
            "source_name": str(software_piracy["source_name"]),
            "source_url": str(software_piracy["source_url"]),
            "period": str(software_piracy["period"]),
        },
        {
            "title": "A janela inicial de monetizacao continua critica",
            "value": f"{crack_first_week['value']} na 1a semana | {crack_twelve_weeks['value']} apos 12 semanas",
            "why": "O impacto economico do crack e muito mais relevante no inicio do ciclo comercial do que no longo prazo.",
            "action": "Capturar usuario por SteamOS, Steam Deck e Steam Machine faz mais sentido estrategico do que apostar apenas em DRM persistente.",
            "source_name": str(crack_first_week["source_name"]),
            "source_url": str(crack_first_week["source_url"]),
            "period": "Publicacao 2025",
        },
    ]


def build_context_reference_table(context: ContextSources) -> pd.DataFrame:
    frames = [
        context.platform_shift,
        context.windows_friction,
        context.hardware_cost_pressure,
        context.piracy_pressure,
    ]
    table = pd.concat(frames, ignore_index=True)
    return table[["theme", "metric", "value", "change", "period", "source_name"]]
