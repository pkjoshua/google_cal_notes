from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from google_auth_oauthlib.flow import InstalledAppFlow
from app.calendar_utils import get_upcoming_events
from app.note_generator import generate_notes
from app.calendar_utils import create_note_event
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    if not os.path.exists("token.json"):
        return RedirectResponse("/auth")

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


@app.get("/auth", response_class=HTMLResponse)
def auth_form(request: Request):
    return templates.TemplateResponse(
        "upload_credentials.html",
        {"request": request}
    )


@app.post("/auth")
async def auth_upload(file: UploadFile = File(...)):
    contents = await file.read()
    with open("credentials.json", "wb") as f:
        f.write(contents)

    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=7568)

    with open("token.json", "w") as token:
        token.write(creds.to_json())

    return RedirectResponse("/", status_code=303)

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

