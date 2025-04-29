import requests

# 發送訊息到 LINE
def push_to_line(access_token, message):
    url = 'https://api.line.me/v2/bot/message/broadcast'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
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
if __name__ == "__main__":
    ACCESS_TOKEN = "qrr1pB8Lt9s6mGs1r9E7SqU7QI0SucHAO6GtcbFtT9ulE2Ha0xLdwj/rBFkq9LnRJxriB5Hvl/QUkSIqCLHq9foGa2zwEyZNinars+mrzFuZq3qAFwuSMw1Hy4N4SobFNfq3ZD+wluVstG2+ICr/OwdB04t89/1O/w1cDnyilFU="
    MESSAGE = "今日房市新聞更新完成！👉 點擊查看詳情：https://estate.ltn.com.tw/article/19382"


    # 呼叫推送函式
    push_to_line(ACCESS_TOKEN, MESSAGE)

