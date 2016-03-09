#!/usr/bin/env python
from setuptools import setup, find_packages


def get_file_content(filename):
    with open(filename, 'r') as f:
        return f.read()

setup(
    name='diff-highlight-tokens',
    version='0.1',
    scripts=['diff-highlight-tokens'],
    description='A script to highlight git diffs using language-specific tokenization',
    author='Andrew Sutton',
    author_email='me@andrewcsutton.com',
    license='MIT',
    packages=find_packages(),
    install_requires=get_file_content('requirements.txt').splitlines(),

    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
