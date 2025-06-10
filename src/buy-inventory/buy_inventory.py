from baseApi.base_api import AllApi


class BuyInventory:
    business_id = None  # 类变量存储 businessId

    def __init__(self):
        self.api = AllApi()
        self.api.send_login("admin-api/config.yml")



    def buy_inventory_add(self):
        """采购管理-采购入库-新增"""
        relative_url = "admin-api/mes/wm/itemrecpt"
        payload = {
            "currency": "美元",
            "distinguish": "0",
            "iqcCode": None,
            "isIncludeTax": "Y",
            "list": [
                {
                    "areaCode": None,
                    "areaId": None,
                    "areaName": None,
                    "batchManagement": False,
                    "goodsTime": None,
                    "index": 1,
                    "inventoryCoefficient": 1,
                    "inventoryUnit": "个",
                    "itemCode": "JYXM202506040001",
                    "itemId": 3943,
                    "itemName": "佛挡杀佛是否",
                    "itemNum": 1,
                    "itemSpec": None,
                    "locationCode": None,
                    "locationId": None,
                    "locationName": None,
                    "procureCoefficient": 1,
                    "procureQuantityOnhand": 5305,
                    "procureUnit": "个",
                    "purchaseId": 438,
                    "purchaseLineId": 696,
                    "quantityOnhand": 5305,
                    "quantityRecived": 1,
                    "receivedGoods": 0,
                    "specification": "csck",
                    "taxRate": 0,
                    "totalMoney": 1,
                    "unitMoney": 1,
                    "unitOfMeasure": "个",
                    "unreceivedGoods": 1,
                    "warehouseCode": "WH243",
                    "warehouseId": 353,
                    "warehouseInfo": [353],
                    "warehouseName": "成品仓库",
                    "warehouseNameZh": "成品仓库"
                }
            ],
            "poCode": None,
            "purchaseId": 438,
            #单据编号也要自动获取
            "recptCode": "R20250609003",
            "recptDate": "2025-06-09 14:29:27",
            "recptId": None,
            "recptName": None,
            "remark": None,
            "status": None,
            "taxRate": 2,
            "type": "00",
            "userId": 2,
            "userName": "cg",
            "vendorCode": "V00139",
            "vendorId": 269,  # 注意：若后端要求数字类型，需移除引号（原数据中为字符串"269"）
            "vendorName": "嘿嘿嘿1",
            "warehouseInfo": []  # 注意：此处与list内的warehouseInfo字段重复，需根据业务保留其一
        }
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
