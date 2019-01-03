#!/usr/bin/env python
import os
from setuptools import setup

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='opiniondb',
    version='0.1',
    packages=['opiniondb'],
    include_package_data=True,
    license='MIT License',
    description='Database like library that can have multiple states at same time.',
    author='Henrik Heino',
    author_email='henrik.heino@gmail.com',
    install_requires=[],
    dependency_links=[],
)
