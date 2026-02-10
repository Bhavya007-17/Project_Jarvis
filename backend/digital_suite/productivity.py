"""
Productivity (Module A – Chief of Staff): Google Calendar, optional Tasks/Gmail.
Uses Google Calendar API (free tier). OAuth tokens stored in backend/credentials/.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Credentials directory (sibling to digital_suite)
_BACKEND_DIR = Path(__file__).resolve().parent.parent
_CREDENTIALS_DIR = _BACKEND_DIR / "credentials"
_TOKEN_FILE = _CREDENTIALS_DIR / "google_tokens.json"
_CLIENT_SECRET_FILE = _CREDENTIALS_DIR / "client_secret.json"


def _get_credentials():
    """
    Load Google OAuth2 credentials from credentials/google_tokens.json.
    Returns None if not configured or token expired and refresh failed.
    """
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        return None

    SCOPES = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events",
    ]
    creds = None
    if _TOKEN_FILE.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(_TOKEN_FILE), SCOPES)
        except Exception:
            creds = None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        if not creds and _CLIENT_SECRET_FILE.exists():
            flow = InstalledAppFlow.from_client_secrets_file(str(_CLIENT_SECRET_FILE), SCOPES)
            # Run local server for OAuth callback (headless: use out-of-band or existing token)
            creds = flow.run_local_server(port=0)
            _CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
            with open(_TOKEN_FILE, "w") as f:
                f.write(creds.to_json())
        else:
            return None
    return creds


def get_today_schedule(calendar_id: str = "primary") -> dict:
    """
    Fetch today's events from Google Calendar.
    Returns {events: [...], error: optional str}. Each event: {summary, start, end, id}.
    """
    creds = _get_credentials()
    if not creds:
        return {"events": [], "error": "Google Calendar not configured. Add credentials to backend/credentials/."}

    try:
        from googleapiclient.discovery import build
        service = build("calendar", "v3", credentials=creds)
        now = datetime.utcnow()
        start_of_day = datetime(now.year, now.month, now.day)
        end_of_day = start_of_day + timedelta(days=1)
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=start_of_day.isoformat() + "Z",
                timeMax=end_of_day.isoformat() + "Z",
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = []
        for e in events_result.get("items", []):
            start = e.get("start", {}).get("dateTime") or e.get("start", {}).get("date")
            end = e.get("end", {}).get("dateTime") or e.get("end", {}).get("date")
            events.append({
                "id": e.get("id"),
                "summary": e.get("summary", "(No title)"),
                "start": start,
                "end": end,
            })
        return {"events": events}
    except Exception as ex:
        return {"events": [], "error": str(ex)}


def reschedule_event(calendar_id: str, event_id: str, new_start_iso: str, new_end_iso: Optional[str] = None) -> dict:
    """
    Move an event to new_start (and optionally new_end). ISO format e.g. 2025-02-09T14:00:00.
    Returns {success: bool, error: optional str}.
    """
    creds = _get_credentials()
    if not creds:
        return {"success": False, "error": "Google Calendar not configured."}

    try:
        from googleapiclient.discovery import build
        service = build("calendar", "v3", credentials=creds)
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        event["start"] = {"dateTime": new_start_iso, "timeZone": event.get("start", {}).get("timeZone", "UTC")}
        if new_end_iso:
            event["end"] = {"dateTime": new_end_iso, "timeZone": event.get("end", {}).get("timeZone", "UTC")}
        service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()
        return {"success": True}
    except Exception as ex:
        return {"success": False, "error": str(ex)}


def format_schedule_for_speech(schedule: dict) -> str:
    """Turn get_today_schedule result into a short paragraph for the assistant."""
    if schedule.get("error"):
        return f"Calendar: {schedule['error']}"
    events = schedule.get("events", [])
    if not events:
        return "You have no events on your calendar today."
    lines = ["Today's schedule:"]
    for e in events:
        summary = e.get("summary", "(No title)")
        start = e.get("start", "")
        # Simplify time display
        if "T" in start:
            try:
                t = start.split("T")[1][:5]  # HH:MM
                start = t
            except Exception:
                pass
        lines.append(f"  - {summary} at {start}")
    return "\n".join(lines)
