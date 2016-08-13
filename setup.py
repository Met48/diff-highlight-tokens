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
    url='https://github.com/Met48/diff-highlight-tokens',
    packages=find_packages(),
    install_requires=get_file_content('requirements.txt').splitlines(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Version Control',
    ],

    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
