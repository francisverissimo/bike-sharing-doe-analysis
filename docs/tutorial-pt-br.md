# Guia didático da análise

Este documento explica o trabalho passo a passo. Seu objetivo não é apenas
apresentar resultados, mas também revisar os conceitos estatísticos e conectá-los
ao código do projeto.

Uma versão equivalente em inglês está disponível em
[`tutorial-en.md`](tutorial-en.md).

## 1. Qual é a pergunta de pesquisa?

Respondemos a duas perguntas relacionadas, mas distintas:

1. **Explicação:** quais fatores estão associados à demanda horária por
   bicicletas e, em especial, o efeito da hora difere entre dias úteis e não
   úteis?
2. **Predição:** esses fatores conseguem prever a demanda em um período posterior?

A resposta é `cnt`, o total de bicicletas alugadas durante uma hora.

## 2. Por que este é um estudo observacional?

Em um experimento controlado, os pesquisadores escolhem os tratamentos e os
distribuem aleatoriamente entre as unidades experimentais. Isso não aconteceu
aqui. Os registros vieram da operação real do Capital Bikeshare.

- Ninguém distribuiu dias chuvosos aleatoriamente.
- Ninguém randomizou quais horas pertenciam a dias úteis.
- Estação, temperatura e umidade ocorreram naturalmente.

Trata-se, portanto, de um **estudo observacional com estrutura fatorial natural**.
Podemos descrever associações, mas não afirmar que uma variável causou outra.

### Terminologia do desenho

| Conceito | Aplicação neste estudo |
|---|---|
| Unidade observacional | Uma hora registrada em uma data |
| Resposta | `cnt`, total de aluguéis na hora |
| Fatores | Hora, tipo de dia, condição climática agrupada, estação |
| Covariáveis | Temperatura, umidade, velocidade do vento |
| Níveis | Por exemplo, `workingday` tem níveis 0 e 1 |
| Randomização | Nenhuma |
| Blocos planejados | Nenhum |
| Repetição temporal | Registros sequenciais e correlacionados no tempo |

### Por que não usar OFAT?

OFAT significa *one factor at a time* (um fator por vez). Seria inadequado porque
o comportamento de uma variável pode depender de outra.

Às 08:00, um dia útil tem alta demanda de deslocamento. Às 08:00 de um domingo, o
padrão é diferente. Essa dependência é uma **interação**.

## 3. Entendendo a base de dados

O arquivo principal é `dataset/hour.csv`.

- 17.379 observações;
- 731 datas de 1 de janeiro de 2011 a 31 de dezembro de 2012;
- `cnt` varia de 1 a 977;
- nenhuma célula ausente nas linhas registradas;
- 165 horários ausentes no calendário horário completo;
- `cnt = casual + registered` em todas as linhas.

Os horários ausentes não foram preenchidos. Um registro ausente não implica zero
aluguéis, portanto atribuir zero introduziria uma suposição sem apoio.

### Variáveis excluídas

- `casual` e `registered`: compõem `cnt`. Usá-las para prever `cnt` seria
  **vazamento da resposta**.
- `atemp`: tem correlação 0,988 com `temp`. Usamos apenas `temp` para evitar
  preditores redundantes.
- `instant`: é apenas um identificador sequencial de linha.

A análise usa quatro fatores: `hr`, `workingday`, uma condição climática
agrupada a partir de `weathersit` e `season`. O nível bruto 4 ocorre em apenas
três horas; por isso os níveis 3 e 4 são combinados em uma única condição de
precipitação/tempo adverso. A variável bruta com quatro níveis é mantida na
validação dos dados.

## 4. Análise descritiva

Estatísticas descritivas resumem os dados observados sem ajustar um modelo
inferencial.

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

A média excede a mediana, indicando distribuição assimétrica à direita: muitas
horas têm demanda baixa ou moderada, enquanto algumas têm demanda muito alta.

### Como ler os gráficos

- **Histograma:** mostra o número de horas em cada faixa de demanda.
- **Boxplot:** compara medianas, quartis e observações extremas entre grupos.
- **Gráfico de efeitos principais:** mostra a média da resposta em cada nível do fator.
- **Gráfico de interação:** mostra as médias de um fator separadamente para os níveis de outro.

Médias observadas pelas condições climáticas agrupadas:

| Condição climática | Média de aluguéis/hora |
|---|---:|
| Claro/parcialmente nublado | 204,87 |
| Névoa/nublado | 175,17 |
| Precipitação/tempo adverso | 111,50 |

Essas são médias **não ajustadas**. Parte de cada diferença pode estar relacionada
a hora, estação, temperatura ou outras variáveis.

## 5. Por que transformar `cnt`?

A regressão linear não exige que a resposta bruta seja normalmente distribuída.
Entre outras pressuposições, os **resíduos** devem ter distribuição adequada e
variância aproximadamente constante.

Contagens costumam ser assimétricas e ter variância que cresce com a média.
Comparamos:

\[
Y_1 = cnt, \qquad Y_2 = \log(1+cnt).
\]

Somar 1 mantém o logaritmo definido caso apareça uma contagem zero em outra base.

### Evidências para a escolha

| Resposta | Shapiro--Wilk \(W\) | Breusch--Pagan | \(R^2\) ajustado |
|---|---:|---:|---:|
| `cnt` | 0,972 | 4282,8 | 0,812 |
| `log1p(cnt)` | 0,949 | 1672,5 | 0,927 |

Os valores de \(p\) dos dois testes ficaram abaixo de 0,001 nas duas escalas.
Usamos `log1p(cnt)` porque ele se ajusta melhor e reduz a estatística de
Breusch--Pagan. Shapiro--Wilk, isoladamente, não favorece essa escala; a decisão é
um compromisso entre variância e ajuste, não uma afirmação de resíduos normais.

Com mais de 17 mil observações, testes formais detectam até desvios pequenos. Por
isso, testes, gráficos e magnitude dos desvios são lidos em conjunto.

## 6. Efeito principal e interação

Um **efeito principal** descreve como a média muda entre os níveis de um fator.
Neste estudo observacional, usamos linguagem de associação.

Uma **interação** ocorre quando o comportamento de um fator depende do nível de
outro. Nosso caso pré-especificado é:

\[
\text{hora} \times \text{tipo de dia}.
\]

Em `outputs/figures/workingday_hr_interaction.png`:

- dias úteis têm pico por volta das 08:00 e entre 17:00--18:00;
- dias não úteis apresentam perfil mais amplo ao meio do dia;
- as linhas não são paralelas e se cruzam.

A média geral do tipo de dia, portanto, não basta. O tipo de dia precisa ser
interpretado em conjunto com a hora.

## 7. Um único modelo de regressão

O modelo foi especificado uma vez:

```text
log1p(cnt) ~ hr * workingday + weather_group + season
            + temp + hum + windspeed + yr
```

Aqui, `weather_group` é a condição climática agrupada em três níveis. Na fórmula
`statsmodels` usada no código, os termos categóricos são escritos
`C(hr)`, `C(workingday)`, `C(weather_group)`, `C(season)` e `C(yr)`.

Em uma fórmula de modelo, `hr * workingday` se expande para:

```text
hr + workingday + hr:workingday
```

Isso segue o **princípio da hierarquia**: quando uma interação está presente,
seus efeitos principais componentes permanecem no modelo.

### Por que tratar a hora como categórica?

Tratar a hora como um único número linear forçaria uma mudança retilínea das
00:00 às 23:00. O padrão real contém uma depressão noturna, dois picos em dias
úteis e quedas posteriores. Por isso usamos 24 níveis categóricos.

O modelo tem 57 parâmetros porque um fator hora com 24 níveis interage com um
fator binário e o clima tem três níveis agrupados. A curva de interação é mais útil do que listar todos os
coeficientes indicadores.

## 8. ANOVA e tamanho de efeito

A ANOVA particiona a variação da resposta entre os termos do modelo e o erro
residual.

- **F:** compara a variação atribuída a um termo com a variação residual.
- **Valor-p:** mede a incompatibilidade com uma hipótese nula sob as pressuposições do teste.
- **Eta quadrado parcial:** descreve a variação relativa atribuída a um termo após
  considerar o erro do modelo.

Resultados centrais:

| Termo | F | Valor-p | Eta quadrado parcial |
|---|---:|---:|---:|
| Hora | 5416,44 | < 0,001 | 0,878 |
| Tipo de dia | 12,27 | < 0,001 | 0,001 |
| Condição climática | 1180,12 | < 0,001 | 0,120 |
| Estação | 1163,90 | < 0,001 | 0,168 |
| Ano | 6204,50 | < 0,001 | 0,264 |
| Hora × tipo de dia | 1079,55 | < 0,001 | 0,589 |

O valor-p do tipo de dia é pequeno, mas seu tamanho de efeito principal é muito
menor que o da interação. Isso mostra que “significativo” ou “não significativo”
não basta para a interpretação. O modelo tem $R^2$ ajustado $0{,}927$,
AIC $15914{,}2$ e BIC $16356{,}7$ em `log1p(cnt)`.

### Tukey HSD para o clima

Como o termo de clima na ANOVA é significativo, o teste de Tukey HSD compara as
três condições agrupadas em `log1p(cnt)`. Ele controla a taxa de erro familiar
nas três comparações e fornece intervalos de confiança simultâneos. Todas as
comparações são significativas após ajuste (\(p<0{,}001\)): claro versus névoa
$0{,}142$ (IC 95\%: $0{,}084$ a $0{,}199$), claro versus adverso $0{,}691$
($0{,}599$ a $0{,}784$) e névoa versus adverso $0{,}550$ ($0{,}450$ a $0{,}650$).
A categoria adversa é heterogênea por agrupar dois níveis brutos raros.

## 9. Diagnósticos básicos dos resíduos

### Resíduos versus ajustados

Este gráfico verifica forma funcional e variância constante. Um padrão em funil
sugere heterocedasticidade.

### Gráfico Q--Q

Compara quantis dos resíduos com quantis normais. Desvios nas caudas indicam
caudas não normais.

### ACF e dependência temporal

A função de autocorrelação (ACF) dos resíduos é:

- defasagem 1: 0,612;
- defasagem 24: 0,243;
- defasagem 168: 0,200.

São defasagens em horas **observadas**, pois o calendário tem lacunas. A ACF mostra
que permanece dependência temporal após os fatores incluídos. Os valores-p da
ANOVA são lidos de forma descritiva, e o conjunto de teste temporal é a principal
evidência de desempenho preditivo.

## 10. Divisão temporal entre treino e teste

Uma divisão aleatória permitiria que observações futuras ajudassem a prever o
passado. Usamos uma única divisão estritamente temporal:

- **treino:** todas as horas até 30 de setembro de 2012 (15.211 horas);
- **teste:** de 1 de outubro a 31 de dezembro de 2012 (2.168 horas).

Os dois anos aparecem nos dados de treino, de modo que o fator ano é estimável.

As previsões ajustadas em `log1p(cnt)` voltam à escala de contagem com a correção
de smearing de Duan. Calcular apenas `exp(previsão) - 1` seria viesado, pois a
exponencial de uma média não é a média da exponencial.

### Métricas

- **MAE:** erro absoluto médio em aluguéis.
- **RMSE:** dá mais peso a erros grandes.
- **\(R^2\) fora da amostra:** compara o modelo com a média do período de teste.

### Resultados no teste

| MAE | RMSE | \(R^2\) |
|---:|---:|---:|
| 45,27 | 72,97 | 0,869 |

## 11. O que podemos concluir?

1. A hora é o principal fator observado de demanda.
2. Seu comportamento depende fortemente do tipo de dia.
3. Condição climática agrupada e estação apresentam associações relevantes.
4. A escala logarítmica apresenta melhor ajuste e comportamento da variância.
5. O modelo prevê um trimestre não visto com \(R^2 = 0{,}869\).
6. Associações não estabelecem causalidade.
7. Permanece dependência residual após o ajuste.

## 12. Como o código está organizado?

| Arquivo | Finalidade |
|---|---|
| `analysis/00_validate_data.py` | Verifica integridade, tipos, intervalos e lacunas |
| `analysis/01_descriptive_analysis.py` | Cria resumos, histogramas, boxplots e correlações |
| `analysis/02_doe_analysis.py` | Cria efeitos principais, interação, ANOVA e Tukey HSD do clima |
| `analysis/03_assumptions_transformations.py` | Compara escalas da resposta e diagnósticos básicos |
| `analysis/04_regression_models.py` | Ajusta o único modelo de regressão |
| `analysis/05_temporal_validation.py` | Avalia o modelo no conjunto de teste temporal |
| `analysis/06_report_assets.py` | Cria tabelas para os artigos e resumos bilíngues |
| `src/bike_sharing/` | Funções compartilhadas chamadas pelos scripts |

Execute a análise completa com:

```bash
make setup
make all
```

Verifique o código com:

```bash
make lint
make test
```

## 13. Perguntas de revisão antes da apresentação

1. Por que este estudo não permite conclusões causais?
2. Qual a diferença entre fator, nível, covariável e resposta?
3. Por que `workingday` não deve ser interpretado sem `hr`?
4. Como a interação aparece na fórmula do modelo?
5. Por que a normalidade é avaliada nos resíduos e não na resposta bruta?
6. Por que usamos `temp` e não `atemp`?
7. O que a ACF dos resíduos nos informa?
8. Por que a divisão temporal é preferível à divisão aleatória aqui?
9. Como diferem os objetivos explicativo e preditivo?
10. Por que um valor-p pequeno não garante importância prática?
11. Por que os níveis 3 e 4 do clima foram agrupados e o que o Tukey HSD controla?
