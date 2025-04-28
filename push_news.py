from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import base64
import os
from googleapiclient.discovery import build
from google.oauth2 import service_account

# Gmail API 認證
def gmail_authenticate():
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    creds = None
    if os.path.exists('token.json'):
        creds = service_account.Credentials.from_service_account_file(
            'token.json', scopes=SCOPES
        )
    else:
        raise Exception('token.json 憑證不存在')
    service = build('gmail', 'v1', credentials=creds)
    return service

# 建立 MIME 郵件
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

# 寄出 Gmail
def send_message(service, sender, to, subject, message_text):
    try:
        message = create_message(sender, to, subject, message_text)
        send_message = service.users().messages().send(userId="me", body=message).execute()
        print(f"訊息 ID: {send_message['id']}")
        return send_message
    except Exception as e:
        print(f"寄送失敗: {e}")

# 主程式示範
if __name__ == '__main__':
    service = gmail_authenticate()
    sender = ('孝麟房產小幫手', 'your_email@gmail.com')  # 改成你的寄件者名稱與信箱
    to = 'target_email@gmail.com'  # 改成你的收件者
    subject = '房市快訊通知'
    body = '今天的房市新聞更新囉～快來看看吧！'
    send_message(service, sender, to, subject, body)
