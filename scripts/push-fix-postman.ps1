# Push del fix de la colección Postman al pipeline
# Doble clic en Explorer o ejecutar con: powershell -ExecutionPolicy Bypass -File .\scripts\push-fix-postman.ps1

$ErrorActionPreference = "Stop"
Set-Location $env:USERPROFILE\Proyecto_Clinica

Write-Host "`n=== Estado actual ===" -ForegroundColor Cyan
git status -sb

Write-Host "`n=== Añadiendo fix ===" -ForegroundColor Cyan
git add tests/api/sece.postman_collection.json

Write-Host "`n=== Commit ===" -ForegroundColor Cyan
$msg = @"
fix(postman): login como medico en request 14-15 para rol MEDICO

El endpoint POST /api/v1/consultas requiere require_role(Rol.MEDICO).
La coleccion estaba logueada como ADMIN, lo que producia 403 en el
request 14 y 404 en cascada para el 15. Ahora el request 14 ejecuta
un prerequest que hace login con el medico creado en el request 06
y guarda medico_token, que ambos requests usan en lugar de admin_token.
"@
git commit -m $msg

Write-Host "`n=== Push ===" -ForegroundColor Cyan
git push origin HEAD

Write-Host "`n*** LISTO ***" -ForegroundColor Green
Write-Host "Revisa el pipeline en: https://github.com/jcastanazab-collab/Proyecto_Clinica/actions"
Write-Host "`nPresiona cualquier tecla para cerrar..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
