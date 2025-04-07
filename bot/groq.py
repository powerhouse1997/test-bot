# bot/groq.py

import httpx
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Put your API Key in environment variable

async def ask_groq(prompt: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": "llama3-70b-8192",  # Llama 3 big model (free + best)
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,  # randomness
            }
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
