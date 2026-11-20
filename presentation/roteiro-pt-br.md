# Roteiro da apresentação — versão simplificada

## 1. Problema de pesquisa

- Explicar por que a demanda horária por bicicletas é relevante.
- Apresentar os objetivos explicativo e preditivo.

## 2. Dataset

- Capital Bikeshare, Washington, D.C., 2011–2012.
- 17.379 horas observadas em 731 dias.
- Resposta: total de aluguéis por hora (`cnt`).

## 3. Desenho do estudo

- Observacional, não randomizado, fatorial natural e dependente no tempo.
- Unidade observacional: uma hora registrada.
- Associações e previsões, não efeitos causais.

## 4. Fatores e hipótese

- Hora, dia útil, clima, estação, temperatura, umidade, vento e ano.
- Hipótese principal: `hora × dia útil`.
- Explicar por que OFAT perderia o padrão de deslocamento.

## 5. Descrição dos dados

- Mostrar `response_distributions.png`.
- Média 189,46; mediana 142; intervalo 1–977.
- Resumir as médias por clima.

## 6. Efeitos e interação

- Mostrar `primary_interaction.png`.
- Interpretar os picos de manhã/fim da tarde em dias úteis.
- Interpretar o pico amplo de meio do dia em dias não úteis.
- Eta quadrado parcial da interação: 0,589.

## 7. Transformação e pressupostos

- Explicar por que avaliamos resíduos, não apenas a resposta.
- Justificar `log1p(cnt)`.
- Mostrar que heterocedasticidade e autocorrelação ainda existem.
- Explicar HAC(168) em linguagem simples.

## 8. Comparação M0–M1

- M0 possui apenas efeitos principais.
- M1 acrescenta `hora × dia útil`.
- R² ajustado aumenta de 0,824 para 0,927.
- Relacionar a melhoria ao gráfico de interação.

## 9. Predição temporal

- Explicar validação expansiva em Q2/Q3 e holdout Q4/2012.
- Mostrar `holdout_predictions.png`.
- P1: MAE 51,99; RMSE 83,07; R² fora da amostra 0,830.

## 10. Conclusões e limitações

- Hora por dia útil é a estrutura central da demanda.
- Clima e estação ainda contribuem como ajustes.
- Não há randomização e ainda existe dependência residual.
- Encerrar com a diferença entre associação e causalidade.
