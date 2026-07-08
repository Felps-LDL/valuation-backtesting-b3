# data/ — arquivos

Não contém código — apenas CSVs gerados pelos scripts do projeto (dados de saída,
não versionados como "fonte de verdade", servem para os gráficos e para consulta).

| Arquivo / padrão | Origem | Conteúdo |
|---|---|---|
| `carteira_AAAAMMDD_HHMM_seed_N.csv` | Aba "Carteira" de `interface/app.py` | Snapshot de uma carteira gerada na interface (ticker, score, indicadores, peso), nomeado com data/hora e seed para rastreabilidade. |
| `resultados_com_filtros.csv` / `resultados_sem_filtros.csv` | `rodar_experimento_completo.py` | Métricas de cada uma das 10 rodadas (seeds 1–10) com filtros e sem filtros, respectivamente. |
| `resultados_reais.csv` | Consolidação manual/dos experimentos acima | Uma linha por rodada e tipo (`com_filtros`/`sem_filtros`) com `Performance (%)`, `Volatilidade Anual (%)` e `Máximo Drawdown (%)` — é o CSV consumido por `gerar_graficos_resultados.py` para os gráficos das 3 hipóteses do TCC. |
| `retornos_carteira.csv` | Aba "Backtesting" de `interface/app.py` | Série diária de retornos líquidos da última carteira testada na interface. |
| `retornos_ibov.csv` | Aba "Backtesting" de `interface/app.py` | Série diária de retornos do Ibovespa no mesmo período, para comparação. |

Esses arquivos são todos **saídas** — para reproduzi-los, basta rodar novamente os
scripts correspondentes (ver [ARQUIVOS.md da raiz](../ARQUIVOS.md)).
