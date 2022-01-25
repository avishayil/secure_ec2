"""Define the logger configuration that secure_ec2 use."""

import logging
from pathlib import Path

from secure_ec2.src.constants import LOGGING_FILE_NAME

logging.basicConfig(
    filename=f"{str(Path.home())}/{LOGGING_FILE_NAME}",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
    level=logging.ERROR,
)

logger = logging.getLogger(__name__)
