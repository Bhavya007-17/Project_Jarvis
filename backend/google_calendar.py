"""
Google Calendar API Integration
Requires: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    import pickle
    GOOGLE_CALENDAR_AVAILABLE = True
except ImportError:
    GOOGLE_CALENDAR_AVAILABLE = False
    print("[WARN] Google Calendar libraries not installed. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class GoogleCalendarClient:
    def __init__(self):
        self.service = None
        self.credentials = None
        self.token_file = os.path.join(os.path.dirname(__file__), 'token.pickle')
        self.credentials_file = os.path.join(os.path.dirname(__file__), 'credentials.json')
        
    def authenticate(self):
        """Authenticate and create the Google Calendar service."""
        if not GOOGLE_CALENDAR_AVAILABLE:
            return False
            
        creds = None
        # The file token.pickle stores the user's access and refresh tokens.
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    print(f"[ERROR] credentials.json not found at {self.credentials_file}")
                    print("[INFO] Please download credentials.json from Google Cloud Console")
                    print("[INFO] See instructions in GOOGLE_CALENDAR_SETUP.md")
                    return False
                    
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.credentials = creds
        self.service = build('calendar', 'v3', credentials=creds)
        return True
    
    def get_events(self, max_results=10, days_ahead=7):
        """Get calendar events for the next N days."""
        if not self.service:
            if not self.authenticate():
                print("[GOOGLE CALENDAR] Authentication failed")
                return []
        
        try:
            # Get current time and time N days ahead
            # Include some past events (last 1 day) to catch today's events that might have started
            time_min = (datetime.utcnow() - timedelta(days=1)).isoformat() + 'Z'
            time_max = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            print(f"[GOOGLE CALENDAR] Fetching events from {time_min} to {time_max}")
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            print(f"[GOOGLE CALENDAR] Retrieved {len(events)} raw events from API")
            
            formatted_events = []
            for event in events:
                try:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    if not start:
                        continue
                    
                    # Handle both dateTime and date formats
                    if 'T' in start:
                        # Has time component
                        if start.endswith('Z'):
                            start_datetime = datetime.fromisoformat(start.replace('Z', '+00:00'))
                        else:
                            # Already has timezone or no timezone
                            try:
                                start_datetime = datetime.fromisoformat(start)
                            except:
                                # Fallback: try parsing without timezone
                                start_datetime = datetime.fromisoformat(start.replace('Z', ''))
                        time_str = start_datetime.strftime('%I:%M %p')
                    else:
                        # All-day event (date only)
                        start_datetime = datetime.fromisoformat(start)
                        time_str = 'All Day'
                    
                    formatted_events.append({
                        'id': event.get('id', ''),
                        'title': event.get('summary', 'No Title'),
                        'time': time_str,
                        'date': start_datetime.strftime('%Y-%m-%d'),
                        'description': event.get('description', '')
                    })
                except Exception as e:
                    print(f"[WARN] Failed to parse event {event.get('id', 'unknown')}: {e}")
                    continue
            
            print(f"[GOOGLE CALENDAR] Successfully formatted {len(formatted_events)} events")
            return formatted_events
            
        except Exception as e:
            print(f"[ERROR] Failed to fetch Google Calendar events: {e}")
            return []

# Global instance
_calendar_client = None

def get_calendar_client():
    """Get or create the global Google Calendar client."""
    global _calendar_client
    if _calendar_client is None:
        _calendar_client = GoogleCalendarClient()
    return _calendar_client

def fetch_google_calendar_events(max_results=10, days_ahead=7):
    """Fetch events from Google Calendar."""
    client = get_calendar_client()
    return client.get_events(max_results=max_results, days_ahead=days_ahead)
