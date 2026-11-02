"""Utilitarios de integracao com Playwright e Chrome DevTools Protocol (CDP).

Fornece inicializacao de navegador headless, emulacao de rede e CPU (throttling),
sincronizacao de clock deterministico e persistencia em disco linha a linha.
"""
import csv
import datetime
import json
from pathlib import Path

BROWSER_ARGS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--enable-blink-features=LayoutNG,PaintTiming,LongTaskObserver",
    "--enable-precise-memory-info",
    "--js-flags=--expose-gc",
]


def launch_browser(playwright):
    """Abre um Chromium headless com os flags usados no benchmark."""
    return playwright.chromium.launch(headless=True, args=BROWSER_ARGS)


def apply_throttle(page, profile_name, profile):
    """Aplica emulação completa e nativa de rede (latência, largura de banda,
    desativação de cache) e CPU via Chrome DevTools Protocol (CDP).
    """
    cdp = page.context.new_cdp_session(page)
    cdp.send("Performance.enable")
    cdp.send("Network.enable")
    cdp.send("Network.setCacheDisabled", {"cacheDisabled": True})
    cdp.send("Network.emulateNetworkConditions", {
        "offline": False,
        "latency": profile["latency"],
        "downloadThroughput": profile["download"],
        "uploadThroughput": profile["upload"],
    })
    cdp.send("Emulation.setCPUThrottlingRate", {"rate": profile["cpu"]})
    return cdp


def get_fixed_benchmark_time():
    """Timestamp fixo correspondente ao momento exato do seed (BENCHMARK_MODE)."""
    dt = None
    for candidate in ("seed_timestamp.json", "/app/seed_timestamp.json", Path(__file__).resolve().parent.parent / "seed_timestamp.json"):
        p = Path(candidate)
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                if "seed_time" in data:
                    return _parse_iso(data["seed_time"])
            except Exception:
                pass
    dt = datetime.datetime(2026, 8, 16, 12, 0, 0, tzinfo=datetime.timezone.utc)
    print(f"  [Clock Sync] Usando timestamp padrão de fallback: {dt.isoformat()}")
    return dt


def _parse_iso(value):
    dt = datetime.datetime.fromisoformat(value)
    print(f"  [Clock Sync] Timestamp fixo: {dt.isoformat()}")
    return dt


def save_seed_timestamp(timestamp=None):
    """Grava o timestamp do seed em seed_timestamp.json e .txt (libfaketime)."""
    if timestamp is None:
        timestamp = datetime.datetime.now(datetime.timezone.utc)
    elif isinstance(timestamp, str):
        timestamp = datetime.datetime.fromisoformat(timestamp)

    data = {
        "seed_time": timestamp.isoformat(),
        "created_at_human": timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
    for p in (Path(__file__).resolve().parent.parent / "seed_timestamp.json",):
        try:
            p.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception:
            pass
    txt = Path(__file__).resolve().parent.parent / "seed_timestamp.txt"
    try:
        txt.write_text(timestamp.strftime("%Y-%m-%d %H:%M:%S\n"), encoding="utf-8")
    except Exception:
        pass
    print(f"  [Seed Timestamp] Registrado: {data['created_at_human']}")
    return timestamp


def append_csv_row(output_file, row_dict, fieldnames):
    """Grava imediatamente uma linha no CSV (flush em disco a cada execução)."""
    p = Path(output_file)
    p.parent.mkdir(parents=True, exist_ok=True)
    file_exists = p.exists() and p.stat().st_size > 0
    with open(p, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        writer.writerow(row_dict)
        f.flush()


def find_csv(csv_path):
    """Retorna o caminho do CSV se existir, ou None."""
    return Path(csv_path) if Path(csv_path).exists() else None


def wait_page_settled(page, timeout_ms=45000):
    """Aguarda a página assentar antes de iniciar interações (scroll/mutações).

    Espera o fim do tráfego de rede (networkidle) e, como fallback, todas as
    imagens carregadas. Evita que as primeiras medições concorram com os
    recursos da página inicial ainda em download (ex.: imagens sob Slow4G).
    """
    try:
        page.wait_for_load_state("networkidle", timeout=timeout_ms)
        return
    except Exception:
        pass
    try:
        page.wait_for_function(
            "() => Array.from(document.images).every((i) => i.complete && i.naturalWidth > 0)",
            timeout=timeout_ms,
        )
    except Exception:
        pass


def get_clean_js_heap(page, cdp=None) -> float:
    """Força Garbage Collection no V8 via CDP/window.gc e retorna o heap utilizado em MB."""
    if cdp is not None:
        try:
            cdp.send("HeapProfiler.collectGarbage")
            metrics = {m["name"]: m["value"] for m in cdp.send("Performance.getMetrics").get("metrics", [])}
            if "JSHeapUsedSize" in metrics:
                return metrics["JSHeapUsedSize"] / (1024 * 1024)
        except Exception:
            pass
    try:
        page.evaluate("if (window.gc) window.gc()")
        return page.evaluate("performance.memory ? performance.memory.usedJSHeapSize / (1024*1024) : 0")
    except Exception:
        return 0.0


def wait_condition_raf(page, js_expression, arg=None, timeout=15000):
    """Executa wait_for_function com polling='raf' (sincronizado com requestAnimationFrame)
    para medição de latência com resolução no frame do navegador (~16ms)."""
    return page.wait_for_function(
        js_expression,
        arg=arg,
        polling="raf",
        timeout=timeout,
    )
