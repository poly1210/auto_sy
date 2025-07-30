from datetime import datetime
from src.time.time_utils import add_random_work_delay, next_valid_work_time, is_work_time
from pymysql.connections import Connection
from baseApi.base_api import AllApi


class DatabaseManipulate:
    def delay_time_sale_order(self, task_id: str):
        conn = AllApi().get_conn()
        current_time = datetime.now()
        new_time = add_random_work_delay(current_time)
        if not is_work_time(new_time):
            new_time = next_valid_work_time(new_time)

        with conn.cursor() as cursor:
            sql = """
                  UPDATE act_hi_taskinst
                  SET END_TIME_ = %s
                  WHERE ID_ = %s
                  """
            # 使用毫秒级精度的时间格式（只取前3位微秒作为毫秒）
            time_str = new_time.strftime('%Y-%m-%d %H:%M:%S') + '.' + '{:03d}'.format(new_time.microsecond // 1000)
            cursor.execute(sql, (time_str, task_id))
            conn.commit()  # 提交事务，确保更改被保存到数据库
        print(f"[{task_id}] 审批时间更新为：{time_str}")
        conn.close()  # 关闭数据库连接

    def delay_time_process_dispatch(self, process_code, global_time):
        """
        更新工序相关的时间，包括工序报工
        :param process_code: 工序派工单据编号
        :param global_time:
        """
        conn = AllApi().get_conn()
        current_time = global_time

        if not is_work_time(current_time):
            current_time = next_valid_work_time(current_time)

        try:
            with conn.cursor() as cursor:
                # 更新工序派工时间
                reporting_sql = """
                                UPDATE pro_workorder_dispatch
                                SET create_time = %s SET update_time = %s
                                WHERE dispatch_code = process_code \
                                """
                current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(reporting_sql, (current_time, current_time))

                conn.commit()
                print(f"[{process_code}] 工序报工时间更新为：{current_time}")
        finally:
            conn.close()
