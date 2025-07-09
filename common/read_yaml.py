import yaml
from pathlib import Path
from typing import Dict, Any
import common.file_path as FilePath  # 这里保持不变

def ReadYaml(file_path: str) -> Dict[str, Any]:
    """
    读取YAML文件内容并返回Python字典

    :param file_path: YAML文件路径（注意：这里传的是完整路径）
    :return: 解析后的字典数据，若失败则返回 None
    """
    try:
        if not Path(file_path).exists():
            raise FileNotFoundError(f"YAML文件不存在: {file_path}")

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
    将 API 响应中的 Token 写入 token.yml（自动处理打包与开发环境）

    :param response: 包含 {"token": "xxx"} 的字典（通常是接口返回）
    """
    try:
        token = response["token"]
        config_data = {"token": token}
        token_path = FilePath.get_token_path()  # 正确使用新函数
        token_file = Path(token_path)
        token_file.parent.mkdir(parents=True, exist_ok=True)

        with open(token_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(config_data, f, sort_keys=False)

        print(f"Token 已成功写入 {token_file.absolute()}")
    except KeyError:
        print("错误：响应中未找到 token 字段")
    except Exception as e:
        print(f"写入配置文件失败: {str(e)}")
        raise
