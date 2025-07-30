from datetime import datetime, timedelta
import random

# 工作时间设置
WORK_START_HOUR = 9
WORK_END_HOUR = 18
LUNCH_START = 12
LUNCH_END = 13


# 全局时间跟踪器
class GlobalTimeTracker:
    def __init__(self):
        self.current_time = datetime.now()

    def advance_time(self, min_hours: float = 0.5, max_hours: float = 4.0) -> datetime:
        """推进时间并返回新的时间"""

        # 添加随机延迟
        delay_hours = random.uniform(min_hours, max_hours)
        self.current_time = self.current_time + timedelta(hours=delay_hours)

        # 确保在工作时间内
        if not is_work_time(self.current_time):
            self.current_time = next_valid_work_time(self.current_time)

        # 为秒添加随机值
        random_seconds = random.randint(0, 59)
        self.current_time = self.current_time.replace(
            second=random_seconds,
        )

        return self.current_time



def is_work_time(dt: datetime):
    if dt.weekday() >= 5:
        return False

    # 判断是否在午休时间（12:00-13:00）
    if LUNCH_START <= dt.hour < LUNCH_END:
        return False

    # 判断是否在工作时间范围内（9:00-18:00）
    return WORK_START_HOUR <= dt.hour < WORK_END_HOUR


def next_valid_work_time(dt: datetime):
    """将时间推进到最近的合法工作时间点"""
    # 如果当前是工作日且在工作时间内，直接返回当前时间
    if is_work_time(dt):
        return dt

    # 如果超出工作时间，则跳转到第二天的9-11点之间
    # 先移到第二天的9点
    next_day_9am = dt.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)

    # 跳过周末
    while next_day_9am.weekday() >= 5:
        next_day_9am += timedelta(days=1)

    # 在9-11点之间生成随机时间
    random_hour = random.randint(9, 10)  # 9点到10点之间
    random_minute = random.randint(0, 59)  # 随机分钟
    random_second = random.randint(0, 59)

    result_time = next_day_9am.replace(hour=random_hour, minute=random_minute, second=random_second)
    return result_time


def add_random_work_delay(current_time: datetime, min_hours: float = 1, max_hours: float = 4):
    """在当前时间上加上一个合法的随机延迟，并将秒和微秒设为随机值"""
    delay = random.uniform(min_hours, max_hours)
    future_time = current_time + timedelta(hours=delay)

    # 生成随机的秒（0-59）
    random_second = random.randint(0, 59)

    # 保留原时间的年、月、日、时、分，替换秒为随机值
    modified_time = future_time.replace(
        second=random_second,
    )

    return next_valid_work_time(modified_time)
