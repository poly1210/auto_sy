import sys
import os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)
# 导入从表格读取销售订单数据方法
from src.read_xlsx.read_sales_xlsx import ReadSalesXlsx
# 导入销售订单新增方法
from src.sale_order.sale_order import SaleOrder
# 导入MRP计算
from src.mrp.mrp_calculate import MRPCalculation
# 从表格读取采购订单数据
from src.buy_order.buy_order_new import BuyOrderNew
from src.read_xlsx.read_buy_xlsx import ReadBuyXlsx
# 导入采购到货
from src.buy_arrival.buy_arrival import BuyArrival
# 导入采购检验
from src.buy_inspection.buy_inspection import BuyInspection

class Configuration:
    def run_one(self):
        # 获取销售订单负载
        reader_sales = ReadSalesXlsx()
        payloads = reader_sales.read_sales_xlsx("D:/桌面/销售订单.xlsx")
        for data in payloads:
            # 新增销售订单
            sales_code = data["salesCode"]
            sale_order = SaleOrder()
            business_id_sale_order = sale_order.sale_order_add(data)
            # 审批
            commit_payload_sale_order = sale_order.commit_task_by_business_id(business_id_sale_order)
            sale_order.process_instance_cancel_flow(commit_payload_sale_order)
            #mrp计算
            mrp_cal = MRPCalculation()
            key = mrp_cal.mrp_calculation(sales_code,30,"测试方案")
            # 生成生产计划，采购计划
            mrp_cal.production_and_buy_plan(key)

    def run_two(self):
        #获取采购订单负载
        reader_buy = ReadBuyXlsx()
        payloads = reader_buy.read_buy_xlsx("D:\桌面\采购订单.xlsx")
        for data in payloads:
            # 新增采购订单
            purchase_code = data["purchaseCode"]
            buy_order_new = BuyOrderNew()
            business_id_buy_order = buy_order_new.buy_order_add(data)
            # 审批
            commit_payload_buy_order = buy_order_new.commit_task_by_business_id(business_id_buy_order)
            buy_order_new.process_instance_cancel_flow(commit_payload_buy_order)
            # 采购到货
            buy_arrival = BuyArrival()
            business_id_arrival_order = buy_arrival.buy_arrival_add(purchase_code)
            # 审批
            commit_payload_arrival_order = buy_arrival.commit_task_by_business_id(business_id_arrival_order)
            buy_arrival.process_instance_cancel_flow(commit_payload_arrival_order)
            # 采购到货单号

            buy_inspection = BuyInspection()











