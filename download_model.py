import openwakeword.utils


print("Downloading 'Hey Jarvis' model...")
openwakeword.utils.download_models(model_names=["hey_jarvis_v0.1"])
print("Download complete!")