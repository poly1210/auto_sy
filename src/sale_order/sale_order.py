from baseApi.base_api import AllApi
import sys
import os

# 获取项目根目录（假设 sale_order.py 路径是 D:\desktop\lyr\erp_auto\src\sale_order\sale_order.py，向上找两级到 erp_auto 目录）
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)

# 改用绝对导入
from src.read_xlsx.read_sales_xlsx import ReadSalesXlsx

#销售订单新增
class SaleOrder:
    business_id = None  # 类变量存储 businessId

    def __init__(self, api):
        self.api = api

    def auto_sale_code(self):
        """获取销售订单的自动编号"""
        relative_url ="admin-api/system/autocode/get/SALES_CODE"
        purchase_code = self.api.send_get_direct(relative_url)
        return purchase_code

    def sale_order_add(self,data):
        """销售管理-销售订单-新增"""
        payload = data
        relative_url = "admin-api/mes/sm/sales"
        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)
        # 打印日志调试
        print("新增订单响应:", response)

        # 断言接口成功
        assert response["code"] == 200, f"新增订单失败，返回：{response}"

        # 保存 businessId
        business_id = response["data"]["businessId"]

        return business_id


    def sale_order_get(self, business_id):
        """销售订单 - 查询详情，返回 insid 和 taskid"""
        relative_url = f"admin-api/mes/sm/sales/{business_id}"

        # 通过 AllApi 的简洁 GET 方法直接发请求
        response = self.api.send_get_direct(relative_url)

        # 日志 + 断言
        print("查询订单响应:", response)
        assert response["code"] == 200, f"查询订单失败，返回：{response}"

        data = response["data"]
        return data["flowInsId"], data["taskId"]

    def commit_task_by_business_id(self, business_id):
        """封装好payload数据"""
        insid, taskid = self.sale_order_get(business_id)
        payload = {
            "taskid": taskid,
            "insid": insid,
            "businessId": business_id,
            "comment": "",
            "operateType": "0",
            "billType": "sm_sales"
        }
        print (payload)
        return  payload

    def process_instance_cancel_flow(self,payload):
        """销售管理-销售订单明细--批量审批"""
        relative_url = "admin-api/oa/myTask/commitTask"

        # 通过 AllApi 的简洁 POST 方法直接发请求
        response  = self.api.send_post_direct(relative_url, payload)
        return response["code"]

# 使用示例
if __name__ == "__main__":
    # 创建 SaleOrder 实例
    sale_order_instance = SaleOrder()
    read = ReadSalesXlsx()
    payloads = read.read_sales_xlsx("D:/桌面/销售订单.xlsx")
    for data in payloads:
        # 调用 订单新增，查询订单，审核订单 方法
        business_id = sale_order_instance.sale_order_add(data)
        payload = sale_order_instance.commit_task_by_business_id(business_id)
        response_code = sale_order_instance.process_instance_cancel_flow(payload)
        print(f"审批返回状态码：{response_code}")
