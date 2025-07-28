from datetime import datetime
from src.time.time_utils import add_random_work_delay, next_valid_work_time, is_work_time
from pymysql.connections import Connection
from baseApi.base_api import AllApi


def delay_time_sale_order(task_id: str, ):
    conn = AllApi().get_conn()
    current_time = datetime.now()
    new_time = add_random_work_delay(current_time)
    if not is_work_time(new_time):
        new_time = next_valid_work_time(new_time)

    with conn.cursor() as cursor:
        sql = """
              UPDATE act_hi_taskinst
              SET LAST_UPDATED_TIME_ = %s
              WHERE PROC_INST_ID_ = %s
              """
        cursor.execute(sql, (new_time.strftime('%Y-%m-%d %H:%M:%S'), task_id))
    print(f"[{task_id}] 审批时间更新为：{new_time}")
