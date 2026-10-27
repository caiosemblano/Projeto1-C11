# Projeto1-C11

Análise das dez perguntas sobre o Oscar para o projeto de Ciência de Dados com Python (C11), entrega 30/10. Dataset: [`unanimad/the-oscar-award`](https://www.kaggle.com/datasets/unanimad/the-oscar-award) (cerimônias 1928–2026). As cinco primeiras são o pitch de 10 minutos; as perguntas 6–10 completam a [`Proposta.md`](Proposta.md).

A lógica fica no pacote `projeto1_c11` (testável e reaproveitável). O notebook só narra e mostra os gráficos.

## Como rodar

```bash
uv sync --dev
uv run pytest
uv run projeto1-c11          # baixa o CSV (se preciso) e grava reports/figures/
```

Depois abra [`notebooks/analise_oscar.ipynb`](notebooks/analise_oscar.ipynb). A primeira execução baixa o dataset via KaggleHub e cacheia em `data/raw/` (gitignored). As PNGs em [`reports/figures/`](reports/figures/) entram no git para os slides.

## Arquitetura

```
src/projeto1_c11/
  data.py             carga + cache + limpeza
  categories.py       aliases de Melhor Filme e atuação, honorários, década
  plotting.py         estilo comum e save_fig
  questions/q01..q10  cada uma expõe QUESTION, compute(df), plot(result)
notebooks/analise_oscar.ipynb
reports/figures/q{01-10}_*.png
tests/                DataFrame sintético (remake, alias de BP, honorário, calendário)
```

`uv run projeto1-c11` chama `projeto1_c11.main()`: carrega, percorre `QUESTIONS` e grava as dez figuras.

## Limpeza dos dados

Três problemas da etapa de Descoberta (material do Slide 4):

1. **Padronização de categorias históricas.** `Outstanding Picture`, `Outstanding Production`, `Outstanding Motion Picture` e `Best Motion Picture` viram `BEST PICTURE`. `ACTOR`/`ACTRESS` viram as categorias principais modernas. Se o CSV trouxer `canon_category`, ela é a fonte; senão usa-se `category`.
2. **Valores ausentes.** Honorários e especiais (HONORARY, SPECIAL AWARD, Thalberg, Hersholt, etc.) frequentemente vêm sem `film`. As perguntas de filme/profissional excluem `is_honorary`. A flag olha a categoria original **e** a canônica, porque o dataset às vezes mapeia honorários antigos para categorias competitivas.
3. **Filmes homônimos.** A chave de filme é sempre `(film, year_ceremony)`, nunca só o título.

Outras decisões:

- década = `(year_ceremony // 10) * 10` em NumPy
- Q4 e Q6 ignoram filme internacional: em `FOREIGN` / `INTERNATIONAL FEATURE` o campo `name` é o país, não o profissional
- SPECIAL EFFECTS não é tratado como honorário (o marcador é `SPECIAL AWARD`, não qualquer `SPECIAL`)

## As dez perguntas

Cada módulo devolve um DataFrame; o gráfico é responsabilidade de `plot`.

| # | Módulo | O que calcula | Figura |
|---|---|---|---|
| 1 | `q01_conversao` | Por filme: indicações, vitórias, taxa. Pearson e Spearman (Spearman = Pearson dos postos, sem SciPy). Taxa média por faixa 1 / 2–3 / 4–6 / 7–9 / 10+. | Scatter com jitter + barras do “ponto de virada” |
| 2 | `q02_precursoras` | Só filmes **indicados** a Melhor Filme. Para cada categoria X: `P(X\|BP)`, `P(BP\|X)` e coeficiente φ (correlação entre duas binárias). | Barras horizontais ordenadas por φ |
| 3 | `q03_evolucao` | Por década: categorias distintas (nome original vs. cânone), indicações e vitórias por cerimônia. | Duas séries temporais |
| 4 | `q04_eficiencia` | Por `name`, ≥ 5 indicações competitivas: volume vs. `vitórias / indicações`. | Dois rankings (top 15) |
| 5 | `q05_concentracao` | Por cerimônia: quantos filmes distintos venceram e a fatia do mais premiado da noite; média móvel de 5 anos e média por década. | Série anual + barras por década |
| 6 | `q06_persistencia` | Por `name`: derrotas com `year_ceremony` estritamente anterior à primeira vitória, ou todas as indicações se nunca venceu. | Persistência premiada vs. injustiçados (top 15) |
| 7 | `q07_atuacao` | Nas quatro categorias de atuação: volume, vitórias, taxa e divisão principal/coadjuvante. | Recordistas de indicações (barras sobrepostas) e de estatuetas |
| 8 | `q08_nomenclatura` | Primeiro e último ano de cada nome original dentro da família canônica; conta quantos rótulos cada família já teve. | Linha do tempo (Gantt) das famílias que se modernizaram |
| 9 | `q09_elegibilidade` | Por cerimônia: `lag = year_ceremony − year_film`, salto de calendário e `offset = ano − 1927 − edição`. | Lag constante do CSV vs. mudança permanente de calendário |
| 10 | `q10_concorrentes` | Indicados a Melhor Filme por ano, `P(vitória) = 1/N`, e média de concorrentes nas demais categorias. | Tamanho da cédula e queda de 20% para 10% |

## O que os dados mostraram (dataset atual)

Números da última geração das figuras; mudam se o CSV do Kaggle for atualizado.

- **Q1.** Pearson 0,69 e Spearman 0,43 entre indicações e vitórias. A taxa média sobe com o volume e chega a **38% na faixa 10+** (n=107). Campeões no gráfico: *Titanic* (1998) e *Ben-Hur* (1960), 11 estatuetas. Maiores esnobados anotados: *The Color Purple* (1986) e *The Turning Point* (1978), 11 indicações e zero vitórias.
- **Q2.** Direção é a precursora clara (φ ≈ 0,68; 72% dos Melhor Filme também levam Direção). Em seguida, roteiro adaptado e montagem.
- **Q3.** A Academia se expande até meados do século e depois estabiliza em torno de 30 categorias canônicas. A linha dos nomes originais dispara nos anos 1970 — é o custo de não unificar rótulos históricos.
- **Q4.** Volume (MGM, Disney, John Williams) não é a mesma lista que eficiência (John Ford 4/5). *Star power* compra indicação com mais previsibilidade do que vitória.
- **Q5.** Hoje cerca de 14 filmes distintos levam pelo menos uma estatueta por noite. As décadas de 1940–50 concentram mais “noites de varredura”; o padrão recente é mais pulverizado.
- **Q6.** Victor Young acumulou 18 derrotas antes da única vitória (1939–1957); Randy Newman, 14; Roger Deakins, 11. Thomas Newman e Alex North chegaram a 14 indicações sem nunca vencer; Diane Warren, a 13.
- **Q7.** Meryl Streep lidera o volume de atuação (21 indicações, 3 vitórias); Katharine Hepburn lidera as estatuetas (12/4). Coadjuvante só aparece no quadro a partir da década de 1930.
- **Q8.** 19 famílias canônicas já trocaram de nome. Melhor Filme teve cinco rótulos (1928–hoje); atuação principal virou “in a Leading Role” em 1977; *Foreign Language Film* virou *International Feature Film* em 2020.
- **Q9.** O CSV padroniza `year_film = year_ceremony − 1` em 100% das linhas. O furo real é 1934: não houve cerimônia, o offset salta de 0 para 1 em 1935, e a Academia alinha o prêmio ao ano civil. A janela COVID-19 de 2021 **não** aparece no lag.
- **Q10.** De 1945 a 2009, Melhor Filme tem 5 indicados (20% de chance individual). Em 2010 a cédula vai a 10 (10%); oscila entre 8 e 10 até 2021 e fica fixa em 10 a partir de 2022. As demais categorias continuam em torno de 5 nomes (~20%).

## Testes

`tests/conftest.py` monta um Oscar em miniatura: alias `OUTSTANDING PICTURE`, remake de *Champ* em 1950 e 2020, honorário sem filme, profissional com 5 indicações, campeão tardio, injustiçado sem vitória, coadjuvante, e o salto de calendário 1933→1935. Os testes travam a unificação de Melhor Filme e de `ACTOR`, a chave `(film, year_ceremony)`, as contas de Q1–Q10 e o fato de SPECIAL EFFECTS não ser honorário.
