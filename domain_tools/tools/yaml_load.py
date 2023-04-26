import yaml
import os
HERE = os.path.abspath(__file__)
HOME_DIR = os.path.split(os.path.split(HERE)[0])[0]
LOG_DIR = os.path.join(HOME_DIR, "tools")

def YamlHandler():
    """
    1.文件为空检查
    2.读配置文件
    3.校验文件后缀名 yaml yml格式结尾
    4.校验配置项格式
    5.参数配置项检查
    6.配置项目不为空检查
    """
    # 检查文件是否为空
    if os.path.getsize(LOG_DIR + '/config.yaml') == 0:
        print("Configuration file is empty.")
        exit(1)

    # 读取配置文件
    with open(LOG_DIR + '/config.yaml', 'r') as f:
        try:
            config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"Error loading YAML file: {e}")
            exit(1)

    # 校验文件后缀名
    if not ('config.yaml'.endswith('.yaml') or 'config.yaml'.endswith('.yml')):
        print("Invalid file extension. File must have .yaml or .yml extension.")
        exit(1)

    # 校验配置项格式
    if 'dingTalk' not in config:
        print("Missing 'dingTalk' section in YAML file.")
        exit(1)

    dingding_config = config['dingTalk']
    if not isinstance(dingding_config, dict):
        print("'dingTalk' section must be a dictionary.")
        exit(1)

    if 'ding_hook_url' not in dingding_config or 'ding_hook_secret' not in dingding_config or 'ding_hook_token' not in dingding_config:
        print("Missing required configuration items in 'dingTalk' section.")
        exit(1)

    access_url = dingding_config.get('ding_hook_url', 'default_url')
    access_secret = dingding_config.get('ding_hook_secret', 'default_secret')
    access_token = dingding_config.get('ding_hook_token', "default_secret")
    if "default_url" in [access_url, access_secret, access_token]:
        print("Config is incomplete. Please check your configuration file.")
        exit(1)
    # 返回配置项字典
    return {"access_url": access_url, "access_secret": access_secret, "access_token": access_token}
