from telegram import Update
from telegram.ext import ContextTypes
from bot.utils import ask_meta_ai
from bot.power_manager import is_power_user
from telegram import ChatPermissions
from telegram import Update
from telegram.ext import ContextTypes

async def daily_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is your daily summary!")

async def power_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I have admin powers!")

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"You said: {update.message.text}")

async def command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Unknown command. Please use a valid command!")

async def features(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 *Bot Features:*\n\n"
        "• 🛡️ /power - Send commands to control the bot\n"
        "• 📖 /manga - Search Manga from MangaDex\n"
        "• 💬 /ask - Chat with AI (Meta AI)\n"
        "• 📝 /todo - Create personal To-Dos\n"
        "• 🗓️ /summary - Daily summary (Weather + Todos)\n"
        "• ⏰ /remindme - Set Reminders\n"
        "• 👥 Auto Welcome - Greets new members\n"
        "• 📊 Group Stats - Show top active users\n"
        "• 🔨 Admin Tools - Mute, Kick, Ban, Promote, Demote\n"
        "• 🔔 Scheduled Announcements - Reminders to group\n"
        "• ❤️ Save Favorite Manga\n"
        "• 🔮 Manga Recommendations\n"
        "• 👑 Only Power Users can control the bot\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def handle_power(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    text = update.message.text.lower()
    chat_id = update.effective_chat.id
    sender = update.effective_user

    # Check if user is power user
    from bot.power_manager import is_power_user
    if not is_power_user(sender.id):
        await update.message.reply_text("🚫 You don't have permission to use power commands.")
        return

    # Only react to replies
    if not update.message.reply_to_message:
        await update.message.reply_text("❗ Please reply to the user's message you want to act on.")
        return

    target_user = update.message.reply_to_message.from_user

    # Parse the action from message
    if "mute" in text:
        await mute_user(chat_id, target_user.id, context)
        await update.message.reply_text(f"🔇 Muted {target_user.mention_html()}!", parse_mode="HTML")

    elif "unmute" in text:
        await unmute_user(chat_id, target_user.id, context)
        await update.message.reply_text(f"🔊 Unmuted {target_user.mention_html()}!", parse_mode="HTML")

    elif "ban" in text:
        await ban_user(chat_id, target_user.id, context)
        await update.message.reply_text(f"🚫 Banned {target_user.mention_html()}!", parse_mode="HTML")

    elif "unban" in text:
        await unban_user(chat_id, target_user.id, context)
        await update.message.reply_text(f"✅ Unbanned {target_user.mention_html()}!", parse_mode="HTML")

    elif "promote" in text:
        await promote_user(chat_id, target_user.id, context)
        await update.message.reply_text(f"👑 Promoted {target_user.mention_html()}!", parse_mode="HTML")

    elif "demote" in text:
        await demote_user(chat_id, target_user.id, context)
        await update.message.reply_text(f"👤 Demoted {target_user.mention_html()}!", parse_mode="HTML")

    else:
        await update.message.reply_text("❓ Unknown power action. (Supported: mute, unmute, ban, unban, promote, demote)")

# ========== Helper Functions ==========

async def mute_user(chat_id, user_id, context):
    permissions = ChatPermissions(can_send_messages=False)
    await context.bot.restrict_chat_member(chat_id, user_id, permissions=permissions)

async def unmute_user(chat_id, user_id, context):
    permissions = ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
    )
    await context.bot.restrict_chat_member(chat_id, user_id, permissions=permissions)

async def ban_user(chat_id, user_id, context):
    await context.bot.ban_chat_member(chat_id, user_id)

async def unban_user(chat_id, user_id, context):
    await context.bot.unban_chat_member(chat_id, user_id)

async def promote_user(chat_id, user_id, context):
    await context.bot.promote_chat_member(
        chat_id,
        user_id,
        can_change_info=True,
        can_post_messages=True,
        can_edit_messages=True,
        can_delete_messages=True,
        can_invite_users=True,
        can_restrict_members=True,
        can_pin_messages=True,
        can_promote_members=False,
    )

async def demote_user(chat_id, user_id, context):
    await context.bot.promote_chat_member(
        chat_id,
        user_id,
        can_change_info=False,
        can_post_messages=False,
        can_edit_messages=False,
        can_delete_messages=False,
        can_invite_users=False,
        can_restrict_members=False,
        can_pin_messages=False,
        can_promote_members=False,
    )
