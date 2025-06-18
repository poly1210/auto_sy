from baseApi.base_api import AllApi
from urllib.parse import quote

#销售出库
class SaleOut:
    business_id = None  # 类变量存储 businessId

    def __init__(self):
        self.api = AllApi()
        self.api.send_login("admin-api/config.yml")

    def auto_sale_out_code(self):
        """获取出库订单的自动编号"""
        relative_url ="admin-api/system/autocode/get/PRODUCTSALSE_CODE"
        product_salse_code = self.api.send_get_direct(relative_url)
        return product_salse_code

    def process_reporting_payload_get(self, code):
        """根据销售订单编号，获取负载主体部分"""
        relative_url = f"admin-api/mes/sm/sales/select?pageNum=1&pageSize=50&salesCode={code}&isReturn=0"
        response = self.api.send_get_direct(relative_url)
        data = response["data"]
        return data["father"][0], data["children"]

    def client_info_get(self, name):
        # 这个有的订单会自带客户信息
        """根据客户名称查客户信息，返回用户id"""
        name_code = quote(name)
        relative_url = f"admin-api/mes/md/client/list?pageNum=1&pageSize=10&clientName={name_code}"
        response = self.api.send_get_direct(relative_url)

        if not response.get("rows"):
            raise ValueError(f"未找到名为 {name} 的客户，请确认客户是否存在")

        client_info = response["rows"][0]  # 取第一个匹配结果
        return client_info["clientId"],client_info["clientName"],client_info["clientCode"]

    def sale_out_add(self):
        """销售管理-销售订单-出库"""
        relative_url = "admin-api/mes/wm/productsalse/addNew"
        data_main,data_list = self.process_reporting_payload_get("SAL2025241")
        updated_data_list = []
        for item in data_list:
            new_item = item.copy()
            # 这里直接把出库数量等于未收货数量，后面再改
            new_item["quantitySalse"] = item["unreceivedGoods"]
            updated_data_list.append(new_item)
        # salseCode是出库单据号，salesCode是销售订单号，注意分辨
        payload = {

            **data_main,
            "list" :updated_data_list,
            "salseCode": self.auto_sale_out_code(),
            "salseDate": "2025-06-17 17:45:48",
            "warehouseInfo" : [],


        }
        print(payload)

        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)

        # 打印日志调试
        print("新增出库响应:", response)

        # 断言接口成功
        assert response["code"] == 200, f"新增出库失败，返回：{response}"

        # 保存 businessId
        business_id = response["data"]["businessId"]

        return business_id


    def sale_out_get(self, business_id):
        """销售出库订单 - 查询详情，返回 insid 和 taskid"""
        relative_url = f"admin-api/mes/wm/productsalse/{business_id}"

        # 通过 AllApi 的简洁 GET 方法直接发请求
        response = self.api.send_get_direct(relative_url)

        # 日志 + 断言
        print("查询订单响应:", response)
        assert response["code"] == 200, f"查询订单失败，返回：{response}"

        data = response["data"]
        return data["flowInsId"], data["taskId"]

    def commit_task_by_business_id(self, business_id):
        """封装好payload数据"""
        insid, taskid = self.sale_out_get(business_id)


        payload = {
            "taskid": taskid,
            "insid": insid,
            "businessId": business_id,
            "comment": "",
            "operateType": "0",
            "billType": "wm_product_salse"
        }
        return  payload

    def process_instance_cancel_flow(self,  payload):
        "销售管理-销售订单明细--批量审批"
        relative_url = "admin-api/oa/myTask/commitTask"

        # 通过 AllApi 的简洁 POST 方法直接发请求
        response  = self.api.send_post_direct(relative_url, payload)
        return response["code"]

# 使用示例
if __name__ == "__main__":
    # 创建 SaleOut 实例
    sale_out_instance = SaleOut()

    # 调用 订单新增，查询订单，审核订单 方法
    business_id = sale_out_instance.sale_out_add()
    payload = sale_out_instance.commit_task_by_business_id(business_id)
    response_code = sale_out_instance.process_instance_cancel_flow(payload)
    print(f"审批返回状态码：{response_code}")
