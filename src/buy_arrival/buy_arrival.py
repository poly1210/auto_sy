from datetime import datetime
from urllib.parse import quote
from baseApi.base_api import AllApi

#采购到货单生成
class BuyArrival:

    def __init__(self, api):
        self.api = api

    def auto_buy_arrival_code(self):
        """获取到货订单的自动编号"""
        relative_url ="admin-api/system/autocode/get/DH_RECEIPTS_CODE"
        dh_receipts_code = self.api.send_get_direct(relative_url)
        return dh_receipts_code

    def auto_buy_arrival_batch_code(self):
        """获取批次号"""
        relative_url ="admin-api/system/autocode/get/BATCH_CODE"
        dh_batch_code = self.api.send_get_direct(relative_url)
        return dh_batch_code

    def warehouse_info_get(self, name):
        """根据仓库名称查询仓库信息，返回完整仓库对象"""
        name = quote(name)
        relative_url = f"admin-api/mes/wm/warehouse/list?pageNum=1&pageSize=10&warehouseName={name}"
        response = self.api.send_get_direct(relative_url)

        if not response.get("rows"):
            raise ValueError(f"未找到名为 {name} 的仓库，请确认仓库是否存在")

        warehouse_info = response["rows"][0]  # 取第一个匹配结果
        return warehouse_info

    def buy_order_arrival_payload_list_get(self, purchase_code):
        """采购单号获取到货单的列表部分"""
        relative_url =f"admin-api/mes/po/purchase/selectArrival?pageNum=1&pageSize=10&purchaseCode={purchase_code}"
        response = self.api.send_get_direct(relative_url)
        data = response["rows"]
        return data

    def buy_arrival_add(self, purchase_code,warehouse_name):
        """采购管理-采购到货单-新增"""
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d")
        relative_url = "admin-api/mes/wm/receipts"
        list_data = self.buy_order_arrival_payload_list_get(purchase_code)
        # TODO 仓库要写成能配置
        warehouse_info = self.warehouse_info_get(warehouse_name)
        receipts_code = self.auto_buy_arrival_code()

        for index,item in enumerate(list_data,start=1):
            item["warehouseName"] = warehouse_info["warehouseName"]
            item["warehouseCode"] = warehouse_info["warehouseCode"]
            item["warehouseId"] = warehouse_info["warehouseId"]
            # TODO: 这里如果是一个订单下，多个物料，不同仓库，就要变
            item["warehouseInfo"] = [warehouse_info["warehouseId"]]
            item["receivedQuantity"] = item["notReceivedGoods"]
            item["index"] = index
            # 修改documentNumber值
            item["documentNumber"] = index
            # item["warehouseNameZh"] = warehouse_info["warehouseNameZh"]
            if item.get("batchManagement", False):
                item["batchCode"] = self.auto_buy_arrival_batch_code()


        payload = {
            "receiptsCode": receipts_code,
            "receiptsDate":  formatted_date,
            "createBy" : "admin",
            "userId" : 1,
            "userDeptId" : 103,
            "userDeptName" : "工程部",
            "vendorCode" : list_data[0]["vendorCode"],
            "vendorId" : list_data[0]["vendorId"],
            "vendorName" :list_data[0]["vendorName"],
            "distinguish" : 0,
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
        return business_id,receipts_code

    def buy_inspection_get(self, business_id):
        """查询详情，返回 insid 和 taskid"""
        relative_url = f"admin-api/mes/wm/receipts/{business_id}"

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
            "billType": "wm_item_receipts"
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
    ba = BuyArrival()

    # 调用 检验订单新增，查询订单，审核订单 方法
    business_id, _ = ba.buy_arrival_add("PUR2025134")
    payload = ba.commit_task_by_business_id(business_id)
    response_code = ba.process_instance_cancel_flow(payload)
    print(f"审批返回状态码：{response_code}")
