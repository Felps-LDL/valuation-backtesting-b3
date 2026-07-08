# Raiz do projeto — arquivos

Referência rápida do que cada arquivo faz, para apoiar a apresentação do TCC.
Para a visão geral do sistema, ver [README.md](README.md).

| Arquivo | Função |
|---|---|
| `carteira_investimento.py` | Ponto de entrada em CLI. Só imprime o cabeçalho do sistema e chama o loop do `menu.py`. Não tem lógica própria — é um "dispatcher". |
| `menu.py` | Menu interativo de terminal (`input()`). Três opções: analisar uma ação individual, montar uma carteira, ou rodar um backtest — tudo via texto, sem gráficos. Alternativa rápida à interface web. |
| `rodar_experimento_completo.py` | Reproduz o experimento do TCC: roda 10 rodadas com filtros fundamentalistas (seeds 1–10) e 10 rodadas sem filtros (baseline aleatório), calcula as métricas de cada rodada e salva os resultados em `data/resultados_com_filtros.csv` e `data/resultados_sem_filtros.csv`. |
| `gerar_graficos_resultados.py` | Lê `data/resultados_reais.csv` e gera os gráficos de barras agrupadas (com vs. sem filtros, rodada a rodada) usados para comparar as 3 hipóteses do TCC (H1 Performance, H2 Volatilidade, H3 Drawdown). Salva HTML interativo e PNG em `analise/`. |
| `config.yaml` | Configuração central do experimento (período do backtest, universo, thresholds de cada estratégia, lógica de combinação da carteira, custos, taxa livre de risco, benchmark). Editar aqui em vez de mexer em valores fixos no código. |
| `requirements.txt` | Dependências Python do projeto (yfinance, pandas, streamlit, plotly, matplotlib/seaborn, pyyaml, kaleido, etc.). |

## Como esses arquivos se encaixam

```
carteira_investimento.py ──> menu.py ──> model/ + backtest/ (CLI, sem gráficos)
interface/app.py ──────────> model/ + backtest/ (interface web, recomendada)
rodar_experimento_completo.py ──> model/ + backtest/ ──> data/resultados_*.csv
gerar_graficos_resultados.py ──> data/resultados_reais.csv ──> analise/*.html, *.png
```
