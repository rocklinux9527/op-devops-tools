# 参考文档
# https://help.aliyun.com/document_detail/88458.html?spm=a2c4g.31965.0.0.5c9e5bb1OUNPYK#t22335.html
# https://help.aliyun.com/document_detail/88442.html?spm=a2c4g.88458.0.0.50742373g1M49M

import logging
import os
import tarfile
import sys
import oss2
import datetime
from tools.yaml_load import YamlHandler

# 设置日志格式
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_FILE = "oss_ops.log"  # 日志文件路径

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as file:
        pass

# 创建日志处理器
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# 创建日志对象
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)


class AliYunOssManager():
    def __init__(self):
        self.auth = oss2.Auth(YamlHandler().get("access_ak"), YamlHandler().get("access_sk"))
        self.bucket = oss2.Bucket(self.auth, YamlHandler().get("access_endpoint"),
                                  YamlHandler().get("access_bucket_name"),
                                  connect_timeout=10)
        self.upload_bucket_dir = YamlHandler().get("upload_bucket_dir")
        self.upload_local_dir = YamlHandler().get("upload_local_dir")
        self.pack_folder_path = YamlHandler().get("pack_folder_path")
        self.pack_output_path = YamlHandler().get("pack_output_path")
        self.delete_file_path = YamlHandler().get("delete_file_path")
        self.list_file_path = YamlHandler().get("list_file_path")
        self.download_local_dir = YamlHandler().get("download_local_dir")

    def upload_file_oss(self):
        try:
            for root, dirs, files in os.walk(self.upload_local_dir):
                for file in files:
                    local_path = os.path.join(root, file)
                    oss_path = os.path.join(self.upload_bucket_dir,
                                            os.path.relpath(local_path, self.upload_local_dir).replace("\\", "/"))
                    print("oss路径", oss_path)
                    print("本地路径", local_path)
                    self.bucket.put_object_from_file(oss_path, local_path)
                    logger.info(f"Uploaded {local_path} to {oss_path}")
            print("Uploaded file Success")
        except Exception as e:
            print("Uploaded file failed")
            logger.error(f"Failed to upload files: {str(e)}")

    def list_file_oss(self):
        prefix = self.list_file_path
        try:
            for obj in oss2.ObjectIterator(self.bucket, prefix=prefix):
                print(f"oss文件列表: {obj.key}")
                logger.info("oss文件列表：" + obj.key)
        except Exception as e:
            print(f"获取 oss文件列表错误{str(e)} ")
            logger.error(f"Failed to list OSS files: {str(e)}")

    def prefix_all_list(self, prefix):
        print("开始列举" + prefix + "全部文件");
        oss_file_size = 0;
        for obj in oss2.ObjectIterator(self.bucket, prefix='%s/' % prefix):
            print(' key : ' + obj.key)
            oss_file_size = oss_file_size + 1;
            self.download_to_local(obj.key, obj.key)
        print(prefix + " file size " + str(oss_file_size));

    def download_objects_in_directory(self,download_bucket_dir):
        files = list(oss2.ObjectIterator(self.bucket, prefix=download_bucket_dir, delimiter='/'))
        for obj in files:
            if obj.is_prefix():  # 如果是目录，则递归下载子目录
                os.makedirs(self.download_local_dir + obj.key, exist_ok=True)
                self.download_objects_in_directory(obj.key)
            else:
                # 下载对象到本地文件
                if obj.key == download_bucket_dir:
                    continue
                self.bucket.get_object_to_file(obj.key, self.download_local_dir + obj.key)
                print(f'Downloaded: {obj.key} -> {self.download_local_dir}')

    def delete_file_oss(self):
        prefix = self.delete_file_path
        try:
            if prefix:
                for obj in oss2.ObjectIterator(self.bucket, prefix=prefix):
                    logger.info("开始删除文件：" + obj.key)
                    self.bucket.delete_object(obj.key)
                print("delete file dir Success")
        except Exception as e:
            print("delete file dir not definition")
            logger.error(f"Failed to delete files: {str(e)}")

    def pack_files(self):
        try:
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%Y%m%d%H%M%S")
            timestamp = int(formatted_time)
            output_file = f"{self.pack_output_path}/oos_backup_{timestamp}.tar.gz"
            with tarfile.open(output_file, "w:gz") as tar:
                tar.add(self.pack_folder_path, arcname=os.path.basename(self.pack_folder_path))
            logger.info(f"Packed files to {output_file}")
            print(f"Packed files to {output_file} Success")
        except Exception as e:
            print(f"Failed to pack files: {str(e)} Failed")
            logger.error(f"Failed to pack files: {str(e)}")


if __name__ == "__main__":

    # 判断命令行参数
    if len(sys.argv) < 2:
        print("Usage: python script.py Supporting Parameter [upload,list,download,delete,pack]")
        sys.exit(1)
        # 获取命令行参数
    action = sys.argv[1]
    # 创建 AliYunOssManager 实例
    oss_manager = AliYunOssManager()

    # 根据命令行参数调用不同的方法
    if action == "upload":
        oss_manager.upload_file_oss()
    elif action == "list":
        oss_manager.list_file_oss()
    elif action == "download":
        oss_manager.download_objects_in_directory(YamlHandler().get("download_bucket_dir"))
        print("end \n")
    elif action == "delete":
        oss_manager.delete_file_oss()
    elif action == "pack":
        oss_manager.pack_files()
    else:
        print(f"Unknown action: {action} ")
        sys.exit(1)
