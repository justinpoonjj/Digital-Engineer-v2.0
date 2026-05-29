import os 

from dotenv import load_dotenv
from openai import OpenAI

class LLMService:
    def __init__(self) -> None:
        load_dotenv()

        self.model = os.getenv("LLM_MODEL", "qwen2.5-coder:7b")
        self.client = OpenAI(
            api_key=os.getenv("LLM_API_KEY")
        )

    def generate(self, instructions: str, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            instructions=instructions,
            input=prompt,
        )

        return response.output_text