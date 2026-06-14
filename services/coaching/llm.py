from services.config.workout_config import PROMPT


class LLMCoach:
    def __init__(self, groq_client):
        self.client = groq_client
        self.history = []
        self.system_prompt = PROMPT

    def give_feedback(self, event, issue):
        prompt = f"Event: {event}"

        if issue:
            prompt += f" Form Issue: {issue}"

        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.history[-10:],
            {"role": "user", "content": prompt}
        ]

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.4
            )

            # Normalize access to returned content; handle SDK variations
            text = None
            if hasattr(response, "choices") and response.choices:
                # common structure: response.choices[0].message.content
                first = response.choices[0]
                if hasattr(first, "message") and hasattr(first.message, "content"):
                    text = first.message.content
                elif isinstance(first, dict) and "message" in first and "content" in first["message"]:
                    text = first["message"]["content"]

            if not text and hasattr(response, "text"):
                text = response.text

            text = (text or "").strip()

            self.history.append({"role": "assistant", "content": text})

            return text
        except Exception as e:
            # On error, append a short message and return a fallback string
            fallback = "Sorry, I couldn't generate feedback right now."
            self.history.append({"role": "assistant", "content": fallback})
            return fallback