$deadline = (Get-Date).AddSeconds(30)
$last = ''

while ((Get-Date) -lt $deadline) {
    $vols = Get-CimInstance Win32_LogicalDisk |
        Where-Object { $_.VolumeName -match 'RPI-RP2|CIRCUITPY' } |
        ForEach-Object { "$($_.DeviceID):$($_.VolumeName)" }

    $devs = Get-PnpDevice -PresentOnly |
        Where-Object {
            $_.FriendlyName -match 'Unknown|RP2|Pico|Circuit|Serial|CIRCUITPY' -or
            $_.InstanceId -match 'VID_239A|VID_2E8A|VID_0000'
        } |
        ForEach-Object { "$($_.Status) $($_.Class) $($_.FriendlyName)" }

    $state = (($vols + $devs) -join "`n")
    if ($state -ne $last) {
        Write-Output '--- change ---'
        if ($state) {
            Write-Output $state
        } else {
            Write-Output '(nothing)'
        }
        $last = $state
    }
    Start-Sleep -Milliseconds 500
}
