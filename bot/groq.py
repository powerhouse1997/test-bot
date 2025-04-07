import aiohttp

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = "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"  # Replace this!

async def ask_groq(question):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "mixtral-8x7b-32768",  # You can change model here
        "messages": [
            {"role": "user", "content": question}
        ],
        "temperature": 0.7
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(GROQ_API_URL, headers=headers, json=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data['choices'][0]['message']['content']
            else:
                return f"❌ Error: {resp.status} - {await resp.text()}"
