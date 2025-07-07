import sys
import os
import time



project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(project_root)
from baseApi.base_api import AllApi
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
# 导入工序上线
from src.process_online.process_online import ProcessOnline
# 导入工序报工
from src.process_reporting.process_reporting import ProcessReporting
# 导入工序检验
from src.process_inspection.process_inspection import ProcessInspection
# 导入工序转移
from src.process_transfer.pocess_transfer import ProcessTransfer
# 导入工序入库
from src.process_inventory.process_inventory import ProcessInventory
# 导入产品入库
from src.production_inventory.production_inventory import ProductionInventory
# 导入产品送检
from src.production_submission.production_submission import ProductionSubmission
# 导入生产检验
from src.production_inspection.production_inspection import ProductionInspection

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
        self.process_inspection = ProcessInspection(api)
        self.process_transfer = ProcessTransfer(api)
        self.process_inventory = ProcessInventory(api)
        self.production_inventory = ProductionInventory(api)
        self.production_submission = ProductionSubmission(api)
        self.production_inspection = ProductionInspection(api)


    def run_one(self,sale_order_path,scheme_id,scheme_name):
        """从表格读取销售订单-新增-审批-mrp运算-生成生产计划和采购计划"""
        # 获取销售订单负载

        try:
            payloads = self.reader_sales.read_sales_xlsx(sale_order_path)
            for data in payloads:
                # 新增销售订单
                sales_code = data["salesCode"]
                business_id_sale_order = self.sale_order.sale_order_add(data)
                # 审批
                commit_payload_sale_order = self.sale_order.commit_task_by_business_id(business_id_sale_order)
                self.sale_order.process_instance_cancel_flow(commit_payload_sale_order)
                #mrp计算
                key = self.mrp_cal.mrp_calculation(sales_code,scheme_id,scheme_name)
                # 生成生产计划，采购计划
                self.mrp_cal.production_and_buy_plan(key)
            return {"msg": "销售订单全流程执行成功"}
        except Exception as e:
            # 捕获异常并返回错误信息
            error_msg = f" 流程执行失败: {str(e)}"
            return {"msg": error_msg}

    def run_two(self,buy_order_path,warehouse):
        """从表格读取采购订单-新增--审批-（到货-审批-采购检验-审批）-采购入库"""
        try:
            #获取采购订单负载
            payloads = self.reader_buy.read_buy_xlsx(buy_order_path)
            for data in payloads:
                # 新增采购订单并审批
                purchase_code = data["purchaseCode"]
                self.buy_order_new.buy_order_add(data)
                # 判断物料是否全要检验，如果全不免检，就要走到货再检验，否则直接走入库
                if not self.is_exempt_inspection.item_code_get(purchase_code) :
                    # 采购到货
                    business_id_arrival_order, arrival_code = self.buy_arrival.buy_arrival_add(purchase_code,warehouse)
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
                    business_id_inventory_by_order = self.buy_inventory.buy_inventory_add_by_order(purchase_code,warehouse)
                    payload_commit_inventory_by_order = self.buy_inventory.commit_task_by_business_id(business_id_inventory_by_order)
                    self.buy_inventory.process_instance_cancel_flow( payload_commit_inventory_by_order)
            return {"msg": "采购订单全流程执行成功"}
        except Exception as e:
            error_msg = f" 流程执行失败: {str(e)}"
            return {"msg": error_msg}

    # worker是车间派工的工作人
    def run_three(self,production_code):
        """生产管理和生产管理——工序的全流程综合"""
        try:
            # 分成两块（报工和不报工的），先是有工序报工的
            if self.production_requisition.has_report(production_code):
                # 工单投产并获取产品编号
                item_codes = self.process_commission.process_commission(production_code)
                # 只要不是末工序就一直在流程中流转
                is_end_precess = True
                # 判断是否成功获取产品编号
                if not item_codes:
                    print("未找到任何 item_code，流程结束")
                    return
                print("item_codes:", item_codes)  # 看看是不是 []
                for item_code in item_codes:
                    while is_end_precess:
                        # 如果是车间派工的，就工序派工
                        # TODO 这里要再写判断逻辑，是看有没有这个部门存在
                        # if True :
                        # 工序派工
                        self.process_dispatch.process_dispatch_add(production_code,item_code)
                        #生产领料
                        # self.production_requisition.production_requisition_add(production_code)
                        #工序上线
                        self.process_online.process_online(production_code)
                        #工序报工,并获取工序号
                        process_code =self.process_reporting.process_reporting_add(production_code)
                        #看是否需要检验,写不免检的流程
                        if not self.process_reporting.has_process_inspection(process_code):
                            self.process_inspection.process_inspection_add(production_code)
                        #判断是否末工序，就看工单投产搜单号能不能返回结果
                        if not self.process_commission.is_last_process(production_code,item_code):
                            is_end_precess = False
                            # 如果是末工序就工序入库
                            self.process_inventory.process_inventory_add(production_code)
                            # 产品入库
                            # self.production_inventory.production_inventory_add_by_production(production_code)
                        # 工序转移
                        else :
                            self.process_transfer.process_transfer(production_code)
                            # 等待两秒让数据库写上数据
                            time.sleep(2)
            # 不报工，生产领料新增并审批
            else:
                business_id_production_requisition = self.production_requisition.production_requisition_add(production_code)
                payload_commit_production_requisition = self.production_requisition.commit_task_by_business_id(business_id_production_requisition)
                self.production_requisition.process_instance_cancel_flow(payload_commit_production_requisition)
                # 产品不免检
                if  not self.production_requisition.item_code_get_by_product_code(production_code):
                    # 产品送检
                    submission_code = self.production_submission.production_submission_add(production_code)
                    # 生产检验
                    inspection_codes = self.production_inspection. production_inspection_add(submission_code)
                    #生产检验单的产品入库
                    for code in inspection_codes:
                        self.production_inventory.production_inventory_add_by_inspection(code)
                # 免检的直接入库
                self.production_inventory.production_inventory_add_by_production(production_code)
            return {"msg": "生产工单全流程执行成功"}
        except Exception as e:
            error_msg = f" 流程执行失败: {str(e)}"
            return {"msg": error_msg}


if __name__ == "__main__":
    api = AllApi()
    api.send_login("admin-api/config.yml")
    configuration = Configuration(api)
    configuration.run_three("MO202507020014")













