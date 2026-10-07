# Install the saved local Python environment; no existing Python is required.
$ErrorActionPreference = 'Stop'
$Shell = (Get-Process -Id $PID).Path
# Child processes isolate bootstrap's exit and environment changes.
& $Shell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'bootstrap.ps1')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Shell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'cosmos.ps1') setup
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host 'Python is ready. From this directory, run: . .\activate.ps1'
Write-Host 'Then run: pixi run --locked python --version'
