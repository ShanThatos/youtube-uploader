import sys

from pathlib import Path

if getattr(sys, 'frozen', False):
    APP_PATH = Path(sys.executable).resolve().parent
    RESOURCE_PATH = Path(sys._MEIPASS).resolve()
else:
    APP_PATH = Path(sys.argv[0]).resolve().parent
    RESOURCE_PATH = APP_PATH

def resource_path(path: str) -> Path:
    return RESOURCE_PATH.joinpath(path).resolve()

def get_local_path(path: str) -> Path:
    return APP_PATH.joinpath(path).resolve()

def save_local_file(file_path: str, content: str):
    path = get_local_path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)

def load_local_file(file_path: str, default: str = None):
    path = get_local_path(file_path)
    if not path.exists():
        return default
    return path.read_text()
