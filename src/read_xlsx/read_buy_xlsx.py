import traceback
from urllib.parse import quote
from typing import List
import pandas as pd
import json

from baseApi.base_api import AllApi

# 读取采购订单表格
class ReadBuyXlsx:

    def __init__(self):
        self.api = AllApi()

    def vendor_id_get(self, vendor_name):
        encoded = quote(vendor_name)
        url = f"admin-api/mes/md/vendor/list?pageNum=1&pageSize=10&vendorName={encoded}"
        res = self.api.send_get_direct(url)
        if res["code"] == 200 and res["total"] > 0:
            return res["rows"][0]
        raise ValueError(f"未找到供货商：{vendor_name}")

    def userid_get(self, user_name):
        encoded = quote(user_name)
        url = f"admin-api/system/user/list?pageNum=1&pageSize=10&userName={encoded}"
        res = self.api.send_get_direct(url)
        if res["code"] == 200 and res["total"] > 0:
            return res["rows"][0]["userId"]
        raise ValueError(f"未找到采购员：{user_name}")

    def buy_order_payload_list_get(self, code: str) -> dict:
        """根据产品编号获取采购单列表项内容"""
        url = f"admin-api/mes/md/mditem/select/page?pageNum=1&pageSize=10&isEnable=true&itemCode={code}&isSales=true"
        res = self.api.send_get_direct(url)
        res["rows"][0]["itemSpec"] = res["rows"][0]["specification"]
        if res.get("code") == 200 and res["total"] > 0:
            return res["rows"][0]
        raise ValueError(f"未找到采购产品编号：{code}")

    def read_buy_xlsx(self, filepath: str) -> List[dict]:
        # 这里的单价是不含税的，和销售订单不一样
        # 采购日期后端写的data你敢信？
        column_map = {
            "单据编号": "purchaseCode",
            "供应商": "vendorName",
            "采购员": "userName",
            "采购日期": "purchaseData",
            "交货日期": "deliveryDate",
            "产品编号": "itemCode",
            "数量": "itemNum",
            "单价": "unitMoney",
            "税率": "taxRate"
        }

        df = pd.read_excel(filepath)
        df.rename(columns=column_map, inplace=True)
        # 排除掉没有填写必要信息的无效行
        df = df[df["purchaseCode"].notna() & df["vendorName"].notna()]
        # 排除模板中的示例行或注释行
        df = df[~df["purchaseCode"].astype(str).str.contains("示例|说明", na=False)]

        grouped = df.groupby("purchaseCode")
        payloads = []

        for purchase_code, group in grouped:
            try:
                # 提取共有字段
                first = group.iloc[0]
                vendor_name = str(first["vendorName"])
                user_name = str(first["userName"])
                purchase_code = str(first["purchaseCode"])
                # 执行查询方法，填入必传的id字段
                vendor_info = self.vendor_id_get(vendor_name)
                vendor_id = vendor_info["vendorId"]
                vendor_code = vendor_info["vendorCode"]
                currency = vendor_info["currency"]
                user_id = self.userid_get(user_name)


                payload = {
                    "purchaseCode": purchase_code,
                    "vendorId": vendor_id,
                    "vendorName": vendor_name,
                    "vendorCode": vendor_code,
                    "currency" : currency,
                    "userName": user_name,
                    "purchaseData": pd.to_datetime(first["purchaseData"]).strftime("%Y-%m-%d"),
                    # "deliveryDate":pd.to_datetime(first["deliveryDate"]).strftime("%Y-%m-%d"),
                    "userId": user_id,
                    "list": []
                }
                # _ 表示忽略索引列
                for _, row in group.iterrows():
                    code = str(row["itemCode"])
                    item_num = row["itemNum"]
                    unit_money = row["unitMoney"]
                    tax_rate = row["taxRate"]
                    goods_time = pd.to_datetime(row["deliveryDate"]).strftime("%Y-%m-%d")

                    item_info = self.buy_order_payload_list_get(code)

                    tax_price = unit_money * (1 + tax_rate / 100)

                    item = {
                        **item_info,
                        # "itemCode": code,
                        # "itemId": item_info["itemId"],
                        # "itemName": item_info["itemName"],
                        "itemNum": item_num,
                        "unitMoney": unit_money,
                        "taxRate": tax_rate,
                        "taxMoney":tax_price * item_num,
                        "totalMoney" : unit_money * item_num,
                        "goodsTime" : goods_time,
                    }

                    payload["list"].append(item)

                payloads.append(payload)
                print(payloads)


            except Exception as e:
                print(f"[!] 采购单号 {purchase_code} 表格处理失败:")
                traceback.print_exc()
                raise

        return payloads


if __name__ == "__main__":
    reader = ReadBuyXlsx()
    result = reader.read_buy_xlsx("D:\桌面\采购订单.xlsx")
    print(json.dumps(result, indent=2, ensure_ascii=False))
