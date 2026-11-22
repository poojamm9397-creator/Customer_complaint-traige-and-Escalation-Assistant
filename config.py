import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    llm_provider: str
    openai_api_key: str
    openai_model: str
    anthropic_api_key: str
    anthropic_model: str
    database_path: str
    max_complaint_chars: int
    api_configured: bool

def get_settings() -> Settings:
    provider = os.getenv("LLM_PROVIDER", "none").strip().lower()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    configured = (provider == "openai" and bool(openai_key)) or (
        provider == "anthropic" and bool(anthropic_key)
    )
    return Settings(
        llm_provider=provider,
        openai_api_key=openai_key,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        anthropic_api_key=anthropic_key,
        anthropic_model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest"),
        database_path=os.getenv("DATABASE_PATH", "data/complaints.db"),
        max_complaint_chars=int(os.getenv("MAX_COMPLAINT_CHARS", "5000")),
        api_configured=configured,
    )
