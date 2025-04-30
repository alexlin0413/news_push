
import os
import re
import base64
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email import policy
from email.parser import BytesParser

def gmail_authenticate():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = None
    if os.path.exists('token.json'):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def search_latest_google_alert(service):
    query = 'from:googlealerts-noreply@google.com newer_than:2d'
    results = service.users().messages().list(userId='me', q=query, maxResults=10).execute()
    messages = results.get('messages', [])

    if not messages:
        return None

    all_links = []

    for msg_meta in messages:
        msg = service.users().messages().get(userId='me', id=msg_meta['id'], format='raw').execute()
        raw_msg = base64.urlsafe_b64decode(msg['raw'].encode('UTF-8'))
        parsed_email = BytesParser(policy=policy.default).parsebytes(raw_msg)

        html_content = None
        for part in parsed_email.walk():
            if part.get_content_type() == 'text/html':
                html_content = part.get_content()
                break

        if not html_content:
            continue

        soup = BeautifulSoup(html_content, 'html.parser')
        script_tag = soup.find("script", {"type": "application/json"})
        if not script_tag:
            continue

        try:
            data = json.loads(script_tag.string)
            cards = data.get("cards", [])
            if not cards:
                continue

            widgets = cards[0].get("widgets", [])
            for w in widgets:
                title = w.get("title")
                raw_url = w.get("url")
                if title and raw_url:
                    parsed = urlparse(raw_url)
                    query = parse_qs(parsed.query)
                    true_url = unquote(query['url'][0]) if 'url' in query else raw_url
                    all_links.append(f"{title}\n{true_url}")
        except Exception as e:
            print("❌ JSON 解析錯誤：", e)

    return all_links if all_links else None

def send_line_notify(access_token, message):
    url = 'https://api.line.me/v2/bot/message/broadcast'
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data, ensure_ascii=False))
    if response.status_code == 200:
        print("✅ LINE推播成功！")
    else:
        print(f"❌ LINE推播失敗！錯誤：{response.text}")

if __name__ == '__main__':
    LINE_ACCESS_TOKEN = 'qrr1pB8Lt9s6mGs1r9E7SqU7QI0SucHAO6GtcbFtT9ulE2Ha0xLdwj/rBFkq9LnRJxriB5Hvl/QUkSIqCLHq9foGa2zwEyZNinars+mrzFuZq3qAFwuSMw1Hy4N4SobFNfq3ZD+wluVstG2+ICr/OwdB04t89/1O/w1cDnyilFU='
    service = gmail_authenticate()
    urls = search_latest_google_alert(service)

    if urls:
        message = f"📬 今日房市快訊：\n\n" + "\n\n".join(urls)
        send_line_notify(LINE_ACCESS_TOKEN, message)
    else:
        send_line_notify(LINE_ACCESS_TOKEN, "❌ 今天沒有收到 Google 快訊郵件")
