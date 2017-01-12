#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt', 'r') as req:
    requirements_install = [l.strip() for l in req.readlines() if l.strip() != '']

with open('requirements_test.txt', 'r') as req:
    requirements_test = [l.strip() for l in req.readlines() if l.strip() != '']

with open('requirements_links.txt', 'r') as req:
    dependency_links = [l.strip() for l in req.readlines() if l.strip() != '']

extras = {
    'test': requirements_test
}


entry_points = '[console_scripts]\ndatafs=datafs.datafs:cli'

setup(
    name='datafs',
    version='0.6.5',
    description="DataFS is an abstraction layer for data storage systems. It manages file versions and metadata using a json-like storage system like AWS's DynamoDB and relies on PyFilesystem to abstract file storage, allowing you to store files locally and on the cloud in a seamless interface.",
    long_description=readme + '\n\n' + history,
    author="Climate Impact Lab",
    url='https://github.com/ClimateImpactLab/datafs',
    packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*', 'tests', 'docs', 'examples']),
    package_dir={'datafs':
                 'datafs'},
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
        'Programming Language :: Python :: 2.7'
    ],
    test_suite='tests',
    tests_require=requirements_test,
    extras_require=extras,
    dependency_links = dependency_links
)
