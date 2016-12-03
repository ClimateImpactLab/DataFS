#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'fs==0.5.4'
]

test_requirements = [
    'pip==9.0.1',
    'watchdog==0.8.3',
    'flake8==3.2.0',
    'tox==2.5.0',
    'coverage==4.2',
    'cryptography==1.5.3',
    'PyYAML==3.12',
    'pytest==3.0.4',
    'fs==0.5.4',
    'pymongo==3.3.1'
]

setup(
    name='datafs',
    version='0.2.2',
    description="DataFS is an abstraction layer for data storage systems. It manages file versions and metadata using a json-like storage system like AWS's DynamoDB and relies on PyFilesystem to abstract file storage, allowing you to store files locally and on the cloud in a seamless interface.",
    long_description=readme + '\n\n' + history,
    author="Climate Impact Lab",
    author_email='jsimcock@rhg.com',
    url='https://github.com/ClimateImpactLab/datafs',
    packages=[
        'datafs',
    ],
    package_dir={'datafs':
                 'datafs'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='datafs',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3'
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
