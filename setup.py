
import requests
import os

url = "https://github.com/dscripka/openWakeWord/raw/main/openwakeword/resources/models/hey_jarvis_v0.1.onnx"
filename = "hey_jarvis_v0.1.onnx"

print(f"Downloading {filename}...")
response = requests.get(url)

with open(filename, "wb") as f:
    f.write(response.content)

print(f"Success! File saved at: {os.path.abspath(filename)}")