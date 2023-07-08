import os

import yaml

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
    if 'Authentication' not in config:
        print("Missing 'Authentication' section in YAML file.")
        exit(1)

    auth_config = config['Authentication']
    if not isinstance(auth_config, dict):
        print("'Authentication' section must be a dictionary.")
        exit(1)

    if 'ak' not in auth_config or 'sk' not in auth_config or 'endpoint' not in auth_config or 'bucket_name' not in auth_config:
        print("Missing required configuration items in 'Authentication' section.")
        exit(1)

    access_ak = auth_config.get('ak', 'default_ak')
    access_sk = auth_config.get('sk', 'default_sk')
    access_endpoint = auth_config.get('endpoint', 'https://oss-cn-hangzhou.aliyuncs.com')
    access_bucket_name = auth_config.get('bucket_name', 'default_bucket_name')
    if "default_ak" in [access_ak, access_sk]:
        print("Config is incomplete. Please check your configuration file.")
        exit(1)

    oos_config = config['AliOss']
    if not isinstance(oos_config, dict):
        print("'oos_config' section must be a dictionary.")
        exit(1)

    if not all(key in oos_config for key in
               ['upload_bucket_dir', 'upload_local_dir', 'download_bucket_dir', 'download_local_dir',
                'pack_folder_path', 'pack_output_path']):
        print("Missing required keys in 'oos_config'.")
        exit(1)

    upload_bucket_dir = oos_config.get('upload_bucket_dir', 'default')
    upload_local_dir = oos_config.get('upload_local_dir', 'default')
    download_bucket_dir = oos_config.get('download_bucket_dir', 'default')
    download_local_dir = oos_config.get('download_local_dir', 'default')
    pack_folder_path = oos_config.get('pack_folder_path', 'default')
    pack_output_path = oos_config.get('pack_output_path', 'default')
    delete_file_path = oos_config.get('delete_file_path', 'default')
    list_file_path = oos_config.get('list_file_path', 'default')
    # delete oss file

    variables = [("upload_bucket_dir", upload_bucket_dir),
                 ("upload_local_dir", upload_local_dir),
                 ("download_bucket_dir", download_bucket_dir),
                 ("download_local_dir", download_local_dir),
                 ("pack_folder_path", pack_folder_path),
                 ("pack_output_path", pack_output_path),
                 ("delete_file_path", delete_file_path), ]

    missing_keys = []

    for i, (var_name, var) in enumerate(variables):
        if not var:
            missing_keys.append(var_name)

    if missing_keys:
        missing_keys_str = ", ".join(missing_keys)
        print(f"The following keys are missing in 'oos_config': {missing_keys_str}.")
        exit(1)
    # 返回配置项字典
    return {"access_ak": access_ak, "access_sk": access_sk,
            "access_endpoint": access_endpoint,
            "access_bucket_name": access_bucket_name,
            "upload_bucket_dir": upload_bucket_dir, "upload_local_dir": upload_local_dir,
            "download_bucket_dir": download_bucket_dir, "download_local_dir": download_local_dir,
            "pack_folder_path": pack_folder_path, "pack_output_path": pack_output_path,
            "delete_file_path": delete_file_path,
            "list_file_path": list_file_path
            }


# if __name__ == "__main__":
#     print(YamlHandler())
