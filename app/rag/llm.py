"""Talks to the Groq chat model."""

from langchain_core.messages import BaseMessage


class LLMClient:
    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.api_key = api_key
        # Phase 2: ChatGroq instance
        self.model = None

    def generate(self, messages: list[BaseMessage]) -> str:
        """Send the prompt messages and return the answer text."""
        raise NotImplementedError
