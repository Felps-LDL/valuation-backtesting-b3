# backtest/

Camada de simulação histórica e avaliação de risco-retorno de uma carteira já selecionada pelo `model/`.

## Arquivos

### `engine.py`

Função `rodar_backtest()`:

- Recebe uma carteira pronta (DataFrame de tickers)
- Baixa os preços históricos via yFinance (2015–2024, por padrão)
- Calcula retornos diários equal-weight
- Aplica um custo de transação simplificado por rebalanceamento trimestral
- Simula o patrimônio acumulado e alinha tudo com o Ibovespa (benchmark)
- Retorna um dicionário com as séries de retornos e patrimônio (carteira e Ibovespa)

### `metricas.py`

Métricas de risco-retorno aplicadas às séries do `engine.py`:

- `retorno_total`, `cagr`, `volatilidade_anualizada`
- `sharpe_ratio`, `sortino_ratio`, `calmar_ratio`
- `max_drawdown` / `serie_drawdown`
- `alpha_beta` (vs. Ibovespa), `hit_rate`
- `calcular_todas()` — agrega tudo em um único dicionário
- `exibir_metricas()` — imprime formatado no terminal

### `__init__.py`

Arquivo vazio que marca `backtest/` como pacote Python (permite `from backtest.engine import ...`).

## Fluxo típico

```
carteira (model/carteira.py) ──> engine.rodar_backtest() ──> {retornos, patrimonio, ...}
                                                                    │
                                                                    ▼
                                                    metricas.calcular_todas() ──> dict de métricas
```

## Hipóteses do TCC

As três hipóteses centrais usam, respectivamente:

- **H1 Outperformance** → `Outperformance (%)`
- **H2 Volatilidade** → `Volatilidade Anual (%)`
- **H3 Drawdown** → `Máximo Drawdown (%)`
