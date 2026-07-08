# analise/ — arquivos

Não contém código — são os gráficos finais gerados por `gerar_graficos_resultados.py`
a partir de `data/resultados_reais.csv`, usados para ilustrar as 3 hipóteses do TCC.

| Arquivo | Hipótese | Conteúdo |
|---|---|---|
| `h1_outperformance_real.html` / `.png` | **H1 — Outperformance** | Gráfico de barras agrupadas comparando a performance (%) da carteira com filtros vs. sem filtros, rodada a rodada (seeds 1–10). Testa se os filtros fundamentalistas superam o Ibovespa de forma mais consistente que uma seleção aleatória. |
| `h2_volatilidade_real.html` / `.png` | **H2 — Volatilidade** | Mesmo formato, comparando a volatilidade anualizada (%) — testa se os filtros reduzem o risco/dispersão dos retornos. |
| `h3_drawdown_real.html` / `.png` | **H3 — Drawdown** | Mesmo formato, comparando o máximo drawdown (%) — testa se os filtros atenuam quedas máximas em relação ao pico. |
| `resumo_real.png` | H1 + H2 + H3 | Painel único (matplotlib) com os três gráficos de barras lado a lado, para uma visão resumida das três hipóteses. |

Os arquivos `.html` são interativos (abrir no navegador); os `.png` são estáticos,
prontos para colar em slides do TCC.
