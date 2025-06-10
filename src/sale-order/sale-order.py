from baseApi.base_api import AllApi

#销售订单新增
class SaleOrder:
    business_id = None  # 类变量存储 businessId

    def __init__(self):
        self.api = AllApi()
        self.api.send_login("admin-api/config.yml")

    def auto_sale_code(self):
        """获取销售订单的自动编号"""
        relative_url ="admin-api/system/autocode/get/SALES_CODE"
        purchase_code = self.api.send_get_direct(relative_url)
        return purchase_code

    def saleorder_add(self):
        """销售管理-销售订单-新增"""
        payload = {
            "clientCode": "C00524",
            "clientId": 1021,
            "clientName": "测试",
            "currency": "美元",
            "delivery": None,
            "salesCode": self.auto_sale_code(),
            "salesData": "2025-06-06 14:09:47",
            "salesId": None,
            "salesName": None,
            "userId": 1,
            "userName": "admin",
            "list": [
                {
                    "searchValue": None,
                    "createBy": None,
                    "createTime": None,
                    "remark": None,
                    "areaCode": None,
                    "areaId": None,
                    "areaName": None,
                    "batchManagement": True,
                    "batchManagementZh": None,
                    "clientItemCode": "是是是123低点",
                    "drawCode": None,
                    "flowInsId": None,
                    "flowKey": None,
                    "index": 1,
                    "inventoryCoefficient": 1,
                    "inventoryUnit": "G",
                    "isEnable": True,
                    "isEnableZh": None,
                    "isExemptInspection": None,
                    "isSafeStock": True,
                    "isSafeStockZh": None,
                    "isUse": None,
                    "isUseZh": None,
                    "itemCode": "JYXM202505280001",
                    "itemId": 3879,
                    "itemName": "物料/产品名称70",
                    "itemNum": 2,
                    "itemOrProduct": None,
                    "itemTypeCode": "ITEM_TYPE_0149",
                    "itemTypeId": 318,
                    "itemTypeName": "成品",
                    "locationCode": None,
                    "locationId": None,
                    "locationName": None,
                    "packageName": "包装方式123",
                    "params": {},  # 空字典
                    "procureCoefficient": 1,
                    "procureQuantityOnhand": 80,
                    "procureUnit": "G",
                    "productionTemplateId": None,
                    "productionTemplateName": None,
                    "purchaseTemplateId": None,
                    "purchaseTemplateName": None,
                    "quantityOnhand": 80,
                    "saleCoefficient": 1,
                    "saleQuantityOnhand": 80,
                    "saleUnit": "G",
                    "salesTemplateId": None,
                    "salesTemplateName": None,
                    "specification": "规格型号123",
                    "status": "0",
                    "statusZh": None,
                    "supplyCoefficient": 1,
                    "supplyQuantityOnhand": 80,
                    "supplyUnit": "G",
                    "taxMoney": 4,
                    "taxPrice": 2,
                    "taxRate": 0,
                    "totalMoney": 4,
                    "unitMoney": 2,
                    "unitOfMeasure": "G",
                    "unreceivedGoods": 2,
                    "updateBy": None,
                    "updateTime": None,
                    "url": None,
                    "version": None,
                    "warehouseCode": "WH253",
                    "warehouseId": 369,
                    "warehouseInfo": [369],  # 数组
                    "warehouseName": "总仓库",
                    "warehouseNameZh": "总仓库"
                }
            ]
        }
        relative_url = "admin-api/mes/sm/sales"
        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)

        # 打印日志调试
        print("新增订单响应:", response)

        # 断言接口成功
        assert response["code"] == 200, f"新增订单失败，返回：{response}"

        # 保存 businessId
        business_id = response["data"]["businessId"]

        return business_id


    def saleorder_get(self, business_id):
        """销售订单 - 查询详情，返回 insid 和 taskid"""
        relative_url = f"admin-api/mes/sm/sales/{business_id}"

        # 通过 AllApi 的简洁 GET 方法直接发请求
        response = self.api.send_get_direct(relative_url)

        # 日志 + 断言
        print("查询订单响应:", response)
        assert response["code"] == 200, f"查询订单失败，返回：{response}"

        data = response["data"]
        return data["flowInsId"], data["taskId"]

    def commit_task_by_business_id(self, business_id):
        """封装好payload数据"""
        insid, taskid = self.saleorder_get(business_id)


        payload = {
            "taskid": taskid,
            "insid": insid,
            "businessId": business_id,
            "comment": "",
            "operateType": "0",
            "billType": "sm_sales"
        }
        return  payload

    def processInstance_cancleFlow(self, business_id, payload):
        "销售管理-销售订单明细--批量审批"
        relative_url = "admin-api/oa/myTask/commitTask"

        # 通过 AllApi 的简洁 POST 方法直接发请求
        response  = self.api.send_post_direct(relative_url, payload)
        return response["code"]

# 使用示例
if __name__ == "__main__":
    # 创建 SaleOrder 实例
    sale_order_instance = SaleOrder()

    # 调用 订单新增，查询订单，审核订单 方法
    business_id = sale_order_instance.saleorder_add()
    payload = sale_order_instance.commit_task_by_business_id(business_id)
    response_code = sale_order_instance.processInstance_cancleFlow(business_id, payload)
    print(f"审批返回状态码：{response_code}")
