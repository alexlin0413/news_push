import os
import base64
import requests
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Gmail API 認證
def gmail_authenticate():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    if not os.path.exists('token.json'):
        raise Exception('找不到 token.json')
    creds = service_account.Credentials.from_service_account_file('token.json', scopes=SCOPES)
    service = build('gmail', 'v1', credentials=creds)
    return service

# 找到最新一封 Google 快訊
def get_latest_google_alert(service):
    query = 'subject:"Google 快訊 - 每日摘要"'
    results = service.users().messages().list(userId='me', q=query, maxResults=1).execute()
    messages = results.get('messages', [])
    if not messages:
        raise Exception('找不到「Google 快訊 - 每日摘要」的信件')
    message = service.users().messages().get(userId='me', id=messages[0]['id'], format='full').execute()
    return message

# 從信件內容提取所有網址
def extract_links_from_email(message):
    parts = message['payload'].get('parts', [])
    for part in parts:
        if part['mimeType'] == 'text/html':
            html_content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            soup = BeautifulSoup(html_content, 'html.parser')
            links = [a['href'] for a in soup.find_all('a', href=True)]
            return links
    raise Exception('找不到 HTML 格式的內容')

# 推播訊息到 LINE
def push_to_line(access_token, message):
    url = 'https://api.line.me/v2/bot/message/broadcast'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}',
    }
    data = {
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("✅ LINE 廣播訊息發送成功！")
    else:
        print(f"❌ LINE 廣播失敗，狀態碼: {response.status_code}")
        print(f"錯誤訊息: {response.text}")

# 主程式
if __name__ == '__main__':
    ACCESS_TOKEN = 'qrr1pB8Lt9s6mGs1r9E7SqU7QI0SucHAO6GtcbFtT9ulE2Ha0xLdwj/rBFkq9LnRJxriB5Hvl/QUkSIqCLHq9foGa2zwEyZNinars+mrzFuZq3qAFwuSMw1Hy4N4SobFNfq3ZD+wluVstG2+ICr/OwdB04t89/1O/w1cDnyilFU='

    service = gmail_authenticate()
    message = get_latest_google_alert(service)
    links = extract_links_from_email(message)

    if links:
        final_message = '今日房市新聞更新完成！\n👉 點擊查看詳情：\n' + '\n'.join(links)
    else:
        final_message = '今日房市新聞更新完成，但今天沒有找到連結喔！'

    push_to_line(ACCESS_TOKEN, final_message)


