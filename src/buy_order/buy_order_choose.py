from datetime import datetime
from urllib.parse import quote

from baseApi.base_api import AllApi

#采购订单，通过选单的方式生成，
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

    def buy_order_apply_info(self ,code):
        relative_url =f"admin-api/po/purchase/approve/select?pageNum=1&pageSize=50&purchaseCode={code}"
        apply_info = self.api.send_get_direct(relative_url)
        data_main = apply_info["data"]["father"][0]
        data_list = apply_info["data"]["children"]
        return data_main, data_list


    def vendor_id_get(self,vendor_name):
        # 根据姓名，查询供应商
        encoded_vendor_name = quote(vendor_name)
        relative_url = f"admin-api/mes/md/vendor/list?pageNum=1&pageSize=10&vendorName={encoded_vendor_name}"

        response = self.api.send_get_direct(relative_url)

        return response["rows"][0]

    def userid_get(self, user_name):
        encoded = quote(user_name)
        url = f"admin-api/system/user/list?pageNum=1&pageSize=10&userName={encoded}"
        res = self.api.send_get_direct(url)
        if res["code"] == 200 and res["total"] > 0:
            return res["rows"][0]["userId"]
        raise ValueError(f"未找到采购员：{user_name}")

    def buy_order_add(self):
        """采购管理-采购订单-新增"""
        relative_url = "admin-api/mes/po/purchase"
        data_main ,data_list = self.buy_order_apply_info("PUA2025027")
        # 如果申请人和采购员是一个人的话，那这里就不需要额外获取user_name，否则就需要覆盖
        # 供应商也是同理
        user_name = "admin"
        vendor_name = "测试3/19供应商"
        delivery_date = "2025-06-28"
        vendor_info = self.vendor_id_get(vendor_name)
        vendor_id = vendor_info["vendorId"]
        vendor_code = vendor_info["vendorCode"]
        currency = vendor_info["currency"]
        user_id = self.userid_get(user_name)
        # 获取当前时间
        now = datetime.now()
        # 格式化为 YYYY-MM-DD
        formatted_date = now.strftime("%Y-%m-%d")


        updated_data_list = []
        for index, item in enumerate(data_list, start=1):
            new_item = item.copy()

            new_item["goodsTime"] = delivery_date
            # 这里采购申请单的采购数量是总数量，但实际新增订单的时候是改成了可执行数量
            new_item["itemNum"] = item["executableNum"]

            updated_data_list.append(new_item)


        payload = {
            **data_main,
            "purchaseCode": self.auto_buy_code(),
            "purchaseData" :formatted_date,
            "deliveryDate" : delivery_date,
            "vendorId": vendor_id,
            "vendorName": vendor_name,
            "vendorCode": vendor_code,
            "currency": currency,
            "userName": user_name,
            "userId": user_id,
            "list": updated_data_list,
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
