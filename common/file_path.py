import sys
import os
from pathlib import Path

def get_project_root() -> Path:
    """动态获取项目根目录 (erp_auto 所在路径)"""
    current_file = Path(__file__).resolve()  # 当前文件的绝对路径

    # 定义识别项目根目录的特征标识
    root_indicators = [
        "erp_auto",       # 项目主目录名
        ".git",           # Git 仓库标识
        "requirements.txt"  # 依赖文件
    ]

    for parent in current_file.parents:
        if any((parent / pattern).exists() for pattern in root_indicators):
            return parent

    raise FileNotFoundError("未找到项目根目录 erp_auto")

def get_config_path(relative_path: str) -> Path:
    """获取 config.yml（打包内只读，开发环境自动找项目根目录）"""
    if getattr(sys, 'frozen', False):
        # exe 运行环境：PyInstaller 临时目录
        base_dir = Path(sys._MEIPASS)
        return base_dir / "config" / relative_path
    else:
        # 开发环境：项目根目录
        project_root = get_project_root()
        return project_root / "config" / relative_path

def get_token_path() -> Path:
    """获取 token.yml（打包外读写，开发环境自动找项目根目录）"""
    if getattr(sys, 'frozen', False):
        # exe 运行环境：放在 exe 同目录（可读写）
        base_dir = Path(os.path.dirname(sys.executable))
        return base_dir / "token.yml"
    else:
        # 开发环境：项目根目录
        project_root = get_project_root()
        return project_root / "config" / "token.yml"
