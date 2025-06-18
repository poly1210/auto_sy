from baseApi.base_api import AllApi
from urllib.parse import quote

#工序入库
class ProcessInventory:
    business_id = None  # 类变量存储 businessId

    def __init__(self):
        self.api = AllApi()
        self.api.send_login("admin-api/config.yml")

    def auto_process_inventory_code(self):
        """获取工序入库单的自动编号"""
        relative_url ="admin-api/system/autocode/get/PRO_RECPT_CODE"
        process_inventory_code = self.api.send_get_direct(relative_url)
        return process_inventory_code

    def process_inventory_payload_get(self, inventory_code):
        """根据工单编号获取请求负载"""
        relative_url =f"admin-api/pro/recpt/selectListByProWorkorderRecpt?pageNum=1&pageSize=10&workorderCode={inventory_code}"
        response = self.api.send_get_direct(relative_url)
        data = response["rows"][0]
        return data

    def warehouse_info_get(self, name):
        """根据仓库名称查询仓库信息，返回完整仓库对象"""
        name = quote(name)
        relative_url = f"admin-api/mes/wm/warehouse/list?pageNum=1&pageSize=10&warehouseName={name}"
        response = self.api.send_get_direct(relative_url)

        if not response.get("rows"):
            raise ValueError(f"未找到名为 {name} 的仓库，请确认仓库是否存在")

        warehouse_info = response["rows"][0]  # 取第一个匹配结果
        return warehouse_info

    def process_inventory_add(self, work_order_code):
        item = self.process_inventory_payload_get(work_order_code)
        # 后续这个仓库要写成可传入的
        warehouse_info = self.warehouse_info_get("总仓库")

        new_item = item.copy()
        new_item["batchCode"] = self.auto_process_inventory_code()
        new_item.update({
            "warehouseId": warehouse_info["warehouseId"],
            "warehouseName": warehouse_info["warehouseName"],
            "warehouseCode": warehouse_info["warehouseCode"]
        })

        payload = {
            "isAutoPass": True,
            "list": [new_item]  # 放入 list 中
        }
        print(payload)


        relative_url = "admin-api/pro/recpt/batchTransfer"
        response = self.api.send_post_direct(relative_url, payload)
        print("工序入库:", response)
        assert response["code"] == 200, f"入库失败，返回：{response}"
        return response



# 使用示例
if __name__ == "__main__":
    # 创建 SaleOrder 实例
    pi = ProcessInventory()

    # 调用 系列 方法
    work_order_code = "MO202503210019"
    result = pi.process_inventory_add(work_order_code)
    print(result)
