# analise/

Gráficos finais gerados por `gerar_graficos_resultados.py` a partir de `data/resultados_reais.csv`, usados para ilustrar as 3 hipóteses do TCC. Não contém código.

## H1 — Outperformance

`h1_outperformance_real.html` / `.png`

- Barras agrupadas: performance (%) com filtros vs. sem filtros, rodada a rodada (seeds 1–10)
- Testa se os filtros fundamentalistas superam o Ibovespa de forma mais consistente que uma seleção aleatória

## H2 — Volatilidade

`h2_volatilidade_real.html` / `.png`

- Mesmo formato do H1, comparando volatilidade anualizada (%)
- Testa se os filtros reduzem o risco/dispersão dos retornos

## H3 — Drawdown

`h3_drawdown_real.html` / `.png`

- Mesmo formato do H1, comparando máximo drawdown (%)
- Testa se os filtros atenuam quedas máximas em relação ao pico

## Resumo

`resumo_real.png`

- Painel único (matplotlib) com os três gráficos lado a lado — visão resumida das três hipóteses

## Formatos

- **`.html`** — interativos, abrir no navegador
- **`.png`** — estáticos, prontos para slides do TCC
