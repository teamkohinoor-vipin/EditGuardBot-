import json
import os
from datetime import datetime

DB_FILE = "data.json"

def load_data():
    """Load data from JSON file."""
    if not os.path.exists(DB_FILE):
        # Create empty structure
        default_data = {
            "users": [],
            "groups": [],
            "group_settings": {},
            "authorized": {}
        }
        with open(DB_FILE, "w") as f:
            json.dump(default_data, f, indent=4)
        return default_data
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    """Save data to JSON file."""
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --------------------- User Functions ---------------------
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

# --------------------- Group Functions ---------------------
def add_group(group_id, title, username, chat_type):
    data = load_data()
    if group_id not in data["groups"]:
        data["groups"].append(group_id)
        # Initialize group settings
        if str(group_id) not in data["group_settings"]:
            data["group_settings"][str(group_id)] = {
                "silent_mode": False,
                "custom_warning": None
            }
        # Initialize authorized users list
        if str(group_id) not in data["authorized"]:
            data["authorized"][str(group_id)] = []
        save_data(data)
        return True
    return False

def remove_group(group_id):
    data = load_data()
    if group_id in data["groups"]:
        data["groups"].remove(group_id)
        # Remove group settings
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
    # We need to return list of (group_id, title, username)
    # But we don't store title/username in DB. This is a limitation.
    # For a complete solution, you'd need to store group info in the JSON.
    # Let's modify: store group details as dict in groups list.
    # For simplicity, we'll store group info as dict when added.
    # We'll adjust add_group to store more data.
    # Let's change: groups list will hold dicts: {"id": id, "title": title, "username": username}
    # We need to adapt add_group and remove_group.
    # I'll rewrite those functions.
    # Since we haven't started, let's update the structure:
    # "groups": [{"id": 123, "title": "Group", "username": "groupusername"}, ...]
    # But previous add_group only added the id. We'll modify.
    # For now, we'll assume groups is list of ids and we return ids, but the command /groups needs titles.
    # We'll fix it.
    # Let's redo the database functions properly.

# Actually, to avoid confusion, I'll rewrite the database from scratch with correct structure.
# Given time constraints, I'll provide a simplified version that still works for /groups (needs titles).
# But since the user requested a JSON database, I'll implement it fully.

# I'll create a new version of database.py with proper structure.

# Let's start fresh:

DB_FILE = "data.json"

def load_data():
    if not os.path.exists(DB_FILE):
        data = {
            "users": [],
            "groups": [],  # list of dicts: {"id": id, "title": title, "username": username}
            "group_settings": {},
            "authorized": {}
        }
        save_data(data)
        return data
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# User
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

# Group
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
        data["group_settings"][str(group_id)] = {
            "silent_mode": False,
            "custom_warning": None
        }
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

# Group settings
def get_group_settings(group_id):
    data = load_data()
    settings = data["group_settings"].get(str(group_id), {"silent_mode": False, "custom_warning": None})
    return settings

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

# Authorized users
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
    user_ids = data["authorized"].get(str(group_id), [])
    # We also need user names. We don't store names in JSON, so we'll just return user IDs.
    # In bot.py, we retrieve user details from the bot's user cache or API.
    # For simplicity, we'll just return IDs; the bot will handle fetching names.
    return user_ids
