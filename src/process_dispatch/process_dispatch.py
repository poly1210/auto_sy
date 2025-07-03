import random
from urllib.parse import quote



#工序派工
class ProcessDispatch:

    def __init__(self, api):
        self.api = api


    def process_dispatch_payload_list_get(self, production_code,item_code):
        """获取工序派工负载的主体和列表部分"""
        relative_url = f"admin-api/mes/pro/dispatch/dispatch/pending?pageNum=1&pageSize=10&workorderCode={production_code}&itemCode={item_code}"
        response = self.api.send_get_direct(relative_url)
        return response["rows"]


    def worker_info_get_by_department(self,dept_id):
        """根据部门名称查员工信息，随机选择一个员工，并返回员工id"""
        relative_url = f"admin-api/system/user/list?pageNum=1&pageSize=10&deptId={dept_id}"
        response = self.api.send_get_direct(relative_url)
        total = response["total"]
        if total == 0:
            raise ValueError("该部门下没有员工")
        random_number = random.randint(1, total)
        random_number_new = random_number-1
        worker_info = response["rows"][random_number_new]  # 取第一个匹配结果
        return worker_info["userId"],worker_info["nickName"]

    def department_info_get(self, department_name):
        name = quote(department_name)
        relative_url = f"admin-api/system/dept/list?deptName={name}"
        response = self.api.send_get_direct(relative_url)
        return response["data"][0]["deptId"]

    def process_dispatch_add(self,production_code,item_code):
        """生产管理-工序批量派工-自动审核"""
        relative_url = "admin-api/mes/pro/dispatch/batchReport/true"
        data_lists = self.process_dispatch_payload_list_get(production_code,item_code)
        # 拿到部门名称后，查询到部门id，再查询部门下的员工
        department_name = data_lists[0]["deptNameZh"]
        dept_id = self.department_info_get(department_name)
        staff_id,staff_name = self.worker_info_get_by_department(dept_id)
        # 处理 list 数据
        # 这里的id是用户编号不是工号
        for item in data_lists:
            item["staffName"] = staff_name
            item["staffId"] = staff_id
            # 构建 payload
        payload = data_lists
        print(payload)
        # 发送请求
        response = self.api.send_post_direct(relative_url, payload)
        print("新增工序派工响应:", response)
        assert response["code"] == 200, f"新增工序派工失败，返回：{response}"

