@echo off
setlocal
cd /d "%~dp0"

if not exist "Release_Unica\IPTV_Studio_Pro.exe" (
    echo [ERRORE] Prima esegui "1_COMPILA_TUTTO_CHIAVI_IN_MANO.bat" per generare Release_Unica\IPTV_Studio_Pro.exe.
    pause
    exit /b 1
)

set "ISCC_EXE="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC_EXE=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC_EXE=C:\Program Files\Inno Setup 6\ISCC.exe"

if not defined ISCC_EXE (
    echo [INFO] Inno Setup 6 non trovato. Puoi scaricarlo gratuitamente da https://jrsoftware.org/isdl.php
    pause
    exit /b 1
)

"%ISCC_EXE%" "installer_iptv_studio_pro.iss"
if not errorlevel 1 (
    echo [OK] Installer creato in Installer_Output\IPTV_Studio_Pro_Setup.exe
    start "" "%~dp0Installer_Output"
)
pause
