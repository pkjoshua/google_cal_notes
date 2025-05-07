from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    if os.path.exists('token.json'):
        print("Already authenticated.")
        return

    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=7568)  # this will now work outside FastAPI

    with open('token.json', 'w') as token:
        token.write(creds.to_json())

    print("Authentication complete. Token saved.")

if __name__ == "__main__":
    main()
