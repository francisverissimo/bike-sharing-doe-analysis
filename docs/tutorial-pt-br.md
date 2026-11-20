# Guia didático da análise simplificada

Este documento explica o trabalho passo a passo. O objetivo não é apenas mostrar
os resultados, mas ajudar a revisar os conceitos estatísticos usados e relacionar
cada conceito ao código do projeto.

Uma versão equivalente em inglês está em [`tutorial-en.md`](tutorial-en.md).

## 1. Qual é a pergunta do trabalho?

Queremos responder duas perguntas relacionadas, mas diferentes:

1. **Explicação:** quais fatores estão associados à demanda horária por
   bicicletas e, principalmente, o efeito da hora muda entre dias úteis e dias
   não úteis?
2. **Predição:** esses fatores permitem prever a demanda de períodos futuros?

A variável que queremos explicar e prever é `cnt`, o total de bicicletas
alugadas em uma hora.

## 2. Por que o estudo é observacional?

Em um experimento controlado, os pesquisadores escolhem tratamentos e os
atribuem aleatoriamente às unidades experimentais. Isso não aconteceu aqui. Os
dados foram registrados durante a operação real do Capital Bikeshare.

- Ninguém escolheu aleatoriamente se um dia teria chuva.
- Ninguém sorteou quais horas seriam dias úteis.
- Estação, temperatura e umidade ocorreram naturalmente.

Portanto, este é um **estudo observacional com estrutura fatorial natural**.
Podemos afirmar que variáveis estão associadas, mas não que uma delas causou a
outra.

### Conceitos do planejamento

| Conceito | Aplicação neste trabalho |
|---|---|
| Unidade observacional | Uma hora registrada em uma determinada data |
| Resposta | `cnt`, total de aluguéis naquela hora |
| Fatores | Hora, dia útil, clima, estação e ano |
| Covariáveis | Temperatura, umidade e velocidade do vento |
| Níveis | Por exemplo, `workingday` possui níveis 0 e 1 |
| Randomização | Não existe |
| Blocos planejados | Não existem |
| Repetição temporal | As observações são sequenciais e correlacionadas no tempo |

### Por que não usamos OFAT?

OFAT significa *one factor at a time*: variar ou examinar um fator por vez. Isso
seria inadequado porque o comportamento de uma variável pode depender de outra.

Neste dataset, o efeito da hora depende do tipo de dia. Às 8h, um dia útil tem
grande demanda de deslocamento para o trabalho. Às 8h de um domingo, o padrão é
diferente. Essa dependência é uma **interação**.

## 3. Conhecendo o dataset

O arquivo principal é `dataset/hour.csv`.

- 17.379 observações;
- 731 datas, entre 01/01/2011 e 31/12/2012;
- `cnt` varia de 1 a 977;
- não há valores ausentes nas linhas registradas;
- há 165 horários ausentes na sequência completa do calendário;
- `cnt = casual + registered` em todas as linhas.

As horas ausentes não foram preenchidas. Uma linha ausente não significa que
ninguém alugou uma bicicleta; atribuir zero seria uma suposição sem evidência.

### Variáveis excluídas

- `casual` e `registered`: formam `cnt`. Usá-las para prever `cnt` seria
  **vazamento de alvo** (*target leakage*).
- `atemp`: tem correlação 0,988 com `temp`. As duas juntas apresentam VIF acima
  de 43. Mantivemos somente `temp` para evitar multicolinearidade.
- `instant`: é apenas o identificador sequencial da linha.

### Agrupamento do clima

O fator original `weathersit` tem quatro níveis, mas o nível 4 aparece somente
três vezes. Não há dados suficientes para estimar um efeito separado estável.

Para a inferência, usamos:

1. claro ou parcialmente nublado;
2. névoa ou nublado;
3. precipitação ou condição adversa, reunindo os níveis originais 3 e 4.

O arquivo original permanece intacto. O agrupamento é criado em memória por
`src/bike_sharing/data.py`.

## 4. Análise descritiva

A estatística descritiva resume o que foi observado sem tentar generalizar por
meio de um modelo.

| Medida | Resultado |
|---|---:|
| Observações | 17.379 |
| Média | 189,46 |
| Mediana | 142 |
| Desvio-padrão | 181,39 |
| Primeiro quartil | 40 |
| Terceiro quartil | 281 |
| Mínimo | 1 |
| Máximo | 977 |

A média é maior que a mediana. Isso indica uma distribuição assimétrica à
direita: muitas horas têm demanda baixa ou moderada e algumas horas têm demanda
muito alta.

### Como interpretar os gráficos

- **Histograma:** mostra quantas horas caem em cada intervalo de demanda.
- **Boxplot:** compara mediana, quartis e valores extremos entre grupos.
- **Gráfico de efeitos principais:** mostra a média da resposta em cada nível de
  um fator, ignorando visualmente as interações.
- **Gráfico de interação:** mostra as médias de um fator separadas pelos níveis de
  outro fator.

As médias observadas por clima são:

| Clima | Média de aluguéis/hora |
|---|---:|
| Claro/parcialmente nublado | 204,87 |
| Névoa/nublado | 175,17 |
| Precipitação/adverso | 111,50 |

Essas médias são **não ajustadas**. Parte da diferença pode estar relacionada a
hora, estação, temperatura ou outras variáveis.

## 5. Por que transformar `cnt`?

A regressão linear não exige que a resposta original tenha distribuição normal.
Ela pressupõe, entre outros pontos, que os **resíduos** tenham comportamento
adequado e variância aproximadamente constante.

Contagens costumam apresentar assimetria e variância crescente. Comparamos:

\[
Y_1 = cnt, \qquad Y_2 = \sqrt{cnt}, \qquad
Y_3 = \log(1+cnt).
\]

Somamos 1 antes do logaritmo para que a expressão continue definida caso uma
contagem zero apareça em outro conjunto de dados.

### Evidências usadas na escolha

Para a estrutura M1:

| Resposta | Shapiro--Wilk \(W\) | Breusch--Pagan | \(R^2\) ajustado |
|---|---:|---:|---:|
| `cnt` | 0,972 | 4282,8 | 0,812 |
| `sqrt(cnt)` | 0,984 | 2039,7 | 0,893 |
| `log1p(cnt)` | 0,949 | 1672,5 | 0,927 |

Os valores de \(p\) de Shapiro--Wilk e Breusch--Pagan ficaram abaixo de 0,001
nas três escalas. Escolhemos `log1p(cnt)` porque apresentou melhor ajuste e a
menor evidência relativa de heterocedasticidade. Note que Shapiro--Wilk sozinho
favoreceria `sqrt(cnt)`; a decisão pelo log é um compromisso entre variância e
ajuste, não uma aprovação da normalidade.

Jarque--Bera, Levene, Box--Cox e Durbin--Watson ainda podem ser calculados a
partir dos artefatos em `outputs/tables/`, mas não fazem parte da narrativa
principal do artigo. Com 17 mil observações, testes como Shapiro--Wilk detectam
até desvios pequenos. Por isso, olhamos testes, gráficos e tamanho dos desvios em
conjunto.

## 6. Efeito principal e interação

Um **efeito principal** descreve como a média muda entre os níveis de um fator,
mantendo a linguagem de associação neste estudo observacional.

Uma **interação** ocorre quando o comportamento de um fator depende do nível de
outro. Nosso caso central é:

\[
\text{hora} \times \text{dia útil}.
\]

No gráfico `outputs/figures/primary_interaction.png`:

- dias úteis apresentam picos próximos de 8h e 17h--18h;
- dias não úteis apresentam uma curva mais ampla durante o meio do dia;
- as linhas não são paralelas e chegam a se cruzar.

Isso mostra por que a média geral de dias úteis, isoladamente, é pouco
informativa. O tipo de dia precisa ser interpretado junto da hora.

## 7. Os dois modelos explicativos

### M0: modelo aditivo

```text
log1p(cnt) ~ hour + workingday + weather + season
           + temp + humidity + windspeed + year
```

M0 supõe que o formato do efeito horário é igual em dias úteis e não úteis. O
tipo de dia apenas deslocaria toda a curva para cima ou para baixo.

### M1: modelo com a interação principal

```text
log1p(cnt) ~ hour * workingday + weather + season
           + temp + humidity + windspeed + year
```

Na fórmula, `hour * workingday` representa:

```text
hour + workingday + hour:workingday
```

Isso respeita o **princípio hierárquico**: se uma interação está no modelo, seus
efeitos principais também permanecem.

### Por que `hour` é categórica?

Se tratássemos hora como um número linear, o modelo tentaria representar a
mudança entre 0h e 23h por uma única reta. O padrão real possui madrugada, dois
picos e quedas; por isso usamos 24 níveis categóricos.

Essa escolha aumenta o número de parâmetros. M1 possui 57 parâmetros, mas sua
interpretação principal vem do gráfico de interação, não de uma lista com todas
as variáveis indicadoras.

## 8. ANOVA e tamanho de efeito

A ANOVA divide a variação da resposta entre os termos do modelo e os resíduos.

- **F:** compara a variação explicada por um termo com a variação residual.
- **p-valor:** mede quão incompatíveis os dados são com uma hipótese nula, sob as
  premissas do teste.
- **Eta quadrado parcial:** estima a proporção relativa da variação atribuída ao
  termo após considerar o erro do modelo.

Resultados centrais de M1:

| Termo | F | p-valor | Eta quadrado parcial |
|---|---:|---:|---:|
| Hora | 5416,44 | < 0,001 | 0,878 |
| Dia útil | 12,27 | < 0,001 | 0,001 |
| Hora × dia útil | 1079,55 | < 0,001 | 0,589 |
| Clima | 1180,12 | < 0,001 | 0,120 |
| Estação | 1163,90 | < 0,001 | 0,168 |

O p-valor de dia útil é pequeno, mas seu efeito principal é muito menor que a
interação. Esse é um exemplo de por que não devemos concluir apenas com base em
“significativo” ou “não significativo”.

## 9. Comparação M0 versus M1

| Modelo | Parâmetros | \(R^2\) ajustado | AIC | BIC |
|---|---:|---:|---:|---:|
| M0 | 34 | 0,824 | 31323,3 | 31587,2 |
| M1 | 57 | 0,927 | 15914,2 | 16356,7 |

- O **\(R^2\) ajustado** recompensa explicação, mas penaliza parcialmente a
  inclusão de parâmetros.
- **AIC** e **BIC** equilibram ajuste e complexidade; valores menores são
  preferíveis quando os modelos usam a mesma resposta e os mesmos dados.
- O teste F aninhado para adicionar a interação produziu \(F=1079,55\) e
  \(p<0,001\).

As três evidências favorecem M1. Mais importante, a melhoria tem uma explicação
comportamental clara: deslocamentos de trabalho geram um perfil horário próprio.

## 10. Diagnósticos do modelo

### Resíduos versus ajustados

Verifica forma funcional e variância constante. Um padrão em funil sugere
heterocedasticidade.

### Q--Q plot

Compara quantis dos resíduos com quantis normais. Desvios nas extremidades
indicam caudas não normais.

### VIF

O *Variance Inflation Factor* mede quanto a correlação entre preditores aumenta a
variância de um coeficiente. A remoção de `atemp` reduziu os VIF das variáveis
numéricas selecionadas para aproximadamente 1,1 ou menos.

### ACF e dependência temporal

A função de autocorrelação (ACF) dos resíduos de M1 foi:

- lag 1: 0,612;
- lag 24: 0,243;
- lag 168: 0,200.

O teste de Durbin--Watson foi mantido apenas nos artefatos gerados; na narrativa
principal, a ACF resume melhor a dependência em várias escalas temporais. Os lags
são horas **observadas**, pois existem lacunas no calendário.

### Por que usar HAC?

HAC significa *heteroskedasticity and autocorrelation consistent*. Newey--West
recalcula erros-padrão e intervalos de confiança considerando heterocedasticidade
e dependência temporal até um número escolhido de lags.

Usamos 168 lags observados, aproximadamente uma semana. HAC não altera os
coeficientes nem as previsões; altera a estimativa de incerteza. Ele também não
elimina toda limitação temporal do estudo.

## 11. Validação preditiva

Uma divisão aleatória permitiria que observações futuras ajudassem a prever o
passado. Para evitar esse vazamento temporal, usamos janelas expansivas:

1. treino até março de 2012, validação em Q2/2012;
2. treino até junho de 2012, validação em Q3/2012;
3. treino até setembro de 2012, teste final em Q4/2012.

O último período permaneceu fora da escolha do modelo.

Comparamos:

- **Baseline:** média histórica para cada combinação de hora e tipo de dia;
- **P0:** versão preditiva aditiva de M0;
- **P1:** versão preditiva com `hour × workingday`.

Os modelos preditivos substituem o ano categórico por um índice temporal
contínuo. Uma categoria “2012” não consegue representar um ano futuro ainda não
observado, enquanto um índice temporal pode representar tendência.

As previsões feitas em `log1p(cnt)` voltam à escala de contagem por correção de
*smearing* de Duan. Aplicar apenas `exp(predição) - 1` produziria viés porque a
exponencial de uma média não é igual à média da exponencial.

### Métricas

- **MAE:** média dos erros absolutos, na unidade “aluguéis”.
- **RMSE:** dá peso maior a erros grandes.
- **\(R^2\) fora da amostra:** compara o modelo com a média do período de teste.
- **RMSLE:** mede erro na escala logarítmica e reduz o domínio das maiores
  contagens.

### Holdout final Q4/2012

| Modelo | MAE | RMSE | \(R^2\) | RMSLE |
|---|---:|---:|---:|---:|
| Baseline | 79,95 | 119,59 | 0,648 | 0,604 |
| P0 | 85,65 | 121,25 | 0,638 | 0,725 |
| P1 | 51,99 | 83,07 | 0,830 | 0,524 |

P1 supera tanto o modelo aditivo quanto o baseline. A interação não é apenas
estatisticamente detectável: ela também melhora a previsão de dados futuros.

## 12. O que podemos concluir?

1. Hora é o principal fator observado da demanda.
2. Seu comportamento depende fortemente de o dia ser útil ou não.
3. Clima e estação apresentam associações importantes com demanda.
4. M1 representa melhor os dados que M0.
5. A mesma interação melhora a previsão temporal.
6. As associações não demonstram causalidade.
7. Ainda existe dependência nos resíduos, mesmo após o ajuste.

## 13. Como o código está organizado?

| Arquivo | Função |
|---|---|
| `analysis/00_validate_data.py` | Verifica integridade, tipos, intervalos e lacunas |
| `analysis/01_descriptive_analysis.py` | Gera resumos, histogramas, boxplots e correlações |
| `analysis/02_doe_analysis.py` | Gera efeitos, interação principal, ANOVA e Tukey |
| `analysis/03_assumptions_transformations.py` | Compara escalas e verifica pressupostos |
| `analysis/04_regression_models.py` | Compara M0 e M1 e gera diagnósticos/HAC |
| `analysis/05_temporal_validation.py` | Avalia baseline, P0 e P1 no tempo |
| `analysis/06_report_assets.py` | Produz tabelas e resumos usados no artigo |
| `src/bike_sharing/` | Contém funções compartilhadas pelos scripts |

Para executar tudo:

```bash
make setup
make all
```

Para verificar o código:

```bash
make lint
make test
```

## 14. Perguntas para revisar antes da apresentação

1. Por que este trabalho não permite conclusões causais?
2. Qual é a diferença entre fator, nível, covariável e resposta?
3. Por que `workingday` não deve ser interpretada sem `hr`?
4. O que a interação acrescenta ao M0?
5. Por que normalidade deve ser avaliada nos resíduos?
6. Por que removemos `atemp`?
7. O que HAC corrige e o que ele não corrige?
8. Por que a divisão temporal é melhor que uma divisão aleatória aqui?
9. Qual é a diferença entre o objetivo explicativo e o preditivo?
10. Por que um p-valor pequeno não garante importância prática?
