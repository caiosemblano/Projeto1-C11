# Projeto1-C11

Análise das cinco perguntas estratégicas do pitch de Ciência de Dados com Python (C11), entrega 30/10. Dataset: [`unanimad/the-oscar-award`](https://www.kaggle.com/datasets/unanimad/the-oscar-award) (cerimônias 1928–2026).

A lógica fica no pacote `projeto1_c11` (testável e reaproveitável). O notebook só narra e mostra os gráficos. As perguntas 6–10 de [`Proposta.md`](Proposta.md) ainda não foram implementadas; a arquitetura aceita um arquivo novo por pergunta.

## Como rodar

```bash
uv sync --dev
uv run pytest
uv run projeto1-c11          # baixa o CSV (se preciso) e grava reports/figures/
```

Depois abra [`notebooks/analise_top5.ipynb`](notebooks/analise_top5.ipynb). A primeira execução baixa o dataset via KaggleHub e cacheia em `data/raw/` (gitignored). As PNGs em [`reports/figures/`](reports/figures/) entram no git para os slides.

## Arquitetura

```
src/projeto1_c11/
  data.py            carga + cache + limpeza
  categories.py      aliases de Melhor Filme, honorários, década
  plotting.py        estilo comum e save_fig
  questions/q01..q05 cada uma expõe QUESTION, compute(df), plot(result)
notebooks/analise_top5.ipynb
reports/figures/q0{1-5}_*.png
tests/               DataFrame sintético (remake, alias de BP, honorário)
```

`uv run projeto1-c11` chama `projeto1_c11.main()`: carrega, percorre `QUESTIONS` e grava as cinco figuras.

## Limpeza dos dados

Três problemas da etapa de Descoberta (material do Slide 4):

1. **Nomes históricos de Melhor Filme.** `Outstanding Picture`, `Outstanding Production`, `Outstanding Motion Picture` e `Best Motion Picture` viram `BEST PICTURE`. Se o CSV trouxer `canon_category`, ela é a fonte; senão usa-se `category`.
2. **Valores ausentes.** Honorários e especiais (HONORARY, SPECIAL AWARD, Thalberg, Hersholt, etc.) frequentemente vêm sem `film`. As perguntas de filme/profissional excluem `is_honorary`. A flag olha a categoria original **e** a canônica, porque o dataset às vezes mapeia honorários antigos para categorias competitivas.
3. **Remakes.** A chave de filme é sempre `(film, year_ceremony)`, nunca só o título.

Outras decisões:

- década = `(year_ceremony // 10) * 10` em NumPy
- Q4 ignora filme internacional: em `FOREIGN` / `INTERNATIONAL FEATURE` o campo `name` é o país, não o profissional
- SPECIAL EFFECTS não é tratado como honorário (o marcador é `SPECIAL AWARD`, não qualquer `SPECIAL`)

## As cinco perguntas

Cada módulo devolve um DataFrame; o gráfico é responsabilidade de `plot`.

| # | Módulo | O que calcula | Figura |
|---|---|---|---|
| 1 | `q01_conversao` | Por filme: indicações, vitórias, taxa. Pearson e Spearman (Spearman = Pearson dos postos, sem SciPy). Taxa média por faixa 1 / 2–3 / 4–6 / 7–9 / 10+. | Scatter com jitter + barras do “ponto de virada” |
| 2 | `q02_precursoras` | Só filmes **indicados** a Melhor Filme. Para cada categoria X: `P(X\|BP)`, `P(BP\|X)` e coeficiente φ (correlação entre duas binárias). | Barras horizontais ordenadas por φ |
| 3 | `q03_evolucao` | Por década: categorias distintas (nome original vs. cânone), indicações e vitórias por cerimônia. | Duas séries temporais |
| 4 | `q04_eficiencia` | Por `name`, ≥ 5 indicações competitivas: volume vs. `vitórias / indicações`. | Dois rankings (top 15) |
| 5 | `q05_concentracao` | Por cerimônia: quantos filmes distintos venceram e a fatia do mais premiado da noite; média móvel de 5 anos e média por década. | Série anual + barras por década |

## O que os dados mostraram (dataset atual)

Números da última geração das figuras; mudam se o CSV do Kaggle for atualizado.

- **Q1.** Pearson 0,69 e Spearman 0,43 entre indicações e vitórias. A taxa média sobe com o volume e chega a **38% na faixa 10+** (n=107). Campeões no gráfico: *Titanic* (1998) e *Ben-Hur* (1960), 11 estatuetas. Maiores esnobados anotados: *The Color Purple* (1986) e *The Turning Point* (1978), 11 indicações e zero vitórias.
- **Q2.** Direção é a precursora clara (φ ≈ 0,68; 72% dos Melhor Filme também levam Direção). Em seguida, roteiro adaptado e montagem.
- **Q3.** A Academia se expande até meados do século e depois estabiliza em torno de 30 categorias canônicas. A linha dos nomes originais dispara nos anos 1970 — é o custo de não unificar rótulos históricos.
- **Q4.** Volume (MGM, Disney, John Williams) não é a mesma lista que eficiência (John Ford 4/5). *Star power* compra indicação com mais previsibilidade do que vitória.
- **Q5.** Hoje cerca de 14 filmes distintos levam pelo menos uma estatueta por noite. As décadas de 1940–50 concentram mais “noites de varredura”; o padrão recente é mais pulverizado.

## Testes

`tests/conftest.py` monta um Oscar em miniatura: alias `OUTSTANDING PICTURE`, remake de *Champ* em 1950 e 2020, honorário sem filme, e um profissional com 5 indicações. Os testes travam a unificação de Melhor Filme, a chave `(film, year_ceremony)`, as contas de Q1/Q2/Q5 e o fato de SPECIAL EFFECTS não ser honorário.
