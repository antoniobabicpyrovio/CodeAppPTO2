<#
.SYNOPSIS
    Pack and import the CFR Project Management solution into a target Dataverse environment.

.DESCRIPTION
    Packs the solution/src source directory into a ZIP, then imports it to the
    specified target environment (Dev, UAT, or Prod).

    PREREQUISITE: PAC auth profile for the target environment must be configured.
    PREREQUISITE: solution/src must be up-to-date (run export-solution.ps1 first
                  or ensure working tree matches desired state).

    DEFAULT TARGET: 731e4975-10cd-4535-b82f-1ff016e59b6c (CFR PMO Dev)
    Change -EnvironmentId to target UAT or Prod.

.USAGE
    From the repository root:
        pwsh scripts/import-solution.ps1
    Target a different environment:
        pwsh scripts/import-solution.ps1 -EnvironmentId <uat-env-id>
    Override publish after import (default: true):
        pwsh scripts/import-solution.ps1 -PublishAfterImport $false
#>

param(
    [string]$EnvironmentId       = '731e4975-10cd-4535-b82f-1ff016e59b6c',
    [string]$SolutionName        = 'CFRProjectManagement',
    [string]$BinDir              = 'solution/bin',
    [string]$SourceDir           = 'solution/src',
    [bool]  $PublishAfterImport  = $true
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "=== CFR PMO Solution Import ===" -ForegroundColor Cyan
Write-Host "Environment : $EnvironmentId"
Write-Host "Solution    : $SolutionName"

# ── 1. Verify pac auth context ────────────────────────────────────────────────
$auth = pac auth list 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "pac auth list failed. Ensure PAC CLI is installed and authenticated."
    exit 1
}
Write-Host "PAC auth available. Proceeding."

# ── 2. Pack solution from source ──────────────────────────────────────────────
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null
$zipPath = Join-Path $BinDir "$SolutionName.zip"

Write-Host "Packing solution from $SourceDir..." -ForegroundColor Yellow
pac solution pack `
    --zipfile $zipPath `
    --folder $SourceDir `
    --packagetype Unmanaged

if ($LASTEXITCODE -ne 0) {
    Write-Error "pac solution pack failed (exit $LASTEXITCODE)."
    exit 1
}
Write-Host "Pack complete: $zipPath" -ForegroundColor Green

# ── 3. Import to target environment ──────────────────────────────────────────
Write-Host "Importing solution to environment $EnvironmentId..." -ForegroundColor Yellow
pac solution import `
    --path $zipPath `
    --environment $EnvironmentId `
    --activate-plugins `
    --async

if ($LASTEXITCODE -ne 0) {
    Write-Error "pac solution import failed (exit $LASTEXITCODE)."
    exit 1
}
Write-Host "Import complete." -ForegroundColor Green

# ── 4. Publish customizations ────────────────────────────────────────────────
if ($PublishAfterImport) {
    Write-Host "Publishing all customizations..." -ForegroundColor Yellow
    pac solution publish --environment $EnvironmentId
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "pac solution publish returned exit $LASTEXITCODE. Check for publish errors."
    } else {
        Write-Host "Publish complete." -ForegroundColor Green
    }
}

Write-Host "=== Import complete ===" -ForegroundColor Cyan
