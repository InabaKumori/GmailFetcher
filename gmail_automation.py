from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import os.path
import time
from datetime import datetime
import psycopg2
from email.utils import parsedate_to_datetime

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host="localhost",
        database="gmail",
        user="postgres",
        password=""
    )
    cur = conn.cursor()

    # Get the timestamp of the last processed email
    cur.execute("SELECT MAX(date) FROM emails")
    last_timestamp = cur.fetchone()[0]

    while True:
        try:
            # Call the Gmail API to fetch new messages since the last timestamp
            query = 'after:' + last_timestamp.strftime('%Y/%m/%d') if last_timestamp else ''
            results = service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])

            if not messages:
                print('No new messages.')
            else:
                print(f'Found {len(messages)} new message(s).')
                for message in messages:
                    msg = service.users().messages().get(userId='me', id=message['id']).execute()
                    payload = msg['payload']
                    headers = payload['headers']
                    subject = next((header['value'] for header in headers if header['name'] == 'Subject'), '')
                    sender = next((header['value'] for header in headers if header['name'] == 'From'), '')
                    date_str = next((header['value'] for header in headers if header['name'] == 'Date'), '')

                    # Convert the date string to a valid timestamp
                    date = parsedate_to_datetime(date_str)

                    # Get the email content
                    parts = payload.get('parts', [])
                    body = None
                    if parts:
                        body = parts[0]['body'].get('data')
                    if body:
                        body = base64.urlsafe_b64decode(body.encode('UTF-8')).decode('UTF-8')
                    else:
                        body = ''

                    # Check if the email already exists in the database
                    cur.execute("SELECT COUNT(*) FROM emails WHERE email_id = %s", (message['id'],))
                    email_exists = cur.fetchone()[0] > 0

                    if not email_exists:
                        # Insert the new email into the PostgreSQL database
                        cur.execute(
                            "INSERT INTO emails (email_id, subject, sender, date, content) VALUES (%s, %s, %s, %s, %s)",
                            (message['id'], subject, sender, date, body)
                        )
                        conn.commit()

                        # Update the last processed timestamp
                        last_timestamp = date

                # Retrieve and display the emails from the database
                cur.execute("SELECT * FROM emails ORDER BY date DESC")
                rows = cur.fetchall()
                for row in rows:
                    print(f"ID: {row[0]}, Subject: {row[2]}, Sender: {row[3]}, Date: {row[4]}")

            # Wait for a shorter interval before checking for new emails again
            print(f'Waiting for 1 second... ({datetime.now()})')
            time.sleep(1)

        except KeyboardInterrupt:
            print('Program interrupted by user. Exiting...')
            break

    # Close the database connection
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
