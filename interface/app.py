"""
interface/app.py
================

DESCRIÇÃO:
    Interface web completa do sistema via Streamlit.
    Oferece 3 abas integradas para análise fundamentalista interativa.

REFERÊNCIAS:
    - TCC seção 6.8: Interface e Visualização
    - TCC seção 3-4: Camadas da metodologia
    - TCC seção 3.7: Look-Ahead Bias (documentado na UI)

TECNOLOGIA:
    - Framework: Streamlit (Python → web sem Flask/Django)
    - Gráficos: Plotly (interativo)
    - Dados: Pandas, yFinance

EXECUÇÃO:
    $ streamlit run interface/app.py
    → Abre http://localhost:8501

ESTRUTURA DE ABAS:

    ┌─────────────────────────────────────────────────────┐
    │  🏗️ Carteira | 📊 Backtesting | 🔍 Ação Individual │
    └─────────────────────────────────────────────────────┘
    
    ABA 1: 🏗️ CARTEIRA
    ├─ Controles:
    │  ├─ Radio: Com filtros / Sem filtros (baseline)
    │  ├─ Slider: Seed (1-9999, padrão 42)
    │  └─ Checkboxes: Graham1, Graham2, Bazin, ROE, Lynch
    ├─ Lógica: k-of-n, AND, OR (default: k-of-n)
    ├─ Slider: k (1-5, default 3)
    ├─ Slider: Top-K (5-30, default 15)
    ├─ Button: Gerar Carteira
    └─ Saída:
       ├─ Tabela: ticker, score, dy, pl, pvp, roe, peso
       ├─ Gráfico: pizza (composição)
       └─ Gráfico: barras (score por ação)
    
    ABA 2: 📊 BACKTESTING
    ├─ Aviso: Look-Ahead Bias explicado
    ├─ Button: Rodar Backtesting
    ├─ Saída (se sucesso):
    │  ├─ 4 KPIs: CAGR, Sharpe, Drawdown, Outperformance
    │  ├─ Expander: Todas as métricas (tabela)
    │  ├─ Gráfico: Equity curve (carteira vs Ibovespa)
    │  ├─ Gráfico: Drawdown (série temporal)
    │  └─ Tabela: Ações na carteira do backtest
    └─ Dados salvos: data/retornos_carteira.csv, data/retornos_ibov.csv
    
    ABA 3: 🔍 AÇÃO INDIVIDUAL
    ├─ Input: Ticker (ex: WEGE3)
    ├─ Button: Analisar
    └─ Saída:
       ├─ Tabela: Indicadores (Preço, P/VP, P/L, DY, ROE, etc.)
       └─ 5 Métricas: Graham1 ✅/❌, Graham2, Bazin, ROE, Lynch

SIDEBAR: ⚙️ CONFIGURAÇÕES
├─ Radio: Tipo de teste (Com filtros / Sem filtros)
├─ Subheader: 🎲 Reprodutibilidade
│  └─ Number Input: Semente Aleatória (1-9999, default 42)
├─ Checkboxes: Critérios (se com filtros)
│  ├─ Graham 1
│  ├─ Graham 2
│  ├─ Bazin
│  ├─ ROE Eq.
│  └─ Lynch
├─ Selectbox: Lógica (k-of-n, AND, OR)
├─ Slider: k (mínimo de critérios)
├─ Slider: Top-K (máximo de ações)
├─ Selectbox: Ponderação (equal, score)
├─ Subheader: Backtesting
│  ├─ Date Input: Início
│  └─ Number Input: Capital inicial (R$)
└─ Layout: wide (aproveita tela inteira)

ESTADO (st.session_state):
    - carteira : DataFrame selecionada na ABA 1
    - backtest : Resultado do rodar_backtest() na ABA 2

RECURSO CRÍTICO: LOOK-AHEAD BIAS
    └─ Warning explicado na ABA 1 e 2
    └─ Recomendação: salvar carteira em CSV para reprodutibilidade
    └─ Solução futura: snapshots automáticos

EXEMPLO DE FLUXO COMPLETO:
    1. User abre interface
    2. Sidebar: ativa Graham1, Bazin, ROE; seed=42; k=2
    3. ABA 1: clica "Gerar Carteira"
       → Universo embaralhado (seed=42)
       → Filtros aplicados (k=2)
       → 15 melhores ações selecionadas
       → Carteira exibida em tabela + gráficos
    4. ABA 2: clica "Rodar Backtesting"
       → Backtest de 2015-2024
       → Métricas calculadas
       → Gráficos de equity curve e drawdown
    5. User pode exportar dados (CSV salvo automaticamente)

DEPENDÊNCIAS:
    - streamlit >= 1.0
    - plotly >= 5.0
    - pandas, yfinance, yaml

PERFORMANCE:
    - Carregamento universo: ~10-15s (yFinance)
    - Filtragem carteira: ~1-2s
    - Backtest 10 anos: ~30-60s (download de preços)

FUTURO:
    - Cache (@st.cache_data) para universo
    - Snapshots automáticos de carteira
    - Export PDF de relatório
    - Comparação entre múltiplos backtests
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import yaml
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from model.acoes import Acao
from model.universo import obter_dataframe_universo
from model.carteira import construir_carteira
from backtest.engine import rodar_backtest
from backtest.metricas import calcular_todas, serie_drawdown


# ──────────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ──────────────────────────────────────────────────────────────────

def _cfg():
    """Carrega config.yaml."""
    p = Path(__file__).parent.parent / "config.yaml"
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


cfg = _cfg()
cfg_est  = cfg.get("estrategias", {})
cfg_cart = cfg.get("carteira", {})
cfg_bt   = cfg.get("backtest", {})
cfg_p    = cfg.get("periodo", {})

st.set_page_config(
    page_title="Análise Fundamentalista — B3",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Sistema de Análise Fundamentalista — B3")
st.caption(
    "Graham · Bazin · Lynch · ROE Equivalente — "
    "TCC, Ciências da Computação, UFPI."
)
st.warning(
    "⚠️ **Este sistema tem finalidade exclusivamente acadêmica e não constitui "
    "recomendação de investimento.** Os resultados são baseados em backtesting "
    "histórico e sujeitos a limitações metodológicas (veja aba Backtesting). "
    "Decisões de investimento são de responsabilidade exclusiva do usuário."
)

# ──────────────────────────────────────────────────────────────────
# SIDEBAR: CONFIGURAÇÕES
# ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("⚙️ Configurações")

    # Tipo de teste
    tipo_teste = st.radio(
        "Tipo de teste",
        ["✅ Com filtros (recomendado)", 
         "⚠️ Sem filtros (baseline)"],
        help="Com filtros: Graham, Bazin, Lynch, ROE\n"
             "Sem filtros: 15 ações aleatórias (comparação justa)"
    )
    
    teste_sem_filtros = (tipo_teste == "⚠️ Sem filtros (baseline)")
    
    # Seed para reprodutibilidade
    st.subheader("🎲 Reprodutibilidade")
    semente_teste = st.number_input(
        "Semente Aleatória (Seed)",
        min_value=1,
        max_value=9999,
        value=42,
        step=1,
        help="Altera a aleatoriedade do embaralhamento.\n"
             "Mesma seed = mesma ordem de universo\n"
             "Use seeds 1-10 para 10 rodadas do experimento"
    )
    
    if teste_sem_filtros:
        st.warning("⚠️ Teste SEM FILTROS: 15 ações aleatórias (baseline).\n"
                  "Valida que filtros fundamentalistas geram alfa.")

    if not teste_sem_filtros:
        st.subheader("Critérios (checkboxes)")
        c_g1  = st.checkbox("Graham 1  (P/VP × P/L ≤ 22,5)",
                            value=cfg_est.get("graham1", {}).get("ativo", True))
        c_g2  = st.checkbox("Graham 2  (Preço ≤ √(22,5×LPA×VPA))",
                            value=cfg_est.get("graham2", {}).get("ativo", True))
        c_baz = st.checkbox("Bazin     (DY ≥ 6%)",
                            value=cfg_est.get("bazin",   {}).get("ativo", True))
        c_roe = st.checkbox("ROE Eq.   (ROE/P/VP ≥ 10%)",
                            value=cfg_est.get("roe_equivalente", {}).get("ativo", True))
        c_lyn = st.checkbox("Lynch     (PEG < 2)",
                            value=cfg_est.get("lynch",   {}).get("ativo", False))

        criterios = {
            "graham1": c_g1,
            "graham2": c_g2,
            "bazin":   c_baz,
            "roe_eq":  c_roe,
            "lynch":   c_lyn,
        }
        
        st.subheader("Combinação")
        logica = st.selectbox("Lógica", ["k-of-n", "AND", "OR"],
                              index=["k-of-n", "AND", "OR"].index(
                                  cfg_cart.get("logica", "k-of-n")))
        k      = st.slider("Mínimo de critérios (k)", 1, 5,
                           cfg_cart.get("k", 3))
        
    else:
        # Sem filtros: desativa automaticamente
        criterios = {
            "graham1": False,
            "graham2": False,
            "bazin": False,
            "roe_eq": False,
            "lynch": False,
        }
        logica = "OR"
        k = 0
        st.info("ℹ️ Critérios desativados automaticamente")

    top_k  = st.slider("Máximo de ações", 5, 30,
                       cfg_cart.get("top_k", 15))
    pond   = st.selectbox("Ponderação", ["equal", "score"],
                          index=0 if cfg_cart.get("ponderacao", "equal") == "equal" else 1)

    st.subheader("Backtesting")
    d_ini = st.date_input("Início", value=pd.to_datetime(
                          cfg_p.get("inicio", "2015-01-01")))
    capital = st.number_input("Capital inicial (R$)", min_value=1_000.0,
                              value=float(cfg_bt.get("capital_inicial", 100_000)),
                              step=1_000.0)

# ──────────────────────────────────────────────────────────────────
# ABAS PRINCIPAIS
# ──────────────────────────────────────────────────────────────────

aba1, aba2, aba3 = st.tabs(["🏗️ Carteira", "📊 Backtesting", "🔍 Ação Individual"])


# ════════════════════════════════════════════════════════════════
# ABA 1: CARTEIRA
# ════════════════════════════════════════════════════════════════
with aba1:
    st.subheader("Construção de Carteira")
    
    if teste_sem_filtros:
        st.info(f"⚠️ Modo TESTE SEM FILTROS — 15 ações aleatórias (Seed: {semente_teste})")
    else:
        st.info(f"✅ Modo COM FILTROS — Multicritério (Seed: {semente_teste})")

    if st.button("🔍 Gerar Carteira", width='stretch'):
        with st.spinner("Buscando universo e aplicando filtros..."):
            df_univ = obter_dataframe_universo()

            import random
            random.seed(semente_teste)
            shuffled_idx = df_univ.index.tolist()
            random.shuffle(shuffled_idx)
            df_univ = df_univ.loc[shuffled_idx]

            if df_univ.empty:
                st.error("Não foi possível carregar o universo.")
            else:
                if teste_sem_filtros:
                    st.info("⏳ Selecionando 15 ações SEM FILTROS (baseline)...")
                    df_c = df_univ.head(top_k or 15).copy()
                    df_c['score'] = 0
                    peso = 100 / len(df_c)
                    df_c['peso'] = peso
                    df_c['criterios_aprovados'] = "NENHUM (teste baseline)"
                    df_c = df_c.reset_index()
                    df_c = df_c.rename(columns={'index': 'ticker'})
                else:
                    st.info("⏳ Aplicando filtros fundamentalistas...")
                    df_c = construir_carteira(
                        df_univ, criterios=criterios,
                        logica=logica, k=k, top_k=top_k, ponderacao=pond,
                        seed=semente_teste
                    )
                
                if df_c.empty:
                    st.warning("Nenhuma ação selecionada.")
                else:
                    st.session_state["carteira"] = df_c
                    Path("data").mkdir(exist_ok=True)
                    df_c.to_csv(
                        f"data/carteira_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}_seed_{semente_teste}.csv",
                        index=False
                    )
                    if teste_sem_filtros:
                        st.warning(f"⚠️ {len(df_c)} ações SEM FILTROS (baseline) | Seed: {semente_teste}")
                    else:
                        st.success(f"✅ {len(df_c)} ações COM FILTROS | Seed: {semente_teste}")

    # Exibição da carteira
    if "carteira" in st.session_state:
        st.warning(
            "⚠️ **Look-Ahead Bias:** Os indicadores fundamentalistas (DY, P/L, etc.) "
            "mudam diariamente. A mesma seed pode gerar carteiras diferentes em datas "
            "diferentes. Para reprodutibilidade total, salve a carteira acima em CSV."
        )
        
        df_c = st.session_state["carteira"]
        col1, col2 = st.columns([3, 2])

        with col1:
            st.dataframe(
                df_c[["ticker", "score", "dy", "pl", "pvp", "roe", "peso"]].rename(
                    columns={"ticker": "Ticker", "score": "Score",
                             "dy": "DY%", "pl": "P/L", "pvp": "P/VP",
                             "roe": "ROE%", "peso": "Peso%"}
                ),
                width='stretch', hide_index=True,
            )

        with col2:
            fig = px.pie(df_c, values="peso", names="ticker",
                         title="Composição da Carteira", hole=0.4)
            st.plotly_chart(fig, width='stretch')

        fig2 = px.bar(
            df_c.sort_values("score", ascending=True),
            x="score", y="ticker", orientation="h",
            title="Score por Ação (critérios aprovados)",
            color="score", color_continuous_scale="Teal",
        )
        st.plotly_chart(fig2, width='stretch')


# ════════════════════════════════════════════════════════════════
# ABA 2: BACKTESTING
# ════════════════════════════════════════════════════════════════
with aba2:
    st.subheader("Backtesting Histórico")
    st.info(
        "⚠️ **Look-Ahead Bias (TCC 3.7):** Os filtros fundamentalistas são aplicados "
        "com indicadores de HOJE, mas simulam retornos de 2015–2024. Indicadores reais "
        "evoluem ao longo do tempo (DY muda, P/L muda, etc.). Uma avaliação rigorosa "
        "exigiria snapshots históricos via Economática/Bloomberg."
    )

    if st.button("▶️ Rodar Backtesting", width='stretch'):
        with st.spinner("Executando backtesting (minutos)..."):
            carteira_selecionada = st.session_state.get("carteira", None)

            if carteira_selecionada is None:
                st.error("⚠️ Gere uma carteira primeiro na ABA 1!")
            else:
                res = rodar_backtest(
                    carteira=carteira_selecionada,
                    data_inicio=d_ini.isoformat(), 
                    capital_inicial=capital,
                    teste_sem_filtros=teste_sem_filtros,
                )
            if res:
                st.session_state["backtest"] = res
                Path("data").mkdir(exist_ok=True)
                res["retornos"].to_csv("data/retornos_carteira.csv")
                if not res["retornos_ibov"].empty:
                    res["retornos_ibov"].to_csv("data/retornos_ibov.csv")
                st.success("✅ Backtesting concluído!")

    # Exibição dos resultados
    if "backtest" in st.session_state:
        res = st.session_state["backtest"]
        ret   = res["retornos"]
        pat   = res["patrimonio"]
        r_ibov = res.get("retornos_ibov", pd.Series(dtype=float))
        p_ibov = res.get("patrimonio_ibov", pd.Series(dtype=float))

        metricas = calcular_todas(ret, pat,
                                  r_ibov if not r_ibov.empty else None)
        
        teste_tipo = res.get("teste_tipo", "com_filtros")
        if teste_tipo == "sem_filtros":
            st.warning(f"📊 RESULTADO DO TESTE SEM FILTROS (Baseline) | Seed: {semente_teste}")
        else:
            st.success(f"📊 RESULTADO DO TESTE COM FILTROS | Seed: {semente_teste}")

        # KPIs
        cols = st.columns(4)
        kpis = [("CAGR (% a.a.)", "📈"), ("Sharpe Ratio", "⚖️"),
                ("Máximo Drawdown (%)", "📉"), ("Outperformance (%)", "🏆")]
        for i, (k_nome, icon) in enumerate(kpis):
            cols[i].metric(f"{icon} {k_nome}",
                           metricas.get(k_nome, "N/A"))

        with st.expander("📋 Todas as métricas"):
            df_m = pd.DataFrame(metricas.items(),
                                columns=["Métrica", "Valor"])
            st.dataframe(df_m, width='stretch', hide_index=True)

        # Equity curve
        fig_eq = go.Figure()
        fig_eq.add_trace(go.Scatter(
            x=pat.index, y=pat.values,
            name="Carteira", line=dict(color="#1D9E75", width=2)
        ))
        if not p_ibov.empty:
            fig_eq.add_trace(go.Scatter(
                x=p_ibov.index, y=p_ibov.values,
                name="Ibovespa", line=dict(color="#E24B4A", width=1.5, dash="dash")
            ))
        fig_eq.update_layout(
            title=f"Equity Curve — Evolução do Patrimônio (Seed: {semente_teste})",
            xaxis_title="Data", yaxis_title="Patrimônio (R$)",
            hovermode="x unified",
        )
        st.plotly_chart(fig_eq, width='stretch')

        # Drawdown
        dd = serie_drawdown(pat) * 100
        fig_dd = go.Figure()
        fig_dd.add_trace(go.Scatter(
            x=dd.index, y=dd.values, fill="tozeroy",
            name="Drawdown", line=dict(color="#E24B4A"),
            fillcolor="rgba(226,75,74,0.2)"
        ))
        fig_dd.update_layout(
            title="Drawdown (%)",
            xaxis_title="Data", yaxis_title="Drawdown (%)",
        )
        st.plotly_chart(fig_dd, width='stretch')

        st.subheader("Ações na carteira do backtest")
        st.dataframe(res["carteira"],
                     width='stretch', hide_index=True)


# ════════════════════════════════════════════════════════════════
# ABA 3: AÇÃO INDIVIDUAL
# ════════════════════════════════════════════════════════════════
with aba3:
    st.subheader("Análise de Ação Individual")
    ticker_in = st.text_input("Digite o ticker (ex: WEGE3, ITUB4):").upper()

    if st.button("🔎 Analisar") and ticker_in:
        with st.spinner(f"Buscando {ticker_in}..."):
            a = Acao()
            ok = a.BuscarIndicadores(ticker_in)

        if not ok:
            st.error(f"Dados não encontrados para {ticker_in}.")
        else:
            st.success(f"✅ Indicadores de {ticker_in}")

            ind = {
                "Preço (R$)":    a.PrecoAcao,
                "P/VP":          a.PVP,
                "P/L":           a.PL,
                "DY (%)":        a.DY,
                "ROE (%)":       a.ROE,
                "Crescimento (%)": a.Crescimento,
                "Payout (%)":    a.Payout,
                "VPA (R$)":      a.VPA,
                "LPA (R$)":      a.LPA,
            }
            st.dataframe(
                pd.DataFrame(ind.items(), columns=["Indicador", "Valor"]),
                width='stretch', hide_index=True
            )

            st.subheader("Resultado dos critérios")
            testes = {
                "Graham 1":        (a.GetGraham1,       c_g1),
                "Graham 2":        (a.GetGraham2,       c_g2),
                "Bazin (DY≥6%)":   (a.GetMetodoBazin,  c_baz),
                "ROE Equivalente": (a.GetRoeEquivalente, c_roe),
                "Lynch (PEG<2)":   (a.GetMetodoLynch,  c_lyn),
            }
            cols = st.columns(5)
            for i, (nome, (func, ativo)) in enumerate(testes.items()):
                if ativo:
                    r = func()
                    cols[i].metric(nome, "✅ Aprovado" if r else "❌ Reprovado")
                else:
                    cols[i].metric(nome, "⏸️ Desativado")
