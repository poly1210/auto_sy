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

    def sale_order_add(self):
        """销售管理-销售订单-新增"""
        payload = {
            "salesCode": self.auto_sale_code(),
             "clientCode": "C00531",
             "clientId": 1028,
            "clientName": "wll测试",
            #选择客户后会带入币种 "currency": "GBP",
            "list": [
                {
                    # "index": 1,
                    "inventoryCoefficient": 1,
                    "inventoryUnit": "G",
                    # "isEnable": True,
                    # "isEnableZh": None,
                    "itemCode": "IF20250528001",
                    "itemId": 3870,
                    "itemName": "桌子",
                    "itemNum": 6000,
                    # "itemTypeCode": "ITEM_TYPE_0149",
                    # "itemTypeId": 318,
                    # "itemTypeName": "成品",
                    # "procureCoefficient": 1,
                    # "procureQuantityOnhand": 962,
                    # "procureUnit": "G",
                    # "quantityOnhand": 962,
                    # "saleCoefficient": 1,
                    # "saleQuantityOnhand": 962,
                    # "saleUnit": "G",
                    # "specification": "zz",
                    # "status": "0",
                    # "statusZh": None,
                    # "supplyCoefficient": 1,
                    # "supplyQuantityOnhand": 962,
                    "supplyUnit": "G",
                    "taxMoney": 200,
                    "taxPrice": 2,
                    "taxRate": 0,
                    "totalMoney": 200,
                    "unitMoney": 2,
                    "unitOfMeasure": "G",
                    # "unreceivedGoods": 100,
                }
            ],
            "salesData": "2025-06-11 10:21:26",
            # "taxRate": None,
            "userId": 1,
            "userName": "admin"
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
    business_id = sale_order_instance.sale_order_add()
    payload = sale_order_instance.commit_task_by_business_id(business_id)
    response_code = sale_order_instance.processInstance_cancleFlow(business_id, payload)
    print(f"审批返回状态码：{response_code}")
