from setuptools import setup, find_packages

setup(
    name="llm-scoring-sdk",
    version="1.0.0",
    description="Python SDK for LLM Scoring Service",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "requests>=2.28.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-mock>=3.10.0",
            "responses>=0.23.0",
        ]
    }
)
