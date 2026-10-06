$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$Exe = Join-Path $RepoRoot "dist\AI-Ngerti-Geopolitik-UI-Shell\AI-Ngerti-Geopolitik-UI-Shell.exe"
$Marker = Join-Path $RepoRoot "dist\s09-ui-smoke.txt"

if (-not (Test-Path $Exe)) {
    throw "STEP 09 executable missing: $Exe"
}
if (Test-Path $Marker) {
    Remove-Item $Marker -Force
}

$env:QT_QPA_PLATFORM = "offscreen"
$process = Start-Process -FilePath $Exe -ArgumentList @("--ui-test-mode", "--ui-state", "UI-010", "--ui-smoke-file", $Marker) -PassThru -Wait
if ($process.ExitCode -ne 0) {
    throw "STEP 09 UI executable exited with code $($process.ExitCode)"
}
if (-not (Test-Path $Marker)) {
    throw "STEP 09 UI smoke marker was not created"
}
$content = (Get-Content $Marker -Raw).Trim()
if ($content -ne "ANG_S09_UI_SMOKE_OK") {
    throw "Unexpected UI smoke marker: $content"
}
Write-Host "PASS STEP 09 portable UI shell smoke"
