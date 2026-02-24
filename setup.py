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
    author="CoderShady",
    description="A professional tool to strip EXIF metadata, blur faces, and reset digital identity via Stealth Mode.",
    python_requires=">=3.6",
)
