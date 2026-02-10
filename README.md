## Jarvis - AI Assistant (ADA V2)

![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-blue?logo=python)
![React](https://img.shields.io/badge/React-18.2-61DAFB?logo=react)
![Electron](https://img.shields.io/badge/Electron-28-47848F?logo=electron)
![Gemini](https://img.shields.io/badge/Google%20Gemini-Native%20Audio-4285F4?logo=google)
![License](https://img.shields.io/badge/License-MIT-green)

Jarvis is a multimodal desktop AI assistant inspired by the “Jarvis OS” fantasy: real-time voice, CAD, web automation, smart home control, and now a full digital suite for briefing, research, and system monitoring.  
It runs entirely on your machine (Electron + Python), talking to Gemini 2.5 Native Audio plus a set of local tools and free APIs.

---

## Key Capabilities

| Capability | What it Does | Tech |
|-----------|--------------|------|
| Low-latency voice loop | Always-on, interruptible conversation, streaming transcription | Gemini 2.5 Native Audio |
| Morning Briefing | Weather, today’s schedule, system health, optional news and stocks | Open-Meteo, Google Calendar, psutil, RSS, yfinance |
| Productivity (Chief of Staff) | Read today’s calendar, reschedule events | Google Calendar API |
| Oracle / Research | Material properties, factual lookups, summaries | DuckDuckGo search, Wikipedia |
| Parametric CAD (Engineer) | Voice-to-CAD, STL export, iterative edits | build123d + local script execution |
| 3D printing pipeline | Discover printers, slice STL, send jobs | OrcaSlicer, Moonraker/OctoPrint |
| Smart home control | Control TP-Link Kasa lights and plugs | python-kasa |
| Face authentication (Sentinel) | Unlock UI only on recognized face | MediaPipe Face Landmarker |
| Gesture UI | “Minority Report” style window manipulation | MediaPipe Hands + React/Three.js |
| Project memory | Per-project logs and CAD artifacts on disk | JSON + file structure |

---

## Digital Suite Overview (New)

The new `digital_suite` backend package implements the PRD “feathers”:

- **Briefing (`digital_suite/briefing.py`)**
  - Single `get_briefing()` call that aggregates:
    - Weather via Open-Meteo (no API key)
    - System status via `psutil` (CPU, RAM, battery, GPU temp when available)
    - Today’s calendar (Google Calendar) when configured
    - Optional RSS news (BBC, TechCrunch) and stocks (yfinance, e.g. NVDA)
  - `format_briefing_for_model()` turns this into a concise text block for Jarvis to speak.

- **Productivity (`digital_suite/productivity.py`)**
  - Google Calendar integration (free tier, OAuth2):
    - `get_today_schedule()` – list today’s events from the primary calendar
    - `reschedule_event()` – move an event to a new time
  - Stores tokens locally in `backend/credentials/google_tokens.json` (never committed).

- **Research (`digital_suite/research.py`)**
  - `search_web()` – DuckDuckGo search for quick factual and reference lookups.
  - `wikipedia_summary()` – short Wikipedia summaries (title, summary, URL).

- **System Ops (`digital_suite/system_ops.py`)**
  - `get_system_status()` – CPU, RAM, battery, GPU note/temperature.
  - `format_system_status_for_speech()` – short “status report” sentence.
  - `list_top_processes()` – top CPU-consuming processes.
  - `kill_process_by_name()` / `kill_process_by_pid()` – terminate misbehaving apps on request.

Jarvis exposes these as tools to Gemini, so you can say:
- “Jarvis, give me the briefing.”
- “What’s on my calendar today?”
- “Kill that render process.”
- “What’s the density of Inconel 718?”

---

## Architecture Overview

```mermaid
flowchart TB
  subgraph frontend [Frontend (Electron + React)]
    ui[React UI]
    three[Three.js 3D Viewer]
    gesture[MediaPipe Gestures]
    socketClient[Socket.IO Client]
  end

  subgraph backend [Backend (Python 3.11 + FastAPI)]
    server[server.py (FastAPI + Socket.IO)]
    jarvis[jarvis.py (Gemini Live AudioLoop)]
    digi[digital_suite (Briefing, Productivity, Research, System Ops)]
    cad[cad_agent.py (build123d CAD)]
    printer[printer_agent.py (3D printing + OrcaSlicer)]
    kasa[kasa_agent.py (Smart Home)]
    auth[authenticator.py (Face Auth)]
    pm[project_manager.py (Projects/Memory)]
    webAgent[web_agent.py (Playwright Web Agent)]
  end

  subgraph external [External APIs]
    gemini[Gemini Live]
    openMeteo[Open-Meteo Weather]
    gcal[Google Calendar]
    rss[RSS News]
    stocks[yfinance]
    ddg[DuckDuckGo Search]
    wiki[Wikipedia]
  end

  ui --> socketClient
  socketClient <--> server

  server --> jarvis
  server --> auth
  server --> printer
  server --> kasa
  server --> pm

  jarvis --> gemini
  jarvis --> cad
  jarvis --> webAgent
  jarvis --> digi

  digi --> openMeteo
  digi --> gcal
  digi --> rss
  digi --> stocks
  digi --> ddg
  digi --> wiki

  cad --> printer
  cad --> ui
```

---

## Quick Start (Experienced Developers)

```bash
# 1. Clone and enter
git clone <this-repo-url> jarvis && cd jarvis

# 2. Create Python environment (Python 3.11)
conda create -n jarvis python=3.11 -y
conda activate jarvis

# 3. Install Python deps and browsers
pip install -r requirements.txt
playwright install chromium

# 4. Setup frontend
npm install

# 5. Configure Gemini key
echo "GEMINI_API_KEY=your_key_here" > .env

# 6. Run
npm run dev
```

The Electron shell will launch and connect to the backend automatically.

---

## Beginner-Friendly Setup

### 1. Tools to Install

- Visual Studio Code – editor and terminal  
- Miniconda – manages Python environments  
- Git – downloads this repository  
- Node.js 18+ – for the React/Electron frontend

Clone the repo with Git, open it in VS Code, and use the built-in terminal for all commands.

### 2. Python Environment

```bash
conda create -n jarvis python=3.11
conda activate jarvis

pip install -r requirements.txt
playwright install chromium
```

### 3. Frontend Setup

```bash
npm install
```

### 4. Gemini API Key

1. Go to `https://aistudio.google.com/app/apikey`
2. Create an API key.
3. In the project root, create `.env`:

```bash
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

Do not commit this file.

### 5. Face Authentication (Optional but Recommended)

1. Take a clear photo of your face.
2. Rename to `reference.jpg`.
3. Place it in the `backend/` folder.
4. In `backend/settings.json`, set `"face_auth_enabled": true` to require face unlock.

---

## Running Jarvis

### Option 1: Single Terminal (recommended)

```bash
conda activate jarvis
npm run dev
```

The React dev server and Electron shell will start, and the backend will be launched for you.

### Option 2: Separate Backend and Frontend

Terminal 1 (backend):

```bash
conda activate jarvis
python backend/server.py
```

Terminal 2 (frontend):

```bash
npm run dev
```

You can also run the backend entrypoint explicitly:

```bash
python backend/main.py
```

---

## Tooling and Configuration

### settings.json

`settings.json` is created on first run and lives in the project root. Key fields:

| Key | Type | Description |
|-----|------|-------------|
| `face_auth_enabled` | bool | Require face recognition before enabling tools. |
| `tool_permissions` | object | Per-tool confirmation flags (true = ask user; false = auto-allow). |

Important tool flags include:

- `generate_cad`
- `run_web_agent`
- `write_file`
- `read_directory`
- `read_file`
- `create_project`, `switch_project`, `list_projects`
- `get_briefing`
- `get_today_schedule`
- `reschedule_event`
- `get_system_status`
- `kill_process`
- `web_search`
- `wikipedia_lookup`

You can tune which tools require explicit user confirmation from the Settings window in the UI or by editing `settings.json` while Jarvis is stopped.

### Google Calendar / Productivity

1. Create a Google Cloud project and OAuth Client ID (Desktop app).
2. Save the downloaded client secrets as `backend/credentials/client_secret.json`.
3. First time Jarvis uses calendar tools (`get_today_schedule`, `reschedule_event`), a browser window will open for OAuth; approve access.
4. Tokens are written to `backend/credentials/google_tokens.json` (ignored by Git).

---

## Digital Suite Scenarios

Some examples of how the new modules behave:

- **Morning Briefing**
  - “Jarvis, wake up.”  
  - “Give me the briefing.”  
  - Jarvis calls `get_briefing` and responds with:
    - Weather in your configured location (Open-Meteo)
    - Today’s schedule (Google Calendar)
    - System health (“CPU at X%, RAM at Y%, battery Z%”)
    - Optional top headlines and a stock like NVDA

- **System Status and Process Control**
  - “Is my GPU running hot?” → `get_system_status`
  - “Kill that render” → `kill_process` by name or PID

- **Research**
  - “Find the density of Inconel 718 and explain it.” → `wikipedia_lookup` and/or `web_search`
  - “Compare carbon fiber and aluminum density.” → DuckDuckGo + Wikipedia tools

- **Engineer Workflow**
  - “Create a 10 cm cube of carbon fiber and tell me its mass.”  
    - Research tools pull density, CAD engine builds the part in `build123d`, Jarvis estimates mass.

---

## Commands and Windows (High Level)

- Voice control:
  - “Create a new project called [Name].”
  - “Switch project to [Name].”
  - “Give me the briefing.”
  - “What’s on my calendar today?”
  - “Turn on the office lights.”
  - “Iterate the design, make the base thicker.”

- CAD:
  - CAD window shows the latest STL / 3D object.
  - Designs are saved under `projects/<ProjectName>/cad/`.

- Web Agent:
  - “Open the browser and look for a USB-C cable under $10.”
  - The Playwright-based web agent automates Chromium using Gemini’s computer-use model.

- Printing:
  - Printer window discovers Moonraker/OctoPrint/PrusaLink printers.
  - Jarvis slices with OrcaSlicer and uploads G-code.

---

## Project Structure

```text
jarvis/
├── backend/                      # Python server & AI logic
│   ├── main.py                   # Optional entrypoint (runs server)
│   ├── server.py                 # FastAPI + Socket.IO server
│   ├── jarvis.py                 # Gemini Live audio loop + tool orchestration
│   ├── digital_suite/            # NEW: Briefing, Productivity, Research, System Ops
│   │   ├── briefing.py
│   │   ├── productivity.py
│   │   ├── research.py
│   │   ├── system_ops.py
│   │   └── __init__.py
│   ├── cad_agent.py              # build123d CAD generation
│   ├── printer_agent.py          # 3D printer discovery & slicing
│   ├── web_agent.py              # Playwright browser automation
│   ├── kasa_agent.py             # TP-Link smart home
│   ├── authenticator.py          # MediaPipe face auth
│   ├── project_manager.py        # Per-project context and logs
│   ├── tools.py                  # Base tool declarations
│   └── credentials/              # OAuth secrets and tokens (gitignored JSON)
├── src/                          # React frontend
│   ├── App.jsx
│   ├── components/
│   └── index.css
├── electron/                     # Electron main process
│   └── main.js
├── projects/                     # User project data (auto-created)
├── .env                          # API keys (Gemini)
├── requirements.txt              # Python dependencies
├── package.json                  # Node.js dependencies
└── README.md                     # This file
```

---

## Known Limitations

| Limitation | Details |
|-----------|---------|
| Platforms | Tested on Windows 10/11 and recent macOS; Linux is not officially supported. |
| Internet required | Gemini, Open-Meteo, DuckDuckGo, Wikipedia, and Google Calendar all require network access. |
| Single primary user | Face auth and reference photo assume a single primary user. |
| API quotas | Gemini free tier and external APIs may impose rate limits. |

---

## Security Notes

| Aspect | Implementation |
|--------|----------------|
| API keys | Stored in `.env`, never committed. |
| OAuth tokens | Stored under `backend/credentials/*.json`, gitignored. |
| Face data | `reference.jpg` and face embeddings are local-only. |
| File access | Destructive tools (write, kill_process, web_agent, CAD) can require explicit confirmation. |

Never share your `.env`, `backend/credentials/` JSON files, or `backend/reference.jpg`.

---

## Contributing

Contributions are welcome:

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Commit changes: `git commit -m "Add your feature"`.
4. Push: `git push origin feature/your-feature`.
5. Open a Pull Request with a clear description.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

