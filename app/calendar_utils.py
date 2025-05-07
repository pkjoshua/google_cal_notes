from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        raise RuntimeError("Missing token.json. Please run auth.py first.")

    return build('calendar', 'v3', credentials=creds)


def get_upcoming_events(max_results=20):
    service = get_calendar_service()
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # UTC now
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    all_events = events_result.get('items', [])
    filtered_events = []

    for event in all_events:
        summary = event.get('summary', '').lower()
        description = event.get('description', '').lower() if 'description' in event else ''

        # Skip prep events or duplicates
        if '📝 prep:' in summary or '[sales_prep]' in description:
            continue

        filtered_events.append(event)

    return filtered_events

def update_event_with_notes(event_id: str, notes: str):
    service = get_calendar_service()
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    event['description'] = notes
    service.events().update(calendarId='primary', eventId=event_id, body=event).execute()

def create_note_event(original_event, notes: str):
    service = get_calendar_service()

    summary = original_event.get('summary', 'Sales Call')
    start = original_event['start']
    end = original_event['end']

    prep_event = {
    'summary': f"📝 Prep: {summary}",
    'description': f"[SALES_PREP]\n\n{notes}",
    'start': start,
    'end': end,
    'visibility': 'private',
    'reminders': {'useDefault': False},
}

    service.events().insert(calendarId='primary', body=prep_event).execute()

