# Relatório Longitudinal e Inferencial do Infinite Scroll: React vs. HTMX

Este relatório apresenta a análise experimental do **comportamento longitudinal** e da **complexidade assintótica** entre **React 19 (SPA)** e **HTMX 2 (HDA)** na página de busca de eventos ao longo de até 50 lotes de scroll.

## 0. Taxa de Conclusão e Integridade Amostral por Perfil de Rede

Verifica a integridade das coletas e se ocorreram interrupções precoces por timeout sob condições severas de rede.

| Perfil de Rede | Tecnologia | Rodadas ($N$) | Lotes Médios Alcançados | Taxa de Conclusão Total (50 Lotes) |
| :--- | :--- | :--- | :--- | :--- |
| NoThrottling | React | 100 | 50.0 ± 0.0 lotes | 100.0% (100/100) |
| NoThrottling | HTMX | 100 | 50.0 ± 0.0 lotes | 100.0% (100/100) |
| Fast4G | React | 100 | 50.0 ± 0.0 lotes | 100.0% (100/100) |
| Fast4G | HTMX | 100 | 50.0 ± 0.0 lotes | 100.0% (100/100) |
| Slow4G | React | 100 | 50.0 ± 0.0 lotes | 100.0% (100/100) |
| Slow4G | HTMX | 100 | 50.0 ± 0.0 lotes | 100.0% (100/100) |

---

## 1. Estatísticas por Rodada Independente ($N = 100$ Rodadas)

Para evitar pseudo-repetição amostral (*pseudoreplication*), as métricas de latência foram consolidadas pela média de cada rodada, e as métricas acumulativas de memória e nós do DOM foram extraídas no **Lote Final Alcançado por Cada Rodada (sem viés de sobrevivência)**.

| Perfil de Rede | Métrica Avaliada | React (Média ± DP) | HTMX (Média ± DP) | Estatística $t$ | $p$-valor | Significativo ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| NoThrottling | Latência Média por Rodada | 76.73 ± 0.79 ms | 42.62 ± 1.05 ms | 259.0766 | < 0.0001 | Sim (p < 0.05) |
| NoThrottling | $\Delta$ JS Heap Final | 6.99 ± 0.01 MB | 0.92 ± 0.03 MB | 2118.6607 | < 0.0001 | Sim (p < 0.05) |
| NoThrottling | JS Heap Total Final | 9.52 ± 0.01 MB | 2.18 ± 0.03 MB | 2567.3899 | < 0.0001 | Sim (p < 0.05) |
| NoThrottling | Nós do DOM Final | 5751 ± 0.0 nós | 5754 ± 0.0 nós | ∞ | < 0.0001 | Sim (p < 0.05) |
| Fast4G | Latência Média por Rodada | 83.89 ± 0.57 ms | 59.76 ± 0.61 ms | 288.6376 | < 0.0001 | Sim (p < 0.05) |
| Fast4G | $\Delta$ JS Heap Final | 6.98 ± 0.01 MB | 0.97 ± 0.03 MB | 2185.5989 | < 0.0001 | Sim (p < 0.05) |
| Fast4G | JS Heap Total Final | 9.53 ± 0.01 MB | 2.23 ± 0.03 MB | 2653.0188 | < 0.0001 | Sim (p < 0.05) |
| Fast4G | Nós do DOM Final | 5751 ± 0.0 nós | 5754 ± 0.0 nós | ∞ | < 0.0001 | Sim (p < 0.05) |
| Slow4G | Latência Média por Rodada | 173.24 ± 0.63 ms | 123.02 ± 0.71 ms | 528.4882 | < 0.0001 | Sim (p < 0.05) |
| Slow4G | $\Delta$ JS Heap Final | 6.98 ± 0.01 MB | 0.96 ± 0.01 MB | 6085.7193 | < 0.0001 | Sim (p < 0.05) |
| Slow4G | JS Heap Total Final | 9.54 ± 0.01 MB | 2.22 ± 0.01 MB | 7391.7038 | < 0.0001 | Sim (p < 0.05) |
| Slow4G | Nós do DOM Final | 5751 ± 0.0 nós | 5754 ± 0.0 nós | ∞ | < 0.0001 | Sim (p < 0.05) |

---

## 2. Taxa de Degradação Linear e Complexidade Assintótica ($\beta$ em ms/lote)

Regressão linear calculada individualmente para cada uma das 100 rodadas: $\text{Latência}(k) = \alpha + \beta \cdot k$, onde $\beta$ representa o custo marginal de reconciliação/inserção por lote adicional.

| Perfil de Rede | Taxa React $\beta_{\text{React}}$ ($R^2$) | Taxa HTMX $\beta_{\text{HTMX}}$ ($R^2$) | Teste Welch ($t, p$) | Complexidade Observada |
| :--- | :--- | :--- | :--- | :--- |
| NoThrottling | 1.6491 ± 0.0556 ms/lote ($R^2=0.89$) | -0.0121 ± 0.0658 ms/lote ($R^2=0.02$) | $t=192.7525, p=< 0.0001$ | HTMX $O(1)$ vs React $O(N)$ |
| Fast4G | 1.0627 ± 0.0416 ms/lote ($R^2=0.90$) | -0.0066 ± 0.0394 ms/lote ($R^2=0.01$) | $t=186.7795, p=< 0.0001$ | HTMX $O(1)$ vs React $O(N)$ |
| Slow4G | 1.8040 ± 0.0524 ms/lote ($R^2=0.96$) | 0.0381 ± 0.0451 ms/lote ($R^2=0.03$) | $t=255.4354, p=< 0.0001$ | HTMX $O(1)$ vs React $O(N)$ |

---

## 3. Estatísticas Descritivas Globais (Todos os Lotes Agregados, $N = 15,000$ observações por tecnologia)

Valores médios calculados sobre a totalidade de requisições de scroll.

| Perfil de Rede | Métrica | React (Média ± DP) | HTMX (Média ± DP) |
| :--- | :--- | :--- | :--- |
| NoThrottling | BatchLoadTime | 76.73 ± 25.29 ms | 42.62 ± 8.58 ms |
| NoThrottling | BatchPayloadKB | 2.72 ± 0.12 KB | 1.71 ± 0.09 KB |
| NoThrottling | JSHeapMB | 6.40 ± 1.91 MB | 1.89 ± 0.20 MB |
| NoThrottling | DeltaJSHeapMB | 3.87 ± 1.91 MB | 0.63 ± 0.20 MB |
| NoThrottling | DOMNodeCount | 3077.40 ± 1597.17 | 3080.40 ± 1597.17 |
| Fast4G | BatchLoadTime | 83.89 ± 16.24 ms | 59.76 ± 5.22 ms |
| Fast4G | BatchPayloadKB | 2.72 ± 0.13 KB | 1.71 ± 0.08 KB |
| Fast4G | JSHeapMB | 6.40 ± 1.91 MB | 1.91 ± 0.22 MB |
| Fast4G | DeltaJSHeapMB | 3.85 ± 1.91 MB | 0.65 ± 0.22 MB |
| Fast4G | DOMNodeCount | 3077.40 ± 1597.17 | 3080.40 ± 1597.17 |
| Slow4G | BatchLoadTime | 173.24 ± 26.57 ms | 123.02 ± 5.07 ms |
| Slow4G | BatchPayloadKB | 2.72 ± 0.10 KB | 1.71 ± 0.06 KB |
| Slow4G | JSHeapMB | 6.41 ± 1.91 MB | 1.91 ± 0.22 MB |
| Slow4G | DeltaJSHeapMB | 3.85 ± 1.91 MB | 0.65 ± 0.22 MB |
| Slow4G | DOMNodeCount | 3077.40 ± 1597.17 | 3080.40 ± 1597.17 |

---

## 4. Análise de Variância de Duas Vias (Two-Way ANOVA por Rodada, $N=100$)

### ANOVA para: BatchLoadTime (Médias/Finais por Rodada, $N=100$)

| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 352703.7375 | < 0.0001 | Sim |
| Condição de Rede | 2 | 827120.9374 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 15577.5237 | < 0.0001 | Sim |


### ANOVA para: BatchPayloadKB (Médias/Finais por Rodada, $N=100$)

| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 2907347.2446 | < 0.0001 | Sim |
| Condição de Rede | 2 | 4.4244 | 0.0124 | Sim |
| Interação (Tecnologia * Rede) | 2 | 1.2230 | 0.2951 | Não |


### ANOVA para: JSHeapMB (Médias/Finais por Rodada, $N=100$)

| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 28813779.2497 | < 0.0001 | Sim |
| Condição de Rede | 2 | 196.5417 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 87.6569 | < 0.0001 | Sim |


### ANOVA para: DeltaJSHeapMB (Médias/Finais por Rodada, $N=100$)

| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 19557629.8357 | < 0.0001 | Sim |
| Condição de Rede | 2 | 66.2443 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 227.5437 | < 0.0001 | Sim |


### ANOVA para: DOMNodeCount (Médias/Finais por Rodada, $N=100$)

| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 43668361024508878678654976.0000 | < 0.0001 | Sim |
| Condição de Rede | 2 | 112.5923 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 57.8330 | < 0.0001 | Sim |

