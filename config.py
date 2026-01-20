
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")
    TODOIST_KEY = os.getenv("TODOIST_API_KEY")
    
    WAKE_WORD = "jarvis" 