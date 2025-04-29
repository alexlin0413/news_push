import os
import base64
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from googleapiclient.discovery import build
from google.oauth2 import service_account

# --- Gmail 認證 ---
def gmail_authenticate():
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    if os.path.exists('token.json'):
        creds = service_account.Credentials.from_service_account_file(
            'token.json', scopes=SCOPES
        )
    else:
        raise Exception('token.json 憑證不存在')
    service = build('gmail', 'v1', credentials=creds)
    print("✅ Gmail API 認證成功！")
    return service

# --- 建立 MIME 郵件 ---
def create_message(sender, to, subject, message_text):
    message = MIMEMultipart()
    message['Subject'] = str(Header(subject, 'utf-8'))
    sender_name, sender_email = sender
    message['From'] = str(Header(sender_name, 'utf-8')) + f" <{sender_email}>"
    message['To'] = to
    msg = MIMEText(message_text, 'plain', 'utf-8')
    message.attach(msg)
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

# --- 發送 Gmail ---
def send_gmail(service, sender, to, subject, message_text):
    try:
        message = create_message(sender, to, subject, message_text)
        send_message = service.users().messages().send(userId="me", body=message).execute()
        print(f"✅ Gmail 寄送成功，訊息 ID: {send_message['id']}")
        return send_message
    except Exception as e:
        print(f"❌ Gmail寄送失敗: {e}")

# --- 發送 LINE 廣播訊息 ---
def send_line_broadcast(message_text):
    access_token = 'qrr1pB8Lt9s6mGs1r9E7SqU7QI0SucHAO6GtcbFtT9ulE2Ha0xLdwj/rBFkq9LnRJxriB5Hvl/QUkSIqCLHq9foGa2zwEyZNinars+mrzFuZq3qAFwuSMw1Hy4N4SobFNfq3ZD+wluVstG2+ICr/OwdB04t89/1O/w1cDnyilFU='  
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'messages': [{'type': 'text', 'text': message_text}]
    }
    url = 'https://api.line.me/v2/bot/message/broadcast'
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("✅ LINE 廣播訊息發送成功！")
    else:
        print(f"❌ LINE 廣播失敗，錯誤訊息: {response.text}")
    return response

# --- 主程式 ---
if __name__ == '__main__':
    # 要推送的訊息內容
    news_message = "📢 今日房市快訊更新囉，快來看看！"

    # Step 1. 推播 LINE 訊息
    send_line_broadcast(news_message)

    # Step 2. 寄送 Gmail 通知
    service = gmail_authenticate()
    sender = ('孝麟房產小幫手', 'your_email@gmail.com')  # 改成你的寄件者名稱與 email
    recipient = 'target_email@gmail.com'               # 改成你的收件者 email
    subject = '🏠 房市快訊通知'
    body = '今天的房市新聞已更新，趕快查看吧！'
    send_gmail(service, sender, recipient, subject, body)

