from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    LLAMA-SERVER_PATH: Path
    GEN_MODEL_LOC: Path
    HF_EMBEDDING_MODEL_LOC: Path
    LOC_EMBEDDING_MODEL_LOC: Path


settings = Settings()
