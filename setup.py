#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

from secure_ec2 import __version__

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "Click>=8.1.7",
    "boto3>=1.34.0",
    "InquirerPy~=0.3.4",
    "requests>=2.32.3",
    "urllib3>=1.26.19",
    "halo>=0.0.31",
    "pyperclip>=1.8.2",
]

test_requirements = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "bandit>=1.7.0",
    "black>=24.3.0",
    "isort>=5.13.2",
    "flake8>=6.1.0",
    "moto>=5.0.0",
    "coverage>=7.0",
    "coverage-badge>=1.1.0",
    "pre-commit>=3.5.0",
    "bump2version>=1.0.1",
    "tox>=4.0",
    "Sphinx>=7.0",
    "flake8-docstrings>=1.7.0",
]

setup(
    author="Avishay Bar",
    author_email="avishay.il@gmail.com",
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    description="CLI tool that helps you to provision EC2 instances securely",
    entry_points={
        "console_scripts": [
            "secure_ec2=secure_ec2.main:cli",
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords="secure_ec2",
    name="secure_ec2",
    packages=find_packages(include=["secure_ec2", "secure_ec2.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    extras_require={
        "develop": test_requirements,
    },
    url="https://github.com/avishayil/secure_ec2",
    version=__version__,
    zip_safe=False,
)
