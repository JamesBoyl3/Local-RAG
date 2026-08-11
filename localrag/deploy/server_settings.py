from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class LLAMA_Server_Settings(BaseSettings):
    _env_path = Path(__file__).resolve().parent / "localrag.env"
    model_config = SettingsConfigDict(env_file=str(_env_path), extra="ignore")

    HOST_IP: str
    LLAMA_GEN_PORT: int
    LLAMA_EMBED_PORT: int
    LLAMA_EMBED_DIM: int


llama_server_settings = LLAMA_Server_Settings()
