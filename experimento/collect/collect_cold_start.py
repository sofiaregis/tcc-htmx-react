"""Coleta do experimento de Carregamento Inicial (Cold Start).

Mede TTFB, FCP, LCP, CLS, TBT, Payload (decomposto por tipo), JS Heap (com GC forçado)
e nós do DOM nas páginas Home, Search e Details sob os perfis NoThrottling, Fast4G e Slow4G,
com execução intercalada (round-robin) entre tecnologias para eliminar viés temporal.
"""
import argparse
import re

from playwright.sync_api import sync_playwright

from src import config
from src.net_profiles import parse_profile_filter, parse_tech_filter
from src.browser import (
    launch_browser, apply_throttle, append_csv_row, get_fixed_benchmark_time,
    get_clean_js_heap, wait_page_settled
)
from src.state import purge

CSV_COLUMNS = [
    "Tecnologia", "Pagina", "PerfilRede", "Rodada",
    "TTFB", "FCP", "LCP", "CLS", "TBT", "DOMLoad", "FullLoad",
    "PayloadKB", "PayloadJS_KB", "PayloadCSS_KB", "PayloadMediaKB", "PayloadDocKB", "PayloadOtherKB",
    "JSHeapMB", "DOMNodeCount",
]

SCRIPT_INJECTION = """
window._lcp = 0;
window._fcp = 0;
window._cls = 0;
window._longTasks = [];

new PerformanceObserver((entryList) => {
  const entries = entryList.getEntries();
  if (entries.length > 0) {
    window._lcp = entries[entries.length - 1].startTime;
  }
}).observe({type: 'largest-contentful-paint', buffered: true});

new PerformanceObserver((entryList) => {
  const entries = entryList.getEntries();
  const fcp = entries.find(entry => entry.name === 'first-contentful-paint');
  if (fcp) {
    window._fcp = fcp.startTime;
  }
}).observe({type: 'paint', buffered: true});

new PerformanceObserver((entryList) => {
  for (const entry of entryList.getEntries()) {
    if (!entry.hadRecentInput) {
      window._cls += entry.value;
    }
  }
}).observe({type: 'layout-shift', buffered: true});

new PerformanceObserver((entryList) => {
  for (const entry of entryList.getEntries()) {
    window._longTasks.push({
      startTime: entry.startTime,
      duration: entry.duration
    });
  }
}).observe({type: 'longtask', buffered: true});
"""


def run_benchmark(tech_dict, runs, output_file, profiles_filter="all"):
    profiles_to_run = parse_profile_filter(profiles_filter)
    tech_names = list(tech_dict.keys())
    print(f"\n======================================================================")
    print(f"  COLD START: {tech_names} | Perfis: {list(profiles_to_run.keys())} | Rodadas: {runs}")
    print(f"======================================================================")

    with sync_playwright() as p:
        browser = launch_browser(p)
        try:
            # 1. Descoberta de IDs e rotas canônicas por tecnologia
            pages_by_tech = {}
            for target_tech, base_url in tech_dict.items():
                event_id = _discover_event_id(browser, target_tech, base_url)
                pages_by_tech[target_tech] = {
                    "Home": "/",
                    "Search": "/search/?q=Python" if target_tech == "HTMX" else "/search?q=Python",
                    "Details": f"/event/{event_id}/" if target_tech == "HTMX" else f"/event/{event_id}",
                }
                # Pré-aquece as rotas no container para eliminar cold import jitter
                _warmup_routes(browser, base_url, pages_by_tech[target_tech])

            # 2. Execução intercalada por Perfil -> Rodada -> Tecnologia
            for profile_name, profile in profiles_to_run.items():
                # Limpa coletas anteriores para garantir homogeneidade atômica
                for target_tech in tech_names:
                    removed = purge(output_file, target_tech, profile_name)
                    if removed:
                        print(f"  [Limpeza] {removed} registro(s) prévio(s) de {target_tech}/{profile_name} removidos do CSV.")

                # Aquece as rotas sob o perfil de rede específico antes de cronometrar a Rodada 1
                _warmup_profile_routes(browser, tech_dict, pages_by_tech, profile_name, profile)

                for run in range(1, runs + 1):
                    for target_tech, base_url in tech_dict.items():
                        pages_dyn = pages_by_tech[target_tech]
                        target_base = base_url.rstrip("/")

                        for page_name, path in pages_dyn.items():
                            url = f"{target_base}{path}"

                            context = browser.new_context()
                            page = context.new_page()

                            payload_tracker = {"doc": 0, "js": 0, "css": 0, "media": 0, "other": 0}

                            def on_response(response):
                                try:
                                    url_lower = response.url.lower()
                                    res_type = response.request.resource_type
                                    content_type = response.headers.get("content-type", "").lower()
                                    req_sizes = response.request.sizes()
                                    size = req_sizes.get("responseBodySize", 0) if req_sizes else 0
                                    if size <= 0 and response.headers.get("content-length"):
                                        try:
                                            size = int(response.headers["content-length"])
                                        except Exception:
                                            size = 0
                                    if size <= 0:
                                        try:
                                            body = response.body()
                                            size = len(body) if body else 0
                                        except Exception:
                                            size = 0
                                    if size <= 0:
                                        return

                                    if res_type == "document" or response.request.is_navigation_request():
                                        payload_tracker["doc"] += size
                                    elif "application/json" in content_type:
                                        payload_tracker["other"] += size
                                    elif res_type == "script" or url_lower.endswith(".js") or ".js?" in url_lower:
                                        payload_tracker["js"] += size
                                    elif res_type == "stylesheet" or url_lower.endswith(".css") or ".css?" in url_lower:
                                        payload_tracker["css"] += size
                                    elif res_type in ["image", "media"] or any(ext in url_lower for ext in [".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".ico"]):
                                        payload_tracker["media"] += size
                                    else:
                                        payload_tracker["other"] += size
                                except Exception:
                                    pass

                            page.on("response", on_response)
                            page.add_init_script(SCRIPT_INJECTION)
                            cdp = apply_throttle(page, profile_name, profile)

                            resp = page.goto(url, wait_until="load", timeout=60000)
                            if resp and resp.status >= 400:
                                print(f"    [ERRO] HTTP {resp.status} em {url} (rodada {run})")
                                context.close()
                                continue

                            # Aguarda hidratação / assentamento de rede
                            wait_page_settled(page)
                            pause_settle = 1500 if profile_name == "Slow4G" else 800
                            page.wait_for_timeout(pause_settle)

                            ttfb, dom_load, full_load = _nav_timings(page)
                            fcp = page.evaluate("""() => {
                                if (window._fcp && window._fcp > 0) return window._fcp;
                                const p = window.performance.getEntriesByType('paint').find(e => e.name === 'first-contentful-paint');
                                return p ? p.startTime : 0;
                            }""") or 0

                            lcp = page.evaluate("""() => {
                                if (window._lcp && window._lcp > 0) return window._lcp;
                                const entries = window.performance.getEntriesByType('largest-contentful-paint');
                                if (entries && entries.length > 0) return entries[entries.length - 1].startTime;
                                return 0;
                            }""") or 0

                            tbt = page.evaluate("""(fcpVal) => {
                                let total = 0;
                                for (const task of (window._longTasks || [])) {
                                    if (task.startTime >= fcpVal) {
                                        const blocking = task.duration - 50;
                                        if (blocking > 0) total += blocking;
                                    }
                                }
                                return total;
                            }""", fcp)

                            cls_val = page.evaluate("window._cls || 0")
                            clean_heap = get_clean_js_heap(page, cdp)
                            total_bytes = sum(payload_tracker.values())

                            row = {
                                "Tecnologia": target_tech,
                                "Pagina": page_name,
                                "PerfilRede": profile_name,
                                "Rodada": run,
                                "TTFB": ttfb,
                                "FCP": fcp,
                                "LCP": lcp,
                                "CLS": cls_val,
                                "TBT": tbt,
                                "DOMLoad": dom_load,
                                "FullLoad": full_load,
                                "PayloadKB": total_bytes / 1024,
                                "PayloadJS_KB": payload_tracker["js"] / 1024,
                                "PayloadCSS_KB": payload_tracker["css"] / 1024,
                                "PayloadMediaKB": payload_tracker["media"] / 1024,
                                "PayloadDocKB": payload_tracker["doc"] / 1024,
                                "PayloadOtherKB": payload_tracker["other"] / 1024,
                                "JSHeapMB": clean_heap,
                                "DOMNodeCount": page.evaluate("document.querySelectorAll('*').length"),
                            }
                            append_csv_row(output_file, row, CSV_COLUMNS)
                            print(f"    -> [{target_tech:5s} | {page_name:7s} | {profile_name:12s}] Rodada {run:02d}/{runs:02d} | FCP: {fcp:6.1f}ms | LCP: {lcp:6.1f}ms | TBT: {tbt:4.1f}ms | Heap: {clean_heap:.2f}MB | Payload: {total_bytes/1024:6.1f}KB", flush=True)
                            context.close()
        finally:
            browser.close()
    print(f"\n[OK] Cold Start concluído -> {output_file}")


def _warmup_routes(browser, base_url, pages_dyn):
    """Executa um pré-aquecimento único de cada rota para que o Gunicorn/Django 
    e o V8 carreguem seus módulos e caches antes de iniciar a medição oficial."""
    temp_context = browser.new_context()
    temp_page = temp_context.new_page()
    target_base = base_url.rstrip("/")
    for page_name, path in pages_dyn.items():
        try:
            temp_page.goto(f"{target_base}{path}", wait_until="load", timeout=15000)
            temp_page.wait_for_timeout(500)
        except Exception:
            pass
    temp_context.close()


def _warmup_profile_routes(browser, tech_dict, pages_by_tech, profile_name, profile):
    """Executa um aquecimento de descarte sob o perfil de rede específico antes de
    iniciar a Rodada 1, garantindo que o pool de sockets TCP do Chromium esteja aquecido."""
    for target_tech, base_url in tech_dict.items():
        ctx = browser.new_context()
        p = ctx.new_page()
        apply_throttle(p, profile_name, profile)
        target_base = base_url.rstrip("/")
        for _, path in pages_by_tech[target_tech].items():
            try:
                p.goto(f"{target_base}{path}", wait_until="load", timeout=20000)
                wait_page_settled(p)
                p.wait_for_timeout(300)
            except Exception:
                pass
        ctx.close()


def _discover_event_id(browser, target_tech, base_url):
    temp_context = browser.new_context()
    temp_page = temp_context.new_page()
    html = ""
    try:
        temp_page.goto(f"{base_url.rstrip('/')}/", wait_until="load", timeout=30000)
        temp_page.wait_for_timeout(2000)
        html = temp_page.content()
    except Exception:
        html = ""
    finally:
        temp_context.close()

    match = re.search(r"/event/(\d+)", html)
    print(f"  [Discover] Event ID ({target_tech}): {match.group(1) if match else 'fallback'}")
    return match.group(1) if match else "1"


def _nav_timings(page):
    data = page.evaluate("""() => {
        const nav = performance.getEntriesByType('navigation')[0];
        if (!nav) return { ttfb: 0, dom_load: 0, full_load: 0 };
        return {
            ttfb: Math.max(0, nav.responseStart - nav.startTime),
            dom_load: Math.max(0, nav.domContentLoadedEventEnd - nav.startTime),
            full_load: Math.max(0, nav.loadEventEnd - nav.startTime),
        };
    }""")
    return data.get("ttfb", 0), data.get("dom_load", 0), data.get("full_load", 0)


def main():
    parser = argparse.ArgumentParser(description="Coleta Cold Start (HTMX vs React)")
    parser.add_argument("--react-url", default="http://react-frontend:5173")
    parser.add_argument("--htmx-url", default="http://htmx:8080")
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--tech", "-t", default="all")
    parser.add_argument("--profiles", "-p", default="all")
    parser.add_argument("--output", default=str(config.COLD_START_CSV))
    args = parser.parse_args()

    techs = parse_tech_filter(args.tech)
    tech_dict = {}
    if "React" in techs:
        tech_dict["React"] = args.react_url
    if "HTMX" in techs:
        tech_dict["HTMX"] = args.htmx_url

    run_benchmark(tech_dict, args.runs, args.output, args.profiles)


if __name__ == "__main__":
    main()
