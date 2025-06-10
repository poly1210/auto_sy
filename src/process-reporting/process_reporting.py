from baseApi.base_api import AllApi
import json

#工序报工
class ProcessReporting:

    def __init__(self):
        self.api = AllApi()
        self.api.send_login("admin-api/config.yml")

    def process_reporting_add(self):
        """生产管理-工序报工-新增"""
        payload = [
            {
                "actualHour": "5",
                "eligibleQuantity": 5,
                "feedbackQuantity": 10,
                "id": 546,
                "industrialWasteQuantity": 1,
                "materialWasteQuantity": 1,
                "remark": None,
                "staffId": 1,
                "staffName": "admin"
            }
        ]
        relative_url = "admin-api/pro/feedback/batch"


        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)
        print("新增工序报工响应:", response)
        return response



if __name__ == "__main__":
    pr = ProcessReporting()
    result = pr.process_reporting_add()
    print("最终结果:", result)