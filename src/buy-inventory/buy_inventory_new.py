from baseApi.base_api import AllApi

#采购入库
class BuyInventory:
    business_id = None  # 类变量存储 businessId

    def __init__(self):
        self.api = AllApi()
        self.api.send_login("admin-api/config.yml")

    def auto_buy_inventory_code(self):
        """获取采购入库订单的自动编号"""
        relative_url ="admin-api/system/autocode/get/ITEMRECPT_CODE"
        item_recept_code = self.api.send_get_direct(relative_url)
        return item_recept_code

    def buy_inventory_payload_list_get(self, code):
        """获取采购检验单负载的主体和列表部分"""
        # purchaseTemplateId = self.buy_order_payload_get()
        relative_url = f"admin-api/mes/po/purchase/select?pageNum=1&pageSize=50&purchaseCode={code}&isReturn=0"
        response = self.api.send_get_direct(relative_url)
        data = response["data"]
        return data["father"][0],data["children"]


    def buy_inventory_add(self):
        """采购管理-采购入库-新增"""
        relative_url = "admin-api/mes/wm/itemrecpt"
        data_main,data_list = self.buy_inventory_payload_list_get("PUR2025236")
        # 遍历data_list，为每个商品行添加入库数量
        updated_data_list = []
        for item in data_list:
            # 复制原商品行数据，避免修改原始对象
            new_item = item.copy()
            # 添加入库数量（注意参数名可能需要根据后端调整）
            new_item["quantityRecived"] = 1
            updated_data_list.append(new_item)
        payload = {
            "recptCode" : self.auto_buy_inventory_code(),
            "recptDate":"2025-06-16 14:19:32",
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

    def processInstance_cancleFlow(self, business_id, payload):
        "采购管理-采购订单明细--批量审批"
        relative_url = "admin-api/oa/myTask/commitTask"

        # 通过 AllApi 的简洁 POST 方法直接发请求
        response = self.api.send_post_direct(relative_url, payload)
        return response["code"]


# 使用示例
if __name__ == "__main__":
    # 创建 SaleOrder 实例
    buy_inventory_instance = BuyInventory()

    # 调用 采购订单新增，查询订单，审核订单 方法
    business_id = buy_inventory_instance.buy_inventory_add()
    payload = buy_inventory_instance.commit_task_by_business_id(business_id)
    response_code = buy_inventory_instance.processInstance_cancleFlow(business_id, payload)
    print(f"审批返回状态码：{response_code}")
