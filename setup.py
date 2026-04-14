from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nightmare-cleaner",
    version="2.0.0",
    author="Moamen Refaay and Mahmoud osama",
    author_email="moamen.refaey.dev@gmail.com, mahmoud4h5@gmail.com",
    description="A modular, high-performance Windows Cleaner and Optimizer CLI tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Moamen-R/Nightmare-Cleaning",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.1.7",
        "colorama>=0.4.6",
        "psutil>=5.9.8",
        "rich>=13.7.0",
    ],
    entry_points={
        "console_scripts": [
            "nightmare=nightmare_cleaner.cli:main",
        ],
    },
)
