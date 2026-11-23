"""Turns text into vectors using Gemini embeddings."""

from langchain_google_genai import GoogleGenerativeAIEmbeddings


class Embedder:
    def __init__(self, model_name: str, api_key: str):
        # The vector store uses this model to embed chunks when they are added
        # and to embed the question when searching.
        self.model = GoogleGenerativeAIEmbeddings(model=model_name, google_api_key=api_key)

    def embed_query(self, text: str) -> list[float]:
        """Return the vector for one piece of text (handy for debugging)."""
        return self.model.embed_query(text)
