from baseApi.base_api import AllApi

#产品入库
class ProductionInventory:
    business_id = None  # 类变量存储 businessId

    def __init__(self):
        self.api = AllApi()
        self.api.send_login("admin-api/config.yml")

    def auto_production_inventory_code(self):
        """获取产品送检单订单的自动编号"""
        relative_url ="admin-api/system/autocode/get/PRODUCTRECPT_CODE"
        product_recept_code = self.api.send_get_direct(relative_url)
        return product_recept_code

    def production_inventory_payload_get(self, inventory_code):
        """根据工单编号获取请求负载"""
        relative_url =f"admin-api/mes/pro/workorder/select?pageNum=1&pageSize=50&workorderCode={inventory_code}"
        response = self.api.send_get_direct(relative_url)
        data = response["data"]
        return data["headers"][0],data["lines"]

    def production_inventory_add(self,code):
        """生产管理-产品入库-产品入库"""
        relative_url = "admin-api/mes/wm/productrecpt"
        data_main, data_list = self.production_inventory_payload_get(code)
        updated_data_list = []
        for index, item in enumerate(data_list, start=1):
            new_item = item.copy()
            new_item["index"] = index
            # 这里直接写死了实收数量就是应收数量
            new_item["actualQuantity"] = item["quantity"]

            # 因为负载里面是product开头，和查询的item开头不同，所以添加额外字段
            new_item["productId"] = item["itemId"]
            new_item["productCode"] = item["itemCode"]
            new_item["productName"] = item["itemName"]
            new_item["productSpec"] = item["itemSpec"]
            updated_data_list.append(new_item)

        # 这里的payload十分复杂，等到后面再继续补上
        payload = {
            **data_main ,
            "orderSource": "生产入库",
            "recptCode": self.auto_production_inventory_code(),
            "recptDate" : "2025-06-17 16:18:53",
            "list" : updated_data_list,
            "status" : "0",
            "documentType" : "pro_work_order",
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


    def production_inventory_get(self, business_id):
        """生产管理-产品入库-产品入库-查询详情，返回 insid 和 taskid"""
        relative_url = f"admin-api/mes/wm/productrecpt/{business_id}"

        # 通过 AllApi 的简洁 GET 方法直接发请求
        response = self.api.send_get_direct(relative_url)

        # 日志 + 断言
        print("查询订单响应:", response)
        assert response["code"] == 200, f"查询订单失败，返回：{response}"

        data = response["data"]
        return data["flowInsId"], data["taskId"]


    def commit_task_by_business_id(self, business_id):
        """封装好payload数据"""
        insid, taskid = self.production_inventory_get(business_id)

        payload = {
            "taskid": taskid,
            "insid": insid,
            "businessId": business_id,
            "comment": "",
            "operateType": "0",
            "billType": "wm_product_recpt"
        }
        return payload


    def process_instance_cancel_flow(self, payload):
        """生产管理-产品入库-产品入库--批量审批"""
        relative_url = "admin-api/oa/myTask/commitTask"

        # 通过 AllApi 的简洁 POST 方法直接发请求
        response = self.api.send_post_direct(relative_url, payload)
        return response["code"]

        # 使用示例


if __name__ == "__main__":
    # 创建 类 实例
    piv = ProductionInventory()
    inventory_code = "MO202505230003"
    # 调用 检验单新增，查询检验订单，审核订单 方法
    business_id = piv.production_inventory_add(inventory_code)
    payload = piv.commit_task_by_business_id(business_id)
    response_code = piv.process_instance_cancel_flow(payload)
    print(f"审批返回状态码：{response_code}")