$ErrorActionPreference = "Stop"
Set-Location $env:USERPROFILE\Proyecto_Clinica

Write-Host ""
Write-Host "=== Archivos a commitear ===" -ForegroundColor Cyan
git status -s

Write-Host ""
Write-Host "=== Añadiendo todo ===" -ForegroundColor Cyan
git add docs/evidencias/
git add scripts/
git add sonar-project.properties
git add tests/load/sece-load.js

Write-Host ""
Write-Host "=== Commit ===" -ForegroundColor Cyan
$msg = "docs(E12-E14): sonar fix + k6 output + ruleset capture + scripts helper"
git commit -m $msg

Write-Host ""
Write-Host "=== Push ===" -ForegroundColor Cyan
git push origin HEAD

Write-Host ""
Write-Host "*** LISTO ***" -ForegroundColor Green
Read-Host "Enter para cerrar"
