from datetime import datetime

from baseApi.base_api import AllApi

#采购到货检验单生成
class BuyInspection:

    def __init__(self, api):
        self.api = api

    def auto_buy_inspection_code(self):
        """获取采购订单的自动编号"""
        relative_url ="admin-api/system/autocode/get/QC_PURCHASE_INSPECTION_CODE"
        qc_purchase_inspection_code = self.api.send_get_direct(relative_url)
        return qc_purchase_inspection_code

    def buy_order_payload_get(self, receipts_code):
        """根据到货单号获取采购检验单负载的主体部分"""
        relative_url =f"admin-api/qc/inspection/proUninspectedList?pageNum=1&pageSize=10&receiptsCode={receipts_code}"
        response = self.api.send_get_direct(relative_url)
        data = response["rows"]
        return data


    def buy_order_payload_list_get(self,purchase_template_id):
        """获取采购检验单负载的列表部分"""
        relative_url = f"admin-api/qc/template/{purchase_template_id}"
        response = self.api.send_get_direct(relative_url)
        data = response["data"]
        return data["list"]

    def inspection_user_info_get(self,user_name):
        relative_url = f"admin-api/system/user/list?pageNum=1&pageSize=10&userName={user_name}"
        response = self.api.send_get_direct(relative_url)
        data = response["rows"][0]
        return data["dept"]["deptId"],data["dept"]["deptName"],data["userId"]

    def buy_inspection_add(self,code,user_name):
        """生产管理-采购检验单-新增"""
        now = datetime.now()
        # 格式化为 YYYY-MM-DD
        formatted_date = now.strftime("%Y-%m-%d")
        dept_id, dept_name, user_id = self.inspection_user_info_get(user_name)
        relative_url = "admin-api/qc/inspection/purchase"
        receipts_code = code
        datas = self.buy_order_payload_get(receipts_code)
        inspection_codes = []
        creator = self.api.create_by_get()
        for index,item in enumerate(datas,start = 1):
            main_data, purchase_template_id = item, item["purchaseTemplateId"]
            list_data = self.buy_order_payload_list_get(purchase_template_id)
            inspection_code = self.auto_buy_inspection_code()
            inspection_codes.append(inspection_code)
            item["documentNumber"] = index
            item["qualifiedQuantity"] = item["receivedQuantity"]
            payload = {
                "inspectionCode": inspection_code,
                **main_data,
                "inspectionDate":  formatted_date,
                # todo 共有三处创建人，后面要写成和登录人名字一样
                "createBy": creator,
                "damagedQuantity" : 0,
                "inspectionQuantity" : item["receivedQuantity"],
                "returnQuantity" : 0,
                "judgmentStatus" : 1,
                "qcUserName" : user_name,
                "qcUserId" : user_id,
                "list" : list_data,

            }
            print("发送的 payload:", payload)
            # 发送 POST 请求（JSON 格式）
            response = self.api.send_post_direct(relative_url, payload)
            # 打印日志调试
            print("新增采购到货检验单响应:", response)
            # 断言接口成功
            assert response["code"] == 200, f"新增采购到货检验单失败，返回：{response}"
            # 保存 businessId
            business_id = response["data"]["businessId"]
            insid, taskid = self.buy_inspection_get(business_id)
            payload_commit = {
            "taskid": taskid,
            "insid": insid,
            "businessId": business_id,
            "comment": "",
            "operateType": "0",
            "billType": "inspection_purchase"
            }
            response_code = self.process_instance_cancel_flow(payload_commit)
            assert response_code == 200, f"采购检验审批失败，状态码：{response_code}"
        return inspection_codes



    def buy_inspection_get(self, business_id):
        """采购检验订单 - 查询详情，返回 insid 和 taskid"""
        relative_url = f"admin-api/qc/inspection/purchase/{business_id}"

        # 通过 AllApi 的简洁 GET 方法直接发请求
        response = self.api.send_get_direct(relative_url)

        # 日志 + 断言
        print("查询订单响应:", response)
        assert response["code"] == 200, f"查询订单失败，返回：{response}"

        data = response["data"]
        return data["flowInsId"], data["taskId"]



    def process_instance_cancel_flow(self,payload):
        """采购管理-采购检验订单明细--批量审批"""
        relative_url = "admin-api/oa/myTask/commitTask"

        # 通过 AllApi 的简洁 POST 方法直接发请求
        response = self.api.send_post_direct(relative_url, payload)
        assert response["code"] == 200, f"采购到货检验单审批失败，返回：{response}"

        return response["code"]




