"""Análise estatística da Mutação de Estado: descritivas, teste t de Welch e ANOVA de duas vias."""
import numpy as np
import pandas as pd
from src.stats_utils import (
    describe, welch_test, fmt_t, fmt_p, pct_variation, two_way_anova,
    cohens_d, fmt_d, fdr_correction
)
from src import config

METRICS = ["MutationLatencyMs", "MutationPayloadKB", "JSHeapMB", "DOMNodeCount"]


def _op(df):
    df = df.copy()
    if "TipoOperacao" not in df.columns:
        df["TipoOperacao"] = df["MutationIndex"].apply(
            lambda x: "POST" if x % 2 != 0 else "DELETE")
    return df


def _aggregate_by_run(df):
    """Consolida as mutações por rodada independente (N=30) para evitar pseudo-repetição amostral."""
    return df.groupby(["PerfilRede", "Tecnologia", "Rodada"]).agg({
        "MutationLatencyMs": "mean",
        "MutationPayloadKB": "mean",
        "JSHeapMB": "last",
        "DOMNodeCount": "last",
    }).reset_index()


def unit(met):
    if "Ms" in met:
        return " ms"
    if "KB" in met:
        return " KB"
    if "MB" in met:
        return " MB"
    return ""


def run(csv_path=config.MUTATION_CSV, out_md=config.MUTATION_MD):
    if not csv_path.exists():
        print(f"[ERRO] {csv_path} não encontrado.")
        return
    df = _op(pd.read_csv(csv_path))
    if df.empty:
        print(f"[AVISO] {csv_path} está vazio.")
        return

    n_runs = df["Rodada"].nunique() if "Rodada" in df.columns else 0

    ops = [
        ("GERAL", df),
        ("POST", df[df["TipoOperacao"] == "POST"]),
        ("DELETE", df[df["TipoOperacao"] == "DELETE"]),
    ]
    md = ["# Relatório Estatístico de Mutação Rápida de Estado: React vs. HTMX\n",
          f"Este relatório apresenta a análise estatística detalhada da latência de resposta, consumo de "
          f"memória e carga de rede durante mutações repetidas de estado ($N = {n_runs}$ rodadas independentes), "
          "com **análise global consolidada** e **desagregação entre Inscrição (POST) e Cancelamento (DELETE)**.\n"]

    # 1. Descritivas
    md += ["## 1. Estatísticas Descritivas Globais (Todos os Ciclos Agregados)\n",
           "Valores representados como Média ± Desvio Padrão (DP).\n"]
    for op_label, op_df in ops:
        md.append(f"### 1.{ops.index((op_label, op_df)) + 1} {_op_title(op_label)}\n")
        md.append("| Perfil de Rede | Métrica | React (Média ± DP) | HTMX (Média ± DP) | Variação |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        for perf in config.PROFILES:
            for met in METRICS:
                if met not in op_df.columns:
                    continue
                r = _sub(op_df, perf, "React", met)
                h = _sub(op_df, perf, "HTMX", met)
                if r.empty and h.empty:
                    continue
                mr, sr = describe(r)
                mh, sh = describe(h)
                var = pct_variation(mr, mh)
                var_s = "N/A" if var is None else f"{var:+.1f}%"
                md.append(f"| {perf} | {met} | {mr:.2f} ± {sr:.2f}{unit(met)} | {mh:.2f} ± {sh:.2f}{unit(met)} | {var_s} |")
        md.append("\n")

    md += ["---\n",
           f"## 2. Teste t de Welch por Rodada Independente ($N = {n_runs}$ Rodadas)\n",
           "Para assegurar a validade inferencial e eliminar **pseudo-repetição amostral**, os testes comparam as médias consolidadas por rodada independente.\n"]
    for op_label, op_df in ops:
        agg_df = _aggregate_by_run(op_df)
        md.append(f"### 2.{ops.index((op_label, op_df)) + 1} {_op_title(op_label)}\n")
        md.append("| Perfil de Rede | Métrica | Estatística $t$ | $p$-valor | Significativo ($\\alpha=0.05$) |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        
        for perf in config.PROFILES:
            for met in METRICS:
                if met not in agg_df.columns:
                    continue
                r = _sub(agg_df, perf, "React", met).dropna()
                h = _sub(agg_df, perf, "HTMX", met).dropna()
                if len(r) <= 1 or len(h) <= 1:
                    md.append(f"| {perf} | {met} | N/A | N/A | N/A |")
                    continue
                t, p = welch_test(r, h)
                sig = "Sim (p < 0.05)" if p < 0.05 else "Não"
                md.append(f"| {perf} | {met} | {fmt_t(t)} | {fmt_p(p)} | {sig} |")
        md.append("\n")

    md += ["---\n",
           f"## 3. Análise de Variância de Duas Vias (Two-Way ANOVA por Rodada, $N={n_runs}$)\n"]
    for op_label, op_df in ops:
        agg_df = _aggregate_by_run(op_df)
        md.append(f"### 3.{ops.index((op_label, op_df)) + 1} ANOVA: {_op_title(op_label)}\n")
        for met in ["MutationLatencyMs", "JSHeapMB"]:
            md.append(f"#### Métrica: {met}\n")
            anova = two_way_anova(agg_df, met)
            if not anova:
                md.append("N/A\n")
                continue
            md.append("| Fator Avaliado | df | $F$ | $p$-valor | Significativo ($\\alpha=0.05$) |")
            md.append("| :--- | :--- | :--- | :--- | :--- |")
            for label, row in anova.items():
                if row["F"] is None:
                    continue
                sig = "Sim" if row["p"] is not None and row["p"] < 0.05 else "Não"
                md.append(f"| {label} | {row['df']:.0f} | {row['F']:.4f} | {fmt_p(row['p'])} | {sig} |")
            md.append("\n")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(md), encoding="utf-8")
    print(f"[OK] Relatório Mutação de Estado salvo em: {out_md}")


def _sub(df, perf, tech, met):
    return df.loc[(df["PerfilRede"] == perf) & (df["Tecnologia"] == tech), met]


def _op_title(label):
    return {
        "GERAL": "Geral (Todas as 20 Mutações)",
        "POST": "Inscrição em Evento (POST - Mutações Ímpares)",
        "DELETE": "Cancelamento de Inscrição (DELETE - Mutações Pares)",
    }.get(label, label)


if __name__ == "__main__":
    run()
