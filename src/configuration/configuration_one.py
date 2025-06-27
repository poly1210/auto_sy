import sys
import os

from baseApi.base_api import AllApi

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
# 导入采购入库
from  src.buy_inventory.buy_inventory import BuyInventory
# 导入物料检验判断
from src.is_exempt_inspection.is_exempt_inspection import IsExemptInspection
# 导入生产领料
from src.production_requisition.production_requisition import ProductionRequisition
# 导入工单投产
from src.process_commission.process_commission import ProcessCommission
# 导入工序派工
from src.process_dispatch.process_dispatch import ProcessDispatch
# 导入生产领料
from src.production_requisition.production_requisition import ProductionRequisition
# 导入工序上线
from src.process_online.process_online import ProcessOnline
# 导入工序报工
from src.process_reporting.process_reporting import ProcessReporting

class Configuration:
    # 引入类实例
    def __init__(self,api):
        self.api = api
        self.reader_sales = ReadSalesXlsx()
        self.sale_order = SaleOrder(api)
        self.mrp_cal = MRPCalculation(api)
        self.reader_buy = ReadBuyXlsx()
        self.buy_order_new = BuyOrderNew(api)
        self.buy_arrival = BuyArrival(api)
        self.buy_inspection = BuyInspection(api)
        self.buy_inventory = BuyInventory(api)
        self.is_exempt_inspection = IsExemptInspection(api)
        self.production_requisition = ProductionRequisition(api)
        self.process_commission = ProcessCommission(api)
        self.process_dispatch = ProcessDispatch(api)
        self.production_requisition = ProductionRequisition(api)
        self.process_online = ProcessOnline(api)
        self.process_reporting = ProcessReporting(api)


    def run_one(self):
        """从表格读取销售订单-新增-审批-mrp运算-生成生产计划和采购计划"""
        # 获取销售订单负载
        payloads = self.reader_sales.read_sales_xlsx("D:/桌面/销售订单.xlsx")
        for data in payloads:
            # 新增销售订单
            sales_code = data["salesCode"]
            business_id_sale_order = self.sale_order.sale_order_add(data)
            # 审批
            commit_payload_sale_order = self.sale_order.commit_task_by_business_id(business_id_sale_order)
            self.sale_order.process_instance_cancel_flow(commit_payload_sale_order)
            #mrp计算
            key = self.mrp_cal.mrp_calculation(sales_code,30,"测试方案")
            # 生成生产计划，采购计划
            self.mrp_cal.production_and_buy_plan(key)

    def run_two(self):
        """从表格读取采购订单-新增--审批-（到货-审批-采购检验-审批）-采购入库"""
        #获取采购订单负载
        payloads = self.reader_buy.read_buy_xlsx("D:\桌面\采购订单.xlsx")
        for data in payloads:
            # 新增采购订单
            purchase_code = data["purchaseCode"]
            business_id_buy_order = self.buy_order_new.buy_order_add(data)
            # 审批
            commit_payload_buy_order = self.buy_order_new.commit_task_by_business_id(business_id_buy_order)
            self.buy_order_new.process_instance_cancel_flow(commit_payload_buy_order)
            # 判断物料是否全要检验，如果全不免检，就要走到货再检验，否则直接走入库
            if not self.is_exempt_inspection.item_code_get(purchase_code) :
                # 采购到货
                business_id_arrival_order, arrival_code = self.buy_arrival.buy_arrival_add(purchase_code,"总仓库")
                # 审批
                commit_payload_arrival_order = self.buy_arrival.commit_task_by_business_id(business_id_arrival_order)
                self.buy_arrival.process_instance_cancel_flow(commit_payload_arrival_order)
                # 传入到货单号,生成采购检验订单和审核
                inspection_codes = self.buy_inspection.buy_inspection_add(arrival_code)
                # 选采购检验单的采购入库,新增并审批
                for code in inspection_codes:
                    business_id_inventory_by_inspection = self.buy_inventory.buy_inventory_add_by_inspection(code)
                    payload_commit_inventory_by_inspection = self.buy_inventory.commit_task_by_business_id(business_id_inventory_by_inspection)
                    self.buy_inventory.process_instance_cancel_flow(payload_commit_inventory_by_inspection)
            #直接采购订单完就入库,新增并审批
            else :
                business_id_inventory_by_order = self.buy_inventory.buy_inventory_add_by_order(purchase_code,"总仓库")
                payload_commit_inventory_by_order = self.buy_inventory.commit_task_by_business_id(business_id_inventory_by_order)
                self.buy_inventory.process_instance_cancel_flow( payload_commit_inventory_by_order)

    # worker是车间派工的工作人
    def run_three(self,production_code,worker):
        """生产领料-"""
        # 分成两块（报工和不报工的），先是有工序报工的
        if self.production_requisition.has_report(production_code):
            # 工单投产
            self.process_commission.process_commission(production_code)
            # 如果是车间派工的，就工序派工
            if True :
                self.process_dispatch.process_dispatch_add(production_code,worker)
                #生产领料
                self.production_requisition.production_requisition_add(production_code)
                #工序上线
                self.process_online.process_online(production_code)
                #工单投产
                self.process_reporting.process_reporting_add()







        # 不报工，生产领料新增并审批
        else:
            business_id_production_requisition = self.production_requisition.production_requisition_add(production_code)
            payload_commit_production_requisition = self.production_requisition.commit_task_by_business_id(business_id_production_requisition)
            self.production_requisition.process_instance_cancel_flow(payload_commit_production_requisition)
            # 产品免检的话直接入库
            if True :








if __name__ == "__main__":
    api = AllApi()
    api.send_login("admin-api/config.yml")
    configuration = Configuration(api)
    configuration.run_two()













