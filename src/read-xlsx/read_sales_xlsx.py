from decimal import Decimal
from urllib.parse import quote

import pandas as pd
from datetime import datetime
from typing import List

from baseApi.base_api import AllApi

class ReadSalesXlsx():

    def __init__(self):
        self.api = AllApi()

    def clientid_get(self, client_name):
        """从表格中传入的客户姓名拿到客户id"""
        encoded_client_name = quote(client_name)
        relative_url = f"admin-api/mes/md/client/list?pageNum=1&pageSize=10&clientName={encoded_client_name}"

        response = self.api.send_get_direct(relative_url)

        if response.get("code") == 200:
            data = response.get("data", {})
            if data.get("total", 0) > 0:
                return data["rows"][0]["clientId"]
            else:
                raise ValueError(f"未找到客户名称为 {client_name} 的客户信息")
        else:
            raise ValueError(f"请求失败：{response.get('msg', '未知错误')}")

    def userid_get(self,user_name):
        """从表格中传入的销售员姓名拿到销售员id"""
        #找出客户名字对应的 URL 编码值，方便进行查询
        encoded_user_name = quote(user_name)
        relative_url = f"admin-api/system/user/list?pageNum=1&pageSize=10&userName=｛encoded_user_name｝"

        # 通过 AllApi 的简洁 GET 方法直接发请求
        response = self.api.send_get_direct(relative_url)
        if response.get("code") == 200:
            data = response.get("data", {})
            if data.get("total", 0) > 0:
                return data["rows"][0]["userId"]
            else:
                raise ValueError(f"未找到销售员名称为 {user_name} 的销售员信息")
        else:
            raise ValueError(f"请求失败：{response.get('msg', '未知错误')}")

    def item_info_get(self, itemCode):
        """从表格中传入的产品编码拿到产品id和产品姓名"""
        # 找出客户名字对应的 URL 编码值，方便进行查询
        relative_url = f"admin-api/md/bom/page?pageNum=1&pageSize=10&itemCode=｛itemCode｝"

        # 通过 AllApi 的简洁 GET 方法直接发请求
        response = self.api.send_get_direct(relative_url)
        if response.get("code") == 200:
            data = response.get("data", {})
            if data.get("total", 0) > 0:
                return data["rows"][0]["itemId"],data["rows"][0]["itemName"]
            else:
                raise ValueError(f"未找到物料编码为{itemCode} 的信息")
        else:
            raise ValueError(f"请求失败：{response.get('msg', '未知错误')}")

    def read_sales_xlsx(self,filepath: str) -> List[dict]:
        """
        从 Excel 文件提取销售订单数据，返回符合接口格式的 payload 列表。

        参数：
            filepath: Excel 文件路径，包含销售订单表格。

        返回：
            List[dict]，每个 dict 对应一个销售订单的请求体。
        """
        # #创建类实例，方便调用方法
        # rsx = ReadSalesXlsx()
        # 中文表头 → 英文字段映射
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

        # 读取 Excel
        df = pd.read_excel(filepath)
        df.rename(columns=column_map, inplace=True)

        # 删除空行、表头示例、说明行
        df = df[df["salesCode"].notna() & df["clientName"].notna()]

        # 分组：每个订单一组
        grouped = df.groupby("salesCode")

        payloads = []

        for salesCode, group in grouped:
            first_row = group.iloc[0]
            #取出表格中的字段
            client_name = str(first_row["clientName"])
            user_name = str(first_row["userName"])

            payload = {
                "salesCode": str(first_row["salesCode"]),
                "clientId": self.clientid_get(client_name),
                "userId": self.userid_get(user_name),
                "salesData": pd.to_datetime(first_row["salesData"]).strftime("%Y-%m-%d"),
                "goodsTime": pd.to_datetime(first_row["goodsTime"]).strftime("%Y-%m-%d"),
                "list": []
            }

            for _, row in group.iterrows():
                itemCode = str(row["itemCode"])
                itemId,itemName = self.item_info_get(itemCode)
                item = {
                    "itemCode": itemCode,
                    "itemId": itemId,
                    "itemName": itemName,
                    "itemNum": Decimal(row["itemNum"]),
                    "unitMoney": Decimal(row["taxPrice"])/(1+row["taxRate"]),
                    "taxRate": Decimal(row["taxRate"]),
                    "totalMoney": Decimal(row["itemNum"]) * Decimal(row["unitMoney"])
                }
                payload["list"].append(item)

            payloads.append(payload)

        return payloads
if __name__ == "__main__":
    # 创建 类 实例
    rsx = ReadSalesXlsx()
    payload = rsx.read_sales_xlsx("D:\桌面\销售订单.xlsx")
    print(payload)