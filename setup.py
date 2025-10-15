#!/usr/bin/env python3
"""
GenreBend Pro - Professional Music Organization Tool
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="genrebend-pro",
    version="1.0.0",
    author="GenreBend Pro Team",
    author_email="team@genrebend-pro.com",
    description="Professional music organization tool with intelligent genre detection",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/genrebend-pro",
    project_urls={
        "Bug Reports": "https://github.com/your-username/genrebend-pro/issues",
        "Source": "https://github.com/your-username/genrebend-pro",
        "Documentation": "https://github.com/your-username/genrebend-pro#readme",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "flake8>=5.0",
            "black>=22.0",
            "mypy>=1.0",
        ],
        "test": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "pytest-mock>=3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "genrebend-pro=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="music, genre, classification, organization, lastfm, musicbrainz, lexicon",
)
