from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class Server:
    host: str
    ports: dict[str, int]

    timeout: float = 5.0
    retires: int = 3
    backoff_factor: float = 1.0

    def rag_addr(self) -> str:
        return f"http://{self.host}:{self.ports.get('rag', 8000)}"

    def gen_addr(self) -> str:
        return f"http://{self.host}:{self.ports.get('gen', 8001)}"

    def embed_addr(self) -> str:
        return f"http://{self.host}:{self.ports.get('embed', 8002)}"


class LLMConfig(BaseModel):
    TEMP: float = 0.2
    MAX_TOKENS: int = 1024
    N_CTX: int = 2048


settings = Settings()  # type: ignore[arg-calls]
