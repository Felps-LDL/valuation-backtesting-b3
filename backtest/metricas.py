"""
backtest/metricas.py
====================

DESCRIÇÃO:
    Calcula métricas de performance ajustadas ao risco para carteiras.

REFERÊNCIAS:
    - TCC seção 2.1.6: Simulação Histórica e Métricas de Risco-Retorno
    - TCC seção 3.5: Camada de Métricas de Avaliação
    - TCC seção 5: Resultados (tabelas com CAGR, Sharpe, Sortino, MDD)

MÉTRICAS IMPLEMENTADAS:
    
    RETORNO:
        - Retorno Total (%) : (1 + r).prod() - 1
        - CAGR (% a.a.)     : retorno_total ^ (1 / anos)
        - Outperformance (%) : retorno_carteira - retorno_ibovespa
    
    RISCO:
        - Volatilidade Anual : std(r) × √252
        - Máximo Drawdown (%) : (patrimônio - pico) / pico (mínimo)
    
    RISCO-RETORNO:
        - Sharpe Ratio (Sharpe, 1966) : (retorno - rf) / volatilidade
        - Sortino Ratio : (retorno - rf) / downside_deviation
        - Calmar Ratio : CAGR / |MDD|
    
    RISCO SISTEMÁTICO:
        - Beta : cov(carteira, benchmark) / var(benchmark)
        - Alpha (anual) : (retorno_carteira - beta × retorno_benchmark) × 252
    
    QUALIDADE:
        - Hit Rate (%) : (dias_ganho / dias_total) × 100

PARÂMETROS GLOBAIS (config.yaml):
    - taxa_livre_risco_anual: 0.1075 (CDI)
    - dias_uteis_ano: 252

EXEMPLO DE USO:
    >>> from backtest.metricas import calcular_todas, exibir_metricas
    >>> m = calcular_todas(retornos, patrimonio, retornos_ibov)
    >>> exibir_metricas(m)

NOTAS:
    - Retornos esperados em Series pandas (índice=datas, valores=retorno%)
    - Patrimônio esperado em Series (índice=datas, valores=R$)
    - Métricas retornadas em dict (facilita export/CSV)
    - CDI anualizado: (1 + CDI_anual) ^ (1/252) - 1
"""

import yaml
import numpy as np
import pandas as pd
from pathlib import Path


def _cfg() -> dict:
    """Carrega config.yaml centralizado."""
    p = Path(__file__).parent.parent / "config.yaml"
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


_BT  = _cfg().get("backtest", {})
CDI_ANUAL  = _BT.get("taxa_livre_risco_anual", 0.1075)
DIAS_ANO   = _BT.get("dias_uteis_ano", 252)
CDI_DIARIO = (1 + CDI_ANUAL) ** (1 / DIAS_ANO) - 1


# ─────────────────────────────────────────────────────────────────
# MÉTRICAS INDIVIDUAIS
# ─────────────────────────────────────────────────────────────────

def retorno_total(r: pd.Series) -> float:
    """
    Retorno total acumulado (%).
    
    Args:
        r (pd.Series): Retornos diários em decimal (0.05 = 5%)
    
    Returns:
        float: Retorno acumulado em decimal
    
    EXEMPLO:
        >>> r_total = retorno_total(retornos)  # 3.45 → 345%
    """
    return float((1 + r).prod() - 1)


def cagr(r: pd.Series) -> float:
    """
    Compound Annual Growth Rate (taxa de crescimento anual composta).
    
    Args:
        r (pd.Series): Retornos diários
    
    Returns:
        float: CAGR em decimal (0.12 = 12% a.a.)
    
    FÓRMULA:
        CAGR = (Valor_Final / Valor_Inicial) ^ (1 / anos) - 1
    
    EXEMPLO:
        >>> cagr_valor = cagr(retornos)  # 0.156 → 15,6% a.a.
    """
    n_anos = len(r) / DIAS_ANO
    if n_anos <= 0:
        return 0.0
    return float((1 + r).prod() ** (1 / n_anos) - 1)


def volatilidade_anualizada(r: pd.Series) -> float:
    """
    Volatilidade anualizada (desvio-padrão dos retornos × √252).
    
    Args:
        r (pd.Series): Retornos diários
    
    Returns:
        float: Volatilidade anual em decimal (0.25 = 25% a.a.)
    
    INTERPRETAÇÃO:
        Risco oscilatório (upside e downside)
        Maior volatilidade = maior dispersão de retornos
    
    EXEMPLO:
        >>> vol = volatilidade_anualizada(retornos)  # 0.185 → 18,5% a.a.
    """
    return float(r.std() * np.sqrt(DIAS_ANO))


def sharpe_ratio(r: pd.Series, rf: float = CDI_DIARIO) -> float:
    """
    Sharpe Ratio (retorno excedente / volatilidade total).
    
    Args:
        r (pd.Series): Retornos diários
        rf (float): Taxa livre de risco diária (padrão: CDI)
    
    Returns:
        float: Sharpe Ratio anualizado
    
    REF: Sharpe (1966)
    
    INTERPRETAÇÃO:
        > 1.0 : Bom
        > 2.0 : Muito bom
        > 3.0 : Excepcional
    
    EXEMPLO:
        >>> sharpe = sharpe_ratio(retornos)  # 1.24 → muito bom
    """
    vol = r.std()
    if vol == 0:
        return 0.0
    return float(((r - rf).mean() / vol) * np.sqrt(DIAS_ANO))


def sortino_ratio(r: pd.Series, rf: float = CDI_DIARIO) -> float:
    """
    Sortino Ratio (penaliza apenas volatilidade negativa).
    
    Args:
        r (pd.Series): Retornos diários
        rf (float): Taxa livre de risco diária
    
    Returns:
        float: Sortino Ratio anualizado
    
    DIFERENÇA VS SHARPE:
        Sharpe : penaliza toda volatilidade (upside + downside)
        Sortino : penaliza só downside (risco de queda)
        → Sortino > Sharpe para carteiras defensivas
    
    EXEMPLO:
        >>> sortino = sortino_ratio(retornos)  # 1.58 → muito bom
    """
    neg = r[r < 0]
    dv  = neg.std() * np.sqrt(DIAS_ANO)
    if dv == 0:
        return 0.0
    return float(((r - rf).mean() * DIAS_ANO) / dv)


def max_drawdown(patrimonio: pd.Series) -> float:
    """
    Máximo Drawdown (maior queda do pico ao vale em %).
    
    Args:
        patrimonio (pd.Series): Série de patrimônio acumulado
    
    Returns:
        float: Drawdown máximo em decimal (-0.35 = -35%)
    
    INTERPRETAÇÃO:
        Mede risco de cauda e resiliência em crises
        Quanto mais próximo de 0 (menos negativo), melhor
    
    EXEMPLO:
        >>> mdd = max_drawdown(patrimonio)  # -0.427 → -42,7%
    """
    pico = patrimonio.cummax()
    dd   = (patrimonio - pico) / pico
    return float(dd.min())


def serie_drawdown(patrimonio: pd.Series) -> pd.Series:
    """
    Retorna série completa de drawdown (para visualização).
    
    Args:
        patrimonio (pd.Series): Série de patrimônio
    
    Returns:
        pd.Series: Drawdown em cada data (para gráfico)
    
    EXEMPLO:
        >>> dd_serie = serie_drawdown(patrimonio)
        >>> plt.plot(dd_serie)  # Visualiza evolução do drawdown
    """
    pico = patrimonio.cummax()
    return (patrimonio - pico) / pico


def calmar_ratio(r: pd.Series, patrimonio: pd.Series) -> float:
    """
    Calmar Ratio (CAGR / |Máximo Drawdown|).
    
    Args:
        r (pd.Series): Retornos diários
        patrimonio (pd.Series): Série de patrimônio
    
    Returns:
        float: Calmar Ratio
    
    INTERPRETAÇÃO:
        > 1.0 : Boa compensação risco-retorno
        > 2.0 : Excelente
    
    EXEMPLO:
        >>> calmar = calmar_ratio(retornos, patrimonio)  # 0.45 → aceitável
    """
    dd = abs(max_drawdown(patrimonio))
    if dd == 0:
        return 0.0
    return float(cagr(r) / dd)


def alpha_beta(r_cart: pd.Series, r_bench: pd.Series) -> tuple:
    """
    Alpha anualizado e Beta vs benchmark via OLS.
    
    Args:
        r_cart (pd.Series): Retornos diários da carteira
        r_bench (pd.Series): Retornos diários do benchmark
    
    Returns:
        tuple: (alpha_anual, beta)
    
    INTERPRETAÇÃO:
        Alpha > 0 : Carteira gera retorno acima do esperado
        Beta ≈ 1.0 : Carteira move-se com o mercado
        Beta > 1.0 : Carteira é mais agressiva
        Beta < 1.0 : Carteira é mais defensiva
    
    EXEMPLO:
        >>> alpha, beta = alpha_beta(ret_cart, ret_ibov)
        >>> print(f"Alpha: {alpha*100:.2f}% a.a., Beta: {beta:.2f}")
    """
    df = pd.DataFrame({"c": r_cart, "b": r_bench}).dropna()
    if len(df) < 30:
        return 0.0, 1.0
    cov  = np.cov(df["c"], df["b"])
    beta = float(cov[0, 1] / cov[1, 1])
    alpha_d = float(df["c"].mean() - beta * df["b"].mean())
    return float(alpha_d * DIAS_ANO), beta


def hit_rate(r: pd.Series) -> float:
    """
    Percentual de dias com retorno positivo.
    
    Args:
        r (pd.Series): Retornos diários
    
    Returns:
        float: Hit rate em % (50-100)
    
    INTERPRETAÇÃO:
        > 50% : Mais dias de ganho que perda
        > 60% : Muito bom
    
    EXEMPLO:
        >>> hr = hit_rate(retornos)  # 55.3 → 55,3% dos dias tiveram ganho
    """
    return float((r > 0).mean() * 100)


# ─────────────────────────────────────────────────────────────────
# CÁLCULO COMPLETO
# ─────────────────────────────────────────────────────────────────

def calcular_todas(
    retornos: pd.Series,
    patrimonio: pd.Series,
    retornos_ibov: pd.Series = None,
) -> dict:
    """
    Calcula TODAS as métricas em um dicionário único.
    
    Args:
        retornos (pd.Series): Retornos diários da carteira
        patrimonio (pd.Series): Patrimônio acumulado
        retornos_ibov (pd.Series, optional): Retornos do Ibovespa
    
    Returns:
        dict: Métricas nomeadas com valores arredondados
    
    EXEMPLO:
        >>> m = calcular_todas(ret, pat, ret_ibov)
        >>> m["CAGR (% a.a.)"]
        15.67
        >>> m["Sharpe Ratio"]
        1.24
    
    NOTAS:
        - Retorna dict (facilita .to_csv(), iteração)
        - Valores já arredondados (2-4 casas decimais)
        - Métrica "Dias simulados" é útil para validação
    """
    m = {
        "Retorno Total (%)":       round(retorno_total(retornos) * 100, 2),
        "CAGR (% a.a.)":          round(cagr(retornos) * 100, 2),
        "Volatilidade Anual (%)":  round(volatilidade_anualizada(retornos) * 100, 2),
        "Sharpe Ratio":            round(sharpe_ratio(retornos), 4),
        "Sortino Ratio":           round(sortino_ratio(retornos), 4),
        "Máximo Drawdown (%)":     round(max_drawdown(patrimonio) * 100, 2),
        "Calmar Ratio":            round(calmar_ratio(retornos, patrimonio), 4),
        "Hit Rate (%)":            round(hit_rate(retornos), 2),
        "Dias simulados":          len(retornos),
    }

    if retornos_ibov is not None and not retornos_ibov.empty:
        a, b = alpha_beta(retornos, retornos_ibov)
        ret_ibov = retorno_total(retornos_ibov)
        m["Alpha anual (%)"]    = round(a * 100, 2)
        m["Beta vs Ibovespa"]   = round(b, 4)
        m["Retorno Ibovespa (%)"] = round(ret_ibov * 100, 2)
        m["Outperformance (%)"] = round(
            (retorno_total(retornos) - ret_ibov) * 100, 2
        )

    return m


def exibir_metricas(m: dict):
    """
    Exibe métricas formatadas no terminal.
    
    Args:
        m (dict): Dicionário de métricas (saída de calcular_todas)
    """
    sep = "=" * 52
    print(f"\n{sep}")
    print(f"{'MÉTRICAS DE PERFORMANCE':^52}")
    print(sep)
    for nome, val in m.items():
        print(f"  {nome:<32} {val:>10}")
    print(sep)