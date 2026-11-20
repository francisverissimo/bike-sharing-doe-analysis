# Resumo dos resultados do MVP simplificado

## Dados

- 17.379 observações horárias de 2011 a 2012.
- Média de `cnt`: 189,46; mediana:
  142; desvio-padrão: 181,39.
- Intervalo: 1–977
  aluguéis por hora observada.
- Há 165 timestamps ausentes na sequência horária; eles não foram imputados.
- Os níveis meteorológicos 3 e 4 foram agrupados; o nível 4 possui somente 3 casos.

## Resultados descritivos

- Média com tempo claro/parcialmente nublado: 204,87.
- Média com névoa/nublado: 175,17.
- Média com precipitação/tempo adverso: 111,50.
- A correlação entre `temp` e `atemp` é 0,988; por isso `atemp` foi excluída.

## DOE e regressão explicativa

- A interação principal `hora × dia útil` possui eta quadrado parcial
  0,589.
- O fator hora possui eta quadrado parcial 0,878 no M1.
- O M1 possui R² ajustado 0,927, AIC
  15.914,2 e BIC 16.356,7
  para `log1p(cnt)`.
- O Durbin–Watson residual é 0,775;
  ainda há
  dependência temporal, portanto são apresentados erros-padrão HAC(168).

## Predição

- O P1, que contém `hora × dia útil`, foi selecionado na validação expansiva de
  Q2 e Q3 de 2012.
- No holdout Q4/2012 (n=2.168), o P1 obteve
  MAE 51,99, RMSE 83,07, R²
  0,830 e RMSLE 0,524.

Os resultados representam associações em dados observacionais não randomizados;
eles não demonstram causalidade.
