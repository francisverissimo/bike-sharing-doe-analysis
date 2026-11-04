# Plano de Trabalho 2 - Design of Experiments
**Dataset escolhido:** `hour.csv` (Bike Sharing Dataset - UCI)

---

## 1. Objetivo do Trabalho

Realizar uma análise estatística completa e bem fundamentada sobre o dataset Bike Sharing, utilizando **raciocínio de Design of Experiments (DOE)** para identificar fatores, níveis, efeitos e interações, e, a partir disso, **desenvolver um modelo de regressão múltipla bem justificado** para prever a variável resposta.

---

## 2. Entendimento do Design Experimental

Como se trata de dados **observacionais** (não um experimento controlado), é necessário descrever adequadamente a estrutura de geração dos dados, conforme solicitado no enunciado.

| Aspecto | Classificação | Justificativa |
|---|---|---|
| **Tipo de estudo** | Observacional (quase-experimental) | Não houve alocação aleatória de tratamentos pelo pesquisador. Clima, dias da semana, estação etc. ocorreram de forma natural. |
| **Design adotado** | Fatorial (natural) | Vários fatores atuam simultaneamente sobre a resposta. Isso justifica a análise de **interações**, sendo muito mais adequado que um enfoque OFAT. |
| **Between/Within-subject** | Predominantemente *between-observations*, com estrutura temporal | Cada registro (hora do dia) é uma observação distinta, não há "sujeitos" submetidos repetidamente a tratamentos planejados. Porém, há **dependência temporal** (dados sequenciais no tempo). |
| **Randomização** | Não existente | São dados reais do sistema Capital Bikeshare em operação (2011–2012). Deve ser mencionado explicitamente como característica do estudo observacional. |
| **Unidade experimental** | Intervalo de tempo | Para `hour.csv`, cada observação corresponde a **1 hora de um determinado dia**. |
| **Repetições/Blocos** | Não planejados | Não há blocos controlados. Dias podem ser vistos como unidades agrupadas, mas não estruturadas em um DOE balanceado. |

**Escolha da base:** Optamos por utilizar **`hour.csv`** (17.379 observações), pois contém a variável `hr` (hora do dia), fundamental para capturar a dinâmica horária e explorar interações de forma mais rica. `day.csv` perderia esse comportamento.

---

## 3. Definição de Variáveis: Fatores, Níveis, Categorias e Resposta

### 3.1 Variável Resposta (Y)

- **`cnt`**: Contagem total de bicicletas alugadas (`casual + registered`).
- **Observação:** Não serão utilizadas as variáveis `casual` e `registered` como preditoras, pois são componentes da própria resposta.

### 3.2 Fatores Categóricos

| Fator | Tipo | Níveis/Categorias | Uso na Análise |
|---|---|---|---|
| `season` | Categórico (nominal) | 1 = Primavera, 2 = Verão, 3 = Outono, 4 = Inverno | Efeitos sazonais. Útil para ANOVA, gráficos de efeitos e modelagem. |
| `yr` | Categórico binário | 0 = 2011, 1 = 2012 | Fator de controle (crescimento do sistema entre anos). |
| `mnth` | Categórico (ordinal) | 1 – 12 | Sazonalidade refinada. Pode ser redundante com `season`. Será avaliado no screening. |
| `hr` | Categórico | 0 – 23 (24 níveis) | **Fator-chave**. Essencial para a interação com `workingday`. |
| `holiday` | Categórico binário | 0 = Não feriado, 1 = Feriado | Pouca frequência. Avaliar relevância no screening. |
| `weekday` | Categórico | 0 – 6 | Dias da semana. Pode ser redundante com `workingday`. |
| `workingday` | Categórico binário | 0 = Fim de semana ou feriado, 1 = Dia útil | **Fator-chave**. Separa uso funcional (deslocamento) vs. recreativo (lazer). |
| `weathersit` | Categórico ordinal | 1 = Claro/parcialmente nublado, 2 = Névoa/nublado, 3 = Chuva fraca (+trovoada), 4 = Chuva forte/neve | Nível 4 aparece com frequência extremamente baixa. **Considerar apenas níveis 1–3**. Excelente para avaliar impacto do mau tempo. |

### 3.3 Variáveis Numéricas (Covariáveis)

| Variável | Intervalo (normalizado) | Sugestão de Tratamento |
|---|---|---|
| `temp` | ~0 – 1 (-8 °C a 33 °C aprox.) | Forte preditor. Para **ANOVA/gráficos DOE**, pode ser discretizado em faixas (Baixo/Médio/Alto). Para **regressão múltipla**, será mantido **contínuo**. |
| `atemp` | 0 – 1 (sensação térmica) | **Muito correlacionado com `temp`**. Optamos por **utilizar apenas `temp`**, justificando essa decisão para evitar multicolinearidade. |
| `hum` | 0 – 1 (umidade) | Pode ter efeito moderado, principalmente associado a `weathersit`. Será avaliado. |
| `windspeed` | 0 – 1 (velocidade do vento) | Efeito esperado menor. Será incluído no *screening*. |

---

## 4. Hipóteses sobre Efeitos e Interações (Raciocínio DOE)

### 4.1 Efeitos Principais Esperados

| Fator | Hipótese | Justificativa |
|---|---|---|
| `hr` | **Muito forte** | Padrão bimodal em dias úteis (ida/volta do trabalho) vs. unimodal/suave em fins de semana. |
| `workingday` | **Forte** | Diferencia demanda funcional (obrigatória) de demanda recreativa (flexível). |
| `weathersit` | **Forte** | Mau tempo reduz significativamente a demanda por bicicletas. |
| `season` / `temp` | **Forte** | Maior demanda em estações mais quentes; menor no inverno. `temp` captura esse efeito de forma contínua. |
| `temp` | **Moderado–Forte** | Provável comportamento curvilíneo (demanda aumenta até faixa de conforto, depois tende a estabilizar/reduzir). |
| `hum` | **Moderado** | Umidade elevada costuma estar associada a condições climáticas adversas. |
| `windspeed` | **Fraco–Moderado** | Vento forte tende a desestimular o uso. |
| `weekday` | **Moderado** | Parcialmente capturado por `workingday`. |
| `holiday` | **Fraco** | Baixa representatividade no dataset. |
| `yr` | **Moderado** | Crescimento natural do sistema entre 2011 e 2012. |

### 4.2 Interações Relevantes a Investigar

| Interação | Justificativa | Relevância para DOE |
|---|---|---|
| **`workingday * hr`** | Crítica. Dias úteis apresentam curva bimodal; dias não-úteis apresentam curva mais suave/unimodal. | **Obrigatória** nesta análise. Representa a interação mais forte e mais explicativa. |
| **`weathersit * hr`** | Mau tempo pode impactar mais fortemente em horários de pico obrigatório (deslocamentos) do que em horários flexíveis (lazer). | Muito relevante. Será testada e justificada sua inclusão/exclusão. |
| **`season * hr``** | Diferenças de luminosidade e temperatura ao longo do dia variam por estação (ex.: inverno com escurecimento mais cedo). | Complementar. Boa para enriquecer a interpretação. |
| **`workingday * weathersit`** | Usuários em dias úteis (viagens obrigatórias) tendem a ser menos sensíveis a chuva leve, enquanto usuários de lazer são mais sensíveis. | Interação interessante do ponto de vista comportamental. |
| **`temp * hr`** | Conforto térmico varia com a hora do dia (frio mais percebido pela manhã). | Pode ser testada no modelo de regressão. |
| **`season * temp`** | Possível redundância, mas vale avaliar (mesma temperatura pode ter efeito distinto por estação). | Checar com cautela (multicolinearidade). |

---

## 5. Metodologia de Análise

A análise será dividida em etapas, seguindo exatamente o que foi solicitado no enunciado: **análise descritiva + análise estatística detalhada (pressupostos, transformações, testes, resultados e conclusões) + desenvolvimento de preditores**.

### 5.1 Etapa 1 - Análise Exploratória de Dados (EDA)

- **Tamanho amostral:** Total de observações (`n = 17.379`) e distribuição por grupos (`season`, `workingday`, `weathersit`, `yr`).
- **Medidas resumo:** Média, mediana, desvio-padrão, mínimo, máximo, 1º e 3º quartis para `cnt`.
- **Distribuições:** Histogramas, densidade de Kernel e assimetria/curtose de `cnt`.
- **Gráficos comparativos:** Boxplots de `cnt` por `hr`, `workingday`, `weathersit`, `season`, `weekday` e `yr`.
- **Série temporal:** Evolução de `cnt` ao longo do tempo (2011 vs. 2012) para identificar tendências e padrões sazonais/anuais.
- **Análise de correlações:** Matriz de correlação entre variáveis numéricas (`temp`, `hum`, `windspeed`, `cnt`).
- **Inspeção preliminar de outliers:** Identificação via boxplots e análise crítica (sem remoção automática, sempre com justificativa).

### 5.2 Etapa 2 - Verificação de Pressupostos, Transformações e Dependência Temporal

| Verificação | Testes/Gráficos | Objetivo |
|---|---|---|
| **Normalidade** | Shapiro–Wilk (ou Kolmogorov–Smirnov), **QQ-Plots** e Histogramas | Avaliar aderência à normalidade, com foco principal nos **resíduos** dos modelos. |
| **Homocedasticidade** | Teste de Levene/Bartlett (para grupos), gráfico **Resíduos vs. Ajustados**, Scale–Location. | Verificar homogeneidade de variâncias para ANOVA e Regressão Linear. |
| **Independência** | **Durbin–Watson**, **Funções ACF/PACF** dos resíduos. | **Ponto mais crítico** (dados temporais). Serão testados, reportados e discutidos (limitação inerente a dados observacionais sequenciais). |
| **Transformações da resposta** | Box–Cox, avaliação de `sqrt(cnt)`, `log(cnt+1)`. | Buscar melhorias nas suposições. A decisão de aplicar ou não será **explicitamente justificada** (trade-off entre aderência aos pressupostos x interpretabilidade dos resultados). |
| **Pontos influentes** | Distância de Cook, Leverage, Resíduos Studentizados. | Identificar observações influentes, descrevendo-os sem remover arbitrariamente. |

### 5.3 Etapa 3 - Análise DOE: Efeitos, Interações e ANOVA

| Análise | Aplicação Proposta | Finalidade |
|---|---|---|
| **Screening inicial** | Avaliar relevância de cada fator (gráficos + análise preliminar). | Selecionar fatores mais relevantes para aprofundamento (DOE focado). |
| **Gráficos de Efeitos Principais (*Main Effects Plots*)** | `workingday`, `hr`, `weathersit`, `season`, `temp` (discretizado), `hum`, `windspeed`. | Visão clássica de DOE: visualizar magnitude e direção dos efeitos. |
| **Gráficos de Interações (*Interaction Plots*)** | **`workingday * hr`** (prioritário), `weathersit * hr`, `season * hr`, `workingday * weathersit`. | Investigar presença/ausência de interações e interpretar cruzamentos das curvas. |
| **ANOVA One-Way** | `cnt ~ workingday`, `cnt ~ weathersit`, `cnt ~ season`. | Testar diferenças significativas entre níveis de fatores individuais. |
| **ANOVA Fatorial (com interações)** | Modelos com efeitos principais + termos de interação (foco em `workingday + hr + workingday:hr`). | Embasar estatisticamente os efeitos e interações visualizados nos gráficos (alinha diretamente ao raciocínio DOE). |
| **Testes Post-Hoc** | **Tukey HSD** (quando ANOVA significativa). | Comparações múltiplas entre pares de níveis (`season`, `weathersit`, grupos de `hr`). |

### 5.4 Etapa 4 - Desenvolvimento do Preditor (Regressão Múltipla)

Os modelos serão construídos de forma **progressiva e justificada**, utilizando os resultados da Etapa 3 como embasamento.

| Modelo | Estrutura | Justificativa (Base DOE) |
|---|---|---|
| **M0 – Base (Efeitos principais)** | `cnt ~ workingday + hr + weathersit + temp + season + yr + hum + windspeed` | Inclui fatores com maior efeito identificado no *screening*. Base inicial coerente com análise exploratória. |
| **M1 – Crítico (Interação fundamental)** | **M0 + `workingday * hr`** | **Interação obrigatória**. Fundamentada na diferença marcante entre perfis horários de dia útil vs. não-útil. |
| **M2 – Interações adicionais** | **M1 + `weathersit * hr`** (avaliar também `season * hr`) | Testar se impacto do mau tempo difere por horário. Será mantida **apenas se significativa, estatisticamente justificada e coerente** com interpretação DOE. |
| **M3 – Não-linearidade** | **M2 + `temp^2`** (+ `hum^2`, se relevante) | Considerando possível efeito curvilíneo da temperatura (ótimo de conforto térmico). Testar significância da inclusão. |
| **M4 – Modelo parcimonioso** | Redução com base em significância, AIC/BIC, VIF e parcimônia. | Remoção criteriosa de termos não significativos, **sempre justificando** cada exclusão (não apenas p-valor). |

### 5.5 Etapa 5 - Seleção, Diagnóstico e Validação dos Modelos

| Critério | Métrica/Ferramenta | Utilização |
|---|---|---|
| **Explicação da variabilidade** | $R^2$ e **$R^2_{ajustado}$** | Avaliação da qualidade explicativa. Priorizar $R^2_{ajustado}$ (penaliza complexidade). |
| **Comparação entre modelos** | **AIC e BIC** | Apoio objetivo para escolha entre modelos aninhados/competitivos. |
| **Multicolinearidade** | **VIF (Variance Inflation Factor)** | Verificar principalmente entre `temp`, `season`, `mnth`. Se VIF elevado, justificar remoção de variável redundante. |
| **Diagnósticos de regressão** | Resíduos vs. Ajustados, QQ-Plot, Scale–Location, Cook's Distance, Leverage, Resíduos Studentizados. | Verificar pressupostos (linearidade, homocedasticidade, normalidade, pontos influentes). |
| **Validação do modelo preditivo** | **Divisão temporal**: Treino = 2011 (yr=0), Teste = 2012 (yr=1). | Mais coerente com dados temporais (evita vazamento temporal). Avaliar desempenho em teste com **RMSE, MAE e MAPE** (quando aplicável). |
| **Princípio de parcimônia** | Avaliação global (significância + interpretabilidade + simplicidade) | Escolha final será **o modelo mais bem justificado** (equilíbrio entre ajuste, interpretabilidade e coerência com DOE), não apenas o de melhor ajuste. |

---

## 6. Estrutura do Artigo Técnico (Formato SBC - 6 a 12 páginas)

O trabalho será escrito em **inglês**, no formato sugerido pela SBC (Brazilian Computer Society), com a seguinte estrutura:

| Seção | Conteúdo a Desenvolver |
|---|---|
| **Título** | Título objetivo e representativo do trabalho (ex.: *"Statistical Analysis and Demand Prediction for Bike Sharing: A DOE-Based Approach"*). |
| **Abstract (Resumo)** | Objetivo, dataset, metodologia (DOE + Regressão), principais resultados e conclusões (~150–250 palavras). |
| **1. Introduction** | Contexto do Bike Sharing, relevância do estudo, objetivos, justificativa da abordagem (DOE + desenvolvimento de preditores). |
| **2. Dataset and Experimental Design** | Fonte (UCI Bike Sharing Dataset), descrição das variáveis, fatores/níveis/resposta, **classificação detalhada do design** (observacional, fatorial, between/within, randomização), unidades experimentais e limitações (estrutura temporal). |
| **3. Methodology** | Descrição das etapas: EDA, pressupostos, transformações (com justificativa), testes estatísticos (ANOVA, Post-hoc), gráficos de efeitos e interações (DOE), modelagem de regressão múltipla, critérios de seleção, diagnósticos e validação temporal. |
| **4. Results** | Estatística descritiva, gráficos (boxplots, histogramas, *Main Effects*, *Interaction Plots*), resultados de ANOVA, tabelas dos modelos ajustados (coeficientes, significância, AIC/BIC, $R^2/R^2_{ajustado}$), diagnósticos e resultados de validação (treino/teste). |
| **5. Discussion** | **Interpretação crítica dos efeitos principais e interações** (visão DOE), comparação entre modelos, **justificativa da escolha do preditor final** (ajuste + significância + coerência teórica + parcimônia), implicações práticas e discussão da dependência temporal (limitações). |
| **6. Conclusion** | Principais achados, fatores mais influentes, modelo mais bem justificado, limitações do estudo e sugestões para trabalhos futuros. |
| **References** | Citação obrigatória de [1] Fanaee-T, H. & Gama, J. (2013), *Event labeling combining ensemble detectors and background knowledge*, Progress in AI, Springer. Referência também ao UCI Bike Sharing Dataset. |
| **Appendix (Opcional)** | Tabelas complementares, outputs estatísticos relevantes, gráficos adicionais e detalhes de diagnósticos. |

---

## 7. Cronograma (Conforme Enunciado)

| Data | Etapa |
|---|---|
| **26/10/2026** | **Deadline para envio das ideias, materiais e métodos** (dataset, o que será feito, metodologia) ao professor (por e-mail). |
| **22/11/2026** | **Submissão** do trabalho completo. |
| **23/11/2026** | **Apresentação** do trabalho. |

---

## 8. Observações Finais

1. **Ênfase em justificativas:** Em todos os pontos (escolha de fatores, inclusão/exclusão de interações, transformação da resposta, escolha do modelo final), as decisões serão **fundamentadas estatisticamente e com base em raciocínio DOE**, não apenas por métricas.
2. **Ponto forte do trabalho:** A **interação `workingday * hr`** será explorada em profundidade (gráficos + ANOVA + inclusão no modelo). Isso conecta perfeitamente DOE, interpretação e predição.
3. **Tratamento das limitações:** A **dependência temporal** (independência dos resíduos) será **testada, reportada e discutida** explicitamente, o que demonstra rigor metodológico.
4. **Bônus - Publicação:** O dataset já é público no UCI (com citação obrigatória). Como bônus, podemos publicar o notebook, scripts e material organizado em repositório público (GitHub/Zenodo), atendendo ao item proposto no enunciado.