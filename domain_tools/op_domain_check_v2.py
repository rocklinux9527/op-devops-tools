import asyncio
import hmac
import hashlib
import base64
import urllib.parse
import json
import logging
from pathlib import Path
from functools import partial
from typing import List
import textwrap

import aiohttp
from aiohttp import ClientSession
import uvloop
import yaml

# 配置文件路径
CONFIG_FILE = 'tools/config.yaml'

# 日志格式
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# 钉钉机器人配置
class DingdingConfig:
    def __init__(self, webhook_url: str, secret: str):
        self.webhook_url = webhook_url
        self.secret = secret


class DomainMonitor:
    def __init__(self):
        self.domains = self.read_domain_name_list()
        self.ding_config = self.read_dingding_config()

    async def domain_control(self):
        async with ClientSession() as session:
            tasks = [self.check_domain_code(domain, session) for domain in self.domains]
            await asyncio.gather(*tasks)

    async def check_domain_code(self, domain: str, session: ClientSession):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            async with session.get(domain, headers=headers, timeout=3) as response:
                status_code = response.status
                response_content = await response.text()
                if status_code == 200:
                    logging.info("检查域名:%s,状态码:%d, 域名可正常访问", domain, status_code)
                else:
                    message = textwrap.dedent(f"""\
                        检查域名{domain},状态码:{status_code}域名异常域名,无法正常访问
                    """).strip()
                    await self.send_dingding_alert(message)
        except asyncio.TimeoutError:
            message = textwrap.dedent(f"""\
                检查域名{domain}时出现超时异常，无法访问
            """).strip()
            await self.send_dingding_alert(message)
        except (aiohttp.ClientError, ValueError) as e:
            message = textwrap.dedent(f"""\
                检查域名{domain}时出现异常: {str(e)}
            """).strip()
            await self.send_dingding_alert(message)

    async def send_dingding_alert(self, message: str):
        """发送告警到钉钉机器人"""
        if not self.ding_config:
            logging.warning("钉钉机器人配置不正确，无法发送告警")
            return False
        timestamp = str(round(asyncio.get_event_loop().time() * 1000))
        string_to_sign = f"{timestamp}\n{self.ding_config.secret}"
        hmac_code = hmac.new(bytes(self.ding_config.secret, 'utf-8'), bytes(string_to_sign, 'utf-8'), digestmod=hashlib.sha256).digest()
        ding_sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        headers = {
            "Content-Type": "application/json;charset=utf-8"
        }
        data = {
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        async with ClientSession() as session:
            async with session.post(self.ding_config.webhook_url, headers=headers, json=data, timeout=3) as response:
                response_data = await response.json()
                if response_data.get("errcode") == 0:
                    logging.info("发送告警到钉钉成功: %s", message)
                    return True
                else:
                    logging.warning("发送告警到钉钉失败: %s", message)
                    return False

    def read_domain_name_list(self) -> List[str]:
        """
        读取域名列表
        """
        path = Path(__file__).parent / 'domainList.txt'
        if not path.exists():
            logging.warning("域名列表文件不存在：%s", path.resolve())
            return []
        with path.open('r') as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines if line.strip()]
        return lines

    def read_dingding_config(self) -> DingdingConfig:
        """
        读取钉钉机器人配置
        """
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = yaml.safe_load(f)
            ding_config = config.get('dingding')
            if ding_config:
                return DingdingConfig(
                    webhook_url=ding_config.get('webhook_url'),
                    secret=ding_config.get('secret')
                )
            else:
                logging.warning("钉钉机器人配置不存在: %s", CONFIG_FILE)
                return None
        except Exception as e:
            logging.warning("读取钉钉机器人配置失败: %s", str(e))
            return None


if __name__ == "__main__":
    # 设置日志格式和日志级别
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    # 优化 asyncio 的事件循环
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

    # 创建 DomainMonitor 实例，然后启动监控任务
    monitor = DomainMonitor()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(monitor.domain_control())
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            pass
            logging.error("发生严重错误： %s", str(e))
    finally:
        try:
            loop.run_until_complete(loop.shutdown_asyncgens())
        finally:
            logging.info("完成所有任务，释放资源...")
            loop.close()
