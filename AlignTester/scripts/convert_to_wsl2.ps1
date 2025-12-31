# Script PowerShell pour convertir Debian en WSL 2
# Usage: powershell -ExecutionPolicy Bypass -File scripts/convert_to_wsl2.ps1
# Note: Doit être exécuté en tant qu'administrateur

$WSL_DISTRO = "Debian"

Write-Host "=== Conversion de Debian en WSL 2 ===" -ForegroundColor Green
Write-Host ""

# Vérifier les privilèges administrateur
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  ERREUR: Ce script doit être exécuté en tant qu'administrateur" -ForegroundColor Red
    Write-Host ""
    Write-Host "Faites un clic droit sur PowerShell et choisissez 'Exécuter en tant qu'administrateur'" -ForegroundColor Yellow
    exit 1
}

# Vérifier la version actuelle
Write-Host "Vérification de la version actuelle..." -ForegroundColor Yellow
$wslList = wsl --list --verbose 2>&1

Write-Host $wslList
Write-Host ""

$currentVersion = ($wslList | Select-String "$WSL_DISTRO\s+\w+\s+(\d+)" | ForEach-Object { $_.Matches.Groups[1].Value })
if ($currentVersion -eq "2") {
    Write-Host "✅ Debian est déjà en WSL 2 !" -ForegroundColor Green
    Write-Host ""
    Write-Host "Vous pouvez maintenant utiliser usbipd :" -ForegroundColor Cyan
    Write-Host "  usbipd bind --busid 3-1" -ForegroundColor White
    Write-Host "  usbipd attach --wsl --busid 3-1" -ForegroundColor White
    exit 0
}

Write-Host "Debian est actuellement en WSL $currentVersion" -ForegroundColor Yellow
Write-Host ""

# Arrêter WSL
Write-Host "Arrêt de WSL..." -ForegroundColor Yellow
wsl --shutdown 2>&1 | Out-Null
Start-Sleep -Seconds 2
Write-Host "  ✅ WSL arrêté" -ForegroundColor Green
Write-Host ""

# Convertir en WSL 2
Write-Host "Conversion de Debian en WSL 2..." -ForegroundColor Yellow
Write-Host "  ⏳ Cette opération peut prendre 2-5 minutes, veuillez patienter..." -ForegroundColor Cyan
Write-Host ""

$convertResult = wsl --set-version $WSL_DISTRO 2 2>&1

# Vérifier le résultat
if ($LASTEXITCODE -eq 0 -or $convertResult -match "completed|terminé|succès|success") {
    Write-Host "  ✅ Conversion terminée avec succès !" -ForegroundColor Green
} else {
    Write-Host "  ❌ Erreur lors de la conversion:" -ForegroundColor Red
    Write-Host $convertResult -ForegroundColor Red
    exit 1
}

Write-Host ""

# Vérifier la nouvelle version
Write-Host "Vérification de la nouvelle version..." -ForegroundColor Yellow
$wslListNew = wsl --list --verbose 2>&1
Write-Host $wslListNew
Write-Host ""

$newVersion = ($wslListNew | Select-String "$WSL_DISTRO\s+\w+\s+(\d+)" | ForEach-Object { $_.Matches.Groups[1].Value })
if ($newVersion -eq "2") {
    Write-Host "✅ Debian est maintenant en WSL 2 !" -ForegroundColor Green
    Write-Host ""
    Write-Host "Prochaines étapes:" -ForegroundColor Cyan
    Write-Host "  1. Redémarrer WSL : wsl -d Debian" -ForegroundColor White
    Write-Host "  2. Attacher le device : usbipd bind --busid 3-1" -ForegroundColor White
    Write-Host "  3. Attacher à WSL : usbipd attach --wsl --busid 3-1" -ForegroundColor White
} else {
    Write-Host "⚠️  La conversion semble ne pas avoir fonctionné. Version détectée: $newVersion" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Essayez manuellement:" -ForegroundColor Cyan
    Write-Host "  wsl --set-version Debian 2" -ForegroundColor White
}







