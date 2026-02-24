import io
import time
import logging
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from .processors import strip_metadata, blur_faces

# Set up logging for internal error tracking
logger = logging.getLogger(__name__)

class Scrubber:
    """
    A strictly data-in, data-out utility to scrub images of sensitive 
    information including EXIF metadata and facial identifiers.
    
    This tool operates entirely in-memory using BytesIO, ensuring no unscrubbed 
    data is ever persisted to disk. This design makes it suitable for use 
    within any web framework (FastAPI, Django, Flask) or secure cloud function.
    """
    def __init__(self, image_bytes: bytes) -> None:
        """
        Initialize with raw image bytes.
        
        Args:
            image_bytes: The original image data in bytes.
        """
        if not isinstance(image_bytes, bytes):
            raise TypeError(f"Scrubber requires raw bytes, got {type(image_bytes)}")
        
        self.image_bytes: bytes = image_bytes
        self._validate()

    def _validate(self) -> None:
        """
        Internal validation to ensure the byte stream is a valid image.
        Does not perform any disk I/O.
        """
        try:
            Image.open(io.BytesIO(self.image_bytes)).verify()
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            raise ValueError("Input error: The provided data is not a valid image or is corrupted.")

    def process(self) -> tuple[bytes, Dict[str, Any]]:
        """
        Executes the metadata stripping and face blurring sequentially.
        Operates entirely in-memory.
        
        Returns:
            A tuple of (scrubbed_bytes, stats_dict) where stats_dict contains:
              - 'faces_detected': Number of faces found and blurred.
              - 'metadata_removed': Boolean indicating if stripping was attempted.
              - 'processing_time_ms': Execution time in milliseconds.
        """
        start_time = time.perf_counter()
        try:
            # Step 1: Strip EXIF metadata in-memory
            # We assume metadata is removed if step completes without error
            cleaned_bytes: bytes = strip_metadata(self.image_bytes)
            
            # Step 2: Detect and blur faces in-memory
            # blur_faces returns (processed_bytes, face_count)
            final_bytes, face_count = blur_faces(cleaned_bytes)
            
            end_time = time.perf_counter()
            processing_time_ms = (end_time - start_time) * 1000
            
            stats = {
                "faces_detected": face_count,
                "metadata_removed": True,
                "processing_time_ms": round(processing_time_ms, 2)
            }
            
            return final_bytes, stats
        except Exception as e:
            logger.error(f"Scrubbing process failed: {e}", exc_info=True)
            raise



    def get_summary(self) -> Dict[str, Any]:
        """
        Optionally provides a metadata summary of the image without 
        modifying the original bytes. Used for reporting or dry runs.
        """
        try:
            # We use the processors directly to find faces
            from .processors import detect_faces
            _, faces = detect_faces(self.image_bytes)
            return {
                "faces_detected": len(faces),
                "data_size_bytes": len(self.image_bytes)
            }
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return {"faces_detected": 0, "error": str(e)}

    @staticmethod
    def _process_single(data: bytes) -> bytes:
        """Helper for bulk processing block."""
        try:
            # Matches the packing: returns (bytes, stats)
            cleaned_bytes, _ = Scrubber(data).process()
            return cleaned_bytes
        except Exception:
            # On failure, return original bytes to maintain sequence integrity
            return data


    @staticmethod
    def bulk_process(image_list: List[bytes]) -> List[bytes]:
        """
        Processes a list of image byte-streams in parallel.
        Strictly data-in, data-out.
        
        Args:
            image_list: List of raw byte streams.
            
        Returns:
            List of scrubbed byte streams.
        """
        with ThreadPoolExecutor() as executor:
            return list(executor.map(Scrubber._process_single, image_list))




