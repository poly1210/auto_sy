from datetime import datetime

from baseApi.base_api import AllApi
from urllib.parse import quote
#产品送检单
class ProductionInspection:
    business_id = None  # 类变量存储 businessId

    def __init__(self):
        self.api = AllApi()
        self.api.send_login("admin-api/config.yml")

    def auto_production_inspection_code(self):
        """获取产品送检单订单的自动编号"""
        relative_url ="admin-api/system/autocode/get/PRODUCTINSPECTION_CODE"
        production_inspection_code = self.api.send_get_direct(relative_url)
        return production_inspection_code

    def auto_batch_code(self):
        """获取产品送检单订单的自动编号"""
        relative_url ="admin-api/system/autocode/get/BATCH_CODE"
        batch_code = self.api.send_get_direct(relative_url)
        return batch_code


    def production_inspection_payload_list_get(self, code):
        """根据到货单号获取采购检验单负载的主体部分"""
        relative_url =f"admin-api/mes/pro/workorderV1/selectByInspection?pageNum=1&pageSize=10&workorderCode={code}"
        response = self.api.send_get_direct(relative_url)
        data = response["rows"][0]
        return data

    def warehouse_info_get(self, name):
        """根据仓库名称查询仓库信息，返回完整仓库对象"""
        name = quote(name)
        relative_url = f"admin-api/mes/wm/warehouse/list?pageNum=1&pageSize=10&warehouseName={name}"
        response = self.api.send_get_direct(relative_url)

        if not response.get("rows"):
            raise ValueError(f"未找到名为 {name} 的仓库，请确认仓库是否存在")

        warehouse_info = response["rows"][0]  # 取第一个匹配结果
        return warehouse_info

    def production_inspection_add(self):
        """生产管理-产品入库-产品送检单"""
        relative_url = "admin-api/qc/product/inspection"
        # 提取数据
        data_list = self.production_inspection_payload_list_get("MO202506180005")
        data_list["batchCode"] = self.auto_batch_code()

        line_data = {
            "documentId": data_list["documentId"],
            "documentLineId": data_list["documentLineId"],
            "documentCode": data_list["documentCode"],
            "itemId": data_list["itemId"],
            "itemCode": data_list["itemCode"],
            "itemName": data_list["itemName"],
            "itemSpec": data_list["itemSpec"],
            "supplyUnit": data_list["supplyUnit"],
            "quantity": int(data_list["quantity"]),
            "warehouseId": data_list["warehouseId"],
            "warehouseCode": data_list["warehouseCode"],
            "warehouseName": data_list["warehouseName"],
            "batchCode": data_list["batchCode"],
            # 可选字段（视接口文档而定）
            "unitPrice": 0.0,
            "totalAmount": 0.0,
            "qualifiedQty": int(data_list["quantity"]),
            "unQualifiedQty": 0,
            "status": "PENDING_INSPECTION"
        }
        warehouse_info = self.warehouse_info_get("总仓库")

        payload = {
            "inspectionCode": self.auto_production_inspection_code(),
            "inspectionDate": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),  # ✅ 完整时间格式
            "deptList": [100, 101, 104],
            "lines": [line_data],
            "userDeptName": "生产办公室",
            "warehouseId": warehouse_info["warehouseId"],
            "warehouseName": "总仓库",
            "warehouseCode": warehouse_info["warehouseCode"]
        }
        print(payload)

        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)

        # 打印日志调试
        print("新增产品检验响应:", response)

        # 断言接口成功
        assert response["code"] == 200, f"产品检验失败，返回：{response}"

        # 保存 businessId
        business_id = response["data"]["businessId"]

        return business_id


    def production_inspection_get(self, business_id):
        """生产管理-产品入库-产品送检单- 查询详情，返回 insid 和 taskid"""
        relative_url = f"admin-api/qc/product/inspection/{business_id}"

        # 通过 AllApi 的简洁 GET 方法直接发请求
        response = self.api.send_get_direct(relative_url)

        # 日志 + 断言
        print("查询订单响应:", response)
        assert response["code"] == 200, f"查询订单失败，返回：{response}"

        data = response["data"]
        return data["flowInsId"], data["taskId"]


    def commit_task_by_business_id(self, business_id):
        """封装好payload数据"""
        insid, taskid = self.production_inspection_get(business_id)

        payload = {
            "taskid": taskid,
            "insid": insid,
            "businessId": business_id,
            "comment": "",
            "operateType": "0",
            "billType": "qc_product_inspection"
        }
        return payload


    def process_instance_cancel_flow(self, payload):
        "销售管理-销售订单明细--批量审批"
        relative_url = "admin-api/oa/myTask/commitTask"

        # 通过 AllApi 的简洁 POST 方法直接发请求
        response = self.api.send_post_direct(relative_url, payload)
        return response["code"]

        # 使用示例


if __name__ == "__main__":
    # 创建 类 实例
    pis = ProductionInspection()

    # 调用 检验单新增，查询检验订单，审核订单 方法
    business_id = pis.production_inspection_add()
    payload = pis.commit_task_by_business_id(business_id)
    response_code = pis.process_instance_cancel_flow(payload)
    print(f"审批返回状态码：{response_code}")