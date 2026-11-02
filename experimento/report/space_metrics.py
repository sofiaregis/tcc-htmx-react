"""Metricas de engenharia de software pelo framework SPACE (analise estatica).

Contagem automatizada de linhas efetivas de codigo (CLOC), total de arquivos e
dependencias externas de terceiros (pip e npm) nas aplicacoes HTMX e React.
"""
import json
from pathlib import Path

from src import config


def count_file_lines(filepath):
    ext = filepath.suffix.lower()
    code = comments = blank = 0
    in_block = False
    try:
        lines = filepath.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception:
        return 0, 0, 0, 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            blank += 1
            continue
        if ext == ".py":
            if in_block:
                comments += 1
                if '"""' in stripped or "'''" in stripped:
                    in_block = False
                continue
            if stripped.startswith('"""') or stripped.startswith("'''"):
                comments += 1
                if (stripped.count('"""') == 1) or (stripped.count("'''") == 1):
                    in_block = True
                continue
            if stripped.startswith("#"):
                comments += 1
                continue
            code += 1
        elif ext in (".js", ".jsx", ".ts", ".tsx", ".css"):
            if in_block:
                comments += 1
                if "*/" in stripped:
                    in_block = False
                continue
            if stripped.startswith("/*"):
                comments += 1
                if "*/" not in stripped:
                    in_block = True
                continue
            if stripped.startswith("//"):
                comments += 1
                continue
            code += 1
        elif ext == ".html":
            if in_block:
                comments += 1
                if "-->" in stripped or "%}" in stripped:
                    in_block = False
                continue
            if stripped.startswith("<!--") or stripped.startswith("{% comment %}"):
                comments += 1
                if "-->" not in stripped and "{% endcomment %}" not in stripped:
                    in_block = True
                continue
            code += 1
        else:
            code += 1
    return code, comments, blank, len(lines)


def analyze_directory(base_dir, valid_exts, ignore_dirs=None):
    if ignore_dirs is None:
        ignore_dirs = {"node_modules", ".venv", "venv", "__pycache__", ".git",
                       "dist", "build", "media", "staticfiles", ".idea", ".vscode", "migrations"}
    results = {"files_count": 0, "cloc": 0, "comments": 0, "blank": 0, "total": 0, "by_ext": {}}
    for root, dirs, files in Path(base_dir).walk():
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
        for file in files:
            if file.endswith(".min.js") or file.endswith(".min.css"):
                continue
            file_path = Path(root) / file
            ext = file_path.suffix.lower()
            if ext in valid_exts:
                code, comm, blk, tot = count_file_lines(file_path)
                results["files_count"] += 1
                results["cloc"] += code
                results["comments"] += comm
                results["blank"] += blk
                results["total"] += tot
                entry = results["by_ext"].setdefault(ext, {"files": 0, "cloc": 0})
                entry["files"] += 1
                entry["cloc"] += code
    return results


def analyze_dependencies(dir_htmx, dir_react):
    deps = {"htmx": {"pip": [], "static_js": []}, "react": {"pip": [], "npm_prod": [], "npm_dev": []}}

    req_htmx = dir_htmx / "requirements.txt"
    if req_htmx.exists():
        for line in req_htmx.read_text(encoding="utf-8").splitlines():
            l = line.strip()
            if l and not l.startswith("#"):
                deps["htmx"]["pip"].append(l.split("==")[0].split(">=")[0])

    # Dependência JS estática externa de terceiro (htmx.min.js)
    htmx_vendor = dir_htmx / "static" / "js" / "htmx.min.js"
    if htmx_vendor.exists():
        deps["htmx"]["static_js"].append(htmx_vendor.name)
    elif (dir_htmx / "events" / "static" / "js" / "htmx.min.js").exists():
        deps["htmx"]["static_js"].append("htmx.min.js")

    req_react = dir_react / "backend" / "requirements.txt"
    if req_react.exists():
        for line in req_react.read_text(encoding="utf-8").splitlines():
            l = line.strip()
            if l and not l.startswith("#"):
                deps["react"]["pip"].append(l.split("==")[0].split(">=")[0])

    pkg = dir_react / "frontend" / "package.json"
    if pkg.exists():
        data = json.loads(pkg.read_text(encoding="utf-8"))
        deps["react"]["npm_prod"] = list(data.get("dependencies", {}).keys())
        deps["react"]["npm_dev"] = list(data.get("devDependencies", {}).keys())
    return deps


def build_artifact_kb(react_dir):
    """Soma os artefatos .js/.css do build de produção do Vite (frontend/dist/)."""
    dist_dir = react_dir / "frontend" / "dist"
    if not dist_dir.exists():
        return None
    js = css = 0
    for f in dist_dir.rglob("*"):
        if f.is_file():
            if f.suffix == ".js":
                js += f.stat().st_size
            elif f.suffix == ".css":
                css += f.stat().st_size
    if js + css == 0:
        return None
    total = (js + css) / 1024
    return {"js_kb": js / 1024, "css_kb": css / 1024, "total_kb": total,
            "desc": f"{js/1024:.1f} KB (JS) + {css/1024:.1f} KB (CSS) = {total:.1f} KB (bundle minificado)"}


def compute_space_metrics():
    """Retorna um dicionário com todas as métricas SPACE calculadas das duas bases de código."""
    htmx = config.HTMX_REPO
    react = config.REACT_REPO
    if not htmx.exists() or not react.exists():
        return None

    valid = {".py", ".js", ".jsx", ".html", ".css"}
    htmx_total = analyze_directory(htmx, valid)
    htmx_py = analyze_directory(htmx, {".py"})
    htmx_front = analyze_directory(htmx, {".html", ".css", ".js"})
    htmx_front_logic = analyze_directory(htmx, {".html", ".js"})

    react_backend = analyze_directory(react / "backend", valid)
    react_frontend = analyze_directory(react / "frontend" / "src", valid)
    react_front_logic = analyze_directory(react / "frontend" / "src", {".jsx", ".js"})

    deps = analyze_dependencies(htmx, react)

    def pct(h, r):
        return ((h - r) / r * 100) if r else None

    build = build_artifact_kb(react)

    return {
        "cloc_total": {"react": react_backend["cloc"] + react_frontend["cloc"],
                       "htmx": htmx_total["cloc"],
                       "pct": pct(htmx_total["cloc"], react_backend["cloc"] + react_frontend["cloc"])},
        "cloc_front": {"react": react_frontend["cloc"], "htmx": htmx_front["cloc"],
                       "pct": pct(htmx_front["cloc"], react_frontend["cloc"])},
        "cloc_front_logic": {"react": react_front_logic["cloc"], "htmx": htmx_front_logic["cloc"],
                             "pct": pct(htmx_front_logic["cloc"], react_front_logic["cloc"])},
        "cloc_back": {"react": react_backend["cloc"], "htmx": htmx_py["cloc"],
                      "pct": pct(htmx_py["cloc"], react_backend["cloc"])},
        "files_total": {"react": react_backend["files_count"] + react_frontend["files_count"],
                        "htmx": htmx_total["files_count"],
                        "pct": pct(htmx_total["files_count"], react_backend["files_count"] + react_frontend["files_count"])},
        "files_front": {"react": react_frontend["files_count"], "htmx": htmx_front["files_count"],
                        "pct": pct(htmx_front["files_count"], react_frontend["files_count"])},
        "files_back": {"react": react_backend["files_count"], "htmx": htmx_py["files_count"], "pct": None},
        "deps": {"react": len(deps["react"]["pip"]) + len(deps["react"]["npm_prod"]) + len(deps["react"]["npm_dev"]),
                 "htmx": len(deps["htmx"]["pip"]) + len(deps["htmx"]["static_js"]),
                 "pip_react": len(deps["react"]["pip"]),
                 "npm_prod": len(deps["react"]["npm_prod"]),
                 "npm_dev": len(deps["react"]["npm_dev"]),
                 "pip_htmx": len(deps["htmx"]["pip"]),
                 "static_js_htmx": len(deps["htmx"]["static_js"]),
                 "pct": pct(len(deps["htmx"]["pip"]) + len(deps["htmx"]["static_js"]),
                            len(deps["react"]["pip"]) + len(deps["react"]["npm_prod"]) + len(deps["react"]["npm_dev"]))},
        "build": build,
    }
