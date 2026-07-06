"""
backtest/engine.py
==================

DESCRIÇÃO:
    Motor de backtesting: simula execução histórica de uma carteira
    de 2015 a 2024 com rebalanceamento trimestral.

REFERÊNCIAS:
    - TCC seção 3.4: Camada de Execução do Backtesting
    - TCC seção 4: Configuração do Experimento
    - TCC seção 3.7: Limitações (look-ahead bias, custos simplificados)

FLUXO:
    1. Recebe carteira pré-selecionada (obrigatório)
    2. Baixa preços históricos via yFinance (2015-2024)
    3. Calcula retornos diários (pct_change)
    4. Aplica custo operacional (0,1% por transação)
    5. Simula patrimônio acumulado
    6. Alinha com Ibovespa para comparação
    7. Retorna séries de retornos, patrimônio, etc.

PARÂMETROS PRINCIPAIS (config.yaml):
    - frequencia_meses: 3 (rebalanceamento trimestral)
    - capital_inicial: 100.000,00 (R$)
    - custo_operacao: 0.001 (0,1% por transação, entrada + saída = 0,2%)
    - taxa_livre_risco_anual: 0,1075 (CDI 2024)

COLUNAS RETORNADAS:
    {
        "retornos": pd.Series — retornos diários líquidos (%)
        "retornos_ibov": pd.Series — retornos Ibovespa
        "patrimonio": pd.Series — patrimônio acumulado (carteira)
        "patrimonio_ibov": pd.Series — patrimônio acumulado (Ibovespa)
        "carteira": pd.DataFrame — ações selecionadas
        "tickers_validos": list — tickers com dados ≥80%
        "teste_tipo": str — "com_filtros" ou "sem_filtros"
    }

TRATAMENTO DE PROVENTOS:
    DY já está incluído nos retornos diários (via pct_change).
    Não há separação explícita de "caixa" no modelo.

CUSTOS DE TRANSAÇÃO:
    Simplificado: (custo × 2) / dias_por_rebalanceamento
    └─ Assume entrada + saída a cada rebalanceamento
    └─ Distribuído em custo diário
    └─ Maior que realidade em spreads/impacto, menor em corretagem

LIMITAÇÕES (TCC 3.7):
    - Survivorship Bias: ações deslistadas não estão representadas
    - Look-Ahead Bias: filtros aplicados com dados de HOJE
    - Sem spread ni impacto de liquidez
    - CDI simplificado (não reflete taxa real do período)

EXEMPLO DE USO:
    >>> from model.carteira import construir_carteira
    >>> from model.universo import obter_dataframe_universo
    >>> from backtest.engine import rodar_backtest
    >>>
    >>> df_u = obter_dataframe_universo()
    >>> df_c = construir_carteira(df_u, seed=42)
    >>> res = rodar_backtest(carteira=df_c)
    >>> print(f"Patrimônio final: R${res['patrimonio'].iloc[-1]:.2f}")
"""

import yaml
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import date
from dateutil.relativedelta import relativedelta
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


def _cfg() -> dict:
    """Carrega config.yaml centralizado."""
    p = Path(__file__).parent.parent / "config.yaml"
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


def _baixar_precos(tickers: list, inicio: str, fim: str) -> pd.DataFrame:
    """
    Baixa preços históricos ajustados via yFinance.
    
    Args:
        tickers (list): Lista de tickers sem sufixo (ex: ["WEGE3", "VALE3"])
        inicio (str): Data início (YYYY-MM-DD)
        fim (str): Data fim (YYYY-MM-DD)
    
    Returns:
        pd.DataFrame: Índice=datas, colunas=tickers, valores=preço de fechamento ajustado
    
    TRATAMENTO DE ERRO:
        - Timeout após 10s
        - Ticker sem dados retorna coluna vazia (after dropna)
        - Progress desligado para evitar poluição de log
    """
    if not tickers:
        return pd.DataFrame()
    
    symbols = [f"{t}.SA" for t in tickers]
    try:
        dados = yf.download(
            symbols,
            start=inicio,
            end=fim,
            auto_adjust=True,
            progress=False,
            timeout=10,
        )
        
        if dados.empty:
            print(f"  ⚠️  Nenhum dado retornado para {len(tickers)} tickers")
            return pd.DataFrame()
        
        if isinstance(dados.columns, pd.MultiIndex):
            precos = dados["Close"]
        else:
            precos = pd.DataFrame(dados["Close"])
        
        precos.columns = [c.replace(".SA", "") if isinstance(c, str) else c 
                         for c in precos.columns]
        
        return precos.dropna(how="all")
        
    except Exception as e:
        print(f"  ⚠️  Erro ao baixar preços: {type(e).__name__}")
        return pd.DataFrame()


def rodar_backtest(
    carteira: pd.DataFrame = None,
    data_inicio: str = None,
    data_fim: str = None,
    capital_inicial: float = None,
    teste_sem_filtros: bool = False,
) -> dict:
    """
    Executa backtesting completo de uma carteira.
    
    Args:
        carteira (pd.DataFrame): Obrigatório. DataFrame com colunas [ticker, ...]
                                Gerada via construir_carteira()
        data_inicio (str): Início do backtest (padrão: config.yaml)
        data_fim (str): Fim do backtest (padrão: hoje)
        capital_inicial (float): Capital em R$ (padrão: config.yaml)
        teste_sem_filtros (bool): Flag para marcar tipo de teste nos resultados
    
    Returns:
        dict: {
            "retornos": pd.Series — retornos diários líquidos,
            "retornos_ibov": pd.Series — retornos Ibovespa,
            "patrimonio": pd.Series — patrimônio acumulado,
            "patrimonio_ibov": pd.Series — patrimônio Ibovespa,
            "carteira": pd.DataFrame — ações simuladas,
            "tickers_validos": list — tickers com dados,
            "teste_tipo": str — "com_filtros" ou "sem_filtros"
        }
        Retorna {} vazio se falhar.
    
    RAISES:
        ValueError: Se carteira for None ou vazia
    
    FLUXO:
        1. Valida carteira (obrigatória)
        2. Baixa preços históricos (tickers da carteira)
        3. Filtra: mantém apenas tickers com ≥80% de dados
        4. Baixa Ibovespa como benchmark
        5. Calcula retornos diários
        6. Aplica custos de transação
        7. Alinha datas carteira + Ibovespa
        8. Simula patrimônio acumulado
    
    EXEMPLO:
        >>> from backtest.engine import rodar_backtest
        >>> res = rodar_backtest(carteira=df_c, capital_inicial=100_000)
        >>> print(f"CAGR: {(res['patrimonio'].iloc[-1] / 100_000) ** (1/10) - 1:.2%}")
    
    NOTAS:
        - Equal-weight: cada ação tem peso idêntico no retorno diário
        - Custos distribuídos diariamente (simplificação)
        - Alinhamento de datas: usa interseção de índices
    """
    
    if carteira is None or carteira.empty:
        raise ValueError("❌ Carteira não pode estar vazia!")
    
    cfg    = _cfg()
    cfg_bt = cfg.get("backtest", {})
    cfg_p  = cfg.get("periodo",  {})
    cfg_bm = cfg.get("benchmark", {})

    data_inicio     = data_inicio     or cfg_p.get("inicio",  "2015-01-01")
    data_fim        = data_fim        or cfg_p.get("fim",      date.today().isoformat())
    capital_inicial = capital_inicial or cfg_bt.get("capital_inicial", 100_000.0)
    custo           = cfg_bt.get("custo_operacao", 0.001)
    freq_meses      = cfg_bt.get("frequencia_meses", 3)
    bench_ticker    = cfg_bm.get("ticker", "^BVSP")

    print(f"\n{'='*55}")
    print(f"  BACKTESTING | {data_inicio} → {data_fim}")
    print(f"  Custo por operação: {custo*100:.1f}% | "
          f"Rebalanceamento: {freq_meses} meses")
    if teste_sem_filtros:
        print(f"  ⚠️  TESTE SEM FILTROS — Baseline (aleatório)")
    else:
        print(f"  ✅ TESTE COM FILTROS — Multicritério")
    print(f"{'='*55}")

    print("\n📋 Usando carteira pré-selecionada...")
    df_cart = carteira.copy()
    
    tickers = df_cart["ticker"].tolist()
    print(f"  ✅ {len(tickers)} ações carregadas")
    print(f"  Tickers: {', '.join(tickers[:5])}...")

    print(f"\n⬇️  Baixando preços ({data_inicio} → {data_fim})...")
    precos = _baixar_precos(tickers, data_inicio, data_fim)

    if precos.empty:
        print("❌ Sem dados de preços.")
        return {}

    limiar = int(len(precos) * 0.8)
    precos = precos.dropna(axis=1, thresh=limiar).ffill()
    tickers_validos = precos.columns.tolist()
    print(f"  ✅ {len(tickers_validos)} tickers com dados suficientes")

    if len(tickers_validos) == 0:
        print("❌ Nenhum ticker com dados válidos")
        return {}

    print(f"\n⬇️  Baixando {bench_ticker} como benchmark...")
    try:
        ibov = yf.download(
            bench_ticker, start=data_inicio, end=data_fim,
            auto_adjust=True, progress=False, timeout=10
        )["Close"].squeeze()
        ibov.name = "IBOV"
    except Exception as e:
        print(f"  ⚠️  Erro ao baixar benchmark: {type(e).__name__}")
        ibov = pd.Series(dtype=float, name="IBOV")

    ret_acoes = precos.pct_change().dropna()
    ret_cart = ret_acoes.mean(axis=1)
    ret_cart.name = "Carteira"

    dias_por_rebalanceamento = int(freq_meses * 21)
    custo_diario = (custo * 2) / dias_por_rebalanceamento

    ret_cart_liquido = ret_cart - custo_diario
    ret_cart_liquido.name = "Carteira (líquido)"

    if not ibov.empty:
        ret_ibov = ibov.pct_change().dropna()
        ret_ibov.name = "IBOV"
        datas = ret_cart_liquido.index.intersection(ret_ibov.index)
        ret_cart_liquido = ret_cart_liquido.loc[datas]
        ret_ibov         = ret_ibov.loc[datas]
    else:
        ret_ibov = pd.Series(dtype=float, name="IBOV")

    patrimonio = capital_inicial * (1 + ret_cart_liquido).cumprod()
    patrimonio.name = "Carteira"

    if not ret_ibov.empty:
        pat_ibov = capital_inicial * (1 + ret_ibov).cumprod()
        pat_ibov.name = "IBOV"
    else:
        pat_ibov = pd.Series(dtype=float, name="IBOV")

    print(f"\n✅ Backtest concluído | "
          f"{len(ret_cart_liquido)} dias úteis simulados")

    return {
        "retornos":         ret_cart_liquido,
        "retornos_ibov":    ret_ibov,
        "patrimonio":       patrimonio,
        "patrimonio_ibov":  pat_ibov,
        "carteira":         df_cart,
        "tickers_validos":  tickers_validos,
        "teste_tipo":       "sem_filtros" if teste_sem_filtros else "com_filtros",
    }