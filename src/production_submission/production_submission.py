from datetime import datetime

from baseApi.base_api import AllApi
from urllib.parse import quote
#产品送检单
class ProductionSubmission:

    def __init__(self, api):
        self.api = api

    def auto_production_submission_code(self):
        """获取产品送检单订单的自动编号"""
        relative_url ="admin-api/system/autocode/get/PRODUCTINSPECTION_CODE"
        production_submission_code = self.api.send_get_direct(relative_url)
        return production_submission_code

    def auto_batch_code(self):
        """获取产品送检单订单的自动批次号"""
        relative_url ="admin-api/system/autocode/get/BATCH_CODE"
        batch_code = self.api.send_get_direct(relative_url)
        return batch_code


    def production_submission_payload_list_get(self, code):
        """根据生产工单号获取负载的列表部分"""
        relative_url =f"admin-api/mes/pro/workorderV1/selectByInspection?pageNum=1&pageSize=10&workorderCode={code}"
        response = self.api.send_get_direct(relative_url)
        data = response["rows"]
        return data

    # def warehouse_info_get(self, name):
    #     """根据仓库名称查询仓库信息，返回完整仓库对象"""
    #     name = quote(name)
    #     relative_url = f"admin-api/mes/wm/warehouse/list?pageNum=1&pageSize=10&warehouseName={name}"
    #     response = self.api.send_get_direct(relative_url)
    #
    #     if not response.get("rows"):
    #         raise ValueError(f"未找到名为 {name} 的仓库，请确认仓库是否存在")
    #
    #     warehouse_info = response["rows"][0]  # 取第一个匹配结果
    #     return warehouse_info

    def production_submission_add(self, production_code):
        """生产管理-产品入库-产品送检单"""
        relative_url = "admin-api/qc/product/inspection"
        data_list = self.production_submission_payload_list_get(production_code)
        for index,item in enumerate(data_list,start=1):
            if item["batchManagement"]:
                item["batchCode"] = self.auto_batch_code()
            item["awaitingQuantity"] = item["quantity"]
            item["inspectionQuantity"] = item["quantity"]
            item["isAuto"] = "true"
            item["unitOfMeasure"] = item["supplyUnit"]
            item["workorderCode"] = item["documentCode"]
            item["workorderSerialNumber"] = index
            item["index"] = index
            item["bomId"] = item["documentLineId"]
            if "workshopName" in item and isinstance(item["workshopName"], str):
                item["workshopName"] = [part.strip() for part in item["workshopName"].split(",")]
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d  %H:%M:%S")

        # warehouse_info = self.warehouse_info_get("总仓库")
        # 新增：将 workshopName 转换为列表格式
        submission_code = self.auto_production_submission_code()
        creator = self.api.create_by_get()
        payload = {
            "createBy": creator,
            "inspectionCode": submission_code,
            "inspectionDate": formatted_time,
            "deptList" :data_list[0]["deptList"],
            "lines" : data_list ,
            "userDeptName": data_list[0]["userDeptName"],
            # 这里把仓库设成和第一个物料信息相同
            "warehouseId": data_list[0]["warehouseId"],
            "warehouseName": data_list[0]["warehouseName"],
            "warehouseCode": data_list[0]["warehouseCode"],
            "warehouseInfo":[data_list[0]["warehouseId"]],

        }
        print(payload)

        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)

        # 打印日志调试
        print("新增产品送检单响应:", response)

        # 断言接口成功
        assert response["code"] == 200, f"产品送检单新增失败，返回：{response}"

        # 保存 businessId
        business_id = response["data"]["businessId"]
        flow_ins_id,task_id = self.production_submission_get(business_id)
        payload_commit = {
            "taskid": task_id,
            "insid": flow_ins_id,
            "businessId": business_id,
            "comment": "",
            "operateType": "0",
            "billType": "qc_product_inspection"
        }
        self.process_instance_cancel_flow(payload_commit)


        return submission_code


    def production_submission_get(self, business_id):
        """生产管理-产品入库-产品送检单- 查询详情，返回 insid 和 taskid"""
        relative_url = f"admin-api/qc/product/inspection/{business_id}"

        # 通过 AllApi 的简洁 GET 方法直接发请求
        response = self.api.send_get_direct(relative_url)

        # 日志 + 断言
        print("查询订单响应:", response)
        assert response["code"] == 200, f"查询订单失败，返回：{response}"

        data = response["data"]
        return data["flowInsId"], data["taskId"]


    # def commit_task_by_business_id(self, business_id):
    #     """封装好payload数据"""
    #     insid, taskid = self.production_inspection_get(business_id)
    #
    #     payload = {
    #         "taskid": taskid,
    #         "insid": insid,
    #         "businessId": business_id,
    #         "comment": "",
    #         "operateType": "0",
    #         "billType": "qc_product_inspection"
    #     }
    #     return payload


    def process_instance_cancel_flow(self, payload):
        """产品送检单-审批"""
        relative_url = "admin-api/oa/myTask/commitTask"

        # 通过 AllApi 的简洁 POST 方法直接发请求
        response = self.api.send_post_direct(relative_url, payload)
        assert response["code"] == 200, f"产品送检单新增审批失败，返回：{response}"

        return response["code"]

        # 使用示例


# if __name__ == "__main__":
#     # 创建 类 实例
#     pis = ProductionSubmission()
#
#     # 调用 检验单新增，查询检验订单，审核订单 方法
#     business_id = pis.production_submission_add("MO202507010008")
#     payload = pis.commit_task_by_business_id(business_id)
#     response_code = pis.process_instance_cancel_flow(payload)
#     print(f"审批返回状态码：{response_code}")