# Script PowerShell pour lister les devices USB et identifier le Greaseweazle
# Usage: powershell -ExecutionPolicy Bypass -File scripts/list_usb_devices.ps1

Write-Host "=== Recherche du device Greaseweazle ===" -ForegroundColor Green
Write-Host ""

# Vérifier si usbipd est installé
$usbipd = Get-Command usbipd -ErrorAction SilentlyContinue
if (-not $usbipd) {
    Write-Host "❌ usbipd n'est pas installé" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installez-le avec:" -ForegroundColor Yellow
    Write-Host "  winget install usbipd" -ForegroundColor White
    exit 1
}

Write-Host "✅ usbipd est installé" -ForegroundColor Green
Write-Host ""

# Lister les devices USB
Write-Host "Liste des devices USB:" -ForegroundColor Cyan
Write-Host ""

$output = usbipd list 2>&1
$output

Write-Host ""
Write-Host "=== Recherche du Greaseweazle ===" -ForegroundColor Cyan
Write-Host ""

# Chercher Greaseweazle dans la sortie
$greaseweazleFound = $false
$lines = $output -split "`n"

foreach ($line in $lines) {
    if ($line -match "Greaseweazle|COM10|FTDI|CH340|USB Serial|Serial Port") {
        Write-Host $line -ForegroundColor Yellow
        $greaseweazleFound = $true
        
        # Extraire le BUSID (format: "BUSID  Description  State")
        if ($line -match "^\s*([\d-]+)") {
            $busid = $matches[1]
            Write-Host ""
            Write-Host "✅ Device trouvé! BUSID: $busid" -ForegroundColor Green
            Write-Host ""
            Write-Host "Pour attacher à WSL, exécutez:" -ForegroundColor Cyan
            Write-Host "  usbipd attach --wsl --busid $busid" -ForegroundColor White
        }
    }
}

if (-not $greaseweazleFound) {
    Write-Host "⚠️  Greaseweazle non trouvé automatiquement" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Recherchez dans la liste ci-dessus:" -ForegroundColor Cyan
    Write-Host "  - Un device avec 'COM10' (votre port série)" -ForegroundColor White
    Write-Host "  - Un device USB série (FTDI, CH340, etc.)" -ForegroundColor White
    Write-Host ""
    Write-Host "Le BUSID est le premier champ (ex: 1-5, 2-3, etc.)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== Alternative: Lister les ports COM ===" -ForegroundColor Cyan
Write-Host ""

# Lister les ports COM pour référence
$comPorts = Get-WmiObject Win32_SerialPort | Select-Object DeviceID, Description, Name
if ($comPorts) {
    Write-Host "Ports COM disponibles:" -ForegroundColor Cyan
    $comPorts | ForEach-Object {
        if ($_.DeviceID -eq "COM10") {
            Write-Host "  $($_.DeviceID) - $($_.Description) - $($_.Name)" -ForegroundColor Yellow
        } else {
            Write-Host "  $($_.DeviceID) - $($_.Description) - $($_.Name)" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "  Aucun port COM trouvé" -ForegroundColor Gray
}

