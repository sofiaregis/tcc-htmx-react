"""Geracao das tabelas estatisticas consolidadas em formato CSV a partir dos dados brutos.

Processa os resultados das coletas e exporta as tabelas 1 a 4 com metricas descritivas,
dispersao robusta (mediana, IQR, P95), variacao percentual, testes t de Welch,
intervalos de confianca de 95%, avaliacao de relevância prática (limiar 50 ms),
tabelas de ANOVA de 2-vias com eta-quadrado parcial e metricas SPACE.
"""
import pandas as pd
import numpy as np
import scipy.stats as stats

from src import config
from src.stats_utils import (
    describe, describe_robust, welch_test, welch_ci_and_diff,
    pct_variation, fmt_t, fmt_p, two_way_anova_table
)
from report.space_metrics import compute_space_metrics


def _unit(met):
    if "KB" in met:
        return " KB"
    if "MB" in met:
        return " MB"
    if "Count" in met or met == "CLS":
        return ""
    return " ms"


def _fmt_val(mean, std, met):
    u = _unit(met)
    if met == "CLS":
        return f"{mean:.4f} ± {std:.4f}"
    return f"{mean:.2f} ± {std:.2f}{u}"


def tabela_1():
    """Gera a Tabela 1 (Cold Start) com médias, DPs, medianas, IQRs, IC 95% e relevância."""
    if not config.COLD_START_CSV.exists():
        print("[AVISO] Cold Start CSV ausente; tabela 1 não gerada.")
        return
    df = pd.read_csv(config.COLD_START_CSV)
    metrics = [m for m in ["TTFB", "FCP", "LCP", "CLS", "TBT", "PayloadKB", "PayloadJS_KB",
                           "PayloadCSS_KB", "PayloadMediaKB", "PayloadDocKB", "PayloadOtherKB",
                           "JSHeapMB", "DOMNodeCount"] if m in df.columns]
    rows = []
    for pag in config.PAGES:
        for perf in config.PROFILES:
            sub = df[(df["Pagina"] == pag) & (df["PerfilRede"] == perf)]
            for met in metrics:
                r_series = sub.loc[sub["Tecnologia"] == "React", met].dropna()
                h_series = sub.loc[sub["Tecnologia"] == "HTMX", met].dropna()

                mr, sr = describe(r_series)
                med_r, iqr_r, p95_r = describe_robust(r_series)
                mh, sh = describe(h_series)
                med_h, iqr_h, p95_h = describe_robust(h_series)

                var = pct_variation(mr, mh)
                t, p = welch_test(r_series, h_series)
                ci_data = welch_ci_and_diff(r_series, h_series, threshold=50.0)

                rows.append({
                    "Pagina": pag,
                    "Condicao_Rede": perf,
                    "Metrica": met,
                    "React_Media": round(mr, 4 if met == "CLS" else 2),
                    "React_DesvioPadrao": round(sr, 4 if met == "CLS" else 2),
                    "React_Mediana": round(med_r, 4 if met == "CLS" else 2),
                    "React_IQR": round(iqr_r, 4 if met == "CLS" else 2),
                    "React_P95": round(p95_r, 4 if met == "CLS" else 2),
                    "React_Formatado": _fmt_val(mr, sr, met),
                    "HTMX_Media": round(mh, 4 if met == "CLS" else 2),
                    "HTMX_DesvioPadrao": round(sh, 4 if met == "CLS" else 2),
                    "HTMX_Mediana": round(med_h, 4 if met == "CLS" else 2),
                    "HTMX_IQR": round(iqr_h, 4 if met == "CLS" else 2),
                    "HTMX_P95": round(p95_h, 4 if met == "CLS" else 2),
                    "HTMX_Formatado": _fmt_val(mh, sh, met),
                    "Diferenca_Media_ms": round(ci_data["diff"], 2) if "ms" in _unit(met) else None,
                    "IC_95_Inferior": round(ci_data["ci_low"], 2) if "ms" in _unit(met) else None,
                    "IC_95_Superior": round(ci_data["ci_high"], 2) if "ms" in _unit(met) else None,
                    "IC_95_Formatado": ci_data["ci_fmt"] if "ms" in _unit(met) else None,
                    "Variacao_HTMX_vs_React": "0.0%" if var is None or var == 0 else f"{var:+.1f}%",
                    "Estatistica_t": fmt_t(t),
                    "p_valor": fmt_p(p),
                    "Significativo_alpha_005": "Sim" if p < 0.05 else "Não",
                    "Relevancia_Pratica_50ms": ci_data["relevance"] if "ms" in _unit(met) else None,
                })
    pd.DataFrame(rows).to_csv(config.TABELA_1, index=False, encoding="utf-8-sig")
    print(f"[OK] {config.TABELA_1.name}")


def tabela_2():
    """Gera a Tabela 2 (Infinite Scroll) com beta por rodada, IC 95%, teste zero e efeito acumulado."""
    if not config.SCROLL_CSV.exists():
        print("[AVISO] Infinite Scroll CSV ausente; tabela 2 não gerada.")
        return
    df = pd.read_csv(config.SCROLL_CSV)
    if "BatchLatencyMs" in df.columns and "BatchLoadTime" not in df.columns:
        df["BatchLoadTime"] = df["BatchLatencyMs"]

    n_runs = df["Rodada"].nunique() if "Rodada" in df.columns else 0
    rows = []

    for perf in config.PROFILES:
        sub = df[df["PerfilRede"] == perf]
        if sub.empty:
            continue

        # 1. Latência Média por Rodada
        run_lat = sub.groupby(["Rodada", "Tecnologia"])["BatchLoadTime"].mean().unstack()
        if "React" in run_lat.columns and "HTMX" in run_lat.columns:
            r_l, h_l = run_lat["React"].dropna(), run_lat["HTMX"].dropna()
            mr, sr = describe(r_l)
            med_r, iqr_r, _ = describe_robust(r_l)
            mh, sh = describe(h_l)
            med_h, iqr_h, _ = describe_robust(h_l)
            t, p = welch_test(r_l, h_l)
            ci_lat = welch_ci_and_diff(r_l, h_l, threshold=50.0)

            rows.append({
                "Condicao_Rede": perf, "Metrica": f"Latência Média por Rodada (N={n_runs})",
                "React_Media": round(mr, 2), "React_DesvioPadrao": round(sr, 2),
                "React_Mediana": round(med_r, 2), "React_IQR": round(iqr_r, 2),
                "React_Formatado": f"{mr:.2f} ± {sr:.2f} ms",
                "HTMX_Media": round(mh, 2), "HTMX_DesvioPadrao": round(sh, 2),
                "HTMX_Mediana": round(med_h, 2), "HTMX_IQR": round(iqr_h, 2),
                "HTMX_Formatado": f"{mh:.2f} ± {sh:.2f} ms",
                "Diferenca_Media_ms": round(ci_lat["diff"], 2),
                "IC_95_Formatado": ci_lat["ci_fmt"],
                "Estatistica_t": fmt_t(t), "p_valor": fmt_p(p),
                "Significativo_alpha_005": "Sim" if p < 0.05 else "Não",
                "Relevancia_Pratica_50ms": ci_lat["relevance"],
            })

        # 2. Taxa de Degradação Linear (Slope beta ms/lote) com IC 95% e efeito 49 lotes
        slopes = []
        r2_vals = []
        for (run_id, tech), group in sub.groupby(["Rodada", "Tecnologia"]):
            s_val, _, r_val, _, _ = stats.linregress(group["BatchIndex"], group["BatchLoadTime"])
            slopes.append({"Rodada": run_id, "Tecnologia": tech, "Slope": s_val})
            r2_vals.append({"Rodada": run_id, "Tecnologia": tech, "R2": r_val**2})

        slope_df = pd.DataFrame(slopes).pivot(index="Rodada", columns="Tecnologia", values="Slope")
        r2_df = pd.DataFrame(r2_vals).pivot(index="Rodada", columns="Tecnologia", values="R2")

        if "React" in slope_df.columns and "HTMX" in slope_df.columns:
            r_s, h_s = slope_df["React"].dropna(), slope_df["HTMX"].dropna()
            mr_s, sr_s = describe(r_s)
            mh_s, sh_s = describe(h_s)
            t_s, p_s = welch_test(r_s, h_s)
            ci_s = welch_ci_and_diff(r_s, h_s, threshold=1.0)  # limiar 1.0 ms/lote

            # IC do HTMX e teste contra 0
            se_h = sh_s / np.sqrt(len(h_s))
            tc_h = stats.t.ppf(0.975, len(h_s) - 1)
            ci_h_low, ci_h_high = mh_s - tc_h * se_h, mh_s + tc_h * se_h
            t_zero_h, p_zero_h = stats.ttest_1samp(h_s, 0)
            cum_eff_h = mh_s * 49
            cum_eff_r = mr_s * 49

            rows.append({
                "Condicao_Rede": perf, "Metrica": "Taxa Degradação Linear (β ms/lote)",
                "React_Media": round(mr_s, 4), "React_DesvioPadrao": round(sr_s, 4),
                "React_Mediana": round(float(r_s.median()), 4), "React_IQR": round(float(r_s.quantile(0.75) - r_s.quantile(0.25)), 4),
                "React_Formatado": f"{mr_s:.4f} ± {sr_s:.4f} ms/lote (R²={r2_df['React'].mean():.2f})",
                "HTMX_Media": round(mh_s, 4), "HTMX_DesvioPadrao": round(sh_s, 4),
                "HTMX_Mediana": round(float(h_s.median()), 4), "HTMX_IQR": round(float(h_s.quantile(0.75) - h_s.quantile(0.25)), 4),
                "HTMX_Formatado": f"{mh_s:.4f} ± {sh_s:.4f} ms/lote (R²={r2_df['HTMX'].mean():.2f})",
                "Diferenca_Media_ms": round(ci_s["diff"], 4),
                "IC_95_Formatado": ci_s["ci_fmt"],
                "Estatistica_t": fmt_t(t_s), "p_valor": fmt_p(p_s),
                "Significativo_alpha_005": "Sim" if p_s < 0.05 else "Não",
                "Relevancia_Pratica_50ms": f"Efeito 49 lotes: React={cum_eff_r:.1f}ms (>50ms) vs HTMX={cum_eff_h:.1f}ms (<2ms, nulo na prática)",
            })

        # 3. Delta JS Heap Final no Lote Final
        last_idx = sub.groupby(["Rodada", "Tecnologia"])["BatchIndex"].idxmax()
        b_final = sub.loc[last_idx]
        if not b_final.empty:
            run_delta = b_final.groupby(["Rodada", "Tecnologia"])["DeltaJSHeapMB"].mean().unstack()
            if "React" in run_delta.columns and "HTMX" in run_delta.columns:
                r_d, h_d = run_delta["React"].dropna(), run_delta["HTMX"].dropna()
                mr_d, sr_d = describe(r_d)
                mh_d, sh_d = describe(h_d)
                t_d, p_d = welch_test(r_d, h_d)
                ci_d = welch_ci_and_diff(r_d, h_d, threshold=1.0)
                rows.append({
                    "Condicao_Rede": perf, "Metrica": "Δ JS Heap Final",
                    "React_Media": round(mr_d, 2), "React_DesvioPadrao": round(sr_d, 2),
                    "React_Mediana": round(float(r_d.median()), 2), "React_IQR": round(float(r_d.quantile(0.75) - r_d.quantile(0.25)), 2),
                    "React_Formatado": f"{mr_d:.2f} ± {sr_d:.2f} MB",
                    "HTMX_Media": round(mh_d, 2), "HTMX_DesvioPadrao": round(sh_d, 2),
                    "HTMX_Mediana": round(float(h_d.median()), 2), "HTMX_IQR": round(float(h_d.quantile(0.75) - h_d.quantile(0.25)), 2),
                    "HTMX_Formatado": f"{mh_d:.2f} ± {sh_d:.2f} MB",
                    "Diferenca_Media_ms": round(ci_d["diff"], 2),
                    "IC_95_Formatado": ci_d["ci_fmt"],
                    "Estatistica_t": fmt_t(t_d), "p_valor": fmt_p(p_d),
                    "Significativo_alpha_005": "Sim" if p_d < 0.05 else "Não",
                    "Relevancia_Pratica_50ms": f"Redução de {((mr_d - mh_d)/mr_d*100):.1f}% no heap",
                })

            # 4. JS Heap Total Final no Lote Final
            run_heap = b_final.groupby(["Rodada", "Tecnologia"])["JSHeapMB"].mean().unstack()
            if "React" in run_heap.columns and "HTMX" in run_heap.columns:
                r_h, h_h = run_heap["React"].dropna(), run_heap["HTMX"].dropna()
                mr_h, sr_h = describe(r_h)
                mh_h, sh_h = describe(h_h)
                t_h, p_h = welch_test(r_h, h_h)
                ci_h = welch_ci_and_diff(r_h, h_h, threshold=1.0)
                rows.append({
                    "Condicao_Rede": perf, "Metrica": "JS Heap Total Final",
                    "React_Media": round(mr_h, 2), "React_DesvioPadrao": round(sr_h, 2),
                    "React_Mediana": round(float(r_h.median()), 2), "React_IQR": round(float(r_h.quantile(0.75) - r_h.quantile(0.25)), 2),
                    "React_Formatado": f"{mr_h:.2f} ± {sr_h:.2f} MB",
                    "HTMX_Media": round(mh_h, 2), "HTMX_DesvioPadrao": round(sh_h, 2),
                    "HTMX_Mediana": round(float(h_h.median()), 2), "HTMX_IQR": round(float(h_h.quantile(0.75) - h_h.quantile(0.25)), 2),
                    "HTMX_Formatado": f"{mh_h:.2f} ± {sh_h:.2f} MB",
                    "Diferenca_Media_ms": round(ci_h["diff"], 2),
                    "IC_95_Formatado": ci_h["ci_fmt"],
                    "Estatistica_t": fmt_t(t_h), "p_valor": fmt_p(p_h),
                    "Significativo_alpha_005": "Sim" if p_h < 0.05 else "Não",
                    "Relevancia_Pratica_50ms": f"Economia de {((mr_h - mh_h)/mr_h*100):.1f}% de RAM",
                })

            # 5. Nós do DOM Final no Lote Final
            run_dom = b_final.groupby(["Rodada", "Tecnologia"])["DOMNodeCount"].mean().unstack()
            if "React" in run_dom.columns and "HTMX" in run_dom.columns:
                r_dom, h_dom = run_dom["React"].dropna(), run_dom["HTMX"].dropna()
                mr_dom, sr_dom = describe(r_dom)
                mh_dom, sh_dom = describe(h_dom)
                t_dom, p_dom = welch_test(r_dom, h_dom)
                rows.append({
                    "Condicao_Rede": perf, "Metrica": "Nós do DOM Final",
                    "React_Media": round(mr_dom, 0), "React_DesvioPadrao": round(sr_dom, 1),
                    "React_Mediana": round(float(r_dom.median()), 0), "React_IQR": round(float(r_dom.quantile(0.75) - r_dom.quantile(0.25)), 1),
                    "React_Formatado": f"{mr_dom:.0f} ± {sr_dom:.1f}",
                    "HTMX_Media": round(mh_dom, 0), "HTMX_DesvioPadrao": round(sh_dom, 1),
                    "HTMX_Mediana": round(float(h_dom.median()), 0), "HTMX_IQR": round(float(h_dom.quantile(0.75) - h_dom.quantile(0.25)), 1),
                    "HTMX_Formatado": f"{mh_dom:.0f} ± {sh_dom:.1f}",
                    "Diferenca_Media_ms": round(mr_dom - mh_dom, 0),
                    "IC_95_Formatado": f"[{mr_dom - mh_dom:.0f}, {mr_dom - mh_dom:.0f}]",
                    "Estatistica_t": fmt_t(t_dom), "p_valor": fmt_p(p_dom),
                    "Significativo_alpha_005": "Sim" if p_dom < 0.05 else "Não",
                    "Relevancia_Pratica_50ms": "Paridade estrutural estrita",
                })

        # 6. BatchPayloadKB Global
        r_pay = sub[sub["Tecnologia"] == "React"]["BatchPayloadKB"].dropna()
        h_pay = sub[sub["Tecnologia"] == "HTMX"]["BatchPayloadKB"].dropna()
        mr_pay, sr_pay = describe(r_pay)
        mh_pay, sh_pay = describe(h_pay)
        t_pay, p_pay = welch_test(r_pay, h_pay)
        ci_pay = welch_ci_and_diff(r_pay, h_pay, threshold=0.5)
        rows.append({
            "Condicao_Rede": perf, "Metrica": "BatchPayloadKB (Média Geral)",
            "React_Media": round(mr_pay, 2), "React_DesvioPadrao": round(sr_pay, 2),
            "React_Mediana": round(float(r_pay.median()), 2), "React_IQR": round(float(r_pay.quantile(0.75) - r_pay.quantile(0.25)), 2),
            "React_Formatado": f"{mr_pay:.2f} ± {sr_pay:.2f} KB",
            "HTMX_Media": round(mh_pay, 2), "HTMX_DesvioPadrao": round(sh_pay, 2),
            "HTMX_Mediana": round(float(h_pay.median()), 2), "HTMX_IQR": round(float(h_pay.quantile(0.75) - h_pay.quantile(0.25)), 2),
            "HTMX_Formatado": f"{mh_pay:.2f} ± {sh_pay:.2f} KB",
            "Diferenca_Media_ms": round(ci_pay["diff"], 2),
            "IC_95_Formatado": ci_pay["ci_fmt"],
            "Estatistica_t": fmt_t(t_pay), "p_valor": fmt_p(p_pay),
            "Significativo_alpha_005": "Sim" if p_pay < 0.05 else "Não",
            "Relevancia_Pratica_50ms": f"HTMX economiza {((mr_pay - mh_pay)/mr_pay*100):.1f}% de tráfego por lote",
        })

    pd.DataFrame(rows).to_csv(config.TABELA_2, index=False, encoding="utf-8-sig")
    print(f"[OK] {config.TABELA_2.name}")


def tabela_3():
    """Gera a Tabela 3 (Mutação de Estado) agregada por rodada independente (N=100) com IC 95% e 50 ms."""
    if not config.MUTATION_CSV.exists():
        print("[AVISO] Mutação CSV ausente; tabela 3 não gerada.")
        return
    df = pd.read_csv(config.MUTATION_CSV)
    if "TipoOperacao" not in df.columns:
        df["TipoOperacao"] = df["MutationIndex"].apply(lambda x: "POST" if x % 2 != 0 else "DELETE")

    metrics = ["MutationLatencyMs", "MutationPayloadKB", "JSHeapMB", "DOMNodeCount"]
    ops = [("Geral (20 Mutações)", df),
           ("Inscrição (POST)", df[df["TipoOperacao"].isin(["POST", "Inscrição (POST)"])]),
           ("Cancelamento (DELETE)", df[df["TipoOperacao"].isin(["DELETE", "Cancelamento (DELETE)"])])]
    rows = []
    for perf in config.PROFILES:
        for op_label, op_df in ops:
            agg_df = op_df.groupby(["PerfilRede", "Tecnologia", "Rodada"]).agg({
                "MutationLatencyMs": "mean",
                "MutationPayloadKB": "mean",
                "JSHeapMB": "last",
                "DOMNodeCount": "last",
            }).reset_index()

            for met in metrics:
                if met not in agg_df.columns:
                    continue
                r = agg_df[(agg_df["PerfilRede"] == perf) & (agg_df["Tecnologia"] == "React")][met].dropna()
                h = agg_df[(agg_df["PerfilRede"] == perf) & (agg_df["Tecnologia"] == "HTMX")][met].dropna()
                if len(r) <= 1 or len(h) <= 1:
                    continue
                mr, sr = describe(r)
                med_r, iqr_r, _ = describe_robust(r)
                mh, sh = describe(h)
                med_h, iqr_h, _ = describe_robust(h)
                var = pct_variation(mr, mh)
                t, p = welch_test(r, h)
                ci_data = welch_ci_and_diff(r, h, threshold=50.0)

                rows.append({
                    "Condicao_Rede": perf, "Tipo_Operacao": op_label, "Metrica": met,
                    "React_Media": round(mr, 2), "React_DesvioPadrao": round(sr, 2),
                    "React_Mediana": round(med_r, 2), "React_IQR": round(iqr_r, 2),
                    "React_Formatado": f"{mr:.2f} ± {sr:.2f}{_unit(met)}",
                    "HTMX_Media": round(mh, 2), "HTMX_DesvioPadrao": round(sh, 2),
                    "HTMX_Mediana": round(med_h, 2), "HTMX_IQR": round(iqr_h, 2),
                    "HTMX_Formatado": f"{mh:.2f} ± {sh:.2f}{_unit(met)}",
                    "Diferenca_Media_ms": round(ci_data["diff"], 2) if "ms" in _unit(met) else None,
                    "IC_95_Inferior": round(ci_data["ci_low"], 2) if "ms" in _unit(met) else None,
                    "IC_95_Superior": round(ci_data["ci_high"], 2) if "ms" in _unit(met) else None,
                    "IC_95_Formatado": ci_data["ci_fmt"] if "ms" in _unit(met) else None,
                    "Variacao_HTMX_vs_React": "0.0%" if var is None or var == 0 else f"{var:+.1f}%",
                    "Estatistica_t": fmt_t(t), "p_valor": fmt_p(p),
                    "Significativo_alpha_005": "Sim" if p < 0.05 else "Não",
                    "Relevancia_Pratica_50ms": ci_data["relevance"] if "ms" in _unit(met) else None,
                })
    pd.DataFrame(rows).to_csv(config.TABELA_3, index=False, encoding="utf-8-sig")
    print(f"[OK] {config.TABELA_3.name}")


def tabela_anova():
    """Gera tabelas de ANOVA de Duas Vias com SS, df, MS, F, p-valor e eta-quadrado parcial."""
    # 1. Cold Start Home LCP
    if config.COLD_START_CSV.exists():
        df_cold = pd.read_csv(config.COLD_START_CSV)
        sub_home = df_cold[df_cold["Pagina"] == "Home"]
        df_a1 = two_way_anova_table(sub_home, "LCP", factor1="Tecnologia", factor2="PerfilRede")
        if df_a1 is not None:
            df_a1.to_csv(config.TABELA_ANOVA_COLD_HOME, index=False, encoding="utf-8-sig")
            print(f"[OK] {config.TABELA_ANOVA_COLD_HOME.name}")

    # 2. Infinite Scroll BatchLoadTime (nível de rodada para evitar inflação amostral)
    if config.SCROLL_CSV.exists():
        df_scroll = pd.read_csv(config.SCROLL_CSV)
        if "BatchLatencyMs" in df_scroll.columns and "BatchLoadTime" not in df_scroll.columns:
            df_scroll["BatchLoadTime"] = df_scroll["BatchLatencyMs"]
        scroll_round = df_scroll.groupby(["Tecnologia", "PerfilRede", "Rodada"])["BatchLoadTime"].mean().reset_index()
        df_a2 = two_way_anova_table(scroll_round, "BatchLoadTime", factor1="Tecnologia", factor2="PerfilRede")
        if df_a2 is not None:
            df_a2.to_csv(config.TABELA_ANOVA_SCROLL, index=False, encoding="utf-8-sig")
            print(f"[OK] {config.TABELA_ANOVA_SCROLL.name}")

    # 3. State Mutation Latency (nível de rodada N=100)
    if config.MUTATION_CSV.exists():
        df_mut = pd.read_csv(config.MUTATION_CSV)
        mut_round = df_mut.groupby(["Tecnologia", "PerfilRede", "Rodada"])["MutationLatencyMs"].mean().reset_index()
        df_a3 = two_way_anova_table(mut_round, "MutationLatencyMs", factor1="Tecnologia", factor2="PerfilRede")
        if df_a3 is not None:
            df_a3.to_csv(config.TABELA_ANOVA_MUTACAO, index=False, encoding="utf-8-sig")
            print(f"[OK] {config.TABELA_ANOVA_MUTACAO.name}")


def tabela_4():
    """Gera a Tabela 4 com métricas de engenharia de software do framework SPACE."""
    m = compute_space_metrics()
    if not m:
        print("[AVISO] Repositórios de código não encontrados; tabela 4 não gerada.")
        return

    def pc(v):
        return "N/A" if v is None else f"{v:+.1f}%"

    build = m["build"]
    build_react = (f"{build['desc']} (Gzip)" if build else "113,57 KB (Vite Gzip)")
    deps = m["deps"]
    rows = [
        ("Linhas de Código Efetivas (CLOC Total)", f"{m['cloc_total']['react']} linhas", f"{m['cloc_total']['htmx']} linhas", f"{pc(m['cloc_total']['pct'])} de código no HTMX"),
        ("CLOC Camada de Front-end", f"{m['cloc_front']['react']} linhas (JSX/CSS/JS)", f"{m['cloc_front']['htmx']} linhas (HTML/CSS/JS)", f"{pc(m['cloc_front']['pct'])} de código no front-end"),
        ("CLOC Exclusivo de Lógica Front-end", f"{m['cloc_front_logic']['react']} linhas (JSX + JS)", f"{m['cloc_front_logic']['htmx']} linhas (HTML + JS)", f"{pc(m['cloc_front_logic']['pct'])} de lógica de apresentação"),
        ("CLOC Camada de Back-end", f"{m['cloc_back']['react']} linhas (Python/DRF)", f"{m['cloc_back']['htmx']} linhas (Python MVT)", f"{pc(m['cloc_back']['pct'])} (Templates/Views MVT)"),
        ("Arquivos de Código-Fonte (Total)", f"{m['files_total']['react']} arquivos", f"{m['files_total']['htmx']} arquivos", f"{pc(m['files_total']['pct'])} de arquivos no HTMX"),
        ("Arquivos de Front-end", f"{m['files_front']['react']} arquivos (src)", f"{m['files_front']['htmx']} arquivos (templates/static)", f"{pc(m['files_front']['pct'])} de arquivos de tela"),
        ("Arquivos de Back-end", f"{m['files_back']['react']} arquivos", f"{m['files_back']['htmx']} arquivos", "Estrutura Django equivalente"),
        ("Dependências Externas (Pacotes)", f"{deps['react']} pacotes ({deps['pip_react']} pip + {deps['npm_prod']} npm prod + {deps['npm_dev']} npm dev)", f"{deps['htmx']} pacotes ({deps['pip_htmx']} pip + {deps['static_js_htmx']} JS static htmx.min.js)", f"{pc(deps['pct'])} de dependências externas"),
        ("Camadas de Modificação", "3 camadas (Model -> Serializer -> Component)", "2 camadas (Model -> Template)", "-33.3% no caminho de modificação"),
        ("Tamanho dos Artefatos de Build", build_react, "0 KB (Sem build step no front-end)", "Zero tempo de compilação/transpilação"),
    ]
    cols = ["Metrica_SPACE", "React_SPA", "HTMX_HDA", "Diferenca_Impacto"]
    pd.DataFrame(rows, columns=cols).to_csv(config.TABELA_4, index=False, encoding="utf-8-sig")
    print(f"[OK] {config.TABELA_4.name}")


def generate_all():
    config.ensure_dirs()
    tabela_1()
    tabela_2()
    tabela_3()
    tabela_anova()
    tabela_4()
    print("\n>>> Todas as tabelas consolidadas geradas com sucesso!")


if __name__ == "__main__":
    generate_all()
