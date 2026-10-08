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

Copy-Item (Join-Path $RepoRoot "THIRD_PARTY_NOTICES.md") (Join-Path $AppDir "THIRD_PARTY_NOTICES.md")

@"
AI Ngerti Geopolitik — SF-STEP 10 packaged media qualification smoke

This is not a user-facing final application.
It proves the packaged Python/domain/application/infrastructure path can use an
external system FFmpeg/ffprobe toolchain to import, edit, save, seek-preview and export.
FFmpeg is NOT bundled in this qualification artifact.
SF12-T10 can test nine typed export profiles through --sf12-t10 with external FFmpeg.
Neither this command-line harness nor the separate STEP09 UI shell is a final editor;
product GUI export remains disabled and native redistribution approval is pending.
"@ | Set-Content -Path (Join-Path $AppDir "STEP10_MEDIA_SMOKE_SCOPE.txt") -Encoding UTF8

Compress-Archive -Path (Join-Path $AppDir "*") -DestinationPath $ZipPath -Force
Write-Host "STEP 10 packaged media smoke: $AppDir"
Write-Host "STEP 10 packaged media ZIP: $ZipPath"
