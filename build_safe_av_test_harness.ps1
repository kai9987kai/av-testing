$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$SourceFile = Join-Path $ScriptDir "safe_av_test_harness.py"
$ExeName = "safe-av-test-harness"

if (-not (Test-Path $SourceFile)) {
    Write-Error "Source file not found: $SourceFile"
}

Write-Host "[1/3] Checking Python..."
python --version | Out-Host

Write-Host "[2/3] Ensuring PyInstaller is installed..."
python -m pip show pyinstaller *> $null
if ($LASTEXITCODE -ne 0) {
    python -m pip install --upgrade pyinstaller
}

Write-Host "[3/3] Building EXE..."
python -m PyInstaller --clean --onefile --name $ExeName $SourceFile

if ($LASTEXITCODE -ne 0) {
    Write-Error "Build failed."
}

$OutputExe = Join-Path $ScriptDir "dist\$ExeName.exe"
if (Test-Path $OutputExe) {
    Write-Host "Build complete: $OutputExe"
} else {
    Write-Warning "Build finished but EXE was not found at expected path: $OutputExe"
}
