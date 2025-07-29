from datetime import datetime
from src.time.time_utils import add_random_work_delay, next_valid_work_time, is_work_time
from pymysql.connections import Connection
from baseApi.base_api import AllApi


def delay_time_sale_order(task_id: str):
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


def delay_process_times(process_code: str):
    """
    更新工序相关的时间，包括工序报工和工序转移的时间
    :param process_code: 工序派工单据编号
    """
    conn = AllApi().get_conn()
    current_time = datetime.now()

    # 为工序报工设置时间
    reporting_time = add_random_work_delay(current_time, 0.5, 2)  # 报工时间在起始时间后0.5-2小时
    if not is_work_time(reporting_time):
        reporting_time = next_valid_work_time(reporting_time)

    # 为工序转移设置时间（在报工之后）
    transfer_time = add_random_work_delay(reporting_time, 0.5, 1.5)  # 转移时间在报工后0.5-1.5小时
    if not is_work_time(transfer_time):
        transfer_time = next_valid_work_time(transfer_time)

    try:
        with conn.cursor() as cursor:
            # 更新工序派工时间
            reporting_sql = """
                            UPDATE pro_workorder_dispatch
                            SET create_time = %s SET update_time = %s
                            WHERE dispatch_code = process_code \
                            """
            reporting_time_str = reporting_time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(reporting_sql, (reporting_time_str, process_code))

            # 更新工序转移时间
            transfer_sql = """
                           UPDATE act_hi_taskinst
                           SET END_TIME_ = %s
                           WHERE PROC_DEF_KEY_ = 'process_transfer'
                             AND BUSINESS_KEY_ = %s \
                           """
            transfer_time_str = transfer_time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(transfer_sql, (transfer_time_str, process_code))

            conn.commit()
            print(f"[{process_code}] 工序报工时间更新为：{reporting_time_str}")
            print(f"[{process_code}] 工序转移时间更新为：{transfer_time_str}")
    finally:
        conn.close()

    # 返回转移时间作为下一个工序的起始时间
    return transfer_time
