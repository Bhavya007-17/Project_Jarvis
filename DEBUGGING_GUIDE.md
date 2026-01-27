# Debugging Guide - JARVIS Issues

## Issue: Jarvis Not Responding with Audio

### Symptoms
- Text commands work (you can see transcriptions)
- No audio/speech response from Jarvis

### Possible Causes & Fixes

1. **Audio Output Device Issue**
   - Check if your speaker/headphones are selected correctly in JARVIS settings
   - Try switching to a different output device
   - Check Windows sound settings - make sure the device is not muted

2. **Audio Stream Not Starting**
   - Check backend console for errors like: `[JARVIS] [ERR] Failed to open audio output stream`
   - Restart JARVIS
   - Check if another application is using the audio device

3. **Audio Queue Blocked**
   - The fix I just made should help - audio is no longer blocked as aggressively
   - If still not working, check console for `[JARVIS DEBUG] [AUDIO]` messages

### Debug Steps
1. Open browser console (F12) and backend terminal
2. Look for `[JARVIS DEBUG] [AUDIO]` messages when Jarvis should be speaking
3. Check if `audio_in_queue` is receiving data
4. Verify audio output device in Windows sound settings

---

## Issue: Calendar Events Not Showing

### Symptoms
- You have events in Google Calendar
- Events don't appear in JARVIS Calendar panel

### Debugging Steps

1. **Check Authentication**
   - Look for `backend/token.pickle` file - if missing, you need to authenticate
   - First run should open a browser for OAuth - did it?
   - Check backend console for: `[GOOGLE CALENDAR] Authentication failed`

2. **Check API Connection**
   - Look in backend console for:
     - `[SERVER] Attempting to fetch Google Calendar events...`
     - `[GOOGLE CALENDAR] Retrieved X raw events from API`
     - `[GOOGLE CALENDAR] Successfully formatted X events`
   
3. **Check Date Range**
   - Events are fetched for the next 30 days
   - Past events (older than 1 day) are excluded
   - Make sure your events are in the future

4. **Check Browser Console**
   - Open browser console (F12)
   - Look for `[CALENDAR] Received events:` message
   - Check if events array is empty or has data

5. **Manual Test**
   - Try running this in Python to test:
   ```python
   from backend.google_calendar import fetch_google_calendar_events
   events = fetch_google_calendar_events(max_results=50, days_ahead=30)
   print(f"Found {len(events)} events")
   for event in events:
       print(f"  - {event['title']} on {event['date']} at {event['time']}")
   ```

### Common Issues

- **"credentials.json not found"**: Download credentials from Google Cloud Console
- **"Permission denied"**: Re-authenticate (delete `token.pickle` and restart)
- **"No events found"**: Check that events exist in Google Calendar for next 30 days
- **Events show but wrong dates**: Timezone issue - check your system timezone

---

## Issue: Todo List Not Showing

### Symptoms
- Todos don't appear in JARVIS
- External API configured but not working

### Debugging Steps

1. **Check API Configuration**
   - Verify `.env` file has:
     ```
     TODO_API_TOKEN=your_token
     TODO_API_URL=https://api.example.com/todos
     TODO_API_TYPE=generic
     ```

2. **Check Backend Console**
   - Look for:
     - `[SERVER] Attempting to fetch todos from external API...`
     - `[SERVER] Successfully fetched X todos from external API`
   - Or error messages if API fails

3. **Check Browser Console**
   - Look for `[TODOS] Received todos list from backend:` message
   - Check if todos array has data

4. **Test API Manually**
   - Try running:
   ```python
   from backend.todo_api import fetch_todos_from_api
   todos = fetch_todos_from_api()
   print(f"Found {len(todos)} todos")
   ```

5. **Fallback to localStorage**
   - If API not configured, JARVIS uses localStorage
   - Check browser localStorage for `jarvis_todos` key
   - Add a todo manually in the UI to test

### Common Issues

- **API not configured**: Add environment variables to `.env`
- **Invalid API token**: Check token is correct
- **API URL wrong**: Verify the base URL is correct
- **API format mismatch**: Ensure API returns JSON in expected format (see TODO_API_SETUP.md)

---

## General Debugging Tips

1. **Check Backend Console**
   - All important messages are prefixed with `[SERVER]`, `[JARVIS]`, `[GOOGLE CALENDAR]`, etc.
   - Look for ERROR or WARN messages

2. **Check Browser Console (F12)**
   - Look for `[CALENDAR]` and `[TODOS]` messages
   - Check for JavaScript errors

3. **Restart JARVIS**
   - Many issues are resolved by restarting
   - Close completely and restart

4. **Check File Permissions**
   - Make sure JARVIS can read/write:
     - `backend/token.pickle` (Google Calendar)
     - `backend/credentials.json` (Google Calendar)
     - Browser localStorage (todos)

5. **Verify Dependencies**
   - Run: `pip install -r requirements.txt`
   - Especially: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`, `requests`

---

## Quick Fixes

### Audio Not Working
```bash
# Restart JARVIS
# Check Windows sound settings
# Try different audio output device
```

### Calendar Not Working
```bash
# Delete token.pickle to re-authenticate
rm backend/token.pickle
# Restart JARVIS - will prompt for OAuth again
```

### Todos Not Working
```bash
# Check .env file has TODO_API_TOKEN and TODO_API_URL
# Or use localStorage (add todos manually in UI)
```
