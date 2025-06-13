# #这个模块合并到MRP计算的后面，直接自动生成生产计划和采购计划
#
# from baseApi.base_api import AllApi
# from src.mrp.mrp_calculate import MRPCalculation
#
# #MRP后的生产计划
# class production_plan():
#     def __init__(self):
#         self.api = AllApi()
#         self.api.send_login("admin-api/config.yml")
#     # def build_key_production(self):
#     #     key=""
#     #     return key
#
#     # 根据传入的key生成生产计划
#     def production_and_buy_plan(self, key):
#         # key = self.build_key_production()
#         relative_url = "admin-api/mrp/calculation"
#         response = self.api.send_post_direct(relative_url, key)
#         # order_num = response["data"]["ordernum"]
#         # calculation_id = response["data"]["calculationId"]
#         # code = response["data"]["code"]
#         return response
#
# if __name__ == "__main__":
#     #创建MRP运算的实例，调用方法，获得key值
#     mrp_calculator = MRPCalculation()
#     key = mrp_calculator.mrp_calculation()
#     print("MRP Calculation Key:", key)
#     pdp = production_plan()
#     code = pdp.production_and_buy_plan(key)["code"]
#     print(code)
