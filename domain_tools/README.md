***1.域名检查非200 触发钉钉告警***

```
 功能列表
 1.1 支持钉钉参数yaml 配置
 1.2 多线程处理域名规则
```

***2.环境描述***
```
Python 3.6.5 版本
```

***3.pip 包管理***
pip3 install -r requirements.txt
```
certifi==2022.12.7
charset-normalizer==3.1.0
click==8.1.3
idna==3.4
importlib-metadata==6.5.0
itsdangerous==2.1.2
Jinja2==3.1.2
MarkupSafe==2.1.2
PyYAML==6.0
requests==2.28.2
urllib3==1.26.15
zipp==3.15.0
```

***4.测试验证***
```
检查域名:https://www.baidu.com/,状态码:200, 域名可正常访问
检查域名:https://www.taobao.com/,状态码:200, 域名可正常访问
检查域名:https://www.sina.com.cn/,状态码:200, 域名可正常访问
{'code': 0, 'status': True, 'message': 'dingding web-hook send success'}
检查域名:https://home.51cto.com/,状态码:200, 域名可正常访问
```
