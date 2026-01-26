# Backend Startup Script for Windows
# Use this to run the backend separately for debugging

Write-Host "Starting JARVIS Backend..." -ForegroundColor Green

# Use conda Python directly
$pythonExe = "C:\Users\bhavy\miniconda3\envs\ada_v2\python.exe"
$serverPath = Join-Path $PSScriptRoot "backend\server.py"

Write-Host "Using Python: $pythonExe" -ForegroundColor Cyan
Write-Host "Server script: $serverPath" -ForegroundColor Cyan

# Change to backend directory and run
Set-Location (Join-Path $PSScriptRoot "backend")
& $pythonExe $serverPath
