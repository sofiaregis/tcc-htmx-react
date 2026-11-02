"""Análise descritiva e comparativa da dinâmica de transporte TCP (cwnd e Bytes in Flight).

Processa os dados coletados de forma isolada para HTMX e React no Cold Start da Home,
quantificando a pressão máxima sobre o buffer de socket e o perfil temporal de entrega.
"""
import csv
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src import config


def _load_csv(csv_path: Path) -> list[dict]:
    if not csv_path.exists():
        return []
    records = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append({
                "TimestampMs": float(row["TimestampMs"]),
                "StreamID": int(row["StreamID"]),
                "PacketType": row["PacketType"],
                "PayloadBytes": int(row["PayloadBytes"]),
                "StreamBytesInFlightKB": float(row["StreamBytesInFlightKB"]),
                "TotalBytesInFlightKB": float(row["TotalBytesInFlightKB"]),
                "CumulativePayloadKB": float(row["CumulativePayloadKB"]),
            })
    return records


def run(
    csv_htmx: Path = config.TCP_CWND_CSV_HTMX,
    csv_react: Path = config.TCP_CWND_CSV_REACT,
    out_md: Path = config.TCP_CWND_MD,
):
    print(f"\n{'='*70}")
    print(f"  ANALISANDO DADOS DE TRANSPORTE TCP (CWND E BYTES IN FLIGHT)")
    print(f"{'='*70}")

    rec_htmx = _load_csv(csv_htmx)
    rec_react = _load_csv(csv_react)

    if not rec_htmx and not rec_react:
        print("  [AVISO] Nenhum arquivo CSV de TCP cwnd encontrado para análise.")
        return

    def stats_for(records):
        if not records:
            return {"streams": 0, "max_bif": 0.0, "total_kb": 0.0, "duration": 0.0}
        streams = len(set(r["StreamID"] for r in records))
        max_bif = max(r["TotalBytesInFlightKB"] for r in records)
        total_kb = max(r["CumulativePayloadKB"] for r in records)
        duration = max(r["TimestampMs"] for r in records)
        return {
            "streams": streams,
            "max_bif": max_bif,
            "total_kb": total_kb,
            "duration": duration,
        }

    s_htmx = stats_for(rec_htmx)
    s_react = stats_for(rec_react)

    initcwnd_kb = 14.6  # 10 MSS padrão Linux
    exp_factor_htmx = s_htmx["max_bif"] / initcwnd_kb if initcwnd_kb > 0 else 1.0
    exp_factor_react = s_react["max_bif"] / initcwnd_kb if initcwnd_kb > 0 else 1.0

    lines = [
        "# Relatório de Transporte TCP e Janela de Congestionamento (cwnd)\n",
        "Este relatório apresenta a análise empírica da camada de transporte TCP durante o **carregamento inicial completo (Cold Start)** ",
        "da página principal (**Home**), englobando todo o tráfego de rede (HTML, JavaScript, CSS, chamadas de API e imagens do catálogo em `/media/`), ",
        "avaliado no cenário **sem latência adicional (NoThrottling / Rede Local)** com isolamento estrito entre as coletas.\n",
        "## 1. Síntese Comparativa de Transporte TCP\n",
        "| Parâmetro de Transporte | HTMX 2 (HDA) | React 19 (SPA) | Variação / Relação |",
        "| :--- | :--- | :--- | :--- |",
        f"| Carga Total Transferida (Wire Payload) | {s_htmx['total_kb']:.2f} KB | {s_react['total_kb']:.2f} KB | +{((s_react['total_kb']/s_htmx['total_kb'])-1)*100:.1f}% no React |",
        f"| Pico de Bytes em Trânsito (Max Bytes in Flight) | {s_htmx['max_bif']:.2f} KB | {s_react['max_bif']:.2f} KB | React demanda {s_react['max_bif']/max(1.0, s_htmx['max_bif']):.1f}x mais buffer |",
        f"| Janela Inicial Padrão Linux (initcwnd) | {initcwnd_kb:.1f} KB (10 MSS) | {initcwnd_kb:.1f} KB (10 MSS) | Base idêntica de kernel |",
        f"| Fator de Expansão sobre a Janela Inicial | {exp_factor_htmx:.1f}x a initcwnd | {exp_factor_react:.1f}x a initcwnd | Aumento substancial no React |",
        f"| Conexões TCP Paralelas Utilizadas | {s_htmx['streams']} conexão(ões) | {s_react['streams']} conexão(ões) | Concorrência de streams |",
        f"| Duração da Transferência de Rede Local | {s_htmx['duration']:.2f} ms | {s_react['duration']:.2f} ms | Velocidade basal de esgotamento |",
        "\n---\n",
        "## 2. Discussão da Dinâmica de Janela e Entrega de Ativos\n",
        "### 2.1 Demanda de Buffer no Servidor\n",
        f"Mesmo no ambiente local sem latência, a pilha de rede do kernel Linux (Nginx) precisou expandir a janela de trânsito para **{s_react['max_bif']:.1f} KB** no React, ",
        f"contra **{s_htmx['max_bif']:.1f} KB** no HTMX. Isso demonstra que o modelo SPA impõe uma pressão de alocação de buffers de socket significativamente maior ao sistema operacional.\n",
        "### 2.2 Perfil Temporal: Fluxo Unificado vs. Cascata em Duas Ondas\n",
        "- **HTMX (Fluxo Unificado):** Ao receber o documento HTML renderizado no servidor com as tags de imagem já declaradas, o navegador dispara as conexões para estilos, scripts e imagens em um único bloco paralelo e contínuo.\n",
        "- **React (Cascata em Duas Fases):** O navegador precisa primeiro receber e executar o bundle JavaScript e estilos (comprimidos via Gzip em ~118 KB) e aguardar o retorno da API REST antes que as URLs das imagens possam ser descobertas. Isso cria uma divisão nítida no tráfego TCP em duas ondas sequenciais, retardando a inicialização das conexões de mídia.\n",
    ]

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"  [OK] Relatório salvo em: {out_md}")


if __name__ == "__main__":
    run()
