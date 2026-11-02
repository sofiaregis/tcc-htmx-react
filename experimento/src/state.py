"""Utilidades de estado/resume para coletores.

Permitem rodar apenas os experimentos/tecnologias/perfis desejados e retomar uma
coleta interrompida SEM duplicar rodadas: a coleta é idempotente por unidade
(Rodada + unidade, ex.: Pagina/BatchIndex/MutationIndex).
"""
from collections import Counter
from pathlib import Path


def load(csv_path):
    """Lê o CSV de resultados, ou None se arquivo/colunas não existirem."""
    if not Path(csv_path).exists():
        return None
    try:
        import pandas as pd
        df = pd.read_csv(csv_path)
    except Exception:
        return None
    if df.empty:
        return None
    return df


def present_units(csv_path, tech, perfil, unit_col):
    """Conjunto de pares (Rodada, valor) já gravados para (tecnologia, perfil)."""
    df = load(csv_path)
    if df is None or unit_col not in df.columns:
        return set()
    for col in ("Tecnologia", "PerfilRede", "Rodada", unit_col):
        if col not in df.columns:
            return set()
    sub = df[(df["Tecnologia"] == tech) & (df["PerfilRede"] == perfil)]
    return {(int(r), u) for r, u in zip(sub["Rodada"].astype(int), sub[unit_col])}


def missing_runs(csv_path, tech, perfil, target_runs, unit_col, per_run_count):
    """Rodadas (1..target_runs) que ainda não têm todas as per_run_count unidades."""
    present = present_units(csv_path, tech, perfil, unit_col)
    counts = Counter(r for (r, _u) in present)
    return [r for r in range(1, target_runs + 1) if counts.get(r, 0) < per_run_count]


def purge(csv_path, tech, perfil):
    """Remove do CSV todas as linhas de (tecnologia, perfil) — usado com --force."""
    df = load(csv_path)
    if df is None:
        return 0
    before = len(df)
    df = df[~((df["Tecnologia"] == tech) & (df["PerfilRede"] == perfil))]
    if len(df) != before:
        df.to_csv(csv_path, index=False, encoding="utf-8")
        return before - len(df)
    return 0
