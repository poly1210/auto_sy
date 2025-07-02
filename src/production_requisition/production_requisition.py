from datetime import datetime
from urllib.parse import quote

from baseApi.base_api import AllApi


#生产领料
class ProductionRequisition:
    business_id = None  # 类变量存储 businessId

    def __init__(self, api):
        self.api = api

    def item_info_get(self, code) :
        """根据产品编号获取具体内容"""
        url = f"admin-api/mes/md/mditem/page?pageNum=1&pageSize=10&itemCode={code}"
        res = self.api.send_get_direct(url)
        if res.get("code") == 200 and res["total"] > 0:
            return res["rows"][0]
        raise ValueError(f"未找到产品编号：{code}")

    def item_code_get_by_product_code(self, product_code):
        """根据生产工单号查询物料编码,并判断是否需要检验"""
        relative_url = f"admin-api/mes/pro/workorderV1/list?pageNum=1&pageSize=10&workorderCode={product_code}"
        response = self.api.send_get_direct(relative_url)
        data = response["rows"][0]["list"]
        is_inspection = False
        for item in data:
            item_code = item["itemCode"]
            item_info = self.item_info_get(item_code)
            is_exempt_inspection = item_info["isExemptInspection"]
            if is_exempt_inspection == "Y" :
                is_inspection = True
                break
        return is_inspection



    def auto_production_requisition_code(self):
        """获取生产领料单的自动编号"""
        relative_url ="admin-api/system/autocode/get/ISSUE_CODE"
        issue_code = self.api.send_get_direct(relative_url)
        return issue_code

    def has_report(self, production_code):
        """判断生产工单是否报工"""
        relative_url = f"admin-api/mes/pro/workorderV1/list?pageNum=1&pageSize=10&workorderCode={production_code}"
        response = self.api.send_get_direct(relative_url)
        data = response["rows"][0]
        return data["report"]

    def production_requisition_payload_list_get(self, code):
        """获取生产领料单负载的主体和列表部分"""
        relative_url = f"admin-api/mes/pro/workorderV1/select?pageNum=1&pageSize=50&workorderCode={code}&issueType=0&isReturn=false"
        response = self.api.send_get_direct(relative_url)
        data = response["data"]
        return data["father"][0],data["children"]

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

    def production_requisition_add(self,production_code):
        """生产管理-生产领料"""
        relative_url = "admin-api/mes/wm/issueheader"
        data_main,data_list = self.production_requisition_payload_list_get(production_code)

        # 获取当前时间并格式化
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

        # 获取仓库信息（例如“总仓库”）
        # warehouse_info = self.warehouse_info_get(warehouse_name)  # 可以改为参数传入不同仓库名

        # 处理 list 数据，添加 issueQuantity 和仓库信息
        updated_data_list = []
        for index, item in enumerate(data_list, start=1):
            new_item = item.copy()
            # 添加领料数量
            new_item["quantityIssued"] = item.get("unpickedQuantity")
            new_item["index"] = index
            item_spec = new_item["itemSpec"]
            item_spec_code = quote(item_spec)
            item_code = new_item["itemCode"]
            if new_item["batchManagement"]:
                new_item["batchCode"] = self.batch_code_choose(item_code,item_spec_code)
            # 添加仓库信息
            # new_item.update({
            #     "warehouseId": warehouse_info["warehouseId"],
            #     "warehouseName": warehouse_info["warehouseName"],
            #     "warehouseCode": warehouse_info["warehouseCode"]
            # })
            updated_data_list.append(new_item)

        # 构建 payload
        payload = {
            "issueCode": self.auto_production_requisition_code(),
            "issueDate": formatted_time,
            "userDeptName":data_main["userDeptName"],
            "issueType": "生产领料",
            "status": "0",
            "deptList": data_main["deptList"],
            "list": updated_data_list,  # 使用更新后的列表
        }
        print(payload)
        # 发送请求
        response = self.api.send_post_direct(relative_url, payload)
        print("新增领料单响应:", response)

        assert response["code"] == 200, f"新增领料单失败，返回：{response}"
        return response["data"]["businessId"]


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
        insid, taskid = self.production_requisition_get(business_id)


        payload = {
            "taskid": taskid,
            "insid": insid,
            "businessId": business_id,
            "comment": "",
            "operateType": "0",
            "billType": "wm_issue_header"
        }
        return  payload

    def process_instance_cancel_flow(self,payload):
        """生产管理--批量审批"""
        relative_url = "admin-api/oa/myTask/commitTask"

        # 通过 AllApi 的简洁 POST 方法直接发请求
        response  = self.api.send_post_direct(relative_url, payload)
        return response["code"]

    def batch_code_choose(self, item_code, item_spec):
        """按先进先出原则选择批次号"""
        relative_url = f"admin-api/mes/wm/wmstock/list?pageNum=1&pageSize=10&itemCode={item_code}&isSelect=true&itemSpec={item_spec}"
        response = self.api.send_get_direct(relative_url)

        if not response.get("rows"):
            raise ValueError(f"未找到物料 {item_code} 规格 {item_spec} 的库存批次，请确认是否已存在可用库存")

        batch_code = response["rows"][0]["batchCode"]
        return batch_code

# 使用示例
if __name__ == "__main__":
    # 创建实例
    production_requisition_instance = ProductionRequisition()
    business_id = production_requisition_instance.production_requisition_add("MO202507010007")
    payload = production_requisition_instance.commit_task_by_business_id(business_id)
    response_code = production_requisition_instance.process_instance_cancel_flow(payload)
    print(f"审批返回状态码：{response_code}")
