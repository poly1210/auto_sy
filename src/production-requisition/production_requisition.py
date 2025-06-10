from baseApi.base_api import AllApi


#生产领料
class ProductionRequisition:
    business_id = None  # 类变量存储 businessId

    def __init__(self):
        self.api = AllApi()
        self.api.send_login("admin-api/config.yml")

    def auto_production_requisition_code(self):
        """获取生产领料单的自动编号"""
        relative_url ="admin-api/system/autocode/get/ISSUE_CODE"
        issue_code = self.api.send_get_direct(relative_url)
        return issue_code

    def production_requisition_add(self):
        """生产管理-生产领料"""
        relative_url = "admin-api/mes/wm/issueheader"
        # 这里的payload十分复杂，等到后面再继续补上
        # payload = {
        #
        # }

        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)

        # 打印日志调试
        print("新增领料单响应:", response)

        # 断言接口成功
        assert response["code"] == 200, f"新增领料单失败，返回：{response}"

        # 保存 businessId
        business_id = response["data"]["businessId"]

        return business_id


    def production_requisition_get(self, business_id):
        """生产领料订单 - 查询详情，返回 insid 和 taskid"""
        relative_url = f"admin-api/mes/wm/issueheader/{business_id}"

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
            "billType": "wm_issue_header"
        }
        return  payload

    def processInstance_cancleFlow(self, business_id, payload):
        "生产管理--批量审批"
        relative_url = "admin-api/oa/myTask/commitTask"

        # 通过 AllApi 的简洁 POST 方法直接发请求
        response  = self.api.send_post_direct(relative_url, payload)
        return response["code"]

# 使用示例
if __name__ == "__main__":
    # 创建 SaleOut 实例
    production_requisition_instance = ProductionRequisition()

    # 调用 订单新增，查询订单，审核订单 方法
    business_id = production_requisition_instance.production_requisition_add()
    payload = production_requisition_instance.commit_task_by_business_id(business_id)
    response_code = production_requisition_instance.processInstance_cancleFlow(business_id, payload)
    print(f"审批返回状态码：{response_code}")
