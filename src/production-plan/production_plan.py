from prefect.cli.dev import api


class production_plan():
    def __init__(self):
        self.api = api
    def build_key_production(self):
        key=""
        return key

    # 根据传入的key生成生产计划
    def production_plan(self):
        key = self.build_key_production()
        relative_url = "admin-api/mrp/calculation"
        response = self.api.send_post_direct(relative_url, key)
        order_num = response["data"]["ordernum"]
        calculation_id = response["data"]["calculationId"]
        code = response["data"]["code"]
