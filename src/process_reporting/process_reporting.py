from baseApi.base_api import AllApi
import json
from urllib.parse import quote

#工序报工
class ProcessReporting:

    def __init__(self):
        self.api = AllApi()
        self.api.send_login("admin-api/config.yml")

    # 查询之后，返回报工id和feedbackQuantity（报工数量）
    def process_reporting_payload_get(self, code):
        """根据订单编号，获取负载"""
        # purchaseTemplateId = self.buy_order_payload_get()
        relative_url = f"admin-api/pro/feedback/list?pageNum=1&pageSize=10&workorderCode={code}"
        response = self.api.send_get_direct(relative_url)
        data = response["rows"][0]
        return data["id"], data["feedbackQuantity"]

    def worker_info_get(self, name):
        """根据user名称查员工信息，返回用户id"""
        name = quote(name)
        relative_url = f"admin-api/system/user/list?pageNum=1&pageSize=10&userName={name}"
        response = self.api.send_get_direct(relative_url)

        if not response.get("rows"):
            raise ValueError(f"未找到名为 {name} 的员工，请确认员工是否存在")

        worker_info = response["rows"][0]  # 取第一个匹配结果
        return worker_info["userId"],worker_info["userName"]

    def process_reporting_add(self):
        """生产管理-工序报工-新增"""
        payload_id,payload_feedback_quantity = self.process_reporting_payload_get("MO202506060009")
        staff_id , staff_name = self.worker_info_get("admin")
        payload = [
            {
                # "actualHour": "5",
                # "eligibleQuantity": 5,
                "feedbackQuantity": payload_feedback_quantity,
                "id": payload_id,
                # "industrialWasteQuantity": 1,
                # "materialWasteQuantity": 1,
                # "remark": None,
                "staffId": staff_id,
                "staffName": "staff_name"
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