import json, os
from datetime import date, timedelta

CONFIG_FILE = "config.json"

def get_config():
    default = {"last_theme": "blue", "streak_element": "Fuoco", "last_play": ""}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return {**default, **json.load(f)}
    return default

def save_config(new_data):
    current = get_config()
    current.update(new_data)
    with open(CONFIG_FILE, "w") as f:
        json.dump(current, f)
