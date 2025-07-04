from datetime import datetime
from urllib.parse import quote

from baseApi.base_api import AllApi

#采购订单，基于erp的采购计划生成采购订单
class BuyOrderByERP:
    business_id = None  # 类变量存储 businessId

    def __init__(self):
        self.api = AllApi()
        self.api.send_login("admin-api/config.yml")



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
        """采购管理-采购订单-新增（根据采购计划）"""
        relative_url = "admin-api/mrp/resultDetails/generatedPoPurchase"

        # 如果申请人和采购员是一个人的话，那这里就不需要额外获取user_name，否则就需要覆盖
        # 供应商也是同理
        user_name = "admin"
        user_id = self.userid_get(user_name)
        vendor_name = "测试3/19供应商"

        vendor_info = self.vendor_id_get(vendor_name)
        vendor_id = vendor_info["vendorId"]
        vendor_code = vendor_info["vendorCode"]
        currency = vendor_info["currency"]

        # 获取当前时间
        now = datetime.now()
        # 格式化为 YYYY-MM-DD
        formatted_date = now.strftime("%Y-%m-%d")

        # 这一块都得后期传
        # 这个id是物料的id，“mrp/calculation/80在这里查
        details_id = 241
        tax_price = 5
        # 这里的税率是整数数字，后面用要除100
        tax_rate = 0
        this_order_num = 10
        unit_money = 5
        goods_time = "2025-06-25"

        payload = [{
            "purchaseDate" :formatted_date,
            "goodsTime" : goods_time,
            "vendorId": vendor_id,
            "vendorName": vendor_name,
            "vendorCode": vendor_code,
            "currency": currency,
            "userName": user_name,
            "userId": user_id,
            "detailsId": details_id,
            "thisOrderNum": this_order_num,
            "unitMoney": unit_money,
            "taxRate": tax_rate,
            "taxPrice" : unit_money*(1+tax_rate/100),
            "taxMoney": tax_price*this_order_num
            }]



        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)

        # 打印日志调试
        print("新增订单响应:", response)

        # 断言接口成功
        assert response["code"] == 200, f"新增订单失败，返回：{response}"

        # 保存 businessId
        msg = response["msg"]

        return msg







# 使用示例
if __name__ == "__main__":
    # 创建 SaleOrder 实例
    buy_erp = BuyOrderByERP()

    # 调用 采购订单新增，查询订单，审核订单 方法
    response = buy_erp.buy_order_add()
    print(f"审批返回状态码：{response}")
