from baseApi.base_api import AllApi

# 查看物料是否免检，决定采购订单下一步是直接入库，还是到货检验
class IsExemptInspection:

    def __init__(self, api):
        self.api = api

    def item_info_get(self, code) :
        """根据产品编号获取具体内容"""
        url = f"admin-api/mes/md/mditem/page?pageNum=1&pageSize=10&itemCode={code}"
        res = self.api.send_get_direct(url)
        if res.get("code") == 200 and res["total"] > 0:
            return res["rows"][0]
        raise ValueError(f"未找到销售产品编号：{code}")

    def item_code_get(self, purchase_code):
        """根据采购订单号查询物料编码,并判断是否需要检验"""
        relative_url = f"admin-api/mes/po/purchase/list?pageNum=1&pageSize=10&purchaseCode={purchase_code}"
        response = self.api.send_get_direct(relative_url)
        data = response["rows"][0]["list"]
        is_inspection = False
        for item in data:
            item_code = item["itemCode"]
            item_info = self.item_info_get(item_code)
            is_exempt_inspection = item_info["isExemptInspection"]
            if is_exempt_inspection == "Y" :
                is_inspection = True
                break
        return is_inspection





