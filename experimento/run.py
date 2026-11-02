"""Orquestrador do pipeline experimental EventFlow (HTMX vs React) em modo producao.

Executa as fases do benchmark:
  1. Coleta automatizada via Playwright/CDP (cold start, infinite scroll, mutacao de estado)
  2. Analise estatistica inferencial (descritivas, teste de Welch, ANOVA, Cohen's d)
  3. Geracao de graficos de publicacao (300 DPI), tabelas consolidadas e metricas SPACE
"""
import argparse
import os
import sys
import time
from pathlib import Path

import urllib.request

from src import config
from src.net_profiles import parse_tech_filter

EXPERIMENTS = ["cold-start", "infinite-scroll", "state-mutation", "tcp-cwnd"]


def parse_experiment_filter(exp_str):
    if not exp_str or exp_str.strip().lower() in ("all", "*", ""):
        return EXPERIMENTS
    requested = [x.strip().lower() for x in exp_str.split(",") if x.strip()]
    selected = []
    aliases = {
        "cold-start": "cold-start", "cold": "cold-start", "cold_start": "cold-start", "coldstart": "cold-start", "1": "cold-start",
        "infinite-scroll": "infinite-scroll", "scroll": "infinite-scroll", "infinite_scroll": "infinite-scroll", "infinitescroll": "infinite-scroll", "2": "infinite-scroll",
        "state-mutation": "state-mutation", "mutation": "state-mutation", "state_mutation": "state-mutation", "statemutation": "state-mutation",
        "mutacao-estado": "state-mutation", "mutacao_estado": "state-mutation", "mutacao": "state-mutation", "3": "state-mutation",
        "tcp-cwnd": "tcp-cwnd", "cwnd": "tcp-cwnd", "tcp": "tcp-cwnd", "4": "tcp-cwnd",
    }
    for r in requested:
        key = aliases.get(r)
        if key and key not in selected:
            selected.append(key)
        elif not key:
            print(f"  [AVISO] Experimento '{r}' não reconhecido. Opções válidas: cold-start, infinite-scroll, state-mutation, tcp-cwnd")
    return selected if selected else EXPERIMENTS


def wait_for_http(url, name, timeout=90):
    print(f"  -> Aguardando prontidão do serviço {name} em {url}...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                if resp.status == 200:
                    print(f"  [OK] {name} está pronto!")
                    return True
        except Exception:
            pass
        time.sleep(1)
    print(f"  [ERRO] Timeout aguardando {name} ({url}).")
    return False


def run_phase(command):
    """Executa um subprocesso (um coletor) e reporta o código de saída."""
    print("\n" + "=" * 70)
    print(f"  EXECUTANDO: {' '.join(command)}")
    print("=" * 70)
    ok = subprocess_run(command)
    if not ok:
        print(f"\n[ERRO] Falha na execução da fase: {command[3] if len(command) > 3 else command}")
        sys.exit(1)


def subprocess_run(command):
    import subprocess
    return subprocess.run(command, cwd=str(config.BASE_DIR)).returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Orquestrador de experimentos (produção)")
    parser.add_argument("--runs", type=int, default=int(os.environ.get("RUNS", 30)))
    parser.add_argument("--scroll-batches", type=int, default=int(os.environ.get("SCROLL_BATCHES", 50)))
    parser.add_argument("--mutations", type=int, default=int(os.environ.get("MUTATIONS", 20)))
    parser.add_argument("--experiments", "-e", default=os.environ.get("EXPERIMENT", "all"))
    parser.add_argument("--tech", "-t", default=os.environ.get("TECH", "all"))
    parser.add_argument("--profiles", "-p", default=os.environ.get("PROFILES", "all"))
    parser.add_argument(
        "--chart-type",
        "-c",
        choices=["hybrid", "bar", "boxplot", "all"],
        default=os.environ.get("CHART_TYPE", "hybrid"),
        help="Tipo de gráficos a gerar: hybrid (padrão: barras para volumes e boxplots para latências), bar (original do TCC), boxplot (estritamente boxplots) ou all (ambos para comparação)",
    )
    parser.add_argument(
        "--show-samples",
        action="store_true",
        default=os.environ.get("SHOW_SAMPLES", "0").lower() in ("1", "true", "yes"),
        help="Exibe os pontos individuais das amostras sobrepostos aos box-plots (padrão: desativado)",
    )
    parser.add_argument("--reset-csv", action="store_true")
    parser.add_argument("--skip-collect", action="store_true")
    parser.add_argument("--skip-analysis", action="store_true", default=os.environ.get("SKIP_ANALYSIS", "0") in ("1", "true", "True"))
    parser.add_argument("--htmx-url", default=os.environ.get("HTMX_URL", "http://htmx:8080"))
    parser.add_argument("--react-url", default=os.environ.get("REACT_URL", "http://react-frontend:5173"))
    args = parser.parse_args()

    selected = parse_experiment_filter(args.experiments)
    techs = parse_tech_filter(args.tech)
    config.ensure_dirs()

    print("\n" + "#" * 70)
    print("   EVENTFLOW BENCHMARK RUNNER - PRODUÇÃO")
    print(f"   Experimentos: {', '.join(selected)} | Tech: {', '.join(techs)} | Perfis: {args.profiles}")
    print(f"   Config: {args.runs} rodadas | {args.scroll_batches} lotes (scroll) | {args.mutations} mutações")
    print("#" * 70)

    if not args.skip_collect:
        if args.reset_csv:
            _reset_csvs()
        if "HTMX" in techs and not wait_for_http(args.htmx_url, "EventFlow HTMX"):
            sys.exit(1)
        if "React" in techs and not wait_for_http(args.react_url, "EventFlow React Frontend"):
            sys.exit(1)

        common = _collector_args(args, techs)
        if "cold-start" in selected:
            run_phase([sys.executable, "-m", "collect.collect_cold_start", *common, "--output", str(config.COLD_START_CSV)])
        if "infinite-scroll" in selected:
            run_phase([sys.executable, "-m", "collect.collect_infinite_scroll", *common,
                       "--batches", str(args.scroll_batches), "--output", str(config.SCROLL_CSV)])
        if "state-mutation" in selected:
            run_phase([sys.executable, "-m", "collect.collect_state_mutation", *common,
                       "--mutations", str(args.mutations), "--output", str(config.MUTATION_CSV)])
        if "tcp-cwnd" in selected:
            tech_arg = "all" if len(techs) > 1 else techs[0]
            run_phase([sys.executable, "-m", "collect.collect_tcp_cwnd", "--tech", tech_arg,
                       "--htmx-url", args.htmx_url, "--react-url", args.react_url])

    if not args.skip_analysis:
        _analysis_phase(args, selected)

    print("\n" + "=" * 70)
    print(">>> EXECUÇÃO CONCLUÍDA COM SUCESSO!")
    print("    Resultados em: resultados/ | gráficos em: graficos*/ | tabelas em: tabelas/")
    print("=" * 70)


def _collector_args(args, techs):
    return [
        "--runs", str(args.runs),
        "--tech", ",".join(techs),
        "--profiles", args.profiles,
        "--htmx-url", args.htmx_url,
        "--react-url", args.react_url
    ]


def _reset_csvs():
    for path in (config.COLD_START_CSV, config.SCROLL_CSV, config.MUTATION_CSV, config.TCP_CWND_CSV_HTMX, config.TCP_CWND_CSV_REACT):
        if path.exists():
            path.unlink()
            print(f"  [Reset] {path.name} removido.")


def _analysis_phase(args, selected=None):
    import analysis.analyze_cold_start as a_cs
    import analysis.analyze_infinite_scroll as a_isc
    import analysis.analyze_state_mutation as a_mut
    import analysis.analyze_tcp_cwnd as a_tcp
    import report.graphs as g
    import report.tables as t

    if selected is None:
        selected = EXPERIMENTS + ["tcp-cwnd"]

    if "cold-start" in selected and config.COLD_START_CSV.exists():
        a_cs.run()
    if "infinite-scroll" in selected and config.SCROLL_CSV.exists():
        a_isc.run()
    if "state-mutation" in selected and config.MUTATION_CSV.exists():
        a_mut.run()
    if "tcp-cwnd" in selected and (config.TCP_CWND_CSV_HTMX.exists() or config.TCP_CWND_CSV_REACT.exists()):
        a_tcp.run()

    chart_mode = getattr(args, "chart_type", "hybrid")
    show_samples = getattr(args, "show_samples", False)

    if set(selected) == {"tcp-cwnd"}:
        g.set_academic_style()
        g.tcp_cwnd_graphs()
    else:
        g.generate_all(mode=chart_mode, show_samples=show_samples)
        t.generate_all()


if __name__ == "__main__":
    main()
