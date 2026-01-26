const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

// Use ANGLE D3D11 backend - more stable on Windows while keeping WebGL working
// This fixes "GPU state invalid after WaitForGetOffsetInRange" error
app.commandLine.appendSwitch('use-angle', 'd3d11');
app.commandLine.appendSwitch('enable-features', 'Vulkan');
app.commandLine.appendSwitch('ignore-gpu-blocklist');

let mainWindow;
let pythonProcess;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1920,
        height: 1080,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false, // For simple IPC/Socket.IO usage
        },
        backgroundColor: '#000000',
        frame: false, // Frameless for custom UI
        titleBarStyle: 'hidden',
        show: false, // Don't show until ready
    });

    // In dev, load Vite server. In prod, load index.html
    const isDev = process.env.NODE_ENV !== 'production';

    const loadFrontend = (retries = 3) => {
        const url = isDev ? 'http://localhost:5173' : null;
        const loadPromise = isDev
            ? mainWindow.loadURL(url)
            : mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));

        loadPromise
            .then(() => {
                console.log('Frontend loaded successfully!');
                windowWasShown = true;
                mainWindow.show();
                if (isDev) {
                    mainWindow.webContents.openDevTools();
                }
            })
            .catch((err) => {
                console.error(`Failed to load frontend: ${err.message}`);
                if (retries > 0) {
                    console.log(`Retrying in 1 second... (${retries} retries left)`);
                    setTimeout(() => loadFrontend(retries - 1), 1000);
                } else {
                    console.error('Failed to load frontend after all retries. Keeping window open.');
                    windowWasShown = true;
                    mainWindow.show(); // Show anyway so user sees something
                }
            });
    };

    loadFrontend();

    mainWindow.on('closed', () => {
        mainWindow = null;
    });
}

function findPythonExecutable() {
    const { execSync } = require('child_process');
    const os = require('os');
    const fs = require('fs');
    
    // Try to find conda Python in common locations
    const homeDir = os.homedir();
    const username = os.userInfo().username;
    const possiblePaths = [
        // Miniconda
        path.join(homeDir, 'miniconda3', 'envs', 'ada_v2', 'python.exe'),
        path.join(homeDir, 'miniconda3', 'envs', 'ada_v2', 'python'),
        // Anaconda
        path.join(homeDir, 'anaconda3', 'envs', 'ada_v2', 'python.exe'),
        path.join(homeDir, 'anaconda3', 'envs', 'ada_v2', 'python'),
        // Common Windows locations with username
        `C:\\Users\\${username}\\miniconda3\\envs\\ada_v2\\python.exe`,
        `C:\\Users\\${username}\\anaconda3\\envs\\ada_v2\\python.exe`,
        // Check CONDA_PREFIX if set
        process.env.CONDA_PREFIX ? path.join(process.env.CONDA_PREFIX, 'python.exe') : null,
        process.env.CONDA_PREFIX ? path.join(process.env.CONDA_PREFIX, 'python') : null,
    ].filter(p => p !== null);
    
    // Check if any of these paths exist
    for (const pythonPath of possiblePaths) {
        try {
            if (fs.existsSync(pythonPath)) {
                console.log(`Found Python at: ${pythonPath}`);
                return pythonPath;
            }
        } catch (e) {
            // Continue checking
        }
    }
    
    // Try to get Python from conda info
    try {
        if (process.platform === 'win32') {
            // Try to get conda base path from conda info
            const condaInfo = execSync('conda info --base', { encoding: 'utf8', stdio: 'pipe', shell: true }).trim();
            if (condaInfo) {
                const envPython = path.join(condaInfo, 'envs', 'ada_v2', 'python.exe');
                if (fs.existsSync(envPython)) {
                    console.log(`Found Python via conda info at: ${envPython}`);
                    return envPython;
                }
            }
        }
    } catch (e) {
        console.log('Could not find conda via conda info, trying other methods...');
    }
    
    // Try using conda run as last resort
    try {
        if (process.platform === 'win32') {
            execSync('conda --version', { encoding: 'utf8', stdio: 'pipe', shell: true });
            console.log('Using conda run to execute Python');
            return 'conda'; // Special flag to use conda run
        }
    } catch (e) {
        // Conda not available
    }
    
    // Fallback to system Python
    console.log('Using system Python (make sure conda environment is activated)');
    return 'python';
}

function startPythonBackend() {
    const scriptPath = path.join(__dirname, '../backend/server.py');
    let pythonExecutable = findPythonExecutable();
    console.log(`Starting Python backend: ${scriptPath}`);
    console.log(`Using Python: ${pythonExecutable}`);

    let command, args;
    if (pythonExecutable === 'conda') {
        // Use conda run to execute in the environment
        command = 'conda';
        args = ['run', '-n', 'ada_v2', 'python', scriptPath];
    } else {
        command = pythonExecutable;
        args = [scriptPath];
    }

    pythonProcess = spawn(command, args, {
        cwd: path.join(__dirname, '../backend'),
        shell: process.platform === 'win32', // Use shell on Windows for better path resolution
        env: {
            ...process.env,
            // Ensure we're using the right Python environment
            PYTHONPATH: path.join(__dirname, '../backend'),
        }
    });

    pythonProcess.stdout.on('data', (data) => {
        console.log(`[Python]: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`[Python Error]: ${data}`);
    });
    
    pythonProcess.on('error', (err) => {
        console.error(`[Python Process Error]: ${err.message}`);
        console.error('Make sure the conda environment "ada_v2" is set up correctly.');
    });
    
    pythonProcess.on('exit', (code, signal) => {
        if (code !== null && code !== 0) {
            console.error(`[Python Process] Exited with code ${code}`);
        }
        if (signal) {
            console.log(`[Python Process] Killed by signal ${signal}`);
        }
    });
}

app.whenReady().then(() => {
    ipcMain.on('window-minimize', () => {
        if (mainWindow) mainWindow.minimize();
    });

    ipcMain.on('window-maximize', () => {
        if (mainWindow) {
            if (mainWindow.isMaximized()) {
                mainWindow.unmaximize();
            } else {
                mainWindow.maximize();
            }
        }
    });

    ipcMain.on('window-close', () => {
        if (mainWindow) mainWindow.close();
    });

    checkBackendPort(8000).then((isTaken) => {
        if (isTaken) {
            console.log('Port 8000 is taken. Assuming backend is already running manually.');
            waitForBackend().then(createWindow);
        } else {
            startPythonBackend();
            // Give it a moment to start, then wait for health check
            setTimeout(() => {
                waitForBackend().then(createWindow);
            }, 1000);
        }
    });

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

function checkBackendPort(port) {
    return new Promise((resolve) => {
        const net = require('net');
        const server = net.createServer();
        server.once('error', (err) => {
            if (err.code === 'EADDRINUSE') {
                resolve(true);
            } else {
                resolve(false);
            }
        });
        server.once('listening', () => {
            server.close();
            resolve(false);
        });
        server.listen(port);
    });
}

function waitForBackend() {
    return new Promise((resolve) => {
        const check = () => {
            const http = require('http');
            http.get('http://127.0.0.1:8000/status', (res) => {
                if (res.statusCode === 200) {
                    console.log('Backend is ready!');
                    resolve();
                } else {
                    console.log('Backend not ready, retrying...');
                    setTimeout(check, 1000);
                }
            }).on('error', (err) => {
                console.log('Waiting for backend...');
                setTimeout(check, 1000);
            });
        };
        check();
    });
}

let windowWasShown = false;

app.on('window-all-closed', () => {
    // Only quit if the window was actually shown at least once
    // This prevents quitting during startup if window creation fails
    if (process.platform !== 'darwin' && windowWasShown) {
        app.quit();
    } else if (!windowWasShown) {
        console.log('Window was never shown - keeping app alive to allow retries');
    }
});

app.on('will-quit', () => {
    console.log('App closing... Killing Python backend.');
    if (pythonProcess) {
        if (process.platform === 'win32') {
            // Windows: Force kill the process tree synchronously
            try {
                const { execSync } = require('child_process');
                execSync(`taskkill /pid ${pythonProcess.pid} /f /t`);
            } catch (e) {
                console.error('Failed to kill python process:', e.message);
            }
        } else {
            // Unix: SIGKILL
            pythonProcess.kill('SIGKILL');
        }
        pythonProcess = null;
    }
});
