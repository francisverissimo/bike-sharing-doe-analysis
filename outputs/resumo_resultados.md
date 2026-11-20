# Resumo dos resultados

## Dados e análise descritiva

- 17.379 horas observadas entre 2011 e 2012.
- Média de `cnt`: 189,46; mediana:
  142; desvio-padrão: 181,39.
- Intervalo: 1--977
  aluguéis por hora; assimetria 1,277.
- Há 165 horários ausentes no calendário; não foi feita imputação.
- O nível 4 da variável climática possui apenas três observações.

## Análise fatorial

- A hora possui eta quadrado parcial 0,878 e a interação
  hora por tipo de dia, 0,589.
- Clima e estação apresentam eta quadrado parcial
  0,120 e
  0,168, respectivamente.
- O único modelo na escala logarítmica usa
  58 parâmetros, com $R^2$ ajustado
  0,927, AIC
  15.916,2 e BIC 16.366,4.
- A ACF residual é 0,612 na defasagem 1,
  0,243 na defasagem 24 e 0,200 na
  defasagem 168.

## Escala da resposta e predição

- O $R^2$ ajustado é 0,812 para
  `cnt` e 0,927 para
  `log1p(cnt)`.
- O treino usa 15.211 horas até setembro de 2012; o
  teste contém 2.168 horas no último trimestre de 2012.
- MAE 45,27, RMSE 72,97 e
  $R^2$ 0,869 no teste.

Os resultados representam associações e previsões em dados observacionais não
randomizados; eles não demonstram causalidade.
