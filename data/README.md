# data/

CSVs gerados pelos scripts do projeto, mais screenshots manuais do experimento — dados de saída, não versionados como "fonte de verdade". Servem para os gráficos e para consulta. Não contém código.

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
- **São os resultados reais e finais utilizados no TCC** — os números reportados no texto do trabalho (performance, volatilidade e máximo drawdown das 10 rodadas com e sem filtros) vêm deste arquivo, não de simulações ou exemplos ilustrativos

### `retornos_carteira.csv`

- **Origem:** aba "Backtesting" de `interface/app.py`
- **Conteúdo:** série diária de retornos líquidos da última carteira testada na interface
- Regenerado a cada rodada de backtest na interface; por isso não fica versionado de forma permanente (o par mais recente foi removido no commit `12ac808`)

### `retornos_ibov.csv`

- **Origem:** aba "Backtesting" de `interface/app.py`
- **Conteúdo:** série diária de retornos do Ibovespa no mesmo período, para comparação
- Mesma observação de regeneração acima

### `resultado_comfiltro/` e `resultado_semfiltro/`

- **Origem:** screenshots manuais da aba "📊 Backtesting" de `interface/app.py`, tirados rodada a rodada durante o experimento de 10+10 (seeds 1–10)
- **Conteúdo:** `resultado_testeN_comfiltro.png` / `resultado_testeN_semfiltro.png` — equity curve e KPIs exibidos na interface para a rodada `N`, com e sem filtros respectivamente
- Servem como evidência visual complementar às métricas agregadas em `resultados_reais.csv`; não são gerados por nenhum script (diferente dos demais arquivos desta pasta)

## Reprodutibilidade

Os CSVs aqui são **saídas** de script — para reproduzi-los, basta rodar novamente os scripts correspondentes (ver [ARQUIVOS.md da raiz](../ARQUIVOS.md)). Já os PNGs em `resultado_comfiltro/`/`resultado_semfiltro/` são screenshots manuais e não são regenerados por nenhum script.
