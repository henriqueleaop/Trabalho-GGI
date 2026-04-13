# SteamLoja Academica

## Introducao

Este relatorio apresenta a SteamLoja como empresa ficticia inspirada no ecossistema Steam. O objetivo e mostrar a passagem de dado bruto para informacao gerencial e, depois, para planejamento estrategico.

## Fase 1: Coleta e Organizacao

Nesta etapa a SteamLoja apenas observa o funcionamento da operacao.

### Nota de metodologia

A camada academica foi modelada em grao detalhado e depois consolidada para apresentacao. O recorte inclui 193,935 pedidos, 110,487 sinais de perfil de cliente e 131,966 sessoes de acesso, distribuidos por pais, canal, campanha, dispositivo e genero.

### Fonte 1: Vendas diarias do mes

```text
weekday         Segunda          Terca         Quarta         Quinta           Sexta          Sabado        Domingo
Semana 1   Dia 2: 5,565   Dia 3: 4,691   Dia 4: 5,759   Dia 5: 5,814    Dia 6: 9,894   Dia 7: 11,595   Dia 1: 4,199
Semana 2   Dia 9: 5,746  Dia 10: 5,029  Dia 11: 5,608  Dia 12: 5,344   Dia 13: 9,175  Dia 14: 10,583   Dia 8: 4,152
Semana 3  Dia 16: 5,158  Dia 17: 4,797  Dia 18: 5,877  Dia 19: 5,931  Dia 20: 10,660  Dia 21: 12,409  Dia 15: 3,854
Semana 4  Dia 23: 5,191  Dia 24: 4,429  Dia 25: 6,251  Dia 26: 5,523   Dia 27: 9,641  Dia 28: 11,048  Dia 22: 4,559
Semana 5  Dia 30: 5,611  Dia 31: 4,774              -              -               -               -  Dia 29: 4,135
```

### Fonte 2: Perfil de clientes por genero

```text
genre    Action  Co-op  Indie    RPG  Simulation  Sports  Strategy
weekday                                                           
Segunda   26.13   9.20  16.20  20.26        9.71    7.07     11.43
Terca     26.00   9.11  17.08  19.25        9.85    7.05     11.66
Quarta    26.36   9.05  16.72  20.02        9.93    6.94     10.98
Quinta    26.12   8.88  17.21  20.46        9.56    6.57     11.21
Sexta     27.61  10.75  15.16  19.53        9.70    6.54     10.71
Sabado    27.97  10.48  14.62  20.18        9.68    6.49     10.58
Domingo   26.13   9.34  16.62  20.44        9.71    7.00     10.76
```

### Fonte 3: Acessos por turno

```text
shift    Manha  Tarde  Noite
weekday                     
Segunda   3588   5163   7619
Terca     3279   4913   6949
Quarta    3829   5593   8180
Quinta    3535   5444   7958
Sexta     4977   7862  11886
Sabado    5340   8532  13719
Domingo   2843   4469   6288
```

## Fase 2: Processamento e Insights

### 10 informacoes estrategicas

1. **Dia com maior media de vendas**: Sabado (11,409 jogos) - Sabado concentra a media mais alta de unidades vendidas no mes analisado. Acao sugerida: A janela de Sabado deve receber o principal destaque promocional da SteamLoja.
2. **Relacao entre o melhor e o pior dia**: 2.73x - A diferenca entre Sabado e Domingo confirma uma operacao com picos claros de demanda. Acao sugerida: Domingo deve ser tratado como prioridade para campanhas de reativacao e oferta de entrada.
3. **Peso de sexta e sabado nas vendas do mes**: 41.9% - O fechamento da semana concentra parte relevante da conversao total da loja. Acao sugerida: Vitrine, bundles e verba promocional precisam estar mais fortes nesse intervalo.
4. **Total vendido e media diaria**: 203,002 jogos | media 6,548 - Esse volume define a escala da operacao academica e cria uma base comparavel para ciclos futuros. Acao sugerida: A media diaria deve ser usada como referencia para metas e avaliacao de campanhas.
5. **Genero com maior interesse do publico**: Action (26.6%) - Esse genero lidera o interesse observado no comportamento semanal dos clientes. Acao sugerida: A curadoria comercial e a comunicacao principal devem priorizar jogos de Action.
6. **Participacao conjunta dos generos mais fortes**: 62.9% - Os tres generos lideres concentram a maior parte do interesse potencial de compra. Acao sugerida: Bundles, colecoes e campanhas tematicas devem partir dos generos mais fortes.
7. **Turno com maior volume de acessos**: Noite (8,943 acessos) - O fluxo de visitas fica mais intenso nesse turno e amplia o potencial de conversao. Acao sugerida: As atualizacoes centrais de vitrine devem ser publicadas na noite.
8. **Dia e turno de maior trafego**: Sabado / Noite - Essa e a janela de maior exposicao da SteamLoja na semana observada. Acao sugerida: Lancamentos, ofertas premium e banners principais devem estrear nesse pico.
9. **Janela de baixa demanda para reativacao**: Domingo / Manha - Esse ponto concentra o menor fluxo de acesso e representa o principal vale operacional. Acao sugerida: Cupom leve, bundle de entrada ou conteudo editorial devem ser testados nesse horario.
10. **Melhor combinacao comercial do recorte**: Sabado + Action + Noite - A combinacao reune o melhor dia de vendas, o genero dominante e o turno de maior trafego. Acao sugerida: A campanha principal deve ser organizada em Sabado, com foco em Action, no turno da noite.

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

A SteamLoja apresenta seu melhor desempenho comercial em Sabado, maior interesse do publico em Action e pico de visitas no turno da noite. O plano proposto busca reduzir o vale de Domingo / Manha sem comprometer a janela mais forte de conversao. Como referencia externa, o mercado Steam mostra diferenca de $37.50 entre AAA e Indie, com 16.8% de jogos gratuitos entre os titulos mais populares e 18.3% de suporte Linux nesse grupo.

### Cronograma de 3 meses
- Fazer isso: Reforcar a vitrine principal em Sabado, com foco na combinacao Sabado + Action + Noite. Por causa disso: Essa e a janela de maior demanda e concentracao de interesse do recorte analisado. Impacto esperado: A medida tende a elevar a conversao sem aumentar significativamente a complexidade operacional.
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
- **Vitrine principal no melhor combo comercial**: Concentrar a campanha principal em Sabado + Action + Noite. Essa combinacao une o melhor dia, o genero dominante e o turno de maior trafego. A expectativa e elevar a conversao nas janelas de maior retorno.
- **Curadoria alinhada ao ecossistema Valve**: Ampliar produtos e comunicacao ligados a Linux, SteamOS e Steam Deck. A Valve migrou de tentativas isoladas para um ecossistema integrado e hoje colhe resultado com o Steam Deck. Isso torna a SteamLoja mais atual, coerente e mais solida para a defesa academica.

### Conexao com o mercado
O plano posiciona a SteamLoja como uma empresa ficticia coerente com o mercado real. Ele aproveita a logica promocional da Steam, observa a forca do free-to-play, reconhece a distancia entre AAA e Indie e usa suporte Linux como sinal de proximidade com a estrategia de SteamOS e Steam Deck. O faturamento observado no mes-base foi de R$22,599,727, o que reforca a necessidade de proteger os dias fortes e recuperar os dias fracos.

## Aderencia as decisoes reais da Steam/Valve

- A leitura de Linux e SteamOS aproxima o trabalho da estrategia de plataforma aberta da Valve.
- O foco em eventos, weekly deals e bundles reflete a forma como a Steam organiza divulgacao e descoberta.
- A referencia a Steam Machine -> Steam Deck reforca que o ecossistema da Valve amadureceu de tentativa isolada para proposta integrada.
