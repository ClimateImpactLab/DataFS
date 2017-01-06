=========================================
DataFS Distributed Data Management System
=========================================


.. image:: https://img.shields.io/pypi/v/datafs.svg
        :target: https://pypi.python.org/pypi/datafs

.. image:: https://travis-ci.org/ClimateImpactLab/DataFS.svg?branch=master
        :target: https://travis-ci.org/ClimateImpactLab/DataFS?branch=master

.. image:: https://coveralls.io/repos/github/ClimateImpactLab/DataFS/badge.svg?branch=master
        :target: https://coveralls.io/github/ClimateImpactLab/DataFS?branch=master

.. image:: https://readthedocs.org/projects/datafs/badge/?version=latest
        :target: https://datafs.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/climateimpactlab/datafs/shield.svg
     :target: https://pyup.io/repos/github/climateimpactlab/datafs/
     :alt: Updates


DataFS is pip for data. It manages file versions, dependencies, and metadata for individual use or large organizations.

Configure and connect to a metadata `Manager <http://datafs.readthedocs.io/en/latest/configure.manager.html>`_ and multiple data `Services <http://datafs.readthedocs.io/en/latest/configure.authorities.html>`_ using a specification file and you'll be sharing, tracking, and using your data in seconds.


* Free software: MIT license
* Documentation: https://datafs.readthedocs.io.


Features
--------

* Explicit version and metadata management for teams
* Unified read/write interface across file systems
* Easily create out-of-the-box configuration files for users
* Track data dependencies and usage logs
* Use datafs from python or from the command line


Usage
-----

First, `configure an API <http://datafs.readthedocs.io/en/latest/configure.html>`_. Don't worry. It's not too bad.

We'll assume we already have an API object created. Once you have this, you can start using DataFS to create and use archives.

.. code-block:: bash

    $ datafs create_archive my_new_data_archive --description "a test archive"
    created versioned archive <DataArchive local://my_new_data_archive>
    
    $ echo "file contents" >> my_file.txt
    
    $ datafs update my_new_data_archive my_file.txt
    
    $ echo "updated contents" >> my_file.txt
    
    $ datafs update my_new_data_archive --bumpversion minor
    
    $ python -m datafs.datafs --profile test delete my_new_data_archive
    deleted archive <DataArchive local://my_new_data_archive>

See `examples <http://datafs.readthedocs.io/en/latest/examples.html>`_ for more extensive use cases.



Installation
------------

``pip install datafs``


Additionally, you'll need to choose a manager and services:

Managers:

* MongoDB: ``pip install pymongo``
* DynamoDB: ``pip install boto3``

Services:

* Ready out-of-the-box:

  - local
  - shared
  - mounted
  - zip
  - ftp
  - http/https
  - in-memory

* Requiring additional packages:

  - AWS/S3: ``pip install boto``
  - SFTP: ``pip install paramiko``
  - HTTP/HTTPS: ``pip install requests``


Requirements
------------

For now, DataFS requires python 2.7. We're working on 3x support.


Todo
----

See `issues <https://github.com/ClimateImpactLab/DataFS/issues>`_ to see and add to our todos.


Credits
---------

This package was created by `Justin Simcock <https://github.com/jgerardsimcock>`_ and `Michael Delgado <https://github.com/delgadom>`_ of the `Climate Impact Lab <http://impactlab.org>`_. Check us out on `github <https://github.com/ClimateImpactLab>`_.

Major kudos to the folks at `PyFilesystem <https://github.com/PyFilesystem>`_. Thanks also to `audreyr <https://github.com/audreyr>`_ for the wonderful `cookiecutter <https://github.com/audreyr/cookiecutter-pypackage>`_ package, and to `Pyup <https://pyup.io>`_, a constant source of inspiration and our silent third contributor.