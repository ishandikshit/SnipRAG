#!/usr/bin/env python
"""
Setup script for SnipRAG package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sniprag",
    version="0.1.0",
    author="Ishan Dikshit",
    author_email="ishan.dikshit@example.com",
    description="Retrieval Augmented Generation with Image Snippets from PDFs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ishandikshit/SnipRAG",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "pymupdf>=1.19.0",
        "pillow>=9.0.0",
        "boto3>=1.18.0",
        "sentence-transformers>=2.2.0",
        "faiss-cpu>=1.7.0",
        "langchain>=0.0.200",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=4.0.0",
        ],
        "viz": [
            "matplotlib>=3.5.0",
        ],
    },
) 