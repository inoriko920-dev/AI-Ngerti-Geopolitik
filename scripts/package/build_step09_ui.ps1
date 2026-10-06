$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

$Name = "AI-Ngerti-Geopolitik-UI-Shell"
$DistDir = Join-Path $RepoRoot "dist"
$AppDir = Join-Path $DistDir $Name
$ZipPath = Join-Path $DistDir "$Name-Windows-x64.zip"

if (Test-Path (Join-Path $RepoRoot "build")) {
    Remove-Item (Join-Path $RepoRoot "build") -Recurse -Force
}
if (Test-Path $DistDir) {
    Remove-Item $DistDir -Recurse -Force
}

uv run pyinstaller --clean --noconfirm --onedir --windowed --name $Name --paths (Join-Path $RepoRoot "src") (Join-Path $RepoRoot "scripts\package\ui_shell_entry.py")

if (-not (Test-Path $AppDir)) {
    throw "STEP 09 portable UI directory was not created: $AppDir"
}

Copy-Item (Join-Path $RepoRoot "THIRD_PARTY_NOTICES.md") (Join-Path $AppDir "THIRD_PARTY_NOTICES.md")

@"
AI Ngerti Geopolitik — SF-STEP 09 UI Shell

This build implements the real PySide6 app shell and representative frozen UI states.
It is NOT the final editor: media-engine, Gemini execution, persistence, and real render/export remain later work.
"@ | Set-Content -Path (Join-Path $AppDir "STEP09_SCOPE.txt") -Encoding UTF8

Compress-Archive -Path (Join-Path $AppDir "*") -DestinationPath $ZipPath -Force
Write-Host "STEP 09 portable UI folder: $AppDir"
Write-Host "STEP 09 portable UI ZIP: $ZipPath"
