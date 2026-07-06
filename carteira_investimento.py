"""
carteira_investimento.py
========================

DESCRIÇÃO:
    Ponto de entrada (main) do sistema de análise fundamentalista.
    Oferece ao usuário a escolha entre:
    - Interface web (Streamlit) — RECOMENDADA
    - Interface terminal (CLI) — alternativa rápida

REFERÊNCIAS:
    - TCC seção 6.8: Interface e Visualização
    - menu.py: interface CLI
    - interface/app.py: interface Streamlit

COMO USAR:

    ┌─ OPÇÃO 1: Interface Web (RECOMENDADA) ────────────────────┐
    │                                                             │
    │  $ streamlit run interface/app.py                          │
    │                                                             │
    │  → Abre http://localhost:8501                              │
    │  → 3 abas interativas (Carteira, Backtesting, Individual)  │
    │  → Gráficos, sliders, configurações visuais                │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
    
    ┌─ OPÇÃO 2: Menu Terminal ──────────────────────────────────┐
    │                                                             │
    │  $ python carteira_investimento.py                         │
    │                                                             │
    │  → Menu interativo em linha de comando                      │
    │  → Entrada de dados via input()                            │
    │  → Sem gráficos (apenas texto)                             │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘

FLUXO PRINCIPAL:
    main()
    ├─ Exibe cabeçalho (nome do sistema)
    ├─ Instrução para abrir app.py via Streamlit
    └─ Loop:
       ├─ menu.menu() → retorna True/False
       └─ True = continua; False = sair

ESTRUTURA:
    - Simples e enxuta (apenas 20 linhas)
    - Sem lógica complexa (delega para menu.py e app.py)
    - Ponto de entrada único do sistema

RECOMENDAÇÃO:
    Para **defesa e uso final**: use interface/app.py (Streamlit)
    Para **testes rápidos**: use menu.py (CLI)
    Arquivo carteira_investimento.py: apenas dispatcher

FUTURO:
    - Adicionar entrada de argumentos CLI (--modo, --seed, --tcc)
    - Menu inicial para escolher interface
    - Log de execução (arquivo de histórico)
"""

import menu


def main():
    """
    Função principal: exibe cabeçalho e loop do menu terminal.
    
    FLUXO:
        1. Imprime cabeçalho do sistema
        2. Instrui sobre interface web
        3. Loop contínuo:
           ├─ menu.menu() retorna bool
           ├─ True: volta ao menu
           └─ False (opção 0): sai
    """
    print("=" * 45)
    print("  SISTEMA DE ANÁLISE FUNDAMENTALISTA — B3")
    print("  Graham · Bazin · Lynch · ROE Equivalente")
    print("=" * 45)
    print("  ⚠️  Uso acadêmico. NÃO é recomendação de investimento.")
    print("=" * 45)
    print("\n💡 Interface web: streamlit run interface/app.py\n")

    continuar = True
    while continuar:
        continuar = menu.menu()


if __name__ == "__main__":
    main()