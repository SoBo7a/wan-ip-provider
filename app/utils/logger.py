import logging
import sys
import os

# Cant use env_vars.py here due to circular dependencies...
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Create logger
logger = logging.getLogger("app_logger")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

handler = logging.StreamHandler(sys.stdout)

# Define log format
formatter = logging.Formatter(
    "%(levelname)s:     %(message)s - %(asctime)s"
)

handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False
