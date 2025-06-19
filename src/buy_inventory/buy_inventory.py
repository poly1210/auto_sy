
from baseApi.base_api import AllApi
from urllib.parse import quote

#采购入库
class BuyInventory:


    def __init__(self):
        self.api = AllApi()
        self.api.send_login("admin-api/config.yml")

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



    def buy_inventory_add_by_order(self):
        """采购管理-采购入库-新增-采购订单"""
        relative_url = "admin-api/mes/wm/itemrecpt"
        data_main,data_list = self.buy_inventory_payload_list_get("PUR2025236")
        # 遍历data_list，为每个商品行添加入库数量
        updated_data_list = []
        for index, item in enumerate(data_list, start=1):
            new_item = item.copy()
            new_item["index"] = index
            if new_item["batchManagement"] == "true":
                new_item["batchCode"] = self.auto_batch_code()
            updated_data_list.append(new_item)
        payload = {
            "recptCode" : self.auto_buy_inventory_code(),
            "recptDate":"2025-06-19 14:19:32",
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
        print("新增订单响应:", response)

        # 断言接口成功
        assert response["code"] == 200, f"新增订单失败，返回：{response}"

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

    def buy_inventory_add_by_inspection(self):
        """采购管理-采购入库-新增-采购检验单"""
        relative_url = "admin-api/mes/wm/itemrecpt"
        data_list = self.buy_inventory_inspection_payload_list_get("QCPI202505220001")
        data_list["quantityRecived"] = data_list["inspectionQuantity"]
        # vendor_info = self.vendor_id_get("wll测试供应商")
        # vendor_id = vendor_info["vendorId"]
        # vendor_code = vendor_info["vendorCode"]
        # currency = vendor_info["currency"]
        user_name = "admin"
        user_id = self.userid_get(user_name)
        payload = {
            "distinguish":0,
            "recptCode" : self.auto_buy_inventory_code(),
            "recptDate":"2025-06-16 14:19:32",
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
        print("新增订单响应:", response)

        # 断言接口成功
        assert response["code"] == 200, f"新增订单失败，返回：{response}"

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
    business_id = buy_inventory_instance.buy_inventory_add_by_order()
    payload = buy_inventory_instance.commit_task_by_business_id(business_id)
    response_code = buy_inventory_instance.process_instance_cancel_flow(payload)
    print(f"审批返回状态码：{response_code}")
