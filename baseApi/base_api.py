import requests
import pymysql
from baseApi.run_method import RunMethod
from common.read_yaml import ReadYaml
from common.read_yaml import write_token
import common.file_path as FilePath
import json
import logging
import user_context


class AllApi(object):
    def __init__(self):
        configPath = FilePath.get_config_path()
        tokenPath = FilePath.get_token_path()
        self.run = RunMethod()
        self.read_config = ReadYaml(configPath)
        self.read_token = ReadYaml(tokenPath)

        # 创建日志实例
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)

        # 配置Handler（可选）
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    # 数据库的配置
    def get_conn(self):
        db_cfg = self.read_config["admin-api/config.yml"]["mysql"]
        conn = pymysql.connect(
            host=db_cfg['host'],
            port=db_cfg['port'],
            user=db_cfg['username'],
            password=db_cfg['password'],
            database=db_cfg['database'],
            charset='utf8mb4'
        )
        return conn

    def send_login(self, api_name):
        try:
            url = self.read_config["pre-url"] + self.read_config[api_name]["url"]
            headers = self.read_config[api_name]["headers"]
            user_key = user_context.user_key
            user_info = self.read_config[api_name]["users"].get(user_key)

            if not user_info:
                raise ValueError(f"用户 {user_key} 未在配置文件中定义")

            data = {
                "username": user_info["username"],
                "password": user_info["password"]
            }

            response = self.run.runPostJson(url, headers, data)
            assert response["code"] == 200

            write_token(response)
            self.read_token = ReadYaml(FilePath.get_token_path())

            return response
        except Exception as e:
            self.logger.info(f"接口访问出错啦~ {e}")
            raise e

    def create_by_get(self):
        return user_context.user_key

    # getData请求
    def send_getData(self,path, api_name):
        self.read_api = ReadYaml(path)
        try:
            # 获取接口请求参数
            url = self.read_config["pre-url"] + self.read_api[api_name]["url"]
            auth_token = self.read_token["token"]
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json;charset=UTF-8"
            }
            data = self.read_api[api_name]["data"]
            print("\n")
            print(f"请求URL:",url)
            print("请求头:", headers)  # 发送前打印自定义头
            print("请求体（表单）:", data)  # 发送前打印
            response = self.run.runGetData(url, headers, data)
            print("响应：", json.dumps(response, indent=2, ensure_ascii=False, sort_keys=False))
            return response
        except Exception as e:
            print("接口访问出错啦~ %s" % e)

    # postJson请求
    def send_postJson(self, path, api_name):
        self.read_api = ReadYaml(path)
        try:
            # 获取接口请求参数
            url = self.read_config["pre-url"] + self.read_api[api_name]["url"]
            auth_token = self.read_token["token"]
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json;charset=UTF-8",
            }
            data = self.read_api[api_name]["data"]
            print("\n")
            print(f"请求URL:",url)
            print("请求头:", headers)  # 发送前打印自定义头
            print("请求体（表单）:", data)  # 发送前打印
            response = self.run.runPostJson(url, headers, data)
            print("响应：", json.dumps(response, indent=2, ensure_ascii=False, sort_keys=False))
            return response
        except Exception as e:
            print("接口访问出错啦~ %s" % e)

    # putJson
    def send_putJson(self, path, api_name):
        self.read_api = ReadYaml(path)
        try:
            # 获取接口请求参数
            url = self.read_config["pre-url"] + self.read_api[api_name]["url"]
            auth_token = self.read_token["token"]
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json;charset=UTF-8",
            }
            data = self.read_api[api_name]["data"]
            print("\n")
            print(f"请求URL:", url)
            print("请求头:", headers)  # 发送前打印自定义头
            print("请求体（表单）:", data)  # 发送前打印
            response = self.run.runPutJson(url, headers, data)
            print("响应：", json.dumps(response, indent=2, ensure_ascii=False, sort_keys=False))
            return response
        except Exception as e:
            print("接口访问出错啦~ %s" % e)

    # Delete
    def send_Delete(self, path, api_name):
        self.read_api = ReadYaml(path)
        try:
            # 获取接口请求参数
            url = self.read_config["pre-url"] + self.read_api[api_name]["url"]
            auth_token = self.read_token["token"]
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json;charset=UTF-8",
            }
            data = self.read_api[api_name]["data"]
            print("\n")
            print(f"请求URL:", url)
            print("请求头:", headers)  # 发送前打印自定义头
            print("请求体（表单）:", data)  # 发送前打印
            response = self.run.runDelete(url, headers, data)
            print("响应：", json.dumps(response, indent=2, ensure_ascii=False, sort_keys=False))
            return response
        except Exception as e:
            print("接口访问出错啦~ %s" % e)

    # Get
    def send_Get(self, path, api_name):
        self.read_api = ReadYaml(path)
        try:
            # 获取接口请求参数
            url = self.read_config["pre-url"] + self.read_api[api_name]["url"]
            auth_token = self.read_token["token"]
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json;charset=UTF-8",
            }
            print("\n")
            print(f"请求URL:", url)
            print("请求头:", headers)  # 发送前打印自定义头
            print("请求体（表单）:", None)  # 发送前打印
            response = self.run.runGet(url, headers, None)
            print("响应：", json.dumps(response, indent=2, ensure_ascii=False, sort_keys=False))
            return response
        except Exception as e:
            print("接口访问出错啦~ %s" % e)

    # Get_text
    def send_Get_text(self, path, api_name):
        self.read_api = ReadYaml(path)
        try:
            # 获取接口请求参数
            url = self.read_config["pre-url"] + self.read_api[api_name]["url"]
            auth_token = self.read_token["token"]
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json;charset=UTF-8",
            }
            print("\n")
            print(f"请求URL:", url)
            print("请求头:", headers)  # 发送前打印自定义头
            print("请求体（表单）:", None)  # 发送前打印
            response = self.run.runGet_text(url, headers, None)
            print("响应：", response)
            return response
        except Exception as e:
            print("接口访问出错啦~ %s" % e)

    # putDate
    def send_putDate(self, path, api_name):
        self.read_api = ReadYaml(path)
        try:
            # 获取接口请求参数
            url = self.read_config["pre-url"] + self.read_api[api_name]["url"]
            auth_token = self.read_token["token"]
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json;charset=UTF-8",
            }
            data = self.read_api[api_name]["data"]
            print("\n")
            print(f"请求URL:", url)
            print("请求头:", headers)  # 发送前打印自定义头
            print("请求体（表单）:", data)  # 发送前打印
            response = self.run.runPutData(url, headers, data)
            print("响应：", json.dumps(response, indent=2, ensure_ascii=False, sort_keys=False))
            return response
        except Exception as e:
            print("接口访问出错啦~ %s" % e)



    # 直接发送GET请求，不依赖yml，用于传具体参
    def send_get_direct(self, relative_url):
        """
        通过拼接 URL 方式直接发起 GET 请求，不依赖 yml 配置
        """
        try:
            url = self.read_config["pre-url"] + relative_url
            auth_token = self.read_token["token"]
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json;charset=UTF-8"
            }
            print("\n")
            print(f"请求URL: {url}")
            print("请求头:", headers)

            response = self.run.runGet(url, headers, None)
            print("响应：", json.dumps(response, indent=2, ensure_ascii=False, sort_keys=False))
            return response
        except Exception as e:
            print("接口访问出错啦~ %s" % e)

    # 直接发送POST请求，不依赖yml，用于传具体参
    def send_post_direct(self, relative_url, data):
        """
        通过拼接 URL 方式直接发起 POST请求，不依赖 yml 配置
        """
        try:
            url = self.read_config["pre-url"] + relative_url
            auth_token = self.read_token["token"]
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json;charset=UTF-8"
            }
            print("\n")
            print(f"请求URL: {url}")
            print("请求头:", headers)

            response = self.run.runPostJson(url, headers, data)
            print("响应：", json.dumps(response, indent=2, ensure_ascii=False, sort_keys=False))
            return response
        except Exception as e:
            print("接口访问出错啦~ %s" % e)

    #直接发送post请求，并且负载是表单格式，不是json
    def send_post_format_direct(self, relative_url, data):
        """
        通过拼接 URL 方式直接发起 POST请求，不依赖 yml 配置
        """
        try:
            url = self.read_config["pre-url"] + relative_url
            auth_token = self.read_token["token"]
            headers = {
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            print("\n")
            print(f"请求URL: {url}")
            print("请求头:", headers)
            # 忽略不安全的请求警告信息
            requests.packages.urllib3.disable_warnings()
            response = requests.post(url, data=data, headers=headers, verify=False)
            return response.json()
        except Exception as e:
            print("接口访问出错啦~ %s" % e)

if __name__ == '__main__':
    api = AllApi()
    # api.send_getData("admin-api/plm/document/list")
    api.send_login("admin-api/config.yml")
    # print(api.read["admin-api-api/login"]["method"])
