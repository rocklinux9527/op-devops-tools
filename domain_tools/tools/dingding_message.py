import requests
import json

class DingTalkMessage:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.headers = {"Content-Type": "application/json;charset=utf-8"}

    def _send_message(self, data):
        try:
            response = requests.post(url=self.webhook_url, data=json.dumps(data), headers=self.headers)
            response.raise_for_status()
            result = response.json()
            if result.get("errcode") != 0:
                print(f"发送消息失败：{result.get('errmsg')}")
        except Exception as e:
            print(f"发送消息失败：{e}")

    def text(self, content, at_mobiles=None, is_at_all=False):
        data = {"msgtype": "text", "text": {"content": content}, "at": {}}
        if is_at_all:
            data["at"]["isAtAll"] = True
        elif at_mobiles:
            data["at"]["atMobiles"] = at_mobiles
        self._send_message(data)

    def link(self, title, text, message_url, pic_url=None):
        data = {"msgtype": "link", "link": {"title": title, "text": text, "messageUrl": message_url}}
        if pic_url:
            data["link"]["picUrl"] = pic_url
        self._send_message(data)

    def markdown(self, title, text, at_mobiles=None, is_at_all=False):
        data = {"msgtype": "markdown", "markdown": {"title": title, "text": text}, "at": {}}
        if is_at_all:
            data["at"]["isAtAll"] = True
        elif at_mobiles:
            data["at"]["atMobiles"] = at_mobiles
        self._send_message(data)

    def action_card(self, title, text, btns, btn_orientation="1"):
        data = {"msgtype": "actionCard", "actionCard": {"title": title, "text": text, "btnOrientation": btn_orientation, "btns": btns}}
        self._send_message(data)

    def feed_card(self, links):
        data = {"msgtype": "feedCard", "feedCard": {"links": links}}
        self._send_message(data)

#测试
webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=xxxxxx"
# 实例化 DingTalkMessage
dingtalk = DingTalkMessage(webhook_url)
# 发送 text 消息
dingtalk.text("这是一条文本消息", at_mobiles=["12345678901"])
# 发送 link 消息
dingtalk.link("这是一条链接消息", "详细信息请点击此处", "https://www.example.com")
# 发送 markdown 消息
dingtalk.markdown("这是一条Markdown消息", "**请注意**，这是一条**加粗**的消息", is_at_all=True)
# 发送 action card 消息
btns = [{"title": "操作一", "actionURL": "https://www.example.com/action1"}, {"title": "操作二", "actionURL": "https://www.example.com/action2"}]
dingtalk.action_card("这是一条Action Card消息", "请执行以下操作", btns)
# 发送 feed card 消息
links = [{"title": "链接1", "messageURL": "
