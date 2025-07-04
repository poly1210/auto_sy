from urllib.parse import quote

from baseApi.base_api import AllApi

#采购订单，通过添加物料方式生成
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



    def vendor_info_get(self,vendor_name):
        # 根据姓名，查询供应商(可以把这个查询的方法卸载baseapi里面复用)
        encoded_vendor_name = quote(vendor_name)
        relative_url = f"admin-api/mes/md/vendor/list?pageNum=1&pageSize=10&vendorName={encoded_vendor_name}"

        response = self.api.send_get_direct(relative_url)

        return response["rows"][0]

    def buy_order_add(self):
        """采购管理-采购订单-新增"""
        relative_url = "admin-api/mes/po/purchase"
        # 这里的采购数量，单价，税率和日期都要后期再填，可以采用查询客户，在查询采购物料信息来填负载，但如果添加多个物料的话，有点麻烦
        payload = {
            "purchaseCode": self.auto_buy_code(),
            "vendorName": "嘿嘿嘿1",
            "vendorCode": "V00139",
            #"currency": "美元",
            #"isApprove": "order",
            #"isIncludeTax": "Y",
            "list": [
                {
                    # "batchManagement": False,
                    "clientItemCode": "FEFREDFREWR45435",
                    "itemCode": "JYXM202506040001",
                    "itemId": 3943,
                    "itemName": "佛挡杀佛是否",
                    "itemNum": 1,
                    "taxMoney": 1,
                    "taxPrice": 1,
                    "taxRate": 0,
                    "totalMoney": 1,
                    "unitMoney": 1,
                    "unitOfMeasure": "个",
                    "procureCoefficient": 1,
                    "procureUnit": "个",
                    # "unreceivedGoods": 1,
                    # "index": 1,
                    # "inventoryCoefficient": 1,
                    # "inventoryUnit": "个",
                    # "isEnable": True,
                    # "isSafeStock": False,
                    # "itemSpec": "csck",
                    # "itemTypeCode": "ITEM_TYPE_0149",
                    # "itemTypeId": 318,
                    # "itemTypeName": "成品",
                    # "packageName": "fsdfsdfsdf",
                    # "params": {},
                    # "saleCoefficient": 1,
                    # "saleUnit": "个",
                    # "specification": "csck",
                    # "status": "0",
                    # "supplyCoefficient": 1,
                    # "supplyUnit": "个",
                    # "warehouseCode": "WH243",
                    # "warehouseId": 353,
                    # "warehouseInfo": [353],
                    # "warehouseName": "成品仓库",
                    # "warehouseNameZh": "成品仓库"
                }
            ],
            # "preAmount": 0,
            "purchaseDate": "2025-06-09 09:26:19",
            # "status": "0",
            # "taxRate": 2,
            # "userId": 1,
            # "userName": "admin",
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

    def process_instance_cancel_flow(self, business_id, payload):
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
    response_code = buy_order_instance.process_instance_cancel_flow(business_id, payload)
    print(f"审批返回状态码：{response_code}")
