import yaml
from pathlib import Path
from typing import Dict, Any
import common.file_path as FilePath


def ReadYaml(file_path: str) -> Dict[str, Any]:
    """
    读取YAML文件内容并返回Python字典

    :param file_path: YAML文件路径
    :return: 解析后的字典数据，若失败则返回None
    """
    try:
        # 验证文件存在性
        if not Path(file_path).exists():
            raise FileNotFoundError(f"YAML文件不存在: {file_path}")

        # 安全加载YAML内容（推荐使用safe_load而非load）
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            return data

    except yaml.YAMLError as e:
        print(f"YAML解析错误: {e}")
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"未知错误: {e}")
    return None


def write_token(response):
    """
    将 API 响应中的 Token 写入 YAML 文件
    :param response: requests.Response 对象，需包含 {"token": "xxx"} 结构
    :param config_path: 配置文件路径 (默认当前目录 config.yml)

    """
    try:
        # 提取 Token
        token = response["token"]

        # 构建数据结构
        config_data = {"token": token}

        # 确保目录存在

        token_path = FilePath.get_token_path()
        token_file = Path(token_path)
        token_file.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        # yaml.safe_dump()：将 Python 字典转换为 YAML 格式并写入文件。
        # sort_keys=False：禁止自动排序键名，保持数据顺序。
        with open(token_file, 'w') as f:
            yaml.safe_dump(config_data, f, sort_keys=False)

        print(f"Token 已成功写入 {token_file.absolute()}")
    except KeyError:
        print("错误：响应中未找到 token 字段")
    except Exception as e:
        print(f"写入配置文件失败: {str(e)}")
        raise