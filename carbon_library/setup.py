from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="carbon_footprint_cal",
    version="1.0.0",
    author="Abigail Anil",
    author_email="abigailanil19@gmail.com",
    description="A library for calculating carbon emissions and managing related data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abigail-anil/Carbon-Footprint-Tracker",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "boto3",
        "requests",
        "requests_mock",
    ],
    extras_require={
        "dev": [
            "pytest",
            "moto",
            "coverage",
            "pylint",
        ],
    },
    
)