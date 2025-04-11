# bot/handlers.py
from telegram import Update
from telegram.ext import ContextTypes

async def handle_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Default fallback for unknown messages
    if update.message:
        await update.message.reply_text(f"🤖 You said: {update.message.text}")

async def search_manga(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("❗ Please provide a manga name after /manga. Example: `/manga Naruto`")
        return
    # Placeholder: Real search logic will go here
    await update.message.reply_text(f"🔍 Searching manga: {query}\n(Feature coming soon!)")

async def save_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    manga = " ".join(context.args)
    if not manga:
        await update.message.reply_text("❗ Please provide a manga name after /fav. Example: `/fav One Piece`")
        return
    # Placeholder: Save to database
    await update.message.reply_text(f"✅ Saved **{manga}** to your favorites!")

async def track_progress(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📈 Tracking your manga reading progress... (Feature coming soon!)")

async def send_recommendations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📚 Here are some manga recommendations for you:\n- Attack on Titan\n- One Punch Man\n- Demon Slayer")

async def send_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📰 Latest Manga News:\n- One Piece Chapter 1100 is out!\n- Jujutsu Kaisen Season 2 coming soon!")
