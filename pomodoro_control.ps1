param(
    [ValidateSet('start', 'pause', 'resume', 'reset', 'skip', 'focus', 'break', 'long')]
    [string]$Command = 'start',
    [string]$PortName = 'COM11'
)

$message = $Command.ToUpperInvariant()
$port = New-Object System.IO.Ports.SerialPort $PortName, 115200, None, 8, One
$port.WriteTimeout = 3000
$port.ReadTimeout = 500
$port.NewLine = "`n"

try {
    $port.Open()
    Start-Sleep -Milliseconds 300
    $port.WriteLine($message)
    Write-Output "Pomodoro command sent: $message via $PortName"
}
finally {
    if ($port.IsOpen) {
        $port.Close()
    }
}
