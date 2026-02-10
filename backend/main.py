"""
Entry point for Jarvis backend (PRD alignment).
Runs the FastAPI + Socket.IO server. Use: python -m backend.main or from backend dir: python main.py
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "server:app_socketio",
        host="127.0.0.1",
        port=8000,
        reload=False,
        loop="asyncio",
    )
