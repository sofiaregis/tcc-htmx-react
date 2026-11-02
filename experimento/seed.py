"""Reset e sincronizacao deterministica dos bancos de dados e catalogos de midia entre HTMX e React.

Gera o seed no projeto HTMX via Docker (comando seed_db) e propaga o arquivo db.sqlite3
e as imagens normalizadas para o backend React, garantindo estrita paridade de dados.
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from src import config
from src.browser import save_seed_timestamp


def main():
    parser = argparse.ArgumentParser(description="Seed e sincronização dos bancos (HTMX/React)")
    parser.add_argument("--events", type=int, default=700)
    parser.add_argument("--past-events", type=int, default=200)
    parser.add_argument("--today-events", type=int, default=100)
    parser.add_argument("--organizers", type=int, default=500)
    parser.add_argument("--participants", type=int, default=10000)
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("  [Seed] RESET E POPULAÇÃO DO BANCO DE DADOS")
    print("=" * 70)

    # 0. Parar containers para liberar locks de arquivo no host Windows
    subprocess.run(["docker", "compose", "down"], cwd=str(config.BASE_DIR),
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    htmx_db = config.HTMX_REPO / "db.sqlite3"
    react_db = config.REACT_REPO / "backend" / "db.sqlite3"

    # Limpar diretórios acidentais criados pelo Docker caso os arquivos não existissem previamente
    for db_path in (htmx_db, react_db):
        if db_path.is_dir():
            shutil.rmtree(str(db_path), ignore_errors=True)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        if not db_path.exists():
            db_path.touch(exist_ok=True)

    # Garantir que o seed_timestamp.json existe antes de montar como volume
    seed_json = config.BASE_DIR / "seed_timestamp.json"
    if not seed_json.exists():
        save_seed_timestamp()

    # 1. Seed no HTMX via Docker
    print("\n=== [1/3] Executando seed_db no HTMX via Docker ===")
    cmd = [
        "docker", "compose", "run", "--rm", "--no-deps",
        "-v", f"{config.HTMX_REPO}:/app",
        "-v", f"{seed_json}:/app/seed_timestamp.json:ro",
        "htmx-backend",
        "python", "manage.py", "seed_db",
        "--events", str(args.events),
        "--past-events", str(args.past_events),
        "--today-events", str(args.today_events),
        "--organizers", str(args.organizers),
        "--participants", str(args.participants),
    ]
    try:
        subprocess.run(cmd, cwd=str(config.BASE_DIR), check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERRO] Falha no seed HTMX: {e}")
        sys.exit(1)

    # 2. Copiar DB HTMX -> React
    print("\n=== [2/3] Sincronizando db.sqlite3 para o React ===")
    try:
        shutil.copy2(str(htmx_db), str(react_db))
        print(f"  [OK] db.sqlite3 copiado para {react_db}")
    except Exception as e:
        print(f"[ERRO] Falha ao copiar o banco: {e}")
        sys.exit(1)

    # 3. Padronizar e Copiar imagens de eventos
    print("\n=== [3/3] Padronizando e Sincronizando imagens dos eventos ===")
    src_media = config.HTMX_REPO / "media" / "event_images"
    dst_media = config.REACT_REPO / "backend" / "media" / "event_images"
    if src_media.exists():
        _normalize_images(src_media)
        if dst_media.exists():
            shutil.rmtree(str(dst_media), ignore_errors=True)
        shutil.copytree(str(src_media), str(dst_media), dirs_exist_ok=True)
        print(f"  [OK] Imagens sincronizadas em {dst_media}")

    save_seed_timestamp()
    print("\n>>> BANCO DE DADOS E MÍDIAS SINCRONIZADOS COM SUCESSO!")


def _normalize_images(img_dir):
    """Padroniza todas as imagens dos eventos para dimensões uniformes (480x270 @ Q75),
    eliminando discrepâncias de tamanho de arquivo entre diferentes lotes de scroll."""
    try:
        from PIL import Image
        count = 0
        for f in list(img_dir.glob("*.jpg")) + list(img_dir.glob("*.png")):
            with Image.open(f) as img:
                img_rgb = img.convert("RGB")
                img_resized = img_rgb.resize((480, 270), Image.Resampling.LANCZOS)
                img_resized.save(f, format="JPEG", quality=75, optimize=True)
                count += 1
        print(f"  [OK] {count} imagens padronizadas para dimensões uniformes (480x270 @ Q75, ~22 KB).")
    except Exception as e:
        print(f"  [AVISO] Falha ao padronizar imagens: {e}")


if __name__ == "__main__":
    main()
