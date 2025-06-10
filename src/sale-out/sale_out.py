from baseApi.base_api import AllApi
import common.file_path as FilePath
from common.read_yaml import ReadYaml
from common.write_yaml import update_yaml_pyyaml


class SaleOut:
    business_id = None  # 类变量存储 businessId

    def __init__(self):
        self.api = AllApi()
        self.api.send_login("admin-api/config.yml")

    def sale_out_add(self):
        """销售管理-销售订单-新增"""
        filepath = "admin-api/mes/sm/sales.yml"
        full_path = FilePath.get_config_path(filepath)
        api_name = "admin-api/mes/sm/sales"

        # 发送 POST 请求（JSON 格式）
        response = self.api.send_postJson(full_path, api_name)

        # 打印日志调试
        print("新增订单响应:", response)

        # 断言接口成功
        assert response["code"] == 200, f"新增订单失败，返回：{response}"

        # 保存 businessId
        business_id = response["data"]["businessId"]

        return business_id


    def sale_out_get(self, business_id):
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
        insid, taskid = self.saleorder_get(business_id)


        payload = {
            "taskid": taskid,
            "insid": insid,
            "businessId": business_id,
            "comment": "",
            "operateType": "0",
            "billType": "sm_sales"
        }
        return  payload

    def processInstance_cancleFlow(self, business_id, payload):
        "销售管理-销售订单明细--批量审批"
        relative_url = "admin-api/oa/myTask/commitTask"

        # 通过 AllApi 的简洁 POST 方法直接发请求
        response  = self.api.send_post_direct(relative_url, payload)
        return response["code"]

# 使用示例
if __name__ == "__main__":
    # 创建 SaleOrder 实例
    sale_order_instance = SaleOrder()

    # 调用 订单新增，查询订单，审核订单 方法
    business_id = sale_order_instance.saleorder_add()
    payload = sale_order_instance.commit_task_by_business_id(business_id)
    response_code = sale_order_instance.processInstance_cancleFlow(business_id, payload)
    print(f"审批返回状态码：{response_code}")
