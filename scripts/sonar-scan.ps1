<#
.SYNOPSIS
  Correr SonarQube scan sobre el proyecto SECE.
.DESCRIPTION
  Requiere:
    - SonarQube Community corriendo en localhost:9000
    - sonar-scanner CLI en el PATH (ver C:\sonar-scanner\bin)
    - Un token generado en SonarQube > My Account > Security
.EXAMPLE
  .\scripts\sonar-scan.ps1 -Token "squ_abc123..."
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$Token,
    [string]$HostUrl = "http://localhost:9000"
)

Write-Host "=== Generando reporte de cobertura previo ===" -ForegroundColor Cyan
uv run pytest --cov=app --cov-report=xml --junitxml=pytest-report.xml

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Pytest falló. Corrige las pruebas antes de escanear." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Ejecutando SonarScanner ===" -ForegroundColor Cyan
sonar-scanner `
    "-Dsonar.host.url=$HostUrl" `
    "-Dsonar.token=$Token"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "SUCCESS: Análisis completado" -ForegroundColor Green
    Write-Host "Abre: $HostUrl/dashboard?id=sece-backend" -ForegroundColor Yellow
} else {
    Write-Host "ERROR: Scanner falló. Revisa el log." -ForegroundColor Red
    exit 1
}
