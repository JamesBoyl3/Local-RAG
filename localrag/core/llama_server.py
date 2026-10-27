import logging
from functools import lru_cache

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


def _server_url(host: str, port: int, path: str = "/v1/models") -> str:
    return f"http://{host}:{port}{path}"


def check_generative_server(serverConfig: LLamaServerConfig) -> bool:
    url = _server_url(serverConfig.HOST, serverConfig.GEN_PORT)
    try:
        response = requests.get(url, timeout=serverConfig.TIMEOUT)
        response.raise_for_status()
        logger.info(f"Generative server reachable at {url}")
        return True
    except requests.RequestException as exc:
        logger.error(f"Generative server unreachable at {url}: {exc}")
        return False


def check_embedding_server(serverConfig: LLamaServerConfig) -> bool:
    url = _server_url(serverConfig.HOST, serverConfig.EMBED_PORT)
    try:
        response = requests.get(url, timeout=serverConfig.TIMEOUT)
        response.raise_for_status()
        logger.info("Embedding server reachable at {url}")
        return True
    except requests.RequestException:
        logger.error("Embedding server unreachable at {url}: {exc}")
        return False


def get_session(serverConfig: LLamaServerConfig) -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=serverConfig.RETRIES,
        backoff_factor=LserverConfig.BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


@lru_cache(maxsize=1)
def get_embedding_dim(serverConfig: LLamaServerConfig) -> int:
    session = get_session()
    response = session.post(
        url=f"http://{serverConfig.HOST}:{serverConfig.EMBED_PORT}/v1/embeddings",
        json={
            "input": "a"
        },  # Dummy Text. Only care about the embedding dim of the response
        timeout=serverConfig.TIMEOUT,
    ).json()
    return len(response["data"][0]["embedding"])
