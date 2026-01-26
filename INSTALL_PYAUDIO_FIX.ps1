# PyAudio Installation Fix for Python 3.14.2
# Run this script in PowerShell as Administrator or in a user-writable location

Write-Host "Installing PyAudio for Python 3.14.2..." -ForegroundColor Cyan

# Method 1: Try pipwin (best for Python 3.14)
Write-Host "`nAttempting Method 1: pipwin..." -ForegroundColor Yellow
pip install pipwin
if ($LASTEXITCODE -eq 0) {
    pipwin install pyaudio
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Success! PyAudio installed via pipwin." -ForegroundColor Green
        exit 0
    }
}

# Method 2: Try installing other requirements first, then pyaudio
Write-Host "`nAttempting Method 2: Install other packages first..." -ForegroundColor Yellow
pip install fastapi uvicorn python-socketio python-multipart google-genai opencv-python pillow mss playwright python-kasa zeroconf aiohttp python-dotenv mediapipe build123d SpeechRecognition
pip install pyaudio
if ($LASTEXITCODE -eq 0) {
    Write-Host "Success! PyAudio installed." -ForegroundColor Green
    exit 0
}

# Method 3: Try with --no-build-isolation
Write-Host "`nAttempting Method 3: Install with --no-build-isolation..." -ForegroundColor Yellow
pip install --no-build-isolation pyaudio
if ($LASTEXITCODE -eq 0) {
    Write-Host "Success! PyAudio installed." -ForegroundColor Green
    exit 0
}

Write-Host "`nAll methods failed. You may need to:" -ForegroundColor Red
Write-Host "1. Install Visual Studio Build Tools" -ForegroundColor Yellow
Write-Host "2. Use Python 3.11 or 3.12 instead of 3.14" -ForegroundColor Yellow
Write-Host "3. Download wheel file manually from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio" -ForegroundColor Yellow
