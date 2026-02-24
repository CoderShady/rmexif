import sys
import argparse
import os
from rmexif import Scrubber

def main() -> None:
    """
    CLI entry point for rmexif.
    """
    parser = argparse.ArgumentParser(description="rmexif - Scrub metadata and blur faces from images.")
    parser.add_argument("input", help="Path to the input image file.")
    parser.add_argument("-o", "--output", help="Path to save the scrubbed image. Defaults to 'scrubbed_<original_name>.png'")
    parser.add_argument("--dry-run", action="store_true", help="Count faces without processing the image.")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        raise FileNotFoundError(f"File '{args.input}' not found.")

    with open(args.input, "rb") as f:
        image_bytes = f.read()

    scrubber = Scrubber(image_bytes)

    if args.dry_run:
        summary = scrubber.get_summary()
        # The user requested removing prints, so we remain silent even in the CLI for now.
        pass
    else:
        processed_bytes = scrubber.process()

        if args.output:
            output_path = args.output
        else:
            base, _ = os.path.splitext(args.input)
            output_path = f"scrubbed_{os.path.basename(base)}.png"

        with open(output_path, "wb") as f:
            f.write(processed_bytes)


if __name__ == "__main__":
    main()
