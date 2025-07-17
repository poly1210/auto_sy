from decimal import Decimal, ROUND_HALF_UP
from urllib.parse import quote
from typing import List
import pandas as pd
import json

from baseApi.base_api import AllApi


class ReadSalesXlsx:

    def __init__(self):
        self.api = AllApi()

    def client_id_get(self, client_name):
        encoded = quote(client_name)
        url = f"admin-api/mes/md/client/list?pageNum=1&pageSize=10&clientName={encoded}"
        res = self.api.send_get_direct(url)
        if res["code"] == 200 and res["total"] > 0:
            return res["rows"][0]["clientId"]
        raise ValueError(f"未找到客户：{client_name}")

    def userid_get(self, user_name):
        encoded = quote(user_name)
        url = f"admin-api/system/user/list?pageNum=1&pageSize=10&userName={encoded}"
        res = self.api.send_get_direct(url)
        if res["code"] == 200 and res["total"] > 0:
            return res["rows"][0]["userId"]
        raise ValueError(f"未找到销售员：{user_name}")

    def sales_order_payload_list_get(self, code: str) -> dict:
        """根据产品编号获取销售单列表项内容"""
        url = f"admin-api/mes/md/mditem/select/page?pageNum=1&pageSize=10&isEnable=true&itemCode={code}&isSales=true"
        res = self.api.send_get_direct(url)
        if res.get("code") == 200 and res["total"] > 0:
            return res["rows"][0]
        raise ValueError(f"未找到销售产品编号：{code}")

    def read_sales_xlsx(self, filepath: str) -> List[dict]:
        column_map = {
            "单据编号": "salesCode",
            "客户": "clientName",
            "销售员": "userName",
            "销售日期": "salesData",
            "交货日期": "goodsTime",
            "产品编号": "itemCode",
            "数量": "itemNum",
            "含税单价": "taxPrice",
            "税率": "taxRate"
        }

        df = pd.read_excel(filepath)
        df.rename(columns=column_map, inplace=True)

        # 确保 taxPrice 是字符串类型，防止浮点精度丢失
        df["taxPrice"] = df["taxPrice"].apply(lambda x: str(x))

        # 排除掉没有填写必要信息的无效行
        df = df[df["salesCode"].notna() & df["clientName"].notna()]
        # 排除模板中的示例行或注释行
        df = df[~df["salesCode"].astype(str).str.contains("示例|说明", na=False)]

        grouped = df.groupby("salesCode")
        payloads = []

        for sales_code, group in grouped:
            try:
                # 提取共有字段
                first = group.iloc[0]
                client_name = str(first["clientName"])
                user_name = str(first["userName"])
                salse_code = str(first["salesCode"])
                # 执行查询方法，填入必传的id字段
                client_id = self.client_id_get(client_name)
                user_id = self.userid_get(user_name)

                payload = {
                    "salesCode": salse_code,
                    "clientId": client_id,
                    "clientName": client_name,
                    "userName": user_name,
                    "salesData": pd.to_datetime(first["salesData"]).strftime("%Y-%m-%d"),
                    "userId": user_id,
                    "list": []
                }

                for _, row in group.iterrows():
                    code = str(row["itemCode"])
                    item_num = row["itemNum"]
                    tax_price = Decimal(str(row["taxPrice"]))
                    tax_rate = Decimal(str(row["taxRate"]))
                    goods_time = row["goodsTime"]

                    item_info = self.sales_order_payload_list_get(code)

                    unit_money = tax_price / (1 + tax_rate / 100)
                    unit_money = unit_money.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

                    item = {
                        **item_info,
                        "itemNum": item_num,
                        "unitMoney": float(unit_money),
                        "taxRate": float(tax_rate.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)),
                        "totalMoney": float((unit_money * item_num).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)),
                        "goodsTime": pd.to_datetime(goods_time).strftime("%Y-%m-%d"),
                        "unreceivedGoods": item_num,
                        "taxMoney": float((tax_price * item_num).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)),
                    }

                    payload["list"].append(item)

                payloads.append(payload)

            except Exception as e:
                print(f"[!] 销售单号 {sales_code} 表格处理失败: {e}")
                raise

        return payloads


if __name__ == "__main__":
    reader = ReadSalesXlsx()
    result = reader.read_sales_xlsx("D:/桌面/销售订单.xlsx")
    print(json.dumps(result, indent=2, ensure_ascii=False))