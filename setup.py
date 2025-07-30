#!/usr/bin/env python3
"""
Setup script for SPX Straddle Bot
"""
from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="spx-straddle-bot",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Automated SPX options straddle trading bot with risk management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/spx-straddle-bot",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "spx-bot=production_strategy_complete:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", ".env.template"],
    },
)