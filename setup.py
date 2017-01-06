#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


requirements_install = [
    'click==6.6',
    'PyYAML==3.12'
]

dependency_links = [
    'git+https://github.com/PyFilesystem/pyfilesystem.git@c94b20c877f1f2ab190d7b1eae3ecc53b3a6d295#egg=pyfilesystem']

requirements_test = [
    'pip==9.0.1',
    'wheel==0.29.0',
    'flake8==3.2.1',
    'tox==2.5.0',
    'coverage==4.3.1',
    'pytest==3.0.5',
    'pytest_cov==2.4.0',
    'Sphinx==1.5.1',
    'sphinx_rtd_theme==0.1.10a0',
    'moto==0.4.30',
    'pymongo==3.4.0',
    'boto3==1.4.3'
]

extras = {
    'test': requirements_test
}


entry_points = '[console_scripts]\ndatafs=datafs.datafs:cli'

setup(
    name='datafs',
    version='0.6.1',
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
