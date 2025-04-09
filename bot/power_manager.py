power_users = set()

def add_power_user(user_id):
    power_users.add(user_id)

def remove_power_user(user_id):
    power_users.discard(user_id)

def is_power_user(user_id):
    return user_id in power_users

def load_power_users():
    power_users.add(123456789)  # Your Telegram ID here
# Power user management
