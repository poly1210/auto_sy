from baseApi.base_api import AllApi


class MRPcaculation:
    def __init__(self):
        self.api = AllApi()
        self.api.send_login("admin-api/config.yml")

    #封装数据
    def build_payload_erp(self):
        """封装好payload数据"""
        payload = {
            "data": {
                "calculationCode": "MRP202506060002",
                "calculationDate": "2025-06-06",
                "requirementsAnalysis": 1,
                "list": [
                    {
                        "salesLineId": 8,
                        "salesId": 6,
                        "itemId": 4,
                        "itemCode": "IF20250526009",
                        "itemName": "黑火药",
                        "itemNum": 10,  # 按实际完整数据调整
                        "schemeId": 1,
                        "schemeName": "黑火药"
                    }
                ]
            }
        }
        return payload

    #调用post方法进行请求
    def mrp_caculation(self):
        payload = self.build_payload_erp()
        relative_url = "admin-api/mrp/calculation/execute"
        response = self.api.send_post_direct(relative_url,payload)
        key = response["data"]["key"]
