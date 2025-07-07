from datetime import datetime

from baseApi.base_api import AllApi

#产品入库
class ProductionInventory:
    business_id = None  # 类变量存储 businessId

    def __init__(self, api):
        self.api = api

    # def auto_production_inventory_batch_code(self):
    #     """获取批次号"""
    #     relative_url ="admin-api/system/autocode/get/BATCH_CODE"
    #     inventory_batch_code = self.api.send_get_direct(relative_url)
    #     return inventory_batch_code

    def auto_production_inventory_code(self):
        """获取产品入库单订单的自动编号"""
        relative_url ="admin-api/system/autocode/get/PRODUCTRECPT_CODE"
        product_recept_code = self.api.send_get_direct(relative_url)
        return product_recept_code

    def payload_get_by_production(self, production_code):
        """根据生产工单编号获取请求负载"""
        relative_url =f"admin-api/mes/pro/workorder/select?pageNum=1&pageSize=50&workorderCode={production_code}"
        response = self.api.send_get_direct(relative_url)
        data = response["data"]
        return data["headers"][0],data["lines"]

    def payload_get_by_inspection(self, inspection_code):
        """根据生产检验单编号获取请求负载"""
        relative_url =f"admin-api/qc/inspection/select?pageNum=1&pageSize=10&inspectionCode={inspection_code}&documentType=inspection_production"
        response = self.api.send_get_direct(relative_url)
        data = response["rows"][0]
        return data


    def production_inventory_add_by_production(self, production_code):
        """生产管理-产品入库-产品入库(选择生产工单)"""
        relative_url = "admin-api/mes/wm/productrecpt"
        data_main, data_list = self.payload_get_by_production(production_code)
        updated_data_list = []
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        for index, item in enumerate(data_list, start=1):
            new_item = item.copy()
            new_item["index"] = index
            # 这里直接写死了实收数量就是应收数量
            new_item["actualQuantity"] = item["quantity"]

            # 因为负载里面是product开头，和查询的item开头不同，所以添加额外字段
            new_item["productId"] = item["itemId"]
            new_item["productCode"] = item["itemCode"]
            new_item["productName"] = item["itemName"]
            new_item["productSpc"] = item["itemSpec"]
            updated_data_list.append(new_item)

        payload = {
            **data_main ,
            "orderSource": "生产入库",
            "recptCode": self.auto_production_inventory_code(),
            "recptDate" : formatted_time,
            "list" : updated_data_list,
            "status" : "2",
            "documentType" : "pro_work_order",
        }
        print(payload)


        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)
        # 打印日志调试
        print("新增入库响应:", response)
        # 断言接口成功
        assert response["code"] == 200, f"新增入库失败，返回：{response}"
        # 保存 businessId
        business_id = response["data"]["businessId"]
        flow_ins_id,task_id = self.production_inventory_get(business_id)
        commit_payload = {
            "taskid": task_id,
            "insid": flow_ins_id,
            "businessId": business_id,
            "comment": "",
            "operateType": "0",
            "billType": "wm_product_recpt"
        }
        self.process_instance_cancel_flow(commit_payload)

    def production_inventory_add_by_inspection(self, inspection_code):
        """生产管理-产品入库-产品入库(选择生产检验单)"""
        relative_url = "admin-api/mes/wm/productrecpt"
        item = self.payload_get_by_inspection(inspection_code)
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        # 这里直接写死了实收数量就是应收数量
        item["actualQuantity"] = item["inspectionQuantity"]


        # 因为负载里面是product开头，和查询的item开头不同，所以添加额外字段
        item["productId"] = item["itemId"]
        item["productCode"] = item["itemCode"]
        item["productName"] = item["itemName"]
        # 这里一个是spec，一个是spc，贼坑
        item["productSpc"] = item["itemSpec"]
        item["workorderId"] = item["documentId"]
        item["workorderBomId"] = item["documentLineId"]

        item["isAuto"] = True

        payload = {
            "orderSource": "生产入库",
            "recptCode": self.auto_production_inventory_code(),
            "recptDate" : formatted_time,
            "list" : [item],
            "status" : "0",
            "documentType" : "inspection_production",
            "deptList":item["deptList"],
            "userDeptName":item["userDeptName"]
        }
        print(payload)


        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)
        # 打印日志调试
        print("新增产品入库响应:", response)
        # 断言接口成功
        assert response["code"] == 200, f"新增产品入库失败，返回：{response}"
        # 保存 businessId
        business_id = response["data"]["businessId"]
        flow_ins_id,task_id = self.production_inventory_get(business_id)
        commit_payload = {
            "taskid": task_id,
            "insid": flow_ins_id,
            "businessId": business_id,
            "comment": "",
            "operateType": "0",
            "billType": "wm_product_recpt"
        }
        self.process_instance_cancel_flow(commit_payload)

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



    def process_instance_cancel_flow(self, commit_payload):
        """生产管理-产品入库-产品入库--批量审批"""
        relative_url = "admin-api/oa/myTask/commitTask"

        # 通过 AllApi 的简洁 POST 方法直接发请求
        response = self.api.send_post_direct(relative_url, commit_payload)
        return response["code"]

        # 使用示例


if __name__ == "__main__":
    # 创建 类 实例
    piv = ProductionInventory()
    piv.production_inventory_add_by_production("MO202505220007")