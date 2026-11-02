# Relatório Estatístico de Mutação Rápida de Estado: React vs. HTMX

Este relatório apresenta a análise estatística detalhada da latência de resposta, consumo de memória e carga de rede durante mutações repetidas de estado ($N = 100$ rodadas independentes), com **análise global consolidada** e **desagregação entre Inscrição (POST) e Cancelamento (DELETE)**.

## 1. Estatísticas Descritivas Globais (Todos os Ciclos Agregados)

Valores representados como Média ± Desvio Padrão (DP).

### 1.1 Geral (Todas as 20 Mutações)

| Perfil de Rede | Métrica | React (Média ± DP) | HTMX (Média ± DP) | Variação |
| :--- | :--- | :--- | :--- | :--- |
| NoThrottling | MutationLatencyMs | 38.74 ± 8.00 ms | 42.68 ± 6.05 ms | +10.2% |
| NoThrottling | MutationPayloadKB | 0.11 ± 0.06 KB | 0.40 ± 0.16 KB | +270.7% |
| NoThrottling | JSHeapMB | 3.04 ± 0.12 MB | 1.72 ± 0.09 MB | -43.5% |
| NoThrottling | DOMNodeCount | 56.00 ± 1.00 | 58.00 ± 1.00 | +3.6% |
| Fast4G | MutationLatencyMs | 77.26 ± 9.76 ms | 62.10 ± 8.22 ms | -19.6% |
| Fast4G | MutationPayloadKB | 0.10 ± 0.06 KB | 0.30 ± 0.23 KB | +191.9% |
| Fast4G | JSHeapMB | 3.04 ± 0.12 MB | 1.71 ± 0.09 MB | -43.8% |
| Fast4G | DOMNodeCount | 56.00 ± 1.00 | 58.00 ± 1.00 | +3.6% |
| Slow4G | MutationLatencyMs | 135.01 ± 3.54 ms | 133.28 ± 6.52 ms | -1.3% |
| Slow4G | MutationPayloadKB | 0.11 ± 0.05 KB | 0.45 ± 0.07 KB | +312.8% |
| Slow4G | JSHeapMB | 3.04 ± 0.12 MB | 1.71 ± 0.09 MB | -43.8% |
| Slow4G | DOMNodeCount | 56.00 ± 1.00 | 58.00 ± 1.00 | +3.6% |


### 1.2 Inscrição em Evento (POST - Mutações Ímpares)

| Perfil de Rede | Métrica | React (Média ± DP) | HTMX (Média ± DP) | Variação |
| :--- | :--- | :--- | :--- | :--- |
| NoThrottling | MutationLatencyMs | 35.93 ± 9.65 ms | 41.58 ± 7.30 ms | +15.7% |
| NoThrottling | MutationPayloadKB | 0.16 ± 0.03 KB | 0.42 ± 0.20 KB | +165.8% |
| NoThrottling | JSHeapMB | 3.03 ± 0.12 MB | 1.71 ± 0.09 MB | -43.5% |
| NoThrottling | DOMNodeCount | 57.00 ± 0.00 | 59.00 ± 0.00 | +3.5% |
| Fast4G | MutationLatencyMs | 72.56 ± 8.27 ms | 62.28 ± 7.23 ms | -14.2% |
| Fast4G | MutationPayloadKB | 0.16 ± 0.01 KB | 0.40 ± 0.22 KB | +147.0% |
| Fast4G | JSHeapMB | 3.03 ± 0.12 MB | 1.70 ± 0.09 MB | -43.8% |
| Fast4G | DOMNodeCount | 57.00 ± 0.00 | 59.00 ± 0.00 | +3.5% |
| Slow4G | MutationLatencyMs | 136.76 ± 3.35 ms | 132.92 ± 6.65 ms | -2.8% |
| Slow4G | MutationPayloadKB | 0.16 ± 0.01 KB | 0.52 ± 0.02 KB | +217.2% |
| Slow4G | JSHeapMB | 3.03 ± 0.12 MB | 1.70 ± 0.09 MB | -43.8% |
| Slow4G | DOMNodeCount | 57.00 ± 0.00 | 59.00 ± 0.00 | +3.5% |


### 1.3 Cancelamento de Inscrição (DELETE - Mutações Pares)

| Perfil de Rede | Métrica | React (Média ± DP) | HTMX (Média ± DP) | Variação |
| :--- | :--- | :--- | :--- | :--- |
| NoThrottling | MutationLatencyMs | 41.55 ± 4.37 ms | 43.77 ± 4.19 ms | +5.4% |
| NoThrottling | MutationPayloadKB | 0.05 ± 0.01 KB | 0.37 ± 0.09 KB | +577.4% |
| NoThrottling | JSHeapMB | 3.04 ± 0.11 MB | 1.72 ± 0.09 MB | -43.5% |
| NoThrottling | DOMNodeCount | 55.00 ± 0.00 | 57.00 ± 0.00 | +3.6% |
| Fast4G | MutationLatencyMs | 81.96 ± 8.84 ms | 61.92 ± 9.11 ms | -24.5% |
| Fast4G | MutationPayloadKB | 0.04 ± 0.02 KB | 0.20 ± 0.20 KB | +359.5% |
| Fast4G | JSHeapMB | 3.05 ± 0.11 MB | 1.71 ± 0.09 MB | -43.8% |
| Fast4G | DOMNodeCount | 55.00 ± 0.00 | 57.00 ± 0.00 | +3.6% |
| Slow4G | MutationLatencyMs | 133.27 ± 2.79 ms | 133.63 ± 6.37 ms | +0.3% |
| Slow4G | MutationPayloadKB | 0.06 ± 0.00 KB | 0.39 ± 0.04 KB | +596.1% |
| Slow4G | JSHeapMB | 3.05 ± 0.11 MB | 1.71 ± 0.09 MB | -43.8% |
| Slow4G | DOMNodeCount | 55.00 ± 0.00 | 57.00 ± 0.00 | +3.6% |


---

## 2. Teste t de Welch por Rodada Independente ($N = 100$ Rodadas)

Para assegurar a validade inferencial e eliminar **pseudo-repetição amostral**, os testes comparam as médias consolidadas por rodada independente.

### 2.1 Geral (Todas as 20 Mutações)

| Perfil de Rede | Métrica | Estatística $t$ | $p$-valor | Significativo ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| NoThrottling | MutationLatencyMs | -10.6038 | < 0.0001 | Sim (p < 0.05) |
| NoThrottling | MutationPayloadKB | -48.1084 | < 0.0001 | Sim (p < 0.05) |
| NoThrottling | JSHeapMB | 3574.8258 | < 0.0001 | Sim (p < 0.05) |
| NoThrottling | DOMNodeCount | ∞ | < 0.0001 | Sim (p < 0.05) |
| Fast4G | MutationLatencyMs | 49.7949 | < 0.0001 | Sim (p < 0.05) |
| Fast4G | MutationPayloadKB | -43.1663 | < 0.0001 | Sim (p < 0.05) |
| Fast4G | JSHeapMB | 5025.4667 | < 0.0001 | Sim (p < 0.05) |
| Fast4G | DOMNodeCount | ∞ | < 0.0001 | Sim (p < 0.05) |
| Slow4G | MutationLatencyMs | 9.8661 | < 0.0001 | Sim (p < 0.05) |
| Slow4G | MutationPayloadKB | -407.4660 | < 0.0001 | Sim (p < 0.05) |
| Slow4G | JSHeapMB | 7325.4100 | < 0.0001 | Sim (p < 0.05) |
| Slow4G | DOMNodeCount | ∞ | < 0.0001 | Sim (p < 0.05) |


### 2.2 Inscrição em Evento (POST - Mutações Ímpares)

| Perfil de Rede | Métrica | Estatística $t$ | $p$-valor | Significativo ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| NoThrottling | MutationLatencyMs | -10.4669 | < 0.0001 | Sim (p < 0.05) |
| NoThrottling | MutationPayloadKB | -29.9071 | < 0.0001 | Sim (p < 0.05) |
| NoThrottling | JSHeapMB | 3073.7719 | < 0.0001 | Sim (p < 0.05) |
| NoThrottling | DOMNodeCount | ∞ | < 0.0001 | Sim (p < 0.05) |
| Fast4G | MutationLatencyMs | 28.7243 | < 0.0001 | Sim (p < 0.05) |
| Fast4G | MutationPayloadKB | -34.7485 | < 0.0001 | Sim (p < 0.05) |
| Fast4G | JSHeapMB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Fast4G | DOMNodeCount | ∞ | < 0.0001 | Sim (p < 0.05) |
| Slow4G | MutationLatencyMs | 16.6357 | < 0.0001 | Sim (p < 0.05) |
| Slow4G | MutationPayloadKB | -601.5104 | < 0.0001 | Sim (p < 0.05) |
| Slow4G | JSHeapMB | 6993.5200 | < 0.0001 | Sim (p < 0.05) |
| Slow4G | DOMNodeCount | ∞ | < 0.0001 | Sim (p < 0.05) |


### 2.3 Cancelamento de Inscrição (DELETE - Mutações Pares)

| Perfil de Rede | Métrica | Estatística $t$ | $p$-valor | Significativo ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| NoThrottling | MutationLatencyMs | -6.9580 | < 0.0001 | Sim (p < 0.05) |
| NoThrottling | MutationPayloadKB | -47.3385 | < 0.0001 | Sim (p < 0.05) |
| NoThrottling | JSHeapMB | 3574.8258 | < 0.0001 | Sim (p < 0.05) |
| NoThrottling | DOMNodeCount | ∞ | < 0.0001 | Sim (p < 0.05) |
| Fast4G | MutationLatencyMs | 48.5768 | < 0.0001 | Sim (p < 0.05) |
| Fast4G | MutationPayloadKB | -27.1042 | < 0.0001 | Sim (p < 0.05) |
| Fast4G | JSHeapMB | 5025.4667 | < 0.0001 | Sim (p < 0.05) |
| Fast4G | DOMNodeCount | ∞ | < 0.0001 | Sim (p < 0.05) |
| Slow4G | MutationLatencyMs | -1.4469 | 0.1504 | Não |
| Slow4G | MutationPayloadKB | -226.4400 | < 0.0001 | Sim (p < 0.05) |
| Slow4G | JSHeapMB | 7325.4100 | < 0.0001 | Sim (p < 0.05) |
| Slow4G | DOMNodeCount | ∞ | < 0.0001 | Sim (p < 0.05) |


---

## 3. Análise de Variância de Duas Vias (Two-Way ANOVA por Rodada, $N=100$)

### 3.1 ANOVA: Geral (Todas as 20 Mutações)

#### Métrica: MutationLatencyMs

| Fator Avaliado | df | $F$ | $p$-valor | Significativo ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 641.3064 | < 0.0001 | Sim |
| Condição de Rede | 2 | 104874.0107 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 1102.5053 | < 0.0001 | Sim |


#### Métrica: JSHeapMB

| Fator Avaliado | df | $F$ | $p$-valor | Significativo ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 66116346.1107 | < 0.0001 | Sim |
| Condição de Rede | 2 | 238.0533 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 216.9517 | < 0.0001 | Sim |


### 3.2 ANOVA: Inscrição em Evento (POST - Mutações Ímpares)

#### Métrica: MutationLatencyMs

| Fator Avaliado | df | $F$ | $p$-valor | Significativo ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 151.3488 | < 0.0001 | Sim |
| Condição de Rede | 2 | 61741.9081 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 407.4838 | < 0.0001 | Sim |


#### Métrica: JSHeapMB

| Fator Avaliado | df | $F$ | $p$-valor | Significativo ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 65546794.3057 | < 0.0001 | Sim |
| Condição de Rede | 2 | 166.8955 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 201.7106 | < 0.0001 | Sim |


### 3.3 ANOVA: Cancelamento de Inscrição (DELETE - Mutações Pares)

#### Métrica: MutationLatencyMs

| Fator Avaliado | df | $F$ | $p$-valor | Significativo ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 910.8036 | < 0.0001 | Sim |
| Condição de Rede | 2 | 77052.3576 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 1368.6218 | < 0.0001 | Sim |


#### Métrica: JSHeapMB

| Fator Avaliado | df | $F$ | $p$-valor | Significativo ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 66116346.1107 | < 0.0001 | Sim |
| Condição de Rede | 2 | 238.0533 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 216.9517 | < 0.0001 | Sim |

