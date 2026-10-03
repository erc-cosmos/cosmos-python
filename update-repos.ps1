param(
    [Parameter(Mandatory=$true, Position=0)][string[]]$Repositories,
    [switch]$DryRun,
    [switch]$Adopt,
    [switch]$Sync
)
$ErrorActionPreference = 'Stop'
$Shell = (Get-Process -Id $PID).Path
& $Shell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'bootstrap.ps1')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $Shell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'cosmos.ps1') setup
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
$Options = @()
if ($DryRun) { $Options += '--dry-run' }
if ($Adopt) { $Options += '--adopt' }
if ($Sync) { $Options += '--sync' }
& (Join-Path $PSScriptRoot '.pixi/envs/default/python.exe') (Join-Path $PSScriptRoot 'update_repos.py') @Options @Repositories
exit $LASTEXITCODE
