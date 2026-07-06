"""
gerar_graficos_linhas.py
========================

DESCRIÇÃO:
    Gera gráficos de LINHAS para as 3 hipóteses.
    Mostra a evolução de cada métrica ao longo das 10 rodadas.
    
    Melhor para visualizar:
    - Tendência geral
    - Variação rodada a rodada
    - Consistência da estratégia com filtros
    
EXECUÇÃO:
    $ python gerar_graficos_linhas.py
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


def plotar_h1_linhas(df):
    """
    H1: Performance (Linhas)
    Mostra evolução das 10 rodadas
    """
    print("\n📈 H1 — PERFORMANCE (Gráfico de Linhas)")
    
    df_com = df[df['tipo'] == 'com_filtros'].sort_values('seed').reset_index(drop=True)
    df_sem = df[df['tipo'] == 'sem_filtros'].sort_values('seed').reset_index(drop=True)
    
    fig = go.Figure()
    
    # Linha com filtros
    fig.add_trace(go.Scatter(
        x=df_com['seed'],
        y=df_com['Performance (%)'],
        mode='lines+markers',
        name='Com Filtros',
        line=dict(color='#1D9E75', width=3),
        marker=dict(size=10, symbol='circle'),
        fill='tozeroy',
        fillcolor='rgba(29, 158, 117, 0.2)',
        hovertemplate='<b>Rodada %{x}</b><br>Performance: %{y:.2f}%<extra></extra>'
    ))
    
    # Linha sem filtros
    fig.add_trace(go.Scatter(
        x=df_sem['seed'],
        y=df_sem['Performance (%)'],
        mode='lines+markers',
        name='Sem Filtros',
        line=dict(color='#E24B4A', width=3, dash='dash'),
        marker=dict(size=10, symbol='diamond'),
        fill='tozeroy',
        fillcolor='rgba(226, 75, 74, 0.1)',
        hovertemplate='<b>Rodada %{x}</b><br>Performance: %{y:.2f}%<extra></extra>'
    ))
    
    # Linha de média com filtros
    media_com = df_com['Performance (%)'].mean()
    fig.add_hline(
        y=media_com,
        line_dash="dot",
        line_color="#1D9E75",
        annotation_text=f"Média Com Filtros: {media_com:.2f}%",
        annotation_position="right"
    )
    
    # Linha de média sem filtros
    media_sem = df_sem['Performance (%)'].mean()
    fig.add_hline(
        y=media_sem,
        line_dash="dot",
        line_color="#E24B4A",
        annotation_text=f"Média Sem Filtros: {media_sem:.2f}%",
        annotation_position="right"
    )
    
    fig.update_layout(
        title='<b>H1: Performance ao Longo de 10 Rodadas</b><br><sub>Mostra consistência e variação (Outperformance vs Ibovespa)</sub>',
        xaxis_title='Seed (Rodada)',
        yaxis_title='Performance (%)',
        height=600,
        hovermode='x unified',
        template='plotly_dark',
        font=dict(size=12),
        legend=dict(x=0.02, y=0.98)
    )
    
    fig.write_html("analise/h1_performance_linhas.html")
    
    print(f"  ✅ Com Filtros Média: {media_com:.2f}%")
    print(f"  ⚠️  Sem Filtros Média: {media_sem:.2f}%")
    print(f"  📊 Diferença: +{media_com - media_sem:.2f}%")


def plotar_h2_linhas(df):
    """
    H2: Volatilidade (Linhas)
    Mostra consistência do risco
    """
    print("\n📊 H2 — VOLATILIDADE ANUALIZADA (Gráfico de Linhas)")
    
    df_com = df[df['tipo'] == 'com_filtros'].sort_values('seed').reset_index(drop=True)
    df_sem = df[df['tipo'] == 'sem_filtros'].sort_values('seed').reset_index(drop=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_com['seed'],
        y=df_com['Volatilidade Anual (%)'],
        mode='lines+markers',
        name='Com Filtros',
        line=dict(color='#1D9E75', width=3),
        marker=dict(size=10, symbol='circle'),
        fill='tozeroy',
        fillcolor='rgba(29, 158, 117, 0.2)',
        hovertemplate='<b>Rodada %{x}</b><br>Volatilidade: %{y:.2f}%<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=df_sem['seed'],
        y=df_sem['Volatilidade Anual (%)'],
        mode='lines+markers',
        name='Sem Filtros',
        line=dict(color='#E24B4A', width=3, dash='dash'),
        marker=dict(size=10, symbol='diamond'),
        fill='tozeroy',
        fillcolor='rgba(226, 75, 74, 0.1)',
        hovertemplate='<b>Rodada %{x}</b><br>Volatilidade: %{y:.2f}%<extra></extra>'
    ))
    
    media_com = df_com['Volatilidade Anual (%)'].mean()
    fig.add_hline(
        y=media_com,
        line_dash="dot",
        line_color="#1D9E75",
        annotation_text=f"Média Com Filtros: {media_com:.2f}%",
        annotation_position="right"
    )
    
    media_sem = df_sem['Volatilidade Anual (%)'].mean()
    fig.add_hline(
        y=media_sem,
        line_dash="dot",
        line_color="#E24B4A",
        annotation_text=f"Média Sem Filtros: {media_sem:.2f}%",
        annotation_position="right"
    )
    
    fig.update_layout(
        title='<b>H2: Volatilidade Anualizada ao Longo de 10 Rodadas</b><br><sub>Menor = Menor risco (Mais consistente)</sub>',
        xaxis_title='Seed (Rodada)',
        yaxis_title='Volatilidade (%)',
        height=600,
        hovermode='x unified',
        template='plotly_dark',
        font=dict(size=12),
        legend=dict(x=0.02, y=0.98)
    )
    
    fig.write_html("analise/h2_volatilidade_linhas.html")
    
    print(f"  ✅ Com Filtros Média: {media_com:.2f}%")
    print(f"  ⚠️  Sem Filtros Média: {media_sem:.2f}%")
    print(f"  📊 Diferença: {media_com - media_sem:.2f}% (Com filtros é mais estável)")


def plotar_h3_linhas(df):
    """
    H3: Drawdown (Linhas)
    Mostra proteção ao longo das rodadas
    """
    print("\n📉 H3 — MÁXIMO DRAWDOWN (Gráfico de Linhas)")
    
    df_com = df[df['tipo'] == 'com_filtros'].sort_values('seed').reset_index(drop=True)
    df_sem = df[df['tipo'] == 'sem_filtros'].sort_values('seed').reset_index(drop=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_com['seed'],
        y=df_com['Máximo Drawdown (%)'],
        mode='lines+markers',
        name='Com Filtros',
        line=dict(color='#1D9E75', width=3),
        marker=dict(size=10, symbol='circle'),
        fill='tozeroy',
        fillcolor='rgba(29, 158, 117, 0.2)',
        hovertemplate='<b>Rodada %{x}</b><br>Drawdown: %{y:.2f}%<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=df_sem['seed'],
        y=df_sem['Máximo Drawdown (%)'],
        mode='lines+markers',
        name='Sem Filtros',
        line=dict(color='#E24B4A', width=3, dash='dash'),
        marker=dict(size=10, symbol='diamond'),
        fill='tozeroy',
        fillcolor='rgba(226, 75, 74, 0.1)',
        hovertemplate='<b>Rodada %{x}</b><br>Drawdown: %{y:.2f}%<extra></extra>'
    ))
    
    media_com = df_com['Máximo Drawdown (%)'].mean()
    fig.add_hline(
        y=media_com,
        line_dash="dot",
        line_color="#1D9E75",
        annotation_text=f"Média Com Filtros: {media_com:.2f}%",
        annotation_position="right"
    )
    
    media_sem = df_sem['Máximo Drawdown (%)'].mean()
    fig.add_hline(
        y=media_sem,
        line_dash="dot",
        line_color="#E24B4A",
        annotation_text=f"Média Sem Filtros: {media_sem:.2f}%",
        annotation_position="right"
    )
    
    fig.update_layout(
        title='<b>H3: Máximo Drawdown ao Longo de 10 Rodadas</b><br><sub>Mais próximo de 0 = Melhor proteção (Menos queda)</sub>',
        xaxis_title='Seed (Rodada)',
        yaxis_title='Drawdown (%)',
        height=600,
        hovermode='x unified',
        template='plotly_dark',
        font=dict(size=12),
        legend=dict(x=0.02, y=0.98)
    )
    
    fig.write_html("analise/h3_drawdown_linhas.html")
    
    print(f"  ✅ Com Filtros Média: {media_com:.2f}%")
    print(f"  ⚠️  Sem Filtros Média: {media_sem:.2f}%")
    print(f"  📊 Diferença: {media_com - media_sem:.2f}% (Com filtros reduz queda)")


def plotar_resumo_linhas_matplotlib(df):
    """
    Resumo em matplotlib com linhas (3 subgráficos).
    """
    df_com = df[df['tipo'] == 'com_filtros'].sort_values('seed')
    df_sem = df[df['tipo'] == 'sem_filtros'].sort_values('seed')
    
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    # H1 — Performance
    ax = axes[0]
    ax.plot(df_com['seed'], df_com['Performance (%)'], 
            marker='o', linewidth=3, markersize=8, 
            color='#1D9E75', label='Com Filtros', alpha=0.8)
    ax.plot(df_sem['seed'], df_sem['Performance (%)'], 
            marker='s', linewidth=3, markersize=8, 
            color='#E24B4A', label='Sem Filtros', linestyle='--', alpha=0.8)
    
    ax.axhline(y=df_com['Performance (%)'].mean(), color='#1D9E75', 
               linestyle=':', linewidth=2, alpha=0.6)
    ax.axhline(y=df_sem['Performance (%)'].mean(), color='#E24B4A', 
               linestyle=':', linewidth=2, alpha=0.6)
    
    ax.set_xlabel('Rodada (Seed)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Performance (%)', fontsize=11, fontweight='bold')
    ax.set_title('H1: Performance\n(Outperformance vs Ibovespa)', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_xticks(range(1, 11))
    
    # H2 — Volatilidade
    ax = axes[1]
    ax.plot(df_com['seed'], df_com['Volatilidade Anual (%)'], 
            marker='o', linewidth=3, markersize=8, 
            color='#1D9E75', label='Com Filtros', alpha=0.8)
    ax.plot(df_sem['seed'], df_sem['Volatilidade Anual (%)'], 
            marker='s', linewidth=3, markersize=8, 
            color='#E24B4A', label='Sem Filtros', linestyle='--', alpha=0.8)
    
    ax.axhline(y=df_com['Volatilidade Anual (%)'].mean(), color='#1D9E75', 
               linestyle=':', linewidth=2, alpha=0.6)
    ax.axhline(y=df_sem['Volatilidade Anual (%)'].mean(), color='#E24B4A', 
               linestyle=':', linewidth=2, alpha=0.6)
    
    ax.set_xlabel('Rodada (Seed)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Volatilidade (%)', fontsize=11, fontweight='bold')
    ax.set_title('H2: Volatilidade Anualizada\n(Menor = Melhor)', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_xticks(range(1, 11))
    
    # H3 — Drawdown
    ax = axes[2]
    ax.plot(df_com['seed'], df_com['Máximo Drawdown (%)'], 
            marker='o', linewidth=3, markersize=8, 
            color='#1D9E75', label='Com Filtros', alpha=0.8)
    ax.plot(df_sem['seed'], df_sem['Máximo Drawdown (%)'], 
            marker='s', linewidth=3, markersize=8, 
            color='#E24B4A', label='Sem Filtros', linestyle='--', alpha=0.8)
    
    ax.axhline(y=df_com['Máximo Drawdown (%)'].mean(), color='#1D9E75', 
               linestyle=':', linewidth=2, alpha=0.6)
    ax.axhline(y=df_sem['Máximo Drawdown (%)'].mean(), color='#E24B4A', 
               linestyle=':', linewidth=2, alpha=0.6)
    
    ax.set_xlabel('Rodada (Seed)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Drawdown (%)', fontsize=11, fontweight='bold')
    ax.set_title('H3: Máximo Drawdown\n(Mais próximo de 0 = Melhor)', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_xticks(range(1, 11))
    
    plt.suptitle('Evolução das 3 Hipóteses ao Longo de 10 Rodadas', 
                 fontsize=14, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig('analise/resumo_linhas.png', dpi=300, bbox_inches='tight')
    print("\n✅ Gráfico resumido (linhas) salvo em analise/resumo_linhas.png")


def main():
    """Executa análise com gráficos de linhas."""
    
    print("\n" + "="*70)
    print("  📈 ANÁLISE COM GRÁFICOS DE LINHAS")
    print("="*70)
    
    df = carregar_dados()
    
    print(f"\n✅ Dados carregados:")
    print(f"   - Com Filtros: {len(df[df['tipo']=='com_filtros'])} rodadas")
    print(f"   - Sem Filtros: {len(df[df['tipo']=='sem_filtros'])} rodadas")
    
    criar_diretorio()
    
    # Gerar gráficos de linhas
    plotar_h1_linhas(df)
    plotar_h2_linhas(df)
    plotar_h3_linhas(df)
    plotar_resumo_linhas_matplotlib(df)
    
    print("\n" + "="*70)
    print("  ✅ ANÁLISE COM LINHAS CONCLUÍDA!")
    print("="*70)
    print("\n📁 Gráficos salvos em analise/:")
    print("   ├─ h1_performance_linhas.html (interativo)")
    print("   ├─ h2_volatilidade_linhas.html (interativo)")
    print("   ├─ h3_drawdown_linhas.html (interativo)")
    print("   └─ resumo_linhas.png (estático)")
    print("\n💡 Abra os .html no navegador para versões interativas!")
    print("   Os gráficos de linhas mostram melhor a evolução e consistência!\n")


if __name__ == "__main__":
    main()