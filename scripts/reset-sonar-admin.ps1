# Resetea el password del admin de SonarQube directamente contra la BD H2
# USAR CON SONARQUBE DETENIDO
# powershell -ExecutionPolicy Bypass -File .\scripts\reset-sonar-admin.ps1

$ErrorActionPreference = "Continue"

Write-Host "`n=== Deteniendo SonarQube si esta corriendo ===" -ForegroundColor Cyan
Get-Process -Name "java","javaw" -ErrorAction SilentlyContinue | ForEach-Object {
    $cmd = (Get-WmiObject Win32_Process -Filter "ProcessId=$($_.Id)" -ErrorAction SilentlyContinue).CommandLine
    if ($cmd -match "sonar") {
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Seconds 3

Write-Host "`n=== Ejecutando UPDATE sobre H2 ===" -ForegroundColor Cyan
# Hash PBKDF2 de "admin" como lo genera SonarQube 10+ con salt vacio: ampliamente documentado
# Fuente: Community SonarQube: "Reset admin password without logging in"
$h2Jar = Get-ChildItem "C:\sonarqube\lib\jdbc\h2\h2-*.jar" | Select-Object -First 1
$dbPath = "C:\sonarqube\data\sonar"

if (-not $h2Jar) {
    Write-Host "ERROR: No encontre h2-*.jar en C:\sonarqube\lib\jdbc\h2\" -ForegroundColor Red
    Read-Host "Enter"; exit 1
}

$sqlFile = "$env:TEMP\reset_admin.sql"
# Reset: borra el user admin para que SonarQube lo recree con default admin/admin al arrancar
@"
DELETE FROM USER_TOKENS WHERE USER_UUID IN (SELECT UUID FROM USERS WHERE LOGIN='admin');
DELETE FROM USERS WHERE LOGIN='admin';
"@ | Out-File -FilePath $sqlFile -Encoding ASCII

& "C:\Program Files\Eclipse Adoptium\jdk-21\bin\java.exe" -cp $h2Jar.FullName org.h2.tools.RunScript -url "jdbc:h2:$dbPath;MV_STORE=TRUE;AUTO_SERVER=FALSE" -user sonar -password sonar -script $sqlFile 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n*** USER admin BORRADO ***" -ForegroundColor Green
    Write-Host "Al arrancar SonarQube, se recreará con contraseña default: admin / admin"
    Write-Host "Ejecuta ahora: .\scripts\start-sonarqube.ps1" -ForegroundColor Yellow
} else {
    Write-Host "`nFallo. Probando sin credenciales..." -ForegroundColor Yellow
    & "C:\Program Files\Eclipse Adoptium\jdk-21\bin\java.exe" -cp $h2Jar.FullName org.h2.tools.RunScript -url "jdbc:h2:$dbPath;MV_STORE=TRUE" -script $sqlFile 2>&1
}
Remove-Item $sqlFile -Force -ErrorAction SilentlyContinue
Read-Host "`nEnter para cerrar"
