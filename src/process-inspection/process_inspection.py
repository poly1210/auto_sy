from baseApi.base_api import AllApi


#工序检验单新增
class ProcessInspection:
    business_id = None  # 类变量存储 businessId

    def __init__(self):
        self.api = AllApi()
        self.api.send_login("admin-api/config.yml")

    def auto_process_inspection_code(self):
        """获取工序检验单单的自动编号"""
        relative_url ="admin-api/system/autocode/get/QC_PROCESS_INSPECTION_CODE"
        qc_process_inspection_code = self.api.send_get_direct(relative_url)
        return qc_process_inspection_code


    def process_reporting_payload_get(self, code):
        """根据工单编号，获取负载主体部分"""

        relative_url = f"admin-api/qc/processInspection/selectProcessInspection?pageNum=1&pageSize=10&workorderCode={code}"
        response = self.api.send_get_direct(relative_url)
        data = response["rows"][0]
        process_reporting_template_id = data["templateId"]
        return data, process_reporting_template_id

    def  process_reporting_payload_list_get(self, process_reporting_template_id):
        """获取负载的列表部分"""
        relative_url = f"admin-api/qc/template/{process_reporting_template_id}"
        response = self.api.send_get_direct(relative_url)
        data = response["data"]
        return data["list"]

    def process_inspection_add(self):
        """质量管理-工单检验-新增"""
        inspection_code = "MO202503180001"
        main_data, process_reporting_template_id = self.process_reporting_payload_get(inspection_code)
        print(main_data)
        list_data = self.process_reporting_payload_list_get(process_reporting_template_id)

        # 添加index
        updated_data_list = []
        for index, item in enumerate(list_data, start=1):
            new_item = item.copy()
            new_item["index"] = index
            new_item["damagedQuantity"] = 0
            new_item["inspectionQuantity"] = 0
            new_item["qualifiedQuantity"] = 0
            new_item["unqualifiedQuantity"] = 0


            updated_data_list.append(new_item)
        payload = {
            "list": updated_data_list,
            "inspectionCode": self.auto_process_inspection_code(),
            **main_data,
            "inspectionDate": "2025-06-17 17:45:48",
            "qcUserName": "admin",
            "qcUserId": 1,
            # "damagedQuantity" : 0,
            "judgmentStatus": 1,
            "returnQuantity": 0,
            "unqualifiedQuantity": 0,
            # "inspectionQuantity":main_data["inspectionQuantity"],
            # "inspectionTotal":main_data["inspectionQuantity"],
            # "processId":main_data["processId"],
            # 两个新增的必需项
            "qualifiedQuantity" : main_data["inspectionQuantity"],
            "proWorkorderInfoId": 346,

            # "remark": null ,
        }
        print(payload)

        relative_url = "admin-api/qc/processInspection"
        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)

        # 打印日志调试
        print("新增检验单响应:", response)

        # 断言接口成功
        assert response["code"] == 200, f"新增订单失败，返回：{response}"

        # 保存 businessId
        business_id = response["data"]["businessId"]

        return business_id

    def process_inspection_get(self, business_id):
        """销售订单 - 查询详情，返回 insid 和 taskid"""
        relative_url = f"admin-api/qc/processInspection/{business_id}"

        # 通过 AllApi 的简洁 GET 方法直接发请求
        response = self.api.send_get_direct(relative_url)

        # 日志 + 断言
        print("查询订单响应:", response)
        assert response["code"] == 200, f"查询订单失败，返回：{response}"

        data = response["data"]
        return data["flowInsId"], data["taskId"]

    def commit_task_by_business_id(self, business_id):
        """封装好payload数据"""
        insid, taskid = self.process_inspection_get(business_id)


        payload = {
            "taskid": taskid,
            "insid": insid,
            "businessId": business_id,
            "comment": "",
            "operateType": "0",
            "billType": "qc_process_inspection",
        }
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
    pi = ProcessInspection()

    # 调用 订单新增，查询订单，审核订单 方法
    business_id = pi.process_inspection_add()
    payload = pi.commit_task_by_business_id(business_id)
    response_code = pi.process_instance_cancel_flow(payload)
    print(f"审批返回状态码：{response_code}")
