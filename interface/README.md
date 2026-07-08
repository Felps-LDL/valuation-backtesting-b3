# interface/ — arquivos

Camada de apresentação: interface web interativa construída com Streamlit.

| Arquivo | Função |
|---|---|
| `app.py` | Interface web completa (`streamlit run interface/app.py`). Sidebar com as configurações (tipo de teste com/sem filtros, seed, critérios ativos, lógica de combinação, k, top-k, ponderação, período e capital do backtest). Três abas: **🏗️ Carteira** (gera e exibe a carteira com tabela + gráfico de pizza/barras via `model/`), **📊 Backtesting** (roda `backtest/engine.py`, mostra KPIs, equity curve e drawdown vs. Ibovespa) e **🔍 Ação Individual** (consulta um ticker específico via `model/acoes.py` e mostra o resultado de cada critério). É a forma recomendada de usar o sistema (a usada na defesa do TCC). |
| `__init__.py` | Arquivo vazio que marca `interface/` como pacote Python. |

## Como se relaciona com o resto do projeto

`app.py` é só uma camada visual: toda a lógica de negócio (filtros, construção de
carteira, backtest, métricas) vem de `model/` e `backtest/`. O arquivo apenas
organiza os widgets do Streamlit e chama essas funções.
