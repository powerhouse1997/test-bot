async def welcome_new_member(update, context):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"👋 Welcome {member.mention_html()}!", parse_mode="HTML")
# Welcome messages for new users
