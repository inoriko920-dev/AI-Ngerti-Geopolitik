$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Exe = Join-Path $RepoRoot "dist\AI-Ngerti-Geopolitik-Foundation\AI-Ngerti-Geopolitik-Foundation.exe"

if (-not (Test-Path $Exe)) {
    throw "Foundation executable missing: $Exe"
}

$Output = (& $Exe 2>&1 | Out-String).Trim()
if ($LASTEXITCODE -ne 0) {
    throw "Foundation executable exited with code $LASTEXITCODE. Output: $Output"
}
if ($Output -notmatch "foundation ready") {
    throw "Unexpected foundation output: $Output"
}

Write-Host "PASS portable foundation smoke"
Write-Host $Output
