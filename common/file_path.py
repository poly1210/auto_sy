from pathlib import Path

def get_project_root() -> Path:
    """动态获取项目根目录 (project 所在路径)"""
    current_file = Path(__file__).resolve()  # 当前文件的绝对路径

    # 定义识别项目根目录的特征标识
    root_indicators = [
        "erp_auto",  # 目录名称匹配
        ".git",  # Git 仓库标识
        "requirements.txt"  # 项目依赖文件
    ]

    # 向上遍历目录树查找特征文件/目录
    for parent in current_file.parents:
        if any((parent / pattern).exists() for pattern in root_indicators):
            return parent

    raise FileNotFoundError("未找到项目根目录 project")

def get_config_path(relative_path: str) -> Path:
    """生成配置文件的完整路径"""
    project_root = get_project_root()
    return project_root / "config" / relative_path

def get_baseApi_path(relative_path: str) -> Path:
    """生成配置文件的完整路径"""
    project_root = get_project_root()
    return project_root / "baseApi" / relative_path

def get_testCase_path(relative_path: str) -> Path:
    """生成配置文件的完整路径"""
    project_root = get_project_root()
    return project_root / "testCase" / relative_path

if __name__ == '__main__':
    path = get_baseApi_path(r"admin-api\plm\document\list.yml")
    print(path)