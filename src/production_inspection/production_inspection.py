import random
from datetime import datetime

from baseApi.base_api import AllApi
from urllib.parse import quote
#生产检验单
class ProductionInspection:

    def __init__(self, api):
        self.api = api

    def auto_production_inspection_code(self):
        """获取生产检验单订单的自动编号"""
        relative_url ="admin-api/system/autocode/get/QC_PRODUCTION_INSPECTION_CODE"
        production_inspection_code = self.api.send_get_direct(relative_url)
        return production_inspection_code


    def production_inspection_payload_main_get(self, commission_code):
        """根据到货单号获取采购检验单负载的主体部分"""
        relative_url =f"admin-api/qc/product/inspection/select?pageNum=1&pageSize=10&inspectionCode={commission_code}&status=2"
        response = self.api.send_get_direct(relative_url)
        data_main = response["rows"]
        return data_main

    def production_inspection_payload_list_get(self, template_id):
        """根据到货单号获取采购检验单负载的列表部分"""
        relative_url =f"admin-api/qc/template/{template_id}"
        response = self.api.send_get_direct(relative_url)
        data_list = response["data"]["list"][0]
        return data_list

    def worker_info_get(self):
        """查询所有员工，随机选择一个员工，并返回员工id"""
        relative_url = f"admin-api/system/user/list?status=0"
        response = self.api.send_get_direct(relative_url)
        total = response["total"]
        if total == 0:
            raise ValueError("没有员工")
        random_number = random.randint(1, total)
        random_number_new = random_number-1
        worker_info = response["rows"][random_number_new]  # 取第一个匹配结果
        return worker_info["userId"],worker_info["nickName"]

    def production_inspection_add(self, commission_code):
        """生产管理-产品入库-生产检验单"""
        relative_url = "admin-api/qc/inspection"
        data_mains = self.production_inspection_payload_main_get(commission_code)
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d  %H:%M:%S")
        user_id,user_name = self.worker_info_get()

        for item in data_mains:
            inspection_code = self.auto_production_inspection_code()
            template_id = item["productionTemplateId"]
            data_list = self.production_inspection_payload_list_get(template_id)
            item["damagedQuantity"] = 0
            item["documentCode"] = item["inspectionCode"]
            item["documentDate"] = formatted_time
            item["documentId"] = item["workorderId"]
            item["documentLineId"] = item["bomId"]
            item["documentNumber"] = item["workorderSerialNumber"]
            item["documentType"] = "inspection_production"
            item["inspectionCode"] = inspection_code
            item["inspectionDate"] = formatted_time
            item["judgmentStatus"] = 1
            item["qcUserId"] = user_id
            item["qcUserName"] = user_name
            item["warehouseInfo"] = [item["warehouseId"]]
            item["qualifiedQuantity"] = item["inspectionQuantity"]
            item["returnQuantity"] = 0
            data_list["damagedQuantity"] = 0
            data_list["inspectionQuantity"] = 0
            data_list["qualifiedQuantity"] = 0
            data_list["unqualifiedQuantity"] = 0
            data_list["index"] = 1


            payload = {
                **item,
                "list": [data_list] ,
            }
            print(payload)


            # 发送 POST 请求（JSON 格式）
            response = self.api.send_post_direct(relative_url, payload)

            # 打印日志调试
            print("新增生产检验响应:", response)

            # 断言接口成功
            assert response["code"] == 200, f"生产检验失败，返回：{response}"

            # 保存 businessId
            business_id = response["data"]["businessId"]
            flow_ins_id,task_id = self.production_inspection_get(business_id)
            payload_commit = {
                "taskid": task_id,
                "insid": flow_ins_id,
                "businessId": business_id,
                "comment": "",
                "operateType": "0",
                "billType": "inspection_production"
            }
            self.process_instance_cancel_flow(payload_commit)





    def production_inspection_get(self, business_id):
        """生产管理-产品入库-产品送检单- 查询详情，返回 insid 和 taskid"""
        relative_url = f"admin-api/qc/inspection/{business_id}"

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
        """审批"""
        relative_url = "admin-api/oa/myTask/commitTask"

        # 通过 AllApi 的简洁 POST 方法直接发请求
        response = self.api.send_post_direct(relative_url, payload)
        return response["code"]

        # 使用示例


if __name__ == "__main__":
    # 创建 类 实例
    pis = ProductionInspection()

    pis.production_inspection_add("CS202507010007")
