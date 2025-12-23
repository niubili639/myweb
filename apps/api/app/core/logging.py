import sys

from loguru import logger


def setup_logging(level: str = "INFO") -> None:
    """Configure loguru logger for console output."""
    logger.remove()
    logger.add(
        sys.stdout,
        level=level.upper(),
        backtrace=False,
        diagnose=False,
        enqueue=True,
        colorize=False,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
    )


__all__ = ["logger", "setup_logging"]
