import logging
from concurrent.futures import ProcessPoolExecutor
from typing import List
from .core import Scrubber

# Set up logging for parallel workers
logger = logging.getLogger(__name__)

def _scrub_task(image_data: bytes) -> bytes:
    """
    Independent task for ProcessPoolExecutor to handle scrubbing.
    Returns cleaned bytes or original bytes on failure.
    """
    try:
        # Scrubber handles memory-only processing
        scrubber = Scrubber(image_data)
        clean_bytes, _ = scrubber.process()
        return clean_bytes
    except Exception as e:
        logger.error(f"Multiprocessing scrub task failed: {e}")
        return image_data

def bulk_process(image_list: List[bytes], max_workers: int = None) -> List[bytes]:
    """
    High-performance bulk processing using ProcessPoolExecutor.
    Ideal for multi-core servers processing many attachments simultaneously.
    
    Args:
        image_list: A list of raw image byte streams.
        max_workers: Number of process workers (defaults to CPU count).
        
    Returns:
        List of scrubbed image byte streams in the original order.
    """
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # executor.map preserves order
        results = list(executor.map(_scrub_task, image_list))
    return results
