# External To-Do List API Setup

JARVIS can connect to external to-do list APIs to sync your tasks. Currently supported:

- **Generic REST API**: Any REST API that returns/accepts JSON in the expected format
- **Todoist**: Todoist API v2 (coming soon)

## Configuration

Add these environment variables to your `.env` file:

```env
# Required: Your API token/key
TODO_API_TOKEN=your_api_token_here

# Required: Base URL of the API
TODO_API_URL=https://api.example.com/todos

# Optional: API type (default: 'generic')
TODO_API_TYPE=generic
```

## Generic REST API Format

Your API should follow this format:

### GET Request (Fetch Todos)
- **Endpoint**: `GET {TODO_API_URL}`
- **Headers**: `Authorization: Bearer {TODO_API_TOKEN}`
- **Response**: Array of todo objects:
```json
[
  {
    "id": "123",
    "text": "Complete project",
    "completed": false,
    "createdAt": "2025-01-27T10:00:00Z"
  }
]
```

### POST Request (Add Todo)
- **Endpoint**: `POST {TODO_API_URL}`
- **Headers**: `Authorization: Bearer {TODO_API_TOKEN}`
- **Body**: `{"text": "New task", "completed": false}`
- **Response**: Created todo object

### PUT Request (Update Todo)
- **Endpoint**: `PUT {TODO_API_URL}/{todo_id}`
- **Headers**: `Authorization: Bearer {TODO_API_TOKEN}`
- **Body**: `{"completed": true}` or `{"text": "Updated task"}`
- **Response**: Updated todo object

## Example: Connecting to Your To-Do List Website

If your to-do list website provides an API:

1. Get your API token from the website's settings/developer section
2. Find the API base URL (e.g., `https://api.yourwebsite.com/v1`)
3. Add to `.env`:
   ```env
   TODO_API_TOKEN=abc123xyz
   TODO_API_URL=https://api.yourwebsite.com/v1/todos
   TODO_API_TYPE=generic
   ```

## Testing

After setup, when you launch JARVIS, it will automatically fetch your todos from the external API. You should see a status message indicating how many todos were loaded.

## Troubleshooting

- **"No todos loaded"**: Check that your API token and URL are correct
- **"Connection error"**: Verify the API URL is accessible and the token is valid
- **"Format error"**: Ensure your API returns todos in the expected JSON format
