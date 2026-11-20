# Roteiro da apresentação

## 1. Problema de pesquisa

- Explicar por que a demanda horária por bicicletas é relevante.
- Apresentar os objetivos explicativo e preditivo.

## 2. Dataset

- Capital Bikeshare, Washington, D.C., 2011--2012.
- 17.379 horas observadas em 731 dias.
- Resposta: total de aluguéis por hora (`cnt`).

## 3. Desenho do estudo

- Observacional, não randomizado, fatorial natural e dependente no tempo.
- Unidade observacional: uma hora registrada.
- Associações e previsões, não efeitos causais.

## 4. Fatores e hipótese

- `hr`, `workingday`, `weathersit`, `season`, além de `temp`, `hum`, `windspeed` e `yr`.
- Hipótese principal: `workingday × hr`.
- Explicar por que OFAT perderia o padrão de deslocamento.

## 5. Descrição dos dados

- Média 189,46; mediana 142; intervalo 1--977; assimetria 1,277.
- Resumir as médias por clima e por estação.

## 6. Efeitos e interação

- Mostrar `main_effects.png` e `workingday_hr_interaction.png`.
- Interpretar os picos de manhã e fim da tarde em dias úteis.
- Interpretar o pico amplo de meio do dia em dias não úteis.
- Eta quadrado parcial da interação: 0,589.

## 7. Escala da resposta e ANOVA fatorial

- Comparar `cnt` com `log1p(cnt)`: $R^2$ ajustado 0,812 contra 0,927.
- Breusch--Pagan 4281,6 contra 1676,6.
- Hora 0,878; clima 0,120; estação 0,168; ano 0,264.

## 8. Regressão e diagnósticos dos resíduos

- Mostrar a fórmula do único modelo, com 58 parâmetros.
- ACF dos resíduos: 0,612 na defasagem 1, 0,243 na 24 e 0,200 na 168.
- Ressaltar que o conjunto de teste é a principal evidência preditiva.

## 9. Predição temporal

- Treino até 30 de setembro de 2012; teste no Q4/2012 (2.168 horas).
- Mostrar `test_predictions.png`.
- MAE 45,27; RMSE 72,97; R² no teste 0,869.

## 10. Conclusões e limitações

- Hora por tipo de dia é a estrutura central da demanda.
- Clima, estação, temperatura e ano fornecem ajuste.
- Não há randomização e ainda existe dependência residual.
- Encerrar com a diferença entre associação e causalidade.
