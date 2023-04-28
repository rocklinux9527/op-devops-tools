import requests
import time
import hmac
import hashlib
import base64
import urllib.parse
import json
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


def _send_ding_ding_hook(data):
    """
    1.发送钉钉消息
    :param data:
    :return:
    """

    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
    response = requests.post(url=_dingding_webhook_sign(), headers=header, data=json.dumps(data), timeout=3)
    try:
        if response.status_code == 200:
            return {"code": 0, "status": True, "message": "dingding web-hook send success"}
        else:
            return {"code": 1, "status": True, "message": "dingding web-hook send failure"}
    except Exception as e:
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


def domain_control():
    """
    1.读取域名列表进行循环检查
    :return:
    """
    for domain in readDomainNamelist():
        check_domain_code(domain)


def check_domain_code(url):
    """
    1.监测域名逻辑
    :return:
    """
    try:
        response = requests.get(url, timeout=3)
        status_code = response.status_code
        response.close()
        if status_code == 200:
            print("检查域名:{domain},状态码:{code}, 域名可正常访问".format(domain=url, code=status_code))
        else:
            sed_dingding_markdown_msg = sed_dingding_markdown(generate_markdown_message(url, status_code))
            sed_dingding_markdown(sed_dingding_markdown_msg)
            result = _send_ding_ding_hook(sed_dingding_markdown_msg)
            print(result)
    except Exception as e:
        print(str(e))
        print(f"Error occurred while checking domain {url}: {str(e)}")


def generate_markdown_message(check_url, code_status):
    """
    1.钉钉发送固定格式消息
    2.**加醋
    3.颜色 <font color=#FF0000>红色</font> <font color=#00FF00>绿色</font> <font color=#0000FF>蓝色</font>
    :param check_url:
    :param code_status:
    :return:
    """
    url = str(check_url)
    status = str(code_status)
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    message = f"""### [业务域名非200检测]  \n\
    **检测时间**：{current_time}  \n\
    **检测对象**：域名  \n\
    **检查域名**：[{url}]({url})</font>   \n\
    **域名状态**: **<font color=#FF0000>{status}</font>**  \n\
    **检查结果**: **<font color=#FF0000>无法正常访问</font>**  \n\
    """
    return message

def sed_dingding_markdown(message):
    """
    1.发送markdown 信息
    :param message:
    :return:
    """
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "业务域名检测",
            "text": message
        }
    }
    return data

def sed_dingding_text(message):
    """
    1.发送 text文本消息
    :param message:
    :return:
    """
    data = {
        "msgtype": "text",
        "text": {
            "content": "业务域名非200检测结果",
            "message": message
        }
    }
    return data


if __name__ == "__main__":
    domain_control()
