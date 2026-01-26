# JARVIS Startup Script for Windows
# This ensures the correct conda Python is used

Write-Host "Starting JARVIS..." -ForegroundColor Green

# Activate conda environment
& C:\Users\bhavy\miniconda3\Scripts\activate.ps1 ada_v2

# Verify we're using the right Python
$pythonPath = & C:\Users\bhavy\miniconda3\envs\ada_v2\python.exe -c "import sys; print(sys.executable)"
Write-Host "Using Python: $pythonPath" -ForegroundColor Cyan

# Check if packages are installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
& C:\Users\bhavy\miniconda3\envs\ada_v2\python.exe -c "import socketio, fastapi, uvicorn; print('All core packages available!')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Packages not installed in conda environment!" -ForegroundColor Red
    Write-Host "Run: C:\Users\bhavy\miniconda3\envs\ada_v2\python.exe -m pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Start the app
Write-Host "`nStarting JARVIS application..." -ForegroundColor Green
npm.cmd run dev
