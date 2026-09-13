"""Logging setup shared by the API and graph."""

import logging


def configure_logging(log_level: str) -> None:
    """Configure a concise, production-friendly application logger."""

    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
