import sys
import os
from pathlib import Path

def get_config_path(relative_path: str) -> Path:
    """config.yml（打包内，只读）"""
    if getattr(sys, 'frozen', False):
        # exe 运行环境
        base_dir = Path(sys._MEIPASS)
        return base_dir / "config" / relative_path
    else:
        # 开发环境
        current_dir = Path(__file__).resolve().parent.parent
        return current_dir / "config" / relative_path

def get_token_path() -> Path:
    """token.yml（打包外，读写）"""
    if getattr(sys, 'frozen', False):
        # exe 运行环境：放在 exe 同目录
        base_dir = Path(os.path.dirname(sys.executable))
        return base_dir / "token.yml"
    else:
        # 开发环境
        current_dir = Path(__file__).resolve().parent.parent
        return current_dir / "config" / "token.yml"
