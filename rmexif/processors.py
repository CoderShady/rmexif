import io
import cv2
import logging
import numpy as np
from PIL import Image
from typing import Tuple, List, Any, Optional

# Set up logging
logger = logging.getLogger(__name__)

def strip_metadata(image_bytes: bytes) -> bytes:
    """
    Opens an image from bytes and saves it to a new BytesIO object
    without any EXIF or metadata.
    """
    try:
        # PIL.Image.open and save are thread-safe for separate ByteIO streams
        img = Image.open(io.BytesIO(image_bytes))
        output = io.BytesIO()
        img_format = img.format if img.format else "JPEG"
        img.save(output, format=img_format)
        return output.getvalue()
    except Exception as e:
        logger.error(f"Failed to strip metadata: {e}", exc_info=True)
        from . import ProcessingError
        raise ProcessingError(f"Failed to strip metadata: {str(e)}")

def detect_faces(image_bytes: bytes) -> Tuple[Optional[np.ndarray], List[Any]]:
    """
    Detects faces in an image using OpenCV.
    
    Thread-Safety:
    This function initializes a local instance of CascadeClassifier for every call,
    ensuring that concurrent threads do not share detector state.
    
    Returns:
        Tuple of (OpenCV image matrix, list of bounding boxes)
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.warning("Decoded image is None. Source bytes may be invalid.")
            return None, []

        # Local initialization ensures thread-safety in multi-threaded environments (e.g. Flask/FastAPI)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        if face_cascade.empty():
            logger.error("Haar Cascade XML file could not be loaded.")
            from . import ProcessingError
            raise ProcessingError("Could not load Haar Cascade XML file.")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        return img, list(faces)
    except Exception as e:
        logger.error(f"Error during face detection: {e}", exc_info=True)
        from . import ProcessingError
        if isinstance(e, ProcessingError):
            raise e
        raise ProcessingError(f"Error during face detection: {str(e)}")

def blur_faces(image_bytes: bytes) -> Tuple[bytes, int]:
    """
    Detects faces and applies Gaussian blur. 
    If no faces are found, it returns the original bytes.
    
    Returns:
        Tuple of (processed bytes, number of faces blurred)
    """
    try:
        img, faces = detect_faces(image_bytes)
        
        if img is None or len(faces) == 0:
            # If no faces found or image decoding failed, return bytes as is
            return image_bytes, 0

        for (x, y, w, h) in faces:
            face_roi = img[y:y+h, x:x+w]
            ksize: int = int(max(w, h) / 2) | 1
            blurred_face = cv2.GaussianBlur(face_roi, (ksize, ksize), 30)
            img[y:y+h, x:x+w] = blurred_face
            
        _, buffer = cv2.imencode('.jpg', img)
        return buffer.tobytes(), len(faces)
    except Exception as e:
        logger.error(f"Failed to blur faces: {e}", exc_info=True)
        from . import ProcessingError
        if isinstance(e, ProcessingError):
            raise e
        raise ProcessingError(f"Failed to blur faces: {str(e)}")
