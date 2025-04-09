# bot/meta_ai.py

import aiohttp
import os

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

async def ask_meta_ai(prompt):
    if not HUGGINGFACE_API_KEY:
        raise ValueError("HuggingFace API key missing! Set HUGGINGFACE_API_KEY in env.")

    url = "https://api-inference.huggingface.co/models/meta-llama/Llama-3-8b-chat-hf"  # Using Llama-3 8B
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7,
            "do_sample": True,
            "return_full_text": False,   # <--- Only new text
            "stream": True               # <--- Stream enabled
        }
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            # Stream the text chunks
            full_text = ""
            async for chunk in response.content:
                full_text += chunk.decode(errors="ignore")
            return full_text.strip()
