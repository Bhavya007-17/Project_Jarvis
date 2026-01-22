# brain.py
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
from config import Config
from skills import available_functions
import datetime

class Brain:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_KEY)
        
        # Define the tools for Gemini
        tools = [
            available_functions['open_daily_stack'],
            available_functions['add_task']
        ]
        
        # System instruction sets the persona
        self.model = genai.GenerativeModel(
            # CHANGED: Added '-latest' to fix the 404 error
            model_name='gemini-1.5-flash-latest-001',
            tools=tools,
            system_instruction=(
                f"You are Jarvis. Current time: {datetime.datetime.now().isoformat()}. "
                "You are concise. If a user asks to do something, call the tool. "
                "If they ask a question, answer briefly."
            )
        )
        self.chat = self.model.start_chat(enable_automatic_function_calling=True)

    def process_input(self, text_input):
        """Sends text to Gemini and executes functions automatically."""
        try:
            response = self.chat.send_message(text_input)
            return response.text
        except Exception as e:
            # This prints the exact error to your terminal so we can see it
            print(f"\n[ERROR DETAILS]: {e}\n") 
            return "I'm having trouble connecting to my brain right now."