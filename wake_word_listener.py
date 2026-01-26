"""
Wake Word Listener for JARVIS
Listens for "jarvis" wake word and launches the main application.
Also listens for "jarvis shut down" to close the application.
Runs continuously in the background.
Uses sounddevice for audio input (no pyaudio).
"""

import os
import sys
import subprocess
import time
import socket
import signal
import io
from pathlib import Path

try:
    import sounddevice as sd
    import numpy as np
    import speech_recognition as sr
except ImportError as e:
    print(f"Error: Required packages not installed. Install with: pip install sounddevice numpy SpeechRecognition")
    print(f"Missing: {e}")
    sys.exit(1)

# Configuration
WAKE_WORD = "jarvis"
SHUTDOWN_PHRASE = "jarvis shut down"
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
ENERGY_THRESHOLD = 1000  # Adjust based on your microphone sensitivity

# Paths
SCRIPT_DIR = Path(__file__).parent.absolute()
MAIN_SCRIPT = SCRIPT_DIR / "electron" / "main.js"
BACKEND_SCRIPT = SCRIPT_DIR / "backend" / "server.py"

# Global process reference
main_process = None

def check_if_running():
    """Check if the main application is already running."""
    try:
        # Check if port 8000 is in use (backend server port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()
        return result == 0
    except:
        return False

def find_process_by_port(port=8000):
    """Find process ID using the specified port."""
    try:
        import psutil
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
                return conn.pid
    except ImportError:
        # Fallback: try to kill by process name on Windows
        if sys.platform == 'win32':
            try:
                result = subprocess.run(
                    ['netstat', '-ano'],
                    capture_output=True,
                    text=True
                )
                for line in result.stdout.split('\n'):
                    if f':{port}' in line and 'LISTENING' in line:
                        parts = line.split()
                        if len(parts) > 4:
                            return int(parts[-1])
            except:
                pass
    return None

def shutdown_application():
    """Shutdown the main JARVIS application."""
    global main_process
    
    if not check_if_running():
        print("[WAKE WORD] JARVIS is not running. Nothing to shut down.")
        return
    
    print("[WAKE WORD] Shutting down JARVIS...")
    
    try:
        # Try to find and kill the process
        pid = find_process_by_port(8000)
        if pid:
            try:
                if sys.platform == 'win32':
                    subprocess.run(['taskkill', '/F', '/PID', str(pid)], check=False)
                else:
                    os.kill(pid, signal.SIGTERM)
                print(f"[WAKE WORD] Terminated process {pid}")
            except Exception as e:
                print(f"[WAKE WORD] Could not terminate process {pid}: {e}")
        
        # Also try to kill the main process if we have a reference
        if main_process:
            try:
                main_process.terminate()
                main_process.wait(timeout=5)
            except:
                try:
                    main_process.kill()
                except:
                    pass
        
        # Wait a moment and check again
        time.sleep(2)
        if not check_if_running():
            print("[WAKE WORD] JARVIS shut down successfully!")
        else:
            print("[WAKE WORD] Warning: JARVIS may still be running.")
            
    except Exception as e:
        print(f"[WAKE WORD] Error shutting down JARVIS: {e}")

def launch_application():
    """Launch the main JARVIS application."""
    global main_process
    
    if check_if_running():
        print("[WAKE WORD] JARVIS is already running. Skipping launch.")
        return
    
    print("[WAKE WORD] Launching JARVIS...")
    
    try:
        # Launch Electron app (which will start the backend)
        if sys.platform == 'win32':
            # Windows: Use npm start or electron directly
            main_process = subprocess.Popen(
                ['npm', 'start'],
                cwd=SCRIPT_DIR,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
            )
        else:
            # Linux/Mac: Use npm start
            main_process = subprocess.Popen(
                ['npm', 'start'],
                cwd=SCRIPT_DIR,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        print("[WAKE WORD] JARVIS launched successfully!")
    except Exception as e:
        print(f"[WAKE WORD] Error launching JARVIS: {e}")

def recognize_speech_from_audio(audio_data_np, sample_rate=SAMPLE_RATE):
    """Recognize speech from numpy audio array using speech_recognition."""
    try:
        recognizer = sr.Recognizer()
        
        # Convert float32 to int16 PCM
        # Clamp values to [-1, 1] range first
        audio_clipped = np.clip(audio_data_np, -1.0, 1.0)
        # Convert to int16
        audio_int16 = (audio_clipped * 32767).astype(np.int16)
        audio_bytes = audio_int16.tobytes()
        
        # Create AudioData object
        # speech_recognition expects (bytes, sample_rate, sample_width)
        # sample_width = 2 for 16-bit (2 bytes per sample)
        audio_source = sr.AudioData(audio_bytes, sample_rate, 2)
        
        # Recognize using Google Speech Recognition (free, no API key needed for basic use)
        try:
            text = recognizer.recognize_google(audio_source).lower()
            return text
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            print(f"[WAKE WORD] Speech recognition service error: {e}")
            return None
            
    except Exception as e:
        print(f"[WAKE WORD] Speech recognition error: {e}")
        return None

def listen_for_wake_word():
    """Continuously listen for the wake word using sounddevice."""
    print(f"[WAKE WORD] Listening for '{WAKE_WORD}'...")
    print("[WAKE WORD] Say 'jarvis' to launch the application.")
    print("[WAKE WORD] Say 'jarvis shut down' to close the application.")
    
    audio_buffer = []
    buffer_duration = 3.0  # seconds - longer buffer for better recognition
    buffer_samples = int(SAMPLE_RATE * buffer_duration)
    
    last_recognition_time = 0
    recognition_cooldown = 3.0  # seconds between recognition attempts
    
    def audio_callback(indata, frames, time_info, status):
        """Callback for audio input stream."""
        if status:
            print(f"[WAKE WORD] Audio status: {status}")
        
        # Add to buffer (indata is already a numpy array)
        audio_buffer.append(indata.copy())
        
        # Keep buffer size manageable
        total_samples = sum(len(chunk) for chunk in audio_buffer)
        while total_samples > buffer_samples:
            removed = audio_buffer.pop(0)
            total_samples -= len(removed)
    
    try:
        # Open audio input stream
        stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype=np.float32,  # Use float32 for better quality
            blocksize=CHUNK_SIZE,
            callback=audio_callback
        )
        stream.start()
        print("[WAKE WORD] Audio stream started. Listening...")
        
        last_check_time = time.time()
        check_interval = 2.0  # Check every 2 seconds
        
        while True:
            time.sleep(0.1)
            
            # Periodically check the buffer for wake words
            current_time = time.time()
            if current_time - last_check_time >= check_interval:
                # Also respect cooldown period
                if current_time - last_recognition_time < recognition_cooldown:
                    continue
                    
                last_check_time = current_time
                
                if len(audio_buffer) > 0:
                    # Concatenate recent audio (last 2 seconds)
                    recent_samples = int(SAMPLE_RATE * 2.0 / CHUNK_SIZE)
                    recent_audio = np.concatenate(audio_buffer[-recent_samples:])
                    
                    # Simple energy-based detection
                    energy = np.abs(recent_audio).mean()
                    
                    if energy > ENERGY_THRESHOLD:
                        # Try speech recognition
                        text = recognize_speech_from_audio(recent_audio)
                        
                        if text:
                            print(f"[WAKE WORD] Heard: {text}")
                            last_recognition_time = current_time
                            
                            # Check for shutdown phrase first (more specific)
                            if SHUTDOWN_PHRASE in text or ("shut down" in text and WAKE_WORD in text):
                                print(f"[WAKE WORD] Shutdown command detected!")
                                shutdown_application()
                                time.sleep(3)  # Wait before listening again
                            
                            # Check for wake word
                            elif WAKE_WORD in text:
                                print(f"[WAKE WORD] Wake word '{WAKE_WORD}' detected!")
                                launch_application()
                                time.sleep(5)  # Wait before listening again
                
    except KeyboardInterrupt:
        print("\n[WAKE WORD] Shutting down wake word listener...")
    except Exception as e:
        print(f"[WAKE WORD] Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'stream' in locals():
            stream.stop()
            stream.close()

if __name__ == "__main__":
    print("=" * 50)
    print("JARVIS Wake Word Listener")
    print("=" * 50)
    print(f"Wake word: '{WAKE_WORD}'")
    print(f"Shutdown phrase: '{SHUTDOWN_PHRASE}'")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    listen_for_wake_word()
