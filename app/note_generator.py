from .static_data import get_mock_notes

def generate_notes(event):
    company = event.get("summary", "Unknown Company")
    return get_mock_notes(company)
