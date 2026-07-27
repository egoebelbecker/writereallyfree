import os
import json
import platform

def get_config_dir():
    system = platform.system()
    app_name = "writereallyfree"
    
    if system == "Windows":
        base = os.environ.get("APPDATA")
        if not base:
            base = os.path.expanduser("~\\AppData\\Roaming")
    elif system == "Darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:  # Linux / Unix
        base = os.environ.get("XDG_CONFIG_HOME")
        if not base:
            base = os.path.expanduser("~/.config")
            
    return os.path.join(base, app_name)

def load_config():
    config_dir = get_config_dir()
    config_path = os.path.join(config_dir, "config.json")
    defaults = {
        "sync_folder_name": "",
        "copy_empty_folders": False,
        "theme": "system",
        "sync_folder_prefix": "",
        "convert_to_docx": False,
        "strip_date_prefix": False
    }
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                data = json.load(f)
                for k, v in defaults.items():
                    if k not in data:
                        data[k] = v
                return data
        except Exception:
            pass
    return defaults

def save_config(config_data):
    config_dir = get_config_dir()
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "config.json")
    try:
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=4)
        return True
    except Exception:
        return False
