import json

#工单投产
class ProcessCommission:
    def __init__(self, api):
        self.api = api



    def process_commission_info_get(self, production_code):
        """获取工单投产的负载信息"""
        relative_url = f"admin-api/mes/pro/info/production/list?pageNum=1&pageSize=10&isCancel=false&workorderCode={production_code}"
        response = self.api.send_get_direct(relative_url)
        data = response["rows"][0]
        return data["lineId"],data["quantity"]


    def process_commission(self,production_code):

       line_id , quantity = self.process_commission_info_get(production_code)
       payload={
           line_id:quantity
       }
       print("请求体：", json.dumps(payload, ensure_ascii=False, indent=2))
       relative_url = "admin-api/mes/pro/info/production/false"
       response = self.api.send_post_direct(relative_url, payload)
       return response

# if __name__ == "__main__":
#     pcm = ProcessCommission()
#     pcm.process_commission("MO202506260009")




