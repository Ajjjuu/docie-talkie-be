"""The Groq chat model used to write answers."""

from langchain_groq import ChatGroq


class LLMClient:
    def __init__(self, model_name: str, api_key: str):
        # temperature=0 keeps answers close to the provided context, with fewer creative guesses
        self.model = ChatGroq(model=model_name, api_key=api_key, temperature=0)
