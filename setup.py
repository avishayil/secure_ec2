#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [
    "Click==8.0.1",
    "boto3==1.17.109",
    "PyInquirer==1.0.3",
    "requests==2.25.1",
    "halo==0.0.31",
    "pyperclip==1.8.2",
]

test_requirements = [
    "pytest>=3",
    "pytest-cov>=2.12",
    "bandit>=1.7.0",
    "black>=21.7b0",
    "isort>=5.9.2",
    "flake8>=3.9.2",
    "moto>=2.2.0",
    "coverage>=5.5",
    "coverage-badge>=1.0.1",
    "pre-commit>=2.13.0",
    "bump2version>=0.5.4",
    "tox>=3.24.5",
    "Sphinx>=4.4.0",
]

setup(
    author="Avishay Bar",
    author_email="avishay.il@gmail.com",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
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
    version="0.0.5",
    zip_safe=False,
)
