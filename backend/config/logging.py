import logging
import sys
from backend.config.settings import get_settings


def setup_logging() -> logging.Logger:
    """Configure and return the root application logger based on current settings."""
    settings = get_settings()
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True,
    )

    logger = logging.getLogger("rag_eval")
    logger.setLevel(log_level)
    return logger
