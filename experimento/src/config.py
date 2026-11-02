"""Caminhos e constantes compartilhados do pipeline experimental EventFlow (HTMX vs React)."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Repositórios do EventFlow na raiz do projeto (ou /app no runner Docker)
HTMX_REPO = Path("/app/eventflow-htmx") if Path("/app/eventflow-htmx").exists() else BASE_DIR.parent / "eventflow-htmx"
REACT_REPO = Path("/app/eventflow-react") if Path("/app/eventflow-react").exists() else BASE_DIR.parent / "eventflow-react"

RESULTS = BASE_DIR / "resultados"
GRAFICOS_COLD = BASE_DIR / "graficos_cold_start"
GRAFICOS = GRAFICOS_COLD  # Alias para compatibilidade
GRAFICOS_SCROLL = BASE_DIR / "graficos_infinite_scroll"
GRAFICOS_MUTACAO = BASE_DIR / "graficos_mutacao_estado"
TABELAS = BASE_DIR / "tabelas"

COLD_START_CSV = RESULTS / "dados_experimento_cold_start.csv"
SCROLL_CSV = RESULTS / "dados_experimento_infinite_scroll.csv"
MUTATION_CSV = RESULTS / "dados_experimento_mutacao_estado.csv"
TCP_CWND_CSV_HTMX = RESULTS / "dados_tcp_cwnd_HTMX.csv"
TCP_CWND_CSV_REACT = RESULTS / "dados_tcp_cwnd_React.csv"

COLD_START_MD = RESULTS / "resultados_estatisticas_cold_start.md"
SCROLL_MD = RESULTS / "resultados_estatisticas_infinite_scroll.md"
MUTATION_MD = RESULTS / "resultados_estatisticas_mutacao_estado.md"
TCP_CWND_MD = RESULTS / "relatorio_tcp_cwnd.md"

TABELA_1 = TABELAS / "tabela_1_cold_start.csv"
TABELA_2 = TABELAS / "tabela_2_infinite_scroll.csv"
TABELA_3 = TABELAS / "tabela_3_mutacao_estado.csv"
TABELA_4 = TABELAS / "tabela_4_metricas_space.csv"
TABELA_ANOVA_COLD_HOME = TABELAS / "tabela_anova_cold_start_home.csv"
TABELA_ANOVA_SCROLL = TABELAS / "tabela_anova_infinite_scroll.csv"
TABELA_ANOVA_MUTACAO = TABELAS / "tabela_anova_mutacao.csv"

PROFILES = ["NoThrottling", "Fast4G", "Slow4G"]
PAGES = ["Home", "Search", "Details"]
TECHNOLOGIES = ["React", "HTMX"]


def ensure_dirs():
    """Cria os diretórios de saída caso ainda não existam."""
    for d in (RESULTS, GRAFICOS_COLD, GRAFICOS_SCROLL, GRAFICOS_MUTACAO, TABELAS):
        d.mkdir(parents=True, exist_ok=True)
