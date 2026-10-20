# Connects a USB phone or emulator to the API tunnel: adb reverse tcp:8000 -> PC 127.0.0.1:8000.
# The SSH tunnel (see README.md) must be started separately.
$ErrorActionPreference = 'Stop'
$props = Join-Path $PSScriptRoot 'local.properties'
if (-not (Test-Path $props)) { Write-Host "local.properties not found. Open the project in Android Studio once."; exit 1 }
$line = Get-Content $props | Where-Object { $_ -match '^sdk\.dir=' } | Select-Object -First 1
if (-not $line) { Write-Host "sdk.dir missing in local.properties."; exit 1 }
# local.properties escapes ':' and '\' (D\:\\android studio)
$sdk = ($line -replace '^sdk\.dir=', '') -replace '\\(.)', '$1'
$adb = Join-Path $sdk 'platform-tools\adb.exe'
if (-not (Test-Path $adb)) { Write-Host "adb not found at $adb"; exit 1 }

& $adb devices
$devices = & $adb devices | Select-Object -Skip 1 | Where-Object { $_ -match '\tdevice$' }
if (-not $devices) {
    Write-Host "No device connected. Plug in the phone (USB debugging on) or start the emulator, then run this again."
    exit 2
}
& $adb reverse tcp:8000 tcp:8000
if ($LASTEXITCODE -ne 0) { Write-Host "adb reverse failed."; exit 1 }
Write-Host "OK: the device's 127.0.0.1:8000 now goes to this PC's 127.0.0.1:8000. Press Run in Android Studio."
