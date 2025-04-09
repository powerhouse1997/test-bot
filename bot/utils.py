import aiohttp

async def ask_meta_ai(prompt):
    url = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-chat-hf"
    headers = {"Authorization": f"Bearer YOUR_HUGGINGFACE_TOKEN"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json={"inputs": prompt}) as resp:
            data = await resp.json()
            return data[0]["generated_text"] if isinstance(data, list) else "❌ AI Error!"
# Utilities like fetch weather etc
