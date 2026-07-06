"""
model/acoes.py
==============

DESCRIÇÃO:
    Classe Acao: coleta de indicadores fundamentalistas e aplicação
    das 5 estratégias de valuation (Graham 1, Graham 2, Bazin, Lynch, ROE Eq.).
    
REFERÊNCIAS:
    - TCC seção 2.1.1: Métodos Baseados em Valor (Graham)
    - TCC seção 2.1.2: Métodos Baseados em Renda (Bazin)
    - TCC seção 2.1.3: Métodos Baseados em Crescimento (Lynch)
    - TCC seção 2.1.4: Métricas de Qualidade (ROE Equivalente)
    - TCC seção 3.2: Camada de Estratégias de Filtragem

FONTE DE DADOS:
    - Primária: yFinance (API aberta)
    - Fallback: Fundamentus (removido em v2.0 por instabilidade)
    - DY: calculado via histórico real (últimos 12 meses)

ESTRATÉGIAS IMPLEMENTADAS:

    1. GRAHAM 1 (Valor Justo - Quantitativo)
       Fórmula: P/VP × P/L ≤ 22,5
       Lógica: Rejeita ações caro-valorizadas
       Threshold: 22,5 (padrão em config.yaml)
       
    2. GRAHAM 2 (Preço Teto - Matemático)
       Fórmula: Preço < √(22,5 × LPA × VPA)
       Lógica: Define preço máximo de entrada baseado em fundamentos
       
    3. BAZIN (Renda Passiva)
       Fórmula: DY ≥ 6% ao ano
       Lógica: Filtra empresas com histórico sólido de dividendos
       Threshold: 6,0% (padrão em config.yaml)
       
    4. LYNCH (Crescimento a Preço Justo)
       Fórmula: PEG Ratio = (P/L) / (Crescimento × (1 - Payout)) < 2,0
       Lógica: Identifica growth stocks com valuation atraente
       Threshold: 2,0 (padrão em config.yaml)
       
    5. ROE EQUIVALENTE (Eficiência Operacional)
       Fórmula: ROE / (P/VP) ≥ 10%
       Lógica: Quantifica retorno real sobre preço pago
       Threshold: 10,0% (padrão em config.yaml)

ATRIBUTOS DA CLASSE:
    - ticker (str)      : símbolo da ação (ex: "WEGE3")
    - PrecoAcao (float) : preço atual em R$
    - PVP (float)       : P/VP (múltiplo de valor)
    - PL (float)        : P/L (múltiplo de lucro)
    - DY (float)        : Dividend Yield em %
    - ROE (float)       : Return On Equity em %
    - VPA (float)       : Valor Patrimonial por Ação (R$)
    - LPA (float)       : Lucro por Ação (R$)
    - Crescimento (float): Taxa de crescimento anual %
    - Payout (float)    : Percentual de lucro distribuído %

EXEMPLO DE USO:
    >>> from model.acoes import Acao
    >>> a = Acao()
    >>> ok = a.BuscarIndicadores("WEGE3")
    >>> if ok:
    ...     print(f"Preço: R${a.PrecoAcao:.2f}")
    ...     print(f"Graham 1 passou? {a.GetGraham1()}")
    ...     print(f"Score: {a.calcular_score()}/5")

FLUXO DE BUSCA:
    1. BuscarIndicadores(ticker)
       ├─ yFinance: preço, P/VP, P/L, ROE, DY (histórico real)
       └─ Retorna True se preço > 0
    
    2. Avaliação silenciosa (carteira.py)
       ├─ GetGraham1() → bool
       ├─ GetGraham2() → bool
       ├─ GetMetodoBazin() → bool
       ├─ GetRoeEquivalente() → bool
       ├─ GetMetodoLynch() → bool
       └─ calcular_score() → int (0-5)

NOTAS IMPORTANTES:
    - ROE é armazenado em % (18.0 = 18%)
    - DY é armazenado em % (6.5 = 6,5%)
    - Payout é calculado como: (DY / 100) × Preço / LPA × 100
    - Se Payout > 100%, é zerado (LPA negativo ou inconsistência)
    - Crescimento para Lynch usa earningsGrowth ou ROE como proxy
    - DY via histórico é mais confiável que dividendYield do yFinance

VIÉS DOCUMENTADO:
    - Look-Ahead Bias: indicadores de HOJE aplicados ao histórico
      (ver TCC seção 3.7)
"""

import math
import yaml
import yfinance as yf
import pandas as pd
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


def _cfg() -> dict:
    """Carrega config.yaml centralizado."""
    p = Path(__file__).parent.parent / "config.yaml"
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else {}


_EST = _cfg().get("estrategias", {})


class Acao:
    """
    Classe para análise fundamentalista de uma ação individual.
    
    Encapsula coleta de dados e aplicação de 5 filtros:
    Graham 1, Graham 2, Bazin, Lynch, ROE Equivalente.
    """

    def __init__(self):
        """Inicializa atributos zerados."""
        self.ticker = ""
        self.PrecoAcao = 0.0
        self.PVP = 0.0
        self.PL = 0.0
        self.Payout = 0.0
        self.DY = 0.0
        self.VPA = 0.0
        self.LPA = 0.0
        self.ROE = 0.0
        self.Crescimento = 0.0

    # ─────────────────────────────────────────────────────────────
    # ESTRATÉGIAS DE VALUATION
    # ─────────────────────────────────────────────────────────────

    def GetGraham1(self) -> bool:
        """Aplica Graham 1 com dados carregados."""
        return self.graham1(self.PVP, self.PL)

    def graham1(self, PVP: float, PL: float) -> bool:
        """
        Graham 1: P/VP × P/L ≤ 22,5
        
        Args:
            PVP (float): Preço/Valor Patrimonial
            PL (float): Preço/Lucro
        
        Returns:
            bool: True se passou no filtro
        
        REF: TCC seção 2.1.1, Graham (2006)
        """
        teto = _EST.get("graham1", {}).get("threshold", 22.5)
        if PVP <= 0 or PL <= 0:
            return False
        p = PVP * PL
        return p <= teto

    def GetGraham2(self) -> bool:
        """Aplica Graham 2 com dados carregados."""
        return self.graham2(self.VPA, self.LPA, self.PrecoAcao)

    def graham2(self, VPA: float, LPA: float, preco: float) -> bool:
        """
        Graham 2: Preço ≤ √(22,5 × LPA × VPA)
        
        Args:
            VPA (float): Valor Patrimonial por Ação
            LPA (float): Lucro por Ação
            preco (float): Preço atual
        
        Returns:
            bool: True se preço está abaixo do teto
        
        REF: TCC seção 2.1.1, Graham (2006)
        """
        prod = 22.5 * LPA * VPA
        if prod <= 0:
            return False
        pt = math.sqrt(prod)
        return preco < pt

    def GetMetodoBazin(self) -> bool:
        """Aplica Bazin com dados carregados."""
        return self.metodoBazin(self.DY)

    def metodoBazin(self, DY: float) -> bool:
        """
        Bazin: DY ≥ 6% ao ano
        
        Args:
            DY (float): Dividend Yield em %
        
        Returns:
            bool: True se DY acima do mínimo
        
        REF: TCC seção 2.1.2, Bazin (1992)
        """
        mn = _EST.get("bazin", {}).get("dy_minimo", 6.0)
        return DY >= mn

    def GetRoeEquivalente(self) -> bool:
        """Aplica ROE Equivalente com dados carregados."""
        return self.roeEquivalente(self.PVP, self.ROE)

    def roeEquivalente(self, PVP: float, ROE: float) -> bool:
        """
        ROE Equivalente: ROE / (P/VP) ≥ 10%
        
        Args:
            PVP (float): Preço/Valor Patrimonial
            ROE (float): Return On Equity em %
        
        Returns:
            bool: True se ROE equivalente acima de 10%
        
        REF: TCC seção 2.1.4, Damodaran (2002)
        
        NOTA: ROE deve estar em % (18.0 = 18%)
        """
        teto = _EST.get("roe_equivalente", {}).get("threshold", 10.0)
        if PVP <= 0:
            return False
        re = ROE / PVP
        return re >= teto

    def GetMetodoLynch(self) -> bool:
        """Aplica Lynch com dados carregados."""
        return self.metodoLynch(self.PL, self.Crescimento, self.Payout)

    def metodoLynch(self, PL: float, Crescimento: float, Payout: float) -> bool:
        """
        Lynch (PEG Ratio): (P/L) / Crescimento_líquido < 2,0
        
        Crescimento_líquido = Crescimento × (1 - Payout / 100)
        
        Args:
            PL (float): Preço/Lucro
            Crescimento (float): Taxa de crescimento anual em %
            Payout (float): Percentual de lucro distribuído em %
        
        Returns:
            bool: True se PEG < 2,0
        
        REF: TCC seção 2.1.3, Lynch (2011)
        """
        pm = _EST.get("lynch", {}).get("peg_maximo", 2.0)
        if PL <= 0:
            return False
        cl = Crescimento * (1 - Payout / 100)
        if cl <= 0:
            return False
        peg = PL / cl
        return peg < pm

    def calcular_score(self) -> int:
        """
        Calcula score: quantos critérios esta ação passou (0-5).
        
        Returns:
            int: Número de critérios aprovados
        
        EXEMPLO:
            >>> a = Acao()
            >>> a.BuscarIndicadores("WEGE3")
            >>> score = a.calcular_score()
            >>> print(f"Passou em {score}/5 critérios")
        """
        import io, contextlib
        r = []
        for f in [self.GetGraham1, self.GetGraham2, self.GetMetodoBazin,
                  self.GetRoeEquivalente, self.GetMetodoLynch]:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                r.append(f())
        return sum(1 for x in r if x)

    # ─────────────────────────────────────────────────────────────
    # COLETA DE DADOS
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def _calcular_dy_historico(yf_ticker, preco: float) -> float:
        """
        Calcula DY a partir da soma real de dividendos (últimos 12m).
        
        Args:
            yf_ticker: Objeto yfinance.Ticker
            preco (float): Preço atual em R$
        
        Returns:
            float: DY em % (ex: 6.5) ou 0.0 se sem dados
        
        NOTA: Mais confiável que dividendYield do yFinance para .SA
        """
        if preco <= 0:
            return 0.0
        try:
            hist = yf_ticker.history(period="1y", auto_adjust=True)
            if hist.empty or "Dividends" not in hist.columns:
                return 0.0
            div_12m = float(hist["Dividends"].sum())
            if div_12m <= 0:
                return 0.0
            return round((div_12m / preco) * 100, 2)
        except Exception:
            return 0.0

    def BuscarIndicadores(self, ticker: str) -> bool:
        """
        Busca indicadores fundamentalistas via yFinance.
        
        Args:
            ticker (str): Símbolo (ex: "WEGE3", "ITUB4")
        
        Returns:
            bool: True se preço > 0 (busca bem-sucedida)
        
        FLUXO:
            1. Tenta yFinance (primária)
            2. Se falhar, tenta Fundamentus (fallback, removido em v2.0)
            3. Calcula DY via histórico real (últimos 12 meses)
            4. Computa Payout, Crescimento, LPA
            5. Chama PrintIndicadores() (log)
        
        EXEMPLO:
            >>> a = Acao()
            >>> sucesso = a.BuscarIndicadores("WEGE3")
            >>> if sucesso:
            ...     print(f"P/VP: {a.PVP}")
            ...     print(f"DY: {a.DY}%")
        """
        self.ticker = ticker.upper().strip()

        try:
            yft = yf.Ticker(f"{self.ticker}.SA")
            info = yft.info

            if info is None:
                raise Exception("Ticker não encontrado")

            def _f(key: str, default: float = 0.0) -> float:
                v = info.get(key)
                try:
                    return float(v) if v is not None else default
                except (TypeError, ValueError):
                    return default

            # Preço
            self.PrecoAcao = (
                _f("currentPrice") or
                _f("regularMarketPrice") or
                _f("previousClose")
            )

            # Múltiplos
            self.PVP = _f("priceToBook")
            self.PL = _f("trailingPE")

            # ROE em %
            roe_raw = info.get("returnOnEquity")
            self.ROE = round(float(roe_raw) * 100, 2) if roe_raw is not None else 0.0

            # DY via histórico real
            self.DY = self._calcular_dy_historico(yft, self.PrecoAcao)

            # VPA e LPA
            self.VPA = _f("bookValue")
            self.LPA = _f("trailingEps")

            # Payout
            if self.LPA > 0 and self.PrecoAcao > 0:
                payout_calc = (self.DY / 100) * self.PrecoAcao / self.LPA * 100
                self.Payout = round(payout_calc, 2) if payout_calc <= 100 else 0.0
            else:
                self.Payout = 0.0

            # Crescimento
            eg = info.get("earningsGrowth")
            if eg is not None and float(eg) > 0:
                self.Crescimento = round(float(eg) * 100, 2)
            elif self.ROE > 0:
                self.Crescimento = self.ROE
            else:
                self.Crescimento = 0.0

        except Exception as e:
            pass

        self.PrintIndicadores()
        return self.PrecoAcao > 0

    # ─────────────────────────────────────────────────────────────
    # EXIBIÇÃO
    # ─────────────────────────────────────────────────────────────

    def PrintIndicadores(self):
        """Exibe indicadores no formato tabular (log)."""
        print(f"\n📊 Indicadores de {self.ticker}:")
        print(f"  Preço:        R$ {self.PrecoAcao:.2f}")
        print(f"  P/VP:         {self.PVP:.2f}")
        print(f"  P/L:          {self.PL:.2f}")
        print(f"  DY:           {self.DY:.2f}%")
        print(f"  ROE:          {self.ROE:.2f}%")
        print(f"  Crescimento:  {self.Crescimento:.2f}% a.a. (Lynch)")
        print(f"  Payout:       {self.Payout:.2f}%")
        print(f"  VPA:          R$ {self.VPA:.2f}")
        print(f"  LPA:          R$ {self.LPA:.2f}")