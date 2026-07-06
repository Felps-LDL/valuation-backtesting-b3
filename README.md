# Sistema de Análise Fundamentalista — B3

Sistema desenvolvido como Trabalho de Conclusão de Curso (Ciência da Computação — UFPI) para
montar e testar carteiras de ações da B3 usando cinco estratégias clássicas de *value investing*
(Graham, Bazin, Lynch e ROE Equivalente), combiná-las de forma configurável e avaliar o resultado
via backtesting histórico contra o Ibovespa.

> ⚠️ **Aviso: este projeto tem finalidade exclusivamente acadêmica e não constitui recomendação
> de investimento.** Os resultados vêm de backtesting histórico sujeito às limitações descritas
> em [Limitações metodológicas](#limitações-metodológicas). Decisões de investimento são de
> responsabilidade exclusiva do usuário.

## Sumário

- [Sobre o projeto](#sobre-o-projeto)
- [Estratégias implementadas](#estratégias-implementadas)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Como usar](#como-usar)
  - [Interface web (recomendada)](#1-interface-web-recomendada)
  - [Menu de terminal](#2-menu-de-terminal)
  - [Experimento completo (10+10 rodadas)](#3-experimento-completo-1010-rodadas)
  - [Geração de gráficos](#4-geração-de-gráficos-das-hipóteses)
- [Configuração (`config.yaml`)](#configuração-configyaml)
- [Limitações metodológicas](#limitações-metodológicas)

## Sobre o projeto

O sistema busca indicadores fundamentalistas (via [yFinance](https://pypi.org/project/yfinance/))
de um universo de ~130 ações da B3, aplica critérios de valuation configuráveis, monta uma
carteira e simula sua performance histórica (2015–2024) comparando com o Ibovespa através de
métricas como CAGR, Sharpe, Sortino, Drawdown, Alpha e Beta.

## Estratégias implementadas

| Estratégia | Critério | Referência |
|---|---|---|
| **Graham 1** | P/VP × P/L ≤ 22,5 | Graham (2006) |
| **Graham 2** | Preço < √(22,5 × LPA × VPA) | Graham (2006) |
| **Bazin** | Dividend Yield ≥ 6% a.a. | Bazin (1992) |
| **Lynch** | PEG Ratio = P/L ÷ crescimento líquido < 2,0 | Lynch (2011) |
| **ROE Equivalente** | ROE ÷ P/VP ≥ 10% | Damodaran (2002) |

Os critérios podem ser combinados de três formas:

- **AND** — a ação precisa passar em todos os critérios ativos;
- **OR** — a ação passa se aprovada em pelo menos um critério;
- **k-of-n** (recomendado) — a ação precisa passar em no mínimo `k` dos critérios ativos.

Também é possível rodar um **teste sem filtros** (baseline aleatório), usado para validar se os
filtros fundamentalistas realmente geram alfa em relação a uma seleção aleatória.

## Estrutura do repositório

```
TCC/
├── carteira_investimento.py     # Ponto de entrada (dispatcher CLI)
├── menu.py                      # Menu interativo de terminal
├── rodar_experimento_completo.py# Roda 10 rodadas com filtros + 10 sem filtros
├── gerar_graficos_resultados.py # Gera gráficos (H1, H2, H3) a partir dos resultados
├── config.yaml                  # Configuração central (período, estratégias, backtest…)
├── requirements.txt
├── interface/
│   └── app.py                   # Interface web (Streamlit)
├── model/
│   ├── acoes.py                 # Classe Acao: coleta indicadores e aplica estratégias
│   ├── universo.py              # Universo de ações da B3 (yFinance)
│   └── carteira.py              # Construção da carteira (lógica AND/OR/k-of-n)
├── backtest/
│   ├── engine.py                # Motor de backtesting histórico
│   └── metricas.py              # CAGR, Sharpe, Sortino, Drawdown, Alpha/Beta…
├── data/                        # CSVs de resultados e séries de retornos
└── analise/                     # Gráficos gerados (HTML/PNG) para o TCC
```

## Requisitos

- Python 3.10 ou superior
- Conexão com a internet (os dados são buscados em tempo real via yFinance)

## Instalação

```bash
git clone <URL-do-repositório>
cd TCC

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS

pip install -r requirements.txt
```

## Como usar

### 1. Interface web (recomendada)

```bash
streamlit run interface/app.py
```

Abre em `http://localhost:8501`, com três abas:

- **🏗️ Carteira** — escolha os critérios, a lógica de combinação e a seed, e gere a carteira;
- **📊 Backtesting** — rode o backtest da carteira gerada e veja CAGR, Sharpe, Drawdown,
  equity curve e comparação com o Ibovespa;
- **🔍 Ação Individual** — analise uma ação específica (ex: `WEGE3`) critério a critério.

### 2. Menu de terminal

Alternativa rápida, sem gráficos:

```bash
python carteira_investimento.py
```

Abre um menu com três opções: analisar uma ação individual, montar uma carteira ou rodar um
backtest, tudo via `input()` no terminal.

### 3. Experimento completo (10+10 rodadas)

Reproduz o experimento usado no TCC: 10 rodadas com filtros fundamentalistas e 10 rodadas sem
filtros (baseline aleatório), salvando os resultados em `data/resultados_com_filtros.csv` e
`data/resultados_sem_filtros.csv`.

```bash
python rodar_experimento_completo.py
```

### 4. Geração de gráficos das hipóteses

A partir de `data/resultados_reais.csv`, gera os gráficos de linha usados para comparar as
hipóteses do TCC (performance, volatilidade, drawdown) e salva em `analise/`.

```bash
python gerar_graficos_resultados.py
```

## Configuração (`config.yaml`)

Todos os parâmetros do experimento ficam centralizados em `config.yaml` — evite alterar valores
diretamente no código, edite este arquivo para manter histórico e reprodutibilidade:

- `periodo` — janela temporal do backtesting (padrão: 2015–2024);
- `universo` — filtros de liquidez e P/L do universo de ações;
- `estrategias` — ativação e thresholds de cada método (Graham, Bazin, Lynch, ROE);
- `carteira` — lógica de combinação (`AND`/`OR`/`k-of-n`), `k`, tamanho da carteira e ponderação;
- `backtest` — capital inicial, custo por operação, frequência de rebalanceamento, taxa livre de
  risco (CDI);
- `benchmark` — ativo de comparação (padrão: Ibovespa, `^BVSP`).

## Limitações metodológicas

- **Look-Ahead Bias**: os indicadores fundamentalistas usados nos filtros são os atuais (do dia
  da consulta), mas aplicados retroativamente na simulação de 2015–2024. Uma avaliação rigorosa
  exigiria snapshots históricos (ex: via Economática/Bloomberg).
- **Survivorship Bias**: ações que foram deslistadas da B3 no período não estão representadas no
  universo consultado.
- **Custos de transação simplificados**: o custo por operação é distribuído diariamente como uma
  aproximação, sem modelar spread ou impacto de liquidez.

Essas limitações estão documentadas em detalhe no texto do TCC.
