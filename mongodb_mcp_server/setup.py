"""Setup script for MongoDB Vector RAG MCP Server."""

from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mongodb-mcp-server",
    version="1.0.0",
    author="MongoDB Hackathon Team",
    author_email="team@example.com",
    description="A Model Context Protocol (MCP) server for MongoDB vector search and RAG applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/mongodb-mcp-server",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.12.0",
            "black>=23.0.0",
            "ruff>=0.1.0",
            "mypy>=1.7.0",
        ],
        "local-embeddings": [
            "sentence-transformers>=2.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mongodb-mcp-server=main:main",
        ],
    },
    keywords="mongodb vector search rag mcp claude ai ml nlp",
    project_urls={
        "Bug Reports": "https://github.com/your-username/mongodb-mcp-server/issues",
        "Source": "https://github.com/your-username/mongodb-mcp-server",
        "Documentation": "https://github.com/your-username/mongodb-mcp-server#readme",
    },
)
