"""
model/carteira.py
=================

DESCRIÇÃO:
    Construção de carteiras fundamentalistas com lógica combinatória.
    
REFERÊNCIAS:
    - TCC seção 3.3: Camada de Construção Combinatória
    - TCC seção 4: Configuração do Experimento (seed, k-of-n)
    - TCC seção 3.7: Look-Ahead Bias (viés documentado)

LÓGICAS DE COMBINAÇÃO:
    1. AND (Interseção)
       └─ Ação selecionada se aprovada em TODOS os critérios
       └─ Mais restritivo, carteira menor e mais concentrada
       
    2. OR (União)
       └─ Ação selecionada se aprovada em PELO MENOS 1 critério
       └─ Mais expansivo, carteira maior e diversificada
       
    3. k-of-n (Flexível — RECOMENDADO)
       └─ Ação selecionada se aprovada em mínimo k de n critérios
       └─ Balanço entre restritibilidade e diversificação
       └─ Ex: k=3 → precisa passar em 3 de 5 critérios

TESTE SEM FILTROS (BASELINE):
    - Ignora toda lógica fundamentalista
    - Seleciona 15 ações aleatoriamente (universo embaralhado)
    - Mesmo seed: garante universo aleatório igual para ambos os testes
    - Valida H1 do TCC: "filtros geram alfa"

EMBARALHAMENTO (Reprodutibilidade):
    - Universo é shuffled com seed antes de aplicar filtros/baseline
    - Garante comparação justa: mesma aleatoriedade para ambos
    - Mesmo seed em duas datas diferentes pode gerar carteiras diferentes
      (por Look-Ahead Bias com indicadores atualizados) — documentado em TCC 3.7

PONDERAÇÃO:
    - equal: peso idêntico para todas as ações (padrão)
    - score: peso proporcional ao score (critérios aprovados)

EXEMPLO DE USO:
    >>> from model.universo import obter_dataframe_universo
    >>> from model.carteira import construir_carteira
    >>> df_u = obter_dataframe_universo()
    >>> df_c = construir_carteira(
    ...     df_u,
    ...     criterios={"graham1": True, "bazin": True, ...},
    ...     logica="k-of-n",
    ...     k=3,
    ...     top_k=15,
    ...     seed=42
    ... )
    >>> print(df_c)
"""

import io
import contextlib
import yaml
import pandas as pd
import random
from pathlib import Path
from model.acoes import Acao


def _cfg() -> dict:
    """Carrega config.yaml centralizado."""
    p = Path(__file__).parent.parent / "config.yaml"
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


def _avaliar_linha(row: pd.Series, criterios: dict) -> dict:
    """
    Avalia uma linha do DataFrame (ação individual) silenciosamente.
    
    Args:
        row (pd.Series): Linha com colunas [cotacao, pvp, pl, roe, dy]
        criterios (dict): {nome: bool} — ex {"graham1": True, "bazin": False}
    
    Returns:
        dict: {
            "score": int (0-5),
            "resultados": dict {nome: bool},
            "acao": Acao (objeto preenchido)
        }
    
    NOTA: Execução silenciosa (print suprimido) para não poluir logs.
    """
    a = Acao()
    a.PrecoAcao = float(row.get("cotacao", 0))
    a.PVP = float(row.get("pvp", 0))
    a.PL = float(row.get("pl", 0))
    a.ROE = float(row.get("roe", 0)) * 100
    a.DY = float(row.get("dy", 0)) * 100

    a.LPA = (a.PrecoAcao / a.PL) if a.PL > 0 else 0.0
    a.VPA = (a.PrecoAcao / a.PVP) if a.PVP > 0 else 0.0
    if "vpa" in row.index and float(row.get("vpa", 0)) > 0:
        a.VPA = float(row["vpa"])

    if a.LPA > 0:
        a.Payout = (a.DY / 100.0) * a.PrecoAcao / a.LPA * 100
    else:
        a.Payout = 0.0

    a.Crescimento = a.ROE

    def silencioso(func):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            return func()

    mapa = {
        "graham1": a.GetGraham1,
        "graham2": a.GetGraham2,
        "bazin": a.GetMetodoBazin,
        "roe_eq": a.GetRoeEquivalente,
        "lynch": a.GetMetodoLynch,
    }

    resultados = {}
    for nome, ativo in criterios.items():
        if ativo and nome in mapa:
            resultados[nome] = silencioso(mapa[nome])

    score = sum(1 for v in resultados.values() if v)
    return {"score": score, "resultados": resultados, "acao": a}


def embaralhar_universo(df_universo: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """
    Embaralha o universo para garantir seleção aleatória justa.
    
    Args:
        df_universo (pd.DataFrame): DataFrame original
        seed (int): Seed para reprodutibilidade (padrão: 42)
    
    Returns:
        pd.DataFrame: Mesmo DataFrame, índice embaralhado
    
    PROPÓSITO:
        - COM FILTROS: Embaralha antes de aplicar critérios
        - SEM FILTROS: Embaralha antes de pegar 15 primeiras
        └─ Resultado: ambos começam com universo aleatório igual
        └─ Diferença é apenas os critérios fundamentalistas
        └─ Valida que diferença de performance vem dos filtros, não do acaso
    
    REPRODUTIBILIDADE:
        Mesma seed = mesma ordem de embaralhamento
        Ideal para comparação justa entre datas diferentes
    
    NOTA: Look-Ahead Bias
        Mesmo com seed idêntica, carteiras podem diferir entre datas
        se indicadores fundamentalistas tiverem mudado (DY, P/L, etc.)
        Documentado em TCC seção 3.7.
    """
    if seed is not None:
        random.seed(seed)
    
    indices = df_universo.index.tolist()
    random.shuffle(indices)
    
    df_shuffled = df_universo.loc[indices]
    print(f"  🔀 Universo embaralhado ({len(df_shuffled)} ações, seed={seed})")
    
    return df_shuffled


def construir_carteira(
    df_universo: pd.DataFrame = None,
    criterios: dict = None,
    logica: str = None,
    k: int = None,
    top_k: int = None,
    ponderacao: str = None,
    teste_sem_filtros: bool = False,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Constrói carteira aplicando filtros fundamentalistas.
    
    Args:
        df_universo (pd.DataFrame): Obrigatório. Índice=tickers, colunas=[cotacao, pvp, pl, roe, dy]
        criterios (dict): {nome: bool} — ex {"graham1": True, "bazin": False}
        logica (str): "AND" | "OR" | "k-of-n" (padrão)
        k (int): Mínimo de critérios (se logica="k-of-n")
        top_k (int): Máximo de ações na carteira (padrão: 15)
        ponderacao (str): "equal" | "score" (padrão: equal)
        teste_sem_filtros (bool): Se True, ignora critérios (baseline)
        seed (int): Seed para embaralhamento (padrão: 42)
    
    Returns:
        pd.DataFrame: Carteira selecionada com colunas:
            [ticker, score, criterios_aprovados, cotacao, dy, pl, pvp, roe, peso]
        Retorna DataFrame vazio se nenhuma ação passou.
    
    FLUXO:
        1. Embaralha universo (seed)
        2. Se teste_sem_filtros: pega top_k primeiras
        3. Senão: aplica lógica AND/OR/k-of-n
        4. Ordena por score decrescente
        5. Seleciona top_k ações
        6. Calcula pesos (equal ou score)
    
    EXEMPLO COM FILTROS:
        >>> df_u = obter_dataframe_universo()
        >>> df_c = construir_carteira(
        ...     df_u,
        ...     criterios={"graham1": True, "bazin": True, "roe_eq": True},
        ...     logica="k-of-n",
        ...     k=2,
        ...     top_k=15,
        ...     seed=42
        ... )
        >>> print(f"Selecionadas {len(df_c)} ações")
    
    EXEMPLO SEM FILTROS (BASELINE):
        >>> df_c_baseline = construir_carteira(
        ...     df_u,
        ...     teste_sem_filtros=True,
        ...     top_k=15,
        ...     seed=42
        ... )
    
    NOTAS:
        - Mesma seed em datas diferentes pode gerar carteiras diferentes
          (Look-Ahead Bias, ver TCC 3.7)
        - Para reprodutibilidade total, salve carteira em CSV
        - Recomendação: use seed=42 para defesa (evita surpresas)
    """
    print(f"\n🏗️  Construindo carteira...")
    
    # Embaralha universo uma única vez
    df_universo = embaralhar_universo(df_universo, seed=seed)
    
    if teste_sem_filtros:
        # ─────────────────────────────────────────────────────────
        # TESTE SEM FILTROS (BASELINE ALEATÓRIO)
        # ─────────────────────────────────────────────────────────
        print(f"  ⚠️  TESTE SEM FILTROS (baseline aleatório)")
        
        top_k = top_k or 15
        
        registros = []
        for ticker, row in df_universo.head(top_k).iterrows():
            registros.append({
                "ticker": ticker,
                "score": 0,
                "criterios_aprovados": "NENHUM (teste baseline)",
                "cotacao": round(float(row.get("cotacao", 0)), 2),
                "dy": round(float(row.get("dy", 0)) * 100, 2),
                "pl": round(float(row.get("pl", 0)), 2),
                "pvp": round(float(row.get("pvp", 0)), 2),
                "roe": round(float(row.get("roe", 0)) * 100, 2),
            })
        
        df = pd.DataFrame(registros)
        df["peso"] = round(100 / len(df), 2)
        
        print(f"  ✅ {len(df)} ações selecionadas (aleatoriamente)")
        return df
    
    # ─────────────────────────────────────────────────────────────
    # TESTE COM FILTROS (FUNDAMENTALISTA)
    # ─────────────────────────────────────────────────────────────
    
    cfg = _cfg()
    cfg_cart = cfg.get("carteira", {})
    cfg_est = cfg.get("estrategias", {})

    logica = logica or cfg_cart.get("logica", "k-of-n")
    k = k if k is not None else cfg_cart.get("k", 3)
    top_k = top_k if top_k is not None else cfg_cart.get("top_k", 15)
    ponderacao = ponderacao or cfg_cart.get("ponderacao", "equal")

    if criterios is None:
        criterios = {
            "graham1": cfg_est.get("graham1", {}).get("ativo", True),
            "graham2": cfg_est.get("graham2", {}).get("ativo", True),
            "bazin": cfg_est.get("bazin", {}).get("ativo", True),
            "roe_eq": cfg_est.get("roe_equivalente", {}).get("ativo", True),
            "lynch": cfg_est.get("lynch", {}).get("ativo", True),
        }

    ativos = {c: v for c, v in criterios.items() if v}
    n = len(ativos)

    if n == 0:
        print("⚠️  Nenhum critério ativado.")
        return pd.DataFrame()

    print(f"  Lógica: {logica} | Critérios: {n} | Top-{top_k}")

    registros = []
    for ticker, row in df_universo.iterrows():
        av = _avaliar_linha(row, ativos)
        score = av["score"]

        if logica == "AND":
            aprovado = score == n
        elif logica == "OR":
            aprovado = score >= 1
        else:  # k-of-n
            aprovado = score >= k

        if aprovado:
            crit_str = ", ".join(c for c, v in av["resultados"].items() if v)
            registros.append({
                "ticker": ticker,
                "score": score,
                "criterios_aprovados": crit_str,
                "cotacao": round(float(row.get("cotacao", 0)), 2),
                "dy": round(float(row.get("dy", 0)) * 100, 2),
                "pl": round(float(row.get("pl", 0)), 2),
                "pvp": round(float(row.get("pvp", 0)), 2),
                "roe": round(float(row.get("roe", 0)) * 100, 2),
            })

    if not registros:
        print("⚠️  Nenhuma ação passou nos filtros.")
        return pd.DataFrame()

    df = (pd.DataFrame(registros)
            .sort_values("score", ascending=False)
            .head(top_k)
            .reset_index(drop=True))

    if ponderacao == "score" and df["score"].sum() > 0:
        df["peso"] = (df["score"] / df["score"].sum() * 100).round(2)
    else:
        df["peso"] = round(100 / len(df), 2)

    print(f"  ✅ {len(df)} ações selecionadas (com filtros)")
    return df


def exibir_carteira(df: pd.DataFrame):
    """
    Exibe carteira formatada no terminal.
    
    Args:
        df (pd.DataFrame): DataFrame com colunas [ticker, score, dy, pl, pvp, roe, peso]
    """
    if df.empty:
        print("Carteira vazia.")
        return
    sep = "=" * 80
    print(f"\n{sep}")
    print(f"{'CARTEIRA SELECIONADA':^80}")
    print(sep)
    print(f"{'Ticker':<8} {'Score':<7} {'DY%':<8} {'P/L':<8} "
          f"{'P/VP':<8} {'ROE%':<8} {'Peso%':<8} {'Critérios'}")
    print("-" * 80)
    for _, r in df.iterrows():
        crit = r.get('criterios_aprovados', 'N/A')
        if len(crit) > 20:
            crit = crit[:17] + "..."
        print(f"{r['ticker']:<8} {r['score']:<7} {r['dy']:<8.2f} "
              f"{r['pl']:<8.2f} {r['pvp']:<8.2f} {r['roe']:<8.2f} {r['peso']:.2f} {crit}")
    print(sep)
    print(f"Total: {len(df)} ações | Peso total: {df['peso'].sum():.2f}%\n")