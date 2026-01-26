# JARVIS Installation and Run Commands

## Prerequisites
- Python 3.11+ installed
- Node.js and npm installed
- Internet connection

## Installation Steps

### 1. Install Python Dependencies

**Note:** PyAudio is commented out in requirements.txt due to Python 3.14 compatibility. Install it separately.

```bash
# Install all requirements except PyAudio
pip install --user -r requirements.txt

# Then install PyAudio separately (see FIX_PYAUDIO.md for options)
# Option 1: Try pipwin (recommended for Python 3.14)
pip install --user pipwin
pipwin install pyaudio

# Option 2: Or try direct install
pip install --user pyaudio
```

If you encounter permission errors, try running PowerShell as Administrator.

### 2. Install Playwright Browsers (for Web Agent)
```bash
playwright install chromium
```

### 3. Install Node.js Dependencies
```bash
npm install
```

## Running the Application

### ⚠️ IMPORTANT FOR WINDOWS USERS

**Problem**: Windows PowerShell may use system Python (3.14) instead of conda Python (3.11), causing import errors.

**Solution**: Always use the conda Python directly or use the provided startup scripts.

### Option 1: Use Startup Script (Easiest - Windows)

**PowerShell:**
```powershell
.\start_jarvis.ps1
```

This script:
- Activates the conda environment
- Verifies packages are installed
- Starts the app with the correct Python

### Option 2: Run Main Application Directly

**Windows PowerShell:**
```powershell
# Use npm.cmd to avoid execution policy issues
npm.cmd start
```

**Or if you have execution policy fixed:**
```powershell
npm start
```

This will:
- Start the Electron frontend
- Automatically launch the Python backend server (using conda Python)
- Open the JARVIS interface

### Option 3: Development Mode (with Hot Reload)

**Windows PowerShell:**
```powershell
npm.cmd run dev
```

This runs Vite dev server and Electron with hot reload enabled.

### Option 4: Run with Wake Word Listener (Recommended)

**Terminal 1 - Wake Word Listener (Background):**
```powershell
C:\Users\bhavy\miniconda3\envs\ada_v2\python.exe wake_word_listener.py
```

This runs in the background and listens for "jarvis" to launch the app.

**Terminal 2 - Main Application:**
```powershell
npm.cmd start
```

Or wait for the wake word listener to launch it automatically.

## Manual Backend Start (if needed)

If you need to run the backend separately for debugging:

**Windows PowerShell:**
```powershell
# Use the startup script
.\start_backend.ps1

# Or manually:
C:\Users\bhavy\miniconda3\envs\ada_v2\python.exe backend\server.py
```

**Linux/Mac:**
```bash
conda activate ada_v2
cd backend
python server.py
```

The backend runs on `http://127.0.0.1:8000`

## Shutting Down

### Via Voice Command
Say: **"jarvis shut down"** or **"jarvis shutdown"**

### Via UI
Click the X button in the top-right corner of the window

### Via Terminal
Press `Ctrl+C` in the terminal running the application

## Troubleshooting

### Audio Issues
- Make sure your microphone and speaker are properly configured
- Check Windows audio settings
- The system automatically prevents feedback loops by pausing audio when you speak

### Port Already in Use
If port 8000 is already in use:
```bash
# Windows: Find and kill process using port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or change the port in backend/server.py (line 989)
```

### Wake Word Listener Not Working
- Make sure `SpeechRecognition` is installed: `pip install SpeechRecognition`
- Check microphone permissions in Windows settings
- Adjust `ENERGY_THRESHOLD` in `wake_word_listener.py` if needed

### Browser Not Opening
- Make sure Playwright browsers are installed: `playwright install chromium`
- Check that `headless=False` in `backend/web_agent.py` (line 198)

### PowerShell Execution Policy Error (Windows)
**Symptoms**: `npm : File C:\Program Files\nodejs\npm.ps1 cannot be loaded because running scripts is disabled`

**Solution**:
1. **Quick Fix**: Use `npm.cmd` instead of `npm`:
   ```powershell
   npm.cmd run dev
   ```

2. **Permanent Fix**: Change PowerShell execution policy (run PowerShell as Administrator):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Alternative**: Use Command Prompt (cmd.exe) instead of PowerShell

### ModuleNotFoundError: No module named 'socketio' (Windows)
**Symptoms**: Backend fails to start with "No module named 'socketio'" even after installing packages

**Cause**: System Python (3.14) is being used instead of conda Python (3.11)

**Solution**:
1. **Always use conda Python directly**:
   ```powershell
   C:\Users\bhavy\miniconda3\envs\ada_v2\python.exe backend\server.py
   ```

2. **Or use the startup scripts**:
   ```powershell
   .\start_jarvis.ps1      # For full app
   .\start_backend.ps1     # For backend only
   ```

3. **Verify which Python is being used**:
   ```powershell
   where.exe python
   # Should show conda Python first, not C:\Python314\python.exe
   ```

4. **If conda activate isn't working**, manually set PATH:
   ```powershell
   $env:PATH = "C:\Users\bhavy\miniconda3\envs\ada_v2;C:\Users\bhavy\miniconda3\envs\ada_v2\Scripts;$env:PATH"
   ```

## Quick Start Commands Summary

### Windows PowerShell Commands:

```powershell
# 1. Install Python dependencies
pip install -r requirements.txt

# If permission errors, use:
pip install --user -r requirements.txt

# 2. Install Playwright browsers
playwright install chromium

# 3. Install Node.js dependencies (already done)
npm install

# 4. Run the application
npm start
```

### For Wake Word Listener:

**Open a new PowerShell window and run:**
```powershell
python wake_word_listener.py
```

This will listen for "jarvis" and automatically launch the app when detected.

## Quick Run Commands

### Just Start JARVIS (Windows):
```powershell
# Easiest way - use the startup script
.\start_jarvis.ps1

# Or directly:
npm.cmd start
```

### Start with Wake Word Listener:
**Terminal 1:**
```powershell
C:\Users\bhavy\miniconda3\envs\ada_v2\python.exe wake_word_listener.py
```

**Terminal 2 (or wait for auto-launch):**
```powershell
npm.cmd start
```

### Development Mode (with hot reload):
```powershell
npm.cmd run dev
```

### Run Backend Separately (for debugging):
```powershell
.\start_backend.ps1
```
