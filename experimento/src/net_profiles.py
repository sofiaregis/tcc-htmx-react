"""Perfis de emulacao de rede (CDP) e filtros de execucao.

Perfis baseados nas especificacoes W3C e Lighthouse:
  - NoThrottling: sem restricao (rede local / ideal).
  - Fast4G: 10 Mbps de download, 5 Mbps de upload, 40 ms RTT, CPU 1x.
  - Slow4G: 4 Mbps de download, 2 Mbps de upload, 100 ms RTT, CPU 2x.
"""
from .config import PROFILES

NETWORK_PROFILES = {
    "NoThrottling": {
        "offline": False,
        "latency": 0,
        "download": -1,
        "upload": -1,
        "cpu": 1,
    },
    "Fast4G": {
        "offline": False,
        "latency": 40,
        "download": int(10 * 1000 * 1000 / 8),   # 10 Mbps -> 1,25 MB/s
        "upload": int(5 * 1000 * 1000 / 8),      # 5 Mbps -> 625 KB/s
        "cpu": 1,
    },
    "Slow4G": {
        "offline": False,
        "latency": 100,
        "download": int(4 * 1000 * 1000 / 8),    # 4 Mbps -> 500 KB/s
        "upload": int(2 * 1000 * 1000 / 8),      # 2 Mbps -> 250 KB/s
        "cpu": 2,
    },
}


def parse_profile_filter(profiles_str, available=None):
    """Filtra os perfis com base em string vírgula-separada ou nome único (case-insensitive)."""
    available = available or NETWORK_PROFILES
    if not profiles_str or profiles_str.strip().lower() in ("all", "*", ""):
        return available

    requested = [x.strip().lower() for x in profiles_str.split(",") if x.strip()]
    filtered = {}
    for req in requested:
        matched = False
        for key, val in available.items():
            if key.lower() == req or key.lower().replace(" ", "") == req:
                filtered[key] = val
                matched = True
                break
        if not matched:
            print(f"  [AVISO] Perfil de rede '{req}' não reconhecido. Disponíveis: {list(available.keys())}")
    return filtered if filtered else available


def parse_tech_filter(tech_str):
    """Retorna ['React', 'HTMX'], ['React'] ou ['HTMX'] conforme a string de filtro."""
    if not tech_str or tech_str.strip().lower() in ("all", "*", ""):
        return ["React", "HTMX"]

    t = tech_str.strip().lower()
    if t in ("htmx", "hda"):
        return ["HTMX"]
    if t in ("react", "spa"):
        return ["React"]
    if "react" in t and "htmx" in t:
        return ["React", "HTMX"]
    return ["React", "HTMX"]
