#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements_install = [
    'click>=6.0',
    'PyYAML>=3.0',
    'fs1>=0.6',
    'whoosh>=2.6'
    ]

requirements_test = [
    'pip>=8.0',
    'wheel>=0.28',
    'flake8>=3.0',
    'tox>=2.1',
    'coverage>=4.0',
    'pytest>=3.0',
    'pytest_cov>=2.0',
    'Sphinx>=1.2',
    'sphinx_rtd_theme>=0.1',
    'moto>=0.4',
    'pymongo>=3.0',
    'boto3>=1.2'
    ]

extras = {
    'test': requirements_test
}


entry_points = '[console_scripts]\ndatafs=datafs.datafs:cli'

setup(
    name='datafs',
    version='0.6.6',
    description="DataFS is an abstraction layer for data storage systems. It manages file versions and metadata using a json-like storage system like AWS's DynamoDB and relies on PyFilesystem to abstract file storage, allowing you to store files locally and on the cloud in a seamless interface.",
    long_description=readme + '\n\n' + history,
    author="Climate Impact Lab",
    url='https://github.com/ClimateImpactLab/datafs',
    packages=find_packages(
        exclude=[
            '*.tests',
            '*.tests.*',
            'tests.*',
            'tests',
            'docs',
            'examples']),
    package_dir={
        'datafs': 'datafs'},
    include_package_data=True,
    install_requires=requirements_install,
    entry_points=entry_points,
    license="MIT license",
    zip_safe=False,
    keywords='datafs',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7'],
    test_suite='tests',
    tests_require=requirements_test,
    extras_require=extras)
