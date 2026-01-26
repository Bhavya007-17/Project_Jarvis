@echo off
echo Installing JARVIS requirements (excluding PyAudio)...
echo.

pip install --user fastapi uvicorn python-socketio python-multipart google-genai opencv-python pillow mss playwright python-kasa zeroconf aiohttp python-dotenv mediapipe build123d SpeechRecognition

echo.
echo ========================================
echo PyAudio installation skipped.
echo.
echo To install PyAudio, try one of these:
echo.
echo Option 1: pipwin (Recommended for Python 3.14)
echo   pip install pipwin
echo   pipwin install pyaudio
echo.
echo Option 2: Install directly
echo   pip install --user pyaudio
echo.
echo Option 3: See FIX_PYAUDIO.md for more solutions
echo ========================================
echo.

pause
