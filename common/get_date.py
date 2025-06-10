from datetime import datetime

def get_today():
    return datetime.now().date()  # 提取日期部分

def get_today_format(format):
    return datetime.now().strftime(format)  # 如：%Y年%m月%d日



if __name__ == '__main__':

    print(get_today())  # 输出示例：2025-03-17