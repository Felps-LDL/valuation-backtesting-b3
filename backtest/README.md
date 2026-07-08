# backtest/ — arquivos

Camada de simulação histórica e avaliação de risco-retorno de uma carteira já
selecionada pelo `model/`.

| Arquivo | Função |
|---|---|
| `engine.py` | Função `rodar_backtest()`: recebe uma carteira pronta (DataFrame de tickers), baixa os preços históricos via yFinance (2015–2024, por padrão), calcula retornos diários equal-weight, aplica um custo de transação simplificado por rebalanceamento trimestral, simula o patrimônio acumulado e alinha tudo com o Ibovespa (benchmark) para comparação. Retorna um dicionário com as séries de retornos e patrimônio (carteira e Ibovespa). |
| `metricas.py` | Conjunto de funções de métricas de risco-retorno aplicadas às séries produzidas pelo `engine.py`: `retorno_total`, `cagr`, `volatilidade_anualizada`, `sharpe_ratio`, `sortino_ratio`, `max_drawdown`/`serie_drawdown`, `calmar_ratio`, `alpha_beta` (vs. Ibovespa) e `hit_rate`. A função `calcular_todas()` agrega tudo em um único dicionário, e `exibir_metricas()` imprime formatado no terminal. |
| `__init__.py` | Arquivo vazio que marca `backtest/` como pacote Python (permite `from backtest.engine import ...`). |

## Fluxo típico

```
carteira (model/carteira.py) ──> engine.rodar_backtest() ──> {retornos, patrimonio, ...}
                                                                    │
                                                                    ▼
                                                    metricas.calcular_todas() ──> dict de métricas
```

As três hipóteses centrais do TCC (H1 Outperformance, H2 Volatilidade, H3 Drawdown)
usam, respectivamente, `Outperformance (%)`, `Volatilidade Anual (%)` e
`Máximo Drawdown (%)` calculados aqui.
