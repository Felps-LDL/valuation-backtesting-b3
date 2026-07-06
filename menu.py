"""
menu.py
-------
Menu de terminal do sistema.
Permite análise individual, carteira e backtesting
sem precisar da interface web.
"""

from model.acoes import Acao
from model.universo import obter_dataframe_universo
from model.carteira import construir_carteira, exibir_carteira
from backtest.engine import rodar_backtest
from backtest.metricas import calcular_todas, exibir_metricas


def menu() -> bool:
    """Exibe o menu e executa a opção. Retorna False para sair."""
    print("\n" + "=" * 45)
    print("  SISTEMA DE ANÁLISE FUNDAMENTALISTA — B3")
    print("=" * 45)
    print("  ⚠️  Uso acadêmico. NÃO é recomendação de investimento.")
    print("=" * 45)
    print("  1. Analisar ação individual")
    print("  2. Montar carteira de ações")
    print("  3. Rodar backtesting")
    print("  0. Sair")
    print("=" * 45)

    try:
        op = int(input("  Opção: ").strip())
    except ValueError:
        print("⚠️  Digite um número válido.")
        return True

    if   op == 1: _analise_acao()
    elif op == 2: _analise_carteira()
    elif op == 3: _executar_backtest()
    elif op == 0:
        print("\nAté logo! 👋")
        return False
    else:
        print("⚠️  Opção inválida.")

    return True


def _analise_acao():
    ticker = input("\nTicker (ex: WEGE3): ").strip().upper()
    if not ticker:
        return

    a = Acao()
    if not a.BuscarIndicadores(ticker):
        print(f"❌ Dados não encontrados para {ticker}.")
        return

    print("\n─── CRITÉRIOS ──────────────────────────────")
    resultados = {
        "Graham 1 (P/VP × P/L ≤ 22,5)":    a.GetGraham1(),
        "Graham 2 (Preço ≤ preço teto)":     a.GetGraham2(),
        "Bazin    (DY ≥ 6%)":               a.GetMetodoBazin(),
        "ROE Eq.  (ROE/P/VP ≥ 10%)":        a.GetRoeEquivalente(),
        "Lynch    (PEG < 2)":               a.GetMetodoLynch(),
    }
    score = 0
    for nome, passou in resultados.items():
        print(f"  {'✅' if passou else '❌'} {nome}")
        if passou:
            score += 1
    print(f"\n  Score: {score}/5")


def _analise_carteira():
    print("\n─── CRITÉRIOS ──────────────────────────────")
    nomes = {
        "graham1": "Graham 1 (P/VP × P/L ≤ 22,5)",
        "graham2": "Graham 2 (Preço ≤ preço teto)",
        "bazin":   "Bazin    (DY ≥ 6%)",
        "roe_eq":  "ROE Eq.  (ROE/P/VP ≥ 10%)",
        "lynch":   "Lynch    (PEG < 2)",
    }
    criterios = {}
    for chave, nome in nomes.items():
        r = input(f"  Ativar {nome}? (s/n): ").strip().lower()
        criterios[chave] = r == "s"

    print("\n─── LÓGICA ─────────────────────────────────")
    print("  1. k-of-n  2. AND  3. OR")
    try:
        op = int(input("  Escolha: ").strip())
        logica = {1: "k-of-n", 2: "AND", 3: "OR"}.get(op, "k-of-n")
    except ValueError:
        logica = "k-of-n"

    k = 3
    if logica == "k-of-n":
        try:
            k = int(input("  Mínimo de critérios (k): ").strip())
        except ValueError:
            k = 3

    try:
        top_k = int(input("  Quantas ações na carteira? (padrão 15): ").strip() or "15")
    except ValueError:
        top_k = 15

    print("\n⏳ Buscando universo...")
    df_u = obter_dataframe_universo()
    if df_u.empty:
        print("❌ Universo vazio.")
        return

    df_c = construir_carteira(df_u, criterios=criterios,
                              logica=logica, k=k, top_k=top_k)
    exibir_carteira(df_c)


def _executar_backtest():
    print("\n─── BACKTESTING ────────────────────────────")
    d_ini = input("  Início (YYYY-MM-DD, padrão 2015-01-01): ").strip()
    if not d_ini:
        d_ini = "2015-01-01"

    try:
        cap = float(input("  Capital inicial R$ (padrão 100000): ").strip() or "100000")
    except ValueError:
        cap = 100_000.0

    print("\n⏳ Rodando backtesting (aguarde)...")
    res = rodar_backtest(data_inicio=d_ini, capital_inicial=cap)

    if not res:
        print("❌ Backtesting falhou.")
        return

    m = calcular_todas(
        res["retornos"], res["patrimonio"],
        res.get("retornos_ibov")
    )
    exibir_metricas(m)

    