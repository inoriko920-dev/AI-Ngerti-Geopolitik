$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RepoRoot

$Name = "AI-Ngerti-Geopolitik-S10-Media-Smoke"
$DistDir = Join-Path $RepoRoot "dist-s10"
$AppDir = Join-Path $DistDir $Name
$ZipPath = Join-Path $DistDir "$Name-Windows-x64.zip"

if (Test-Path (Join-Path $RepoRoot "build-s10")) { Remove-Item (Join-Path $RepoRoot "build-s10") -Recurse -Force }
if (Test-Path $DistDir) { Remove-Item $DistDir -Recurse -Force }

uv run pyinstaller --clean --noconfirm --onedir --console --workpath (Join-Path $RepoRoot "build-s10") --distpath $DistDir --name $Name --paths (Join-Path $RepoRoot "src") (Join-Path $RepoRoot "scripts\package\step10_media_smoke_entry.py")

if (-not (Test-Path $AppDir)) { throw "STEP 10 packaged media smoke directory was not created: $AppDir" }

@"
AI Ngerti Geopolitik — SF-STEP 10 packaged media qualification smoke

This is not a user-facing final application.
It proves the packaged Python/domain/application/infrastructure path can use an
external system FFmpeg/ffprobe toolchain to import, edit, save, seek-preview and export.
FFmpeg is NOT bundled in this qualification artifact.
"@ | Set-Content -Path (Join-Path $AppDir "STEP10_MEDIA_SMOKE_SCOPE.txt") -Encoding UTF8

Compress-Archive -Path (Join-Path $AppDir "*") -DestinationPath $ZipPath -Force
Write-Host "STEP 10 packaged media smoke: $AppDir"
Write-Host "STEP 10 packaged media ZIP: $ZipPath"
