from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, filters

app = Flask(__name__)
bot_token = "6438781804:AAGvcF5pp2gg2Svr5f0kpxvG9ZMoiG1WACc"
bot = Bot(token=bot_token)
application = Application.builder().token(bot_token).build()

@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        update_data = request.get_json()
        update = Update.de_json(update_data, bot)

        # Check if it's a message and respond
        if update.message:
            chat_id = update.message.chat.id
            user_text = update.message.text
            response_text = f"You said: {user_text}"
            await bot.send_message(chat_id=chat_id, text=response_text)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
