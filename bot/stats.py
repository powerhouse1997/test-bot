user_message_counts = {}

async def track_activity(update, context):
    user_id = update.effective_user.id
    user_message_counts[user_id] = user_message_counts.get(user_id, 0) + 1

async def send_stats(update, context):
    sorted_users = sorted(user_message_counts.items(), key=lambda x: x[1], reverse=True)
    msg = "📊 *Group Activity Stats:*\n\n"
    for user_id, count in sorted_users[:10]:
        user = await context.bot.get_chat_member(update.effective_chat.id, user_id)
        name = user.user.first_name
        msg += f"• {name}: {count} messages\n"
    await update.message.reply_text(msg, parse_mode="Markdown")
# Group statistics tracking
