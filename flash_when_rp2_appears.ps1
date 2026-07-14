$firmware = 'C:\Users\fgobe\Documents\RoundyPi\circuitpython-10.2.1-pico.uf2'
$deadline = (Get-Date).AddSeconds(45)

while ((Get-Date) -lt $deadline) {
    $vol = Get-CimInstance Win32_LogicalDisk |
        Where-Object { $_.VolumeName -eq 'RPI-RP2' } |
        Select-Object -First 1

    if ($vol) {
        $drive = $vol.DeviceID + '\'
        Write-Output "RPI-RP2 detected on $drive"
        Copy-Item -LiteralPath $firmware -Destination $drive -Force
        Write-Output "Firmware copied."
        exit 0
    }

    Start-Sleep -Milliseconds 200
}

throw 'RPI-RP2 did not appear within 45 seconds.'
