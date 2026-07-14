$portName = 'COM11'
$sourcePath = 'C:\Users\fgobe\Documents\RoundyPi\code.py'

$bytes = [System.IO.File]::ReadAllBytes($sourcePath)
$base64 = [Convert]::ToBase64String($bytes)
$chunkSize = 240

$py = New-Object System.Text.StringBuilder
[void]$py.AppendLine('import binascii')
[void]$py.AppendLine('f = open("code.py", "wb")')
for ($i = 0; $i -lt $base64.Length; $i += $chunkSize) {
    $len = [Math]::Min($chunkSize, $base64.Length - $i)
    $chunk = $base64.Substring($i, $len)
    [void]$py.AppendLine("f.write(binascii.a2b_base64('$chunk'))")
}
[void]$py.AppendLine('f.close()')
[void]$py.AppendLine('print("UPLOAD_OK")')

$port = New-Object System.IO.Ports.SerialPort $portName, 115200, None, 8, One
$port.ReadTimeout = 500
$port.WriteTimeout = 5000
$port.NewLine = "`n"
$port.DtrEnable = $true
$port.RtsEnable = $true

try {
    $port.Open()
    Start-Sleep -Milliseconds 1200
    $port.DiscardInBuffer()

    # Stop the running program and enter paste mode in the CircuitPython REPL.
    $port.Write([string][char]3)
    Start-Sleep -Milliseconds 250
    $port.Write([string][char]3)
    Start-Sleep -Milliseconds 700
    $port.Write([string][char]5)
    Start-Sleep -Milliseconds 400

    foreach ($line in ($py.ToString() -split "`n")) {
        if ($line.Length -gt 0) {
            $port.WriteLine($line.TrimEnd("`r"))
            Start-Sleep -Milliseconds 18
        }
    }
    Start-Sleep -Milliseconds 500
    $port.Write([string][char]4)

    $deadline = (Get-Date).AddSeconds(12)
    $output = New-Object System.Text.StringBuilder
    while ((Get-Date) -lt $deadline) {
        try {
            [void]$output.Append($port.ReadExisting())
        } catch {
        }
        if ($output.ToString().Contains('UPLOAD_OK')) {
            break
        }
        Start-Sleep -Milliseconds 200
    }

    $text = $output.ToString()
    Write-Output $text
    if (-not $text.Contains('UPLOAD_OK')) {
        throw 'Upload did not report UPLOAD_OK.'
    }

    # Soft-reload so the animation starts immediately.
    $port.Write([string][char]4)
    Write-Output 'RoundyPi animation upload complete; soft reload sent.'
}
finally {
    if ($port.IsOpen) {
        $port.Close()
    }
}
