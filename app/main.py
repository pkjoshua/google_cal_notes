from fastapi import FastAPI
from .calendar import get_upcoming_events, update_event_with_notes
from .note_generator import generate_notes

app = FastAPI()

@app.get("/generate-notes")
def generate_notes_for_sales_calls():
    events = get_upcoming_events()
    updated = []

    for event in events:
        summary = event.get('summary', '').lower()
        if 'demo' in summary or 'call' in summary or 'meeting' in summary:
            notes = generate_notes(event)
            update_event_with_notes(event['id'], notes)
            updated.append(event['summary'])

    return {"updated_events": updated}
