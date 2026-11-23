@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title Build Chiavi in Mano - IPTV Studio Pro (.exe + FFmpeg)

echo ============================================================================
echo   IPTV STUDIO PRO - BUILD CHIAVI IN MANO (EXE UNICO + FFMPEG + ICONA)
echo ============================================================================
echo.

:: 1. Verifica Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERRORE] Python non trovato nel PATH di Windows.
    echo Installa Python 3.x selezionando "Add Python to PATH" e riprova.
    pause
    exit /b 1
)

:: 2. Verifica / Installa PyInstaller automaticamente
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller non trovato. Installazione automatica in corso...
    python -m pip install --upgrade pyinstaller
    if errorlevel 1 (
        echo [ERRORE] Impossibile installare PyInstaller tramite pip.
        pause
        exit /b 1
    )
)
echo [OK] Python e PyInstaller pronti.
echo.

:: 3. Ricerca binari FFmpeg (ffmpeg.exe, ffprobe.exe, ffplay.exe)
call :FindFFmpegBins

if not defined FFMPEG_EXE (
    echo [AVVISO] Binari FFmpeg non trovati nella cartella locale o in C:\ffmpeg\bin.
    echo.
    set /p "DL_CHOICE=Vuoi scaricare e configurare automaticamente FFmpeg per Windows ora? (S/N): "
    if /i "!DL_CHOICE!"=="S" (
        call :DownloadFFmpeg
        call :FindFFmpegBins
    )
)

set "ADD_BINS="
if defined FFMPEG_EXE (
    echo [OK] ffmpeg.exe  : "!FFMPEG_EXE!"
    set "ADD_BINS=!ADD_BINS! --add-binary "!FFMPEG_EXE!;.""
) else (
    echo [!] ffmpeg.exe non incluso ^(verra usato il fallback interno HLS^).
)

if defined FFPROBE_EXE (
    echo [OK] ffprobe.exe : "!FFPROBE_EXE!"
    set "ADD_BINS=!ADD_BINS! --add-binary "!FFPROBE_EXE!;.""
) else (
    echo [!] ffprobe.exe non incluso.
)

if defined FFPLAY_EXE (
    echo [OK] ffplay.exe  : "!FFPLAY_EXE!"
    set "ADD_BINS=!ADD_BINS! --add-binary "!FFPLAY_EXE!;.""
) else (
    echo [!] ffplay.exe non incluso.
)

set "ICON_OPT="
if exist "%~dp0iptv_studio_pro.ico" (
    echo [OK] Icona app   : "%~dp0iptv_studio_pro.ico"
    set "ICON_OPT=--icon "%~dp0iptv_studio_pro.ico""
)

echo.
echo [STEP 1/2] Compilazione eseguibile singolo IPTV_Studio_Pro.exe...
python -m PyInstaller --noconfirm --clean --onefile --windowed --name "IPTV_Studio_Pro" !ICON_OPT! !ADD_BINS! "iptv_checker_2.py"
if errorlevel 1 (
    echo.
    echo [ERRORE] Compilazione PyInstaller fallita.
    pause
    exit /b 1
)

if not exist "Release_Unica" mkdir "Release_Unica"
copy /Y "dist\IPTV_Studio_Pro.exe" "Release_Unica\IPTV_Studio_Pro.exe" >nul
echo [OK] Eseguibile creato: "%~dp0Release_Unica\IPTV_Studio_Pro.exe"

:: 4. Compilazione Installer Windows (se Inno Setup 6 e installato)
set "ISCC_EXE="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC_EXE=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC_EXE=C:\Program Files\Inno Setup 6\ISCC.exe"

echo.
if defined ISCC_EXE (
    echo [STEP 2/2] Compilazione Installer Windows con Inno Setup...
    "%ISCC_EXE%" "installer_iptv_studio_pro.iss"
    if not errorlevel 1 (
        echo [OK] Installer pronto in: "%~dp0Installer_Output\IPTV_Studio_Pro_Setup.exe"
    )
) else (
    echo [STEP 2/2] Inno Setup 6 non installato ^(passaggio installer saltato^).
    echo            Puoi comunque usare direttamente "Release_Unica\IPTV_Studio_Pro.exe".
)

echo.
echo ============================================================================
echo   TUTTO PRONTO!
echo   Cartella output: "%~dp0Release_Unica"
echo ============================================================================
start "" "%~dp0Release_Unica"
pause
exit /b 0

:FindFFmpegBins
set "FFMPEG_EXE="
set "FFPROBE_EXE="
set "FFPLAY_EXE="

for %%P in (
    "%~dp0ffmpeg.exe"
    "%~dp0bin\ffmpeg.exe"
    "%~dp0ffmpeg\bin\ffmpeg.exe"
    "%~dp0ffmpeg_dist\bin\ffmpeg.exe"
    "C:\ffmpeg\bin\ffmpeg.exe"
    "C:\Program Files\ffmpeg\bin\ffmpeg.exe"
) do (
    if not defined FFMPEG_EXE if exist "%%~P" set "FFMPEG_EXE=%%~fP"
)

for %%P in (
    "%~dp0ffprobe.exe"
    "%~dp0bin\ffprobe.exe"
    "%~dp0ffmpeg\bin\ffprobe.exe"
    "%~dp0ffmpeg_dist\bin\ffprobe.exe"
    "C:\ffmpeg\bin\ffprobe.exe"
    "C:\Program Files\ffmpeg\bin\ffprobe.exe"
) do (
    if not defined FFPROBE_EXE if exist "%%~P" set "FFPROBE_EXE=%%~fP"
)

for %%P in (
    "%~dp0ffplay.exe"
    "%~dp0bin\ffplay.exe"
    "%~dp0ffmpeg\bin\ffplay.exe"
    "%~dp0ffmpeg_dist\bin\ffplay.exe"
    "C:\ffmpeg\bin\ffplay.exe"
    "C:\Program Files\ffmpeg\bin\ffplay.exe"
) do (
    if not defined FFPLAY_EXE if exist "%%~P" set "FFPLAY_EXE=%%~fP"
)
exit /b 0

:DownloadFFmpeg
echo.
echo [INFO] Download pacchetto FFmpeg Essentials per Windows in corso...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ProgressPreference = 'SilentlyContinue';" ^
  "$zip = Join-Path $env:TEMP 'ffmpeg_essentials.zip';" ^
  "$ext = Join-Path $env:TEMP 'ffmpeg_essentials_ext';" ^
  "if (Test-Path $ext) { Remove-Item $ext -Recurse -Force };" ^
  "Invoke-WebRequest -Uri 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip' -OutFile $zip;" ^
  "Expand-Archive -Path $zip -DestinationPath $ext -Force;" ^
  "$binDir = Get-ChildItem -Path $ext -Recurse -Directory -Filter 'bin' | Select-Object -First 1;" ^
  "if ($binDir) {" ^
  "  Copy-Item (Join-Path $binDir.FullName 'ffmpeg.exe') '%~dp0' -Force;" ^
  "  Copy-Item (Join-Path $binDir.FullName 'ffprobe.exe') '%~dp0' -Force;" ^
  "  Copy-Item (Join-Path $binDir.FullName 'ffplay.exe') '%~dp0' -Force;" ^
  "  Write-Host '[OK] ffmpeg.exe, ffprobe.exe e ffplay.exe estratti con successo!' -ForegroundColor Green" ^
  "} else {" ^
  "  Write-Host '[ERRORE] Cartella bin non trovata nell archivio scaricato.' -ForegroundColor Red" ^
  "}"
exit /b 0
