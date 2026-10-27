O dataset configurado no seu `dataset.py` é o **`unanimad/the-oscar-award`** (*The Oscar Award, 1927 - 2024*), que possui o arquivo `the_oscar_award.csv` (dica: em `dataset.py`, defina `file_path = "the_oscar_award.csv"` para que o `kagglehub.load_dataset` funcione sem erro).

### Estrutura das Colunas do Dataset
Para garantir que todas as 10 perguntas possam ser respondidas **100% com os dados disponíveis** (usando `NumPy`, `Pandas` e `Matplotlib`), vale lembrar as 7 colunas presentes nele:
* `year_film` (Ano de lançamento do filme)
* `year_ceremony` (Ano da cerimônia do Oscar)
* `ceremony` (Número da edição da cerimônia)
* `category` (Categoria do prêmio — ex: *BEST PICTURE*, *DIRECTING*, *ACTOR IN A LEADING ROLE*)
* `name` (Nome do indicado: ator, diretor, produtor, estúdio etc.)
* `film` (Título do filme)
* `winner` (Booleano `True`/`False` indicando se venceu ou apenas foi indicado)

---

### Alinhamento com os Requisitos do Projeto (PDF e Template PPTX)
Segundo o PDF da disciplina e o Slide 2/Slide 3 do template:
* **Público-alvo estratégico (Slide 2):** Estúdios de cinema, plataformas de *streaming* (Netflix, Apple TV+, Amazon Prime), produtoras e distribuidoras que investem milhões em campanhas de *For Your Consideration* (FYC) para ganhar prestígio, retenção de assinantes e retorno de bilheteria, além de curadores e críticos culturais.
* **Ordenação (Slide 3):** O template pede que **as 5 perguntas mais importantes venham primeiro** (pois serão as 5 apresentadas no pitch de 10 minutos em sala de aula).

---

### Sugestão das 10 Perguntas (Divididas conforme o Template)

#### Top 5: As Perguntas Mais Estratégicas (Para apresentar no Pitch em sala)

1. **Qual é a relação entre o volume de indicações de um filme e sua taxa de conversão em vitórias? Existe um "ponto de virada" em que muitas indicações garantem o domínio da noite ou geram os maiores "esnobados" da história?**
   * **Insight de negócio:** Ajuda estúdios a entender se vale mais pulverizar investimentos em várias categorias técnicas ou focar em poucas categorias-chave. Permite identificar tanto os maiores campeões (*Ben-Hur*, *Titanic*, *O Senhor dos Anéis*) quanto os filmes com mais indicações que saíram de mãos vazias (`winner == False`).
   * **Como responder no código:** Agrupar por `film` e `year_ceremony`, somar indicações (`count`) e vitórias (`sum` de `winner`), calcular a taxa de conversão (%) e plotar um *scatter plot* ou gráfico de barras horizontais.

2. **Para um filme vencer a categoria principal ("Melhor Filme" / *Best Picture*), quais outras categorias (ex: Direção, Roteiro, Montagem) historicamente têm a maior correlação de vitória conjunta?**
   * **Insight de negócio:** Termômetro estratégico para produtoras e apostadores do mercado audiovisual saberem quais categorias funcionam como "precursoras" reais do prêmio principal da noite.
   * **Como responder no código:** Filtrar os filmes vencedores de *Best Picture* / *Outstanding Picture*, cruzar com as demais categorias que esses mesmos filmes venceram no mesmo `year_ceremony` e calcular a frequência percentual de cada categoria acompanhante.

3. **Como o perfil da Academia evoluiu ao longo das décadas em termos de diversidade de categorias e quantidade de prêmios distribuídos por cerimônia?**
   * **Insight de negócio / cultural:** Mostra a expansão da indústria cinematográfica (surgimento de categorias técnicas, efeitos visuais, animação, som) e como o mercado de trabalho de Hollywood abriu novas frentes de reconhecimento ao longo de quase 100 anos.
   * **Como responder no código:** Agrupar por década (criada via `NumPy`/`Pandas` a partir de `year_ceremony`), contar categorias únicas (`nunique` de `category`) e total de indicados/vencedores, plotando uma série temporal (*line plot*).

4. **Quais profissionais ou entidades (diretores, atores, compositores ou estúdios) possuem o maior histórico de indicações e quem tem a melhor eficiência (taxa de vitória entre os mais indicados)?**
   * **Insight de negócio:** Avalia o "efeito grife" (*star power*) na contratação de talentos. Contratar um profissional historicamente premiado aumenta as chances reais de vitória de uma produção ou apenas garante a indicação?
   * **Como responder no código:** Agrupar por `name`, filtrar quem possui pelo menos $N$ indicações (ex: $\ge 5$), calcular total de indicações, vitórias e proporção `vitórias / indicações`.

5. **Qual é o nível de concentração vs. democratização do Oscar ao longo do tempo: em média, quantos filmes diferentes dividem os prêmios em uma cerimônia (efeito "varredura" vs. premiação pulverizada)?**
   * **Insight de negócio:** Indica para distribuidoras e *streamings* se o mercado está em uma era em que um único *blockbuster* monopoliza a cerimônia (alto risco para concorrentes) ou se há espaço para múltiplos filmes independentes conquistarem 1 ou 2 estatuetas.
   * **Como responder no código:** Para cada `year_ceremony` (onde `winner == True`), contar quantos `film` distintos venceram pelo menos um prêmio e analisar a tendência histórica ou média por década.

---

#### Perguntas 6 a 10: Complementares (Constam nos slides completos e no código)

6. **Quais são os casos de "persistência premiada" — ou seja, os profissionais que acumularam o maior número de indicações antes de finalmente conquistarem sua primeira estatueta (e quem são os maiores injustiçados que nunca venceram)?**
   * **Insight social/cultural:** Analisa o fenômeno de reconhecimento tardio de carreira pela Academia.
   * **Como responder no código:** Ordenar por `year_ceremony` para cada `name`, identificar o número de `False` acumulados antes do primeiro `True` (ou nomes com 100% de `False`).

7. **Qual a evolução e representatividade das categorias de atuação (Ator/Atriz Principal e Coadjuvante) — quem são os recordistas de indicações e vitórias nessas quatro categorias?**
   * **Insight de negócio:** Identifica os maiores ícones de atuação de Hollywood cujo nome no elenco agrega valor imediato de marketing e prestígio.
   * **Como responder no código:** Filtrar `category` contendo termos de atuação (*ACTOR*, *ACTRESS*), agrupar por `name` e comparar indicações vs. vitórias.

8. **Como a nomenclatura das categorias mudou ao longo da história do Oscar e o que isso revela sobre a modernização da indústria (ex: unificação de categorias, mudança no nome de "Melhor Filme")?**
   * **Insight técnico (ótimo também para citar no Slide 4 como um dos "3 maiores desafios na etapa de Descoberta"):** A categoria principal já se chamou *Outstanding Picture*, *Outstanding Production*, *Best Motion Picture* e *Best Picture*.
   * **Como responder no código:** Mapear o primeiro e o último `year_ceremony` de cada `category` e mostrar a linha do tempo das mudanças.

9. **Existe diferença histórica no comportamento de `year_film` vs. `year_ceremony` (como mudanças nas janelas de elegibilidade em anos atípicos, ex: pandemia ou primeiros anos da Academia)?**
   * **Insight de mercado:** Mostra como crises globais ou mudanças de regulamento impactaram o calendário de lançamentos da indústria.
   * **Como responder no código:** Calcular `lag = year_ceremony - year_film`, verificar anomalias e a distribuição ao longo dos anos.

10. **Qual é a proporção média de concorrentes por categoria ao longo das décadas (especialmente a expansão de 5 para até 10 indicados em Melhor Filme a partir de 2010)? Como isso alterou a probabilidade matemática de vitória?**
    * **Insight de negócio:** A partir de 2010, a Academia ampliou os indicados a Melhor Filme para incluir obras mais populares/comerciais, reduzindo a probabilidade individual de vitória de 20% (1 em 5) para 10% (1 em 10), mas aumentando o número de filmes que podem usar o selo "Indicado ao Oscar" no marketing.
    * **Como responder no código:** Filtrar a categoria de Melhor Filme por `year_ceremony`, contar o número de indicados por ano e plotar a mudança de patamar e a probabilidade associada.

---

### Dica Bônus para o Slide 4 ("3 maiores desafios na etapa de Descoberta")
O template de apresentação pergunta quais foram os **3 maiores desafios na exploração dos dados**. Com esse dataset e essas perguntas, vocês já terão respostas prontas e técnicas:
1. **Padronização de categorias históricas:** A mesma categoria mudou de nome várias vezes desde 1927 (ex: *Best Picture* teve 5 nomes diferentes).
2. **Valores ausentes (`NaN`):** Prêmios honorários ou especiais muitas vezes não possuem título na coluna `film` ou nome específico padronizado.
3. **Filmes homônimos (*remakes*):** Filmes com o mesmo nome lançados em décadas diferentes (ex: *A Star Is Born* ou *West Side Story*), exigindo agrupar sempre por `['film', 'year_ceremony']` em vez de apenas `'film'`.
