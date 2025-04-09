# Setup instructions
# Personal Assistant Bot

- Powered by Meta AI (via HuggingFace Inference).
- Telegram group moderation features (mute, kick, welcome).
- Scheduled reminders.
- Dynamic power user management.

## Setup

1. Set environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `DOMAIN`
   - `HUGGINGFACE_TOKEN`

2. Run:

```bash
pip install -r requirements.txt
uvicorn bot.main:app --host 0.0.0.0 --port 8000
