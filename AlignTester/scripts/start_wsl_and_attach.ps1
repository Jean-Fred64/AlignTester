# Script PowerShell pour démarrer WSL et attacher le Greaseweazle
# Usage: powershell -ExecutionPolicy Bypass -File scripts/start_wsl_and_attach.ps1
# Note: Doit être exécuté en tant qu'administrateur

$BUSID = "3-1"
$WSL_DISTRO = "Debian"  # Ajustez selon votre distribution WSL

Write-Host "=== Démarrer WSL et attacher Greaseweazle ===" -ForegroundColor Green
Write-Host ""

# Vérifier la version de WSL
Write-Host "Vérification de la version WSL..." -ForegroundColor Yellow
$wslList = wsl --list --verbose 2>&1
if ($LASTEXITCODE -ne 0) {
    $wslList = wsl -l -v 2>&1
}

Write-Host $wslList
Write-Host ""

# Vérifier si la distribution est en WSL 2
$isWSL2 = $wslList -match "2\s+$WSL_DISTRO|$WSL_DISTRO\s+2"
if (-not $isWSL2) {
    Write-Host "⚠️  ATTENTION: Votre distribution doit être en WSL 2 pour usbipd" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Pour convertir en WSL 2:" -ForegroundColor Cyan
    Write-Host "  wsl --set-version $WSL_DISTRO 2" -ForegroundColor White
    Write-Host ""
    Write-Host "Ou vérifiez la version avec:" -ForegroundColor Cyan
    Write-Host "  wsl --list --verbose" -ForegroundColor White
    Write-Host ""
}

# Démarrer WSL explicitement
Write-Host "Démarrage de WSL ($WSL_DISTRO)..." -ForegroundColor Yellow
$wslStart = wsl -d $WSL_DISTRO echo "WSL démarré" 2>&1
Write-Host "  $wslStart" -ForegroundColor Gray
Write-Host ""

# Attendre un peu pour que WSL soit complètement démarré
Start-Sleep -Seconds 2

# Vérifier que le device est lié
Write-Host "Vérification que le device est lié..." -ForegroundColor Yellow
$bindCheck = usbipd list 2>&1 | Select-String "3-1"
if ($bindCheck -match "Shared|Attached") {
    Write-Host "  ✅ Device déjà lié" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Device non lié, liaison en cours..." -ForegroundColor Yellow
    $bindResult = usbipd bind --busid $BUSID 2>&1
    if ($LASTEXITCODE -eq 0 -or $bindResult -match "already|déjà") {
        Write-Host "  ✅ Device lié" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Erreur: $bindResult" -ForegroundColor Red
    }
}

Write-Host ""

# Attacher à WSL
Write-Host "Attachement à WSL..." -ForegroundColor Yellow
$attachResult = usbipd attach --wsl --busid $BUSID 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Device attaché à WSL avec succès!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Dans WSL, vérifiez avec:" -ForegroundColor Cyan
    Write-Host "  ls -la /dev/ttyACM*" -ForegroundColor White
    Write-Host ""
    Write-Host "Si le device apparaît, vous pouvez utiliser:" -ForegroundColor Cyan
    Write-Host "  gw info" -ForegroundColor White
    Write-Host "  gw align --device /dev/ttyACM0 --tracks c=40:h=0 --reads 10" -ForegroundColor White
} else {
    Write-Host "  ❌ Erreur: $attachResult" -ForegroundColor Red
    Write-Host ""
    Write-Host "Solutions possibles:" -ForegroundColor Yellow
    Write-Host "  1. Vérifiez que WSL 2 est actif: wsl --list --verbose" -ForegroundColor White
    Write-Host "  2. Gardez un terminal WSL ouvert pendant l'attachement" -ForegroundColor White
    Write-Host "  3. Vérifiez que usbip est installé dans WSL: sudo apt install usbip" -ForegroundColor White
}

