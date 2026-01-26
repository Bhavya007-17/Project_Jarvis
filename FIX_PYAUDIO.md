# Fix PyAudio Installation on Windows

**Note:** You're using Python 3.14.2, which is very new. PyAudio may not have pre-built wheels for Python 3.14 yet.

PyAudio can be tricky to install on Windows. Here are several solutions:

## Solution 1: Install PyAudio Separately (Recommended)

Try installing PyAudio separately after installing other requirements:

```powershell
# First, install all other requirements (skip pyaudio)
pip install --user fastapi uvicorn python-socketio python-multipart google-genai opencv-python pillow mss playwright python-kasa zeroconf aiohttp python-dotenv mediapipe build123d SpeechRecognition

# Then install PyAudio separately
pip install --user pyaudio
```

## Solution 2: Use pipwin (NOT WORKING with Python 3.14)

⚠️ **pipwin has compatibility issues with Python 3.14.2** - the js2py dependency fails.

**Skip this method** and use Solution 3 (download wheel) or Solution 1 (run as admin) instead.

## Solution 3: Install Pre-built Wheel File

1. Check your Python version:
```powershell
python --version
```

2. Download the appropriate wheel file from:
   - https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
   - Or use: https://github.com/intxcc/pyaudio_portaudio/releases

3. Install the wheel file:
```powershell
pip install --user [path_to_downloaded_wheel_file].whl
```

For example, if you downloaded `PyAudio-0.2.14-cp311-cp311-win_amd64.whl`:
```powershell
pip install --user PyAudio-0.2.14-cp311-cp311-win_amd64.whl
```

## Solution 4: Install Visual C++ Build Tools (If needed)

If all else fails, you may need Visual Studio Build Tools:

1. Download Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
2. Install "Desktop development with C++" workload
3. Then try: `pip install --user pyaudio`

## Solution 5: Use Conda (If you have Anaconda/Miniconda)

```powershell
conda install pyaudio
```

## Quick Fix Script

Run this PowerShell script to try multiple methods:

```powershell
# Try standard pip first
pip install --user pyaudio

# If that fails, try pipwin
if ($LASTEXITCODE -ne 0) {
    pip install --user pipwin
    pipwin install pyaudio
}
```

## Verify Installation

After installation, verify it works:
```powershell
python -c "import pyaudio; print('PyAudio installed successfully!')"
```
