import logging
from openai import OpenAI

logger = logging.getLogger("GmailAIResponder")


class AIResponder:
    def __init__(self, api_key, model="gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_reply(self, email_detail, system_prompt):
        user_message = (
            f"From: {email_detail['sender']}\n"
            f"Subject: {email_detail['subject']}\n\n"
            f"{email_detail['body'][:3000]}"
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=500,
                temperature=0.7,
            )
            reply = response.choices[0].message.content.strip()
            logger.info(f"AI reply generated ({len(reply)} chars)")
            return reply
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
