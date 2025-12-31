# Script PowerShell pour lister les ports COM et devices USB
# Usage: powershell -ExecutionPolicy Bypass -File scripts/list_com_ports.ps1

Write-Host "=== Recherche du port COM10 (Greaseweazle) ===" -ForegroundColor Green
Write-Host ""

# Méthode 1: Utiliser Get-WmiObject
Write-Host "Ports COM disponibles:" -ForegroundColor Cyan
Write-Host ""

$comPorts = Get-WmiObject Win32_SerialPort | Select-Object DeviceID, Description, Name, PNPDeviceID | Sort-Object DeviceID

if ($comPorts) {
    foreach ($port in $comPorts) {
        if ($port.DeviceID -eq "COM10") {
            Write-Host "✅ $($port.DeviceID) - $($port.Description)" -ForegroundColor Green
            Write-Host "   Nom: $($port.Name)" -ForegroundColor Gray
            Write-Host "   PNP: $($port.PNPDeviceID)" -ForegroundColor Gray
        } else {
            Write-Host "   $($port.DeviceID) - $($port.Description)" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "  Aucun port COM trouvé" -ForegroundColor Yellow
}

Write-Host ""

# Méthode 2: Utiliser Get-PnpDevice
Write-Host "Devices USB série (PNP):" -ForegroundColor Cyan
Write-Host ""

$usbDevices = Get-PnpDevice | Where-Object {
    $_.Class -eq "Ports" -or 
    $_.FriendlyName -match "COM|Serial|USB.*Serial|FTDI|CH340|Greaseweazle"
} | Select-Object FriendlyName, InstanceId, Status | Sort-Object FriendlyName

if ($usbDevices) {
    foreach ($device in $usbDevices) {
        if ($device.FriendlyName -match "COM10|Greaseweazle") {
            Write-Host "✅ $($device.FriendlyName)" -ForegroundColor Green
            Write-Host "   Statut: $($device.Status)" -ForegroundColor Gray
            Write-Host "   ID: $($device.InstanceId)" -ForegroundColor Gray
        } else {
            Write-Host "   $($device.FriendlyName) - $($device.Status)" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "  Aucun device USB série trouvé" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Si usbipd est installé ===" -ForegroundColor Cyan
Write-Host ""

$usbipd = Get-Command usbipd -ErrorAction SilentlyContinue
if ($usbipd) {
    Write-Host "✅ usbipd est disponible" -ForegroundColor Green
    Write-Host ""
    Write-Host "Liste des devices USB (usbipd):" -ForegroundColor Cyan
    usbipd list 2>&1
    Write-Host ""
    Write-Host "Pour attacher le Greaseweazle à WSL:" -ForegroundColor Yellow
    Write-Host "  usbipd attach --wsl --busid <BUSID>" -ForegroundColor White
    Write-Host ""
    Write-Host "Note: Le BUSID se trouve dans la liste ci-dessus (ex: 1-5, 2-3)" -ForegroundColor Gray
} else {
    Write-Host "⚠️  usbipd n'est pas installé" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Pour l'installer:" -ForegroundColor Cyan
    Write-Host "  winget install usbipd" -ForegroundColor White
    Write-Host ""
    Write-Host "Une fois installé, vous pourrez:" -ForegroundColor Cyan
    Write-Host "  1. Lister les devices: usbipd list" -ForegroundColor White
    Write-Host "  2. Attacher à WSL: usbipd attach --wsl --busid <BUSID>" -ForegroundColor White
}

Write-Host ""
Write-Host "=== Alternative: Utiliser directement gw.exe Windows ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Vous pouvez utiliser directement le gw.exe Windows qui détecte COM10:" -ForegroundColor Yellow
Write-Host "  cd 'S:\Divers SSD M2\Test D7\Greaseweazle\greaseweazle-1.23b'" -ForegroundColor White
Write-Host "  .\gw.exe info" -ForegroundColor White
Write-Host "  .\gw.exe align --device COM10 --tracks c=40:h=0 --reads 10" -ForegroundColor White

