import aiohttp
import dateparser


async def ask_meta_ai(prompt):
    url = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-chat-hf"
    headers = {"Authorization": f"Bearer YOUR_HUGGINGFACE_TOKEN"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json={"inputs": prompt}) as resp:
            data = await resp.json()
            return data[0]["generated_text"] if isinstance(data, list) else "❌ AI Error!"
# bot/utils.py


def parse_reminder_time(text: str):
    """
    Parse a natural language time like 'in 10 minutes' or 'tomorrow 5pm'
    and return a datetime object.
    """
    reminder_time = dateparser.parse(text)
    return reminder_time

# Utilities like fetch weather etc
