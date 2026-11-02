"""Coleta do experimento de Mutação Rápida de Estado (State Mutation).

Simula um usuário autenticado que alterna 20 vezes o estado de participação em um
evento (10 inscrições POST em ciclos ímpares e 10 cancelamentos DELETE em ciclos
pares), medindo a latência de atualização visual, payload e memória JS Heap (com GC forçado),
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
    "Tecnologia", "PerfilRede", "Rodada", "MutationIndex", "TipoOperacao",
    "MutationLatencyMs", "MutationPayloadKB", "DOMNodeCount", "JSHeapMB",
]

BUTTON_SELECTOR = "#registration-card button, .event-details-sidebar .sidebar-card button"


def run_benchmark(tech_dict, runs, output_file, mutations_count=20, profiles_filter="all"):
    profiles_to_run = parse_profile_filter(profiles_filter)
    tech_names = list(tech_dict.keys())
    print(f"\n======================================================================")
    print(f"  MUTAÇÃO DE ESTADO: {tech_names} | Perfis: {list(profiles_to_run.keys())} | Rodadas: {runs} | Mutações: {mutations_count}")
    print(f"======================================================================")

    with sync_playwright() as p:
        browser = launch_browser(p)
        try:
            event_urls = {}
            for target_tech, base_url in tech_dict.items():
                event_urls[target_tech] = _discover_active_event(browser, base_url, target_tech)

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
                        page.on("dialog", lambda dialog: dialog.accept())
                        response_bytes = [0]

                        def on_response(response):
                            try:
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
                        target_base = base_url.rstrip("/")
                        event_url = event_urls[target_tech]

                        try:
                            _login(page, target_tech, target_base, run)
                            resp = page.goto(event_url, wait_until="load", timeout=60000)
                            if resp and resp.status >= 400:
                                print(f"    [ERRO] HTTP {resp.status} ao carregar evento {event_url} (rodada {run})")
                                context.close()
                                continue

                            page.wait_for_selector(BUTTON_SELECTOR, timeout=15000)
                            wait_page_settled(page)
                            page.wait_for_timeout(800)

                            for m_idx in range(1, mutations_count + 1):
                                # Limpeza de lixo prévia para evitar congelamento durante o clique
                                get_clean_js_heap(page, cdp)
                                page.wait_for_timeout(50)

                                btn = page.locator(BUTTON_SELECTOR).first
                                try:
                                    text_before = btn.inner_text().strip()
                                except Exception:
                                    break

                                is_post = "Cancelar" not in text_before
                                bytes_before = response_bytes[0]

                                t_start = time.time()
                                btn.click(no_wait_after=True)
                                try:
                                    wait_condition_raf(
                                        page,
                                        """(args) => {
                                            const el = document.querySelector(args.selector);
                                            if (!el) return false;
                                            const txt = el.innerText.trim();
                                            if (txt.includes('Processando')) return false;
                                            if (args.isPost) {
                                                return txt.includes('Cancelar');
                                            } else {
                                                return txt.includes('Garantir') && !txt.includes('Cancelar');
                                            }
                                        }""",
                                        arg={"selector": BUTTON_SELECTOR, "isPost": is_post},
                                        timeout=15000,
                                    )
                                    mutation_latency = (time.time() - t_start) * 1000
                                except Exception as ex:
                                    print(f"      [TIMEOUT/ERRO] Mutação {m_idx} falhou na rodada {run}: {ex}")
                                    break

                                mutation_payload_kb = max(0, (response_bytes[0] - bytes_before) / 1024)
                                js_heap_mb = get_clean_js_heap(page, cdp)

                                append_csv_row(output_file, {
                                    "Tecnologia": target_tech,
                                    "PerfilRede": profile_name,
                                    "Rodada": run,
                                    "MutationIndex": m_idx,
                                    "TipoOperacao": "POST" if is_post else "DELETE",
                                    "MutationLatencyMs": mutation_latency,
                                    "MutationPayloadKB": mutation_payload_kb,
                                    "DOMNodeCount": page.evaluate("document.querySelectorAll('*').length"),
                                    "JSHeapMB": js_heap_mb,
                                }, CSV_COLUMNS)

                                page.wait_for_timeout(300)

                            print(f"    -> [{target_tech:5s} | {profile_name:12s}] Rodada {run:02d}/{runs:02d} concluída | Mutações: {mutations_count}", flush=True)
                        except Exception as ex:
                            print(f"    Erro no benchmark ({target_tech} | {profile_name} | Rodada {run}): {ex}")
                        finally:
                            context.close()
        finally:
            browser.close()
    print(f"\n[OK] Mutação de Estado concluído -> {output_file}")


def _login(page, target_tech, base_url, run):
    import time
    username = f"bench_{run}_{int(time.time() * 1000) % 100000}"
    password = "password123"
    email = f"{username}@ufsc.br"
    reg_url = f"{base_url.rstrip('/')}/users/register/"
    page.goto(reg_url, wait_until="load", timeout=30000)
    page.wait_for_timeout(300)
    if target_tech == "HTMX":
        page.fill("input[name='username']", username)
        page.fill("input[name='email']", email)
        page.fill("input[name='password']", password)
        page.fill("input[name='confirm_password']", password)
        page.click("button[type='submit']")
    else:
        page.fill("input[placeholder='Ex: sofia_regis']", username)
        page.fill("input[placeholder='Ex: sofia@ufsc.br']", email)
        page.fill("input[placeholder='Mínimo 6 caracteres']", password)
        page.fill("input[placeholder='Digite a senha novamente']", password)
        page.click("button[type='submit']")
    
    page.wait_for_url(lambda u: "register" not in u, timeout=15000)
    page.wait_for_timeout(300)


def _discover_active_event(browser, base_url, target_tech):
    """Encontra o primeiro evento na Home (assumindo que os dados de teste contêm eventos abertos)."""
    temp_context = browser.new_context()
    temp_page = temp_context.new_page()
    html = ""
    try:
        temp_page.goto(f"{base_url.rstrip('/')}/", wait_until="load", timeout=30000)
        temp_page.wait_for_timeout(2000)
        html = temp_page.content()
    except Exception:
        pass
    finally:
        temp_context.close()

    import re
    match = re.search(r"/event/(\d+)", html)
    if match:
        event_id = match.group(1)
        url = f"{base_url.rstrip('/')}/event/{event_id}/" if target_tech == "HTMX" else f"{base_url.rstrip('/')}/event/{event_id}"
        print(f"  [Discover] Evento ativo ({target_tech}): {url}")
        return url

    fallback = f"{base_url.rstrip('/')}/event/1/" if target_tech == "HTMX" else f"{base_url.rstrip('/')}/event/1"
    print(f"  [Discover] Usando fallback ({target_tech}): {fallback}")
    return fallback


def main():
    parser = argparse.ArgumentParser(description="Coleta Mutação de Estado (HTMX vs React)")
    parser.add_argument("--react-url", default="http://react-frontend:5173")
    parser.add_argument("--htmx-url", default="http://htmx:8080")
    parser.add_argument("--runs", type=int, default=30)
    parser.add_argument("--mutations", type=int, default=20)
    parser.add_argument("--tech", "-t", default="all")
    parser.add_argument("--profiles", "-p", default="all")
    parser.add_argument("--output", default=str(config.MUTATION_CSV))
    args = parser.parse_args()

    techs = parse_tech_filter(args.tech)
    tech_dict = {}
    if "React" in techs:
        tech_dict["React"] = args.react_url
    if "HTMX" in techs:
        tech_dict["HTMX"] = args.htmx_url

    run_benchmark(tech_dict, args.runs, args.output, args.mutations, args.profiles)


if __name__ == "__main__":
    main()
