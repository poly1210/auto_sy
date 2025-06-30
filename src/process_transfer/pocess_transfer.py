from baseApi.base_api import AllApi

#工序转移
class ProcessTransfer:
    def __init__(self, api):
        self.api = api


    def process_transfer_payload_get(self, production_code):
        """根据订单编号，获取负载"""
        relative_url = f"admin-api/pro/protransfer/selectListByProWorkorderTransfer?pageNum=1&pageSize=10&workorderCode={production_code}"
        response = self.api.send_get_direct(relative_url)
        data = response["rows"]
        return data


    def process_transfer(self,production_code):
        """工序转移"""
        relative_url = "admin-api/pro/protransfer/batchTransfer"
        payload = self.process_transfer_payload_get(production_code)
        print(payload)
        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)

        # 打印日志调试
        print("工序转移响应:", response)

        # 断言接口成功
        assert response["code"] == 200, f"工序转移失败，返回：{response}"
        # return response["code"]






