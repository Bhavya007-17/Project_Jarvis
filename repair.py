# repair.py
import requests
import os

# The OFFICIAL release URL (v0.5.1)
url = "https://github.com/dscripka/openWakeWord/releases/download/v0.5.1/hey_jarvis_v0.1.onnx"
filename = "hey_jarvis_v0.1.onnx"

print(f"Attempting download from: {url}")

try:
    response = requests.get(url, allow_redirects=True)
    
    # Check if the download actually worked (Status 200 = OK)
    if response.status_code == 404:
        raise Exception("File not found (404). The version number might have changed.")
    
    response.raise_for_status()
    
    with open(filename, "wb") as f:
        f.write(response.content)
    
    # Verify file size (Real model is ~400KB - 500KB)
    size = os.path.getsize(filename)
    print(f"Download complete! File size: {size} bytes")
    
    if size < 5000:
        print("❌ WARNING: File is too small. It is likely corrupted.")
    else:
        print("✅ SUCCESS: Model downloaded correctly. You can run main.py now.")

except Exception as e:
    print(f"❌ Error: {e}")