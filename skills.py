
import webbrowser
import os
import subprocess
import datetime
from todoist_api_python.api import TodoistAPI
from config import Config


def open_daily_stack():
    """Opens the user's core productivity tabs."""
    urls = [
        "https://calendar.google.com",
        "https://todoist.com/app/today",
        "https://gemini.google.com"
    ]
    
    try:
        if os.name == 'nt': # Windows
            subprocess.Popen(["start", "notion://www.notion.so"], shell=True)
        else: # Mac/Linux
            subprocess.Popen(["open", "notion://www.notion.so"])
    except Exception:
        urls.append("https://www.notion.so")

    for url in urls:
        webbrowser.open(url)
    
    return "I've opened your daily dashboard."


def add_task(task_content: str, due_string: str = "today"):
    """Adds a task to Todoist.
    Args:
        task_content: The description of the task.
        due_string: Natural language date (e.g., 'tomorrow at 5pm').
    """
    if not Config.TODOIST_KEY:
        return "Todoist API key is missing."
        
    api = TodoistAPI(Config.TODOIST_KEY)
    try:
        task = api.add_task(content=task_content, due_string=due_string)
        return f"Task created: {task_content} due {due_string}"
    except Exception as e:
        return f"Error creating task: {e}"


available_functions = {
    "open_daily_stack": open_daily_stack,
    "add_task": add_task,
}