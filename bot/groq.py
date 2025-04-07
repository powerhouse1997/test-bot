from groq import Groq
import os

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

async def ask_ai(prompt: str) -> str:
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-70b-8192"  # or your Groq model name
    )
    return chat_completion.choices[0].message.content
