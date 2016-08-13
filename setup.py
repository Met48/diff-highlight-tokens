#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='diff-highlight-tokens',
    version='0.2.0',
    scripts=['diff-highlight-tokens'],
    description='A command line tool to apply language-specific highlighting to git diffs',
    author='Andrew Sutton',
    author_email='me@andrewcsutton.com',
    url='https://github.com/Met48/diff-highlight-tokens',
    packages=find_packages(),
    install_requires=[
        'pygments>=2.1'
    ],
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
