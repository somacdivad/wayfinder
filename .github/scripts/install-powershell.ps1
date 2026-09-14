$ErrorActionPreference = 'Stop'
$version = '7.6.6'
$archive = Join-Path $env:RUNNER_TEMP "powershell-$version-win-x64.zip"
$destination = Join-Path $env:RUNNER_TEMP "powershell-$version"
$expected = '02FE458BE20493FBDF43F61EA20610B811EE6C738AB1676C61B9CFCD1A33C860'
$url = "https://github.com/PowerShell/PowerShell/releases/download/v$version/PowerShell-$version-win-x64.zip"

Invoke-WebRequest -Uri $url -OutFile $archive
$actual = (Get-FileHash -Algorithm SHA256 -Path $archive).Hash
if ($actual -ne $expected) {
    throw "PowerShell archive SHA-256 differs: $actual"
}
New-Item -ItemType Directory -Path $destination | Out-Null
Expand-Archive -LiteralPath $archive -DestinationPath $destination
Add-Content -LiteralPath $env:GITHUB_PATH -Value $destination
