$portName = 'COM11'
$now = Get-Date
$weekday = ([int]$now.DayOfWeek + 6) % 7
$command = 'TIME,{0},{1},{2},{3},{4},{5},{6}' -f `
    $now.Year, $now.Month, $now.Day, $now.Hour, $now.Minute, $now.Second, $weekday

$port = [System.IO.Ports.SerialPort]::new($portName, 115200, 'None', 8, 'One')
$port.NewLine = "`n"
$port.ReadTimeout = 2000
try {
    $port.Open()
    Start-Sleep -Milliseconds 800
    $port.WriteLine($command)
    Write-Host "RoundyPi synchronisé sur $($now.ToString('yyyy-MM-dd HH:mm:ss')) via $portName"
}
finally {
    if ($port.IsOpen) { $port.Close() }
}
