#!/usr/bin/env python3
"""Setup script for CIS Assistant MCP Server"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cis-assistant-mcp",
    version="1.0.0",
    author="CIS Assistant Team",
    description="CIS (Circulatory Informatics System) Assistant MCP Server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tap919/CIS-Assistant-",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "mcp>=0.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cis-assistant=cis_assistant_mcp.server:main",
        ],
    },
)
