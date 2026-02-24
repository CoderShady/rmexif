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
            
        # 5. Print the API response and identity verification
        print(f"--- File: {filenames[i]} ---")
        print(f"Original Hash: {stats['original_hash']}")
        print(f"Scrubbed Hash: {stats['new_hash']}")
        print(f"Identity Changed: {stats['original_hash'] != stats['new_hash']}")
        print(json.dumps(stats, indent=2))
        print("\n")

if __name__ == "__main__":
    test_api()
