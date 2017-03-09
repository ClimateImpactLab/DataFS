#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
DataFS is an abstraction layer for data storage systems.

DataFS is a package manager for data. It manages file versions, dependencies,
and metadata for individual use or large organizations.
'''


from setuptools import setup, find_packages

description = __doc__

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements_install = [
    'click>=6.0',
    'PyYAML>=3.0',
    'fs==0.5.5a1'
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
    'boto3>=1.2',
    'clatter>=0.0.4'
    ]

extras = {
    'test': requirements_test
}


entry_points = '[console_scripts]\ndatafs=datafs.datafs:cli'

setup(
    name='datafs',
    version='0.7.0',
    description=description,
    long_description=readme,
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
    setup_requires=['pytest-runner'],
    tests_require=requirements_test,
    extras_require=extras)
