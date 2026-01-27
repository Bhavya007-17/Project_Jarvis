# Google Calendar API Setup

To connect your Google Calendar to JARVIS, follow these steps:

## 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

## 2. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" (unless you have a Google Workspace account)
   - Fill in the required fields (App name, User support email, etc.)
   - Add your email to test users
   - Save and continue through the scopes (default is fine)
   - Save and continue through test users
   - Back to dashboard
4. Create OAuth client ID:
   - Application type: "Desktop app"
   - Name: "JARVIS Calendar"
   - Click "Create"
5. Download the credentials JSON file
6. Rename it to `credentials.json` and place it in the `backend/` directory

**Example Structure**: The `credentials.json` file should look like this (see `backend/credentials.json.example`):
```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "your-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "YOUR_CLIENT_SECRET",
    "redirect_uris": ["http://localhost"]
  }
}
```

**Important**: Replace the placeholder values with your actual credentials from Google Cloud Console.

## 3. Install Required Python Packages

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

## 4. First-Time Authentication

When you first run JARVIS with Google Calendar enabled:
1. A browser window will open asking you to sign in to Google
2. Grant permissions to access your calendar
3. The credentials will be saved to `backend/token.pickle` for future use

## 5. Verify Setup

After setup, your calendar events should automatically appear in the Calendar & Todos panel when you launch JARVIS.

## Troubleshooting

- **"credentials.json not found"**: Make sure the file is in the `backend/` directory
- **"Permission denied"**: Make sure you've granted calendar access during OAuth
- **No events showing**: Check that you have events in your Google Calendar for the next 30 days
