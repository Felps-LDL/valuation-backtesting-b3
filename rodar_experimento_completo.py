"""
rodar_experimento_completo.py
-----
Executa o experimento completo conforme TCC seção 4:
- 10 rodadas para teste COM filtros
- 10 rodadas para teste SEM filtros
Salva resultados em CSV para análise
"""

import pandas as pd
from model.universo import obter_dataframe_universo
from model.carteira import construir_carteira
from backtest.engine import rodar_backtest
from backtest.metricas import calcular_todas

def rodar_10_rodadas(teste_sem_filtros=False):
    resultados_rodadas = []
    
    for seed in range(1, 11):
        print(f"\n{'='*60}")
        print(f"  RODADA {seed}/10 — {'SEM FILTROS' if teste_sem_filtros else 'COM FILTROS'}")
        print(f"{'='*60}")
        
        df_u = obter_dataframe_universo()
        
        if teste_sem_filtros:
            df_c = construir_carteira(
                df_u, teste_sem_filtros=True, seed=seed, top_k=15
            )
        else:
            df_c = construir_carteira(
                df_u, teste_sem_filtros=False, seed=seed, top_k=15
            )
        
        res = rodar_backtest(carteira=df_c, teste_sem_filtros=teste_sem_filtros)
        
        if res:
            m = calcular_todas(res["retornos"], res["patrimonio"], 
                              res.get("retornos_ibov"))
            
            resultados_rodadas.append({
                "seed": seed,
                "tipo": "sem_filtros" if teste_sem_filtros else "com_filtros",
                **m
            })
    
    return pd.DataFrame(resultados_rodadas)

if __name__ == "__main__":
    print("\n🔬 EXPERIMENTO COMPLETO — 20 RODADAS (10+10)\n")
    
    df_com = rodar_10_rodadas(teste_sem_filtros=False)
    df_sem = rodar_10_rodadas(teste_sem_filtros=True)
    
    df_com.to_csv("data/resultados_com_filtros.csv", index=False)
    df_sem.to_csv("data/resultados_sem_filtros.csv", index=False)
    
    print("\n✅ Experimento concluído. Resultados salvos em /data/")