# Resumo dos resultados

## Dados e análise descritiva

- 17.379 horas observadas entre 2011 e 2012.
- Média de `cnt`: 189,46; mediana:
  142; desvio-padrão: 181,39.
- Intervalo: 1--977
  aluguéis por hora; assimetria 1,277.
- Há 165 horários ausentes no calendário; não foi feita imputação.
- Os níveis 3 e 4 foram agrupados porque o nível 4 tem apenas três observações.
- Média de aluguéis por condição climática: claro/parcialmente nublado
  204,87, névoa/nublado
  175,17 e precipitação/tempo adverso
  111,50.

## Delineamento, ANOVA e sequência de modelos

- ANOVA one-way é reportada para os quatro fatores em `log1p(cnt)`.
- A hora possui eta quadrado parcial 0,866 e a interação
  hora por tipo de dia, 0,569.
- Condição climática e estação apresentam eta quadrado parcial
  0,124 e
  0,197, respectivamente.
- O teste de Tukey HSD em `log1p(cnt)` compara as três condições climáticas
  agrupadas; todas as 3 de 3 comparações ajustadas
  são significativas.
- M0--M3 foram comparados nos dados de treino de 2011. O BIC selecionou
  M1, mantido como M4; o modelo selecionado usa
  56 parâmetros, com $R^2$ ajustado
  0,920, AIC
  8.277,9 e BIC 8.673,5.
- A ACF residual é 0,593 na defasagem 1,
  0,201 na defasagem 24 e
  0,138 na defasagem 168.
- Durbin--Watson é 0,814; o VIF máximo é
  24,0; Levene e Bartlett são significativos.

## Escala da resposta e predição

- Quatro escalas foram comparadas: bruta, raiz quadrada, `log1p(cnt)` e
  Box--Cox (expoente estimado 0,315).
- `log1p(cnt)` foi mantida pela melhor acurácia no teste e interpretação direta.
- O treino usa 8.645 horas em 2011; o teste contém
  8.734 horas em 2012.
- MAE 87,67, RMSE 125,19 e
  $R^2$ 0,641 no teste.

Os resultados representam associações e previsões em dados observacionais não
randomizados; eles não demonstram causalidade.
