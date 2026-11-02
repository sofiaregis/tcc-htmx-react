# Relatório de Resultados Estatísticos: React vs. HTMX

Este relatório resume a análise comparativa entre as tecnologias React (SPA) e HTMX (HDA) com base nas coletas realizadas.

## 1. Estatísticas Descritivas

| Página | Perfil de Rede | Métrica | React (Média ± DP) | HTMX (Média ± DP) |
| :--- | :--- | :--- | :--- | :--- |
| Home | NoThrottling | TTFB | 1.21 ± 0.08 ms | 18.03 ± 0.79 ms |
| Home | NoThrottling | FCP | 263.16 ± 13.54 ms | 286.54 ± 41.64 ms |
| Home | NoThrottling | LCP | 325.35 ± 13.47 ms | 286.54 ± 41.64 ms |
| Home | NoThrottling | CLS | 0.0020 ± 0.0000 | 0.0021 ± 0.0000 |
| Home | NoThrottling | TBT | 0.00 ± 0.00 ms | 0.00 ± 0.00 ms |
| Home | NoThrottling | PayloadKB | 1069.37 ± 0.01 KB | 975.57 ± 0.01 KB |
| Home | NoThrottling | PayloadJS_KB | 113.57 ± 0.00 KB | 19.46 ± 0.00 KB |
| Home | NoThrottling | PayloadCSS_KB | 4.68 ± 0.01 KB | 5.45 ± 0.01 KB |
| Home | NoThrottling | PayloadMediaKB | 899.02 ± 0.00 KB | 899.02 ± 0.00 KB |
| Home | NoThrottling | PayloadDocKB | 0.31 ± 0.00 KB | 3.98 ± 0.00 KB |
| Home | NoThrottling | JSHeapMB | 2.04 ± 0.00 MB | 0.71 ± 0.00 MB |
| Home | NoThrottling | DOMNodeCount | 289.00 ± 0.00 | 292.00 ± 0.00 |
| Home | Fast4G | TTFB | 1.26 ± 0.08 ms | 17.92 ± 0.46 ms |
| Home | Fast4G | FCP | 394.25 ± 30.88 ms | 422.04 ± 40.95 ms |
| Home | Fast4G | LCP | 801.08 ± 31.58 ms | 422.04 ± 40.95 ms |
| Home | Fast4G | CLS | 0.0021 ± 0.0000 | 0.0021 ± 0.0000 |
| Home | Fast4G | TBT | 0.00 ± 0.00 ms | 0.00 ± 0.00 ms |
| Home | Fast4G | PayloadKB | 1069.37 ± 0.01 KB | 975.57 ± 0.01 KB |
| Home | Fast4G | PayloadJS_KB | 113.57 ± 0.00 KB | 19.46 ± 0.00 KB |
| Home | Fast4G | PayloadCSS_KB | 4.68 ± 0.01 KB | 5.45 ± 0.01 KB |
| Home | Fast4G | PayloadMediaKB | 899.02 ± 0.00 KB | 899.02 ± 0.00 KB |
| Home | Fast4G | PayloadDocKB | 0.31 ± 0.00 KB | 3.98 ± 0.00 KB |
| Home | Fast4G | JSHeapMB | 2.04 ± 0.00 MB | 0.71 ± 0.00 MB |
| Home | Fast4G | DOMNodeCount | 289.00 ± 0.00 | 292.00 ± 0.00 |
| Home | Slow4G | TTFB | 1.23 ± 0.09 ms | 18.57 ± 1.64 ms |
| Home | Slow4G | FCP | 646.32 ± 10.13 ms | 556.13 ± 39.66 ms |
| Home | Slow4G | LCP | 1578.60 ± 11.93 ms | 700.55 ± 29.01 ms |
| Home | Slow4G | CLS | 0.0021 ± 0.0000 | 0.0021 ± 0.0000 |
| Home | Slow4G | TBT | 0.00 ± 0.00 ms | 0.00 ± 0.00 ms |
| Home | Slow4G | PayloadKB | 1069.37 ± 0.02 KB | 975.57 ± 0.02 KB |
| Home | Slow4G | PayloadJS_KB | 113.57 ± 0.00 KB | 19.46 ± 0.00 KB |
| Home | Slow4G | PayloadCSS_KB | 4.68 ± 0.02 KB | 5.45 ± 0.01 KB |
| Home | Slow4G | PayloadMediaKB | 899.02 ± 0.00 KB | 899.02 ± 0.00 KB |
| Home | Slow4G | PayloadDocKB | 0.31 ± 0.00 KB | 3.98 ± 0.00 KB |
| Home | Slow4G | JSHeapMB | 2.05 ± 0.00 MB | 0.71 ± 0.00 MB |
| Home | Slow4G | DOMNodeCount | 289.00 ± 0.00 | 292.00 ± 0.00 |
| Search | NoThrottling | TTFB | 1.24 ± 0.09 ms | 8.41 ± 0.32 ms |
| Search | NoThrottling | FCP | 263.63 ± 12.20 ms | 280.78 ± 71.04 ms |
| Search | NoThrottling | LCP | 307.02 ± 13.72 ms | 280.78 ± 71.04 ms |
| Search | NoThrottling | CLS | 0.0016 ± 0.0000 | 0.0016 ± 0.0000 |
| Search | NoThrottling | TBT | 0.00 ± 0.00 ms | 0.00 ± 0.00 ms |
| Search | NoThrottling | PayloadKB | 194.26 ± 0.00 KB | 101.31 ± 0.02 KB |
| Search | NoThrottling | PayloadJS_KB | 113.57 ± 0.00 KB | 19.46 ± 0.00 KB |
| Search | NoThrottling | PayloadCSS_KB | 4.68 ± 0.00 KB | 5.45 ± 0.02 KB |
| Search | NoThrottling | PayloadMediaKB | 26.81 ± 0.00 KB | 26.81 ± 0.00 KB |
| Search | NoThrottling | PayloadDocKB | 0.31 ± 0.00 KB | 1.93 ± 0.00 KB |
| Search | NoThrottling | JSHeapMB | 1.91 ± 0.00 MB | 0.69 ± 0.00 MB |
| Search | NoThrottling | DOMNodeCount | 89.00 ± 0.00 | 90.00 ± 0.00 |
| Search | Fast4G | TTFB | 1.23 ± 0.09 ms | 8.47 ± 0.44 ms |
| Search | Fast4G | FCP | 390.91 ± 13.42 ms | 411.91 ± 43.28 ms |
| Search | Fast4G | LCP | 509.04 ± 14.33 ms | 411.91 ± 43.28 ms |
| Search | Fast4G | CLS | 0.0016 ± 0.0000 | 0.0016 ± 0.0000 |
| Search | Fast4G | TBT | 0.00 ± 0.00 ms | 0.00 ± 0.00 ms |
| Search | Fast4G | PayloadKB | 194.26 ± 0.00 KB | 101.31 ± 0.02 KB |
| Search | Fast4G | PayloadJS_KB | 113.57 ± 0.00 KB | 19.46 ± 0.00 KB |
| Search | Fast4G | PayloadCSS_KB | 4.68 ± 0.00 KB | 5.45 ± 0.02 KB |
| Search | Fast4G | PayloadMediaKB | 26.81 ± 0.00 KB | 26.81 ± 0.00 KB |
| Search | Fast4G | PayloadDocKB | 0.31 ± 0.00 KB | 1.93 ± 0.00 KB |
| Search | Fast4G | JSHeapMB | 1.91 ± 0.00 MB | 0.69 ± 0.00 MB |
| Search | Fast4G | DOMNodeCount | 89.00 ± 0.00 | 90.00 ± 0.00 |
| Search | Slow4G | TTFB | 1.20 ± 0.09 ms | 8.73 ± 0.44 ms |
| Search | Slow4G | FCP | 644.38 ± 8.25 ms | 543.96 ± 50.82 ms |
| Search | Slow4G | LCP | 988.48 ± 10.45 ms | 543.96 ± 50.82 ms |
| Search | Slow4G | CLS | 0.0016 ± 0.0000 | 0.0016 ± 0.0000 |
| Search | Slow4G | TBT | 0.00 ± 0.00 ms | 0.00 ± 0.00 ms |
| Search | Slow4G | PayloadKB | 194.27 ± 0.02 KB | 101.31 ± 0.01 KB |
| Search | Slow4G | PayloadJS_KB | 113.57 ± 0.00 KB | 19.46 ± 0.00 KB |
| Search | Slow4G | PayloadCSS_KB | 4.68 ± 0.01 KB | 5.45 ± 0.01 KB |
| Search | Slow4G | PayloadMediaKB | 26.81 ± 0.00 KB | 26.81 ± 0.00 KB |
| Search | Slow4G | PayloadDocKB | 0.31 ± 0.00 KB | 1.93 ± 0.00 KB |
| Search | Slow4G | JSHeapMB | 1.91 ± 0.00 MB | 0.69 ± 0.00 MB |
| Search | Slow4G | DOMNodeCount | 89.00 ± 0.00 | 90.00 ± 0.00 |
| Details | NoThrottling | TTFB | 1.19 ± 0.08 ms | 4.97 ± 0.24 ms |
| Details | NoThrottling | FCP | 259.02 ± 14.29 ms | 267.93 ± 32.09 ms |
| Details | NoThrottling | LCP | 294.92 ± 14.35 ms | 267.93 ± 32.09 ms |
| Details | NoThrottling | CLS | 0.0844 ± 0.0423 | 0.0003 ± 0.0000 |
| Details | NoThrottling | TBT | 0.00 ± 0.00 ms | 0.00 ± 0.00 ms |
| Details | NoThrottling | PayloadKB | 256.05 ± 0.01 KB | 163.73 ± 0.01 KB |
| Details | NoThrottling | PayloadJS_KB | 113.57 ± 0.00 KB | 19.46 ± 0.00 KB |
| Details | NoThrottling | PayloadCSS_KB | 4.68 ± 0.01 KB | 5.45 ± 0.01 KB |
| Details | NoThrottling | PayloadMediaKB | 89.40 ± 0.00 KB | 89.40 ± 0.00 KB |
| Details | NoThrottling | PayloadDocKB | 0.31 ± 0.00 KB | 1.75 ± 0.00 KB |
| Details | NoThrottling | JSHeapMB | 1.79 ± 0.00 MB | 0.66 ± 0.00 MB |
| Details | NoThrottling | DOMNodeCount | 51.00 ± 0.00 | 54.00 ± 0.00 |
| Details | Fast4G | TTFB | 1.28 ± 0.10 ms | 4.96 ± 0.24 ms |
| Details | Fast4G | FCP | 383.84 ± 12.16 ms | 412.20 ± 33.10 ms |
| Details | Fast4G | LCP | 596.46 ± 15.88 ms | 412.20 ± 33.10 ms |
| Details | Fast4G | CLS | 0.1055 ± 0.0000 | 0.0003 ± 0.0000 |
| Details | Fast4G | TBT | 0.00 ± 0.00 ms | 0.00 ± 0.00 ms |
| Details | Fast4G | PayloadKB | 256.05 ± 0.00 KB | 163.73 ± 0.01 KB |
| Details | Fast4G | PayloadJS_KB | 113.57 ± 0.00 KB | 19.46 ± 0.00 KB |
| Details | Fast4G | PayloadCSS_KB | 4.68 ± 0.00 KB | 5.45 ± 0.01 KB |
| Details | Fast4G | PayloadMediaKB | 89.40 ± 0.00 KB | 89.40 ± 0.00 KB |
| Details | Fast4G | PayloadDocKB | 0.31 ± 0.00 KB | 1.75 ± 0.00 KB |
| Details | Fast4G | JSHeapMB | 1.79 ± 0.00 MB | 0.66 ± 0.00 MB |
| Details | Fast4G | DOMNodeCount | 51.00 ± 0.00 | 54.00 ± 0.00 |
| Details | Slow4G | TTFB | 1.24 ± 0.09 ms | 5.08 ± 0.23 ms |
| Details | Slow4G | FCP | 635.84 ± 7.57 ms | 534.02 ± 50.71 ms |
| Details | Slow4G | LCP | 1105.65 ± 9.12 ms | 534.02 ± 50.71 ms |
| Details | Slow4G | CLS | 0.1055 ± 0.0000 | 0.0003 ± 0.0000 |
| Details | Slow4G | TBT | 0.00 ± 0.00 ms | 0.00 ± 0.00 ms |
| Details | Slow4G | PayloadKB | 256.05 ± 0.01 KB | 163.73 ± 0.01 KB |
| Details | Slow4G | PayloadJS_KB | 113.57 ± 0.00 KB | 19.46 ± 0.00 KB |
| Details | Slow4G | PayloadCSS_KB | 4.68 ± 0.01 KB | 5.45 ± 0.01 KB |
| Details | Slow4G | PayloadMediaKB | 89.40 ± 0.00 KB | 89.40 ± 0.00 KB |
| Details | Slow4G | PayloadDocKB | 0.31 ± 0.00 KB | 1.75 ± 0.00 KB |
| Details | Slow4G | JSHeapMB | 1.79 ± 0.00 MB | 0.66 ± 0.00 MB |
| Details | Slow4G | DOMNodeCount | 51.00 ± 0.00 | 54.00 ± 0.00 |

---

## 2. Teste t de Welch (Comparação Direta de Médias)

| Página | Perfil de Rede | Métrica | Estatística $t$ | $p$-valor | Significativo ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Home | NoThrottling | TTFB | -211.6489 | < 0.0001 | Sim (p < 0.05) |
| Home | NoThrottling | FCP | -5.3403 | < 0.0001 | Sim (p < 0.05) |
| Home | NoThrottling | LCP | 8.8680 | < 0.0001 | Sim (p < 0.05) |
| Home | NoThrottling | CLS | -69.6491 | < 0.0001 | Sim (p < 0.05) |
| Home | NoThrottling | TBT | 0.0000 | 1.0000 | Não |
| Home | NoThrottling | PayloadKB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Home | NoThrottling | PayloadJS_KB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Home | NoThrottling | PayloadCSS_KB | -512.0243 | < 0.0001 | Sim (p < 0.05) |
| Home | NoThrottling | PayloadMediaKB | 0.0000 | 1.0000 | Não |
| Home | NoThrottling | PayloadDocKB | -∞ | < 0.0001 | Sim (p < 0.05) |
| Home | NoThrottling | JSHeapMB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Home | NoThrottling | DOMNodeCount | ∞ | < 0.0001 | Sim (p < 0.05) |
| Home | Fast4G | TTFB | -355.7409 | < 0.0001 | Sim (p < 0.05) |
| Home | Fast4G | FCP | -5.4190 | < 0.0001 | Sim (p < 0.05) |
| Home | Fast4G | LCP | 73.2957 | < 0.0001 | Sim (p < 0.05) |
| Home | Fast4G | CLS | 0.0000 | 1.0000 | Não |
| Home | Fast4G | TBT | 0.0000 | 1.0000 | Não |
| Home | Fast4G | PayloadKB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Home | Fast4G | PayloadJS_KB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Home | Fast4G | PayloadCSS_KB | -502.5686 | < 0.0001 | Sim (p < 0.05) |
| Home | Fast4G | PayloadMediaKB | 0.0000 | 1.0000 | Não |
| Home | Fast4G | PayloadDocKB | -∞ | < 0.0001 | Sim (p < 0.05) |
| Home | Fast4G | JSHeapMB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Home | Fast4G | DOMNodeCount | ∞ | < 0.0001 | Sim (p < 0.05) |
| Home | Slow4G | TTFB | -105.5917 | < 0.0001 | Sim (p < 0.05) |
| Home | Slow4G | FCP | 22.0313 | < 0.0001 | Sim (p < 0.05) |
| Home | Slow4G | LCP | 279.9428 | < 0.0001 | Sim (p < 0.05) |
| Home | Slow4G | CLS | 0.0000 | 1.0000 | Não |
| Home | Slow4G | TBT | 0.0000 | 1.0000 | Não |
| Home | Slow4G | PayloadKB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Home | Slow4G | PayloadJS_KB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Home | Slow4G | PayloadCSS_KB | -360.4153 | < 0.0001 | Sim (p < 0.05) |
| Home | Slow4G | PayloadMediaKB | 0.0000 | 1.0000 | Não |
| Home | Slow4G | PayloadDocKB | -∞ | < 0.0001 | Sim (p < 0.05) |
| Home | Slow4G | JSHeapMB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Home | Slow4G | DOMNodeCount | ∞ | < 0.0001 | Sim (p < 0.05) |
| Search | NoThrottling | TTFB | -216.9009 | < 0.0001 | Sim (p < 0.05) |
| Search | NoThrottling | FCP | -2.3793 | 0.0192 | Sim (p < 0.05) |
| Search | NoThrottling | LCP | 3.6263 | 0.0004 | Sim (p < 0.05) |
| Search | NoThrottling | CLS | 0.0000 | 1.0000 | Não |
| Search | NoThrottling | TBT | 0.0000 | 1.0000 | Não |
| Search | NoThrottling | PayloadKB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Search | NoThrottling | PayloadJS_KB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Search | NoThrottling | PayloadCSS_KB | -506.7296 | < 0.0001 | Sim (p < 0.05) |
| Search | NoThrottling | PayloadMediaKB | 0.0000 | 1.0000 | Não |
| Search | NoThrottling | PayloadDocKB | -∞ | < 0.0001 | Sim (p < 0.05) |
| Search | NoThrottling | JSHeapMB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Search | NoThrottling | DOMNodeCount | ∞ | < 0.0001 | Sim (p < 0.05) |
| Search | Fast4G | TTFB | -162.8824 | < 0.0001 | Sim (p < 0.05) |
| Search | Fast4G | FCP | -4.6348 | < 0.0001 | Sim (p < 0.05) |
| Search | Fast4G | LCP | 21.3021 | < 0.0001 | Sim (p < 0.05) |
| Search | Fast4G | CLS | 0.0000 | 1.0000 | Não |
| Search | Fast4G | TBT | 0.0000 | 1.0000 | Não |
| Search | Fast4G | PayloadKB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Search | Fast4G | PayloadJS_KB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Search | Fast4G | PayloadCSS_KB | -507.0851 | < 0.0001 | Sim (p < 0.05) |
| Search | Fast4G | PayloadMediaKB | 0.0000 | 1.0000 | Não |
| Search | Fast4G | PayloadDocKB | -∞ | < 0.0001 | Sim (p < 0.05) |
| Search | Fast4G | JSHeapMB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Search | Fast4G | DOMNodeCount | ∞ | < 0.0001 | Sim (p < 0.05) |
| Search | Slow4G | TTFB | -167.5627 | < 0.0001 | Sim (p < 0.05) |
| Search | Slow4G | FCP | 19.5059 | < 0.0001 | Sim (p < 0.05) |
| Search | Slow4G | LCP | 85.6757 | < 0.0001 | Sim (p < 0.05) |
| Search | Slow4G | CLS | 0.0000 | 1.0000 | Não |
| Search | Slow4G | TBT | 0.0000 | 1.0000 | Não |
| Search | Slow4G | PayloadKB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Search | Slow4G | PayloadJS_KB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Search | Slow4G | PayloadCSS_KB | -418.7518 | < 0.0001 | Sim (p < 0.05) |
| Search | Slow4G | PayloadMediaKB | 0.0000 | 1.0000 | Não |
| Search | Slow4G | PayloadDocKB | -8804.0377 | < 0.0001 | Sim (p < 0.05) |
| Search | Slow4G | JSHeapMB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Search | Slow4G | DOMNodeCount | ∞ | < 0.0001 | Sim (p < 0.05) |
| Details | NoThrottling | TTFB | -149.2119 | < 0.0001 | Sim (p < 0.05) |
| Details | NoThrottling | FCP | -2.5381 | 0.0123 | Sim (p < 0.05) |
| Details | NoThrottling | LCP | 7.6775 | < 0.0001 | Sim (p < 0.05) |
| Details | NoThrottling | CLS | 19.8997 | < 0.0001 | Sim (p < 0.05) |
| Details | NoThrottling | TBT | 0.0000 | 1.0000 | Não |
| Details | NoThrottling | PayloadKB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Details | NoThrottling | PayloadJS_KB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Details | NoThrottling | PayloadCSS_KB | -511.9409 | < 0.0001 | Sim (p < 0.05) |
| Details | NoThrottling | PayloadMediaKB | 0.0000 | 1.0000 | Não |
| Details | NoThrottling | PayloadDocKB | -6709.5588 | < 0.0001 | Sim (p < 0.05) |
| Details | NoThrottling | JSHeapMB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Details | NoThrottling | DOMNodeCount | ∞ | < 0.0001 | Sim (p < 0.05) |
| Details | Fast4G | TTFB | -141.3828 | < 0.0001 | Sim (p < 0.05) |
| Details | Fast4G | FCP | -8.0434 | < 0.0001 | Sim (p < 0.05) |
| Details | Fast4G | LCP | 50.1979 | < 0.0001 | Sim (p < 0.05) |
| Details | Fast4G | CLS | ∞ | < 0.0001 | Sim (p < 0.05) |
| Details | Fast4G | TBT | 0.0000 | 1.0000 | Não |
| Details | Fast4G | PayloadKB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Details | Fast4G | PayloadJS_KB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Details | Fast4G | PayloadCSS_KB | -724.9926 | < 0.0001 | Sim (p < 0.05) |
| Details | Fast4G | PayloadMediaKB | 0.0000 | 1.0000 | Não |
| Details | Fast4G | PayloadDocKB | -7749.8650 | < 0.0001 | Sim (p < 0.05) |
| Details | Fast4G | JSHeapMB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Details | Fast4G | DOMNodeCount | ∞ | < 0.0001 | Sim (p < 0.05) |
| Details | Slow4G | TTFB | -157.3680 | < 0.0001 | Sim (p < 0.05) |
| Details | Slow4G | FCP | 19.8583 | < 0.0001 | Sim (p < 0.05) |
| Details | Slow4G | LCP | 110.9508 | < 0.0001 | Sim (p < 0.05) |
| Details | Slow4G | CLS | ∞ | < 0.0001 | Sim (p < 0.05) |
| Details | Slow4G | TBT | 0.0000 | 1.0000 | Não |
| Details | Slow4G | PayloadKB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Details | Slow4G | PayloadJS_KB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Details | Slow4G | PayloadCSS_KB | -502.6022 | < 0.0001 | Sim (p < 0.05) |
| Details | Slow4G | PayloadMediaKB | 0.0000 | 1.0000 | Não |
| Details | Slow4G | PayloadDocKB | -6849.5280 | < 0.0001 | Sim (p < 0.05) |
| Details | Slow4G | JSHeapMB | ∞ | < 0.0001 | Sim (p < 0.05) |
| Details | Slow4G | DOMNodeCount | ∞ | < 0.0001 | Sim (p < 0.05) |

---

## 3. Análise de Variância de Duas Vias (Two-Way ANOVA)

A ANOVA avalia o impacto de **Tecnologia** (React vs. HTMX), de **Rede** (NoThrottling, Fast4G, Slow4G) e do **Efeito de Interação** entre os dois fatores.

### ANOVA para a Métrica: TTFB

#### Página: Home
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 72806.3331 | < 0.0001 | Sim |
| Condição de Rede | 2 | 10.0357 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 10.6342 | < 0.0001 | Sim |


#### Página: Search
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 94594.4374 | < 0.0001 | Sim |
| Condição de Rede | 2 | 12.9198 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 20.9579 | < 0.0001 | Sim |


#### Página: Details
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 66688.7377 | < 0.0001 | Sim |
| Condição de Rede | 2 | 10.7419 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 10.2658 | < 0.0001 | Sim |


### ANOVA para a Métrica: FCP

#### Página: Home
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 24.4507 | < 0.0001 | Sim |
| Condição de Rede | 2 | 5192.4124 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 215.6067 | < 0.0001 | Sim |


#### Página: Search
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 39.1727 | < 0.0001 | Sim |
| Condição de Rede | 2 | 3182.1007 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 144.3674 | < 0.0001 | Sim |


#### Página: Details
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 81.5695 | < 0.0001 | Sim |
| Condição de Rede | 2 | 6125.2398 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 289.7084 | < 0.0001 | Sim |


### ANOVA para a Métrica: LCP

#### Página: Home
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 30131.0013 | < 0.0001 | Sim |
| Condição de Rede | 2 | 38292.4719 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 9590.8660 | < 0.0001 | Sim |


#### Página: Search
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 3223.1077 | < 0.0001 | Sim |
| Condição de Rede | 2 | 6882.3541 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 1502.5043 | < 0.0001 | Sim |


#### Página: Details
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 11701.7684 | < 0.0001 | Sim |
| Condição de Rede | 2 | 16767.4796 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 4500.2132 | < 0.0001 | Sim |


### ANOVA para a Métrica: CLS

#### Página: Home
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 4851.0000 | < 0.0001 | Sim |
| Condição de Rede | 2 | 4851.0000 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 4851.0000 | < 0.0001 | Sim |


#### Página: Search
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 203.4606 | < 0.0001 | Sim |
| Condição de Rede | 2 | 20.8032 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 18.4175 | < 0.0001 | Sim |


#### Página: Details
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 4851.0000 | < 0.0001 | Sim |
| Condição de Rede | 2 | 24.7500 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 24.7500 | < 0.0001 | Sim |


### ANOVA para a Métrica: TBT

#### Página: Home
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |


#### Página: Search
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |


#### Página: Details
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |


### ANOVA para a Métrica: PayloadKB

#### Página: Home
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 8521325665.5169 | < 0.0001 | Sim |
| Condição de Rede | 2 | 0.4282 | 0.6519 | Não |
| Interação (Tecnologia * Rede) | 2 | 0.0125 | 0.9876 | Não |


#### Página: Search
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 9566940584.1262 | < 0.0001 | Sim |
| Condição de Rede | 2 | 0.0975 | 0.9071 | Não |
| Interação (Tecnologia * Rede) | 2 | 1.4207 | 0.2424 | Não |


#### Página: Details
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 12993547531.7848 | < 0.0001 | Sim |
| Condição de Rede | 2 | 0.2212 | 0.8016 | Não |
| Interação (Tecnologia * Rede) | 2 | 0.2742 | 0.7603 | Não |


### ANOVA para a Métrica: PayloadJS_KB

#### Página: Home
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 9108192129482437772628113489920.0000 | < 0.0001 | Sim |
| Condição de Rede | 2 | 100.6761 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 1.4940 | 0.2253 | Não |


#### Página: Search
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 9108192129482437772628113489920.0000 | < 0.0001 | Sim |
| Condição de Rede | 2 | 100.6761 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 1.4940 | 0.2253 | Não |


#### Página: Details
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 9108192129482437772628113489920.0000 | < 0.0001 | Sim |
| Condição de Rede | 2 | 100.6761 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 1.4940 | 0.2253 | Não |


### ANOVA para a Métrica: PayloadCSS_KB

#### Página: Home
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 581720.0216 | < 0.0001 | Sim |
| Condição de Rede | 2 | 0.4800 | 0.6190 | Não |
| Interação (Tecnologia * Rede) | 2 | 0.0013 | 0.9987 | Não |


#### Página: Search
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 667858.0744 | < 0.0001 | Sim |
| Condição de Rede | 2 | 0.1101 | 0.8958 | Não |
| Interação (Tecnologia * Rede) | 2 | 1.3745 | 0.2538 | Não |


#### Página: Details
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 930402.0444 | < 0.0001 | Sim |
| Condição de Rede | 2 | 0.2063 | 0.8137 | Não |
| Interação (Tecnologia * Rede) | 2 | 0.1882 | 0.8285 | Não |


### ANOVA para a Métrica: PayloadMediaKB

#### Página: Home
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 265.6168 | < 0.0001 | Sim |
| Condição de Rede | 2 | 16.1743 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 25.8432 | < 0.0001 | Sim |


#### Página: Search
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 206.9181 | < 0.0001 | Sim |
| Condição de Rede | 2 | 3.6427 | 0.0268 | Sim |
| Interação (Tecnologia * Rede) | 2 | 6.5616 | 0.0015 | Sim |


#### Página: Details
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 124.2251 | < 0.0001 | Sim |
| Condição de Rede | 2 | 117.6428 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 52.0324 | < 0.0001 | Sim |


### ANOVA para a Métrica: PayloadDocKB

#### Página: Home
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 1217331249.6733 | < 0.0001 | Sim |
| Condição de Rede | 2 | 0.7514 | 0.4722 | Não |
| Interação (Tecnologia * Rede) | 2 | 0.7514 | 0.4722 | Não |


#### Página: Search
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 303014379.9029 | < 0.0001 | Sim |
| Condição de Rede | 2 | 0.0587 | 0.9430 | Não |
| Interação (Tecnologia * Rede) | 2 | 0.0587 | 0.9430 | Não |


#### Página: Details
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 149556499.6674 | < 0.0001 | Sim |
| Condição de Rede | 2 | 0.1239 | 0.8835 | Não |
| Interação (Tecnologia * Rede) | 2 | 0.1239 | 0.8835 | Não |


### ANOVA para a Métrica: JSHeapMB

#### Página: Home
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 1469590273.7604 | < 0.0001 | Sim |
| Condição de Rede | 2 | 231.1236 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 232.3129 | < 0.0001 | Sim |


#### Página: Search
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 2615820763.5446 | < 0.0001 | Sim |
| Condição de Rede | 2 | 97.4670 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 88.8568 | < 0.0001 | Sim |


#### Página: Details
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 7052966885.0617 | < 0.0001 | Sim |
| Condição de Rede | 2 | 94.3496 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 89.0398 | < 0.0001 | Sim |


### ANOVA para a Métrica: DOMNodeCount

#### Página: Home
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 1155381887222863779818635264.0000 | < 0.0001 | Sim |
| Condição de Rede | 2 | 19.3847 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 9.3399 | 0.0001 | Sim |


#### Página: Search
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 2014620228315075292407267328.0000 | < 0.0001 | Sim |
| Condição de Rede | 2 | 10.8508 | < 0.0001 | Sim |
| Interação (Tecnologia * Rede) | 2 | 3.2552 | 0.0393 | Sim |


#### Página: Details
| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\alpha=0.05$) |
| :--- | :--- | :--- | :--- | :--- |
| Tecnologia | 1 | 14514544348024832321636007936.0000 | < 0.0001 | Sim |
| Condição de Rede | 2 | 4.6752 | 0.0097 | Sim |
| Interação (Tecnologia * Rede) | 2 | 9.2181 | 0.0001 | Sim |

