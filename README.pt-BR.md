# Análise DOE de Compartilhamento de Bicicletas

**Português (Brasil)** | [English](README.md)

Análise estatística e predição de demanda com o UCI Bike Sharing Dataset,
desenvolvida para um trabalho de Planejamento de Experimentos. A narrativa final
foi deliberadamente concentrada em uma pergunta: como o tipo de dia altera o
perfil horário da demanda?

## Objetivos

1. Caracterizar o desenho observacional, fatorial natural e temporal dos dados.
2. Descrever os efeitos de hora, dia útil, clima, estação e covariáveis ambientais.
3. Comparar um modelo aditivo M0 com um modelo M1 contendo `hora × dia útil`.
4. Verificar pressupostos, incluindo heterocedasticidade e autocorrelação.
5. Avaliar o preditor correspondente em períodos futuros, sem divisão aleatória.

## Guia para aprender a análise

O documento [`docs/tutorial-pt-br.md`](docs/tutorial-pt-br.md) explica, passo a
passo:

- fatores, níveis, resposta e covariáveis;
- estudo observacional, DOE fatorial e OFAT;
- estatística descritiva e transformação logarítmica;
- efeitos principais e interações;
- ANOVA, p-valor e eta quadrado parcial;
- regressões M0 e M1;
- resíduos, VIF, Durbin--Watson, ACF e HAC;
- validação temporal, baseline, MAE, RMSE e R²;
- relação entre cada conceito e os scripts do projeto.

Também existe uma [versão equivalente em inglês](docs/tutorial-en.md).

## Dataset

A análise utiliza `dataset/hour.csv`, com 17.379 observações horárias do Capital
Bikeshare entre 2011 e 2012. A resposta `cnt` é o total de aluguéis. As variáveis
`casual` e `registered` não são preditoras, pois sua soma forma a resposta.

Consulte [`dataset/README.md`](dataset/README.md) para origem, licença, citação e
checksums dos arquivos.

## Modelos centrais

```text
M0: log1p(cnt) ~ efeitos principais
M1: log1p(cnt) ~ efeitos principais + hora × dia útil
```

O R² ajustado aumenta de 0,824 em M0 para 0,927 em M1. No holdout do último
trimestre de 2012, o preditor P1 obteve MAE 51,99, RMSE 83,07 e R² 0,830.

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
`src/bike_sharing/`, resultados reproduzíveis em `outputs/` e o artigo SBC em
`paper/main.tex`.

## Documentação

- Protocolo estatístico: `docs/analysis_protocol.md`
- Decisões metodológicas: `docs/decision_log.md`
- Guia didático em português: `docs/tutorial-pt-br.md`
- Guia didático em inglês: `docs/tutorial-en.md`
- Resumo dos resultados em português: `outputs/resultados_mvp-pt-br.md`
- Artigo para entrega: `paper/main.tex`
- Roteiro da apresentação: `presentation/roteiro-pt-br.md`

## Licenciamento

O dataset é distribuído pela UCI sob CC BY 4.0. Nenhuma licença foi concedida até
o momento ao código e aos textos originais deste repositório.
