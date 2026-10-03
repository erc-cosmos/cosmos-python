param(
    [Parameter(Mandatory=$true, Position=0)][string]$Repository,
    [string]$PythonVersion = '3.11',
    [switch]$DryRun,
    [switch]$FilesOnly
)
$ErrorActionPreference = 'Stop'
$Target = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Repository)
# Child PowerShell processes keep bootstrap's exit and environment changes isolated.
$Shell = (Get-Process -Id $PID).Path
& $Shell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'bootstrap.ps1')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Shell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'cosmos.ps1') setup
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$Options = @($Target, '--python', $PythonVersion)
if ($DryRun) { $Options += '--dry-run' }
if ($FilesOnly) { $Options += '--files-only' }
& $Shell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'cosmos.ps1') run python (Join-Path $PSScriptRoot 'setup_repo.py') @Options
exit $LASTEXITCODE
