from baseApi.base_api import AllApi

#MRP运算列表
class MRPCaculation:
    def __init__(self):
        self.api = AllApi()
        self.api.send_login("admin-api/config.yml")

    def auto_mrp_code(self):
        """获取MRP运算列表的自动编号"""
        relative_url ="admin-api/system/autocode/get/MRP_CALCULATION_CODE"
        purchase_code = self.api.send_get_direct(relative_url)
        return purchase_code
    #封装数据
    # def build_payload_erp(self):
    #     """封装好payload数据"""
    #     return payload

    #调用post方法进行请求
    def mrp_caculation(self):
        payload = {
            "calculationCode": "MRP202506110010",
            "calculationDate": "2025-06-11",
            "requirementsAnalysis": 1,
            "list": [
                {
                    "salesLineId": 1256,
                    "salesId": 1113,
                    "itemId": 3861,
                    "itemCode": "IF20250526001",
                    "itemName": "mrp-可乐",
                    "batchManagement": False,
                    "bomCode": "BOM000890",
                    "bomId": 891,
                    "calculatedQuantity": 0,
                    "clientItemCode": "123456",
                    "executeNum": 0,
                    "goodsTime": "2025-06-30 00:00:00",
                    "index": 1,
                    "inventoryCoefficient": 1,
                    "itemNum": 120,
                    "itemNumber": None,
                    "itemSpec": "kl",
                    "matnr": None,
                    "operationQuantity": 120,
                    "packageName": None,
                    "quantity": 120,
                    "quantityOnhand": 100,
                    "receivedGoods": 0,
                    "saleCoefficient": 1,
                    "saleQuantityOnhand": 100,
                    "saleUnit": "G",
                    "sourceOrderCode": "SAL2025199",
                    "sourceOrderDate": "2025-06-30 00:00:00",
                    "sourceOrderId": 1113,
                    "sourceOrderLineId": 1256,
                    "sourceOrderType": 1,
                    "sourceOrderTypeZh": "销售订单",
                    "specification": "kl",
                    "supplyCoefficient": 1,
                    "supplyQuantityOnhand": 100,
                    "taxMoney": None,
                    "taxPrice": 10,
                    "taxRate": 0,
                    "totalMoney": 1200,
                    "unitMoney": 10,
                    "unitOfMeasure": "G",
                    "unreceivedGoods": 120
                }
            ],
            "schemeId": 30,
            "schemeName": "测试方案"
        }
        relative_url = "admin-api/mes/sm/sales"
        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)
        key = response["data"]["key"]
        return key
