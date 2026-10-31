$ErrorActionPreference = "Stop"
Set-Location $env:USERPROFILE\Proyecto_Clinica

Write-Host "`n=== 1. Guardando rama actual ===" -ForegroundColor Cyan
$branchActual = (git branch --show-current).Trim()
Write-Host "Estabas en: $branchActual"

Write-Host "`n=== 2. Cambiando a dev ===" -ForegroundColor Cyan
git fetch origin
git checkout dev
git pull origin dev

Write-Host "`n=== 3. Merging feature/E11-E14-evidencias ===" -ForegroundColor Cyan
git merge origin/feature/E11-E14-evidencias --no-edit

Write-Host "`n=== 4. Push a dev ===" -ForegroundColor Cyan
git push origin dev

Write-Host "`n=== 5. Volviendo a tu rama ===" -ForegroundColor Cyan
git checkout $branchActual

Write-Host "`n*** LISTO. Pipeline arrancando en dev ***" -ForegroundColor Green
Write-Host "Monitorealo en: https://github.com/jcastanazab-collab/Proyecto_Clinica/actions"
Write-Host ""
Read-Host "Enter para cerrar"
