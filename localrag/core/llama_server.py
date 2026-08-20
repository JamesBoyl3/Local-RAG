import logging
from typing import Callable

import numpy as np
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


def _server_url(host: str, port: int, path: str = "/v1/models") -> str:
    return f"http://{host}:{port}{path}"


def check_generative_server(host: str, port: int, timeout: float = 5.0) -> bool:
    url = _server_url(host, port)
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        logger.info("Generative server reachable at %s", url)
        return True
    except requests.RequestException as exc:
        logger.error("Generative server unreachable at %s: %s", url, exc)
        return False


def check_embedding_server(host: str, port: int, timeout: float = 5.0) -> bool:
    url = _server_url(host, port)
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        logger.info("Embedding server reachable at %s", url)
        return True
    except requests.RequestException as exc:
        logger.error("Embedding server unreachable at %s: %s", url, exc)
        return False


def get_session(retries: int = 3, backoff_factor: float = 1.0) -> requests.Session:
    session = requests.Session()
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def start_generative_server() -> None:
    logger.warning(
        "start_generative_server() is a stub. Use systemd to manage llama.cpp generative server."
    )


def start_embedding_server() -> None:
    logger.warning(
        "start_embedding_server() is a stub. Use systemd to manage llama.cpp embedding server."
    )


