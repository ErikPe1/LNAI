#!/usr/bin/env python3
"""
Setup script for LinkedIn Scraper package.
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="linkedin-scraper",
    version="1.0.0",
    author="Erik Pe",
    author_email="175506674+ErikPe1@users.noreply.github.com",
    description="Automated LinkedIn profile scraper with intelligent scheduling and data extraction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ErikPe1/LNAI",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
    ],
    python_requires=">=3.9",
    install_requires=[
        "selenium==4.16.0",
        "webdriver-manager==4.0.1",
        "beautifulsoup4==4.12.2",
        "pandas==2.1.4",
        "python-dotenv==1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "flake8>=6.0",
            "black>=23.0",
        ]
    },
    include_package_data=True,
)
