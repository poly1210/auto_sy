import random

def get_random_number(length):
    # 生成由随机数字组成的字符串（允许包含前导零）
    return ''.join(str(random.randint(0, 9)) for _ in range(length))




if __name__ == "__main__":
    try:
        user_input = int(input("请输入随机数的位数："))
        if user_input <= 0:
            print("请输入大于0的正整数")
        else:
            result = get_random_number(user_input)
            print(f"生成的{user_input}位随机数是：{result}")
    except ValueError:
        print("输入无效，请输入整数")