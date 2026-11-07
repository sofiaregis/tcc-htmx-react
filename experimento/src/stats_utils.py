"""Utilitários estatísticos compartilhados: descritivas, robustas, Welch, IC 95% e ANOVA de duas vias."""
import warnings

import numpy as np
import scipy.stats as stats
import pandas as pd


def describe(series):
    """Retorna (média, desvio padrão amostral) de uma série."""
    s = np.asarray(series, dtype=float)
    s = s[~np.isnan(s)]
    if s.size == 0:
        return float("nan"), float("nan")
    return float(s.mean()), float(s.std(ddof=1))


def describe_robust(series):
    """Retorna (mediana, IQR, P95) de uma série."""
    s = np.asarray(series, dtype=float)
    s = s[~np.isnan(s)]
    if s.size == 0:
        return float("nan"), float("nan"), float("nan")
    med = float(np.median(s))
    q25, q75 = float(np.percentile(s, 25)), float(np.percentile(s, 75))
    iqr = q75 - q25
    p95 = float(np.percentile(s, 95))
    return med, iqr, p95


def welch_test(a, b):
    """Teste t de Welch para duas amostras independentes. Retorna (t, p)."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[~np.isnan(a)]
    b = b[~np.isnan(b)]
    if a.size == 0 or b.size == 0:
        return float("nan"), float("nan")
    if a.std() == 0 and b.std() == 0:
        return (0.0, 1.0) if a.mean() == b.mean() else (9999.0, 0.0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        t, p = stats.ttest_ind(a, b, equal_var=False)
    if np.isnan(t):
        return 0.0, 1.0
    if np.isinf(t):
        return (9999.0 if t > 0 else -9999.0), 0.0
    return float(t), float(p)


def welch_ci_and_diff(a, b, alpha=0.05, threshold=50.0):
    """Calcula diferenca das medias (a - b), erro-padrao de Welch, graus de liberdade,
    intervalo de confianca (1 - alpha) e classificacao frente ao limiar pratico (ex: 50 ms)."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[~np.isnan(a)]
    b = b[~np.isnan(b)]
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return {
            "diff": 0.0, "se": 0.0, "df": 0.0, "ci_low": 0.0, "ci_high": 0.0,
            "ci_fmt": "N/A", "relevance": "N/A"
        }
    ma, mb = float(a.mean()), float(b.mean())
    sa2, sb2 = float(a.var(ddof=1)), float(b.var(ddof=1))
    diff = ma - mb
    se = np.sqrt(sa2 / na + sb2 / nb)
    if se == 0:
        return {
            "diff": diff, "se": 0.0, "df": na + nb - 2, "ci_low": diff, "ci_high": diff,
            "ci_fmt": f"[{diff:.2f}, {diff:.2f}]",
            "relevance": f"Equivalente na Prática (±{threshold:.0f} ms)" if abs(diff) <= threshold else "Diferença Relevante"
        }
    df = (sa2 / na + sb2 / nb)**2 / ((sa2 / na)**2 / (na - 1) + (sb2 / nb)**2 / (nb - 1))
    t_crit = float(stats.t.ppf(1 - alpha / 2, df))
    ci_low = diff - t_crit * se
    ci_high = diff + t_crit * se

    if ci_low > threshold:
        rel = f"Diferença Relevante (> {threshold:.0f} ms)"
    elif ci_high < -threshold:
        rel = f"Diferença Relevante a favor React (< -{threshold:.0f} ms)"
    elif ci_low >= -threshold and ci_high <= threshold:
        rel = f"Equivalente na Prática (±{threshold:.0f} ms)"
    else:
        rel = "Inconclusivo (cruza limiar)"

    return {
        "diff": diff, "se": se, "df": df, "ci_low": ci_low, "ci_high": ci_high,
        "ci_fmt": f"[{ci_low:.2f}, {ci_high:.2f}]", "relevance": rel
    }


def cohens_d(a, b):
    """Calcula o tamanho de efeito d de Cohen com desvio padrão combinado (pooled)."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[~np.isnan(a)]
    b = b[~np.isnan(b)]
    na, nb = len(a), len(b)
    if na < 2 or nb < 2:
        return 0.0
    sa2 = a.var(ddof=1)
    sb2 = b.var(ddof=1)
    pooled_sd = np.sqrt(((na - 1) * sa2 + (nb - 1) * sb2) / (na + nb - 2))
    if pooled_sd == 0:
        return 0.0
    return float((a.mean() - b.mean()) / pooled_sd)


def fmt_t(t):
    if abs(t) >= 9000:
        return "∞" if t > 0 else "-∞"
    return f"{t:.4f}"


def fmt_d(d):
    if d is None or (isinstance(d, float) and np.isnan(d)):
        return "N/A"
    return f"{d:.2f}"


def fmt_p(p):
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return "N/A"
    return "< 0.0001" if p < 0.0001 else f"{p:.4f}"


def pct_variation(base, other):
    """Variação percentual de `other` em relação a `base` (%), ou None se base == 0."""
    if base == 0:
        return None
    return ((other - base) / base) * 100


def two_way_anova_table(df, metric, factor1="Tecnologia", factor2="PerfilRede"):
    """Calcula tabela de ANOVA 2-vias balanceada com SS, df, MS, F, p-valor e eta-quadrado parcial."""
    sub = df.dropna(subset=[metric, factor1, factor2])
    if len(sub) <= 10:
        return None

    levels1 = sorted(sub[factor1].unique())
    levels2 = sorted(sub[factor2].unique())
    a = len(levels1)
    b = len(levels2)

    counts = sub.groupby([factor1, factor2])[metric].count()
    n = int(counts.min())

    cell_means = sub.groupby([factor1, factor2])[metric].mean().unstack()
    row_means = sub.groupby(factor1)[metric].mean()
    col_means = sub.groupby(factor2)[metric].mean()
    grand_mean = sub[metric].mean()

    ss_a = b * n * sum((row_means - grand_mean)**2)
    ss_b = a * n * sum((col_means - grand_mean)**2)

    ss_ab = 0.0
    for l1 in levels1:
        for l2 in levels2:
            mu_ij = cell_means.loc[l1, l2]
            mu_i = row_means[l1]
            mu_j = col_means[l2]
            ss_ab += n * (mu_ij - mu_i - mu_j + grand_mean)**2

    ss_resid = 0.0
    for (l1, l2), grp in sub.groupby([factor1, factor2]):
        mu_ij = cell_means.loc[l1, l2]
        ss_resid += sum((grp[metric] - mu_ij)**2)

    df_a = a - 1
    df_b = b - 1
    df_ab = (a - 1) * (b - 1)
    df_resid = a * b * (n - 1)

    ms_a = ss_a / df_a if df_a > 0 else 0.0
    ms_b = ss_b / df_b if df_b > 0 else 0.0
    ms_ab = ss_ab / df_ab if df_ab > 0 else 0.0
    ms_resid = ss_resid / df_resid if df_resid > 0 else 0.0

    f_a = ms_a / ms_resid if ms_resid > 0 else 0.0
    f_b = ms_b / ms_resid if ms_resid > 0 else 0.0
    f_ab = ms_ab / ms_resid if ms_resid > 0 else 0.0

    p_a = 1.0 - stats.f.cdf(f_a, df_a, df_resid)
    p_b = 1.0 - stats.f.cdf(f_b, df_b, df_resid)
    p_ab = 1.0 - stats.f.cdf(f_ab, df_ab, df_resid)

    eta_a = ss_a / (ss_a + ss_resid) if (ss_a + ss_resid) > 0 else 0.0
    eta_b = ss_b / (ss_b + ss_resid) if (ss_b + ss_resid) > 0 else 0.0
    eta_ab = ss_ab / (ss_ab + ss_resid) if (ss_ab + ss_resid) > 0 else 0.0

    rows = [
        {"Fonte": factor1, "SS": ss_a, "df": df_a, "MS": ms_a, "F": f_a, "p_valor": p_a, "eta_sq_partial": eta_a},
        {"Fonte": factor2, "SS": ss_b, "df": df_b, "MS": ms_b, "F": f_b, "p_valor": p_b, "eta_sq_partial": eta_b},
        {"Fonte": f"Interação ({factor1} * {factor2})", "SS": ss_ab, "df": df_ab, "MS": ms_ab, "F": f_ab, "p_valor": p_ab, "eta_sq_partial": eta_ab},
        {"Fonte": "Resíduos", "SS": ss_resid, "df": df_resid, "MS": ms_resid, "F": None, "p_valor": None, "eta_sq_partial": None},
    ]
    return pd.DataFrame(rows)


def anova_diagnostics_row(df, metric, label, factor1="Tecnologia", factor2="PerfilRede"):
    """Calcula diagnosticos de pressupostos (Levene, Shapiro-Wilk) e auditoria robusta HC3."""
    import statsmodels.formula.api as smf
    from statsmodels.stats.anova import anova_lm

    sub = df.dropna(subset=[metric, factor1, factor2])
    grouped = sub.groupby([factor1, factor2])[metric]
    samples = [g.values for _, g in grouped]

    # 1. Homocedasticidade (Levene centrado na mediana / Brown-Forsythe)
    w_bf, p_bf = stats.levene(*samples, center="median")

    # 2. Ajuste OLS e Normalidade dos Resíduos
    formula = f"{metric} ~ C({factor1}) * C({factor2})"
    model = smf.ols(formula, data=sub).fit()
    w_sh, p_sh = stats.shapiro(model.resid)

    # 3. ANOVA Clássica
    a_classic = anova_lm(model, typ=2)
    f_tec = a_classic.loc[f"C({factor1})", "F"]
    f_rede = a_classic.loc[f"C({factor2})", "F"]
    f_int = a_classic.loc[f"C({factor1}):C({factor2})", "F"]

    # 4. Erros-padrão robustos HC3 (White-MacKinnon)
    model_hc3 = smf.ols(formula, data=sub).fit(cov_type="HC3")
    terms_tec = [t for t in model_hc3.params.index if f"C({factor1})" in t and ":" not in t]
    w_tec = model_hc3.wald_test(terms_tec, scalar=True)
    f_tec_hc3 = float(np.squeeze(w_tec.statistic))
    p_tec_hc3 = float(np.squeeze(w_tec.pvalue))

    terms_rede = [t for t in model_hc3.params.index if f"C({factor2})" in t and ":" not in t]
    w_rede = model_hc3.wald_test(terms_rede, scalar=False)
    f_rede_hc3 = float(np.squeeze(w_rede.statistic))
    p_rede_hc3 = float(np.squeeze(w_rede.pvalue))

    terms_int = [t for t in model_hc3.params.index if ":" in t]
    w_int = model_hc3.wald_test(terms_int, scalar=False)
    f_int_hc3 = float(np.squeeze(w_int.statistic))
    p_int_hc3 = float(np.squeeze(w_int.pvalue))

    return {
        "Bateria_Cenario": label,
        "Metrica": metric,
        "Levene_W": round(w_bf, 4),
        "Levene_p": "< 0.0001" if p_bf < 0.0001 else f"{p_bf:.4f}",
        "Homocedasticidade": "Rejeitada (p < 0.05)" if p_bf < 0.05 else "Atendida (p >= 0.05)",
        "Shapiro_W": round(w_sh, 4),
        "Shapiro_p": "< 0.0001" if p_sh < 0.0001 else f"{p_sh:.4f}",
        "Normalidade_Residuos": "Rejeitada (p < 0.05)" if p_sh < 0.05 else "Atendida (p >= 0.05)",
        "F_Tecnologia_Classico": round(f_tec, 2),
        "F_Tecnologia_HC3": round(f_tec_hc3, 2),
        "p_Tecnologia_HC3": "< 0.0001" if p_tec_hc3 < 0.0001 else f"{p_tec_hc3:.4f}",
        "F_Rede_Classico": round(f_rede, 2),
        "F_Rede_HC3": round(f_rede_hc3, 2),
        "p_Rede_HC3": "< 0.0001" if p_rede_hc3 < 0.0001 else f"{p_rede_hc3:.4f}",
        "F_Interacao_Classico": round(f_int, 2),
        "F_Interacao_HC3": round(f_int_hc3, 2),
        "p_Interacao_HC3": "< 0.0001" if p_int_hc3 < 0.0001 else f"{p_int_hc3:.4f}",
    }
