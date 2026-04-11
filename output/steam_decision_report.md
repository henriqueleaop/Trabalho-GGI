# SteamLoja Academica

## Introducao

Este relatorio apresenta a SteamLoja como empresa ficticia inspirada no ecossistema Steam. O objetivo e mostrar a passagem de dado bruto para informacao gerencial e, depois, para planejamento estrategico.

## Fase 1: Coleta e Organizacao

Nesta etapa a SteamLoja apenas observa o funcionamento da operacao.

### Fonte 1: Vendas diarias do mes

```text
weekday      Segunda       Terca      Quarta      Quinta       Sexta      Sabado     Domingo
Semana 1   Dia 2: 58   Dia 3: 23   Dia 4: 57   Dia 5: 31   Dia 6: 94   Dia 7: 79   Dia 1: 24
Semana 2   Dia 9: 62  Dia 10: 28  Dia 11: 55  Dia 12: 33  Dia 13: 91  Dia 14: 77   Dia 8: 15
Semana 3  Dia 16: 53  Dia 17: 21  Dia 18: 59  Dia 19: 26  Dia 20: 95  Dia 21: 70  Dia 15: 19
Semana 4  Dia 23: 45  Dia 24: 25  Dia 25: 48  Dia 26: 20  Dia 27: 92  Dia 28: 68  Dia 22: 27
Semana 5  Dia 30: 57  Dia 31: 27           -           -           -           -  Dia 29: 34
```

### Fonte 2: Perfil de clientes por genero

```text
genre    Action  Estrategia  Indie  RPG  Simulacao
weekday                                           
Segunda      43           5     20   24          8
Terca        41           5     21   25          8
Quarta       44           5     19   24          8
Quinta       42           5     20   25          8
Sexta        46           5     18   23          8
Sabado       47           5     18   22          8
Domingo      45           5     19   23          8
```

### Fonte 3: Acessos por turno

```text
shift    Manha  Tarde  Noite
weekday                     
Segunda    620    930   1280
Terca      540    880   1160
Quarta     660    980   1340
Quinta     590    910   1250
Sexta      840   1490   1980
Sabado     910   1650   2140
Domingo    430    770    980
```

## Fase 2: Processamento e Insights

### 10 informacoes estrategicas

1. **Dia com maior media de vendas**: Sexta (93.0 jogos) - Sexta apresenta o melhor desempenho medio de vendas no mes analisado. Acao sugerida: Recomenda-se concentrar campanhas de destaque e bundles em Sexta.
2. **Relacao entre o melhor e o pior dia**: 3.91x - Sexta vende significativamente mais do que Domingo, evidenciando uma operacao com picos bem definidos. Acao sugerida: Domingo deve ser tratado como janela prioritaria para acoes de reativacao e ofertas de entrada.
3. **Peso de sexta e sabado nas vendas do mes**: 44.0% - O fim da semana concentra uma parcela relevante da demanda da SteamLoja. Acao sugerida: A vitrine principal e o investimento promocional devem ser mais fortes nessa janela.
4. **Total vendido e media diaria**: 1,513 jogos | media 48.81 - Esse numero define a escala da operacao analisada e serve de referencia para metas e comparacoes futuras. Acao sugerida: A media diaria deve ser adotada como linha de base para avaliar o desempenho das proximas campanhas.
5. **Genero com maior interesse do publico**: Action (44.0%) - Esse genero aparece como preferencia dominante no perfil semanal de clientes. Acao sugerida: A comunicacao e a curadoria comercial devem dar maior destaque aos jogos de Action.
6. **Participacao conjunta dos generos mais fortes**: 87.0% - Os tres generos lideres concentram a maior parte do interesse comercial observado na semana. Acao sugerida: Catalogo, bundles e anuncios devem priorizar os generos com maior tracao.
7. **Turno com maior volume de acessos**: Noite (1447 acessos) - O horario noturno concentra mais visitas e tende a reunir maior potencial de conversao. Acao sugerida: As principais atualizacoes de vitrine e comunicacao devem ser programadas para a noite.
8. **Dia e turno de maior trafego**: Sabado / Noite - Essa e a janela de maior exposicao da SteamLoja na semana analisada. Acao sugerida: Esse pico deve receber lancamentos, bundles premium e o principal destaque de vitrine.
9. **Janela de baixa demanda para reativacao**: Domingo / Manha - Esse e o ponto mais fraco de acesso da semana e exige intervencao para reduzir o vale operacional. Acao sugerida: Vale testar cupom, oferta leve ou bundle de entrada nesse horario.
10. **Melhor combinacao comercial do recorte**: Sexta + Action + Noite - A combinacao reune o melhor dia de venda, o genero de maior interesse e o turno de maior trafego. Acao sugerida: A campanha principal da SteamLoja deve ser organizada em Sexta, no turno da noite, com foco em Action.

### Ancoras de mercado Steam

- Diferenca de preco mediano entre AAA e Indie: $37.50
- Participacao de jogos gratis no topo: 16.8%
- Presenca de suporte Linux no topo: 18.3%

### Jogos com maior potencial

- People Playground | Indie | Action | $0.99 | indicador 93.6 | Linux: Nao
- Zup! S | Indie | Casual | $0.59 | indicador 93.6 | Linux: Nao
- Zup! Z | Indie | Casual | $0.69 | indicador 93.4 | Linux: Nao
- Zup! 8 | Indie | Casual | $0.59 | indicador 93.3 | Linux: Nao
- Blood and Bacon | Catalogo Geral | Action | $0.59 | indicador 93.1 | Linux: Nao
- Fox Hime Zero | Indie | Adventure | $0.59 | indicador 93.1 | Linux: Nao
- Mirror | Indie | Adventure | $0.79 | indicador 93.0 | Linux: Nao
- Refunct | Indie | Adventure | $0.74 | indicador 92.6 | Linux: Nao

### Indicador composto de oportunidade

Indicador composto: combina base estimada de owners, aprovacao do publico, engajamento e acessibilidade de preco. Ele orienta a leitura comercial do catalogo, mas nao substitui avaliacao qualitativa.

## Fase 3: Planejamento Estrategico

### Resumo executivo

A SteamLoja apresenta seu melhor desempenho comercial em Sexta, maior interesse do publico em Action e pico de visitas no turno da noite. O plano proposto busca reduzir o vale de Domingo / Manha sem comprometer a janela mais forte de conversao. Como referencia externa, o mercado Steam mostra diferenca de $37.50 entre AAA e Indie, com 16.8% de jogos gratuitos entre os titulos mais populares e 18.3% de suporte Linux nesse grupo.

### Cronograma de 3 meses
- Fazer isso: Reforcar a vitrine principal em Sexta, com foco na combinacao Sexta + Action + Noite. Por causa disso: Essa e a janela de maior demanda e concentracao de interesse do recorte analisado. Impacto esperado: A medida tende a elevar a conversao sem aumentar significativamente a complexidade operacional.
- Fazer isso: Criar uma campanha de reativacao para Domingo / Manha. Por causa disso: Esse e o principal vale semanal de acesso e precisa ser tratado com prioridade. Impacto esperado: A acao reduz ociosidade e melhora a distribuicao das vendas ao longo da semana.
- Fazer isso: Organizar bundles simples por genero lider e ticket de entrada. Por causa disso: O publico demonstrou preferencia clara por poucos generos centrais. Impacto esperado: Isso tende a acelerar a decisao de compra e simplificar a comunicacao da loja.

### Cronograma de 6 meses
- Fazer isso: Criar rotina mensal de leitura de indicadores e ajuste de calendario promocional. Por causa disso: A operacao precisa transformar dados em decisao recorrente, e nao em analise eventual. Impacto esperado: A iniciativa melhora previsibilidade comercial e disciplina gerencial.
- Fazer isso: Ampliar a curadoria de jogos alinhados a Linux e SteamOS. Por causa disso: A Valve continua investindo em plataforma aberta e compatibilidade, especialmente apos o Steam Deck. Impacto esperado: Isso posiciona a SteamLoja mais perto das tendencias reais do ecossistema Steam.
- Fazer isso: Testar campanhas tematicas inspiradas em weekly deals e eventos sazonais. Por causa disso: A divulgacao da Steam se apoia em rituais promocionais recorrentes e de facil comunicacao. Impacto esperado: A medida tende a gerar previsibilidade de audiencia e aumentar lembranca de marca.

### Cronograma de 1 ano
- Fazer isso: Abrir uma frente comercial para hardware, gift cards e acessorios do ecossistema Steam. Por causa disso: A transicao de Steam Machine para Steam Deck mostra que a aderencia vem do ecossistema, nao de um produto isolado. Impacto esperado: A estrategia diversifica receita e fortalece a identidade da SteamLoja.
- Fazer isso: Evoluir o painel para monitoramento continuo com mais fontes do mercado Steam. Por causa disso: O trabalho atual demonstra valor, mas a maturidade depende de acompanhamento continuo. Impacto esperado: Isso permite planejamento anual com menos intuicao e mais evidencia.
- Fazer isso: Construir experiencias proprias de divulgacao, como calendario de eventos e recomendacoes editoriais. Por causa disso: A Steam nao depende apenas de preco, mas tambem de descoberta, comunidade e repertorio de vitrine. Impacto esperado: A medida fortalece diferenciacao competitiva e fidelizacao.

### Demandas e tarefas
- Aumentar vendas fora do pico de sexta e sabado.
- Melhorar o aproveitamento dos horarios com maior trafego.
- Ajustar catalogo e comunicacao ao interesse dominante do publico.
- Revisar semanalmente vendas, genero preferido e acessos por turno.
- Atualizar vitrine e bundles de acordo com o calendario promocional.
- Acompanhar evidencias de mercado Steam para validar o posicionamento da SteamLoja.

### Prioridades
- Alta: ocupar a janela mais forte com campanhas melhores e corrigir o principal vale da semana.
- Media: expandir curadoria e comunicacao para o genero lider e para produtos aderentes ao SteamOS.
- Baixa: abrir novas frentes de hardware e experiencias editoriais proprias.

### Riscos e contingencias
- Risco comercial: campanhas fracas em dias de pico desperdicam a melhor janela de conversao.
- Risco operacional: excesso de concentracao no fim da semana pode sobrecarregar suporte e atendimento.
- Risco estrategico: ignorar movimentos da Valve em Linux, SteamOS e Steam Deck afasta a loja das tendencias reais do mercado.
- Manter plano promocional alternativo para dias de baixa resposta.
- Reforcar suporte nos picos de sexta e sabado.
- Revisar trimestralmente o catalogo com base em aderencia ao ecossistema Steam.

### 3 acoes estrategicas principais
- **Campanhas de reativacao na janela fraca**: Ativar bundles leves e cupons em Domingo / Manha. Esse e o ponto mais fraco da semana em acesso e potencial de venda. A tendencia e reduzir o vale operacional e gerar receita incremental.
- **Vitrine principal no melhor combo comercial**: Concentrar a campanha principal em Sexta + Action + Noite. Essa combinacao une o melhor dia, o genero dominante e o turno de maior trafego. A expectativa e elevar a conversao nas janelas de maior retorno.
- **Curadoria alinhada ao ecossistema Valve**: Ampliar produtos e comunicacao ligados a Linux, SteamOS e Steam Deck. A Valve migrou de tentativas isoladas para um ecossistema integrado e hoje colhe resultado com o Steam Deck. Isso torna a SteamLoja mais atual, coerente e mais solida para a defesa academica.

### Conexao com o mercado
O plano posiciona a SteamLoja como uma empresa ficticia coerente com o mercado real. Ele aproveita a logica promocional da Steam, observa a forca do free-to-play, reconhece a distancia entre AAA e Indie e usa suporte Linux como sinal de proximidade com a estrategia de SteamOS e Steam Deck. O faturamento observado no mes-base foi de R$161,205, o que reforca a necessidade de proteger os dias fortes e recuperar os dias fracos.

## Aderencia as decisoes reais da Steam/Valve

- A leitura de Linux e SteamOS aproxima o trabalho da estrategia de plataforma aberta da Valve.
- O foco em eventos, weekly deals e bundles reflete a forma como a Steam organiza divulgacao e descoberta.
- A referencia a Steam Machine -> Steam Deck reforca que o ecossistema da Valve amadureceu de tentativa isolada para proposta integrada.
