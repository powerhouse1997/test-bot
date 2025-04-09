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


---

2. Update utils.py

Change your is_power_user to import from power_manager:

# bot/utils.py
from bot.power_manager import is_power_user


---

3. Add /addpower and /removepower Commands

In handlers.py:

from bot.power_manager import add_power_user, remove_power_user, is_power_user

async def add_power(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_power_user(user_id):
        await update.message.reply_text("🚫 You're not authorized to add power users.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /addpower <user_id>")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid user ID.")
        return

    if add_power_user(target_id):
        await update.message.reply_text(f"✅ User {target_id} added as a power user.")
    else:
        await update.message.reply_text(f"⚠️ User {target_id} is already a power user.")

async def remove_power(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_power_user(user_id):
        await update.message.reply_text("🚫 You're not authorized to remove power users.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /removepower <user_id>")
        return

    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid user ID.")
        return

    if remove_power_user(target_id):
        await update.message.reply_text(f"✅ User {target_id} removed from power users.")
    else:
        await update.message.reply_text(f"⚠️ User {target_id} was not a power user.")


---

4. Register the Commands in main.py

# bot/main.py

from bot.handlers import add_power, remove_power

application.add_handler(CommandHandler("addpower", add_power))
application.add_handler(CommandHandler("removepower", remove_power))

Also, load the initial power users when bot starts:

# At the top of main.py
from bot.power_manager import load_power_users

# Inside your `on_startup` function
await application.initialize()
load_power_users()
await application.start()
 