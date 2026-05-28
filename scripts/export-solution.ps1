<#
.SYNOPSIS
    Export the CFR Project Management solution from the DEV Dataverse environment.

.DESCRIPTION
    Exports the unmanaged solution CFRProjectManagement, then unpacks it into
    the solution/src source directory for source control.

    PREREQUISITE: PAC auth profile for CFR PMO dev environment must be configured.
    Run: pac auth create --url https://<cfr-pmo-dev>.crm.dynamics.com --name cfr-pmo-dev
         pac auth select --name cfr-pmo-dev
    (Or use --environment flag with the target environment ID.)

    ENVIRONMENT: 731e4975-10cd-4535-b82f-1ff016e59b6c (CFR PMO Dev)
    SOLUTION:    CFRProjectManagement

.USAGE
    From the repository root:
        pwsh scripts/export-solution.ps1
    Or with explicit environment override:
        pwsh scripts/export-solution.ps1 -EnvironmentId <env-id>
#>

param(
    [string]$EnvironmentId = '731e4975-10cd-4535-b82f-1ff016e59b6c',
    [string]$SolutionName  = 'CFRProjectManagement',
    [string]$OutputDir     = 'solution/bin',
    [string]$SourceDir     = 'solution/src'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "=== CFR PMO Solution Export ===" -ForegroundColor Cyan
Write-Host "Environment : $EnvironmentId"
Write-Host "Solution    : $SolutionName"
Write-Host "Output dir  : $OutputDir"

# ── 1. Verify pac auth context ────────────────────────────────────────────────
$auth = pac auth list 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "pac auth list failed. Ensure PAC CLI is installed and authenticated."
    exit 1
}
Write-Host "PAC auth profiles available. Proceeding with environment $EnvironmentId."

# ── 2. Create output directory ────────────────────────────────────────────────
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$zipPath = Join-Path $OutputDir "$SolutionName.zip"

# ── 3. Export unmanaged solution ──────────────────────────────────────────────
Write-Host "Exporting solution..." -ForegroundColor Yellow
pac solution export `
    --name $SolutionName `
    --path $zipPath `
    --managed false `
    --overwrite `
    --environment $EnvironmentId

if ($LASTEXITCODE -ne 0) {
    Write-Error "pac solution export failed (exit $LASTEXITCODE)."
    exit 1
}
Write-Host "Export complete: $zipPath" -ForegroundColor Green

# ── 4. Unpack into source ────────────────────────────────────────────────────
Write-Host "Unpacking solution into $SourceDir..." -ForegroundColor Yellow
pac solution unpack `
    --zipfile $zipPath `
    --folder $SourceDir `
    --packagetype Unmanaged `
    --allowWrite `
    --clobber

if ($LASTEXITCODE -ne 0) {
    Write-Error "pac solution unpack failed (exit $LASTEXITCODE)."
    exit 1
}
Write-Host "Unpack complete. Bot components written to $SourceDir/botcomponents/" -ForegroundColor Green

Write-Host "=== Export complete ===" -ForegroundColor Cyan
Write-Host "Review changes in $SourceDir and commit to source control."
