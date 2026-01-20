
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
from config import Config
from skills import available_functions
import datetime

class Brain:
    def __init__(self):
        genai.configure(api_key=Config.GEMINI_KEY)
        
        
        tools = [
            available_functions['open_daily_stack'],
            available_functions['add_task']
        ]
        
        
        self.model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
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
            return f"I encountered an error processing that: {e}"