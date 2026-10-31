Write-Host ""
Write-Host "=== 1. Matando Java zombies de SonarQube ===" -ForegroundColor Cyan
Get-Process -Name java,javaw -ErrorAction SilentlyContinue | ForEach-Object {
    $pid_ = $_.Id
    try {
        $wmi = Get-WmiObject Win32_Process -Filter "ProcessId=$pid_" -ErrorAction SilentlyContinue
        if ($wmi -and $wmi.CommandLine -match "sonar") {
            Write-Host "  Matando PID $pid_" -ForegroundColor Yellow
            Stop-Process -Id $pid_ -Force -ErrorAction SilentlyContinue
        }
    } catch {}
}
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "=== 2. Limpiando temp ===" -ForegroundColor Cyan
if (Test-Path "C:\sonarqube\temp") {
    Remove-Item "C:\sonarqube\temp\*" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  temp limpio."
}

Write-Host ""
Write-Host "=== 3. Lanzando SonarQube ===" -ForegroundColor Cyan
$bat = "C:\sonarqube\bin\windows-x86-64\StartSonar.bat"
if (-not (Test-Path $bat)) {
    Write-Host "ERROR: No existe $bat" -ForegroundColor Red
    Read-Host "Enter"; exit 1
}
Start-Process -FilePath $bat -WorkingDirectory "C:\sonarqube\bin\windows-x86-64"

Write-Host ""
Write-Host "=== 4. Esperando que suba ===" -ForegroundColor Cyan
$up = $false
for ($i = 1; $i -le 60; $i++) {
    Start-Sleep -Seconds 3
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:9000/api/system/status" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        $j = $r.Content | ConvertFrom-Json
        Write-Host ("  [{0:00}] status={1}" -f $i, $j.status) -ForegroundColor Yellow
        if ($j.status -eq "UP") {
            $up = $true
            break
        }
    } catch {
        Write-Host "." -NoNewline -ForegroundColor DarkGray
    }
}

Write-Host ""
if ($up) {
    Write-Host "*** SONARQUBE OPERACIONAL ***" -ForegroundColor Green
    Write-Host "URL: http://localhost:9000/dashboard?id=sece-backend"
    Write-Host "Login default: admin / admin"
    Start-Process "http://localhost:9000/dashboard?id=sece-backend"
} else {
    Write-Host "Timeout. Mira el log en C:\sonarqube\logs\web.log" -ForegroundColor Red
}
Write-Host ""
Read-Host "Enter para cerrar"
