$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

$Name = "AI-Ngerti-Geopolitik-Foundation"
$DistDir = Join-Path $RepoRoot "dist"
$AppDir = Join-Path $DistDir $Name
$ZipPath = Join-Path $DistDir "$Name-Windows-x64.zip"

if (Test-Path (Join-Path $RepoRoot "build")) {
    Remove-Item (Join-Path $RepoRoot "build") -Recurse -Force
}
if (Test-Path $DistDir) {
    Remove-Item $DistDir -Recurse -Force
}

uv run pyinstaller --clean --noconfirm --onedir --name $Name --paths (Join-Path $RepoRoot "src") (Join-Path $RepoRoot "scripts\package\foundation_entry.py")

if (-not (Test-Path $AppDir)) {
    throw "Portable foundation directory was not created: $AppDir"
}

Copy-Item (Join-Path $RepoRoot "THIRD_PARTY_NOTICES.md") (Join-Path $AppDir "THIRD_PARTY_NOTICES.md")

@"
AI Ngerti Geopolitik — SF-STEP 08 foundation artifact

This is NOT the product editor and NOT a final release.
It only proves the repository/package/Windows portable scaffold.
No media engine, Gemini editing, or production render stack is included.
"@ | Set-Content -Path (Join-Path $AppDir "FOUNDATION_SCOPE.txt") -Encoding UTF8

Compress-Archive -Path (Join-Path $AppDir "*") -DestinationPath $ZipPath -Force

Write-Host "Portable foundation directory: $AppDir"
Write-Host "Portable foundation ZIP: $ZipPath"
