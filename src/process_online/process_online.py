from baseApi.base_api import AllApi

#工序上线
class ProcessOnline:
    def __init__(self, api):
        self.api = api


    def process_online_payload_get(self, code):
        """根据订单编号，获取负载"""
        # purchaseTemplateId = self.buy_order_payload_get()
        relative_url = f"admin-api/pro/online/list?pageNum=1&pageSize=10&workorderCode={code}"
        response = self.api.send_get_direct(relative_url)
        data = response["rows"][0]
        return data["id"], data["onlineQuantity"]


    def process_online(self,production_code):
        """工序上线"""
        relative_url = "admin-api/pro/online/batch"
        payload_id,online_quantity=self.process_online_payload_get(production_code)
        payload = [{
            "id":payload_id,
            "onlineQuantity" : online_quantity ,
        }]
        print(payload)
        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)

        # 打印日志调试
        print("工序上线响应:", response)

        # 断言接口成功
        assert response["code"] == 200, f"工序上线失败，返回：{response}"
        return response["code"]





# 使用示例
if __name__ == "__main__":
    # 创建 SaleOrder 实例
    pol = ProcessOnline()
    # 调用 采购订单新增，查询订单，审核订单 方法
    code = pol.process_online()
    print(f"审批返回状态码：{code}")
