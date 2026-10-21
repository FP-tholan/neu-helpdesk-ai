from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Ollama
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    ollama_timeout: int = 60
    ollama_max_retries: int = 3

    # Service
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "INFO"
    secret_key: str = "dev-secret"

    # KB
    kb_dir: str = "./data/knowledge_base"

    # Retrieval
    retrieval_top_k: int = 5
    rerank_top_k: int = 3
    bm25_weight: float = 0.6
    faiss_weight: float = 0.4
    enable_faiss: bool = False

    # Agent
    agent_max_iterations: int = 5
    agent_timeout_sec: int = 45

    # Memory
    memory_max_per_session: int = 50
    memory_top_k: int = 5

    # Router
    router_confidence_threshold: float = 0.5

    @property
    def kb_path(self) -> Path:
        p = Path(self.kb_dir)
        if not p.is_absolute():
            p = Path(__file__).resolve().parent.parent / p
        return p


settings = Settings()