import re
import requests
from command import enable_api, disable_api, set_status_api, Device
import config

def parse_message(message_text: str, device: Device, reply_token: str, get_current_status) -> bool:
    """解析 LINE 訊息並執行相應命令"""
    message_text = message_text.lower().strip()

    # 使用正則表達式解析命令，允許靈活輸入
    if re.match(r"^(enable|turn\s+on)(\s+.*)?$", message_text):
        if enable_api(device):
            send_message(reply_token, "Turning on the light!")
            return True
        else:
            send_message(reply_token, "Failed to turn on the light.")
            return False
    elif re.match(r"^(disable|turn\s+off)(\s+.*)?$", message_text):
        if disable_api(device):
            send_message(reply_token, "Turning off the light~")
            return True
        else:
            send_message(reply_token, "Failed to turn off the light.")
            return False
    elif re.match(r"^(get\s+status)(\s+.*)?$", message_text):
        current_status = get_current_status()
        send_message(reply_token, f"Current status: {current_status}")
        return True
    elif re.match(r"^set\s+status\s+(on|off)(\s+.*)?$", message_text):
        status = re.search(r"set\s+status\s+(on|off)", message_text).group(1)
        if set_status_api(device, status):
            send_message(reply_token, f"Status set to {status}!")
            return True
        else:
            send_message(reply_token, f"Failed to set status to {status}.")
            return False
    else:
        send_message(reply_token, "Sorry, I don't understand that message.")
        return False

def send_message(reply_token: str, text: str) -> bool:
    """發送 LINE 訊息"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {config.LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }
    try:
        response = requests.post(config.LINE_API_URL, headers=headers, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"LINE 訊息發送失敗: {e}")
        return False