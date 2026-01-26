# Windows Setup Fix - Step by Step

## The Problem

Your system has multiple Python installations:
- **System Python 3.14** at `C:\Python314\python.exe` (first in PATH)
- **Conda Python 3.11** at `C:\Users\bhavy\miniconda3\envs\ada_v2\python.exe` (has all packages)

When you run `python`, Windows uses Python 3.14, which doesn't have the packages installed.

## The Solution

### Step 1: Verify Packages Are Installed in Conda Environment

Open PowerShell and run:

```powershell
C:\Users\bhavy\miniconda3\envs\ada_v2\python.exe -c "import socketio, fastapi, uvicorn; print('All packages OK!')"
```

If this works, packages are installed correctly. If not, install them:

```powershell
C:\Users\bhavy\miniconda3\envs\ada_v2\python.exe -m pip install -r requirements.txt
```

### Step 2: Start JARVIS (Choose ONE method)

#### Method A: Use the Startup Script (Easiest)

```powershell
cd C:\Users\bhavy\ada_v2
.\start_jarvis.ps1
```

#### Method B: Use npm.cmd directly

```powershell
cd C:\Users\bhavy\ada_v2
npm.cmd run dev
```

The Electron app will automatically use the conda Python (we already fixed this in `electron/main.js`).

#### Method C: Run Backend Separately (for debugging)

**Terminal 1 - Backend:**
```powershell
cd C:\Users\bhavy\ada_v2
.\start_backend.ps1
```

**Terminal 2 - Frontend:**
```powershell
cd C:\Users\bhavy\ada_v2
npm.cmd run dev
```

### Step 3: If You Still Get Errors

#### Error: "No module named 'socketio'"

This means the backend is still using the wrong Python. Check Electron console logs - it should show:
```
Found Python at: C:\Users\bhavy\miniconda3\envs\ada_v2\python.exe
```

If it shows a different path, the Electron fix didn't work. Manually verify the path exists:

```powershell
Test-Path "C:\Users\bhavy\miniconda3\envs\ada_v2\python.exe"
```

Should return `True`.

#### Error: PowerShell execution policy

Use `npm.cmd` instead of `npm`, or fix the policy:

```powershell
# Run PowerShell as Administrator, then:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Quick Reference

**Always use conda Python directly:**
```powershell
C:\Users\bhavy\miniconda3\envs\ada_v2\python.exe <script>
```

**Or use the startup scripts:**
```powershell
.\start_jarvis.ps1      # Full app
.\start_backend.ps1     # Backend only
```

**For npm commands, use:**
```powershell
npm.cmd <command>       # Instead of npm <command>
```

## Verification Checklist

- [ ] Conda Python can import socketio: `C:\Users\bhavy\miniconda3\envs\ada_v2\python.exe -c "import socketio"`
- [ ] Startup scripts exist: `Test-Path .\start_jarvis.ps1`
- [ ] Electron main.js has the Python detection code (already fixed)
- [ ] npm.cmd works: `npm.cmd --version`

If all checkboxes pass, JARVIS should start successfully!
