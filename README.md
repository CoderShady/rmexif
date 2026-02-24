# rmexif: Privacy-Preserving Image Scrubbing

rmexif is a specialized Python library designed to automate the removal of sensitive image metadata and the redaction of facial identifiers. It is engineered for high-security environments where data privacy and zero-persistence are critical requirements.

## Core Principles

### Zero-Persistence Architecture
The library utilizes a memory-only processing pipeline. Image data is handled exclusively via in-memory buffers (BytesIO and NumPy arrays). No temporary files are generated, and no data is written to the local file system during processing, ensuring compatibility with RAM-only environments and encrypted volumes.

### Data Privacy
- **Metadata Redaction**: Complete removal of EXIF tags, GPS coordinates, camera signatures, and software identifiers.
- **Automated Face Redaction**: AI-driven detection and heavy Gaussian blurring of facial regions to prevent biometric identification.
- **Stealth Mode (Digital Identity Reset)**: Automatic 0.99x resizing and quality re-encoding to ensure the resulting file has a unique cryptographic hash, effectively "de-indexing" it from the original.

## How to Use

Below is a quick example of how to integrate the `Scrubber` into a typical Python workflow, such as an image upload handler:

```python
from rmexif import Scrubber

# A dev's hypothetical messaging app function
def handle_image_upload(raw_bytes):
    # Initialize your tool with the raw data
    api = Scrubber(raw_bytes)
    
    # Get the clean version and the stats via tuple unpacking
    clean_bytes, stats = api.process()
    
    print(f"Privacy Check: {stats['faces_detected']} faces blurred.")
    print(f"New Digital Identity: {stats['new_hash']}")
    return clean_bytes
```

## Technical Features
- **Stateless Operation**: Thread-safe implementation designed for high-concurrency server environments.
- **Resilient Validation**: Rigorous verification of image integrity and format before processing.
- **Digital Fingerprinting**: Built-in SHA-256 hashing to verify "Stealth Mode" efficacy and track file transformations.
- **Atomic Operations**: Functions are designed to either complete successfully or raise a specific `ProcessingError`, ensuring predictable state management in complex workflows.

## How to Install

Install the required dependencies via pip:

```bash
pip install Pillow opencv-python numpy requests
```

To install the rmexif package locally:

```bash
pip install .
```

## CLI Usage
The library includes a silent CLI tool for programmatic automation.

```bash
# Redact faces and strip metadata
rmexif input.jpg -o output.png

# Perform a dry run to audit face detection counts
rmexif --dry-run input.jpg
```

## Security Specifications
- **Processing Logic**: Memory-only (Zero-disk footprint).
- **Concurrency**: Fully thread-safe for multi-worker environments.
- **Error Handling**: Strict exception-based error reporting; no standard output side-effects.
- **Modern Performance**: Integrated with `ThreadPoolExecutor` for high-throughput bulk processing.

## Integration Example

The following script demonstrates how a developer can incorporate `rmexif` into their existing codebase to process images in bulk while preserving privacy and generating audit stats.

```python
import os
import json
from rmexif import Scrubber

def test_api():
    # Define directories
    input_dir = "sampleinputs"
    output_dir = "sampleoutputs"
    
    # 1. Define a list of raw image bytes from local files
    image_data_list = []
    filenames = []
    
    if not os.path.exists(input_dir):
        print(f"Error: {input_dir} directory not found.")
        return

    # Filter for common image extensions
    valid_extensions = ('.jpg', '.jpeg', '.png', '.webp')
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(valid_extensions):
            input_path = os.path.join(input_dir, filename)
            with open(input_path, 'rb') as f:
                image_data_list.append(f.read())
                filenames.append(filename)

    # 2. Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 3. Loop through the images and call scrubber.process()
    for i, image_bytes in enumerate(image_data_list):
        # Initialize Scrubber with the raw bytes
        scrubber = Scrubber(image_bytes)
        
        # Execute processing
        scrubbed_bytes, stats = scrubber.process()
        
        # 4. Save the outputs in sampleoutputs
        output_filename = f"scrubbed_{filenames[i]}"
        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, 'wb') as f:
            f.write(scrubbed_bytes)
            
        # 5. Print only the JSON dictionary of stats to show the 'API' response
        print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    test_api()
```

