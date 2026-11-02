import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats

res_nb = Path(r'D:\dev\tcc-htmx-react\experimento\resultados')
res_ufsc = Path(r'D:\dev\tcc-htmx-react\experimento\resultados_linux_vm_ufsc')

print("=" * 90)
print("COMPARAÇÃO DETALHADA: NOTEBOOK LINUX vs VM UFSC (1 vCPU)")
print("=" * 90)

# -------------------------------------------------------------
# 1. VERIFICAÇÃO DE AMOSTRAGEM E CONFIGURAÇÃO
# -------------------------------------------------------------
df_cs_nb = pd.read_csv(res_nb / 'dados_experimento_cold_start.csv')
df_cs_ufsc = pd.read_csv(res_ufsc / 'dados_experimento_cold_start.csv')

df_sc_nb = pd.read_csv(res_nb / 'dados_experimento_infinite_scroll.csv')
df_sc_ufsc = pd.read_csv(res_ufsc / 'dados_experimento_infinite_scroll.csv')

df_mut_nb = pd.read_csv(res_nb / 'dados_experimento_mutacao_estado.csv')
df_mut_ufsc = pd.read_csv(res_ufsc / 'dados_experimento_mutacao_estado.csv')

print("\n[1] METADADOS E VOLUME DE AMOSTRAS")
print(f"Cold Start:")
print(f"  Notebook: {len(df_cs_nb)} linhas | Rodadas únicas: {df_cs_nb['Rodada'].nunique()} (Min: {df_cs_nb['Rodada'].min()}, Max: {df_cs_nb['Rodada'].max()})")
print(f"  VM UFSC:  {len(df_cs_ufsc)} linhas | Rodadas únicas: {df_cs_ufsc['Rodada'].nunique()} (Min: {df_cs_ufsc['Rodada'].min()}, Max: {df_cs_ufsc['Rodada'].max()})")

print(f"\nInfinite Scroll:")
print(f"  Notebook: {len(df_sc_nb)} linhas | Rodadas únicas: {df_sc_nb['Rodada'].nunique()} (Max batch: {df_sc_nb['BatchIndex'].max()})")
print(f"  VM UFSC:  {len(df_sc_ufsc)} linhas | Rodadas únicas: {df_sc_ufsc['Rodada'].nunique()} (Max batch: {df_sc_ufsc['BatchIndex'].max()})")

print(f"\nState Mutation:")
print(f"  Notebook: {len(df_mut_nb)} linhas | Rodadas únicas: {df_mut_nb['Rodada'].nunique()} (Max mutation: {df_mut_nb['MutationIndex'].max()})")
print(f"  VM UFSC:  {len(df_mut_ufsc)} linhas | Rodadas únicas: {df_mut_ufsc['Rodada'].nunique()} (Max mutation: {df_mut_ufsc['MutationIndex'].max()})")

# -------------------------------------------------------------
# 2. COLD START COMPARATIVO
# -------------------------------------------------------------
print("\n" + "=" * 90)
print("[2] COLD START: IMPACTO DA VM (1 vCPU) POR PERFIL E PÁGINA")
print("=" * 90)

cs_metrics = ["TTFB", "FCP", "LCP", "TBT", "DOMLoad", "FullLoad"]

for profile in ["NoThrottling", "Fast4G", "Slow4G"]:
    print(f"\n=======================================================")
    print(f"  PERFIL DE REDE: {profile}")
    print(f"=======================================================")
    for page in ["Home", "Search", "Details"]:
        print(f"\n--- Página: {page} ---")
        for metric in cs_metrics:
            print(f"\n  Métrica: {metric}")
            for tech in ["HTMX", "React"]:
                s_nb = df_cs_nb[(df_cs_nb['PerfilRede'] == profile) & (df_cs_nb['Pagina'] == page) & (df_cs_nb['Tecnologia'] == tech)][metric].dropna()
                s_ufsc = df_cs_ufsc[(df_cs_ufsc['PerfilRede'] == profile) & (df_cs_ufsc['Pagina'] == page) & (df_cs_ufsc['Tecnologia'] == tech)][metric].dropna()
                
                med_nb, mean_nb, std_nb = s_nb.median(), s_nb.mean(), s_nb.std()
                p95_nb = np.percentile(s_nb, 95)
                cov_nb = (std_nb / mean_nb * 100) if mean_nb > 0 else 0
                
                med_u, mean_u, std_u = s_ufsc.median(), s_ufsc.mean(), s_ufsc.std()
                p95_u = np.percentile(s_ufsc, 95)
                cov_u = (std_u / mean_u * 100) if mean_u > 0 else 0
                
                delta_med = ((med_u - med_nb) / med_nb * 100) if med_nb > 0 else 0
                delta_mean = ((mean_u - mean_nb) / mean_nb * 100) if mean_nb > 0 else 0
                
                print(f"    {tech:<5} | NB (N={len(s_nb):3d}): med={med_nb:7.1f}ms, mean={mean_nb:7.1f}ms, sd={std_nb:6.1f}, p95={p95_nb:7.1f}ms, CoV={cov_nb:4.1f}%")
                print(f"          | UFSC(N={len(s_ufsc):3d}): med={med_u:7.1f}ms, mean={mean_u:7.1f}ms, sd={std_u:6.1f}, p95={p95_u:7.1f}ms, CoV={cov_u:4.1f}%")
                print(f"          | Impacto VM: Mediana {delta_med:+6.1f}% | Média {delta_mean:+6.1f}% | Razão Desv. Padrão: {std_u/max(0.001, std_nb):.2f}x")

# -------------------------------------------------------------
# 3. INFINITE SCROLL COMPARATIVO
# -------------------------------------------------------------
print("\n" + "=" * 90)
print("[3] INFINITE SCROLL: LATÊNCIA DE LOTE (BatchLatencyMs)")
print("=" * 90)
for profile in ["NoThrottling", "Fast4G", "Slow4G"]:
    print(f"\n--- Perfil: {profile} ---")
    for tech in ["HTMX", "React"]:
        s_nb = df_sc_nb[(df_sc_nb['PerfilRede'] == profile) & (df_sc_nb['Tecnologia'] == tech)]['BatchLatencyMs'].dropna()
        s_ufsc = df_sc_ufsc[(df_sc_ufsc['PerfilRede'] == profile) & (df_sc_ufsc['Tecnologia'] == tech)]['BatchLatencyMs'].dropna()
        
        med_nb, mean_nb, std_nb = s_nb.median(), s_nb.mean(), s_nb.std()
        p95_nb = np.percentile(s_nb, 95)
        cov_nb = (std_nb / mean_nb * 100) if mean_nb > 0 else 0
        
        med_u, mean_u, std_u = s_ufsc.median(), s_ufsc.mean(), s_ufsc.std()
        p95_u = np.percentile(s_ufsc, 95)
        cov_u = (std_u / mean_u * 100) if mean_u > 0 else 0
        
        delta_med = ((med_u - med_nb) / med_nb * 100) if med_nb > 0 else 0
        
        print(f"  {tech:<5} | NB (N={len(s_nb):5d}): med={med_nb:6.2f}ms, mean={mean_nb:6.2f}ms, sd={std_nb:6.2f}, p95={p95_nb:6.2f}ms, CoV={cov_nb:4.1f}%")
        print(f"        | UFSC(N={len(s_ufsc):5d}): med={med_u:6.2f}ms, mean={mean_u:6.2f}ms, sd={std_u:6.2f}, p95={p95_u:6.2f}ms, CoV={cov_u:4.1f}%")
        print(f"        | Impacto VM: Mediana {delta_med:+6.1f}% | Razão Desv. Padrão: {std_u/max(0.001, std_nb):.2f}x")

# -------------------------------------------------------------
# 4. STATE MUTATION COMPARATIVO
# -------------------------------------------------------------
print("\n" + "=" * 90)
print("[4] STATE MUTATION: LATÊNCIA DE MUTAÇÃO (MutationLatencyMs)")
print("=" * 90)
for profile in ["NoThrottling", "Fast4G", "Slow4G"]:
    print(f"\n--- Perfil: {profile} ---")
    for tech in ["HTMX", "React"]:
        s_nb = df_mut_nb[(df_mut_nb['PerfilRede'] == profile) & (df_mut_nb['Tecnologia'] == tech)]['MutationLatencyMs'].dropna()
        s_ufsc = df_mut_ufsc[(df_mut_ufsc['PerfilRede'] == profile) & (df_mut_ufsc['Tecnologia'] == tech)]['MutationLatencyMs'].dropna()
        
        med_nb, mean_nb, std_nb = s_nb.median(), s_nb.mean(), s_nb.std()
        p95_nb = np.percentile(s_nb, 95)
        cov_nb = (std_nb / mean_nb * 100) if mean_nb > 0 else 0
        
        med_u, mean_u, std_u = s_ufsc.median(), s_ufsc.mean(), s_ufsc.std()
        p95_u = np.percentile(s_ufsc, 95)
        cov_u = (std_u / mean_u * 100) if mean_u > 0 else 0
        
        delta_med = ((med_u - med_nb) / med_nb * 100) if med_nb > 0 else 0
        
        print(f"  {tech:<5} | NB (N={len(s_nb):5d}): med={med_nb:6.2f}ms, mean={mean_nb:6.2f}ms, sd={std_nb:6.2f}, p95={p95_nb:6.2f}ms, CoV={cov_nb:4.1f}%")
        print(f"        | UFSC(N={len(s_ufsc):5d}): med={med_u:6.2f}ms, mean={mean_u:6.2f}ms, sd={std_u:6.2f}, p95={p95_u:6.2f}ms, CoV={cov_u:4.1f}%")
        print(f"        | Impacto VM: Mediana {delta_med:+6.1f}% | Razão Desv. Padrão: {std_u/max(0.001, std_nb):.2f}x")

# -------------------------------------------------------------
# 5. TCP CWND COMPARATIVO
# -------------------------------------------------------------
print("\n" + "=" * 90)
print("[5] TCP CWND / BYTES IN FLIGHT")
print("=" * 90)
for tech in ["HTMX", "React"]:
    f_nb = res_nb / f'dados_tcp_cwnd_{tech}.csv'
    f_ufsc = res_ufsc / f'dados_tcp_cwnd_{tech}.csv'
    if f_nb.exists() and f_ufsc.exists():
        t_nb = pd.read_csv(f_nb)
        t_ufsc = pd.read_csv(f_ufsc)
        print(f"\n  Tecnologia: {tech}")
        print(f"    Notebook: {len(t_nb)} pacotes | Max BIF: {t_nb['TotalBytesInFlightKB'].max():.2f} KB | Total Payload: {t_nb['CumulativePayloadKB'].max():.2f} KB | Duração: {t_nb['TimestampMs'].max():.1f}ms")
        print(f"    VM UFSC:  {len(t_ufsc)} pacotes | Max BIF: {t_ufsc['TotalBytesInFlightKB'].max():.2f} KB | Total Payload: {t_ufsc['CumulativePayloadKB'].max():.2f} KB | Duração: {t_ufsc['TimestampMs'].max():.1f}ms")
