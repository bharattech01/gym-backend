# app/services/groq_provider.py

import os

from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_response(messages):

    completion = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=messages,

        temperature=0.5,

        max_completion_tokens=1024,
    )

    return completion.choices[0].message.content