param(
    [Parameter(Mandatory=$true)][string]$Fixture,
    [Parameter(Mandatory=$true)][string]$EvidenceDir
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Exe = Join-Path $RepoRoot "dist-s10\AI-Ngerti-Geopolitik-S10-Media-Smoke\AI-Ngerti-Geopolitik-S10-Media-Smoke.exe"
$OutputDir = Join-Path $EvidenceDir "packaged_media_smoke"

if (-not (Test-Path $Exe)) { throw "STEP 10 packaged media smoke executable missing: $Exe" }
if (Test-Path $OutputDir) { Remove-Item $OutputDir -Recurse -Force }

$Output = (& $Exe --fixture $Fixture --output-dir $OutputDir 2>&1 | Out-String)
if ($LASTEXITCODE -ne 0) { throw "STEP 10 packaged media smoke failed with exit code $LASTEXITCODE. Output: $Output" }
if ($Output -notmatch "ANG_S10_PACKAGED_MEDIA_SMOKE_OK") { throw "STEP 10 packaged media smoke token missing. Output: $Output" }

$Output | Set-Content -Path (Join-Path $EvidenceDir "16_packaged_media_smoke.txt") -Encoding UTF8
Write-Host "PASS STEP 10 packaged media smoke"
Write-Host $Output
