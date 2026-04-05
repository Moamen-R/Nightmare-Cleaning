@echo off
setlocal

:: Check for administrative privileges using PowerShell (no temp files)
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
    echo Requesting administrative privileges...
    :: Use PowerShell Start-Process -Verb RunAs instead of VBScript
    :: This avoids the race condition of writing a .vbs to %temp%
    powershell -Command "Start-Process '%~f0' -Verb RunAs -ArgumentList '-Elevated'"
    exit /B
)

:gotAdmin
pushd "%CD%"
CD /D "%~dp0"

echo Nightmare Cleaner - Installation
echo =================================
powershell -ExecutionPolicy Bypass -File "%~dp0install.ps1" -InstallPython
echo.
pause
