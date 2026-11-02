# EventFlow: Estudo Comparativo Experimental entre HTMX (HDA) e React (SPA)

Este repositorio contem o ecossistema de codigo e a suite experimental do Trabalho de Conclusao de Curso (TCC) intitulado **"Comparacao Experimental de Desempenho e Produtividade entre Arquiteturas Baseadas em Hipermidia (HTMX) e Aplicacoes de Pagina Unica (React)"**.

O projeto avalia empiricamente os compromissos de engenharia (trade-offs) entre dois paradigmas arquiteturais para a Web:
1. **Hypermedia-Driven Application (HDA):** Renderizacao no servidor orientada a hipermidia com **HTMX 2** e **Django 5**.
2. **Single-Page Application (SPA):** Renderizacao no cliente com **React 19**, **Vite 6** e **Django REST Framework**.

---

## 1. Estrutura do Repositorio

O projeto organiza-se em tres diretorios principais:

```
tcc-htmx-react/
├── .gitignore                         # Regras globais de exclusao do Git
├── README.md                          # Visao geral do ecossistema e instrucoes de execucao
│
├── eventflow-htmx/                    # Implementacao HDA (Django + Templates + HTMX 2)
│   ├── backend/                       # Configuracao do projeto Django
│   ├── events/                        # Modulo principal (views SSR, models e comandos)
│   ├── media/                         # Catalogo de imagens normalizadas para seed offline
│   ├── static/                        # CSS global, scripts JS nativos e htmx.min.js local
│   ├── templates/                     # Templates base e componentes parciais (templates/c/)
│   └── users/                         # Autenticacao de sessao nativa Django
│
├── eventflow-react/                   # Implementacao SPA (Django REST + React 19)
│   ├── backend/                       # API REST em Django REST Framework
│   │   ├── api/                       # Endpoints JSON, serializers e views REST
│   │   ├── backend/                   # Configuracao do Django REST
│   │   ├── media/                     # Catalogo de imagens espelhado
│   │   └── users/                     # Autenticacao e endpoints de sessao
│   └── frontend/                      # Aplicacao client-side em React 19 e Vite
│       ├── src/                       # Componentes, rotas, paginas e gerenciamento de estado
│       ├── public/                    # Arquivos estaticos do cliente
│       └── package.json               # Dependencias npm do frontend
│
└── experimento/                       # Suite automatizada de benchmark e analise estatistica
    ├── README.md                      # Documentacao metodologica e guia de reproducao
    ├── docker-compose.yml             # Orquestracao dos servicos sob Nginx e Gunicorn
    ├── executar_experimento.sh        # Script de orquestracao para Linux / Ubuntu
    ├── executar_experimento.ps1       # Script de orquestracao para Windows PowerShell
    ├── run.py                         # CLI central de coleta, analise e relatorios
    ├── seed.py                        # Sincronizacao deterministica dos bancos e imagens
    ├── seed_timestamp.json            # Ancora temporal para garantia de reprodutibilidade
    ├── deploy/                        # Dockerfiles de producao (backends, frontends, runner) e Nginx
    ├── collect/                       # Scripts de medicao Playwright (Cold Start, Scroll, Mutacao)
    ├── analysis/                      # Testes estatisticos (Welch, ANOVA, Cohen's d, Regressao)
    ├── report/                        # Geradores de tabelas CSV e graficos em 300 DPI
    ├── resultados/                    # Dados brutos coletados e relatorios em markdown
    ├── tabelas/                       # Tabelas consolidadas para a dissertacao
    ├── graficos_cold_start/           # Graficos em 300 DPI de Cold Start
    ├── graficos_infinite_scroll/      # Graficos de evolucao longitudinal de Scroll
    └── graficos_mutacao_estado/       # Graficos de latencia de mutacao atomica de estado
```

---

## 2. Criterios de Paridade e Controle Experimental

Para eliminar variaveis de confusao e garantir validade interna ao experimento, as duas aplicacoes seguem requisitos estritos de equivalencia:

1. **Paridade Funcional e de Dominio:**
   * Ambas implementam o sistema de gestao de eventos EventFlow, contendo descoberta de eventos, busca filtrada, paginacao infinita, cadastro e login de usuarios, tela de detalhes com inscricao e cancelamento atomico, alem de dashboard de organizador.
   * Ambas utilizam exatamente o mesmo esquema de banco de dados relacional SQLite, mesma massa de dados deterministica (seed) e o mesmo catalogo de imagens normalizadas em proporcao 16:9 (480x270 a 75% de qualidade JPEG).

2. **Paridade Visual e de Design System:**
   * Ambas compartilham o mesmo design system, estrutura de cores, tipografia, espacamentos e cartoes de eventos, assegurando identidade visual identica em modo claro (Light Mode).

3. **Paridade de Infraestrutura em Producao:**
   * Ambas sao executadas com `DEBUG=False` em conteineres Docker com limites identicos de recursos (2 vCPUs e 2 GB de memoria RAM por servico).
   * **Camada Web / Borda:** Servidor Nginx como proxy reverso de alto desempenho e servidor de arquivos estaticos e de midia (porta 8080 no HTMX; porta 5173 no React).
   * **Camada de Aplicacao:** Servidor WSGI Gunicorn (2 workers e 2 threads) executando o Django na porta interna 8000.

| Camada | Servico HTMX (HDA) | Servico React (SPA) |
| :--- | :--- | :--- |
| **Borda / Web** | `htmx-frontend` (`efp-htmx-front`) | `react-frontend` (`efp-react-front`) |
| **Aplicacao** | `htmx-backend` (`efp-htmx-back`) | `react-backend` (`efp-react-back`) |
| **Porta de Acesso** | `http://localhost:8080/` | `http://localhost:5173/` |

---

## 3. Execucao em Modo de Desenvolvimento

Caso deseje executar as aplicacoes localmente fora de conteineres:

### 3.1. EventFlow HTMX (HDA)

```bash
cd eventflow-htmx

# 1. Instalar dependencias Python
pip install -r requirements.txt

# 2. Executar migracoes
python manage.py migrate

# 3. Iniciar servidor de desenvolvimento na porta 8080
python manage.py runserver 8080
```
Acesse no navegador: `http://localhost:8080/`

---

### 3.2. EventFlow React (SPA)

**Backend (Django REST Framework):**
```bash
cd eventflow-react/backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000
```

**Frontend (React 19 + Vite):**
```bash
cd eventflow-react/frontend
npm install
npm run dev
```
Acesse no navegador: `http://localhost:5173/`

---

## 4. Execucao da Suite Experimental e Benchmarking

A suite experimental conteinerizada permite reproduzir todos os testes sob condicoes rigorosamente controladas de rede e CPU via Chrome DevTools Protocol (CDP).

### 4.1. Execucao Completa do Benchmark

Navegue ate a pasta `experimento/` e execute o script orquestrador de acordo com o sistema operacional:

**No Linux / Ubuntu (recomendado):**
```bash
cd experimento
chmod +x executar_experimento.sh
./executar_experimento.sh -r 30
```

**No Windows PowerShell:**
```powershell
cd experimento
.\executar_experimento.ps1 -Runs 30
```

O script realiza automaticamente o seed das bases de dados, constroi as imagens Docker de producao, sobe os servicos, executa a coleta via Playwright em contêiner headless isolado e processa a analise estatistica completa.

### 4.2. Parametros Disponiveis nos Scripts

* `-e, --experiment <nome>`: Escolha entre `all`, `cold-start`, `infinite-scroll` ou `state-mutation` (padrao: `all`).
* `-t, --tech <nome>`: Tecnologia a testar: `all`, `htmx` ou `react` (padrao: `all`).
* `-p, --profile <nome>`: Perfil de rede: `all`, `NoThrottling`, `Fast4G` ou `Slow4G` (padrao: `all`).
* `-r, --runs <num>`: Quantidade de repeticoes por condicao (padrao: 30).
* `-b, --batches <num>`: Quantidade de lotes de rolagem no infinite scroll (padrao: 50).
* `-m, --mutations <num>`: Quantidade de mutacoes alternadas de inscricao e cancelamento (padrao: 20).
* `-s, --seed`: Forca o reset e re-populacao dos bancos de dados antes da rodada.
* `--analysis-only`: Pula a coleta no navegador e apenas regera as tabelas e graficos a partir dos CSVs existentes.

### 4.3. Regerar Graficos e Tabelas Instantaneamente

Todos os dados brutos oficiais estao preservados na pasta `experimento/resultados/`. Para regerar todos os 65 graficos em 300 DPI e as 4 tabelas consolidadas:

```bash
cd experimento
docker compose run --rm runner python run.py --skip-collect
```

As saidas sao salvas em:
* Tabelas consolidadas: `experimento/tabelas/`
* Relatorios estatisticos: `experimento/resultados/`
* Figuras academicas em alta resolucao: `experimento/graficos_*/`
