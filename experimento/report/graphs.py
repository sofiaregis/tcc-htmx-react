"""Módulo para geração padronizada e modular de gráficos acadêmicos do EventFlow.

Gera figuras em alta resolução (300 DPI) com identidade visual consistente:
- React 19 (SPA): Azul (#3B82F6)
- HTMX 2 (HDA): Verde (#10B981)
- Modo Híbrido Inteligente (Padrão):
  * Métricas Estocásticas (Latências: TTFB, FCP, LCP, Mutação de Estado): Box-plots (Mediana, Faixa Interquartil, Média e Outliers)
  * Métricas Determinísticas / Volumes (Payload Total, Payload JS, JS Heap, TBT): Gráficos de Barra com anotação de mediana no topo
  * Séries Longitudinais (Infinite Scroll): Trajetórias com Mediana e Faixa Interquartil (IQR)
- Modos suportados:
  * 'hybrid' (padrão): Combina box-plots para latências e barras para volumes determinísticos.
  * 'bar': Gera apenas os gráficos originais de barras clássicos do TCC (prefixo bar_).
  * 'boxplot': Gera estritamente box-plots para todas as métricas (prefixo boxplot_).
  * 'all': Gera ambos os conjuntos lado a lado para permitir comparação visual imediata.
"""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
import pandas as pd
import seaborn as sns

from src import config

PALETTE = {
    "React": "#3B82F6",
    "HTMX": "#10B981",
    "React 19 (SPA)": "#3B82F6",
    "HTMX 2 (HDA)": "#10B981",
}

PERFIS_DESC = {
    "NoThrottling": "Sem Restrição (Rede Local / Ideal)",
    "Fast4G": "Rede Fast 4G (10 Mbps, 40 ms RTT)",
    "Slow4G": "Rede Slow 4G (4 Mbps, 100 ms RTT)",
}


def set_academic_style():
    """Configura tema visual acadêmico e tipografia padronizada."""
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "xtick.labelsize": 10.5,
        "ytick.labelsize": 10.5,
        "legend.fontsize": 11,
        "figure.titlesize": 14,
    })


def _padronizar(df: pd.DataFrame) -> pd.DataFrame:
    """Padroniza os nomes das tecnologias no DataFrame."""
    df = df.copy()
    if "Tecnologia" in df.columns:
        df["Tecnologia"] = df["Tecnologia"].replace({
            "React": "React 19 (SPA)",
            "HTMX": "HTMX 2 (HDA)"
        })
    return df


def _hue_order() -> list[str]:
    """Ordem canônica das tecnologias para legendas e paletas."""
    return ["React 19 (SPA)", "HTMX 2 (HDA)"]


def _fmt_num(val: float, unit_str: str = "") -> str:
    """Formata valores numéricos com separadores no padrão pt-BR."""
    if val >= 100:
        txt = f"{val:,.0f} {unit_str}"
    elif val >= 10:
        txt = f"{val:.1f} {unit_str}"
    else:
        txt = f"{val:.2f} {unit_str}"
    return txt.strip().replace(",", "X").replace(".", ",").replace("X", ".")


def _anotar_barras(
    ax: plt.Axes,
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    hue_col: str,
    x_order: list,
    hue_order: list,
    unit_str: str = "",
):
    """Insere anotações de mediana sobre cada barra com ajuste de limite vertical."""
    stats = df.groupby([x_col, hue_col])[y_col].agg(
        median="median",
        p75=lambda x: np.percentile(x.dropna(), 75) if len(x.dropna()) > 0 else np.nan
    ).reset_index()

    max_top = 0.0
    for c_idx, container in enumerate(ax.containers):
        if c_idx >= len(hue_order):
            continue
        hue = hue_order[c_idx]
        for b_idx, bar in enumerate(container):
            if b_idx >= len(x_order):
                continue
            row = stats[(stats[x_col] == x_order[b_idx]) & (stats[hue_col] == hue)]
            if row.empty:
                continue
            med_val = row["median"].values[0]
            p75_val = row["p75"].values[0]
            if np.isnan(p75_val):
                p75_val = med_val
            y_pos = max(med_val, p75_val)
            max_top = max(max_top, y_pos)
            txt = _fmt_num(med_val, unit_str)
            ax.annotate(
                txt,
                (bar.get_x() + bar.get_width() / 2.0, y_pos),
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
                color="#111111",
                xytext=(0, 4),
                textcoords="offset points",
            )
    if max_top > 0:
        ax.set_ylim(0, max_top * 1.30)


def _bar_chart(
    df: pd.DataFrame,
    out_path: Path,
    title: str,
    ylabel: str,
    x_col: str,
    x_order: list,
    y_col: str,
    unit_str: str = "",
    xlabel: str = None,
    xticklabels: list = None,
    figsize: tuple = (8.0, 4.8),
    ylim_padding: float = 1.18,
):
    """Gera um gráfico de barras acadêmico padronizado com P50 e IQR."""
    fig, ax = plt.subplots(figsize=figsize, dpi=300)
    sns.barplot(
        data=df,
        x=x_col,
        y=y_col,
        order=x_order,
        hue="Tecnologia",
        hue_order=_hue_order(),
        palette=PALETTE,
        estimator=np.median,
        errorbar=("pi", 50),
        capsize=0.1,
        err_kws={"linewidth": 1.2, "color": "#333333"},
        ax=ax,
    )
    ax.set_title(title, pad=12, fontweight="bold")

    if xlabel is None:
        xlabel = "Página da Aplicação (EventFlow)" if x_col == "Pagina" else "Condição de Rede"
    ax.set_xlabel(xlabel, fontweight="bold", labelpad=8)
    ax.set_ylabel(ylabel, fontweight="bold", labelpad=8)
    ax.grid(True, linestyle="--", alpha=0.6, axis="y")

    if xticklabels is not None:
        ax.set_xticks(range(len(x_order)))
        ax.set_xticklabels(xticklabels, fontweight="bold")
    else:
        plt.setp(ax.get_xticklabels(), rotation=0, ha="center", fontweight="bold")

    _anotar_barras(ax, df, x_col, y_col, "Tecnologia", x_order, _hue_order(), unit_str)
    ax.legend(
        title="Tecnologia",
        title_fontsize="10",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.20),
        ncol=2,
        frameon=True,
        framealpha=0.95,
    )
    ax.set_ylim(0, ax.get_ylim()[1] * ylim_padding)
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def _box_chart(
    df: pd.DataFrame,
    out_path: Path,
    title: str,
    ylabel: str,
    x_col: str,
    x_order: list,
    y_col: str,
    unit_str: str = "",
    xlabel: str = None,
    xticklabels: list = None,
    figsize: tuple = (8.2, 5.0),
    show_samples: bool = False,
    show_fliers: bool = True,
):
    """Gera um box-plot acadêmico padronizado com mediana, média, quartis, outliers e dispersão opcional."""
    fig, ax = plt.subplots(figsize=figsize, dpi=300)
    sns.boxplot(
        data=df,
        x=x_col,
        y=y_col,
        order=x_order,
        hue="Tecnologia",
        hue_order=_hue_order(),
        palette=PALETTE,
        ax=ax,
        width=0.55,
        showfliers=show_fliers,
        fliersize=3.5 if show_fliers else 0,
        flierprops={
            "marker": "o",
            "markerfacecolor": "#6B7280",
            "markeredgecolor": "none",
            "alpha": 0.6,
        } if show_fliers else {},
        boxprops={"alpha": 0.90, "linewidth": 1.2, "edgecolor": "#1F2937"},
        whiskerprops={"linewidth": 1.2, "color": "#374151"},
        capprops={"linewidth": 1.2, "color": "#374151"},
        medianprops={"linewidth": 2.2, "color": "#111827"},
        showmeans=True,
        meanprops={
            "marker": "D",
            "markerfacecolor": "white",
            "markeredgecolor": "#111827",
            "markersize": 5.5,
        },
    )
    if show_samples:
        sns.stripplot(
            data=df,
            x=x_col,
            y=y_col,
            order=x_order,
            hue="Tecnologia",
            hue_order=_hue_order(),
            dodge=True,
            jitter=0.15,
            alpha=0.45,
            size=4.0,
            palette=PALETTE,
            ax=ax,
            legend=False,
        )
    ax.set_title(title, pad=12, fontweight="bold")

    if xlabel is None:
        xlabel = "Página da Aplicação (EventFlow)" if x_col == "Pagina" else "Condição de Rede"
    ax.set_xlabel(xlabel, fontweight="bold", labelpad=8)
    ax.set_ylabel(ylabel, fontweight="bold", labelpad=8)
    ax.grid(True, linestyle="--", alpha=0.6, axis="y")

    vals = df[y_col].dropna()
    if not vals.empty:
        if not show_fliers:
            uppers = []
            lowers = []
            for (x_val, t_val), grp in df.groupby([x_col, "Tecnologia"]):
                t_vals = grp[y_col].dropna()
                if not t_vals.empty:
                    q25 = t_vals.quantile(0.25)
                    q75 = t_vals.quantile(0.75)
                    iqr = q75 - q25
                    lowers.append(max(t_vals.min(), q25 - 1.5 * iqr))
                    uppers.append(min(t_vals.max(), q75 + 1.5 * iqr))
            y_min = min(lowers) if lowers else vals.min()
            y_max = max(uppers) if uppers else vals.max()
        else:
            y_min = vals.min()
            y_max = vals.max()
        span = max(y_max - y_min, 1.0)
        if y_min >= 0 and y_min > span * 0.8:
            ax.set_ylim(max(0, y_min - span * 0.12), y_max + span * 0.12)
        elif y_min >= 0:
            ax.set_ylim(bottom=0, top=y_max + span * 0.12)

    if xticklabels is not None:
        ax.set_xticks(range(len(x_order)))
        ax.set_xticklabels(xticklabels, fontweight="bold")
    else:
        plt.setp(ax.get_xticklabels(), rotation=0, ha="center", fontweight="bold")

    custom_handles = [
        Patch(facecolor=PALETTE["React 19 (SPA)"], edgecolor="#374151", label="React 19 (SPA)"),
        Patch(facecolor=PALETTE["HTMX 2 (HDA)"], edgecolor="#374151", label="HTMX 2 (HDA)"),
        Line2D([0], [0], color="#111827", lw=2.2, label="Mediana (P50)"),
        Line2D(
            [0],
            [0],
            marker="D",
            color="none",
            markerfacecolor="white",
            markeredgecolor="#111827",
            markersize=5.5,
            label=r"Média ($\bar{x}$)",
        ),
    ]
    if show_samples:
        custom_handles.append(
            Line2D(
                [0],
                [0],
                marker="o",
                color="none",
                markerfacecolor="#6B7280",
                markeredgecolor="none",
                markersize=4.5,
                alpha=0.6,
                label=r"Amostras ($N$)",
            )
        )
    ax.legend(
        handles=custom_handles,
        title="Legenda",
        title_fontsize="10",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.20),
        ncol=len(custom_handles),
        frameon=True,
        framealpha=0.95,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def _box_chart_faceted(
    df: pd.DataFrame,
    out_path: Path,
    title: str,
    ylabel: str,
    facet_col: str,
    facet_order: list,
    facet_labels: dict,
    y_col: str,
    unit_str: str = "",
    figsize: tuple = (11.5, 5.2),
    show_samples: bool = False,
    show_fliers: bool = True,
):
    """Gera gráficos box-plot em painéis facetados com eixos Y independentes e legenda externa."""
    fig, axes = plt.subplots(1, len(facet_order), figsize=figsize, dpi=300, sharey=False)
    if len(facet_order) == 1:
        axes = [axes]

    for idx, facet_val in enumerate(facet_order):
        ax = axes[idx]
        sub_df = df[df[facet_col] == facet_val]

        if not sub_df.empty:
            sns.boxplot(
                data=sub_df,
                x="Tecnologia",
                y=y_col,
                order=_hue_order(),
                hue="Tecnologia",
                palette=PALETTE,
                legend=False,
                ax=ax,
                width=0.48,
                showfliers=show_fliers,
                fliersize=3.5 if show_fliers else 0,
                flierprops={
                    "marker": "o",
                    "markerfacecolor": "#6B7280",
                    "markeredgecolor": "none",
                    "alpha": 0.6,
                } if show_fliers else {},
                boxprops={"alpha": 0.90, "linewidth": 1.2, "edgecolor": "#1F2937"},
                whiskerprops={"linewidth": 1.2, "color": "#374151"},
                capprops={"linewidth": 1.2, "color": "#374151"},
                medianprops={"linewidth": 2.2, "color": "#111827"},
                showmeans=True,
                meanprops={
                    "marker": "D",
                    "markerfacecolor": "white",
                    "markeredgecolor": "#111827",
                    "markersize": 5.5,
                },
            )
            if show_samples:
                sns.stripplot(
                    data=sub_df,
                    x="Tecnologia",
                    y=y_col,
                    order=_hue_order(),
                    hue="Tecnologia",
                    palette=PALETTE,
                    legend=False,
                    ax=ax,
                    size=4.0,
                    jitter=0.15,
                    alpha=0.45,
                    edgecolor="none",
                )
            vals = sub_df[y_col].dropna()
            if not vals.empty:
                if not show_fliers:
                    uppers = []
                    lowers = []
                    for t in sub_df["Tecnologia"].unique():
                        t_vals = sub_df[sub_df["Tecnologia"] == t][y_col].dropna()
                        if not t_vals.empty:
                            q25 = t_vals.quantile(0.25)
                            q75 = t_vals.quantile(0.75)
                            iqr = q75 - q25
                            lowers.append(max(t_vals.min(), q25 - 1.5 * iqr))
                            uppers.append(min(t_vals.max(), q75 + 1.5 * iqr))
                    y_min = min(lowers) if lowers else vals.min()
                    y_max = max(uppers) if uppers else vals.max()
                else:
                    y_min = vals.min()
                    y_max = vals.max()
                span = max(y_max - y_min, 1.0)
                ax.set_ylim(max(0, y_min - span * 0.12), y_max + span * 0.12)

        panel_title = facet_labels.get(facet_val, str(facet_val))
        ax.set_title(panel_title, pad=10, fontweight="bold", fontsize=11)
        ax.set_xlabel("")
        plt.setp(ax.get_xticklabels(), rotation=0, ha="center", fontweight="bold", fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.6, axis="y")

        if idx == 0:
            ax.set_ylabel(ylabel, fontweight="bold", labelpad=8)
        else:
            ax.set_ylabel("")

    fig.suptitle(title, fontsize=13, fontweight="bold", y=0.98)

    custom_handles = [
        Patch(facecolor=PALETTE["React 19 (SPA)"], edgecolor="#374151", label="React 19 (SPA)"),
        Patch(facecolor=PALETTE["HTMX 2 (HDA)"], edgecolor="#374151", label="HTMX 2 (HDA)"),
        Line2D([0], [0], color="#111827", lw=2.2, label="Mediana (P50)"),
        Line2D(
            [0],
            [0],
            marker="D",
            color="none",
            markerfacecolor="white",
            markeredgecolor="#111827",
            markersize=5.5,
            label=r"Média ($\bar{x}$)",
        ),
    ]
    if show_samples:
        custom_handles.append(
            Line2D(
                [0],
                [0],
                marker="o",
                color="none",
                markerfacecolor="#6B7280",
                markeredgecolor="none",
                markersize=4.5,
                alpha=0.6,
                label=r"Amostras ($N$)",
            )
        )
    fig.legend(
        handles=custom_handles,
        title="Legenda",
        loc="lower center",
        bbox_to_anchor=(0.5, -0.05),
        ncol=len(custom_handles),
        frameon=True,
        framealpha=0.95,
        fontsize=10,
        title_fontsize=10.5,
    )
    fig.tight_layout(rect=[0, 0.08, 1, 0.94])
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def _line_chart(
    df: pd.DataFrame,
    out_path: Path,
    title: str,
    ylabel: str,
    x_col: str,
    y_col: str,
    xlabel: str = None,
    x_ticks: list = None,
    marker: str = "o",
    markersize: float = 5.5,
    linewidth: float = 2.2,
    figsize: tuple = (8.0, 4.8),
):
    """Gera um gráfico de linha temporal/assintótico padronizado com P50 e IQR."""
    fig, ax = plt.subplots(figsize=figsize, dpi=300)
    sns.lineplot(
        data=df,
        x=x_col,
        y=y_col,
        hue="Tecnologia",
        hue_order=_hue_order(),
        palette=PALETTE,
        marker=marker,
        markersize=markersize,
        linewidth=linewidth,
        estimator=np.median,
        errorbar=("pi", 50),
        ax=ax,
    )
    ax.set_title(title, pad=12, fontweight="bold")

    if xlabel is None:
        max_x = int(df[x_col].max()) if x_col in df.columns and not df.empty else 50
        xlabel = f"Número do Lote Inserido (Lote 1 a {max_x})"
    ax.set_xlabel(xlabel, fontweight="bold", labelpad=8)
    ax.set_ylabel(ylabel, fontweight="bold", labelpad=8)

    if x_ticks is not None:
        ax.set_xticks(x_ticks)
    ax.set_ylim(bottom=0)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(
        title="Tecnologia",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.20),
        ncol=2,
        frameon=True,
        framealpha=0.95,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def _boxplot_beta(df: pd.DataFrame, out_path: Path, show_samples: bool = False, show_fliers: bool = True):
    """Gera o boxplot de distribuição das taxas de degradação linear (beta)."""
    import scipy.stats as stats

    slopes = []
    col = "BatchNum" if "BatchNum" in df.columns else "BatchIndex"
    for (run_id, tech, perf), group in df.groupby(["Rodada", "Tecnologia", "PerfilRede"]):
        res = stats.linregress(group[col], group["BatchLoadTime"])
        slopes.append({
            "Rodada": run_id,
            "Tecnologia": tech,
            "PerfilRede": perf,
            "Slope": res.slope,
        })
    slope_df = pd.DataFrame(slopes)
    if slope_df.empty:
        return

    fig, ax = plt.subplots(figsize=(8.0, 5.0), dpi=300)
    sns.boxplot(
        data=slope_df,
        x="PerfilRede",
        y="Slope",
        order=config.PROFILES,
        hue="Tecnologia",
        hue_order=_hue_order(),
        palette=PALETTE,
        ax=ax,
        width=0.55,
        showfliers=show_fliers,
        fliersize=3.5 if show_fliers else 0,
        flierprops={
            "marker": "o",
            "markerfacecolor": "#6B7280",
            "markeredgecolor": "none",
            "alpha": 0.6,
        } if show_fliers else {},
        boxprops={"alpha": 0.90, "linewidth": 1.2, "edgecolor": "#1F2937"},
        whiskerprops={"linewidth": 1.2, "color": "#374151"},
        capprops={"linewidth": 1.2, "color": "#374151"},
        medianprops={"linewidth": 2.2, "color": "#111827"},
        showmeans=True,
        meanprops={
            "marker": "D",
            "markerfacecolor": "white",
            "markeredgecolor": "#111827",
            "markersize": 5.5,
        },
    )
    if show_samples:
        sns.stripplot(
            data=slope_df,
            x="PerfilRede",
            y="Slope",
            order=config.PROFILES,
            hue="Tecnologia",
            hue_order=_hue_order(),
            dodge=True,
            jitter=0.15,
            alpha=0.45,
            size=4.0,
            palette=PALETTE,
            ax=ax,
            legend=False,
        )
    ax.set_title(
        "Distribuição da Taxa de Degradação Marginal (β em ms/lote)\n"
        "Complexidade Assintótica: HTMX O(1) vs React O(N)",
        pad=12,
        fontweight="bold",
    )
    ax.set_xlabel("Condição de Rede", fontweight="bold", labelpad=8)
    ax.set_ylabel("Taxa de Degradação β (ms adicionais por lote)", fontweight="bold", labelpad=8)
    ax.axhline(0, color="gray", linestyle=":", linewidth=1.2)
    ax.grid(True, linestyle="--", alpha=0.6, axis="y")

    if not show_fliers:
        uppers = []
        lowers = []
        for (perf, t), grp in slope_df.groupby(["PerfilRede", "Tecnologia"]):
            t_vals = grp["Slope"].dropna()
            if not t_vals.empty:
                q25 = t_vals.quantile(0.25)
                q75 = t_vals.quantile(0.75)
                iqr = q75 - q25
                lowers.append(max(t_vals.min(), q25 - 1.5 * iqr))
                uppers.append(min(t_vals.max(), q75 + 1.5 * iqr))
        y_min = min(lowers) if lowers else slope_df["Slope"].min()
        y_max = max(uppers) if uppers else slope_df["Slope"].max()
        span = max(y_max - y_min, 0.1)
        ax.set_ylim(y_min - span * 0.12, y_max + span * 0.12)

    custom_handles = [
        Patch(facecolor=PALETTE["React 19 (SPA)"], edgecolor="#374151", label="React 19 (SPA)"),
        Patch(facecolor=PALETTE["HTMX 2 (HDA)"], edgecolor="#374151", label="HTMX 2 (HDA)"),
        Line2D([0], [0], color="#111827", lw=2.2, label="Mediana (P50)"),
        Line2D(
            [0],
            [0],
            marker="D",
            color="none",
            markerfacecolor="white",
            markeredgecolor="#111827",
            markersize=5.5,
            label=r"Média ($\bar{x}$)",
        ),
    ]
    if show_samples:
        custom_handles.append(
            Line2D(
                [0],
                [0],
                marker="o",
                color="none",
                markerfacecolor="#6B7280",
                markeredgecolor="none",
                markersize=4.5,
                alpha=0.6,
                label=r"Amostras ($N$)",
            )
        )
    ax.legend(
        handles=custom_handles,
        title="Legenda",
        loc="upper center",
        bbox_to_anchor=(0.5, -0.20),
        ncol=len(custom_handles),
        frameon=True,
        framealpha=0.95,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Funções Públicas de Alto Nível com Suporte a Modos
# ---------------------------------------------------------------------------

def cold_start_graphs(mode: str = "hybrid", show_samples: bool = False, show_fliers: bool = True):
    """Gera gráficos da Bateria 1 (Cold Start) nos formatos selecionados.
    
    Formatos controlados por mode:
      'hybrid': barras para grandezas determinísticas (Payload, Heap, TBT) e box-plots para latências (TTFB, FCP, LCP).
      'bar': gera apenas gráficos de barras originais (prefixo bar_).
      'boxplot': gera estritamente box-plots (prefixo boxplot_).
      'all': gera ambos os conjuntos para comparação direta.
    """
    csv_path = config.COLD_START_CSV
    if not csv_path.exists():
        print(f"[AVISO] {csv_path} não encontrado.")
        return
    df = _padronizar(pd.read_csv(csv_path))

    gen_bar_payload = mode in ("hybrid", "bar", "all")
    gen_box_payload = mode in ("boxplot", "all")

    # 1. Payload total por página na condição NoThrottling
    sub_no_throt = df[df["PerfilRede"] == "NoThrottling"]
    if not sub_no_throt.empty:
        if gen_bar_payload:
            _bar_chart(
                sub_no_throt,
                config.GRAFICOS_COLD / "bar_PayloadTotal_por_pagina.png",
                "Volume Total de Dados Transferidos por Página (Payload de Rede)",
                "Carga Total Transferida (KB)",
                "Pagina",
                config.PAGES,
                "PayloadKB",
                unit_str="KB",
                xlabel="Página da Aplicação (EventFlow)",
                figsize=(8.2, 4.8),
            )
            print("[OK] bar_PayloadTotal_por_pagina.png")
        if gen_box_payload:
            _box_chart(
                sub_no_throt,
                config.GRAFICOS_COLD / "boxplot_PayloadTotal_por_pagina.png",
                "Volume Total de Dados Transferidos por Página (Payload de Rede)",
                "Carga Total Transferida (KB)",
                "Pagina",
                config.PAGES,
                "PayloadKB",
                unit_str="KB",
                xlabel="Página da Aplicação (EventFlow)",
                figsize=(8.2, 5.0),
                show_samples=show_samples,
                show_fliers=show_fliers,
            )
            print("[OK] boxplot_PayloadTotal_por_pagina.png")

    # Mapeamento: chave -> (Label, Unidade, is_deterministic)
    metrics = {
        "TTFB": ("Time to First Byte (TTFB)", "ms", False),
        "FCP": ("First Contentful Paint (FCP)", "ms", False),
        "LCP": ("Largest Contentful Paint (LCP)", "ms", False),
        "TBT": ("Total Blocking Time (TBT)", "ms", True),
        "PayloadKB": ("Carga de Rede Total (Payload)", "KB", True),
        "PayloadJS_KB": ("Volume de Código JavaScript Transferido", "KB", True),
        "JSHeapMB": ("Consumo de Memória RAM JS Heap", "MB", True),
    }

    # 2. Gráficos agrupados por perfil de rede (x = Pagina)
    for met, (label, unit_str, is_det) in metrics.items():
        if met not in df.columns:
            continue
        gen_bar = mode == "bar" or mode == "all" or (mode == "hybrid" and is_det)
        gen_box = mode == "boxplot" or mode == "all" or (mode == "hybrid" and not is_det)

        for perf in config.PROFILES:
            sub_df = df[df["PerfilRede"] == perf]
            if sub_df.empty:
                continue
            if gen_bar:
                _bar_chart(
                    sub_df,
                    config.GRAFICOS_COLD / f"bar_{met}_{perf}.png",
                    f"{label}\nCondição de Rede: {PERFIS_DESC[perf]} (Mediana e IQR)",
                    f"{label} ({unit_str})",
                    "Pagina",
                    config.PAGES,
                    met,
                    unit_str=unit_str,
                    xlabel="Página da Aplicação (EventFlow)",
                )
                print(f"[OK] bar_{met}_{perf}.png")
            if gen_box:
                _box_chart(
                    sub_df,
                    config.GRAFICOS_COLD / f"boxplot_{met}_{perf}.png",
                    f"{label}\nCondição de Rede: {PERFIS_DESC[perf]}",
                    f"{label} ({unit_str})",
                    "Pagina",
                    config.PAGES,
                    met,
                    unit_str=unit_str,
                    xlabel="Página da Aplicação (EventFlow)",
                    show_samples=show_samples,
                    show_fliers=show_fliers,
                )
                print(f"[OK] boxplot_{met}_{perf}.png")

    # 3. Gráficos agrupados por página (x = PerfilRede)
    profile_labels = [PERFIS_DESC[p].split(" (")[0] for p in config.PROFILES]
    for met, (label, unit_str, is_det) in metrics.items():
        if met not in df.columns:
            continue
        gen_bar = mode == "bar" or mode == "all" or (mode == "hybrid" and is_det)
        gen_box = mode == "boxplot" or mode == "all" or (mode == "hybrid" and not is_det)

        for pag in config.PAGES:
            sub_pag = df[df["Pagina"] == pag]
            if sub_pag.empty:
                continue
            if gen_bar:
                _bar_chart(
                    sub_pag,
                    config.GRAFICOS_COLD / f"bar_{met}_{pag}.png",
                    f"{label}: Página {pag}\nImpacto da Degradação de Rede (Mediana e IQR)",
                    f"{label} ({unit_str})",
                    "PerfilRede",
                    config.PROFILES,
                    met,
                    unit_str=unit_str,
                    xlabel="Condição de Rede",
                    xticklabels=profile_labels,
                )
                print(f"[OK] bar_{met}_{pag}.png")
            if gen_box:
                facet_perfis_desc = {
                    "NoThrottling": "Sem Restrição\n(Rede Local / Ideal)",
                    "Fast4G": "Rede Fast 4G\n(10 Mbps, 40 ms RTT)",
                    "Slow4G": "Rede Slow 4G\n(4 Mbps, 100 ms RTT)",
                }
                _box_chart_faceted(
                    sub_pag,
                    config.GRAFICOS_COLD / f"boxplot_{met}_{pag}.png",
                    f"{label}: Página {pag} sob Degradação de Rede",
                    f"{label} ({unit_str})",
                    "PerfilRede",
                    config.PROFILES,
                    facet_perfis_desc,
                    met,
                    unit_str=unit_str,
                    show_samples=show_samples,
                    show_fliers=show_fliers,
                )
                print(f"[OK] boxplot_{met}_{pag}.png")


def infinite_scroll_graphs(mode: str = "hybrid", show_samples: bool = False, show_fliers: bool = True):
    """Gera todos os gráficos da Bateria 2 (Deep Infinite Scroll)."""
    csv_path = config.SCROLL_CSV
    if not csv_path.exists():
        print(f"[AVISO] {csv_path} não encontrado.")
        return
    df = _padronizar(pd.read_csv(csv_path))
    if "BatchLatencyMs" in df.columns and "BatchLoadTime" not in df.columns:
        df["BatchLoadTime"] = df["BatchLatencyMs"]

    metrics = {
        "BatchLoadTime": ("Tempo Mediano por Lote (P50 ± IQR P25-P75)", "ms", "Latência Mediana por Lote (ms)"),
        "DOMNodeCount": ("Acúmulo de Nós no DOM", "nós", "Contagem Total de Nós no DOM"),
        "JSHeapMB": ("Consumo de Memória JS Heap", "MB", "Memória RAM Heap (MB)"),
    }
    col = "BatchNum" if "BatchNum" in df.columns else "BatchIndex"

    for met, (label, unit_str, ylabel) in metrics.items():
        if met not in df.columns:
            continue
        for perf in config.PROFILES:
            sub_df = df[df["PerfilRede"] == perf]
            if sub_df.empty:
                continue
            max_b = int(sub_df[col].max()) if col in sub_df.columns and not sub_df.empty else 50
            ticks = [1] + [x for x in range(5, max_b + 1, 5)]
            _line_chart(
                sub_df,
                config.GRAFICOS_SCROLL / f"evolucao_{met}_{perf}.png",
                f"{label} ({max_b} Lotes)\nCondição de Rede: {PERFIS_DESC[perf]}",
                ylabel,
                col,
                met,
                xlabel=f"Número do Lote Inserido (Lote 1 a {max_b})",
                x_ticks=ticks,
            )
            print(f"[OK] evolucao_{met}_{perf}.png")

    _boxplot_beta(df, config.GRAFICOS_SCROLL / "boxplot_taxa_degradacao_beta.png", show_samples=show_samples, show_fliers=show_fliers)
    print("[OK] boxplot_taxa_degradacao_beta.png")


def mutation_graphs(mode: str = "hybrid", show_samples: bool = False, show_fliers: bool = True):
    """Gera todos os gráficos da Bateria 3 (State Mutation)."""
    csv_path = config.MUTATION_CSV
    if not csv_path.exists():
        print(f"[AVISO] {csv_path} não encontrado.")
        return
    df = _padronizar(pd.read_csv(csv_path))
    df["TipoOperacao"] = df["MutationIndex"].apply(lambda x: "POST" if x % 2 != 0 else "DELETE")

    gen_bar = mode in ("bar", "all")
    gen_box = mode in ("boxplot", "all", "hybrid")

    ops = [
        ("geral", "Geral (Todas as Mutações)", df, "o"),
        ("inscricao_POST", "Inscrição em Evento (POST)", df[df["TipoOperacao"] == "POST"], "s"),
        ("cancelamento_DELETE", "Cancelamento de Inscrição (DELETE)", df[df["TipoOperacao"] == "DELETE"], "^"),
    ]
    for slug, title, sub, marker in ops:
        if sub.empty:
            continue
        # 1. Gráficos por condição de rede
        if gen_bar:
            _bar_chart(
                sub,
                config.GRAFICOS_MUTACAO / f"bar_MutationLatencyMs_{slug}.png",
                f"Latência Mediana da Mutação: {title} (P50 ± IQR)",
                "Latência de Resposta (ms)",
                "PerfilRede",
                config.PROFILES,
                "MutationLatencyMs",
                unit_str="ms",
                xlabel="Condição de Rede",
                figsize=(7.5, 4.8),
            )
            print(f"[OK] bar_MutationLatencyMs_{slug}.png")
        if gen_box:
            facet_perfis_desc = {
                "NoThrottling": "Sem Restrição\n(Rede Local / Ideal)",
                "Fast4G": "Rede Fast 4G\n(10 Mbps, 40 ms RTT)",
                "Slow4G": "Rede Slow 4G\n(4 Mbps, 100 ms RTT)",
            }
            _box_chart_faceted(
                sub,
                config.GRAFICOS_MUTACAO / f"boxplot_MutationLatencyMs_{slug}.png",
                f"Latência da Mutação de Estado: {title}",
                "Latência de Resposta (ms)",
                "PerfilRede",
                config.PROFILES,
                facet_perfis_desc,
                "MutationLatencyMs",
                unit_str="ms",
                show_samples=show_samples,
                show_fliers=show_fliers,
            )
            print(f"[OK] boxplot_MutationLatencyMs_{slug}.png")

        # 2. Evolução ciclo a ciclo por condição de rede (sempre gerada)
        for perf in config.PROFILES:
            sub_perf = sub[sub["PerfilRede"] == perf]
            if sub_perf.empty:
                continue
            cycles = sorted(sub_perf["MutationIndex"].unique())
            _line_chart(
                sub_perf,
                config.GRAFICOS_MUTACAO / f"evolucao_MutationLatencyMs_{slug}_{perf}.png",
                f"Evolução de {title}\nCondição de Rede: {PERFIS_DESC[perf]}",
                "Latência (ms)",
                "MutationIndex",
                "MutationLatencyMs",
                xlabel="Ciclo Sequencial da Operação",
                x_ticks=cycles,
                marker=marker,
                markersize=6.0,
                linewidth=2.0,
                figsize=(8.0, 4.5),
            )
            print(f"[OK] evolucao_MutationLatencyMs_{slug}_{perf}.png")


def tcp_cwnd_graphs():
    """Gera gráficos didáticos em dois painéis (Dinâmica de cwnd + Carga Acumulada no estilo Stevens/tcptrace)
    com recorte focado no período de transferência ativa (0 a 600 ms) e anotações das fases da aplicação.
    """
    for tech, csv_path, color, out_name in [
        ("HTMX", config.TCP_CWND_CSV_HTMX, PALETTE["HTMX 2 (HDA)"], "tcp_cwnd_NoThrottling_HTMX.png"),
        ("React", config.TCP_CWND_CSV_REACT, PALETTE["React 19 (SPA)"], "tcp_cwnd_NoThrottling_React.png"),
    ]:
        if not csv_path.exists():
            continue
        df = pd.read_csv(csv_path)
        if df.empty:
            continue

        # Ordena e isola a janela ativa (0 a 280 ms no Linux nativo) eliminando o silêncio pós-carregamento
        df = df.sort_values("TimestampMs").reset_index(drop=True)
        active_limit_ms = 280.0
        active_df = df[df["TimestampMs"] <= active_limit_ms].copy()
        if active_df.empty:
            active_df = df.copy()

        # Cria figura acadêmica com 2 subplots verticais com eixo X sincronizado
        fig, (ax_top, ax_bottom) = plt.subplots(
            2, 1,
            figsize=(10.0, 7.6),
            dpi=300,
            sharex=True,
            gridspec_kw={"height_ratios": [1.2, 1.0], "hspace": 0.22},
        )

        agg_active = active_df.drop_duplicates(subset=["TimestampMs"], keep="last").copy()
        t_vals = agg_active["TimestampMs"].values
        bif_vals = agg_active["TotalBytesInFlightKB"].values

        # -------------------------------------------------------------------
        # 1. Painel Superior: Dinâmica de Janela (cwnd estimada) e Trânsito
        # -------------------------------------------------------------------
        ax_top.fill_between(
            t_vals,
            0,
            bif_vals,
            color=color,
            alpha=0.30,
            label="Bytes em Trânsito (Instantâneo)",
            step="post",
        )
        ax_top.plot(
            t_vals,
            bif_vals,
            color=color,
            linewidth=1.2,
            alpha=0.65,
            drawstyle="steps-post",
        )

        # Envoltória de pico de cwnd por burst ativo adaptada à temporização Linux nativa
        data_active = active_df[active_df["PayloadBytes"] > 0]
        t_first_data = data_active["TimestampMs"].min() if not data_active.empty else 0.0
        t_last_data = data_active["TimestampMs"].max() if not data_active.empty else 0.0

        if tech == "React":
            # React tem dois bursts bem definidos: Onda 1 (JS/CSS Gzip) e Onda 2 (Imagens)
            envelope_t = [0.0, 3.5, 4.0, 8.0, 8.5, 242.0, 243.0, 250.5, 251.2, 252.0, active_limit_ms]
            envelope_cwnd = [14.6, 14.6, 28.3, 28.3, 14.6, 14.6, 119.1, 119.1, 119.1, 14.6, 14.6]
        else:
            # HTMX tem um burst unificado concentrado entre ~39 ms e ~54,4 ms
            envelope_t = [0.0, 38.0, 39.0, 43.0, 54.4, 55.0, active_limit_ms]
            envelope_cwnd = [14.6, 14.6, 98.6, 98.6, 98.6, 14.6, 14.6]

        ax_top.plot(
            envelope_t,
            envelope_cwnd,
            color="#1F2937",
            linewidth=2.0,
            linestyle="--",
            drawstyle="steps-post",
            label="Teto da Janela de Congestionamento (cwnd estimada)",
            zorder=4,
        )

        # Linha horizontal de referência do initcwnd
        ax_top.axhline(
            14.6,
            color="#6B7280",
            linestyle=":",
            linewidth=1.5,
            label="initcwnd padrão Linux (14,6 KB / 10 MSS)",
            zorder=2,
        )

        # Anotações de fases contextuais da aplicação
        if tech == "React":
            ax_top.axvspan(0, 10, color="#3B82F6", alpha=0.10)
            ax_bottom.axvspan(0, 10, color="#3B82F6", alpha=0.10)
            ax_top.annotate(
                "Fase 1: Bundle JS + CSS (~118 KB)",
                xy=(6.0, 28.3),
                xytext=(16.0, 48.0),
                arrowprops=dict(arrowstyle="->", color="#1E40AF", lw=1.3),
                fontsize=8.5,
                fontweight="bold",
                color="#1E40AF",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#EFF6FF", edgecolor="#93C5FD", alpha=0.92),
                zorder=10,
            )

            ax_top.axvspan(10, 240, color="#F59E0B", alpha=0.08)
            ax_bottom.axvspan(10, 240, color="#F59E0B", alpha=0.08)
            ax_top.text(
                130, 28,
                "Pausa de Execução V8 & Espera da API REST (~230 ms)\n(Janela TCP em repouso basal)",
                fontsize=8.5, fontweight="bold", color="#92400E", ha="center",
                bbox=dict(boxstyle="round,pad=0.35", facecolor="#FFFBEB", edgecolor="#FCD34D", alpha=0.92),
                zorder=10,
            )

            ax_top.axvspan(240, 252, color="#3B82F6", alpha=0.10)
            ax_bottom.axvspan(240, 252, color="#3B82F6", alpha=0.10)
            ax_top.annotate(
                "Fase 2: API REST (JSON) + Imagens (~909 KB)",
                xy=(243.0, 119.1),
                xytext=(235.0, 80.0),
                ha="right",
                arrowprops=dict(arrowstyle="->", color="#1E40AF", lw=1.3),
                fontsize=8.5,
                fontweight="bold",
                color="#1E40AF",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#EFF6FF", edgecolor="#93C5FD", alpha=0.92),
                zorder=10,
            )
        else:
            ax_top.axvspan(0, 39, color="#9CA3AF", alpha=0.08)
            ax_bottom.axvspan(0, 39, color="#9CA3AF", alpha=0.08)
            ax_top.annotate(
                "Processamento Inicial (TTFB ~39 ms)",
                xy=(39.0, 5.0),
                xytext=(15.0, 45.0),
                arrowprops=dict(arrowstyle="->", color="#374151", lw=1.3),
                fontsize=8.5,
                fontweight="bold",
                color="#374151",
                bbox=dict(boxstyle="round,pad=0.25", facecolor="#F3F4F6", edgecolor="#D1D5DB", alpha=0.92),
                zorder=10,
            )

            ax_top.axvspan(39, 54.4, color="#10B981", alpha=0.10)
            ax_bottom.axvspan(39, 54.4, color="#10B981", alpha=0.10)
            ax_top.annotate(
                "Fluxo Unificado (39 a 54 ms)\n(HTML + Assets + Imagens simultâneas)\nConcluído em 54,4 ms",
                xy=(47.0, 75.0),
                xytext=(95.0, 68.0),
                ha="left",
                va="center",
                arrowprops=dict(arrowstyle="->", color="#059669", lw=1.4),
                fontsize=8.5,
                fontweight="bold",
                color="#065F46",
                bbox=dict(boxstyle="round,pad=0.35", facecolor="#ECFDF5", edgecolor="#059669", linewidth=1.2, alpha=0.96),
                zorder=10,
            )

        tech_title = "HTMX 2 (HDA)" if tech == "HTMX" else "React 19 (SPA)"
        ax_top.set_title(
            f"Dinâmica de Transporte TCP e Janela de Congestionamento (cwnd)\n"
            f"Tecnologia: {tech_title} | Carregamento Completo da Página Home (NoThrottling)",
            pad=30,
            fontweight="bold",
            fontsize=11.5,
        )
        ax_top.set_ylabel("Capacidade / Trânsito (KB)", fontweight="bold", labelpad=8)
        ax_top.set_xlim(0, active_limit_ms)
        ax_top.set_ylim(-2, 160 if tech == "React" else 125)
        ax_top.grid(True, linestyle="--", alpha=0.55, axis="both")
        
        # Legenda externa acima do painel superior
        ax_top.legend(
            loc="lower center",
            bbox_to_anchor=(0.5, 1.02),
            ncol=3,
            frameon=True,
            facecolor="#F9FAFB",
            edgecolor="#E5E7EB",
            fontsize=8.2,
        )

        # -------------------------------------------------------------------
        # 2. Painel Inferior: Carga Acumulada de Rede (Stevens / tcptrace Plot)
        # -------------------------------------------------------------------
        cum_t = agg_active["TimestampMs"].values
        cum_kb = agg_active["CumulativePayloadKB"].values

        ax_bottom.plot(
            cum_t,
            cum_kb,
            color=color,
            linewidth=2.8,
            label=f"Carga Acumulada de Rede ({tech})",
        )
        ax_bottom.fill_between(
            cum_t,
            0,
            cum_kb,
            color=color,
            alpha=0.12,
        )

        final_kb = cum_kb.max() if len(cum_kb) > 0 else 0.0
        ax_bottom.axhline(
            final_kb,
            color="#4B5563",
            linestyle="--",
            linewidth=1.2,
            label=f"Carga Final: {final_kb:.1f} KB",
        )

        if tech == "React":
            ax_bottom.axhline(
                118.1,
                color="#2563EB",
                linestyle=":",
                linewidth=1.2,
                label="Degrau 1: Bundle JS/CSS (~118,1 KB)",
            )
            ax_bottom.text(
                125, 200,
                "Patamar de Inatividade de Rede (~230 ms)\n(Zero bytes transferidos)",
                fontsize=8.5, fontstyle="italic", color="#92400E", ha="center", zorder=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFFBEB", edgecolor="#FCD34D", alpha=0.9),
            )
        else:
            ax_bottom.text(
                110, 450,
                "Transferência Contínua e Direta\n(Esgotamento da carga em apenas 15,4 ms de rede)",
                fontsize=8.5, fontstyle="italic", color="#065F46", ha="left", zorder=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#F0FDF4", edgecolor="#BBF7D0", alpha=0.9),
            )

        ax_bottom.set_xlabel("Tempo Decorrido da Sessão TCP (ms)", fontweight="bold", labelpad=8)
        ax_bottom.set_ylabel("Carga Acumulada (KB)", fontweight="bold", labelpad=8)
        ax_bottom.set_xlim(0, active_limit_ms)
        ax_bottom.set_ylim(-20, 1250 if tech == "React" else 1100)
        ax_bottom.grid(True, linestyle="--", alpha=0.55, axis="both")
        
        # Legenda externa abaixo do painel inferior
        ax_bottom.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, -0.22),
            ncol=3 if tech == "React" else 2,
            frameon=True,
            facecolor="#F9FAFB",
            edgecolor="#E5E7EB",
            fontsize=8.5,
        )

        # Caixa com métricas no painel superior
        max_bif = agg_active["TotalBytesInFlightKB"].max()
        active_duration = t_last_data
        conns = len(active_df["StreamID"].unique())
        info_box = (
            f"Métricas Chave:\n"
            f"• Carga Total: {final_kb:.1f} KB\n"
            f"• Pico cwnd / BIF: {max_bif:.1f} KB\n"
            f"• Conexões TCP: {conns}\n"
            f"• Fim da Transferência: {active_duration:.1f} ms"
        )
        if tech == "React":
            ax_top.text(
                0.55,
                0.94,
                info_box,
                transform=ax_top.transAxes,
                fontsize=8.5,
                verticalalignment="top",
                horizontalalignment="center",
                bbox=dict(boxstyle="round,pad=0.45", facecolor="white", edgecolor="#D1D5DB", alpha=0.92),
                zorder=10,
            )
        else:
            ax_top.text(
                0.985,
                0.93,
                info_box,
                transform=ax_top.transAxes,
                fontsize=8.8,
                verticalalignment="top",
                horizontalalignment="right",
                bbox=dict(boxstyle="round,pad=0.45", facecolor="white", edgecolor="#D1D5DB", alpha=0.92),
                zorder=10,
            )

        fig.align_ylabels([ax_top, ax_bottom])
        out_path = config.GRAFICOS_COLD / out_name
        if out_path.exists():
            try:
                out_path.unlink()
            except Exception:
                pass
        fig.savefig(out_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        print(f"[OK] {out_name}")

    # -----------------------------------------------------------------------
    # 3. Gráfico Comparativo Consolidado (HTMX vs React na Mesma Escala)
    # -----------------------------------------------------------------------
    _generate_comparative_tcp_graph()


def _generate_comparative_tcp_graph():
    """Gera gráfico comparativo direto unindo HTMX e React na mesma escala temporal (0 a 280 ms no Linux)."""
    p_htmx = config.TCP_CWND_CSV_HTMX
    p_react = config.TCP_CWND_CSV_REACT
    if not p_htmx.exists() or not p_react.exists():
        return

    df_h = pd.read_csv(p_htmx).sort_values("TimestampMs").reset_index(drop=True)
    df_r = pd.read_csv(p_react).sort_values("TimestampMs").reset_index(drop=True)

    active_limit_ms = 280.0
    df_h = df_h[df_h["TimestampMs"] <= active_limit_ms]
    df_r = df_r[df_r["TimestampMs"] <= active_limit_ms]

    fig, (ax_top, ax_bottom) = plt.subplots(
        2, 1,
        figsize=(10.0, 7.6),
        dpi=300,
        sharex=True,
        gridspec_kw={"height_ratios": [1.2, 1.0], "hspace": 0.22},
    )

    color_h = PALETTE["HTMX 2 (HDA)"]
    color_r = PALETTE["React 19 (SPA)"]

    # Top: Bytes in flight e cwnd das duas tecnologias
    agg_h = df_h.drop_duplicates(subset=["TimestampMs"], keep="last")
    agg_r = df_r.drop_duplicates(subset=["TimestampMs"], keep="last")

    max_bif_h = agg_h["TotalBytesInFlightKB"].max()
    max_bif_r = agg_r["TotalBytesInFlightKB"].max()

    ax_top.plot(agg_h["TimestampMs"], agg_h["TotalBytesInFlightKB"], color=color_h, linewidth=1.8, label=f"HTMX: Bytes em Trânsito (Pico: {max_bif_h:.1f} KB)", drawstyle="steps-post")
    ax_top.plot(agg_r["TimestampMs"], agg_r["TotalBytesInFlightKB"], color=color_r, linewidth=1.8, label=f"React: Bytes em Trânsito (Pico: {max_bif_r:.1f} KB)", drawstyle="steps-post")
    ax_top.axhline(14.6, color="#6B7280", linestyle=":", linewidth=1.5, label="initcwnd padrão Linux (14,6 KB / 10 MSS)")

    ax_top.set_title(
        "Comparativo de Transporte TCP: HTMX 2 (HDA) vs React 19 (SPA)\n"
        "Carregamento Completo da Página Home (NoThrottling / Rede Local)",
        pad=30, fontweight="bold", fontsize=11.5,
    )
    ax_top.set_ylabel("Volume em Trânsito (KB)", fontweight="bold", labelpad=8)
    ax_top.set_xlim(0, active_limit_ms)
    ax_top.set_ylim(-2, 145)
    ax_top.grid(True, linestyle="--", alpha=0.55, axis="both")
    ax_top.legend(
        loc="lower center",
        bbox_to_anchor=(0.5, 1.02),
        ncol=3,
        frameon=True,
        facecolor="#F9FAFB",
        edgecolor="#E5E7EB",
        fontsize=8.2,
    )

    # Bottom: Cargas acumuladas sobrepostas
    cum_h_max = agg_h["CumulativePayloadKB"].max()
    cum_r_max = agg_r["CumulativePayloadKB"].max()
    ax_bottom.plot(agg_h["TimestampMs"], agg_h["CumulativePayloadKB"], color=color_h, linewidth=2.8, label=f"HTMX: Carga Acumulada (Total: {cum_h_max:.1f} KB)")
    ax_bottom.plot(agg_r["TimestampMs"], agg_r["CumulativePayloadKB"], color=color_r, linewidth=2.8, label=f"React: Carga Acumulada (Total: {cum_r_max:.1f} KB)")
    ax_bottom.axhline(cum_h_max, color=color_h, linestyle="--", alpha=0.7, linewidth=1.0)
    ax_bottom.axhline(cum_r_max, color=color_r, linestyle="--", alpha=0.7, linewidth=1.0)

    # Destaque do patamar de inatividade do React
    ax_bottom.annotate(
        "Patamar de Inatividade de Rede no React\n(Execução V8 e espera da API REST)",
        xy=(110, 118.1),
        xytext=(70, 480),
        arrowprops=dict(arrowstyle="->", color=color_r, lw=1.3),
        fontsize=8.5,
        fontweight="bold",
        color="#1E40AF",
        bbox=dict(boxstyle="round,pad=0.30", facecolor="#EFF6FF", edgecolor="#93C5FD", alpha=0.92),
    )

    # Destaque da conclusão do HTMX
    ax_bottom.annotate(
        "HTMX: Transferência Concluída (54,4 ms)",
        xy=(54.4, cum_h_max),
        xytext=(80.0, 850),
        arrowprops=dict(arrowstyle="->", color=color_h, lw=1.3),
        fontsize=8.5,
        fontweight="bold",
        color="#065F46",
        bbox=dict(boxstyle="round,pad=0.30", facecolor="#ECFDF5", edgecolor="#A7F3D0", alpha=0.92),
    )

    # Destaque da conclusão do React
    ax_bottom.annotate(
        "React: Transferência Concluída (251,1 ms)",
        xy=(250.8, cum_r_max),
        xytext=(215.0, 1150.0),
        ha="right",
        arrowprops=dict(arrowstyle="->", color=color_r, lw=1.3),
        fontsize=8.5,
        fontweight="bold",
        color="#1E40AF",
        bbox=dict(boxstyle="round,pad=0.30", facecolor="#EFF6FF", edgecolor="#93C5FD", alpha=0.92),
    )

    ax_bottom.set_xlabel("Tempo Decorrido da Sessão TCP (ms)", fontweight="bold", labelpad=8)
    ax_bottom.set_ylabel("Carga Acumulada (KB)", fontweight="bold", labelpad=8)
    ax_bottom.set_xlim(0, active_limit_ms)
    ax_bottom.set_ylim(-20, 1280)
    ax_bottom.grid(True, linestyle="--", alpha=0.55, axis="both")
    ax_bottom.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.22),
        ncol=2,
        frameon=True,
        facecolor="#F9FAFB",
        edgecolor="#E5E7EB",
        fontsize=8.5,
    )

    fig.align_ylabels([ax_top, ax_bottom])
    out_comp = config.GRAFICOS_COLD / "tcp_cwnd_comparativo.png"
    if out_comp.exists():
        try:
            out_comp.unlink()
        except Exception:
            pass
    fig.savefig(out_comp, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[OK] {out_comp.name}")


def generate_all(mode: str = "hybrid", show_samples: bool = None, show_fliers: bool = None):
    """Executa a geração de todos os gráficos das três baterias experimentais.
    
    Parâmetros:
      mode: 'hybrid' (padrão: boxplots para latências e barras para volumes),
            'bar' (versão clássica do TCC com barras e IQR),
            'boxplot' (versão estrita com boxplots para todas as métricas),
            'all' (gera ambos os conjuntos para comparação lado a lado).
      show_samples: bool (se True, renderiza os pontos de amostra sobrepostos aos boxplots; padrão: False).
      show_fliers: bool (se False, oculta os pontos de outliers dos boxplots; padrão: True).
    """
    import os
    if show_samples is None:
        show_samples = os.environ.get("SHOW_SAMPLES", "0").lower() in ("1", "true", "yes")
    if show_fliers is None:
        show_fliers = os.environ.get("NO_FLIERS", "0").lower() not in ("1", "true", "yes")

    set_academic_style()
    config.ensure_dirs()
    cold_start_graphs(mode=mode, show_samples=show_samples, show_fliers=show_fliers)
    infinite_scroll_graphs(mode=mode, show_samples=show_samples, show_fliers=show_fliers)
    mutation_graphs(mode=mode, show_samples=show_samples, show_fliers=show_fliers)
    tcp_cwnd_graphs()
    print(f"\n>>> Todos os gráficos gerados com sucesso no modo: {mode} (amostras individuais: {'ativadas' if show_samples else 'desativadas'}, outliers: {'visíveis' if show_fliers else 'ocultados'})!")


if __name__ == "__main__":
    import argparse
    import os

    parser = argparse.ArgumentParser(description="Gerador modular de gráficos do benchmark EventFlow")
    parser.add_argument(
        "--mode",
        "-m",
        choices=["hybrid", "bar", "boxplot", "all"],
        default=os.environ.get("CHART_TYPE", "hybrid"),
        help="Modo de geração (hybrid, bar, boxplot, all)",
    )
    parser.add_argument(
        "--show-samples",
        action="store_true",
        default=os.environ.get("SHOW_SAMPLES", "0").lower() in ("1", "true", "yes"),
        help="Exibe os pontos individuais das amostras sobrepostos aos box-plots (padrão: desativado)",
    )
    parser.add_argument(
        "--no-fliers",
        "--hide-outliers",
        dest="no_fliers",
        action="store_true",
        default=os.environ.get("NO_FLIERS", "0").lower() in ("1", "true", "yes"),
        help="Oculta os pontos de outliers (fliers) dos box-plots para uma visualização limpa",
    )
    cli_args = parser.parse_args()
    generate_all(
        mode=cli_args.mode,
        show_samples=cli_args.show_samples,
        show_fliers=not cli_args.no_fliers,
    )
