import os
import re
import base64
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

# 認證 Gmail
def gmail_authenticate():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    creds = None
    # 嘗試讀取現有 token.json
    if os.path.exists('token.json'):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # 如果 token 不存在或失效，就重新認證
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # 把新的憑證存回 token.json
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

# 搜尋最新的 Google快訊郵件
def search_latest_google_alert(service):
    query = 'subject:"Google 快訊 - 每日摘要"'
    results = service.users().messages().list(userId='me', q=query, maxResults=1).execute()
    messages = results.get('messages', [])
    if not messages:
        print("❌ 沒找到今天的 Google 快訊郵件")
        return None
    msg = service.users().messages().get(userId='me', id=messages[0]['id'], format='raw').execute()
    msg_raw = base64.urlsafe_b64decode(msg['raw'].encode('UTF-8'))
    soup = BeautifulSoup(msg_raw, 'html.parser')
    urls = [a['href'] for a in soup.find_all('a', href=True)]
    return urls

# 傳送到 LINE
def send_line_notify(access_token, message):
    url = 'https://api.line.me/v2/bot/message/broadcast'
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("✅ LINE推播成功！")
    else:
        print(f"❌ LINE推播失敗！錯誤：{response.text}")

# 主程式
if __name__ == '__main__':
    LINE_ACCESS_TOKEN = '你的LINE長期Token'  # <--- 改成你自己的 LINE Bot Token

    service = gmail_authenticate()
    urls = search_latest_google_alert(service)

    if urls:
        links = '\n'.join(urls)
        message = f"今日房市新聞更新！👉\n{links}"
        send_line_notify(LINE_ACCESS_TOKEN, message)
    else:
        send_line_notify(LINE_ACCESS_TOKEN, "❌ 今天沒有收到 Google 快訊郵件")
