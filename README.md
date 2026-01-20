# Jarvis: Multimodal AI Desktop Assistant

**A hybrid edge-cloud voice assistant engineered for secure, context-aware desktop automation.**

## 📖 Description
Jarvis is a custom voice interface designed to bridge the gap between local signal processing and cloud-based cognitive reasoning. Unlike standard consumer assistants, this project prioritizes low-latency execution and extensible, deterministic tool use. It operates by delegating "reflex" tasks (wake-word detection) to the edge while offloading semantic reasoning to large language models, enabling a private yet intelligent user experience tailored for engineering workflows.

## ⚙️ Technical Features

### **Hybrid Architecture**
* **Edge Processing:** Utilizes **ONNX Runtime** and `openWakeWord` for private, offline wake-word detection, eliminating the need for continuous cloud audio streaming.
* **Cloud Intelligence:** Integrates **Google Gemini 1.5 Flash** for high-speed semantic understanding and complex query resolution.

### **Deterministic Function Calling**
* Transforms the LLM from a text generator into a logic engine.
* Dynamically selects between conversational responses and executing Python code based on user intent (e.g., distinguishing between "What is the time?" and "Set a timer").

### **System Integration**
* **Task Automation:** Direct REST API integration with **Todoist** for natural language task management.
* **OS Control:** Context-aware browser automation using `webbrowser` and custom URI schemes to manage workspace states (Notion, Calendar).

### **Audio Pipeline**
* **Input:** Asynchronous audio buffering with `PyAudio` and dynamic ambient noise thresholding via `SpeechRecognition`.
* **Output:** Low-latency feedback loop using `pyttsx3` for near-instantaneous system status updates.

## 🛠️ Tech Stack
![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square&logo=python)
![Gemini](https://img.shields.io/badge/Google_Gemini-1.5_Flash-orange?style=flat-square&logo=google)
![ONNX](https://img.shields.io/badge/Runtime-ONNX-lightgrey?style=flat-square)

* **Core:** Python 3.11, Google Generative AI SDK
* **Signal Processing:** NumPy, PyAudio, OpenWakeWord
* **APIs:** Todoist REST API, Google Calendar API

## 🚀 Quick Start
```bash
# Clone and Setup
git clone [https://github.com/yourusername/jarvis-assistant.git](https://github.com/yourusername/jarvis-assistant.git)
cd jarvis-assistant

# Install Dependencies & Models
pip install -r requirements.txt
python setup.py

# Run
python main.py
