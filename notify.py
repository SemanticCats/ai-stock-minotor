import requests
import os

def push_to_wechat(title, content):
    sckey = os.getenv("SERVERCHAN_SCKEY")
    if not sckey:
        print("未设置 SERVERCHAN_SCKEY，跳过推送")
        return
    url = f"https://sctapi.ftqq.com/{sckey}.send"
    data = {"title": title, "desp": content}
    try:
        resp = requests.post(url, data=data)
        print("推送结果:", resp.json())
    except Exception as e:
        print("推送失败:", e)
