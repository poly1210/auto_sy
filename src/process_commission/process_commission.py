import json

#工单投产
class ProcessCommission:
    def __init__(self, api):
        self.api = api

    def is_last_process(self,production_code,item_code):
        relative_url = f"admin-api/pro/protransfer/selectListByProWorkorderTransfer?pageNum=1&pageSize=10&workorderCode={production_code}&itemCode={item_code}"
        response = self.api.send_get_direct(relative_url)
        # 等于0就是末工序
        if response["total"] == 0:
            return False
        else:
            return True


    def has_process_dispatch(self):
        relative_url = "admin-api/system/parameter/list"
        response = self.api.send_get_direct(relative_url)
        result = response["data"]["processDispatch"]
        if result:
            return True
        else:
            return False


    def process_commission_info_get(self, production_code):
        """获取工单投产的负载信息"""
        relative_url = f"admin-api/mes/pro/info/production/list?pageNum=1&pageSize=10&isCancel=false&workorderCode={production_code}"
        response = self.api.send_get_direct(relative_url)
        data = response["rows"]
        return data

    # def item_codes_get(self, production_code):
    #     """获取一个生产工单下的所有产品编号"""
    #     lists = self.process_commission_info_get(production_code)
    #     item_codes = []
    #     for item in lists:
    #         item_codes.append(item["itemCode"])
    #     return item_codes


    def process_commission(self,production_code):
        payload = {}
        lists = self.process_commission_info_get(production_code)
        item_codes = []
        for item in lists:
            line_id , quantity = item["lineId"],item["quantity"]
            payload[line_id] = quantity
            item_codes.append(item["itemCode"])
        print("请求体：", json.dumps(payload, ensure_ascii=False, indent=2))
        relative_url = "admin-api/mes/pro/info/production/false"
        response = self.api.send_post_direct(relative_url, payload)
        print(response)
        assert response["code"] == 200, f"新增工单投产失败，返回：{response}"

        return item_codes

# if __name__ == "__main__":
#     pcm = ProcessCommission()
#     pcm.process_commission("MO202506260009")




