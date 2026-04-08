# Steam Decision Dashboard

Aplicacao em Python para analise de jogos da Steam com foco academico nos tres niveis de decisao:

- Operacional: jogadores por hora e por dia da semana.
- Gerencial: preco, idade, genero, owners, reviews e comparativos de mercado.
- Estrategico: 10 insights automaticos e plano de 3, 6 e 12 meses.

O projeto usa um CSV grande de jogos como base principal e complementa isso com coleta ao vivo de jogadores atuais via Steam.

## O que a aplicacao entrega

- Dashboard em `Streamlit + Plotly`
- Pipeline para preparar o CSV bruto
- Coletor de CCU atual por jogo
- Relatorio academico em Markdown
- Testes unitarios das regras centrais

## Estrutura do projeto

- [app.py](/D:/_Projetos/Faculdade/Governanca/app.py): entrada do dashboard
- [scripts/prepare_dataset.py](/D:/_Projetos/Faculdade/Governanca/scripts/prepare_dataset.py): prepara a base analitica
- [scripts/collect_ccu.py](/D:/_Projetos/Faculdade/Governanca/scripts/collect_ccu.py): coleta jogadores atuais
- [scripts/generate_report.py](/D:/_Projetos/Faculdade/Governanca/scripts/generate_report.py): gera relatorio em Markdown
- [src/steam_dashboard/transform.py](/D:/_Projetos/Faculdade/Governanca/src/steam_dashboard/transform.py): limpeza, derivacoes e segmentacao
- [src/steam_dashboard/dashboard.py](/D:/_Projetos/Faculdade/Governanca/src/steam_dashboard/dashboard.py): interface e graficos
- [src/steam_dashboard/insights.py](/D:/_Projetos/Faculdade/Governanca/src/steam_dashboard/insights.py): insights, snapshot operacional e estrategia
- [tests](/D:/_Projetos/Faculdade/Governanca/tests): testes unitarios

## Requisitos

- Windows PowerShell
- Python 3.11+ instalado
- Arquivo CSV bruto de jogos

O projeto foi preparado para usar este arquivo como entrada principal:

```text
D:/Downloads/Copy of games.csv
```

## Instalacao

No diretório do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Se o PowerShell bloquear a ativacao da virtualenv:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

## Como rodar

### 1. Preparar a base analitica

Esse passo le o CSV bruto, corrige o schema do arquivo, cria colunas derivadas e separa os 20 apps monitorados.

```powershell
.\.venv\Scripts\python scripts/prepare_dataset.py --input "D:/Downloads/Copy of games.csv"
```

Saidas geradas:

- [games_processed.csv](/D:/_Projetos/Faculdade/Governanca/data/processed/games_processed.csv)
- [games_processed.parquet](/D:/_Projetos/Faculdade/Governanca/data/processed/games_processed.parquet)
- [monitor_candidates.csv](/D:/_Projetos/Faculdade/Governanca/data/processed/monitor_candidates.csv)

### 2. Coletar dados operacionais

#### Coleta rapida para demo

Boa para gerar historico no mesmo dia.

```powershell
.\.venv\Scripts\python scripts/collect_ccu.py --mode demo --iterations 6 --interval-seconds 300
```

#### Coleta curta para teste rapido

Boa para validar tudo sem esperar.

```powershell
.\.venv\Scripts\python scripts/collect_ccu.py --mode demo --iterations 4 --interval-seconds 2
```

#### Coleta academica por hora

Boa para montar historico mais defensavel para o trabalho.

```powershell
.\.venv\Scripts\python scripts/collect_ccu.py --mode academic --iterations 24
```

Saida gerada:

- [ccu_snapshots.csv](/D:/_Projetos/Faculdade/Governanca/data/monitoring/ccu_snapshots.csv)

### 3. Abrir o dashboard

```powershell
.\.venv\Scripts\streamlit run app.py
```

Depois abra:

```text
http://localhost:8501
```

## Como gerar o relatorio final

O projeto consegue gerar um resumo academico em Markdown com:

- resumo executivo
- 10 informacoes gerenciais
- radar de oportunidade
- monitoramento operacional
- estrategia de 3, 6 e 12 meses

Comando:

```powershell
.\.venv\Scripts\python scripts/generate_report.py
```

Saida:

- [steam_decision_report.md](/D:/_Projetos/Faculdade/Governanca/output/steam_decision_report.md)

## Como testar

```powershell
.\.venv\Scripts\python -m unittest discover -s tests
```

## Fluxo recomendado ponta a ponta

Se quiser rodar tudo do zero:

```powershell
.\.venv\Scripts\python scripts/prepare_dataset.py --input "D:/Downloads/Copy of games.csv"
.\.venv\Scripts\python scripts/collect_ccu.py --mode demo --iterations 4 --interval-seconds 2
.\.venv\Scripts\python scripts/generate_report.py
.\.venv\Scripts\streamlit run app.py
```

## Principais colunas derivadas

A base processada cria colunas que o dashboard usa diretamente:

- `release_year`
- `game_age_years`
- `owners_min`
- `owners_max`
- `owners_mid`
- `positive_ratio`
- `price_bucket`
- `is_free`
- `segment`
- `market_tier`
- `opportunity_score`

## Regras importantes do projeto

- `Indie`: jogo cujo campo de genero contem `Indie`
- `AAA`: jogo nao indie com `price >= 29.99` e `owners_mid >= 1_000_000`
- `Blockbuster F2P`: jogo gratis com base muito grande de owners
- `Other/Catalogo Geral`: restante do catalogo

## O que olhar no dashboard

- Aba `Resumo`: KPIs, tiers de mercado, owners por tier e radar de oportunidade
- Aba `Operacional`: linha do total monitorado, heatmap de horario, ranking e `CCU atual vs pico`
- Aba `Gerencial`: idade dos jogos mais jogados, preco `AAA vs Indie`, preco x popularidade e forca por genero
- Aba `Estrategico e Relatorio`: 10 insights automaticos e plano de 3, 6 e 12 meses

## Observacoes importantes

- O projeto nao depende de scraping do SteamDB.
- A coleta operacional usa o endpoint oficial `ISteamUserStats/GetNumberOfCurrentPlayers`.
- O CSV bruto usado neste projeto tem inconsistencias de schema no cabecalho. A leitura foi implementada de forma posicional para corrigir isso.
- Alguns jogos podem aparecer com `CCU atual > Peak CCU historico`. Isso indica que o dataset bruto pode estar desatualizado em alguns titulos, nao que o coletor esteja errado.
- Com poucos snapshots, a aba operacional ainda funciona, mas as conclusoes de horario e dia da semana ficam preliminares.

## Troubleshooting

### O dashboard abre mas nao mostra dados

Rode primeiro:

```powershell
.\.venv\Scripts\python scripts/prepare_dataset.py --input "D:/Downloads/Copy of games.csv"
```

### A aba Operacional aparece vazia

Rode o coletor:

```powershell
.\.venv\Scripts\python scripts/collect_ccu.py --mode demo --iterations 4 --interval-seconds 2
```

### O relatorio nao eh gerado

Confirme se existem:

- [games_processed.parquet](/D:/_Projetos/Faculdade/Governanca/data/processed/games_processed.parquet)
- [ccu_snapshots.csv](/D:/_Projetos/Faculdade/Governanca/data/monitoring/ccu_snapshots.csv)

Depois rode novamente:

```powershell
.\.venv\Scripts\python scripts/generate_report.py
```

### Os testes falham

Garanta que a virtualenv esta ativa e rode:

```powershell
.\.venv\Scripts\python -m unittest discover -s tests
```

## Estado validado

Esta implementacao ja foi executada localmente com sucesso em:

- preparo da base
- coleta operacional real
- subida do Streamlit
- geracao do relatorio
- testes unitarios
