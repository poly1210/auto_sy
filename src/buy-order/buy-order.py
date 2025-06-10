from baseApi.base_api import AllApi

#采购订单生成
class BuyOrder:
    business_id = None  # 类变量存储 businessId

    def __init__(self):
        self.api = AllApi()
        self.api.send_login("admin-api/config.yml")

    def auto_buy_code(self):
        """获取采购订单的自动编号"""
        relative_url ="admin-api/system/autocode/get/PURCHASE_CODE"
        purchase_code = self.api.send_get_direct(relative_url)
        return purchase_code

    def buy_order_add(self):
        """采购管理-采购订单-新增"""
        relative_url = "admin-api/mes/po/purchase"
        payload = {
            "purchaseCode": self.auto_buy_code(),
            "purchaseName": None,
            "vendorName": "嘿嘿嘿1",
            "vendorCode": "V00139",
            "currency": "美元",
            "deliveryDate": None,
            "isApprove": "order",
            "isIncludeTax": "Y",
            "list": [
                {
                    "searchValue": None,
                    "createBy": None,
                    "createTime": None,
                    "updateBy": None,
                    "updateTime": None,
                    "remark": None,
                    "areaCode": None,
                    "areaId": None,
                    "areaName": None,
                    "batchManagement": False,
                    "batchManagementZh": None,
                    "clientItemCode": "FEFREDFREWR45435",
                    "drawCode": None,
                    "flowInsId": None,
                    "flowKey": None,
                    "index": 1,
                    "inventoryCoefficient": 1,
                    "inventoryUnit": "个",
                    "isEnable": True,
                    "isEnableZh": None,
                    "isExemptInspection": None,
                    "isSafeStock": False,
                    "isSafeStockZh": None,
                    "isUse": None,
                    "isUseZh": None,
                    "itemCode": "JYXM202506040001",
                    "itemId": 3943,
                    "itemName": "佛挡杀佛是否",
                    "itemNum": 1,
                    "itemOrProduct": None,
                    "itemSpec": "csck",
                    "itemTypeCode": "ITEM_TYPE_0149",
                    "itemTypeId": 318,
                    "itemTypeName": "成品",
                    "locationCode": None,
                    "locationId": None,
                    "locationName": None,
                    "packageName": "fsdfsdfsdf",
                    "params": {},
                    "procureCoefficient": 1,
                    #"procureQuantityOnhand": 5305,
                    "procureUnit": "个",
                    "productionTemplateId": None,
                    "productionTemplateName": None,
                    "purchaseTemplateId": None,
                    "purchaseTemplateName": None,
                    #"quantityOnhand": 5305,
                    "saleCoefficient": 1,
                    #"saleQuantityOnhand": 5305,
                    "saleUnit": "个",
                    "salesTemplateId": None,
                    "salesTemplateName": None,
                    "specification": "csck",
                    "status": "0",
                    "statusZh": None,
                    "supplyCoefficient": 1,
                    #"supplyQuantityOnhand": 5305,
                    "supplyUnit": "个",
                    "taxMoney": 1,
                    "taxPrice": 1,
                    "taxRate": 0,
                    "totalMoney": 1,
                    "unitMoney": 1,
                    "unitOfMeasure": "个",
                    "unreceivedGoods": 1,
                    "url": None,
                    "version": None,
                    "warehouseCode": "WH243",
                    "warehouseId": 353,
                    "warehouseInfo": [353],
                    "warehouseName": "成品仓库",
                    "warehouseNameZh": "成品仓库"
                }
                # 如果有多个 list 元素，继续在这里添加字典即可
            ],
            "preAmount": 0,
            "purchaseData": "2025-06-09 09:26:19",
            "remark": None,
            "status": "0",
            "taxRate": 2,
            "totalMoney": None,
            "userId": 1,
            "userName": "admin",
            "vendorId": 269
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

    def buy_order_get(self, business_id):
        """采购订单 - 查询详情，返回 insid 和 taskid"""
        relative_url = f"admin-api/mes/po/purchase/{business_id}"

        # 通过 AllApi 的简洁 GET 方法直接发请求
        response = self.api.send_get_direct(relative_url)

        # 日志 + 断言
        print("查询订单响应:", response)
        assert response["code"] == 200, f"查询订单失败，返回：{response}"

        data = response["data"]
        return data["flowInsId"], data["taskId"]

    def commit_task_by_business_id(self, business_id):
        """封装好审批的payload数据"""
        insid, taskid = self.buy_order_get(business_id)

        payload = {
            "taskid": taskid,
            "insid": insid,
            "businessId": business_id,
            "comment": "",
            "operateType": "0",
            "billType": "purchase"
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
    buy_order_instance = BuyOrder()

    # 调用 采购订单新增，查询订单，审核订单 方法
    business_id = buy_order_instance.buy_order_add()
    payload = buy_order_instance.commit_task_by_business_id(business_id)
    response_code = buy_order_instance.processInstance_cancleFlow(business_id, payload)
    print(f"审批返回状态码：{response_code}")
