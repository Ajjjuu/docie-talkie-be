"""App settings, loaded once from BE/.env."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# The BE/ folder. Relative paths in .env are resolved against it, so the app
# works no matter which folder it is started from.
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    # LLM (Groq)
    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-120b"

    # Embeddings (Gemini)
    google_api_key: str = ""
    embedding_model: str = "models/gemini-embedding-001"

    # Storage
    sqlite_path: str = "data/app.db"
    chroma_dir: str = "data/chroma"
    chroma_collection: str = "documents"
    upload_dir: str = "data/uploads"

    # RAG tuning
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 4
    max_upload_mb: int = 20

    # API
    cors_origins: str = "http://localhost:5173"

    # --- Resolved values (absolute paths, parsed lists) ---

    @property
    def sqlite_file(self) -> Path:
        return BASE_DIR / self.sqlite_path

    @property
    def chroma_path(self) -> Path:
        return BASE_DIR / self.chroma_dir

    @property
    def upload_path(self) -> Path:
        return BASE_DIR / self.upload_dir

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def check_api_keys(self) -> None:
        """Fail with a clear message if an API key is missing from .env."""
        missing = []
        if not self.groq_api_key:
            missing.append("GROQ_API_KEY")
        if not self.google_api_key:
            missing.append("GOOGLE_API_KEY")
        if missing:
            raise RuntimeError(f"Missing {', '.join(missing)} in BE/.env. Add your keys and restart.")

    def ensure_data_dirs(self) -> None:
        """Create the data folders if they don't exist yet."""
        self.sqlite_file.parent.mkdir(parents=True, exist_ok=True)
        self.chroma_path.mkdir(parents=True, exist_ok=True)
        self.upload_path.mkdir(parents=True, exist_ok=True)


settings = Settings()
# Folders must exist before SQLite or Chroma try to write into them
settings.ensure_data_dirs()
