$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python 3.12 fehlt. Installieren: winget install Python.Python.3.12"
}

py -3.12 -m venv .build-venv
& .\.build-venv\Scripts\python.exe -m pip install --upgrade pip
& .\.build-venv\Scripts\pip.exe install -r requirements.txt pyinstaller pytest

$env:PYTHONPATH = "."
$env:QT_QPA_PLATFORM = "offscreen"
& .\.build-venv\Scripts\python.exe -m pytest -q 2>&1 | Tee-Object -FilePath "build-test.log"
$testExitCode = $LASTEXITCODE
if ($testExitCode -ne 0) {
    throw "Tests fehlgeschlagen; Details stehen in build-test.log."
}

Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
& .\.build-venv\Scripts\pyinstaller.exe --noconfirm --clean --windowed `
    --name ArtursTaskmanager `
    --collect-submodules taskmanager `
    --collect-submodules openpyxl `
    --add-data "taskmanager/assets;taskmanager/assets" `
    --hidden-import taskmanager.weekly_review `
    --hidden-import taskmanager.notifications `
    --hidden-import taskmanager.calendar_view `
    main.py

$exe = Join-Path $PSScriptRoot "dist\ArtursTaskmanager\ArtursTaskmanager.exe"
if (-not (Test-Path $exe)) { throw "EXE wurde nicht erzeugt." }

$process = Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -PassThru
Start-Sleep -Seconds 12
if ($process.HasExited) { throw "EXE-Starttest fehlgeschlagen: Exitcode $($process.ExitCode)" }
Stop-Process -Id $process.Id -Force

$zip = Join-Path $PSScriptRoot "ArtursTaskmanager-V10.0-Windows.zip"
Compress-Archive -Path "dist\ArtursTaskmanager\*" -DestinationPath $zip -Force
$hash = (Get-FileHash $zip -Algorithm SHA256).Hash.ToLower()
"$hash  ArtursTaskmanager-V10.0-Windows.zip" | Set-Content "SHA256SUMS-V10.0.txt" -Encoding ascii

Write-Host ""
Write-Host "V10-Release erfolgreich erstellt:" -ForegroundColor Green
Write-Host $zip
Write-Host (Join-Path $PSScriptRoot "SHA256SUMS-V10.0.txt")
