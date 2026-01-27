"""
External To-Do List API Integration
Supports any REST API that follows a standard pattern.
Configure via environment variables.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class TodoAPIClient:
    def __init__(self):
        self.api_token = os.getenv('TODO_API_TOKEN')
        self.api_url = os.getenv('TODO_API_URL', '')
        self.api_type = os.getenv('TODO_API_TYPE', 'generic').lower()  # 'generic', 'todoist', 'asana', etc.
        
    def is_configured(self):
        """Check if API is configured."""
        return bool(self.api_token and self.api_url)
    
    def fetch_todos(self):
        """Fetch todos from the external API."""
        if not self.is_configured():
            return []
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            # Different API types may have different endpoints
            if self.api_type == 'todoist':
                # Todoist API v2
                response = requests.get(
                    f'{self.api_url}/tasks',
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                tasks = response.json()
                
                # Convert Todoist format to our format
                todos = []
                for task in tasks:
                    todos.append({
                        'id': task.get('id', ''),
                        'text': task.get('content', ''),
                        'completed': task.get('completed', False),
                        'createdAt': task.get('created_at', '')
                    })
                return todos
                
            elif self.api_type == 'generic':
                # Generic REST API - expects array of {id, text, completed, createdAt}
                response = requests.get(
                    self.api_url,
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                return response.json()
                
            else:
                print(f"[WARN] Unknown TODO API type: {self.api_type}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Failed to fetch todos from API: {e}")
            return []
        except Exception as e:
            print(f"[ERROR] Unexpected error fetching todos: {e}")
            return []
    
    def add_todo(self, text):
        """Add a new todo to the external API."""
        if not self.is_configured():
            return False
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            if self.api_type == 'todoist':
                response = requests.post(
                    f'{self.api_url}/tasks',
                    headers=headers,
                    json={'content': text},
                    timeout=10
                )
            else:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json={'text': text, 'completed': False},
                    timeout=10
                )
            
            response.raise_for_status()
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to add todo to API: {e}")
            return False
    
    def update_todo(self, todo_id, completed=None, text=None):
        """Update a todo in the external API."""
        if not self.is_configured():
            return False
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_token}',
                'Content-Type': 'application/json'
            }
            
            data = {}
            if completed is not None:
                data['completed'] = completed
            if text is not None:
                data['text'] = text
            
            if self.api_type == 'todoist':
                endpoint = f'{self.api_url}/tasks/{todo_id}'
                if completed:
                    # Todoist uses close/reopen endpoints
                    if completed:
                        endpoint = f'{self.api_url}/tasks/{todo_id}/close'
                    else:
                        endpoint = f'{self.api_url}/tasks/{todo_id}/reopen'
                    response = requests.post(endpoint, headers=headers, timeout=10)
                else:
                    response = requests.post(endpoint, headers=headers, json=data, timeout=10)
            else:
                response = requests.put(
                    f'{self.api_url}/{todo_id}',
                    headers=headers,
                    json=data,
                    timeout=10
                )
            
            response.raise_for_status()
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to update todo in API: {e}")
            return False

# Global instance
_todo_client = None

def get_todo_client():
    """Get or create the global Todo API client."""
    global _todo_client
    if _todo_client is None:
        _todo_client = TodoAPIClient()
    return _todo_client

def fetch_todos_from_api():
    """Fetch todos from the external API."""
    client = get_todo_client()
    return client.fetch_todos()
