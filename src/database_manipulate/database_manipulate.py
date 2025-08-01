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

    def delay_time_process_dispatch_create(self, process_code, global_time):
        """
        更新工序派工创建时间
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
                                SET create_time = %s
                                WHERE dispatch_code = %s
                                """
                current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(reporting_sql, (current_time, process_code))

                conn.commit()
                print(f"[{process_code}] 工序派工创建时间更新为：{current_time}")
        finally:
            conn.close()

    def delay_time_process_dispatch_update(self, process_code, global_time):
        """
        更改工序派工更新时间
        :param process_code: 工序派工单据编号
        :param global_time:
        """
        conn = AllApi().get_conn()
        current_time = global_time

        if not is_work_time(current_time):
            current_time = next_valid_work_time(current_time)

        try:
            with conn.cursor() as cursor:

                reporting_sql = """
                                UPDATE pro_workorder_dispatch
                                SET update_time = %s
                                WHERE dispatch_code = %s
                                """
                current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(reporting_sql, (current_time, process_code))

                conn.commit()
                print(f"[{process_code}] 工序派工审核时间更新为：{current_time}")
        finally:
            conn.close()

    def change_porcess_online_time(self, process_id, global_time):
        """
                更改工序上线的时间
                :param process_code: 工序派工单据编号
                :param global_time:
                """
        conn = AllApi().get_conn()
        current_time = global_time

        try:
            with conn.cursor() as cursor:
                reporting_sql = """
                                UPDATE pro_workorder_info
                                SET request_date = %s
                                WHERE id = process_id
                                """
                # 修改数据格式，使之和数据库格式匹配
                current_time = current_time.replace(hour=0, minute=0, second=0)
                current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(reporting_sql, current_time)

                conn.commit()
                print(f"[{process_id}] 工序上线审核时间更新为：{current_time}")
        finally:
            conn.close()

    def change_porcess_reporting_time(self, work_order_code, global_time):
        """
                更改工序报工的时间
                :param global_time:
                """
        conn = AllApi().get_conn()
        current_time = global_time

        try:
            with conn.cursor() as cursor:
                reporting_sql = """
                                UPDATE pro_workorder_operation
                                SET create_time = %s
                                WHERE id = (SELECT id \
                                            FROM (SELECT id \
                                                  FROM pro_workorder_operation \
                                                  WHERE workorder_code = %s \
                                                    and operation_type = 3 \
                                                  ORDER BY process_order_num DESC LIMIT 1) AS subquery) \
                                """
                # 修改数据格式，使之和数据库格式匹配
                current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(reporting_sql, (current_time, work_order_code))

                conn.commit()
                print(f"[{work_order_code}] 工序报工审核时间更新为：{current_time}")
        finally:
            conn.close()

    def change_porcess_inspection_time(self, inspection_code, global_time):
        """
                更改工序检验单的时间
                :param global_time:
                """
        conn = AllApi().get_conn()
        current_time = global_time

        try:
            with conn.cursor() as cursor:
                reporting_sql = """
                                UPDATE qc_process_inspection
                                SET workorder_date = %s
                                WHERE inspection_code = %s
                                """
                # 修改数据格式，使之和数据库格式匹配
                current_time = current_time.replace(hour=0, minute=0, second=0)
                current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(reporting_sql, (current_time, inspection_code))

                conn.commit()
                print(f"[{inspection_code}] 工序检验单审核时间更新为：{current_time}")
        finally:
            conn.close()

    def change_porcess_inventory_time(self, inspection_code, global_time):
        """
                更改工序入库的时间
                :param global_time:
                """
        conn = AllApi().get_conn()
        current_time = global_time

        try:
            with conn.cursor() as cursor:
                reporting_sql = """
                                UPDATE
                                    SET workorder_date = %s
                                WHERE = %s
                                """
                # 修改数据格式，使之和数据库格式匹配
                current_time = current_time.replace(hour=0, minute=0, second=0)
                current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(reporting_sql, (current_time, inspection_code))

                conn.commit()
                print(f"[{inspection_code}] 工序入库时间更新为：{current_time}")
        finally:
            conn.close()
