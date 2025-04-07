import os
import aiohttp

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

async def ask_groq(question):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "llama3-70b-8192",  # ✅ correct model name
        "messages": [
            {"role": "user", "content": question}
        ],
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            data = await response.json()
            return data['choices'][0]['message']['content']
