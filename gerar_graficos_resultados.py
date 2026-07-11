"""
gerar_graficos_resultados.py
=============================

DESCRIÇÃO:
    Gera gráficos de BARRAS (agrupadas) para as 3 hipóteses.
    Compara, rodada a rodada, o desempenho com filtros vs. sem filtros.

    Melhor para visualizar:
    - Comparação direta rodada a rodada (com vs. sem filtros)
    - Diferença absoluta entre as duas condições
    - Leitura rápida em apresentação/TCC

EXECUÇÃO:
    $ python gerar_graficos_resultados.py
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# Configurar matplotlib
plt.rcParams['figure.figsize'] = (16, 5)
plt.rcParams['font.size'] = 10
sns.set_style("whitegrid")


def carregar_dados():
    """Carrega os dados reais do CSV."""
    try:
        df = pd.read_csv("data/resultados_reais.csv")
        return df
    except FileNotFoundError:
        print("❌ Arquivo não encontrado: data/resultados_reais.csv")
        exit(1)


def criar_diretorio():
    """Cria diretório para gráficos."""
    Path("analise").mkdir(exist_ok=True)


def plotar_h1_barras(df):
    """
    H1: Performance (Barras)
    Compara com/sem filtros rodada a rodada
    """
    print("\n📈 H1 — PERFORMANCE (Gráfico de Barras)")

    df_com = df[df['tipo'] == 'com_filtros'].sort_values('seed').reset_index(drop=True)
    df_sem = df[df['tipo'] == 'sem_filtros'].sort_values('seed').reset_index(drop=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_com['seed'],
        y=df_com['Performance (%)'],
        name='Com Filtros',
        marker_color='#1D9E75',
        text=df_com['Performance (%)'],
        texttemplate='%{text:.1f}',
        textposition='inside',
        textangle=-90,
        textfont=dict(color='white', size=11),
        hovertemplate='<b>Rodada %{x}</b><br>Performance: %{y:.2f}%<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=df_sem['seed'],
        y=df_sem['Performance (%)'],
        name='Sem Filtros',
        marker_color='#E24B4A',
        text=df_sem['Performance (%)'],
        texttemplate='%{text:.1f}',
        textposition='inside',
        textangle=-90,
        textfont=dict(color='white', size=11),
        hovertemplate='<b>Rodada %{x}</b><br>Performance: %{y:.2f}%<extra></extra>'
    ))

    media_com = df_com['Performance (%)'].mean()
    media_sem = df_sem['Performance (%)'].mean()

    fig.update_layout(
        title=dict(
            text='<b>Q1: Performance (Outperformance vs Ibovespa)</b>'
                 '<br><sup>10 rodadas com seed 1-10</sup>',
            x=0.01, xanchor='left', y=0.95, yanchor='top', font=dict(size=16),
        ),
        xaxis_title='Seed (Rodada)',
        yaxis_title='Performance (%)',
        xaxis=dict(dtick=2),
        barmode='group',
        height=600,
        hovermode='x unified',
        template='plotly_dark',
        font=dict(size=12),
        legend=dict(x=1.0, y=1.0),
        uniformtext_minsize=9,
    )

    fig.write_html("analise/h1_outperformance_real.html")
    fig.write_image("analise/h1_outperformance_real.png", scale=2)

    print(f"  ✅ Com Filtros Média: {media_com:.2f}%")
    print(f"  ⚠️  Sem Filtros Média: {media_sem:.2f}%")
    print(f"  📊 Diferença: +{media_com - media_sem:.2f}%")


def plotar_h2_barras(df):
    """
    H2: Volatilidade (Barras)
    Compara consistência do risco rodada a rodada
    """
    print("\n📊 H2 — VOLATILIDADE ANUALIZADA (Gráfico de Barras)")

    df_com = df[df['tipo'] == 'com_filtros'].sort_values('seed').reset_index(drop=True)
    df_sem = df[df['tipo'] == 'sem_filtros'].sort_values('seed').reset_index(drop=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_com['seed'],
        y=df_com['Volatilidade Anual (%)'],
        name='Com Filtros',
        marker_color='#1D9E75',
        text=df_com['Volatilidade Anual (%)'],
        texttemplate='%{text:.1f}',
        textposition='inside',
        textangle=-90,
        textfont=dict(color='white', size=11),
        hovertemplate='<b>Rodada %{x}</b><br>Volatilidade: %{y:.2f}%<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=df_sem['seed'],
        y=df_sem['Volatilidade Anual (%)'],
        name='Sem Filtros',
        marker_color='#E24B4A',
        text=df_sem['Volatilidade Anual (%)'],
        texttemplate='%{text:.1f}',
        textposition='inside',
        textangle=-90,
        textfont=dict(color='white', size=11),
        hovertemplate='<b>Rodada %{x}</b><br>Volatilidade: %{y:.2f}%<extra></extra>'
    ))

    media_com = df_com['Volatilidade Anual (%)'].mean()
    media_sem = df_sem['Volatilidade Anual (%)'].mean()

    fig.update_layout(
        title=dict(
            text='<b>Q2: Volatilidade Anualizada (Menor = Menor Risco)</b>'
                 '<br><sup>10 rodadas com seed 1-10</sup>',
            x=0.01, xanchor='left', y=0.95, yanchor='top', font=dict(size=16),
        ),
        xaxis_title='Seed (Rodada)',
        yaxis_title='Volatilidade (%)',
        xaxis=dict(dtick=2),
        barmode='group',
        height=600,
        hovermode='x unified',
        template='plotly_dark',
        font=dict(size=12),
        legend=dict(x=1.0, y=1.0),
        uniformtext_minsize=9,
    )

    fig.write_html("analise/h2_volatilidade_real.html")
    fig.write_image("analise/h2_volatilidade_real.png", scale=2)

    print(f"  ✅ Com Filtros Média: {media_com:.2f}%")
    print(f"  ⚠️  Sem Filtros Média: {media_sem:.2f}%")
    print(f"  📊 Diferença: {media_com - media_sem:.2f}% (Com filtros é mais estável)")


def plotar_h3_barras(df):
    """
    H3: Drawdown (Barras)
    Compara proteção rodada a rodada
    """
    print("\n📉 H3 — MÁXIMO DRAWDOWN (Gráfico de Barras)")

    df_com = df[df['tipo'] == 'com_filtros'].sort_values('seed').reset_index(drop=True)
    df_sem = df[df['tipo'] == 'sem_filtros'].sort_values('seed').reset_index(drop=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_com['seed'],
        y=df_com['Máximo Drawdown (%)'],
        name='Com Filtros',
        marker_color='#1D9E75',
        text=df_com['Máximo Drawdown (%)'],
        texttemplate='%{text:.1f}',
        textposition='inside',
        textangle=-90,
        textfont=dict(color='white', size=11),
        hovertemplate='<b>Rodada %{x}</b><br>Drawdown: %{y:.2f}%<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=df_sem['seed'],
        y=df_sem['Máximo Drawdown (%)'],
        name='Sem Filtros',
        marker_color='#E24B4A',
        text=df_sem['Máximo Drawdown (%)'],
        texttemplate='%{text:.1f}',
        textposition='inside',
        textangle=-90,
        textfont=dict(color='white', size=11),
        hovertemplate='<b>Rodada %{x}</b><br>Drawdown: %{y:.2f}%<extra></extra>'
    ))

    media_com = df_com['Máximo Drawdown (%)'].mean()
    media_sem = df_sem['Máximo Drawdown (%)'].mean()

    fig.update_layout(
        title=dict(
            text='<b>Q3: Máximo Drawdown (Mais Próximo de 0 = Melhor)</b>'
                 '<br><sup>10 rodadas com seed 1-10</sup>',
            x=0.01, xanchor='left', y=0.95, yanchor='top', font=dict(size=16),
        ),
        xaxis_title='Seed (Rodada)',
        yaxis_title='Drawdown (%)',
        xaxis=dict(dtick=2),
        barmode='group',
        height=600,
        hovermode='x unified',
        template='plotly_dark',
        font=dict(size=12),
        legend=dict(x=1.0, y=1.0),
        uniformtext_minsize=9,
    )

    fig.write_html("analise/h3_drawdown_real.html")
    fig.write_image("analise/h3_drawdown_real.png", scale=2)

    print(f"  ✅ Com Filtros Média: {media_com:.2f}%")
    print(f"  ⚠️  Sem Filtros Média: {media_sem:.2f}%")
    print(f"  📊 Diferença: {media_com - media_sem:.2f}% (Com filtros reduz queda)")


def plotar_resumo_barras_matplotlib(df):
    """
    Resumo em matplotlib com barras agrupadas (3 subgráficos).
    """
    df_com = df[df['tipo'] == 'com_filtros'].sort_values('seed')
    df_sem = df[df['tipo'] == 'sem_filtros'].sort_values('seed')

    largura = 0.35
    x = np.arange(1, 11)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # H1 — Performance
    ax = axes[0]
    ax.bar(x - largura / 2, df_com['Performance (%)'], width=largura,
           color='#1D9E75', label='Com Filtros', alpha=0.85)
    ax.bar(x + largura / 2, df_sem['Performance (%)'], width=largura,
           color='#E24B4A', label='Sem Filtros', alpha=0.85)

    ax.axhline(y=df_com['Performance (%)'].mean(), color='#1D9E75',
               linestyle=':', linewidth=2, alpha=0.6)
    ax.axhline(y=df_sem['Performance (%)'].mean(), color='#E24B4A',
               linestyle=':', linewidth=2, alpha=0.6)

    ax.set_xlabel('Rodada (Seed)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Performance (%)', fontsize=11, fontweight='bold')
    ax.set_title('Q1: Performance\n(Outperformance vs Ibovespa)', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_xticks(x)

    # H2 — Volatilidade
    ax = axes[1]
    ax.bar(x - largura / 2, df_com['Volatilidade Anual (%)'], width=largura,
           color='#1D9E75', label='Com Filtros', alpha=0.85)
    ax.bar(x + largura / 2, df_sem['Volatilidade Anual (%)'], width=largura,
           color='#E24B4A', label='Sem Filtros', alpha=0.85)

    ax.axhline(y=df_com['Volatilidade Anual (%)'].mean(), color='#1D9E75',
               linestyle=':', linewidth=2, alpha=0.6)
    ax.axhline(y=df_sem['Volatilidade Anual (%)'].mean(), color='#E24B4A',
               linestyle=':', linewidth=2, alpha=0.6)

    ax.set_xlabel('Rodada (Seed)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Volatilidade (%)', fontsize=11, fontweight='bold')
    ax.set_title('Q2: Volatilidade Anualizada\n(Menor = Melhor)', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_xticks(x)

    # H3 — Drawdown
    ax = axes[2]
    ax.bar(x - largura / 2, df_com['Máximo Drawdown (%)'], width=largura,
           color='#1D9E75', label='Com Filtros', alpha=0.85)
    ax.bar(x + largura / 2, df_sem['Máximo Drawdown (%)'], width=largura,
           color='#E24B4A', label='Sem Filtros', alpha=0.85)

    ax.axhline(y=df_com['Máximo Drawdown (%)'].mean(), color='#1D9E75',
               linestyle=':', linewidth=2, alpha=0.6)
    ax.axhline(y=df_sem['Máximo Drawdown (%)'].mean(), color='#E24B4A',
               linestyle=':', linewidth=2, alpha=0.6)

    ax.set_xlabel('Rodada (Seed)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Drawdown (%)', fontsize=11, fontweight='bold')
    ax.set_title('Q3: Máximo Drawdown\n(Mais próximo de 0 = Melhor)', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_xticks(x)

    plt.suptitle('Evolução das 3 Hipóteses ao Longo de 10 Rodadas',
                 fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig('analise/resumo_real.png', dpi=300, bbox_inches='tight')
    print("\n✅ Gráfico resumido (barras) salvo em analise/resumo_real.png")


def main():
    """Executa análise com gráficos de barras."""

    print("\n" + "="*70)
    print("  📊 ANÁLISE COM GRÁFICOS DE BARRAS")
    print("="*70)

    df = carregar_dados()

    print(f"\n✅ Dados carregados:")
    print(f"   - Com Filtros: {len(df[df['tipo']=='com_filtros'])} rodadas")
    print(f"   - Sem Filtros: {len(df[df['tipo']=='sem_filtros'])} rodadas")

    criar_diretorio()

    # Gerar gráficos de barras
    plotar_h1_barras(df)
    plotar_h2_barras(df)
    plotar_h3_barras(df)
    plotar_resumo_barras_matplotlib(df)

    print("\n" + "="*70)
    print("  ✅ ANÁLISE COM BARRAS CONCLUÍDA!")
    print("="*70)
    print("\n📁 Gráficos salvos em analise/:")
    print("   ├─ h1_outperformance_real.html (interativo)")
    print("   ├─ h2_volatilidade_real.html (interativo)")
    print("   ├─ h3_drawdown_real.html (interativo)")
    print("   └─ resumo_real.png (estático)")
    print("\n💡 Abra os .html no navegador para versões interativas!")
    print("   Os gráficos de barras facilitam a comparação direta por rodada!\n")


if __name__ == "__main__":
    main()
