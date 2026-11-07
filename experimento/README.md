# Suite Experimental de Benchmarking e Analise Estatistica: HTMX vs. React

Este diretorio contem o pipeline automatizado de experimentos, medicao de desempenho em ambiente de producao conteinerizado, analise estatistica inferencial e geracao de tabelas e graficos em alta resolucao (300 DPI) para o Trabalho de Conclusao de Curso (TCC).

---

## 1. Reproducao Rapida dos Graficos e Tabelas

Para preservar a leveza e a velocidade das operacoes no Git, os arquivos de imagem das pastas `graficos_cold_start/`, `graficos_infinite_scroll/` e `graficos_mutacao_estado/` sao mantidos vazios no versionamento atraves de arquivos `.gitkeep`.

Todos os dados brutos oficiais estao preservados na pasta `resultados/`. Qualquer pessoa pode reproduzir e regerar todos os 65 graficos em 300 DPI e as 4 tabelas consolidadas em menos de 3 segundos executando:

### 1.1. Execucao via Docker Runner (Recomendado)

Estando dentro da pasta `experimento/`:

```bash
docker compose run --rm runner python run.py --skip-collect
```

### 1.2. Execucao via Shell Script ou PowerShell

**No Linux / Ubuntu:**
```bash
./executar_experimento.sh --analysis-only
```

**No Windows PowerShell:**
```powershell
.\executar_experimento.ps1 -AnalysisOnly
```

### 1.3. Padrao Visual e Metodologico dos Graficos

Todos os graficos sao renderizados em 300 DPI seguindo as diretrizes de visualizacao cientifica:
* **Estimador de Tendencia Central:** Mediana (P50) em todas as barras e curvas de evolucao longitudinal.
* **Barra de Erro e Faixa Sombreada:** Faixa Interquartil (IQR / P25 - P75), garantindo representatividade nao-parametrica imune a ruidos transientes de sistema operacional.
* **Paleta Academica:** React 19 em Azul Royal (`#3B82F6`) e HTMX 2 em Verde Esmeralda (`#10B981`) com alto contraste para leitura impressa e digital.

---

## 2. Eixos Experimentais Avaliados

A suite investiga tres dimensoes centrais do desempenho de aplicacoes web:

### 2.1. Experimento 1: Carregamento Inicial (Cold Start)
* **Objetivo:** Avaliar a penalidade do carregamento inicial (First Load Penalty) imposta pela transferencia e parsing do pacote JavaScript em relacao a entrega direta de HTML.
* **Rotas Testadas:** Home (`/`), Search (`/search?q=Python`) e Details (`/event/<id>`).
* **Perfis de Rede:** Sem Restricao (`NoThrottling`), 4G Rapido (`Fast4G`) e 4G Lento (`Slow4G`).
* **Metricas Coletadas:**
  * Core Web Vitals e Carregamento: TTFB, FCP, LCP, CLS, TBT, Tempo de DOM Load e Tempo de Carga Completa.
  * Consumo de Recursos: Payload Total transferido e decomposto por tipo (Documento, JavaScript, CSS, Midia, Outros), Tamanho do JS Heap apos Garbage Collection reforcado e Contagem de Elementos no DOM.

### 2.2. Experimento 2: Paginacao Continua Profunda (Infinite Scroll)
* **Objetivo:** Avaliar a complexidade assintotica e a degradacao progressiva de desempenho ao longo de 50 lotes consecutivos de rolagem (600 cartoes adicionados sequencialmente na tela).
* **Fundamentacao Teorica:** O HTMX opera com insercao direta de fragmentos HTML via `insertAdjacentHTML` (complexidade O(1)), enquanto o React realiza a reconciliacao do Virtual DOM sobre o array acumulado de componentes (complexidade O(N)).
* **Metricas Coletadas:**
  * Latencia de carga de cada lote individual (`BatchLoadTimeMs`).
  * Coeficiente de degradacao angular (inclinacao beta via regressao linear por Mínimos Quadrados Ordinarios).
  * Crescimento de memoria JavaScript Heap (`JSHeapMB`) e acumulacao de nos na arvore DOM (`DOMNodeCount`).

### 2.3. Experimento 3: Mutacao Atomica de Estado no Cliente
* **Objetivo:** Avaliar a latencia de interacao do usuario ao alternar 20 vezes consecutivas entre os estados de inscricao (POST) e cancelamento (DELETE) no cartao lateral de eventos.
* **Metricas Coletadas:**
  * Latencia ponta a ponta da mutacao (`MutationLatencyMs`), desde o disparo do evento de clique ate a estabilizacao visual do novo estado e contador.
  * Volume de dados trafegado na mutacao (`MutationPayloadKB`).
  * Estabilidade do DOM e retencao de memoria.

---

## 3. Arquitetura da Infraestrutura Experimental

Para garantir validade interna estrita, todas as coletas sao executadas sob uma malha de conteineres isolados:

```
                  +----------------------------------------------+
                  |            efp-runner (Playwright)           |
                  |     Chromium Headless + CDP Instrumentation  |
                  +----------------------+-----------------------+
                                         |
                     Rede Docker Bridge (eventflow-net)
                                         |
         +-------------------------------+-------------------------------+
         |                                                               |
+--------v-----------------------+                               +-------v-----------------------+
|  efp-htmx-front (Nginx:8080)   |                               | efp-react-front (Nginx:5173)  |
|  - Arquivos Estaticos e Midias |                               | - Bundle React (Vite dist/)   |
|  - Proxy Reverso Dinamico      |                               | - Proxy /api e /media         |
+--------+-----------------------+                               +-------+-----------------------+
         |                                                               |
         | proxy_pass :8000                                              | proxy_pass :8000
         |                                                               |
+--------v-----------------------+                               +-------v-----------------------+
|  efp-htmx-back (Gunicorn)      |                               |  efp-react-back (Gunicorn)    |
|  Django MVT (2w x 2t)          |                               |  Django REST API (2w x 2t)    |
|  Volume: db.sqlite3            |                               |  Volume: db.sqlite3           |
+--------------------------------+                               +-------------------------------+
```

* **Simetria dos Servicos:**
  * Pilha HTMX: `htmx-backend` (`efp-htmx-back`) e `htmx-frontend` (`efp-htmx-front`).
  * Pilha React: `react-backend` (`efp-react-back`) e `react-frontend` (`efp-react-front`).
* **Isolamento de Recursos:** Cada conteiner tem limite configurado de 2 vCPUs e 2048 MB de memoria RAM.
* **Sincronizacao Temporal:** Variavel `BENCHMARK_MODE=1` ativada em todos os backends para congelar o relogio no instante exato do seed (`seed_timestamp.json`), garantindo que consultas relativas ao tempo permaneçam identicas entre rodadas.

---

## 4. Instrucoes de Execucao do Benchmark

### 4.1. No Linux / Ubuntu Nativo (Ambiente Oficial do Estudo)

Recomenda-se a execucao em ambiente Linux nativo conectado a alimentacao externa e sem outras aplicacoes em execucao:

```bash
cd experimento

# Executar benchmark oficial com 30 rodadas por condicao
chmod +x executar_experimento.sh
./executar_experimento.sh -r 30

# Executar teste piloto com 5 rodadas apenas no Cold Start
./executar_experimento.sh -e cold-start -r 5

# Executar apenas o Infinite Scroll sob 4G Lento
./executar_experimento.sh -e infinite-scroll -p Slow4G -r 10
```

### 4.2. No Windows PowerShell

```powershell
cd experimento

# Execucao padrao com 30 rodadas
.\executar_experimento.ps1 -Runs 30

# Execucao de um experimento especifico
.\executar_experimento.ps1 -Experiment state-mutation -Runs 10
```

---

## 5. Estrutura dos Arquivos de Saida

* **`resultados/`**:
  * `dados_experimento_cold_start.csv`: Registros individuais de cada medicao de carregamento inicial.
  * `dados_experimento_infinite_scroll.csv`: Registros lote a lote da evolucao do scroll.
  * `dados_experimento_mutacao_estado.csv`: Registros de cada transicao atomica de inscricao.
  * `resultados_estatisticas_*.md`: Relatorios consolidados com medias, desvios padrao, medianas, IQRs, testes t de Welch e testes ANOVA de duas vias.
* **`tabelas/`**:
  * `tabela_1_cold_start.csv`: Tabela consolidada de carregamento inicial para a dissertacao.
  * `tabela_2_infinite_scroll.csv`: Tabela consolidada de degradacao do infinite scroll.
  * `tabela_3_mutacao_estado.csv`: Tabela consolidada de mutacao de estado.
  * `tabela_4_metricas_space.csv`: Tabela consolidada de metricas de engenharia do framework SPACE.
  * `tabela_anova_*.csv`: Tabelas de modelos fatoriais de ANOVA de duas vias por bateria.
  * `tabela_diagnostico_anova.csv`: Diagnostico de pressupostos (Levene, Shapiro-Wilk) e auditoria robusta HC3 (White-MacKinnon).
