import json
from datetime import datetime
from typing import TypedDict
from baseApi.base_api import AllApi


#MRP运算列表
class MRPCalculation:
    def __init__(self, api):
        self.api = api

    def auto_mrp_code(self):
        """获取MRP运算列表的自动编号"""
        relative_url ="admin-api/system/autocode/get/MRP_CALCULATION_CODE"
        purchase_code = self.api.send_get_direct(relative_url)
        return purchase_code

    #  这里的sales_code对应后端中的salesCode
    def mrp_list_info_get(self, sales_code):
        """根据销售订单号查询详情获取erp运算时的list表"""
        #  &isCalculation=true是必带的，因为这样才能查出children
        relative_url = f"admin-api/mes/sm/sales/select?pageNum=1&pageSize=50&salesCode={sales_code}&isCalculation=true"

        # 通过 AllApi 的简洁 GET 方法直接发请求
        response = self.api.send_get_direct(relative_url)
        if response.get("code") == 200:
            data = response.get("data", {})
            if data.get("childrenSize", 0) > 0:
                return data["children"][0]
            else:
                raise ValueError(f"未找到销售订单编码为{sales_code} 的信息")
        else:
            raise ValueError(f"请求失败：{response.get('msg', '未知错误')}")



    #调用post方法进行请求
    #schemeId是运算方案，requirementsAnalysis是运算模式（就两个，（1.物料需求分析 2.批次需求计划））
    def mrp_calculation(self,sales_code: str,  scheme_id: int, scheme_name: str):

        #这里是查询到的list
        sales_item = self.mrp_list_info_get(sales_code)
        # 加上 operationQuantity 和 quantity 字段
        executable_num = sales_item.get("executableNum", 0)
        sales_item["operationQuantity"] = executable_num
        sales_item["quantity"] = executable_num
        #sales_item["index"] = 1
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d")
        payload = {
            "calculationCode": self.auto_mrp_code(),
            # 这里的单据日期直接选择和销售订单的销售日期相同
            "calculationDate": formatted_date,
            "list": [sales_item],
            # 这三个需要前端传入
            "requirementsAnalysis": 1,
            "schemeId": scheme_id,
            "schemeName": scheme_name
        }
        print("请求体：", json.dumps(payload, ensure_ascii=False, indent=2))

        relative_url = "admin-api/mrp/calculation/execute"
        # 发送 POST 请求（JSON 格式）
        response = self.api.send_post_direct(relative_url, payload)
        # 判断接口是否调用成功
        assert response["code"] == 200, f"MRP计算接口调用失败: {response}"

        data = response.get("data", {})
        error_list = data.get("error", [])

        # 判断是否响应为200，但是有业务错误
        assert not error_list, f"MRP计算发现业务错误: {error_list}"
        key = response["data"]["key"]
        return key

    # 根据传入的key生成生产计划和采购计划
    def production_and_buy_plan(self, key):
        # 将 key 放入表单数据中
        data = {"key": key}
        relative_url = "admin-api/mrp/calculation"
        response = self.api.send_post_format_direct(relative_url, data)
        return response



# 使用示例
if __name__ == "__main__":
    # 创建 SaleOrder 实例
    MRPcal = MRPCalculation()
    # 调用方法请求
    key = MRPcal.mrp_calculation("SAL2025237",30,"测试方案")
    print(key)
    #生成生产计划和采购计划
    code = MRPcal.production_and_buy_plan(key)["code"]
    print(code)

