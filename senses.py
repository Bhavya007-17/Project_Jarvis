
import pyttsx3
import speech_recognition as sr
import openwakeword
from openwakeword.model import Model
import pyaudio
import numpy as np
import os

class Speaker:
    def __init__(self):
        self.engine = pyttsx3.init()
        
        self.engine.setProperty('rate', 170) 

    def speak(self, text):
        print(f"JARVIS: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

class Ear:
    def __init__(self):
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(current_dir, "hey_jarvis_v0.1.onnx")

        
        if not os.path.exists(model_path):
            raise ValueError(f"Model file missing at: {model_path}. Did you run setup.py?")

       
        self.owwModel = Model(
            wakeword_models=[model_path], 
            inference_framework="onnx"
        )
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()

    def listen_for_wake_word(self):
        """Blocks until wake word is detected."""
        print("Waiting for wake word...")
        
        
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, 
                        input=True, frames_per_buffer=1280)

        while True:
            
            audio = np.frombuffer(stream.read(1280), dtype=np.int16)
            
            
            prediction = self.owwModel.predict(audio)
            
            
            if prediction["hey_jarvis_v0.1"] > 0.5:
                stream.stop_stream()
                stream.close()
                p.terminate()
                return True

    def listen_for_command(self):
        """Records after wake word is detected."""
        with self.mic as source:
            print("Listening for command...")
            
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                text = self.recognizer.recognize_google(audio)
                print(f"USER: {text}")
                return text
            except sr.UnknownValueError:
                return None
            except sr.WaitTimeoutError:
                return None