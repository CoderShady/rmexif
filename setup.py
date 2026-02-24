from setuptools import setup, find_packages

setup(
    name="rmexif",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Pillow",
        "opencv-python",
        "numpy",
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "rmexif=rmexif.cli:main",
        ],
    },
    author="Your Name",
    description="A professional tool to strip EXIF metadata and blur faces from images.",
    python_requires=">=3.6",
)
