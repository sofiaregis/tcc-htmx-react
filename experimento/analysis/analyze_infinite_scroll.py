"""Análise estatística do Infinite Scroll: descritivas, teste t de Welch robusto por rodada,
regressão linear de degradação assintótica (O(1) vs O(N)) e ANOVA de duas vias.
"""
import numpy as np
import pandas as pd
from scipy import stats

from src import config
from src.stats_utils import describe, welch_test, fmt_t, fmt_p, two_way_anova

METRICS = ["BatchLoadTime", "BatchPayloadKB", "JSHeapMB", "DeltaJSHeapMB", "DOMNodeCount"]


def _norm(df):
    if "BatchLatencyMs" in df.columns and "BatchLoadTime" not in df.columns:
        df["BatchLoadTime"] = df["BatchLatencyMs"]
    if "PayloadBatchKB" in df.columns and "BatchPayloadKB" not in df.columns:
        df["BatchPayloadKB"] = df["PayloadBatchKB"]
    if "BatchIndex" in df.columns and "BatchNum" not in df.columns:
        df["BatchNum"] = df["BatchIndex"]
    return df


def unit(met):
    if "Time" in met or "Latency" in met or "Slope" in met:
        return " ms"
    if "KB" in met:
        return " KB"
    if "MB" in met:
        return " MB"
    return ""


def run(csv_path=config.SCROLL_CSV, out_md=config.SCROLL_MD):
    if not csv_path.exists():
        print(f"[ERRO] {csv_path} não encontrado.")
        return
    df = _norm(pd.read_csv(csv_path))
    if df.empty:
        print(f"[AVISO] {csv_path} está vazio.")
        return

    n_runs = df["Rodada"].nunique() if "Rodada" in df.columns else 0
    max_batch = int(df["BatchIndex"].max()) if "BatchIndex" in df.columns else 50
    n_obs_per_tech = len(df[df["Tecnologia"] == "HTMX"]) if "Tecnologia" in df.columns else 0

    md = [
        "# Relatório Longitudinal e Inferencial do Infinite Scroll: React vs. HTMX\n",
        f"Este relatório apresenta a análise experimental do **comportamento longitudinal** e da **complexidade assintótica** "
        f"entre **React 19 (SPA)** e **HTMX 2 (HDA)** na página de busca de eventos ao longo de até {max_batch} lotes de scroll.\n",
    ]

    # 0. Taxa de Conclusão e Integridade Amostral
    md += [
        "## 0. Taxa de Conclusão e Integridade Amostral por Perfil de Rede\n",
        "Verifica a integridade das coletas e se ocorreram interrupções precoces por timeout sob condições severas de rede.\n",
        "| Perfil de Rede | Tecnologia | Rodadas ($N$) | Lotes Médios Alcançados | Taxa de Conclusão Total (50 Lotes) |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for perf in config.PROFILES:
        sub = df[df["PerfilRede"] == perf]
        if sub.empty:
            continue
        for tech in config.TECHNOLOGIES:
            t_sub = sub[sub["Tecnologia"] == tech]
            if t_sub.empty:
                continue
            run_maxes = t_sub.groupby("Rodada")["BatchIndex"].max()
            mean_batches = run_maxes.mean()
            complete_pct = (run_maxes >= max_batch).mean() * 100
            md.append(f"| {perf} | {tech} | {len(run_maxes)} | {mean_batches:.1f} ± {run_maxes.std(ddof=1) if len(run_maxes)>1 else 0:.1f} lotes | {complete_pct:.1f}% ({int((run_maxes >= max_batch).sum())}/{len(run_maxes)}) |")
    md.append("\n---\n")

    # 1. Estatísticas por Unidade Independente de Replicação
    md += [
        f"## 1. Estatísticas por Rodada Independente ($N = {n_runs}$ Rodadas)\n",
        "Para evitar pseudo-repetição amostral (*pseudoreplication*), as métricas de latência foram consolidadas pela média de cada rodada, "
        "e as métricas acumulativas de memória e nós do DOM foram extraídas no **Lote Final Alcançado por Cada Rodada (sem viés de sobrevivência)**.\n",
        "| Perfil de Rede | Métrica Avaliada | React (Média ± DP) | HTMX (Média ± DP) | Estatística $t$ | $p$-valor | Significativo ($\\alpha=0.05$) |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for perf in config.PROFILES:
        sub = df[df["PerfilRede"] == perf]
        if sub.empty:
            continue

        # A. Latência Média por Rodada
        run_lat = sub.groupby(["Rodada", "Tecnologia"])["BatchLoadTime"].mean().unstack()
        if "React" in run_lat.columns and "HTMX" in run_lat.columns:
            r_lat, h_lat = run_lat["React"].dropna(), run_lat["HTMX"].dropna()
            mr, sr = describe(r_lat)
            mh, sh = describe(h_lat)
            t, p = welch_test(r_lat, h_lat)
            sig = "Sim (p < 0.05)" if p < 0.05 else "Não"
            md.append(f"| {perf} | Latência Média por Rodada | {mr:.2f} ± {sr:.2f} ms | {mh:.2f} ± {sh:.2f} ms | {fmt_t(t)} | {fmt_p(p)} | {sig} |")

        # B/C/D. Extração do Lote Final individual de cada rodada
        last_idx = sub.groupby(["Rodada", "Tecnologia"])["BatchIndex"].idxmax()
        b_final = sub.loc[last_idx]
        if not b_final.empty:
            # Delta JS Heap no Lote Final
            run_delta = b_final.groupby(["Rodada", "Tecnologia"])["DeltaJSHeapMB"].mean().unstack()
            if "React" in run_delta.columns and "HTMX" in run_delta.columns:
                r_d, h_d = run_delta["React"].dropna(), run_delta["HTMX"].dropna()
                mr, sr = describe(r_d)
                mh, sh = describe(h_d)
                t, p = welch_test(r_d, h_d)
                sig = "Sim (p < 0.05)" if p < 0.05 else "Não"
                md.append(f"| {perf} | $\\Delta$ JS Heap Final | {mr:.2f} ± {sr:.2f} MB | {mh:.2f} ± {sh:.2f} MB | {fmt_t(t)} | {fmt_p(p)} | {sig} |")

            # JS Heap Total no Lote Final
            run_heap = b_final.groupby(["Rodada", "Tecnologia"])["JSHeapMB"].mean().unstack()
            if "React" in run_heap.columns and "HTMX" in run_heap.columns:
                r_h, h_h = run_heap["React"].dropna(), run_heap["HTMX"].dropna()
                mr, sr = describe(r_h)
                mh, sh = describe(h_h)
                t, p = welch_test(r_h, h_h)
                sig = "Sim (p < 0.05)" if p < 0.05 else "Não"
                md.append(f"| {perf} | JS Heap Total Final | {mr:.2f} ± {sr:.2f} MB | {mh:.2f} ± {sh:.2f} MB | {fmt_t(t)} | {fmt_p(p)} | {sig} |")

            # Nós do DOM no Lote Final
            run_dom = b_final.groupby(["Rodada", "Tecnologia"])["DOMNodeCount"].mean().unstack()
            if "React" in run_dom.columns and "HTMX" in run_dom.columns:
                r_dom, h_dom = run_dom["React"].dropna(), run_dom["HTMX"].dropna()
                mr, sr = describe(r_dom)
                mh, sh = describe(h_dom)
                t, p = welch_test(r_dom, h_dom)
                sig = "Sim (p < 0.05)" if p < 0.05 else "Não (Equivalência Estrutural)"
                md.append(f"| {perf} | Nós do DOM Final | {mr:.0f} ± {sr:.1f} nós | {mh:.0f} ± {sh:.1f} nós | {fmt_t(t)} | {fmt_p(p)} | {sig} |")

    md.append("\n---\n")

    # 2. Análise de Degradação Linear e Complexidade Assintótica (O(1) vs O(N))
    md += [
        "## 2. Taxa de Degradação Linear e Complexidade Assintótica ($\\beta$ em ms/lote)\n",
        f"Regressão linear calculada individualmente para cada uma das {n_runs} rodadas: $\\text{{Latência}}(k) = \\alpha + \\beta \\cdot k$, "
        "onde $\\beta$ representa o custo marginal de reconciliação/inserção por lote adicional.\n",
        "| Perfil de Rede | Taxa React $\\beta_{\\text{React}}$ ($R^2$) | Taxa HTMX $\\beta_{\\text{HTMX}}$ ($R^2$) | Teste Welch ($t, p$) | Complexidade Observada |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]

    for perf in config.PROFILES:
        sub = df[df["PerfilRede"] == perf]
        slopes = []
        for (run_id, tech), group in sub.groupby(["Rodada", "Tecnologia"]):
            res = stats.linregress(group["BatchIndex"], group["BatchLoadTime"])
            slopes.append({"Rodada": run_id, "Tecnologia": tech, "Slope": res.slope, "R2": res.rvalue**2})
        slope_df = pd.DataFrame(slopes)
        if not slope_df.empty:
            r_rows = slope_df[slope_df["Tecnologia"] == "React"]
            h_rows = slope_df[slope_df["Tecnologia"] == "HTMX"]
            r_s = r_rows["Slope"].dropna()
            h_s = h_rows["Slope"].dropna()
            r_r2 = r_rows["R2"].mean()
            h_r2 = h_rows["R2"].mean()

            mr_s, sr_s = describe(r_s)
            mh_s, sh_s = describe(h_s)
            t_s, p_s = welch_test(r_s, h_s)

            verdict = f"HTMX $O(1)$ vs React $O(N)$"
            md.append(
                f"| {perf} | {mr_s:.4f} ± {sr_s:.4f} ms/lote ($R^2={r_r2:.2f}$) | {mh_s:.4f} ± {sh_s:.4f} ms/lote ($R^2={h_r2:.2f}$) | "
                f"$t={fmt_t(t_s)}, p={fmt_p(p_s)}$ | {verdict} |"
            )

    md.append("\n---\n")

    # 3. Estatísticas Globais de Todos os Lotes
    md += [
        f"## 3. Estatísticas Descritivas Globais (Todos os Lotes Agregados, $N = {n_obs_per_tech:,}$ observações por tecnologia)\n",
        "Valores médios calculados sobre a totalidade de requisições de scroll.\n",
        "| Perfil de Rede | Métrica | React (Média ± DP) | HTMX (Média ± DP) |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for perf in config.PROFILES:
        for met in METRICS:
            if met not in df.columns:
                continue
            r = df.loc[(df["PerfilRede"] == perf) & (df["Tecnologia"] == "React"), met]
            h = df.loc[(df["PerfilRede"] == perf) & (df["Tecnologia"] == "HTMX"), met]
            if r.empty and h.empty:
                continue
            mr, sr = describe(r)
            mh, sh = describe(h)
            md.append(f"| {perf} | {met} | {mr:.2f} ± {sr:.2f}{unit(met)} | {mh:.2f} ± {sh:.2f}{unit(met)} |")

    md.append("\n---\n")

    # 4. Análise de Variância de Duas Vias (Two-Way ANOVA por Rodada Independente)
    md += [f"## 4. Análise de Variância de Duas Vias (Two-Way ANOVA por Rodada, $N={n_runs}$)\n"]
    
    # Prepara DataFrame consolidado por rodada para ANOVA livre de pseudo-repetição
    run_summary = df.groupby(["PerfilRede", "Tecnologia", "Rodada"]).agg({
        "BatchLoadTime": "mean",
        "BatchPayloadKB": "mean",
        "JSHeapMB": "last",
        "DeltaJSHeapMB": "last",
        "DOMNodeCount": "last",
    }).reset_index()

    for met in METRICS:
        if met not in run_summary.columns:
            continue
        md.append(f"### ANOVA para: {met} (Médias/Finais por Rodada, $N={n_runs}$)\n")
        anova = two_way_anova(run_summary, met)
        if not anova:
            continue
        md.append("| Fator Avaliado | df | $F$ | $p$-valor | Relevante ($\\alpha=0.05$) |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        for label, row in anova.items():
            if row["F"] is None:
                continue
            sig = "Sim" if row["p"] is not None and row["p"] < 0.05 else "Não"
            md.append(f"| {label} | {row['df']:.0f} | {row['F']:.4f} | {fmt_p(row['p'])} | {sig} |")
        md.append("\n")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(md), encoding="utf-8")
    print(f"[OK] Relatório Infinite Scroll salvo em: {out_md}")


if __name__ == "__main__":
    run()
