# bot/power_manager.py
power_users = set()

def load_power_users():
    # Hardcoded initial admins (optional)
    global power_users
    power_users = set([
        123456789,  # Your Telegram ID
    ])

def add_power_user(user_id: int) -> bool:
    if user_id in power_users:
        return False
    power_users.add(user_id)
    return True

def remove_power_user(user_id: int) -> bool:
    if user_id not in power_users:
        return False
    power_users.remove(user_id)
    return True

def is_power_user(user_id: int) -> bool:
    return user_id in power_users