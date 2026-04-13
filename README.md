# SteamLoja Acadêmica

Projeto acadêmico em Python que transforma dados operacionais e sinais reais do ecossistema Steam em informações gerenciais e planejamento estratégico.

O trabalho foi estruturado para uma empresa fictícia chamada `SteamLoja`, inspirada na operação de venda de jogos, bundles, DLCs e produtos do ecossistema Steam. A aplicação mostra, de forma visual e defensável, como um conjunto de dados brutos evolui para insights e, depois, para ações estratégicas.

## Contexto do trabalho

Este projeto foi desenvolvido para a disciplina de `Gestão e Governança da Informação`, com foco no desafio dos três níveis de decisão:

- `Fase 1: Coleta e Organização`
- `Fase 2: Processamento e Insights`
- `Fase 3: Planejamento Estratégico`

O objetivo central é demonstrar:

- o que são dados operacionais
- como esses dados se transformam em informação gerencial
- como a informação gerencial sustenta decisões estratégicas

## Visão geral da solução

A solução combina duas camadas de dados:

- `Dados reais`: base de jogos Steam já processada, usada como evidência de mercado.
- `Dados fictícios, mas defensáveis`: base acadêmica da SteamLoja com vendas diárias, perfil de clientes por gênero e acessos por turno.
- `Dados fictícios, mas defensáveis`: base acadêmica da SteamLoja modelada em grão detalhado e consolidada no app para apresentação.

Com isso, o projeto não depende só de simulação. Ele usa uma narrativa acadêmica clara, mas se ancora em sinais que realmente fazem sentido no ecossistema Steam e na estratégia histórica da Valve.

O sistema entrega:

- dashboard em `Streamlit + Plotly`
- base acadêmica para a SteamLoja
- pipeline para preparar a base real de jogos Steam
- relatório acadêmico em Markdown
- testes unitários para regras de negócio e geração dos dados centrais

## O que é real e o que é fictício

### Dados reais

Os dados reais do projeto representam a camada de mercado Steam:

- arquivo bruto de jogos em `D:/Downloads/Copy of games.csv`
- base processada com:
  - preço
  - data de lançamento
  - owners estimados
  - Peak CCU
  - reviews positivas e negativas
  - playtime
  - gêneros
  - suporte a Windows, Mac e Linux

Esses dados sustentam análises de mercado como:

- diferença de preço entre `AAA` e `Indie`
- participação de jogos grátis entre títulos mais populares
- presença de suporte Linux como proxy de aderência a `SteamOS`
- leitura de oportunidades comerciais por catálogo

### Dados fictícios

Os dados fictícios do projeto representam a operação da `SteamLoja`, mas nao foram preenchidos manualmente em tabelas pequenas. Eles sao simulados com logica operacional de escala e depois consolidados no dashboard:

- `daily_sales_month.csv`
  - pedidos detalhados do mês-base
  - data e horario do pedido
  - pais, regiao e canal
  - tipo de campanha
  - genero, segmento e tipo de produto
  - unidades, preco, desconto e faturamento
- `customer_genre_profile_week.csv`
  - sinais detalhados de perfil de cliente em uma semana
  - pais, plataforma, canal de aquisicao e tipo de cliente
  - genero preferido, wishlist, carrinho e intencao de compra
- `store_access_shift_week.csv`
  - sessoes detalhadas de acesso ao longo da semana
  - dia, turno, pais, dispositivo, origem de trafego e superficie de entrada
  - minutos de sessao, paginas vistas e acoes de wishlist/carrinho

Esses dados são fictícios, mas foram construídos para serem:

- simples
- coerentes com o enunciado do trabalho
- alinhados a padrões plausíveis do mercado Steam
- defensáveis em apresentação

Na prática, isso significa:

- milhares de pedidos por dia, em vez de dezenas de vendas artificiais
- picos mais fortes em `Sexta` e `Sabado`
- maior intensidade de acesso no turno da `Noite`
- predominio de `Action`, com variacao real entre dias e canais
- distribuicao internacional com peso maior para `Brasil`, `Estados Unidos` e Europa
- campanhas, bundles, dispositivos e canais com impacto real no resultado agregado

## Por que a estratégia híbrida foi escolhida

Se o projeto usasse apenas dados fictícios, ele ficaria mais fácil de montar, mas mais frágil para defender.

Se usasse apenas dados reais da Steam, ficaria tecnicamente interessante, mas perderia aderência direta ao enunciado acadêmico da SteamLoja.

Por isso a estratégia híbrida foi adotada:

- a operação da SteamLoja é mostrada com dados claros, objetivos e controlados
- a camada de mercado Steam valida que o planejamento conversa com decisões reais da Valve e com a dinâmica do setor

## Fases do trabalho

## Fase 1: Coleta e Organização

Nesta fase, o sistema mostra o quadro de dados brutos da SteamLoja.

As três fontes principais são:

1. `Vendas diárias do mês`
2. `Perfil de clientes por gênero`
3. `Acessos por turno`

O foco aqui é observação do funcionamento da operação, não decisão.

O dashboard apresenta:

- tabela de vendas diárias do mês
- gráfico de vendas diárias
- tabela e gráfico do perfil de clientes por gênero
- tabela e heatmap dos acessos por turno

## Fase 2: Processamento e Insights

Nesta fase, os dados deixam de ser apenas observados e passam a ser interpretados.

O painel gera `10 informações estratégicas`, agrupadas em:

- vendas
- clientes
- acessos e comportamento

Exemplos:

- dia com maior média de vendas
- peso do fim de semana nas vendas do mês
- gênero com maior interesse do público
- turno com maior volume de acessos
- janela de baixa demanda para reativação
- melhor combinação comercial do recorte

Depois disso, o sistema adiciona `âncoras de mercado Steam`, como:

- diferença de preço entre AAA e Indie
- participação de jogos grátis no topo
- presença de suporte Linux entre os títulos mais fortes

Esses sinais ajudam a mostrar que o planejamento da SteamLoja não foi construído isoladamente.

## Fase 3: Planejamento Estratégico

Nesta fase, os insights são transformados em plano de ação.

O sistema organiza:

- resumo executivo
- cronograma de `3 meses`
- cronograma de `6 meses`
- cronograma de `1 ano`
- demandas e tarefas
- prioridades
- riscos e contingências
- 3 ações estratégicas principais
- conexão com o mercado

Cada ação estratégica segue a lógica:

- `Fazer isso`
- `Por causa disso`
- `Impacto esperado`

## Como os resultados agregam valor

### Valor operacional

Os dados operacionais da SteamLoja ajudam a entender:

- quando a loja vende mais
- quando a loja recebe mais acessos
- quais janelas têm menor tração
- onde concentrar comunicação, vitrine e campanhas

### Valor gerencial

Os insights ajudam a decidir:

- quais dias merecem maior investimento promocional
- quais gêneros devem ter mais destaque
- quais turnos devem receber campanhas principais
- quais momentos exigem reativação comercial

### Valor estratégico

O plano final ajuda a justificar:

- ajustes rápidos de curto prazo
- consolidação de processo no médio prazo
- expansão de posicionamento e ecossistema no longo prazo

### Aderência ao ecossistema Steam/Valve

O trabalho foi pensado para dialogar com tendências e decisões que fazem sentido no mundo Steam:

- uso de promoções e bundles como lógica de divulgação
- observação de jogos grátis e modelos de entrada
- leitura de Linux como aproximação com `SteamOS`
- referência ao amadurecimento do ecossistema `Steam Machine -> Steam Deck`

## Como foi feito

O projeto foi implementado em Python com a seguinte lógica:

- leitura e preparação da base real de jogos Steam
- geracao deterministica de uma base academica propria para a SteamLoja
- consolidação das duas camadas no dashboard
- geração de relatório acadêmico em Markdown
- exportacao do relatorio em PDF
- validação por testes automatizados

Tecnologias usadas:

- `Python`
- `pandas`
- `Streamlit`
- `Plotly`
- `pyarrow`
- `requests`

## Estrutura do código

Arquivos principais:

- [app.py](/D:/_Projetos/Faculdade/Governanca/app.py)
  - ponto de entrada da aplicação
- [src/steam_dashboard/dashboard.py](/D:/_Projetos/Faculdade/Governanca/src/steam_dashboard/dashboard.py)
  - interface principal, tema visual, sidebar e renderização das três fases
- [src/steam_dashboard/academic.py](/D:/_Projetos/Faculdade/Governanca/src/steam_dashboard/academic.py)
  - carga das bases acadêmicas detalhadas, agregação para o dashboard, geração dos 10 insights, âncoras de mercado e plano estratégico
- [src/steam_dashboard/transform.py](/D:/_Projetos/Faculdade/Governanca/src/steam_dashboard/transform.py)
  - preparação da base real de jogos Steam
- [src/steam_dashboard/insights.py](/D:/_Projetos/Faculdade/Governanca/src/steam_dashboard/insights.py)
  - lógica de insights e apoio analítico herdada da camada de mercado
- [src/steam_dashboard/paths.py](/D:/_Projetos/Faculdade/Governanca/src/steam_dashboard/paths.py)
  - caminhos padrão do projeto
- [src/steam_dashboard/reporting.py](/D:/_Projetos/Faculdade/Governanca/src/steam_dashboard/reporting.py)
  - montagem do contexto do relatório, saída em Markdown e exportação em PDF
- [scripts/prepare_dataset.py](/D:/_Projetos/Faculdade/Governanca/scripts/prepare_dataset.py)
  - prepara a base real
- [scripts/generate_academic_data.py](/D:/_Projetos/Faculdade/Governanca/scripts/generate_academic_data.py)
  - gera as bases fictícias detalhadas da SteamLoja com seed fixa
- [scripts/generate_report.py](/D:/_Projetos/Faculdade/Governanca/scripts/generate_report.py)
  - gera o relatório final em Markdown e PDF

Diretórios de dados:

- [data/academic](/D:/_Projetos/Faculdade/Governanca/data/academic)
  - dados fictícios da SteamLoja
- [data/processed](/D:/_Projetos/Faculdade/Governanca/data/processed)
  - dados reais processados da Steam
- [data/monitoring](/D:/_Projetos/Faculdade/Governanca/data/monitoring)
  - histórico de coleta operacional de CCU

## Requisitos

- Windows com PowerShell
- Python `3.11` ou superior
- CSV bruto de jogos Steam disponível em:

```text
D:/Downloads/Copy of games.csv
```

## Dependências

As dependências estão em [requirements.txt](/D:/_Projetos/Faculdade/Governanca/requirements.txt):

- `pandas`
- `plotly`
- `pyarrow`
- `requests`
- `reportlab`
- `streamlit`

## Setup local completo

No diretório do projeto:

```powershell
cd D:\_Projetos\Faculdade\Governanca
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Se o PowerShell bloquear a ativação da virtualenv:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

## Como rodar o trabalho

### 1. Preparar a base real da Steam

```powershell
.\.venv\Scripts\python scripts/prepare_dataset.py --input "D:/Downloads/Copy of games.csv"
```

Saídas:

- [games_processed.csv](/D:/_Projetos/Faculdade/Governanca/data/processed/games_processed.csv)
- [games_processed.parquet](/D:/_Projetos/Faculdade/Governanca/data/processed/games_processed.parquet)
- [monitor_candidates.csv](/D:/_Projetos/Faculdade/Governanca/data/processed/monitor_candidates.csv)

### 2. Gerar ou regenerar a base acadêmica da SteamLoja

```powershell
.\.venv\Scripts\python scripts/generate_academic_data.py
```

Saídas:

- [daily_sales_month.csv](/D:/_Projetos/Faculdade/Governanca/data/academic/daily_sales_month.csv)
- [customer_genre_profile_week.csv](/D:/_Projetos/Faculdade/Governanca/data/academic/customer_genre_profile_week.csv)
- [store_access_shift_week.csv](/D:/_Projetos/Faculdade/Governanca/data/academic/store_access_shift_week.csv)

### 3. Gerar o relatório acadêmico

```powershell
.\.venv\Scripts\python scripts/generate_report.py --with-pdf
```

Saída:

- [steam_decision_report.md](/D:/_Projetos/Faculdade/Governanca/output/steam_decision_report.md)
- [steamloja_academica.pdf](/D:/_Projetos/Faculdade/Governanca/output/pdf/steamloja_academica.pdf)

### 4. Abrir o dashboard

```powershell
.\.venv\Scripts\streamlit run app.py
```

Depois abra no navegador:

```text
http://localhost:8501
```

Se a porta `8501` estiver ocupada:

```powershell
.\.venv\Scripts\streamlit run app.py --server.port 8502
```

## Como executar testes

```powershell
.\.venv\Scripts\python -m unittest discover -s tests
```

## Fluxo recomendado ponta a ponta

```powershell
cd D:\_Projetos\Faculdade\Governanca
.\.venv\Scripts\Activate.ps1
.\.venv\Scripts\python scripts/prepare_dataset.py --input "D:/Downloads/Copy of games.csv"
.\.venv\Scripts\python scripts/generate_academic_data.py
.\.venv\Scripts\python scripts/generate_report.py --with-pdf
.\.venv\Scripts\streamlit run app.py
```

## O que observar no dashboard

### Fase 1: Coleta e Organização

Observe:

- quadro de vendas diárias
- perfil de clientes por gênero
- acessos por turno

Pergunta principal:

- como a operação funciona antes da interpretação?

### Fase 2: Processamento e Insights

Observe:

- 10 informações estratégicas
- gráficos resumindo vendas, clientes e acessos
- âncoras de mercado Steam

Pergunta principal:

- o que os dados significam e quais decisões eles sugerem?

### Fase 3: Planejamento Estratégico

Observe:

- cronograma de 3, 6 e 12 meses
- demandas, prioridades e riscos
- ações principais
- conexão com o mercado

Pergunta principal:

- como transformar leitura de dados em ação?

## Limitações e observações importantes

- A SteamLoja é uma empresa fictícia.
- A base acadêmica da loja foi simulada para fins de apresentação e defesa, mas segue regras de distribuição plausíveis para uma operação grande.
- A base de jogos Steam é real, mas representa uma fotografia de mercado do arquivo utilizado.
- O projeto não depende de scraping do SteamDB.
- O CSV bruto da Steam possui inconsistências de schema; por isso a leitura da base real foi implementada de forma posicional.
- O indicador composto de oportunidade é heurístico e serve para apoio analítico, não para decisão isolada.
- Os CSVs acadêmicos agora estão em grão detalhado; o dashboard consolida esses eventos para manter a leitura simples nas três fases.

## Troubleshooting

### O app não abre

Confirme se a base real foi preparada:

```powershell
.\.venv\Scripts\python scripts/prepare_dataset.py --input "D:/Downloads/Copy of games.csv"
```

### O relatório não é gerado

Confirme se existe a base processada:

- [games_processed.parquet](/D:/_Projetos/Faculdade/Governanca/data/processed/games_processed.parquet)

Depois rode novamente:

```powershell
.\.venv\Scripts\python scripts/generate_academic_data.py
.\.venv\Scripts\python scripts/generate_report.py --with-pdf
```

### A porta 8501 está ocupada

Use outra porta:

```powershell
.\.venv\Scripts\streamlit run app.py --server.port 8502
```

### Os testes falham

Garanta que a virtualenv está ativa e rode:

```powershell
.\.venv\Scripts\python -m unittest discover -s tests
```

## Estado validado localmente

Esta versão já foi validada localmente com:

- compilação do projeto
- testes unitários
- geração do relatório em Markdown
- renderização do dashboard via `AppTest`
- subida real do Streamlit em ambiente local

## Resumo final

Este repositório entrega um trabalho acadêmico completo sobre a `SteamLoja`, unindo:

- observação operacional
- interpretação gerencial
- planejamento estratégico
- aderência ao mercado real da Steam

O resultado final foi pensado para ser:

- simples de entender
- forte para apresentação
- coerente com o enunciado
- defensável em sala
