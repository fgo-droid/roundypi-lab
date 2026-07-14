param(
    [Parameter(Mandatory = $true)]
    [string]$AppPath,
    [string]$Drive = 'D:'
)

$source = Resolve-Path -LiteralPath $AppPath
$target = Join-Path $Drive 'code.py'
$sourceDir = Split-Path -Parent $source.Path

if (-not (Test-Path -LiteralPath $target.Substring(0, 2))) {
    throw "Target drive $Drive is not available. Is CIRCUITPY mounted?"
}

Copy-Item -LiteralPath $source.Path -Destination $target -Force
Write-Output "Installed $($source.Path) to $target"

$support = Join-Path $sourceDir '_roundypi.py'
if (Test-Path -LiteralPath $support) {
    Copy-Item -LiteralPath $support -Destination (Join-Path $Drive '_roundypi.py') -Force
    Write-Output "Installed shared support _roundypi.py"
}
