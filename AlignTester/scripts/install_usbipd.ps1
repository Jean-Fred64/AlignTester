# Script PowerShell pour installer usbipd
# Usage: powershell -ExecutionPolicy Bypass -File scripts/install_usbipd.ps1
# Note: Doit être exécuté en tant qu'administrateur

Write-Host "=== Installation de usbipd ===" -ForegroundColor Green
Write-Host ""

# Vérifier si winget est disponible
$winget = Get-Command winget -ErrorAction SilentlyContinue
if (-not $winget) {
    Write-Host "❌ winget n'est pas disponible" -ForegroundColor Red
    Write-Host ""
    Write-Host "winget est inclus avec Windows 10/11 depuis la version 1809" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternatives:" -ForegroundColor Cyan
    Write-Host "1. Mettre à jour Windows" -ForegroundColor White
    Write-Host "2. Installer winget depuis le Microsoft Store" -ForegroundColor White
    Write-Host "3. Utiliser directement gw.exe Windows (plus simple)" -ForegroundColor White
    exit 1
}

Write-Host "✅ winget est disponible" -ForegroundColor Green
Write-Host ""

# Vérifier si usbipd est déjà installé
$usbipd = Get-Command usbipd -ErrorAction SilentlyContinue
if ($usbipd) {
    Write-Host "✅ usbipd est déjà installé" -ForegroundColor Green
    Write-Host "   Emplacement: $($usbipd.Source)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Vous pouvez maintenant utiliser:" -ForegroundColor Cyan
    Write-Host "  usbipd list" -ForegroundColor White
    exit 0
}

Write-Host "Installation de usbipd..." -ForegroundColor Yellow
Write-Host ""

# Installer usbipd
try {
    $installOutput = winget install usbipd --accept-package-agreements --accept-source-agreements 2>&1
    Write-Host $installOutput
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ usbipd installé avec succès!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Vous pouvez maintenant utiliser:" -ForegroundColor Cyan
        Write-Host "  usbipd list" -ForegroundColor White
        Write-Host ""
        Write-Host "Note: Vous devrez peut-être redémarrer PowerShell ou ajouter au PATH" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "❌ Erreur lors de l'installation" -ForegroundColor Red
        Write-Host "Vérifiez que vous exécutez PowerShell en tant qu'administrateur" -ForegroundColor Yellow
    }
} catch {
    Write-Host ""
    Write-Host "❌ Erreur: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Essayez d'installer manuellement:" -ForegroundColor Yellow
    Write-Host "  winget install usbipd" -ForegroundColor White
}

