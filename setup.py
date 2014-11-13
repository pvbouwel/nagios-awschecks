#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = [
    "boto"
]

setup(
    name='awschecks',
    version='0.0.1',
    description='A script to check whether tag policy is adhered to.',
    author='pvbouwel',
    url='https://github.com/pvbouwel/awschecks ',
    entry_points={},
    packages=find_packages(exclude=("tests", "tests.*")),
    install_requires=install_requires,
    license="Apache",
    test_suite="tests",
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: Apache Software License",
    ],
)
