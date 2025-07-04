from urllib.parse import quote
import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)
# 改用绝对导入
from src.read_xlsx.read_buy_xlsx import ReadBuyXlsx

from baseApi.base_api import AllApi

#采购订单，通过添加物料方式生成,直接从表格读取数据
class BuyOrderNew:
    business_id = None  # 类变量存储 businessId

    def __init__(self, api):
        self.api = api



    def buy_order_add(self,data):
        """采购管理-采购订单-新增"""
        relative_url = "admin-api/mes/po/purchase"
        # 这里的采购数量，单价，税率和日期都要后期再填，可以采用查询客户，在查询采购物料信息来填负载，但如果添加多个物料的话，有点麻烦
        payload = data
        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)

        # 打印日志调试
        print("新增采购订单响应:", response)

        # 断言接口成功
        assert response["code"] == 200, f"新增采购订单失败，返回：{response}"

        # 保存 businessId
        business_id = response["data"]["businessId"]
        flow_ins_id,task_id = self.buy_order_get(business_id)
        payload_commit = {
            "taskid": task_id,
            "insid": flow_ins_id,
            "businessId": business_id,
            "comment": "",
            "operateType": "0",
            "billType": "purchase"
        }
        print(payload_commit)
        self.process_instance_cancel_flow(payload_commit)



    def buy_order_get(self, business_id):
        """采购订单 - 查询详情，返回 insid 和 taskid"""
        relative_url = f"admin-api/mes/po/purchase/{business_id}"

        # 通过 AllApi 的简洁 GET 方法直接发请求
        response = self.api.send_get_direct(relative_url)

        # 日志 + 断言
        print("查询订单响应:", response)
        assert response["code"] == 200, f"查询订单失败，返回：{response}"

        data = response["data"]
        return data["flowInsId"], data["taskId"]



    def process_instance_cancel_flow(self, payload):
        """采购管理-采购订单明细--批量审批"""
        relative_url = "admin-api/oa/myTask/commitTask"

        # 通过 AllApi 的简洁 POST 方法直接发请求
        response = self.api.send_post_direct(relative_url, payload)
        return response["code"]


# 使用示例
if __name__ == "__main__":
    # 创建 SaleOrder 实例
    buy_order_instance = BuyOrderNew()
    read = ReadBuyXlsx()
    payloads = read.read_buy_xlsx("D:/桌面/采购订单.xlsx")

    # 调用 采购订单新增，查询订单，审核订单 方法
    for data in payloads:
        # 调用 订单新增，查询订单，审核订单 方法
        business_id = buy_order_instance.buy_order_add(data)
        payload = buy_order_instance.commit_task_by_business_id(business_id)
        response_code = buy_order_instance.process_instance_cancel_flow(payload)
        print(f"审批返回状态码：{response_code}")
