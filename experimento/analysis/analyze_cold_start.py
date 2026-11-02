"""Análise estatística do Cold Start: descritivas, teste t de Welch e ANOVA de duas vias."""
import numpy as np
from src.stats_utils import (
    describe, welch_test, fmt_t, fmt_p, pct_variation, two_way_anova
)
from src import config

METRICS = ["TTFB", "FCP", "LCP", "CLS", "TBT", "PayloadKB", "PayloadJS_KB",
           "PayloadCSS_KB", "PayloadMediaKB", "PayloadDocKB", "JSHeapMB", "DOMNodeCount"]


def unit(met):
    if "KB" in met:
        return " KB"
    if "MB" in met:
        return " MB"
    if "Count" in met or met == "CLS":
        return ""
    return " ms"


def run(csv_path=config.COLD_START_CSV, out_md=config.COLD_START_MD):
    import pandas as pd
    if not csv_path.exists():
        print(f"[ERRO] {csv_path} não encontrado.")
        return
    df = pd.read_csv(csv_path)
    md = ["# Relatório de Resultados Estatísticos: React vs. HTMX\n",
          "Este relatório resume a análise comparativa entre as tecnologias React (SPA) e HTMX (HDA) com base nas coletas realizadas.\n"]

    md += ["## 1. Estatísticas Descritivas\n",
           "| Página | Perfil de Rede | Métrica | React (Média ± DP) | HTMX (Média ± DP) |",
           "| :--- | :--- | :--- | :--- | :--- |"]
    for pag in config.PAGES:
        for perf in config.PROFILES:
            for met in METRICS:
                if met not in df.columns:
                    continue
                r = _sub(df, pag, perf, "React", met)
                h = _sub(df, pag, perf, "HTMX", met)
                if r.empty and h.empty:
                    continue
                mr, sr = describe(r)
                mh, sh = describe(h)
                u = unit(met)
                if met == "CLS":
                    sr_row, sh_row = f"{mr:.4f} ± {sr:.4f}", f"{mh:.4f} ± {sh:.4f}"
                else:
                    sr_row, sh_row = f"{mr:.2f} ± {sr:.2f}{u}", f"{mh:.2f} ± {sh:.2f}{u}"
                md.append(f"| {pag} | {perf} | {met} | {sr_row} | {sh_row} |")
    md.append("\n---\n")

    md += ["## 2. Teste t de Welch (Comparação Direta de Médias)\n",
           "| Página | Perfil de Rede | Métrica | Estatística $t$ | $p$-valor | Significativo ($\\alpha=0.05$) |",
           "| :--- | :--- | :--- | :--- | :--- | :--- |"]
    for pag in config.PAGES:
        for perf in config.PROFILES:
            for met in METRICS:
                if met not in df.columns:
                    continue
                r = _sub(df, pag, perf, "React", met).dropna()
                h = _sub(df, pag, perf, "HTMX", met).dropna()
                if len(r) <= 1 or len(h) <= 1:
                    md.append(f"| {pag} | {perf} | {met} | N/A | N/A | N/A |")
                    continue
                t, p = welch_test(r, h)
                sig = "Sim (p < 0.05)" if p < 0.05 else "Não"
                md.append(f"| {pag} | {perf} | {met} | {fmt_t(t)} | {fmt_p(p)} | {sig} |")
    md.append("\n---\n")

    md += ["## 3. Análise de Variância de Duas Vias (Two-Way ANOVA)\n",
           "A ANOVA avalia o impacto de **Tecnologia** (React vs. HTMX), de **Rede** " 
           "(NoThrottling, Fast4G, Slow4G) e do **Efeito de Interação** entre os dois fatores.\n"]
    for met in METRICS:
        if met not in df.columns:
            continue
        md.append(f"### ANOVA para a Métrica: {met}\n")
        for pag in config.PAGES:
            anova = two_way_anova(df[(df["Pagina"] == pag)], met)
            if not anova:
                continue
            md.append(f"#### Página: {pag}")
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
    print(f"[OK] Relatório Cold Start salvo em: {out_md}")


def _sub(df, pag, perf, tech, met):
    return df.loc[(df["Pagina"] == pag) & (df["PerfilRede"] == perf) & (df["Tecnologia"] == tech), met]


if __name__ == "__main__":
    run()
