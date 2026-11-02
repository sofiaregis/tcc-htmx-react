# ==============================================================================
# Execução dos experimentos em ambiente de PRODUÇÃO (PowerShell)
#
# Exemplos:
#   .\executar_experimento.ps1                                              # roda os 3 experimentos (30 runs)
#   .\executar_experimento.ps1 -Experiment state-mutation                   # roda só mutação de estado
#   .\executar_experimento.ps1 -Experiment infinite-scroll                   # roda só o infinite scroll
#   .\executar_experimento.ps1 -Experiment cold-start                        # roda só cold start
#   .\executar_experimento.ps1 -Experiment infinite-scroll -Tech htmx        # só infinite scroll do HTMX
#   .\executar_experimento.ps1 -Profiles Slow4G                              # roda os 3 apenas sob Slow4G
#   .\executar_experimento.ps1 -Runs 30 -ScrollBatches 50                    # 30 rodadas com 50 lotes
#   .\executar_experimento.ps1 -AnalysisOnly                                 # apenas regera tabelas e gráficos
# ==============================================================================
param(
    [Alias("Experiments", "Exp", "e")]
    [string]$Experiment = "all",

    [Alias("Technology", "t")]
    [string]$Tech = "all",

    [Alias("Profile", "p")]
    [string]$Profiles = "all",

    [Alias("r")]
    [int]$Runs = 30,

    [Alias("Batches", "b")]
    [int]$ScrollBatches = 50,

    [Alias("m")]
    [int]$Mutations = 20,

    [Alias("Chart", "c")]
    [string]$ChartType = "hybrid",

    [switch]$Seed,
    [switch]$SkipAnalysis,
    [switch]$NoCollect,
    [switch]$AnalysisOnly
)

# Configuração de Codificação UTF-8 para o Console do Windows
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 > $null

# Elevação de Prioridade de Processo no Windows para imunidade a contenções de CPU
try {
    [System.Diagnostics.Process]::GetCurrentProcess().PriorityClass = [System.Diagnostics.ProcessPriorityClass]::High
} catch {}

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "   EVENTFLOW BENCHMARK (PRODUÇÃO) - AMBIENTE CONTROLADO DOCKER" -ForegroundColor Cyan
Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "  - Experimento(s):  $Experiment" -ForegroundColor Gray
Write-Host "  - Tecnologia(s):   $Tech" -ForegroundColor Gray
Write-Host "  - Perfil(is) Rede: $Profiles" -ForegroundColor Gray
Write-Host "  - Parâmetros:      $Runs rodadas | $ScrollBatches lotes (scroll) | $Mutations mutações" -ForegroundColor Gray
Write-Host "  [DICA] Para precisão máxima, pause a sincronização do OneDrive durante a coleta." -ForegroundColor Yellow
Write-Host "==============================================================================" -ForegroundColor Cyan

Set-Location $PSScriptRoot

$projectRoot = Split-Path $PSScriptRoot -Parent
$htmxDb = Join-Path $projectRoot "eventflow-htmx\db.sqlite3"
$reactDb = Join-Path $projectRoot "eventflow-react\backend\db.sqlite3"

# Se o Docker tiver criado db.sqlite3 como pasta por engano, removemos
if (Test-Path $htmxDb -PathType Container) {
    Write-Host "[Aviso] Removendo diretório indevido em $htmxDb..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $htmxDb
}
if (Test-Path $reactDb -PathType Container) {
    Write-Host "[Aviso] Removendo diretório indevido em $reactDb..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $reactDb
}

# Verifica se os bancos existem e possuem dados (> 0 bytes)
$htmxDbValid = (Test-Path $htmxDb -PathType Leaf) -and ((Get-Item $htmxDb -ErrorAction SilentlyContinue).Length -gt 0)
$reactDbValid = (Test-Path $reactDb -PathType Leaf) -and ((Get-Item $reactDb -ErrorAction SilentlyContinue).Length -gt 0)
$needsSeed = $Seed -or (-not $htmxDbValid) -or (-not $reactDbValid)

# 1. Seed automático se os bancos não existirem, ou opcional via parâmetro -Seed
if ($needsSeed -and (-not $AnalysisOnly)) {
    if (-not $Seed) {
        Write-Host "`n[1/3] Banco de dados não encontrado ou vazio. Gerando seed inicial automaticamente..." -ForegroundColor Yellow
    } else {
        Write-Host "`n[1/3] Executando seed e sincronização do banco de dados..." -ForegroundColor Yellow
    }
    python seed.py
    if ($LASTEXITCODE -ne 0) { Write-Host "[ERRO] Falha no seed." -ForegroundColor Red; exit 1 }
}

# 2. Garantir serviços de produção no ar (apenas se for coletar)
if (-not $AnalysisOnly) {
    Write-Host "`n[1/3] Subindo serviços de produção..." -ForegroundColor Yellow
    docker compose up -d --build htmx-backend htmx-frontend react-backend react-frontend
    if ($LASTEXITCODE -ne 0) { Write-Host "[ERRO] Falha ao subir os serviços." -ForegroundColor Red; exit 1 }
}

# 3. Executar runner (coleta e/ou análise)
if (-not $NoCollect) {
    Write-Host "`n[2/3] Executando runner de benchmark..." -ForegroundColor Yellow
    $runnerArgs = @("python", "run.py",
        "--experiments", "$Experiment",
        "--tech", "$Tech",
        "--profiles", "$Profiles",
        "--runs", "$Runs",
        "--chart-type", "$ChartType",
        "--scroll-batches", "$ScrollBatches",
        "--mutations", "$Mutations")
    if ($SkipAnalysis) { $runnerArgs += "--skip-analysis" }
    if ($AnalysisOnly) { $runnerArgs += "--skip-collect" }
    
    docker compose run --rm runner @runnerArgs
    if ($LASTEXITCODE -ne 0) { Write-Host "[ERRO] Falha no runner." -ForegroundColor Red; exit 1 }
}

# 4. Cleanup dos serviços (mantém os resultados/gráficos/tabelas)
Write-Host "`n[3/3] Derrubando serviços de produção..." -ForegroundColor Yellow
docker compose down

Write-Host ""
Write-Host "==============================================================================" -ForegroundColor Green
Write-Host "   BENCHMARK CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
Write-Host "   - Tabelas consolidadas: 'tabelas/'" -ForegroundColor Green
Write-Host "   - Relatórios estatísticos: 'resultados/'" -ForegroundColor Green
Write-Host "   - Figuras e Gráficos (300 DPI): 'graficos*/'" -ForegroundColor Green
Write-Host "==============================================================================" -ForegroundColor Green
