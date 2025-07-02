from datetime import datetime
from urllib.parse import quote

from baseApi.base_api import AllApi


#工序派工
class ProcessDispatch:

    def __init__(self, api):
        self.api = api

    # def auto_work_order_code(self):
    #     """获取工序派工的自动编号"""
    #     relative_url ="admin-api/system/autocode/get/PRO_WORKORDER_DISPATCH_CODE"
    #     work_code = self.api.send_get_direct(relative_url)
    #     return work_code



    def process_dispatch_payload_list_get(self, code):
        """获取工序派工负载的主体和列表部分"""
        relative_url = f"admin-api/mes/pro/dispatch/dispatch/pending?pageNum=1&pageSize=10&workorderCode={code}"
        response = self.api.send_get_direct(relative_url)

        return response["rows"]
    # TODO 这里要改成按部门查找，因为不同工序分给了不同部门
    def worker_info_get(self, name):
        """根据user名称查员工信息，返回用户id"""
        name = quote(name)
        relative_url = f"admin-api/system/user/list?pageNum=1&pageSize=10&userName={name}"
        response = self.api.send_get_direct(relative_url)

        if not response.get("rows"):
            raise ValueError(f"未找到名为 {name} 的员工，请确认员工是否存在")

        worker_info = response["rows"][0]  # 取第一个匹配结果
        return worker_info["userId"]


    # def worker_payload(self):
    #     """获取负载中的工作人员列表"""
    #     relative_url = f"admin-api/system/user/list?pageNum=1&pageSize=10000&deptId=103&status=0"
    #     response = self.api.send_get_direct(relative_url)
    #     return response["rows"]

    def department_info_get(self, department_name):
        name = quote(department_name)
        relative_url = f"admin-api/system/dept/list?deptName={name}"
        response = self.api.send_get_direct(relative_url)
        return response["data"][0]["deptId"]

    def process_dispatch_add(self,production_code,worker_name):
        """生产管理-工序批量派工-自动审核"""
        relative_url = "admin-api/mes/pro/dispatch/batchReport/true"
        data_lists = self.process_dispatch_payload_list_get(production_code)


        # 处理 list 数据
        for item in data_lists:
            # dept_name = item["deptName"]
            # dept_list = [int(x) for x in dept_name.split(',')]
            # item["dispatchQuantity"] = item["disQuantity"]

            item["staffName"] = worker_name
            item["staffId"] = self.worker_info_get(worker_name)

            # 构建 payload
            payload = data_lists
                # "deptId": self.department_info_get(item["deptNameZh"]),
                # "dispatchCode": self.auto_work_order_code(),
                # "dispatchDate": formatted_time,
                # "deptList":dept_list,
                # "status": "0",
                # "staffOptions": staff_options,
                # "list":[item]# 使用更新后的列表


            print(payload)

            # 发送请求
            response = self.api.send_post_direct(relative_url, payload)
            print("新增工序派工响应:", response)
            # assert response["code"] == 200, f"新增工序派工失败，返回：{response}"
            # business_id = response["data"]["businessId"]
            # insid , taskid = self.process_dispatch_get(business_id)
            # payload_commit = {
            #     "taskid": taskid,
            #     "insid": insid,
            #     "businessId": business_id,
            #     "comment": "",
            #     "operateType": "0",
            #     "billType": "pro_workorder_dispatch"
            # }
            # self.process_instance_cancel_flow(payload_commit)



    # def process_dispatch_get(self, business_id):
    #     """查询详情，返回 insid 和 taskid"""
    #     relative_url = f"admin-api/mes/pro/dispatch/{business_id}"
    #
    #     # 通过 AllApi 的简洁 GET 方法直接发请求
    #     response = self.api.send_get_direct(relative_url)
    #
    #     # 日志 + 断言
    #     print("查询订单响应:", response)
    #     assert response["code"] == 200, f"查询订单失败，返回：{response}"
    #
    #     data = response["data"]
    #     return data["flowInsId"], data["taskId"]
    #
    #
    #
    # def process_instance_cancel_flow(self,payload):
    #     """生产管理--批量审批"""
    #     relative_url = "admin-api/oa/myTask/commitTask"
    #
    #     # 通过 AllApi 的简洁 POST 方法直接发请求
    #     response  = self.api.send_post_direct(relative_url, payload)
    #     return response["code"]

# 使用示例
# if __name__ == "__main__":
#     # 创建实例
#     pdp = ProcessDispatch()
#     pdp.process_dispatch_add("MO202506030008","jwg")

