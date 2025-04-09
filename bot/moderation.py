from telegram import ChatPermissions

async def mute_user(update, context):
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user's message to mute them!")
        return
    user_id = update.message.reply_to_message.from_user.id
    await context.bot.restrict_chat_member(
        chat_id=update.effective_chat.id,
        user_id=user_id,
        permissions=ChatPermissions(can_send_messages=False)
    )
    await update.message.reply_text("✅ User has been muted.")

async def kick_user(update, context):
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user's message to kick them!")
        return
    user_id = update.message.reply_to_message.from_user.id
    await context.bot.ban_chat_member(update.effective_chat.id, user_id)
    await update.message.reply_text("✅ User has been kicked.")
# Moderation tools like mute/kick
