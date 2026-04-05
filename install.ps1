#requires -RunAsAdministrator

<#
.SYNOPSIS
One-command installation script for Nightmare Cleaner.
#>

param (
    [switch]$InstallPython = $false
)

Write-Host "Nightmare Cleaner - One-Command Installation" -ForegroundColor Magenta

# Check for Python
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not installed or not in PATH." -ForegroundColor Red
    if ($InstallPython) {
        Write-Host "Installing Python via winget..." -ForegroundColor Yellow
        winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    } else {
        Write-Host "Please install Python or run with -InstallPython flag." -ForegroundColor Red
        exit 1
    }
}

Write-Host "Setting up Python environment and installing Nightmare Cleaner..." -ForegroundColor Cyan
python -m pip install --upgrade pip
python -m pip install -e .

Write-Host "Installation complete! You can now run 'nightmare' from your terminal." -ForegroundColor Green
