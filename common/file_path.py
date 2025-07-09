import sys
import os
from pathlib import Path

def get_config_path() -> Path:
    """config.yml（放在 exe 同目录，读写）"""
    if getattr(sys, 'frozen', False):
        # 打包环境，exe同目录
        base_dir = Path(os.path.dirname(sys.executable))
        return base_dir / "config.yml"
    else:
        # 开发环境，config目录下
        current_dir = Path(__file__).resolve().parent.parent
        return current_dir / "config" / "config.yml"

def get_token_path() -> Path:
    """token.yml（同目录，读写）"""
    if getattr(sys, 'frozen', False):
        base_dir = Path(os.path.dirname(sys.executable))
        return base_dir / "token.yml"
    else:
        current_dir = Path(__file__).resolve().parent.parent
        return current_dir / "config" / "token.yml"
