"""Coleta do experimento de Paginação Contínua Profunda (Deep Infinite Scroll).

Mede a evolução da latência por lote, payload (wire size), memória JS Heap (com GC forçado)
e nós do DOM ao longo de `scroll_batches` lotes de 12 eventos na página de busca,
com execução intercalada (round-robin) e sincronização via requestAnimationFrame ('raf').
"""
import argparse
import time

from playwright.sync_api import sync_playwright

from src import config
from src.net_profiles import parse_profile_filter, parse_tech_filter
from src.browser import (
    launch_browser, apply_throttle, append_csv_row, get_fixed_benchmark_time,
    wait_page_settled, get_clean_js_heap, wait_condition_raf
)
from src.state import purge

CSV_COLUMNS = [
    "Tecnologia", "PerfilRede", "Rodada", "BatchIndex",
    "BatchLatencyMs", "BatchPayloadKB", "TotalCardsRendered",
    "DOMNodeCount", "JSHeapMB", "DeltaJSHeapMB",
]

CARD_SELECTOR = ".event-card"


def _wait_for_min_cards(page, selector, expected_count, timeout=15000):
    """Espera sincronizada com requestAnimationFrame até haver pelo menos `expected_count` cards."""
    wait_condition_raf(
        page,
        "(args) => document.querySelectorAll(args.selector).length >= args.min",
        arg={"selector": selector, "min": expected_count},
        timeout=timeout,
    )


def run_benchmark(tech_dict, runs, output_file, scroll_batches=50, profiles_filter="all"):
    profiles_to_run = parse_profile_filter(profiles_filter)
    tech_names = list(tech_dict.keys())
    print(f"\n======================================================================")
    print(f"  INFINITE SCROLL: {tech_names} | Perfis: {list(profiles_to_run.keys())} | Rodadas: {runs} | Lotes: {scroll_batches}")
    print(f"======================================================================")

    with sync_playwright() as p:
        browser = launch_browser(p)
        try:
            for profile_name, profile in profiles_to_run.items():
                # Limpa coletas anteriores para garantir homogeneidade atômica
                for target_tech in tech_names:
                    removed = purge(output_file, target_tech, profile_name)
                    if removed:
                        print(f"  [Limpeza] {removed} registro(s) prévio(s) de {target_tech}/{profile_name} removidos do CSV.")

                for run in range(1, runs + 1):
                    for target_tech, base_url in tech_dict.items():
                        context = browser.new_context()
                        page = context.new_page()
                        page.set_default_navigation_timeout(60000)
                        response_bytes = [0]

                        def on_response(response):
                            try:
                                url_lower = response.url.lower()
                                res_type = response.request.resource_type
                                # Ignora imagens e mídias para contabilizar estritamente o payload arquitetural de dados (JSON vs HTML fragment)
                                if res_type in ["image", "media"] or any(ext in url_lower for ext in [".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".ico"]):
                                    return
                                if res_type in ["script", "stylesheet", "font"]:
                                    return

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
                                if size > 0:
                                    response_bytes[0] += size
                            except Exception:
                                pass

                        page.on("response", on_response)
                        cdp = apply_throttle(page, profile_name, profile)
                        url = f"{base_url.rstrip('/')}/search/"

                        try:
                            resp = page.goto(url, wait_until="load", timeout=60000)
                            if resp and resp.status >= 400:
                                print(f"    [ERRO] HTTP {resp.status} em {url} (rodada {run})")
                                context.close()
                                continue

                            page.wait_for_selector(CARD_SELECTOR, timeout=15000)
                            wait_page_settled(page)

                            current_card_count = page.locator(CARD_SELECTOR).count()
                            initial_heap_mb = get_clean_js_heap(page, cdp)

                            for batch in range(1, scroll_batches + 1):
                                # Força coleta de lixo e assentamento prévio para eliminar pausas de GC e deixar a thread 100% ociosa
                                get_clean_js_heap(page, cdp)
                                page.wait_for_timeout(250)

                                bytes_before = response_bytes[0]
                                t_start = time.time()
                                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                                expected_count = current_card_count + 12

                                timed_out = False
                                try:
                                    _wait_for_min_cards(page, CARD_SELECTOR, expected_count, timeout=15000)
                                    batch_latency = (time.time() - t_start) * 1000
                                except Exception:
                                    batch_latency = (time.time() - t_start) * 1000
                                    timed_out = True

                                new_card_count = page.locator(CARD_SELECTOR).count()
                                if new_card_count == current_card_count or timed_out:
                                    print(f"      [FIM] Nenhum novo card no lote {batch} (total {current_card_count}, timeout={timed_out}). Encerrando rodada.")
                                    break

                                current_card_count = new_card_count
                                batch_payload_kb = max(0, (response_bytes[0] - bytes_before) / 1024)
                                js_heap_mb = get_clean_js_heap(page, cdp)

                                append_csv_row(output_file, {
                                    "Tecnologia": target_tech,
                                    "PerfilRede": profile_name,
                                    "Rodada": run,
                                    "BatchIndex": batch,
                                    "BatchLatencyMs": batch_latency,
                                    "BatchPayloadKB": batch_payload_kb,
                                    "TotalCardsRendered": current_card_count,
                                    "DOMNodeCount": page.evaluate("document.querySelectorAll('*').length"),
                                    "JSHeapMB": js_heap_mb,
                                    "DeltaJSHeapMB": js_heap_mb - initial_heap_mb,
                                }, CSV_COLUMNS)

                                if batch % 10 == 0 or batch in (1, scroll_batches):
                                    print(f"      [{target_tech:5s} | {profile_name:12s}] Rodada {run:02d}/{runs:02d} | Lote {batch:02d}/{scroll_batches:02d} | Lat: {batch_latency:6.1f}ms | Cards: {current_card_count:3d} | Heap: {js_heap_mb:.2f}MB", flush=True)

                                pause_ms = 1800 if profile_name == "Slow4G" else 1000
                                page.wait_for_timeout(pause_ms)

                            print(f"    -> [{target_tech:5s} | {profile_name:12s}] Rodada {run:02d}/{runs:02d} concluída | Cards Finais: {current_card_count}", flush=True)
                        except Exception as ex:
                            print(f"    Erro no benchmark ({target_tech} | {profile_name} | Rodada {run}): {ex}")
                        finally:
                            context.close()
        finally:
            browser.close()
    print(f"\n[OK] Infinite Scroll concluído -> {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Coleta Infinite Scroll (HTMX vs React)")
    parser.add_argument("--react-url", default="http://react-frontend:5173")
    parser.add_argument("--htmx-url", default="http://htmx:8080")
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--batches", type=int, default=50)
    parser.add_argument("--tech", "-t", default="all")
    parser.add_argument("--profiles", "-p", default="all")
    parser.add_argument("--output", default=str(config.SCROLL_CSV))
    args = parser.parse_args()

    techs = parse_tech_filter(args.tech)
    tech_dict = {}
    if "React" in techs:
        tech_dict["React"] = args.react_url
    if "HTMX" in techs:
        tech_dict["HTMX"] = args.htmx_url

    run_benchmark(tech_dict, args.runs, args.output, args.batches, args.profiles)


if __name__ == "__main__":
    main()
