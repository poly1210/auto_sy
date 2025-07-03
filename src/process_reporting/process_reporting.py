from baseApi.base_api import AllApi
import json
from urllib.parse import quote

#工序报工
class ProcessReporting:
    def __init__(self, api):
        self.api = api


    def process_reporting_payload_get(self, code):
        """根据订单编号，获取负载"""
        # purchaseTemplateId = self.buy_order_payload_get()
        relative_url = f"admin-api/pro/feedback/list?pageNum=1&pageSize=10&workorderCode={code}"
        response = self.api.send_get_direct(relative_url)
        data = response["rows"]
        return data

    def has_process_inspection(self, process_code):
        """判断工序是否免检"""
        relative_url = f"admin-api/mes/pro/process/page?pageNum=1&pageSize=10&processCode={process_code}"
        response = self.api.send_get_direct(relative_url)
        data = response["rows"][0]["isInspected"]
        # 等于1是免检
        if data == "1" :
            return True
        else:
            return False



    # def worker_info_get(self, name):
    #     """根据user名称查员工信息，返回用户id"""
    #     name = quote(name)
    #     relative_url = f"admin-api/system/user/list?pageNum=1&pageSize=10&userName={name}"
    #     response = self.api.send_get_direct(relative_url)
    #
    #     if not response.get("rows"):
    #         raise ValueError(f"未找到名为 {name} 的员工，请确认员工是否存在")
    #
    #     worker_info = response["rows"][0]  # 取第一个匹配结果
    #     return worker_info["userId"],worker_info["userName"]

    def process_reporting_add(self,production_code):
        """生产管理-工序报工-新增"""
        data = self.process_reporting_payload_get(production_code)
        process_code = data[0]["processCode"]
        payload = []
        for item in data:
            # staff_id = self.worker_info_get(staff)
            # 工时是必填的,这里让工时=数量了
            item["actualHour"] = item["feedbackQuantity"]
            item["eligibleQuantity"] = item["quantity"]
            item["feedbackQuantity"] = item["quantity"]
            # 创建人一定要写
            # TODO 后面创建人根据登录人而变
            item["staffIds"] = [1]
            payload.append(item)
        print(payload)
        relative_url = "admin-api/pro/feedback/batch"


        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)
        print("新增工序报工响应:", response)
        assert response["code"] == 200, f"工序报工失败，返回：{response}"
        return process_code



# if __name__ == "__main__":
#     pr = ProcessReporting()
#     result = pr.process_reporting_add("MO202506190002")
#     print("最终结果:", result)