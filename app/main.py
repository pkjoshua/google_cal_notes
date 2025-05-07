from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.calendar_utils import get_upcoming_events, update_event_with_notes
from app.note_generator import generate_notes
from app.calendar_utils import create_note_event

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    events = get_upcoming_events()
    processed_events = []

    for event in events:
        summary = event.get('summary', '').lower()
        if 'demo' in summary or 'call' in summary or 'meeting' in summary:
            notes = generate_notes(event)
            processed_events.append({
                'title': event.get('summary', 'No Title'),
                'start': event.get('start', {}).get('dateTime', 'Unknown'),
                'notes': notes,
                'id': event.get('id')
            })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "events": processed_events
    })

@app.get("/generate-notes")
def generate_notes_for_sales_calls():
    events = get_upcoming_events()
    updated = []

    for event in events:
        summary = event.get('summary', '')
        lower_summary = summary.lower()

        # Skip events we've already created notes for
        if '📝 prep:' in lower_summary or '[sales_prep]' in event.get('description', '').lower():
            continue

        if any(keyword in lower_summary for keyword in ['demo', 'call', 'meeting']):
            notes = generate_notes(event)
            create_note_event(event, notes)
            updated.append(summary)

    return {"updated_events": updated}

