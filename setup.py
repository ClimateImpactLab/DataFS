#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


with open('requirements.txt', 'r') as req:
    requirements = [req for req in req.readlines() if '==' in req]

with open('requirements.txt', 'r') as req:
    dependency_links = [req for req in req.readlines() if 'http' in req]

with open('requirements_test.txt', 'r') as req:
    test_requirements = [req for req in req.readlines() if '==' in req]

with open('entry_points.cfg', 'r') as e:
    entry_points = e.read()

setup(
    name='datafs',
    version='0.5.0',
    description="DataFS is an abstraction layer for data storage systems. It manages file versions and metadata using a json-like storage system like AWS's DynamoDB and relies on PyFilesystem to abstract file storage, allowing you to store files locally and on the cloud in a seamless interface.",
    long_description=readme + '\n\n' + history,
    author="Climate Impact Lab",
    url='https://github.com/ClimateImpactLab/datafs',
    packages=find_packages(exclude=['*.tests', '*.tests.*', 'tests.*', 'tests', 'docs', 'examples']),
    package_dir={'datafs':
                 'datafs'},
    include_package_data=True,
    install_requires=requirements,
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
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    dependency_links = [
    'git+https://github.com/PyFilesystem/pyfilesystem.git@c94b20c877f1f2ab190d7b1eae3ecc53b3a6d295#egg=pyfilesystem'
    ]
)
