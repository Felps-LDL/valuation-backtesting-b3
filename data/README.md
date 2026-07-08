# data/

CSVs gerados pelos scripts do projeto — dados de saída, não versionados como "fonte de verdade". Servem para os gráficos e para consulta. Não contém código.

## Arquivos

### `carteira_AAAAMMDD_HHMM_seed_N.csv`

- **Origem:** aba "Carteira" de `interface/app.py`
- **Conteúdo:** snapshot de uma carteira gerada na interface (ticker, score, indicadores, peso)
- Nomeado com data/hora e seed para rastreabilidade

### `resultados_com_filtros.csv` / `resultados_sem_filtros.csv`

- **Origem:** `rodar_experimento_completo.py`
- **Conteúdo:** métricas de cada uma das 10 rodadas (seeds 1–10), com filtros e sem filtros respectivamente

### `resultados_reais.csv`

- **Origem:** consolidação manual/dos experimentos acima
- **Conteúdo:** uma linha por rodada e tipo (`com_filtros`/`sem_filtros`) com `Performance (%)`, `Volatilidade Anual (%)` e `Máximo Drawdown (%)`
- É o CSV consumido por `gerar_graficos_resultados.py` para os gráficos das 3 hipóteses

### `retornos_carteira.csv`

- **Origem:** aba "Backtesting" de `interface/app.py`
- **Conteúdo:** série diária de retornos líquidos da última carteira testada na interface

### `retornos_ibov.csv`

- **Origem:** aba "Backtesting" de `interface/app.py`
- **Conteúdo:** série diária de retornos do Ibovespa no mesmo período, para comparação

## Reprodutibilidade

Todos os arquivos aqui são **saídas** — para reproduzi-los, basta rodar novamente os scripts correspondentes (ver [ARQUIVOS.md da raiz](../ARQUIVOS.md)).
