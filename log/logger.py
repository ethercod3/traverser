import logging
from rich.logging import RichHandler

_FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=_FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

logger = logging.getLogger("Traverser")
logger_extra = {"markup": True}
