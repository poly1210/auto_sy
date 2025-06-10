from baseApi.base_api import AllApi

#工序入库单新增
class ProcessInspection:
    business_id = None  # 类变量存储 businessId

    def __init__(self):
        self.api = AllApi()
        self.api.send_login("admin-api/config.yml")

    # def auto_process_inspection_code(self):
    #     """获取工序入库单的自动编号"""
    #     relative_url ="admin-api/system/autocode/get/QC_PROCESS_INSPECTION_CODE"
    #     QC_PROCESS_INSPECTION_CODE = self.api.send_get_direct(relative_url)
    #     return QC_PROCESS_INSPECTION_CODE

    def process_inspection_add(self):
        """生产管理-工序入库单单-批量新增"""
        payload = {

        }

        relative_url = "admin-api/pro/recpt/batchTransfer"
        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)

        # 打印日志调试
        print("新增检验单响应:", response)

        # 断言接口成功
        assert response["code"] == 200, f"新增订单失败，返回：{response}"
        return response




# 使用示例
if __name__ == "__main__":
    # 创建 SaleOrder 实例
    pi = ProcessInspection()

    # 调用 订单新增，查询订单，审核订单 方法
    response = pi.process_inspection_add()
    print(response)
