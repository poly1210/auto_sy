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
        QC_PROCESS_INSPECTION_CODE = self.api.send_get_direct(relative_url)
        return QC_PROCESS_INSPECTION_CODE

    def process_inspection_add(self):
        """销售管理-销售订单-新增"""
        payload = {

        }

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

    def processInstance_cancleFlow(self, business_id, payload):
        "销售管理-销售订单明细--批量审批"
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
    response_code = pi.processInstance_cancleFlow(business_id, payload)
    print(f"审批返回状态码：{response_code}")
