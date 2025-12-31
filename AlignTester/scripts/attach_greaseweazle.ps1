# Script PowerShell pour attacher le Greaseweazle à WSL
# Usage: powershell -ExecutionPolicy Bypass -File scripts/attach_greaseweazle.ps1
# Note: Doit être exécuté en tant qu'administrateur

$BUSID = "3-1"

Write-Host "=== Attacher Greaseweazle (BUSID: $BUSID) à WSL ===" -ForegroundColor Green
Write-Host ""

# Étape 1: Bind le device
Write-Host "1. Liaison (bind) du device..." -ForegroundColor Yellow
$bindResult = usbipd bind --busid $BUSID 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Device lié avec succès" -ForegroundColor Green
} else {
    # Si le device est déjà lié, c'est OK
    if ($bindResult -match "already|déjà") {
        Write-Host "   ℹ️  Device déjà lié (normal)" -ForegroundColor Cyan
    } else {
        Write-Host "   ❌ Erreur lors de la liaison: $bindResult" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Étape 2: Attacher à WSL
Write-Host "2. Attachement à WSL..." -ForegroundColor Yellow
$attachResult = usbipd attach --wsl --busid $BUSID 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Device attaché à WSL avec succès!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Dans WSL, vérifiez avec:" -ForegroundColor Cyan
    Write-Host "  ls -la /dev/ttyACM*" -ForegroundColor White
    Write-Host ""
    Write-Host "Puis utilisez:" -ForegroundColor Cyan
    Write-Host "  gw info" -ForegroundColor White
    Write-Host "  gw align --device /dev/ttyACM0 --tracks c=40:h=0 --reads 10" -ForegroundColor White
} else {
    Write-Host "   ❌ Erreur lors de l'attachement: $attachResult" -ForegroundColor Red
    exit 1
}

