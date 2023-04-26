#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3.6
import requests
import time
import hmac
import hashlib
import base64
import urllib.parse
import json
import asyncio
from tools.yaml_load import YamlHandler
def _dingding_webhook_sign():
    try:
        access_url = YamlHandler().get("access_url")
        token = YamlHandler().get("access_token")
        secret = YamlHandler().get("access_secret")
        timestamp = str(round(time.time() * 1000))
        string_to_sign = f"{timestamp}\n{secret}"
        hmac_code = hmac.new(bytes(secret, 'utf-8'), bytes(string_to_sign, 'utf-8'), digestmod=hashlib.sha256).digest()
        ding_sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return f"{access_url}/robot/send?access_token={token}&timestamp={timestamp}&sign={ding_sign}"
    except Exception as e:
        print(f"Error: {e}")
        return None


def sendDingDingHook(data):
    session = requests.Session()
    """
     1.使用 requests.Session() 对象发送 HTTP 请求.
     这将使多次调用 sendDingDingHook() 更有效率。
     使用 response.raise_for_status() 方法检查 HTTP 响应的状态码是否为 200，以确保请求成功。
     2.此外，如果发送请求时出现异常，应该关闭响应对象 response。
     3.捕获 requests.exceptions.RequestException 异常，以避免捕获 Exception 异常并打印其字符串表示形式。这将更清晰地显示实际的异常类型和消息。
    """
    try:
        header = {
            "Content-Type": "application/json",
            "Charset": "UTF-8"
        }
        send_data = json.dumps(data).encode("utf-8")
        response = session.post(url=_dingding_webhook_sign(), headers=header, data=send_data, timeout=3)
        response.raise_for_status()
        result_dingding = response.json()
        if result_dingding.get("errcode") == 0 and result_dingding.get("errmsg") == "ok":
            return {"code": 0, "status": True, "message": "dingding web-hook send success"}
        else:
            return {"code": 1, "status": True, "message": "dingding web-hook send failure"}

    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
    finally:
        response.close()


def readDomainNamelist():
    """
    1.一行一行读取域名文件列表
    2.去除文件内部空行和末尾的'\n'去掉
    3.使用列表推导式生成域名列表内容
    4.返回域名列表
    :return:
    """
    with open('domainList.txt', 'r') as f:
        lines = f.readlines()
        non_empty_lines = [line.strip() for line in lines if line.strip()]
    return non_empty_lines


def domain_control_old():
    """
    1.遍历域名列表拿出域名进行处理逻辑
    """
    urlList = readDomainNamelist()
    for send in urlList:
        print(check_domain_code(send))

async def domain_control():
    tasks = []
    for domain in readDomainNamelist():
        tasks.append(asyncio.ensure_future(check_domain_code(domain)))
    await asyncio.wait(tasks)


async def check_domain_code(url):
    """
    1.监测域名逻辑
    :return:
    """
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, requests.get, url, {'timeout': 3})
        status_code = response.status_code
        response.close()
        if status_code == 200:
            print("检查域名:{domain},状态码:{code}, 域名可正常访问".format(domain=url, code=status_code))
        else:
            message = """检查域名{domain},状态码:{status_code}域名异常域名,无法正常访问""".format(domain=url,
                                                                                                  status_code=status_code)
            data = {"msgtype": "text", "text": {"content": "{message}".format(message=message)}}
            result = sendDingDingHook(data)
            print(result)
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while checking domain {url}: {str(e)}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(domain_control())
    finally:
        loop.close()
