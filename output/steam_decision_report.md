# SteamLoja Academica

## Introducao

Este relatorio apresenta a SteamLoja como empresa ficticia inspirada no ecossistema Steam. O objetivo e mostrar a passagem de dado bruto para informacao gerencial e, depois, para planejamento estrategico.

## Fase 1: Coleta e Organizacao

Nesta etapa a SteamLoja apenas observa o funcionamento da operacao.

### Nota de metodologia

A camada academica foi modelada em grao detalhado e depois consolidada para apresentacao. O recorte inclui 193,935 pedidos, 110,487 sinais de perfil de cliente e 131,966 sessoes de acesso, distribuidos por pais, canal, campanha, dispositivo e genero. Somam-se a isso 13 leituras externas reais sobre plataforma, Windows, custo de hardware e pirataria para sustentar o planejamento de medio e longo prazo.

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

### Fontes externas de contexto estrategico

```text
                  theme                                                                metric                                                     value                                     change                                         period                                         source_name
  Mudanca de plataforma                                      Participacao do Windows na Steam                                                    92.33%                                 -4.28 p.p.                                       Mar/2026            Steam Hardware & Software Survey (Valve)
  Mudanca de plataforma                                        Participacao do Linux na Steam                                                     5.33%                                 +3.10 p.p.                                       Mar/2026            Steam Hardware & Software Survey (Valve)
  Mudanca de plataforma            Participacao do SteamOS Holo entre usuarios Linux da Steam                                                    24.48%                                 +0.65 p.p.                                       Mar/2026 Steam Hardware & Software Survey Linux view (Valve)
     Atrito com Windows Apps inbox configuraveis para remocao por politica no Windows 11 25H2                                                   26 apps                 Suporte oficial de remocao                                           2026   Policy-based in-box app removal (Microsoft Learn)
     Atrito com Windows                                    Recall em dispositivos gerenciados                        Desabilitado e removido por padrao           Opt-in apenas quando TI permitir                                           2026                     Manage Recall (Microsoft Learn)
      Custo de hardware                                                 Consumer DRAM no 2Q26                                           +45% a +50% QoQ                             Alta projetada                                     07/04/2026                    TrendForce consumer DRAM outlook
      Custo de hardware                                             Conventional DRAM no 2Q26                                           +58% a +63% QoQ                             Alta projetada                                     31/03/2026                    TrendForce DRAM and NAND outlook
      Custo de hardware                                                    NAND Flash no 2Q26                                           +70% a +75% QoQ                             Alta projetada                                     31/03/2026                    TrendForce DRAM and NAND outlook
      Custo de hardware       Steam Deck refurbished e Steam Machine listados na loja oficial Steam Deck Refurbished US$279 | Steam Machine coming soon Entrada acessivel + ampliacao de portfolio                                       Abr/2026                Steam Store hardware catalog (Valve)
Monetizacao e pirataria                      Visitas globais a sites de pirataria de software                                                     14.9B                                      -2.1%                                           2024                MUSO 2024 Piracy Trends and Insights
Monetizacao e pirataria                           Visitas globais totais a sites de pirataria                                                    216.3B                                     -5.72%                                           2024                MUSO 2024 Piracy Trends and Insights
Monetizacao e pirataria                   Perda media de receita com crack na primeira semana                                                      ~20%             Impacto alto na janela inicial Artigo publicado em 2025 com amostra 2014-2022                 Volckmann - Entertainment Computing
Monetizacao e pirataria                                 Perda media apos 12 semanas sem crack                                                       ~0%                     Impacto residual baixo Artigo publicado em 2025 com amostra 2014-2022                 Volckmann - Entertainment Computing
```

## Fase 2: Processamento e Insights

### 14 informacoes estrategicas

1. **Dia com maior media de vendas**: Sabado (11,409 jogos) - Sabado concentra a media mais alta de unidades vendidas no mes analisado. Acao sugerida: A janela de Sabado deve receber o principal destaque promocional da SteamLoja. Fonte: Operacao SteamLoja (Mar/2026)
2. **Relacao entre o melhor e o pior dia**: 2.73x - A diferenca entre Sabado e Domingo confirma uma operacao com picos claros de demanda. Acao sugerida: Domingo deve ser tratado como prioridade para campanhas de reativacao e oferta de entrada. Fonte: Operacao SteamLoja (Mar/2026)
3. **Peso de sexta e sabado nas vendas do mes**: 41.9% - O fechamento da semana concentra parte relevante da conversao total da loja. Acao sugerida: Vitrine, bundles e verba promocional precisam estar mais fortes nesse intervalo. Fonte: Operacao SteamLoja (Mar/2026)
4. **Total vendido e media diaria**: 203,002 jogos | media 6,548 - Esse volume define a escala da operacao academica e cria uma base comparavel para ciclos futuros. Acao sugerida: A media diaria deve ser usada como referencia para metas e avaliacao de campanhas. Fonte: Operacao SteamLoja (Mar/2026)
5. **Genero com maior interesse do publico**: Action (26.6%) - Esse genero lidera o interesse observado no comportamento semanal dos clientes. Acao sugerida: A curadoria comercial e a comunicacao principal devem priorizar jogos de Action. Fonte: Operacao SteamLoja (Mar/2026)
6. **Participacao conjunta dos generos mais fortes**: 62.9% - Os tres generos lideres concentram a maior parte do interesse potencial de compra. Acao sugerida: Bundles, colecoes e campanhas tematicas devem partir dos generos mais fortes. Fonte: Operacao SteamLoja (Mar/2026)
7. **Turno com maior volume de acessos**: Noite (8,943 acessos) - O fluxo de visitas fica mais intenso nesse turno e amplia o potencial de conversao. Acao sugerida: As atualizacoes centrais de vitrine devem ser publicadas na noite. Fonte: Operacao SteamLoja (Mar/2026)
8. **Dia e turno de maior trafego**: Sabado / Noite - Essa e a janela de maior exposicao da SteamLoja na semana observada. Acao sugerida: Lancamentos, ofertas premium e banners principais devem estrear nesse pico. Fonte: Operacao SteamLoja (Mar/2026)
9. **Janela de baixa demanda para reativacao**: Domingo / Manha - Esse ponto concentra o menor fluxo de acesso e representa o principal vale operacional. Acao sugerida: Cupom leve, bundle de entrada ou conteudo editorial devem ser testados nesse horario. Fonte: Operacao SteamLoja (Mar/2026)
10. **Melhor combinacao comercial do recorte**: Sabado + Action + Noite - A combinacao reune o melhor dia de vendas, o genero dominante e o turno de maior trafego. Acao sugerida: A campanha principal deve ser organizada em Sabado, com foco em Action, no turno da noite. Fonte: Operacao SteamLoja (Mar/2026)
11. **Linux ganhou espaco enquanto Windows recuou na Steam**: Linux 5.33% | Windows 92.33% - A troca simultanea de participacao mostra que existe uma migracao relevante para fora do Windows dentro da base Steam. Acao sugerida: Esse sinal justifica colocar SteamOS no centro da estrategia de medio prazo da SteamLoja. Fonte: Steam Hardware & Software Survey (Valve) (Mar/2026)
12. **SteamOS Holo ja lidera o recorte Linux da Steam**: 24.48% - SteamOS Holo aparece como a distribuicao mais representativa no recorte Linux, mostrando tracao do ambiente controlado da Valve. Acao sugerida: A SteamLoja pode defender colecoes e comunicacao SteamOS Ready com base em uma base instalada real. Fonte: Steam Hardware & Software Survey Linux view (Valve) (Mar/2026)
13. **Windows 11 25H2 reconhece a necessidade de enxugar a experiencia padrao**: 26 apps removiveis por politica - A propria Microsoft criou uma politica especifica para remover apps inbox, o que mostra que simplificacao e controle viraram demanda concreta. Acao sugerida: Esse dado sustenta a narrativa de que SteamOS entrega uma experiencia mais focada em jogo e menos carregada de atritos. Fonte: Policy-based in-box app removal (Microsoft Learn) (2026)
14. **Memoria, storage e a vitrine oficial de hardware reforcam o valor de um ecossistema proprio e acessivel**: DRAM +58% a +63% QoQ | NAND +70% a +75% QoQ - A pressao de custo em memoria e armazenamento convive com uma estrategia oficial de entrada acessivel via Steam Deck refurbished e com Steam Machine listada como proximo passo do portfolio. Acao sugerida: O plano de 1 ano deve priorizar bundle de hardware, financiamento leve e captura por ecossistema em vez de depender de aumento de taxa da loja. Fonte: TrendForce + Steam Store hardware catalog (Mar/Abr 2026)

### Apoio de monetizacao e pirataria

- **Pirataria continua grande, mesmo em queda**: 14.9B em software | 216.3B no total - A demanda por acesso informal continua massiva em escala global, ainda que categorias maduras de acesso legal estejam reduzindo parte das visitas. Implicacao: A SteamLoja deve competir por conveniencia e acesso integrado ao ecossistema, nao so por repressao. Fonte: MUSO 2024 Piracy Trends and Insights (2024)
- **A janela inicial de monetizacao continua critica**: ~20% na 1a semana | ~0% apos 12 semanas - O impacto economico do crack e muito mais relevante no inicio do ciclo comercial do que no longo prazo. Implicacao: Capturar usuario por SteamOS, Steam Deck e Steam Machine faz mais sentido estrategico do que apostar apenas em DRM persistente. Fonte: Volckmann - Entertainment Computing (Publicacao 2025)

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

A SteamLoja segue com seu pico comercial em Sabado, interesse dominante em Action e maior trafego no turno da noite. A diferenca agora e que o plano de medio e longo prazo passa a se apoiar em sinais externos mais fortes: Linux chegou a 5.33% na Steam, Windows caiu para 92.33%, SteamOS Holo ja representa 24.48% do recorte Linux e o Windows 11 25H2 preve remocao de 26 apps. No hardware, a pressao de consumer DRAM (+45% a +50% QoQ), DRAM convencional (+58% a +63% QoQ) e NAND (+70% a +75% QoQ) se combina com uma entrada oficial mais acessivel (Steam Deck Refurbished US$279 | Steam Machine coming soon) e reforca a importancia de bundles e hardware proprio. Como referencia de mercado, AAA e Indie mantem distancia mediana de $37.50, com 16.8% de jogos gratuitos entre os titulos mais populares e 18.3% de suporte Linux nesse grupo.

### Cronograma de 3 meses
- Fazer isso: Reforcar a vitrine principal em Sabado, com foco na combinacao Sabado + Action + Noite. Por causa disso: Essa e a janela de maior demanda e concentracao de interesse do recorte analisado. Impacto esperado: A medida tende a elevar a conversao sem aumentar significativamente a complexidade operacional. Sustentado por: Infos 1, 8 e 10
- Fazer isso: Criar uma campanha de reativacao para Domingo / Manha. Por causa disso: Esse e o principal vale semanal de acesso e precisa ser tratado com prioridade. Impacto esperado: A acao reduz ociosidade e melhora a distribuicao das vendas ao longo da semana. Sustentado por: Infos 2 e 9
- Fazer isso: Organizar bundles simples por genero lider e ticket de entrada. Por causa disso: O publico demonstrou preferencia clara por poucos generos centrais. Impacto esperado: Isso tende a acelerar a decisao de compra e simplificar a comunicacao da loja. Sustentado por: Infos 5 e 6

### Cronograma de 6 meses
- Fazer isso: Investir na divulgacao do SteamOS com uma frente editorial e comercial chamada SteamOS Ready. Por causa disso: A migracao de base para Linux e o peso crescente do SteamOS Holo mostram que o ecossistema da Valve ja tem tracao real fora do Windows. Impacto esperado: A SteamLoja passa a capturar mais usuarios dentro do ecossistema Steam, com maior recorrencia e menor dependencia de plataformas concorrentes. Sustentado por: Infos 11 e 12
- Fazer isso: Criar colecoes, filtros e campanhas Steam Deck / Steam Machine / SteamOS Ready dentro da loja. Por causa disso: Quando a experiencia Windows exige simplificacao oficial e a busca por plataformas focadas em jogo aumenta, uma curadoria guiada por compatibilidade ganha valor comercial. Impacto esperado: Isso melhora conversao, reduz duvida de compra e reforca a identidade da SteamLoja como extensao do ecossistema Valve. Sustentado por: Infos 12 e 13
- Fazer isso: Padronizar a comunicacao da loja em torno de conveniencia, biblioteca unificada e experiencia mais limpa do que o PC gamer tradicional. Por causa disso: O recorte de plataforma mostra evasao relativa do Windows e abre espaco para posicionar SteamOS como ambiente mais focado em jogo. Impacto esperado: A marca da SteamLoja ganha um discurso mais coerente com a direcao atual da Valve e com a defesa academica. Sustentado por: Infos 11, 12 e 13

### Cronograma de 1 ano
- Fazer isso: Montar bundles de hardware proprio com Steam Deck, futura linha Steam Machine, credito de loja, gift cards e acessorios. Por causa disso: A alta de memoria e armazenamento pressiona o custo do PC tradicional, enquanto a loja oficial da Steam ja combina entrada acessivel via refurbished com expansao do catalogo de hardware. Impacto esperado: A SteamLoja passa a vender entrada no ecossistema, e nao apenas software, elevando receita por cliente e fidelizacao. Sustentado por: Info 14
- Fazer isso: Criar uma politica de acessibilidade para hardware com parcelamento, refurbished e combos de entrada. Por causa disso: Acessibilidade de hardware se torna argumento central num mercado em que DRAM e NAND pressionam o preco final do consumidor. Impacto esperado: A loja amplia alcance sem depender de aumento direto da taxa da plataforma, o que deixa a estrategia mais defensavel. Sustentado por: Info 14
- Fazer isso: Subsidiar parte do hardware pelo attach rate do ecossistema, e nao por uma assinatura centralizada. Por causa disso: Os dados observados sustentam melhor a captura por hardware, OS e biblioteca do que uma mudanca abrupta para um modelo tipo Game Pass. Impacto esperado: A SteamLoja preserva coerencia com a estrategia Valve e evita conflito prematuro entre assinatura, margem e venda unitaria. Sustentado por: Info 14 + apoio de pirataria

### Demandas e tarefas
- Aumentar vendas fora do pico de sexta e sabado.
- Transformar o crescimento de Linux e SteamOS em argumentacao comercial real da loja.
- Construir uma frente de hardware proprio acessivel sem depender de aumento de taxa como alavanca principal.
- Revisar semanalmente vendas, genero preferido e acessos por turno.
- Atualizar vitrine e bundles de acordo com o calendario promocional e com a colecao SteamOS Ready.
- Acompanhar mensalmente sinais de plataforma, custo de hardware e monetizacao para ajustar a estrategia.

### Prioridades
- Alta: ocupar a janela mais forte da semana e corrigir o principal vale operacional.
- Media: transformar SteamOS e compatibilidade com hardware Valve em pilar visivel de curadoria e divulgacao.
- Baixa: avaliar assinatura apenas como oportunidade futura, depois da consolidacao do ecossistema.

### Riscos e contingencias
- Risco comercial: insistir apenas em promocao de software e perder a onda de captura por ecossistema SteamOS e hardware.
- Risco operacional: comunicar hardware proprio sem politica clara de preco, bundle e reposicao.
- Risco estrategico: tentar forcar assinatura cedo demais e gerar conflito com a logica atual de ecossistema da Valve.
- Manter plano promocional alternativo para dias de baixa resposta.
- Trabalhar hardware com combos de entrada, refurbished e parcelamento antes de discutir expansao agressiva.
- Revisar trimestralmente o discurso de SteamOS e hardware com base em sinais reais de plataforma e custo.

### 3 acoes estrategicas principais
- **Campanhas de reativacao na janela fraca**: Ativar bundles leves e cupons em Domingo / Manha. Esse e o ponto mais fraco da semana em acesso e potencial de venda. A tendencia e reduzir o vale operacional e gerar receita incremental. Sustentado por: Infos 2 e 9
- **Divulgacao estruturada do SteamOS**: Lancar colecoes SteamOS Ready e guias de migracao suave para Steam Deck e Steam Machine. Linux cresceu na Steam, SteamOS Holo ganhou peso dentro desse recorte e o Windows passou a sinalizar mais atrito de experiencia. A SteamLoja fortalece captura de usuario dentro do ecossistema Valve e melhora a coerencia do plano de medio prazo. Sustentado por: Infos 11, 12 e 13
- **Hardware proprio com acesso comercial mais inteligente**: Estruturar bundles de Steam Deck e futura Steam Machine com credito de loja, acessorios e opcao de entrada acessivel. Memoria e storage ficaram mais caros, e a loja oficial da Steam ja sinaliza uma escada comercial que vai do refurbished ao hardware novo. A SteamLoja passa a capturar valor por ecossistema completo, e nao apenas por venda pontual de software. Sustentado por: Info 14

### Conexao com o mercado
O plano posiciona a SteamLoja como uma empresa ficticia coerente com o mercado real. No curto prazo, ele protege as melhores janelas de conversao da operacao. No medio prazo, transforma a migracao para Linux e o crescimento do SteamOS em argumento comercial concreto. No longo prazo, usa a pressao de custo em hardware e a ampliacao do catalogo Steam para defender bundles, acessibilidade e captura por ecossistema. O faturamento observado no mes-base foi de R$22,599,727, o que reforca a necessidade de ligar operacao, plataforma e hardware em uma mesma narrativa estrategica.

### Hipotese futura nao priorizada
- Assinatura tipo Game Pass fica como hipotese futura, nao como eixo principal do plano.
- Ela so deve ser reconsiderada depois que a base de hardware e a colecao SteamOS Ready estiverem mais maduras.

## Aderencia as decisoes reais da Steam/Valve

- A leitura de Linux e SteamOS aproxima o trabalho da estrategia de plataforma aberta da Valve.
- O foco em eventos, weekly deals e bundles reflete a forma como a Steam organiza divulgacao e descoberta.
- A referencia a Steam Machine -> Steam Deck reforca que o ecossistema da Valve amadureceu de tentativa isolada para proposta integrada.
