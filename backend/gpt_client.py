from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

def get_horoscope_response(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "너는 별자리 운세 전문가야."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

