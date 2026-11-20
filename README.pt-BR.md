# Análise DOE de Compartilhamento de Bicicletas

**Português (Brasil)** | [English](README.md)

Análise estatística e predição de demanda com o UCI Bike Sharing Dataset,
desenvolvida para um trabalho de Planejamento de Experimentos. A análise segue a
proposta com um único modelo de regressão.

## Objetivos

1. Caracterizar o desenho observacional, fatorial natural e temporal dos dados.
2. Descrever `cnt` e os efeitos de `hr`, `workingday`, `weathersit` e `season`.
3. Apresentar gráficos de efeitos principais e a interação `workingday × hr`.
4. Comparar `cnt` e `log1p(cnt)` e verificar diagnósticos básicos dos resíduos.
5. Ajustar um único modelo com `hr × workingday`, `weather_group`, `season`,
   `temp`, `hum`, `windspeed` e `yr`, e comparar as três condições climáticas com
   Tukey HSD.
6. Avaliar o modelo em uma divisão temporal entre treino e teste, com MAE, RMSE e
   R².

## Guia para aprender a análise

O documento [`docs/tutorial-pt-br.md`](docs/tutorial-pt-br.md) explica, passo a
passo:

- fatores, níveis, resposta e covariáveis;
- estudo observacional, DOE fatorial e OFAT;
- estatística descritiva e transformação logarítmica;
- efeitos principais e interações;
- ANOVA, valor-p e eta quadrado parcial;
- o modelo de regressão único;
- diagnósticos básicos dos resíduos e ACF;
- divisão temporal, MAE, RMSE e R²;
- relação entre cada conceito e os scripts do projeto.

Também existe uma [versão equivalente em inglês](docs/tutorial-en.md).

O artigo no formato SBC também é mantido nas duas línguas:

- [Artigo em inglês](paper/main.tex) — fonte canônica para submissão
- [Artigo em português brasileiro](paper/main-pt-br.tex) — versão para estudo e revisão

## Base de dados

A análise utiliza `dataset/hour.csv`, com 17.379 observações horárias do Capital
Bikeshare entre 2011 e 2012. A resposta `cnt` é o total de aluguéis. As variáveis
`casual` e `registered` não são preditoras, pois sua soma forma a resposta.

Consulte [`dataset/README.md`](dataset/README.md) para origem, licença, citação e
checksums dos arquivos.

## Modelo central

```text
log1p(cnt) ~ hr * workingday + weather_group + season + temp + hum + windspeed + yr
```

`weather_group` reúne os níveis brutos 3 e 4 de `weathersit`, pois o nível 4 tem
apenas três horas. O modelo possui 57 parâmetros e $R^2$ ajustado 0,927 na amostra completa. No
conjunto de teste do último trimestre de 2012 (2.168 horas), obteve MAE 45,27,
RMSE 72,97 e R² 0,869. A interação `hora × tipo de dia` possui eta quadrado
parcial 0,589.

Esses resultados representam associações e capacidade preditiva; eles não
demonstram causalidade porque não houve randomização.

## Execução

Python 3.10 é a versão de referência.

```bash
make setup
make all
make lint
make test
```

Os scripts numerados ficam em `analysis/`, funções compartilhadas em
`src/bike_sharing/`, resultados reproduzíveis em `outputs/` e os artigos SBC em
`paper/` (inglês e português brasileiro).

## Documentação

- Protocolo estatístico: `docs/analysis_protocol.md`
- Decisões metodológicas: `docs/decision_log.md`
- Guia didático em português: `docs/tutorial-pt-br.md`
- Guia didático em inglês: `docs/tutorial-en.md`
- Resumo dos resultados em português: `outputs/resumo_resultados.md`
- Artigo para entrega (inglês): `paper/main.tex`
- Artigo em português brasileiro: `paper/main-pt-br.tex`
- Roteiro da apresentação: `presentation/roteiro-pt-br.md`

## Licenciamento

O dataset é distribuído pela UCI sob CC BY 4.0. Nenhuma licença foi concedida até
o momento ao código e aos textos originais deste repositório.
