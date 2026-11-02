#!/usr/bin/env bash
# ==============================================================================
# Execução dos experimentos em ambiente de PRODUÇÃO (Ubuntu / Linux Nativo)
#
# Exemplos:
#   ./executar_experimento.sh                                              # roda os 3 experimentos (30 runs)
#   ./executar_experimento.sh -e state-mutation                           # roda só mutação de estado
#   ./executar_experimento.sh -e infinite-scroll                          # roda só o infinite scroll
#   ./executar_experimento.sh -e cold-start                               # roda só cold start
#   ./executar_experimento.sh -e infinite-scroll -t htmx                  # só infinite scroll do HTMX
#   ./executar_experimento.sh -p Slow4G                                   # roda os 3 apenas sob Slow4G
#   ./executar_experimento.sh -r 30 -b 50                                 # 30 rodadas com 50 lotes
#   ./executar_experimento.sh --analysis-only                             # apenas regera tabelas e gráficos
# ==============================================================================

set -eo pipefail

# Cores para o terminal
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Valores padrão
EXPERIMENT="all"
TECH="all"
PROFILES="all"
RUNS=30
SCROLL_BATCHES=50
MUTATIONS=20
SEED=false
SKIP_ANALYSIS=false
NO_COLLECT=false
ANALYSIS_ONLY=false
CHART_TYPE="hybrid"

# Função de ajuda
show_help() {
    echo -e "${CYAN}Uso: ./executar_experimento.sh [opções]${NC}"
    echo ""
    echo "Opções disponíveis:"
    echo "  -e, --experiment, --experiments <exp>   Experimento a executar (all, cold-start, infinite-scroll, state-mutation) [padrão: all]"
    echo "  -t, --tech, --technology <tech>         Tecnologia a testar (all, htmx, react) [padrão: all]"
    echo "  -p, --profile, --profiles <profile>     Perfil de rede (all, NoThrottling, Fast4G, Slow4G) [padrão: all]"
    echo "  -r, --runs <num>                        Número de rodadas por condição [padrão: 30]"
    echo "  -c, --chart-type <type>                 Tipo de gráficos (hybrid, bar, boxplot, all) [padrão: hybrid]"
    echo "  -b, --batches, --scroll-batches <num>   Número de lotes no Infinite Scroll [padrão: 50]"
    echo "  -m, --mutations <num>                   Número de mutações alternadas [padrão: 20]"
    echo "  -s, --seed                              Força o reset e re-população do banco de dados"
    echo "  --skip-analysis                         Pula a etapa de análise estatística/gráficos"
    echo "  --no-collect                            Pula a coleta via navegador"
    echo "  --analysis-only                         Pula a coleta e apenas regera tabelas e gráficos"
    echo "  -h, --help                              Exibe esta mensagem de ajuda"
    echo ""
}

# Processamento de argumentos
while [[ $# -gt 0 ]]; do
    case "$1" in
        -e|--experiment|--experiments)
            EXPERIMENT="$2"
            shift 2
            ;;
        -t|--tech|--technology)
            TECH="$2"
            shift 2
            ;;
        -p|--profile|--profiles)
            PROFILES="$2"
            shift 2
            ;;
        -r|--runs)
            RUNS="$2"
            shift 2
            ;;
        -c|--chart-type)
            CHART_TYPE="$2"
            shift 2
            ;;
        -b|--batches|--scroll-batches)
            SCROLL_BATCHES="$2"
            shift 2
            ;;
        -m|--mutations)
            MUTATIONS="$2"
            shift 2
            ;;
        -s|--seed)
            SEED=true
            shift
            ;;
        --skip-analysis)
            SKIP_ANALYSIS=true
            shift
            ;;
        --no-collect)
            NO_COLLECT=true
            shift
            ;;
        --analysis-only)
            ANALYSIS_ONLY=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}[ERRO] Opção desconhecida: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

echo -e "${CYAN}==============================================================================${NC}"
echo -e "${CYAN}   EVENTFLOW BENCHMARK (PRODUÇÃO) - AMBIENTE CONTROLADO DOCKER (LINUX)${NC}"
echo -e "${CYAN}==============================================================================${NC}"
echo -e "${GRAY}  - Experimento(s):  $EXPERIMENT${NC}"
echo -e "${GRAY}  - Tecnologia(s):   $TECH${NC}"
echo -e "${GRAY}  - Perfil(is) Rede: $PROFILES${NC}"
echo -e "${GRAY}  - Parâmetros:      $RUNS rodadas | $SCROLL_BATCHES lotes (scroll) | $MUTATIONS mutações${NC}"
echo -e "${CYAN}==============================================================================${NC}"

# Define diretórios
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
HTMX_DB="$PROJECT_ROOT/eventflow-htmx/db.sqlite3"
REACT_DB="$PROJECT_ROOT/eventflow-react/backend/db.sqlite3"

# Garante comando docker compose
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif which docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo -e "${RED}[ERRO] 'docker compose' não encontrado. Instale o plugin do Docker Compose.${NC}"
    exit 1
fi

# Detecta interpretador python
if which python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif which python &> /dev/null; then
    PYTHON_CMD="python"
else
    PYTHON_CMD=""
fi

# Limpa diretórios acidentais criados pelo Docker caso os arquivos não existissem previamente
if [ -d "$HTMX_DB" ]; then
    echo -e "${YELLOW}[Aviso] Removendo diretório indevido em $HTMX_DB...${NC}"
    rm -rf "$HTMX_DB"
fi
if [ -d "$REACT_DB" ]; then
    echo -e "${YELLOW}[Aviso] Removendo diretório indevido em $REACT_DB...${NC}"
    rm -rf "$REACT_DB"
fi

# Valida se os bancos de dados existem e possuem conteúdo (> 0 bytes)
HTMX_DB_VALID=false
if [ -f "$HTMX_DB" ] && [ -s "$HTMX_DB" ]; then
    HTMX_DB_VALID=true
fi

REACT_DB_VALID=false
if [ -f "$REACT_DB" ] && [ -s "$REACT_DB" ]; then
    REACT_DB_VALID=true
fi

NEEDS_SEED=false
if [ "$SEED" = true ] || [ "$HTMX_DB_VALID" = false ] || [ "$REACT_DB_VALID" = false ]; then
    NEEDS_SEED=true
fi

# 1. Seed automático se os bancos não existirem, ou forçado via --seed
if [ "$NEEDS_SEED" = true ] && [ "$ANALYSIS_ONLY" = false ]; then
    if [ "$SEED" = false ]; then
        echo -e "\n${YELLOW}[1/3] Banco de dados não encontrado ou vazio. Gerando seed inicial automaticamente...${NC}"
    else
        echo -e "\n${YELLOW}[1/3] Executando seed e sincronização do banco de dados...${NC}"
    fi

    if [ -n "$PYTHON_CMD" ]; then
        $PYTHON_CMD seed.py
    else
        echo -e "${YELLOW}[Info] Python do host não encontrado. Executando seed.py via container Docker...${NC}"
        $DOCKER_COMPOSE run --rm runner python seed.py
    fi
    echo -e "${GREEN}[OK] Seed concluído com sucesso.${NC}"
fi

# 2. Subir os serviços de produção (apenas se for coletar)
if [ "$ANALYSIS_ONLY" = false ]; then
    echo -e "\n${YELLOW}[1/3] Subindo serviços de produção...${NC}"
    $DOCKER_COMPOSE up -d --build htmx-backend htmx-frontend react-backend react-frontend
fi

# 3. Executar o runner de benchmark
if [ "$NO_COLLECT" = false ]; then
    echo -e "\n${YELLOW}[2/3] Executando runner de benchmark...${NC}"
    RUNNER_ARGS=(
        "python" "run.py"
        "--experiments" "$EXPERIMENT"
        "--tech" "$TECH"
        "--profiles" "$PROFILES"
        "--runs" "$RUNS"
        "--chart-type" "$CHART_TYPE"
        "--scroll-batches" "$SCROLL_BATCHES"
        "--mutations" "$MUTATIONS"
    )

    if [ "$SKIP_ANALYSIS" = true ]; then
        RUNNER_ARGS+=("--skip-analysis")
    fi
    if [ "$ANALYSIS_ONLY" = true ]; then
        RUNNER_ARGS+=("--skip-collect")
    fi

    $DOCKER_COMPOSE run --rm runner "${RUNNER_ARGS[@]}"
fi

# 4. Cleanup dos serviços (preserva os dados coletados, gráficos e tabelas)
echo -e "\n${YELLOW}[3/3] Derrubando serviços de produção...${NC}"
$DOCKER_COMPOSE down

echo ""
echo -e "${GREEN}==============================================================================${NC}"
echo -e "${GREEN}   BENCHMARK CONCLUÍDO COM SUCESSO!${NC}"
echo -e "${GREEN}   - Tabelas consolidadas: 'tabelas/'${NC}"
echo -e "${GREEN}   - Relatórios estatísticos: 'resultados/'${NC}"
echo -e "${GREEN}   - Figuras e Gráficos (300 DPI): 'graficos*/'${NC}"
echo -e "${GREEN}==============================================================================${NC}"
