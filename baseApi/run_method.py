import requests


class RunMethod(object):

    def runPostJson(self, url, headers, data):
        # 忽略不安全的请求警告信息
        requests.packages.urllib3.disable_warnings()
        # 遇到requests的ssl验证，若想直接跳过不验证，设置verify=False即可
        response = requests.post(url=url, headers=headers, json=data, verify=False)
        return response.json()

    def runPutJson(self, url, headers, data):
        # 忽略不安全的请求警告信息
        requests.packages.urllib3.disable_warnings()
        # 遇到requests的ssl验证，若想直接跳过不验证，设置verify=False即可
        response = requests.put(url=url, headers=headers, json=data, verify=False)
        return response.json()

    def runGetData(self, url, headers, data):
        # 忽略不安全的请求警告信息
        requests.packages.urllib3.disable_warnings()
        # 遇到requests的ssl验证，若想直接跳过不验证，设置verify=False即可
        response = requests.get(url=url, headers=headers, data=data, verify=False)
        return response.json()

    def runPutData(self, url, headers, data):
        # 忽略不安全的请求警告信息
        requests.packages.urllib3.disable_warnings()
        # 遇到requests的ssl验证，若想直接跳过不验证，设置verify=False即可
        response = requests.put(url=url, headers=headers, data=data, verify=False)
        return response.json()

    def runDelete(self, url, headers, data):
        # 忽略不安全的请求警告信息
        requests.packages.urllib3.disable_warnings()
        # 遇到requests的ssl验证，若想直接跳过不验证，设置verify=False即可
        response = requests.delete(url=url, headers=headers, data=data, verify=False)
        return response.json()

    def runGet(self, url, headers, data):
        # 忽略不安全的请求警告信息
        requests.packages.urllib3.disable_warnings()
        # 遇到requests的ssl验证，若想直接跳过不验证，设置verify=False即可
        response = requests.get(url=url, headers=headers, data=None, verify=False)
        # 尝试解析响应为JSON，如果失败则返回原始文本
        try:
            return response.json()
        except ValueError:
            return response.text.strip()


    def runGet_text(self, url, headers, data):
        # 忽略不安全的请求警告信息
        requests.packages.urllib3.disable_warnings()
        # 遇到requests的ssl验证，若想直接跳过不验证，设置verify=False即可
        response = requests.get(url=url, headers=headers, data=None, verify=False)
        return response.text

if __name__ == '__main__':
    run = RunMethod()
    payload = {
        "username": "zxx",
        "password": "123456"
    }
    headers = {
        "content-type": "application/json;charset=UTF-8"
    }  # 自定义请求头

    response = run.runPostJson("http://192.168.3.128:1110/admin-api/login",headers, payload)

    print(response)
