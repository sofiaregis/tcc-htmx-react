import os
import json
from pathlib import Path
from django.utils import timezone
from django.utils.dateparse import parse_datetime

def get_current_time():
    """
    Retorna o horário atual do sistema ou, se BENCHMARK_MODE=1, o timestamp
    congelado do momento do seed para garantir reprodutibilidade temporal perfeita
    sem interferir em sockets de rede ou bibliotecas C do sistema operacional.
    """
    if os.environ.get("BENCHMARK_MODE") == "1" or os.environ.get("USE_FIXED_TIME") == "1":
        candidates = [
            Path("/app/seed_timestamp.json"),
            Path("/app/seed_timestamp.txt"),
            Path(__file__).resolve().parent.parent / "seed_timestamp.json",
            Path(__file__).resolve().parent.parent.parent.parent / "experimento" / "seed_timestamp.json",
        ]
        for p in candidates:
            if p.exists():
                try:
                    content = p.read_text(encoding="utf-8").strip()
                    if content.startswith("{"):
                        data = json.loads(content)
                        iso_str = data.get("seed_time")
                        if iso_str:
                            dt = parse_datetime(iso_str)
                            if dt:
                                if timezone.is_naive(dt):
                                    dt = timezone.make_aware(dt, timezone.get_current_timezone())
                                return timezone.localtime(dt)
                    else:
                        dt = timezone.datetime.strptime(content[:19], "%Y-%m-%d %H:%M:%S")
                        dt = timezone.make_aware(dt, timezone.get_current_timezone())
                        return timezone.localtime(dt)
                except Exception:
                    pass
    return timezone.localtime()
