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


DataFS is an abstraction layer for data storage systems. It manages file versions and metadata using document-based storage systems (for now it supports DynamoDB and MongoDB) and relies on PyFilesystem to abstract file storage, allowing you to store files locally and on the cloud in a seamless interface.


* Free software: MIT license
* Documentation: https://datafs.readthedocs.io.

Features
--------

* Explicit version and metadata management for teams
* Unified read/write interface across file systems
* Easily create out-of-the-box configuration files for users



Usage
-----

DataFS is built on the concept of "archives," which are like files but with some additional features. Archives can track versions explicitly, can live on remote servers, and can be cached locally.

To interact with DataFS, you need to create an API object. This can be done in a number of ways, both within python and using spec files to allow users to use archives out of the box. See `specifying DataAPI objects <http://datafs.readthedocs.io/en/latest/usage.api.specification.html>`_ for more detail.

We'll assume we already have an API object created. Once you have this, you can start using DataFS to create and use archives:

.. code-block:: python

    >>> my_archive = api.create_archive('my_archive', description = 'test data')
    >>> my_archive.metadata
    {'description': 'test data'}

Archives can be read from and written to much like a normal file:

.. code-block:: python

    >>> with my_archive.open('w+') as f:
    ...     f.write(u'test archive contents')
    ...
    >>> with my_archive.open('r') as f:
    ...     print(f.read())
    ...
    test archive contents
    >>>
    >>> with my_archive.open('w+') as f:
    ...     f.write(u'new archive contents')
    ...
    >>> with my_archive.open('r') as f:
    ...     print(f.read())
    ...
    new archive contents

By default, archives track versions explicitly. This can be turned off (such that old versions can be overwritten) using the flag ``versioned=False`` in ``create_archive``. Version ``patch`` is bumped by default, but this can be overridden with the ``bumpversion`` argument on any write operations:

.. code-block:: python

    >>> my_archive.versions
    ['0.0.1', '0.0.2']
    >>>
    >>> with my_archive.open('w+', bumpversion='major') as f:
    ...     f.write(u'a major improvement')
    ...
    >>> my_archive.versions
    ['0.0.1', '0.0.2', '1.0']

We can also retrieve versioned data specifically:

.. code-block:: python

    >>> with my_archive.open('r', version='0.0.2') as f:
    ...     print(f.read())
    ...
    new archive contents
    >>>
    >>> with my_archive.open('r', version='1.0') as f:
    ...     print(f.read())
    ...
    a major improvement
    >>>

See `examples <http://datafs.readthedocs.io/en/latest/examples.html>`_ for more extensive use cases.

Todo
----

See `issues <https://github.com/ClimateImpactLab/DataFS/issues>`_ to see and add to our todos.


Credits
---------

This package was created by `Justin Simcock <https://github.com/jgerardsimcock>`_ and `Michael Delgado <https://github.com/delgadom>`_ of the `Climate Impact Lab <http://impactlab.org>`_. Check us out on `github <https://github.com/ClimateImpactLab>`_.

Thanks also to `audreyr <https://github.com/audreyr>`_ for the wonderful `cookiecutter <https://github.com/audreyr/cookiecutter-pypackage>`_ package, and to `pyup <https://pyup.io>`_, a constant source of inspiration and our third contributor.