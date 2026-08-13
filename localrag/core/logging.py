import logging


def configure_logger(level: int) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        filename="localrag.log",
    )
