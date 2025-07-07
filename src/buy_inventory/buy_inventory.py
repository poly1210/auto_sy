from datetime import datetime

from baseApi.base_api import AllApi
from urllib.parse import quote

#采购入库
class BuyInventory:

    def __init__(self, api):
        self.api = api

    def auto_buy_inventory_code(self):
        """获取采购入库订单的自动编号"""
        relative_url ="admin-api/system/autocode/get/ITEMRECPT_CODE"
        item_recept_code = self.api.send_get_direct(relative_url)
        return item_recept_code



    def auto_batch_code(self):
        """针对需要批次管理的物料，加上批次号"""
        relative_url = "admin-api/system/autocode/get/BATCH_CODE"
        batch_code = self.api.send_get_direct(relative_url)
        return batch_code


    def userid_get(self, user_name):
        encoded = quote(user_name)
        url = f"admin-api/system/user/list?pageNum=1&pageSize=10&userName={encoded}"
        res = self.api.send_get_direct(url)
        if res["code"] == 200 and res["total"] > 0:
            return res["rows"][0]["userId"]
        raise ValueError(f"未找到经手人：{user_name}")

    def buy_inventory_payload_list_get(self, code):
        """获取采购订单负载的主体和列表部分"""
        # purchaseTemplateId = self.buy_order_payload_get()
        relative_url = f"admin-api/mes/po/purchase/select?pageNum=1&pageSize=50&purchaseCode={code}&isReturn=0"
        response = self.api.send_get_direct(relative_url)
        data = response["data"]
        return data["father"][0],data["children"]

    def warehouse_info_get(self, name):
        """根据仓库名称查询仓库信息，返回完整仓库对象"""
        name = quote(name)
        relative_url = f"admin-api/mes/wm/warehouse/list?pageNum=1&pageSize=10&warehouseName={name}"
        response = self.api.send_get_direct(relative_url)

        if not response.get("rows"):
            raise ValueError(f"未找到名为 {name} 的仓库，请确认仓库是否存在")

        warehouse_info = response["rows"][0]  # 取第一个匹配结果
        return warehouse_info



    def buy_inventory_add_by_order(self,sales_code,warehouse_name):
        """采购管理-采购入库-新增-采购订单"""
        relative_url = "admin-api/mes/wm/itemrecpt"
        data_main,data_list = self.buy_inventory_payload_list_get(sales_code)
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d")
        # 遍历data_list，为每个商品行添加入库数量
        updated_data_list = []
        recept_code = self.auto_buy_inventory_code()
        warehouse_info = self.warehouse_info_get(warehouse_name)

        for index, item in enumerate(data_list, start=1):
            new_item = item.copy()
            new_item["index"] = index
            new_item["warehouseName"] = warehouse_info["warehouseName"]
            new_item["warehouseCode"] = warehouse_info["warehouseCode"]
            new_item["warehouseId"] = warehouse_info["warehouseId"]
            new_item["quantityRecived"] = item["itemNum"]
            if new_item["batchManagement"] is True and not new_item.get("batchCode"):
                new_item["batchCode"] = self.auto_batch_code()
            updated_data_list.append(new_item)
        payload = {
            "recptCode" : recept_code,
            "recptDate":formatted_date,
            **data_main,
            # type代表不同类型的入库方式
            "type":"00",
            # 这个入库数量的英文是跟后端同步的，后端就是错的，而且不知道为什么查询的时候没带入库数量
            # 入库数量是放在list里面的
            "list": updated_data_list ,
        }
        print(payload)
        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)

        # 打印日志调试
        print("不检验订单的新增采购入库响应:", response)

        # 断言接口成功
        assert response["code"] == 200, f"不检验订单的新增采购入库失败，返回：{response}"

        # 保存 businessId
        business_id = response["data"]["businessId"]

        return business_id

    def buy_inventory_inspection_payload_list_get(self, code):
        """获取采购检验单负载的主体和列表部分"""
        # 这里传的是单据编号
        relative_url = f"admin-api/qc/inspection/select?pageNum=1&pageSize=10&inspectionCode={code}&documentType=inspection_purchase"
        response = self.api.send_get_direct(relative_url)
        data = response["rows"][0]
        return data

    def buy_inventory_add_by_inspection(self,inspection_code):
        """采购管理-采购入库-新增-采购检验单"""
        relative_url = "admin-api/mes/wm/itemrecpt"
        data_list = self.buy_inventory_inspection_payload_list_get(inspection_code)
        data_list["quantityRecived"] = data_list["inspectionQuantity"]

        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d")
        user_name = "admin"
        user_id = self.userid_get(user_name)
        payload = {
            "distinguish":0,
            "recptCode" : self.auto_buy_inventory_code(),
            "recptDate":formatted_date,
            "purchaseId":data_list["purchaseId"],
            # type代表不同类型的入库方式
            "type":"00",
            # 这里默认入库单和采购检验单的供应商是一个人
            "vendorId": data_list["vendorId"],
            "vendorName":data_list["vendorName"],
            "vendorCode":data_list["vendorCode"],
            "userId":user_id,
            "userName":user_name,
            "list": [data_list] ,
        }
        print(payload)
        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)

        # 打印日志调试
        print("检验订单的新增采购入库订单响应:", response)

        # 断言接口成功
        assert response["code"] == 200, f"检验订单的新增采购入库订单失败，返回：{response}"

        # 保存 businessId
        business_id = response["data"]["businessId"]

        return business_id

    def buy_inventory_get(self, business_id):
        """采购订单 - 查询详情，返回 insid 和 taskid"""
        relative_url = f"admin-api/mes/wm/itemrecpt/{business_id}"

        # 通过 AllApi 的简洁 GET 方法直接发请求
        response = self.api.send_get_direct(relative_url)

        # 日志 + 断言
        print("查询订单响应:", response)
        assert response["code"] == 200, f"查询订单失败，返回：{response}"

        data = response["data"]
        return data["flowInsId"], data["taskId"]

    def commit_task_by_business_id(self, business_id):
        """封装好审批的payload数据"""
        insid, taskid = self.buy_inventory_get(business_id)

        payload = {
            "taskid": taskid,
            "insid": insid,
            "businessId": business_id,
            "comment": "",
            "operateType": "0",
            "billType": "material_storage"
        }
        return payload

    def process_instance_cancel_flow(self,payload):
        """采购管理-采购入库订单明细--批量审批"""
        relative_url = "admin-api/oa/myTask/commitTask"

        # 通过 AllApi 的简洁 POST 方法直接发请求
        response = self.api.send_post_direct(relative_url, payload)
        return response["code"]


# 使用示例
if __name__ == "__main__":
    # 创建 SaleOrder 实例
    buy_inventory_instance = BuyInventory()

    # 调用 采购订单新增，查询订单，审核订单 方法
    business_id = buy_inventory_instance.buy_inventory_add_by_order("PUR2025295","总仓库")
    payload = buy_inventory_instance.commit_task_by_business_id(business_id)
    response_code = buy_inventory_instance.process_instance_cancel_flow(payload)
    print(f"审批返回状态码：{response_code}")
