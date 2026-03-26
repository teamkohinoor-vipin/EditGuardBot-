import json
import os

DB_FILE = "data.json"

def load_data():
    """Load data from JSON file."""
    if not os.path.exists(DB_FILE):
        default_data = {
            "users": [],
            "groups": [],  # list of dicts: {"id": id, "title": title, "username": username}
            "group_settings": {},
            "authorized": {}
        }
        save_data(default_data)
        return default_data
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    """Save data to JSON file."""
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------- User ----------
def add_user(user_id, first_name, last_name, username):
    data = load_data()
    if user_id not in data["users"]:
        data["users"].append(user_id)
        save_data(data)
        return True
    return False

def get_total_users():
    data = load_data()
    return len(data["users"])

# ---------- Group ----------
def add_group(group_id, title, username, chat_type):
    data = load_data()
    # Check if group already exists
    existing = next((g for g in data["groups"] if g["id"] == group_id), None)
    if not existing:
        data["groups"].append({
            "id": group_id,
            "title": title,
            "username": username
        })
        # Initialize group settings
        if str(group_id) not in data["group_settings"]:
            data["group_settings"][str(group_id)] = {
                "silent_mode": False,
                "custom_warning": None
            }
        if str(group_id) not in data["authorized"]:
            data["authorized"][str(group_id)] = []
        save_data(data)

def remove_group(group_id):
    data = load_data()
    data["groups"] = [g for g in data["groups"] if g["id"] != group_id]
    if str(group_id) in data["group_settings"]:
        del data["group_settings"][str(group_id)]
    if str(group_id) in data["authorized"]:
        del data["authorized"][str(group_id)]
    save_data(data)

def get_total_groups():
    data = load_data()
    return len(data["groups"])

def get_all_groups():
    data = load_data()
    return [(g["id"], g["title"], g["username"]) for g in data["groups"]]

# ---------- Group Settings ----------
def get_group_settings(group_id):
    data = load_data()
    return data["group_settings"].get(str(group_id), {"silent_mode": False, "custom_warning": None})

def set_silent_mode(group_id, silent):
    data = load_data()
    if str(group_id) not in data["group_settings"]:
        data["group_settings"][str(group_id)] = {"silent_mode": False, "custom_warning": None}
    data["group_settings"][str(group_id)]["silent_mode"] = silent
    save_data(data)

def set_custom_warning(group_id, warning):
    data = load_data()
    if str(group_id) not in data["group_settings"]:
        data["group_settings"][str(group_id)] = {"silent_mode": False, "custom_warning": None}
    data["group_settings"][str(group_id)]["custom_warning"] = warning
    save_data(data)

# ---------- Authorized Users ----------
def is_authorized(group_id, user_id):
    data = load_data()
    return user_id in data["authorized"].get(str(group_id), [])

def add_authorized_user(group_id, user_id, added_by):
    data = load_data()
    if str(group_id) not in data["authorized"]:
        data["authorized"][str(group_id)] = []
    if user_id not in data["authorized"][str(group_id)]:
        data["authorized"][str(group_id)].append(user_id)
        save_data(data)

def remove_authorized_user(group_id, user_id):
    data = load_data()
    if str(group_id) in data["authorized"] and user_id in data["authorized"][str(group_id)]:
        data["authorized"][str(group_id)].remove(user_id)
        save_data(data)

def get_authorized_users(group_id):
    data = load_data()
    return data["authorized"].get(str(group_id), [])
