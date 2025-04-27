
import os
import base64
import json
import requests
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email import policy
from email.parser import BytesParser

CHANNEL_ACCESS_TOKEN = '你的 LINE Bot Channel Access Token'

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def gmail_authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_google_alerts(service):
    today = datetime.utcnow() - timedelta(hours=8)
    today_str = today.strftime('%Y/%m/%d')

    results = service.users().messages().list(
        userId='me',
        q=f'from:(googlealerts-noreply@google.com) after:{today_str}',
        maxResults=5
    ).execute()

    messages = results.get('messages', [])
    news_list = []

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='raw').execute()
        msg_bytes = base64.urlsafe_b64decode(msg_data['raw'].encode('ASCII'))
        email_message = BytesParser(policy=policy.default).parsebytes(msg_bytes)
        payload = email_message.get_payload()

        if isinstance(payload, list):
            body = payload[0].get_payload(decode=True).decode()
        else:
            body = payload

        lines = body.splitlines()
        for line in lines:
            if line.startswith('http'):
                news_list.append(line)
            elif line.strip() != "" and not line.startswith('<'):
                news_list.append(line.strip())

    return '\n\n'.join(news_list[:5])

def push_to_line(message):
    headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    response = requests.post(
        "https://api.line.me/v2/bot/message/broadcast",
        headers=headers,
        json=data
    )
    return response.status_code

if __name__ == "__main__":
    service = gmail_authenticate()
    news = get_google_alerts(service)
    if news:
        status = push_to_line(news)
        print(f"推播成功，狀態碼：{status}")
    else:
        print("今天沒有新的 Google快訊。")
