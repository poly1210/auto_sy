from baseApi.base_api import AllApi

#采购检验单生成
class BuyInspection:
    business_id = None  # 类变量存储 businessId

    def __init__(self):
        self.api = AllApi()
        self.api.send_login("admin-api/config.yml")

    def auto_buy_inspection_code(self):
        """获取采购订单的自动编号"""
        relative_url ="admin-api/system/autocode/get/QC_PURCHASE_INSPECTION_CODE"
        qc_purchase_inspection_code = self.api.send_get_direct(relative_url)
        return qc_purchase_inspection_code

    def buy_order_payload_get(self, receipts_code):
        """根据到货单号获取采购检验单负载的主体部分"""
        relative_url =f"admin-api/qc/inspection/proUninspectedList?pageNum=1&pageSize=10&receiptsCode={receipts_code}"
        response = self.api.send_get_direct(relative_url)
        data = response["rows"][0]
        purchase_template_id = data["purchaseTemplateId"]
        #返回采购检验编号，给下面查询方法
        return data,purchase_template_id


    def buy_order_payload_list_get(self,purchase_template_id):
        """获取采购检验单负载的列表部分"""
        # purchaseTemplateId = self.buy_order_payload_get()
        relative_url = f"admin-api/qc/template/{purchase_template_id}"
        response = self.api.send_get_direct(relative_url)
        data = response["data"]
        return data["list"]

    def buy_inspection_add(self):
        """生产管理-采购检验单-新增"""
        relative_url = "admin-api/qc/inspection/purchase"
        receipts_code = "DH202506160001"
        main_data, purchase_template_id = self.buy_order_payload_get(receipts_code)
        list_data = self.buy_order_payload_list_get(purchase_template_id)
        payload = {
            "inspectionCode": self.auto_buy_inspection_code(),
            **main_data,
            "inspectionDate":  "2025-06-16",
            "createBy": "admin",
            "damagedQuantity" : 0,
            "inspectionQuantity" : 1,
            "returnQuantity" : 0,
            "judgmentStatus" : 1,
            "qcUserName" : "admin",
            "qcUserId" : 1,
            "list" : list_data,

        }
        print("发送的 payload:", payload)
        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)

        # 打印日志调试
        print("新增检验单响应:", response)

        # 断言接口成功
        assert response["code"] == 200, f"新增检验单失败，返回：{response}"

        # 保存 businessId
        business_id = response["data"]["businessId"]

        return business_id

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

    def commit_task_by_business_id(self, business_id):
        """封装好审批的payload数据"""
        insid, taskid = self.buy_inspection_get(business_id)

        payload = {
            "taskid": taskid,
            "insid": insid,
            "businessId": business_id,
            "comment": "",
            "operateType": "0",
            "billType": "inspection_purchase"
        }
        return payload

    def process_instance_cancel_flow(self,payload):
        """采购管理-采购检验订单明细--批量审批"""
        relative_url = "admin-api/oa/myTask/commitTask"

        # 通过 AllApi 的简洁 POST 方法直接发请求
        response = self.api.send_post_direct(relative_url, payload)
        return response["code"]


# 使用示例
if __name__ == "__main__":
    # 创建 SaleOrder 实例
    bi = BuyInspection()

    # 调用 检验订单新增，查询订单，审核订单 方法
    business_id = bi.buy_inspection_add()
    payload = bi.commit_task_by_business_id(business_id)
    response_code = bi.process_instance_cancel_flow(payload)
    print(f"审批返回状态码：{response_code}")
