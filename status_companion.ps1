param(
    [string]$PortName = 'COM11'
)

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

function Send-RoundyCommand {
    param(
        [string]$Command,
        [string]$Port
    )

    $serial = New-Object System.IO.Ports.SerialPort $Port, 115200, None, 8, One
    $serial.WriteTimeout = 3000
    $serial.ReadTimeout = 500
    $serial.NewLine = "`n"
    try {
        $serial.Open()
        Start-Sleep -Milliseconds 250
        $serial.WriteLine($Command)
        return "Sent $Command to $Port"
    }
    catch {
        return "ERROR: $($_.Exception.Message)"
    }
    finally {
        if ($serial.IsOpen) {
            $serial.Close()
        }
    }
}

$form = New-Object System.Windows.Forms.Form
$form.Text = 'RoundyPi Status Companion'
$form.Size = New-Object System.Drawing.Size(330, 500)
$form.StartPosition = 'CenterScreen'
$form.FormBorderStyle = 'FixedDialog'
$form.MaximizeBox = $false
$form.BackColor = [System.Drawing.Color]::FromArgb(18, 22, 35)

$title = New-Object System.Windows.Forms.Label
$title.Text = 'RoundyPi Status'
$title.ForeColor = [System.Drawing.Color]::White
$title.Font = New-Object System.Drawing.Font('Segoe UI', 16, [System.Drawing.FontStyle]::Bold)
$title.Location = New-Object System.Drawing.Point(22, 18)
$title.Size = New-Object System.Drawing.Size(280, 34)
$form.Controls.Add($title)

$portLabel = New-Object System.Windows.Forms.Label
$portLabel.Text = 'Port'
$portLabel.ForeColor = [System.Drawing.Color]::LightGray
$portLabel.Font = New-Object System.Drawing.Font('Segoe UI', 9)
$portLabel.Location = New-Object System.Drawing.Point(24, 62)
$portLabel.Size = New-Object System.Drawing.Size(40, 24)
$form.Controls.Add($portLabel)

$portBox = New-Object System.Windows.Forms.TextBox
$portBox.Text = $PortName
$portBox.Location = New-Object System.Drawing.Point(65, 59)
$portBox.Size = New-Object System.Drawing.Size(80, 24)
$form.Controls.Add($portBox)

$statusLabel = New-Object System.Windows.Forms.Label
$statusLabel.Text = 'Ready'
$statusLabel.ForeColor = [System.Drawing.Color]::FromArgb(168, 255, 241)
$statusLabel.Font = New-Object System.Drawing.Font('Segoe UI', 9)
$statusLabel.Location = New-Object System.Drawing.Point(24, 424)
$statusLabel.Size = New-Object System.Drawing.Size(270, 24)
$form.Controls.Add($statusLabel)

function New-StatusButton {
    param(
        [string]$Text,
        [string]$State,
        [int]$X,
        [int]$Y,
        [System.Drawing.Color]$Color
    )

    $button = New-Object System.Windows.Forms.Button
    $button.Text = $Text
    $button.Tag = $State
    $button.Location = New-Object System.Drawing.Point($X, $Y)
    $button.Size = New-Object System.Drawing.Size(130, 58)
    $button.FlatStyle = 'Flat'
    $button.FlatAppearance.BorderSize = 0
    $button.BackColor = $Color
    $button.ForeColor = [System.Drawing.Color]::White
    $button.Font = New-Object System.Drawing.Font('Segoe UI', 13, [System.Drawing.FontStyle]::Bold)
    $button.Add_Click({
        $state = $this.Tag
        $result = Send-RoundyCommand -Command "STATUS,$state" -Port $portBox.Text
        $statusLabel.Text = $result
    })
    return $button
}

function New-PetButton {
    param(
        [string]$Text,
        [string]$Command,
        [int]$X,
        [int]$Y,
        [System.Drawing.Color]$Color
    )

    $button = New-Object System.Windows.Forms.Button
    $button.Text = $Text
    $button.Tag = $Command
    $button.Location = New-Object System.Drawing.Point($X, $Y)
    $button.Size = New-Object System.Drawing.Size(130, 50)
    $button.FlatStyle = 'Flat'
    $button.FlatAppearance.BorderSize = 0
    $button.BackColor = $Color
    $button.ForeColor = [System.Drawing.Color]::White
    $button.Font = New-Object System.Drawing.Font('Segoe UI', 11, [System.Drawing.FontStyle]::Bold)
    $button.Add_Click({
        $command = $this.Tag
        $result = Send-RoundyCommand -Command $command -Port $portBox.Text
        $statusLabel.Text = $result
    })
    return $button
}

$form.Controls.Add((New-StatusButton -Text 'FREE' -State 'FREE' -X 24 -Y 100 -Color ([System.Drawing.Color]::FromArgb(30, 170, 88))))
$form.Controls.Add((New-StatusButton -Text 'BUSY' -State 'BUSY' -X 170 -Y 100 -Color ([System.Drawing.Color]::FromArgb(210, 145, 20))))
$form.Controls.Add((New-StatusButton -Text 'DND' -State 'DND' -X 24 -Y 174 -Color ([System.Drawing.Color]::FromArgb(210, 45, 65))))
$form.Controls.Add((New-StatusButton -Text 'AWAY' -State 'AWAY' -X 170 -Y 174 -Color ([System.Drawing.Color]::FromArgb(120, 90, 230))))

$petTitle = New-Object System.Windows.Forms.Label
$petTitle.Text = 'Tiny coach'
$petTitle.ForeColor = [System.Drawing.Color]::White
$petTitle.Font = New-Object System.Drawing.Font('Segoe UI', 12, [System.Drawing.FontStyle]::Bold)
$petTitle.Location = New-Object System.Drawing.Point(24, 252)
$petTitle.Size = New-Object System.Drawing.Size(260, 24)
$form.Controls.Add($petTitle)

$form.Controls.Add((New-PetButton -Text 'CHECKIN' -Command 'CHECKIN' -X 24 -Y 286 -Color ([System.Drawing.Color]::FromArgb(30, 135, 220))))
$form.Controls.Add((New-PetButton -Text 'FOCUS' -Command 'FOCUS' -X 170 -Y 286 -Color ([System.Drawing.Color]::FromArgb(210, 45, 65))))
$form.Controls.Add((New-PetButton -Text 'QUICK WIN' -Command 'WIN' -X 24 -Y 350 -Color ([System.Drawing.Color]::FromArgb(30, 170, 88))))
$form.Controls.Add((New-PetButton -Text 'REST' -Command 'REST' -X 170 -Y 350 -Color ([System.Drawing.Color]::FromArgb(120, 90, 230))))

[void]$form.ShowDialog()
