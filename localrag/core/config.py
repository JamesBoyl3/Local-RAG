from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from pathlib import Path
from functools import lru_cache

class LLMConfig(BaseModel):
    TEMP: float = 0.2
    MAX_TOKENS: int = 1024
    N_CTX: int = 2048


class LLamaServerConfig(BaseModel):
    LLAMA_BIN_PATH: str
    GEN_GGUF_PATH: str
    EMBED_GGUF_PATH: str
    HOST_IP: str = "127.0.0.1"
    GEN_PORT: int = 8080
    EMBED_PORT: int = 8081


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_nested_delimiter="__", env_nested_max_split=1
    )

    llm: LLMConfig
    llama_server: LLamaServerConfig


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
