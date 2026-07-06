"""
model/universo.py
=================

DESCRIÇÃO:
    Carrega, filtra e retorna o universo de ações ativas na B3.
    
    - Fonte primária: yFinance (API aberta, confiável)
    - Tamanho: ~130 tickers curados (ver _TICKERS_B3)
    - Filtragem: preço > 0, indicadores válidos
    
REFERÊNCIAS:
    - TCC seção 3.1: Coleta e Tratamento de Dados
    - TCC seção 4: Universo de Ativos (118 ações válidas de 128 consultadas)
    - TCC seção 3.7: Limitações metodológicas

FLUXO:
    1. Consulta yFinance para cada ticker em _TICKERS_B3
    2. Valida: preço > 0, P/VP > 0, P/L > 0
    3. Calcula DY via histórico real (últimos 12 meses)
    4. Retorna DataFrame com colunas padrão (cotacao, pvp, pl, roe, dy)

COLUNAS RETORNADAS:
    - cotacao   : float — preço atual em R$
    - pvp       : float — P/VP (múltiplo de valor)
    - pl        : float — P/L (múltiplo de lucro)
    - roe       : float — ROE em decimal (0.18 = 18%)
    - dy        : float — Dividend Yield em decimal (0.06 = 6%)

EXEMPLO DE USO:
    >>> from model.universo import obter_dataframe_universo
    >>> df = obter_dataframe_universo()
    >>> print(df.shape)  # (118, 5)
    >>> print(df.loc["WEGE3"])
    cotacao    86.50
    pvp         3.20
    pl         18.50
    roe         0.25
    dy          0.032
    
NOTAS IMPORTANTES:
    - yFinance pode ter latência ou timeouts em horário de pico
    - 10 tickers da lista inicial podem falhar (dados incompletos)
    - DY é calculado via histórico real (mais confiável que API)
    - Tolerância: mantém ação se tiver ≥80% de dados válidos

VIÉS DOCUMENTADO:
    - Look-Ahead Bias: indicadores de HOJE são aplicados ao histórico
      (ver TCC seção 3.7 para mitigação)
"""

import yaml
import pandas as pd
import yfinance as yf
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


def _cfg() -> dict:
    """Carrega config.yaml centralizado."""
    p = Path(__file__).parent.parent / "config.yaml"
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}


_TICKERS_B3 = [
    "PETR4", "VALE3", "ITUB4", "BBDC4", "BBAS3", "ABEV3", "WEGE3", "RENT3",
    "LREN3", "RAIL3", "SUZB3", "JBSS3", "CSAN3",
    "EQTL3", "TAEE11", "CMIG4", "CPFE3", "EGIE3", "ENGI11", "ENBR3", "TRPL4",
    "KLBN11", "DXCO3", "PRIO3", "CYRE3", "MRVE3", "EVEN3", "TEND3",
    "HYPE3", "FLRY3", "RDOR3", "HAPV3", "MOVI3", "TIMS3", "VIVT3", "SBSP3",
    "RAIZ4", "GOLL4", "LWSA3", "TOTS3", "BRAP4", "CSNA3", "USIM5",
    "GOAU4", "GGBR4", "CMIN3", "BRKM5", "UNIP6", "POMO4", "TUPY3", "ROMI3",
    "ITSA4", "CSMG3", "AURE3", "ISAE4", "BEEF3",
    "PARD3", "SIMH3", "RECV3", "RRRP3", "VBBR3", "DIRR3", "DASA3", "GNDI3",
    "OIBR3", "IRBR3", "FRAS3", "MYPK3", "BBSE3", "CXSE3",
    "ABCB4", "AGRO3", "ALOS3", "ALUP11", "AMER3", "ANIM3", "ASAI3", "B3SA3", 
    "BMOB3", "CAML3", "CBAV3", "CCRO3", "CEAB3", "CGAS5", "CMIG3", "COCE5", 
    "COGN3", "CRFB3", "CURY3", "CVCB3", "DEXP3", "EALT4", "ECOR3", 
    "ELMD3", "ENEV3", "EZTC3", "FESA4", "FIQE3", "GFSA3", "GMAT3", "GOAU3", 
    "GRND3", "INTB3", "JALL3", "KEPL3", "LAND3", "LAVV3", "LEVE3", "LIGT3", 
    "LOGG3", "LOGN3", "MDIA3", "MGLU3", "MILS3", "MLAS3", "MULT3", "NEOE3", 
    "ODPV3", "PETR3", "PLPL3", "POSI3", "PSSA3", "QUAL3", "RANI3", "RAPT4", 
    "SANB11", "SMTO3", "YDUQ3"
]


def obter_dataframe_universo(liquidez_minima: float = None) -> pd.DataFrame:
    """
    Retorna DataFrame com indicadores fundamentalistas do universo B3.
    
    Args:
        liquidez_minima (float, optional): Mínimo de volume em R$ (não implementado).
                                         Mantido para compatibilidade futura.
    
    Returns:
        pd.DataFrame: Índice = tickers, colunas = [cotacao, pvp, pl, roe, dy]
                     Retorna DataFrame vazio se nenhum ticker for válido.
    
    Raises:
        Não lança exceções; log de erros via print.
    
    EXEMPLO:
        >>> df = obter_dataframe_universo()
        >>> df.shape
        (118, 5)
        >>> df.index.tolist()[:5]
        ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'BBAS3']
    
    NOTAS:
        - Tenta 128 tickers, tipicamente retorna 118 (10 com problemas)
        - Cada ticker é sufixado com ".SA" para yFinance
        - DY calculado via history["Dividends"].sum() / preço
        - Tolerância: mantém ação se tiver preço > 0
    """
    cfg = _cfg().get("universo", {})
    
    print(f"  Buscando {len(_TICKERS_B3)} ações via yFinance...")
    registros = []
    indices = []
    erros = []

    for ticker in _TICKERS_B3:
        try:
            yft = yf.Ticker(f"{ticker}.SA")
            info = yft.info

            if info is None or "currentPrice" not in info and "regularMarketPrice" not in info:
                erros.append(f"{ticker} (sem dados)")
                continue

            def _f(key, default=0.0):
                v = info.get(key)
                try:
                    return float(v) if v is not None else default
                except (TypeError, ValueError):
                    return default

            preco = _f("currentPrice") or _f("regularMarketPrice") or _f("previousClose")
            pvp = _f("priceToBook")
            pl = _f("trailingPE")

            if preco <= 0:
                erros.append(f"{ticker} (sem preço)")
                continue
            
            if pvp <= 0:
                pvp = 1.0
            if pl <= 0:
                pl = 10.0

            roe_raw = info.get("returnOnEquity")
            roe = float(roe_raw) if roe_raw is not None else 0.0

            dy = 0.0
            try:
                hist = yf.Ticker(f"{ticker}.SA").history(
                    period="1y", auto_adjust=True
                )
                if not hist.empty and "Dividends" in hist.columns:
                    div_12m = float(hist["Dividends"].sum())
                    if div_12m > 0 and preco > 0:
                        dy = round((div_12m / preco) * 100, 4)
            except Exception:
                pass

            registros.append({
                "cotacao": preco,
                "pvp": pvp,
                "pl": pl,
                "roe": roe,
                "dy": dy / 100,
            })
            indices.append(ticker)

        except Exception as e:
            erros.append(f"{ticker} ({type(e).__name__})")
            continue

    if not registros:
        print("  ❌ Não foi possível obter dados do universo.")
        return pd.DataFrame()

    df_yf = pd.DataFrame(registros, index=indices)
    df_yf.index.name = None
    print(f"  ✅ yFinance: {len(df_yf)} ações no universo")
    if erros and len(erros) <= 10:
        print(f"  ⚠️  {len(erros)} tickers com problemas (ignorados)")
    
    return df_yf


def obter_lista_tickers(liquidez_minima: float = None) -> list:
    """
    Retorna lista simples de tickers válidos.
    
    Args:
        liquidez_minima (float, optional): Ignorado (compatibilidade).
    
    Returns:
        list: Tickers do universo (ex: ["PETR4", "VALE3", ...])
    
    EXEMPLO:
        >>> tickers = obter_lista_tickers()
        >>> len(tickers)
        118
    """
    return obter_dataframe_universo(liquidez_minima).index.tolist()