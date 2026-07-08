# model/ — arquivos

Camada de domínio: representa uma ação, o universo de ações da B3 e a lógica de
construção de carteiras. Não faz backtest nem interface — só filtragem e seleção.

| Arquivo | Função |
|---|---|
| `acoes.py` | Classe `Acao`. Busca indicadores fundamentalistas de um ticker via yFinance (preço, P/VP, P/L, ROE, DY calculado pelo histórico real de dividendos, VPA, LPA, payout, crescimento) e implementa as 5 estratégias de valuation como métodos que retornam `True`/`False`: `GetGraham1`, `GetGraham2`, `GetMetodoBazin`, `GetRoeEquivalente`, `GetMetodoLynch`. Também calcula um score (0–5) de quantos critérios a ação passou. |
| `universo.py` | Define a lista curada de ~130 tickers da B3 (`_TICKERS_B3`) e a função `obter_dataframe_universo()`, que consulta o yFinance para cada um, valida os dados (preço > 0) e devolve um DataFrame com `cotacao`, `pvp`, `pl`, `roe`, `dy` — a matéria-prima usada por `carteira.py`. |
| `carteira.py` | Função `construir_carteira()`: embaralha o universo (com seed, para reprodutibilidade) e aplica os critérios ativados de `acoes.py` segundo a lógica escolhida — **AND** (passa em todos), **OR** (passa em pelo menos um) ou **k-of-n** (passa em no mínimo `k` critérios). Ordena por score, seleciona as `top_k` melhores ações e calcula o peso de cada uma (igual ou proporcional ao score). Também implementa o modo **sem filtros** (baseline aleatório, usado para comparar com o teste com filtros e validar a Hipótese 1 do TCC). |

## Fluxo típico

```
universo.py (busca yFinance)
      │
      ▼
carteira.py (embaralha + aplica critérios de acoes.py + seleciona top_k)
      │
      ▼
DataFrame da carteira final ──> backtest/engine.py
```
