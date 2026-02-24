class ProcessingError(Exception):
    """Custom exception for errors during image processing."""
    pass

from .core import Scrubber
from .utils import bulk_process

__all__ = ["Scrubber", "ProcessingError", "bulk_process"]

