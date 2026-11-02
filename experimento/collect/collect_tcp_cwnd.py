"""Coletor automatizado da janela de congestionamento TCP (cwnd) e Bytes em Trânsito.

Mede o tráfego real no nível de transporte TCP durante o Cold Start da página Home
(HTML, JS, CSS, chamadas de API e imagens do catálogo em /media/), garantindo
isolamento estrito entre as execuções de React e HTMX com purga do cache tcp_metrics.
"""
import argparse
import csv
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Permite execução direta ou via módulo
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src import config

CSV_COLUMNS = [
    "TimestampMs",
    "StreamID",
    "PacketType",
    "PayloadBytes",
    "StreamBytesInFlightKB",
    "TotalBytesInFlightKB",
    "CumulativePayloadKB",
]

# Garante que /sbin e /usr/sbin estejam no PATH dentro do container
for sbin_dir in ("/usr/sbin", "/sbin"):
    if sbin_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = f"{os.environ.get('PATH', '')}:{sbin_dir}"


class CollectionError(RuntimeError):
    """Erro fatal durante a coleta empírica de transporte TCP."""


def verify_environment(iface: str):
    """Valida a existência das ferramentas de rede e da interface antes de iniciar o experimento."""
    missing_bins = [b for b in ("tcpdump", "ip") if not shutil.which(b)]
    if missing_bins:
        raise CollectionError(
            f"Binários obrigatórios não encontrados no container: {', '.join(missing_bins)}.\n"
            "  -> Solução: Adicione 'apt-get update && apt-get install -y tcpdump iproute2' "
            "no Dockerfile do serviço 'runner' e reconstrua a imagem (docker compose build runner)."
        )

    if iface != "any":
        sys_net = Path("/sys/class/net")
        if sys_net.exists():
            available_ifaces = [p.name for p in sys_net.iterdir()]
            if iface not in available_ifaces:
                raise CollectionError(
                    f"Interface de rede '{iface}' não encontrada no container.\n"
                    f"  -> Interfaces disponíveis: {', '.join(available_ifaces)} (ou utilize '-i any')."
                )


def flush_kernel_tcp_metrics():
    """Limpa o cache de métricas TCP do kernel Linux para evitar contaminação de cwnd anterior."""
    ip_bin = shutil.which("ip")
    res = subprocess.run(
        [ip_bin, "tcp_metrics", "flush", "all"],
        capture_output=True,
        text=True,
        check=False,
    )
    if res.returncode != 0:
        err = res.stderr.strip() or f"código de saída {res.returncode}"
        print(
            f"  [Aviso TCP Cache] Falha ao executar 'ip tcp_metrics flush all': {err}\n"
            "  -> Verifique se o container possui 'cap_add: [NET_ADMIN]' no docker-compose.yml."
        )
    else:
        print("  [TCP Cache] 'ip tcp_metrics flush all' executado com sucesso.")

    # Pausa para garantir que sockets anteriores saiam de TIME_WAIT
    time.sleep(1.0)


def parse_pcap_to_records(pcap_path: Path, server_port: int) -> tuple[list[dict], dict]:
    """Decodifica arquivo .pcap e extrai Bytes in Flight e carga acumulada por stream TCP."""
    stats = {"total_packets": 0, "ipv4_packets": 0, "tcp_port_packets": 0}

    if not pcap_path.exists() or pcap_path.stat().st_size <= 24:
        return [], stats

    records = []
    with open(pcap_path, "rb") as f:
        ghdr = f.read(24)
        if len(ghdr) < 24:
            return [], stats

        magic = struct.unpack("<I", ghdr[0:4])[0]
        if magic in (0xA1B2C3D4, 0xA1B23C4D):
            endian = "<"
        elif magic in (0xD4C3B2A1, 0x4D3CB2A1):
            endian = ">"
        else:
            raise CollectionError(f"Arquivo PCAP corrompido ou formato desconhecido (magic={hex(magic)}).")

        is_nano = magic in (0xA1B23C4D, 0x4D3CB2A1)
        linktype = struct.unpack(f"{endian}I", ghdr[20:24])[0]

        if linktype == 1:        # Ethernet
            link_offset = 14
        elif linktype == 113:    # Linux cooked v1 (SLL)
            link_offset = 16
        elif linktype == 276:    # Linux cooked v2 (SLL2)
            link_offset = 20
        elif linktype in (0, 101):
            link_offset = 4 if linktype == 0 else 0
        else:
            raise CollectionError(f"Link-layer header type não suportado no PCAP: linktype={linktype}.")

        t0 = None
        streams = {}

        while True:
            rhdr = f.read(16)
            if len(rhdr) < 16:
                break
            ts_sec, ts_usec, incl_len, orig_len = struct.unpack(f"{endian}IIII", rhdr)
            raw = f.read(incl_len)
            if len(raw) < incl_len:
                break

            stats["total_packets"] += 1

            pkt_time = ts_sec + ts_usec / (1e9 if is_nano else 1e6)
            if t0 is None:
                t0 = pkt_time
            t_ms = max(0.0, (pkt_time - t0) * 1000.0)

            if len(raw) < link_offset + 20:
                continue
            ip_data = raw[link_offset:]
            ver_ihl = ip_data[0]
            if (ver_ihl >> 4) != 4:
                continue  # Apenas IPv4
            stats["ipv4_packets"] += 1

            ihl = (ver_ihl & 0x0F) * 4
            protocol = ip_data[9]
            if protocol != 6 or len(ip_data) < ihl + 20:
                continue  # Apenas TCP

            total_ip_len = struct.unpack(">H", ip_data[2:4])[0]
            if total_ip_len == 0 or total_ip_len > orig_len:
                total_ip_len = orig_len - link_offset

            tcp_data = ip_data[ihl:]
            sport, dport, seq, ack, offset_flags = struct.unpack(">HHIIH", tcp_data[0:14])
            tcp_hdr_len = ((offset_flags >> 12) & 0x0F) * 4
            tcp_flags = offset_flags & 0x3F
            payload_len = max(0, total_ip_len - ihl - tcp_hdr_len)

            # Ignora pacotes puros de fechamento de conexão (FIN=0x01 ou RST=0x04) sem carga útil
            if payload_len == 0 and (tcp_flags & 0x05):
                continue

            if sport == server_port:
                client_port = dport
                pkt_type = "DATA"
            elif dport == server_port:
                client_port = sport
                pkt_type = "ACK"
            else:
                continue

            stats["tcp_port_packets"] += 1

            if client_port not in streams:
                streams[client_port] = {
                    "server_base_seq": None,
                    "highest_server_seq": None,
                    "last_server_ack": None,
                    "bytes_in_flight": 0,
                    "cumulative": 0,
                }
            st = streams[client_port]

            if pkt_type == "DATA":
                if st["server_base_seq"] is None:
                    st["server_base_seq"] = seq
                    st["last_server_ack"] = seq

                if payload_len > 0:
                    seq_end = (seq + payload_len) & 0xFFFFFFFF
                    if st["highest_server_seq"] is None or seq_end > st["highest_server_seq"]:
                        st["highest_server_seq"] = seq_end
                    st["cumulative"] += payload_len
            else:
                if st["server_base_seq"] is not None:
                    if st["last_server_ack"] is None or ack > st["last_server_ack"]:
                        st["last_server_ack"] = ack

            if st["highest_server_seq"] is not None and st["last_server_ack"] is not None:
                diff = st["highest_server_seq"] - st["last_server_ack"]
                if 0 <= diff <= 10 * 1024 * 1024:
                    st["bytes_in_flight"] = diff
                else:
                    st["bytes_in_flight"] = 0
            else:
                st["bytes_in_flight"] = 0

            tot_bif = sum(s["bytes_in_flight"] for s in streams.values())
            tot_cum = sum(s["cumulative"] for s in streams.values())

            records.append({
                "TimestampMs": round(t_ms, 3),
                "StreamID": client_port,
                "PacketType": pkt_type,
                "PayloadBytes": payload_len,
                "StreamBytesInFlightKB": round(st["bytes_in_flight"] / 1024.0, 3),
                "TotalBytesInFlightKB": round(tot_bif / 1024.0, 3),
                "CumulativePayloadKB": round(tot_cum / 1024.0, 3),
            })

    # Remove pacotes ociosos (ex.: Keep-Alive/Teardown) após o ACK do último pacote DATA do servidor
    last_data_idx = None
    for idx, rec in enumerate(records):
        if rec["PacketType"] == "DATA" and rec["PayloadBytes"] > 0:
            last_data_idx = idx

    if last_data_idx is not None:
        cutoff_idx = len(records) - 1
        for idx in range(last_data_idx + 1, len(records)):
            if records[idx]["TotalBytesInFlightKB"] == 0.0:
                cutoff_idx = idx
                break
        records = records[: cutoff_idx + 1]

    return records, stats


def run_collection_for_tech(tech: str, base_url: str, output_csv: Path, iface: str = "eth0"):
    """Executa a coleta empírica de transporte TCP ou lança CollectionError se falhar."""
    print(f"\n{'='*70}")
    print(f"  COLETA TCP CWND: {tech} (Cold Start Completo na Home)")
    print(f"  URL: {base_url} | Interface: {iface} | Saída: {output_csv.name}")
    print(f"{'='*70}")

    flush_kernel_tcp_metrics()

    server_port = 8080 if tech == "HTMX" else 5173
    pcap_path = Path(tempfile.gettempdir()) / f"tcp_capture_{tech}.pcap"
    if pcap_path.exists():
        pcap_path.unlink()

    tcpdump_bin = shutil.which("tcpdump")
    # -U: escrita imediata por pacote (evita arquivo vazio ao encerrar rápido)
    # -Z root: evita drop de privilégio que falha ao gravar em /tmp ou sob AppArmor no Docker
    cmd = [
        tcpdump_bin,
        "-i", iface,
        "-U",
        "-Z", "root",
        "-w", str(pcap_path),
        "-n",
        "-s", "128",
        f"tcp and port {server_port}",
    ]

    tcpdump_proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    time.sleep(0.4)

    # Verifica se o tcpdump morreu imediatamente após iniciar (ex.: falta de CAP_NET_RAW ou AppArmor)
    if tcpdump_proc.poll() is not None:
        _, stderr_out = tcpdump_proc.communicate()
        raise CollectionError(
            f"O processo tcpdump encerrou prematuramente (código {tcpdump_proc.returncode}).\n"
            f"  -> Saída de erro do tcpdump:\n     {stderr_out.strip()}\n"
            "  -> Causas comuns no Linux/Docker:\n"
            "     1. Falta de permissão de captura: adicione 'cap_add: [NET_ADMIN, NET_RAW]' ao serviço 'runner' no docker-compose.yml.\n"
            "     2. Bloqueio do AppArmor no host Linux: adicione 'security_opt: [apparmor=unconfined]' ao serviço 'runner'."
        )

    print(f"  [tcpdump] Captura ativa na interface '{iface}' (PID {tcpdump_proc.pid}, porta {server_port}).")

    try:
        from playwright.sync_api import sync_playwright
        from src.browser import launch_browser, wait_page_settled

        with sync_playwright() as p:
            browser = launch_browser(p)
            try:
                context = browser.new_context()
                page = context.new_page()
                page.set_default_navigation_timeout(60000)

                cdp = page.context.new_cdp_session(page)
                cdp.send("Network.enable")
                cdp.send("Network.setCacheDisabled", {"cacheDisabled": True})

                url = f"{base_url.rstrip('/')}/"
                print(f"  [Navegador] Acessando {url} com cache desabilitado...")
                page.goto(url, wait_until="load", timeout=60000)
                wait_page_settled(page)
                page.wait_for_timeout(1000)
                if tcpdump_proc and tcpdump_proc.poll() is None:
                    tcpdump_proc.terminate()

                context.close()
            finally:
                browser.close()
    except Exception as ex:
        tcpdump_proc.terminate()
        raise CollectionError(f"Falha durante a execução do navegador Playwright para {tech}: {ex}") from ex

    # Aguarda flush final dos pacotes e encerra o tcpdump de forma limpa
    time.sleep(0.5)
    tcpdump_proc.terminate()
    try:
        _, tcpdump_stderr = tcpdump_proc.communicate(timeout=3)
    except subprocess.TimeoutExpired:
        tcpdump_proc.kill()
        _, tcpdump_stderr = tcpdump_proc.communicate()

    print("  [tcpdump] Captura finalizada.")

    if not pcap_path.exists():
        raise CollectionError(
            f"Arquivo de captura '{pcap_path}' não foi criado pelo tcpdump.\n"
            f"  -> Log do tcpdump: {tcpdump_stderr.strip()}"
        )

    pcap_size = pcap_path.stat().st_size
    if pcap_size <= 24:
        raise CollectionError(
            f"O arquivo PCAP foi criado apenas com o cabeçalho ({pcap_size} bytes — 0 pacotes capturados).\n"
            f"  -> Log do tcpdump: {tcpdump_stderr.strip()}\n"
            f"  -> Verifique se o tráfego para {base_url} (porta {server_port}) realmente passa pela interface '{iface}'. "
            "Tente executar com '--interface any' para testar todas as interfaces."
        )

    print(f"  [Parser] Decodificando pacotes capturados ({pcap_size} bytes)...")
    records, stats = parse_pcap_to_records(pcap_path, server_port)

    if not records:
        raise CollectionError(
            f"O arquivo PCAP contém {stats['total_packets']} pacotes brutos, mas 0 registros válidos foram extraídos.\n"
            f"  -> Estatísticas do parser: Total={stats['total_packets']}, IPv4={stats['ipv4_packets']}, "
            f"TCP na porta {server_port}={stats['tcp_port_packets']}.\n"
            "  -> Se Total > 0 e IPv4 == 0, o Docker pode estar roteando via IPv6 entre os containers."
        )

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(records)

    max_bif = max((r["TotalBytesInFlightKB"] for r in records), default=0.0)
    final_payload = max((r["CumulativePayloadKB"] for r in records), default=0.0)
    duration = max((r["TimestampMs"] for r in records), default=0.0)

    print(f"  -> Concluído {tech}: {len(records)} registros reais salvos.")
    print(f"     Pico Bytes in Flight: {max_bif:.1f} KB | Carga Total: {final_payload:.1f} KB | Duração: {duration:.2f} ms")


def main():
    parser = argparse.ArgumentParser(description="Coletor de Janela de Congestionamento TCP (cwnd)")
    parser.add_argument("--tech", "-t", default="all")
    parser.add_argument("--htmx-url", default=os.environ.get("HTMX_URL", "http://htmx:8080"))
    parser.add_argument("--react-url", default=os.environ.get("REACT_URL", "http://react-frontend:5173"))
    parser.add_argument("--interface", "-i", default=os.environ.get("INTERFACE", "eth0"))
    args = parser.parse_args()

    config.ensure_dirs()

    try:
        verify_environment(args.interface)

        tech_input = args.tech.lower()
        run_htmx = "htmx" in tech_input or tech_input in ("all", "*")
        run_react = "react" in tech_input or tech_input in ("all", "*")

        if run_htmx:
            run_collection_for_tech("HTMX", args.htmx_url, config.TCP_CWND_CSV_HTMX, iface=args.interface)
            if run_react:
                print("\n  [Isolamento] Aguardando 2 segundos para liberar sockets e purgar buffers...")
                time.sleep(2.0)

        if run_react:
            run_collection_for_tech("React", args.react_url, config.TCP_CWND_CSV_REACT, iface=args.interface)

        print(f"\n[OK] Coleta empírica de transporte TCP concluída com sucesso em {config.RESULTS}!")
    except CollectionError as err:
        print(f"\n[ERRO FATAL NA COLETA TCP]\n  {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
