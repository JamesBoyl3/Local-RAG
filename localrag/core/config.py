from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    LLAMA_SERVER_PATH: Path
    GEN_MODEL_PATH: Path
    EMBED_MODEL_PATH: Path


settings = Settings()  # type: ignore[arg-calls]
