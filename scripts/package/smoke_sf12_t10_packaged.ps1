param(
    [Parameter(Mandatory=$true)][string]$Fixture,
    [Parameter(Mandatory=$true)][string]$EvidenceDir
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$AppDir = Join-Path $RepoRoot "dist-s10\AI-Ngerti-Geopolitik-S10-Media-Smoke"
$Exe = Join-Path $AppDir "AI-Ngerti-Geopolitik-S10-Media-Smoke.exe"
$Target = Join-Path $EvidenceDir "t10_packaged_exports"
if (-not (Test-Path $Exe)) { throw "T10_PACKAGED_EXECUTABLE_MISSING" }
if (-not (Test-Path (Join-Path $AppDir "THIRD_PARTY_NOTICES.md"))) {
    throw "T10_THIRD_PARTY_NOTICES_MISSING"
}
# Packaging contract: binaries from Chocolatey remain external to ZIP.
$Bundled = @(Get-ChildItem -Path $AppDir -Recurse -File | Where-Object {
    $_.Name -match '^(ffmpeg|ffprobe|ffplay)\.exe$|^libx26[45].*\.dll$'
})
if ($Bundled.Count -ne 0) { throw "T10_NATIVE_FFMPEG_BUNDLED_WITHOUT_ADR" }
if (Test-Path $Target) { Remove-Item $Target -Recurse -Force }
$Output = (& $Exe --fixture (Resolve-Path $Fixture) --output-dir $Target --sf12-t10 2>&1 | Out-String)
if ($LASTEXITCODE -ne 0) { throw "T10_PACKAGED_EXPORT_FAILED: $LASTEXITCODE; $Output" }
if ($Output -notmatch "ANG_SF12_T10_PACKAGED_EXPORT_QUALIFICATION_OK") {
    throw "T10_PACKAGED_QUALIFICATION_TOKEN_MISSING"
}
$Report = Join-Path $Target "sf12_t10_packaged_qualification.json"
if (-not (Test-Path $Report)) { throw "T10_EVIDENCE_MISSING" }
$Json = Get-Content -Path $Report -Raw | ConvertFrom-Json
if ($Json.status -ne "PASS" -or $Json.verified_mp4_profiles.Count -ne 9) {
    throw "T10_PROFILE_COUNT_OR_STATUS_INVALID"
}
if ($Json.qt_render_connected -ne $false -or $Json.release_permission -ne $false) {
    throw "T10_SCOPE_NOT_HONEST"
}
if (@(Get-ChildItem -Path $Target -Filter "*.mp4").Count -ne 9) {
    throw "T10_PACKAGED_FILES_MISSING"
}
$Zip = Join-Path $RepoRoot "dist-s10\AI-Ngerti-Geopolitik-S10-Media-Smoke-Windows-x64.zip"
if (-not (Test-Path $Zip)) { throw "T10_MEDIA_ZIP_MISSING" }
$Hashes = @{
    "packaged_media_smoke_zip_sha256" = (Get-FileHash $Zip -Algorithm SHA256).Hash.ToLowerInvariant()
    "packaged_media_smoke_exe_sha256" = (Get-FileHash $Exe -Algorithm SHA256).Hash.ToLowerInvariant()
    "native_ffmpeg_executable_bundled" = $false
    "qualification_only" = $true
}
$Hashes | ConvertTo-Json | Set-Content -Path (Join-Path $EvidenceDir "t10_packaging_manifest.json") -Encoding UTF8
Write-Host "PASS T10 packaged media E2E; nine actual verified external-FFmpeg MP4 cells; no GUI export"
