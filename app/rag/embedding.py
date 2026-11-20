"""Turns text into vectors using Gemini embeddings."""


class Embedder:
    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.api_key = api_key
        # Phase 2: GoogleGenerativeAIEmbeddings instance, also passed to Chroma
        self.model = None

    def embed_query(self, text: str) -> list[float]:
        """Return the vector for one piece of text (handy for debugging)."""
        raise NotImplementedError
