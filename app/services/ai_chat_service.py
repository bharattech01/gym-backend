# app/services/ai_chat_service.py

from app.services.prompts import SYSTEM_PROMPT
from app.services.groq_provider import generate_response


class AIChatService:

    @staticmethod
    def ask_ai(chat_history, user_message):

        messages = [

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }

        ]

        messages.extend(chat_history)

        messages.append(

            {
                "role": "user",
                "content": user_message
            }

        )

        reply = generate_response(messages)

        return reply