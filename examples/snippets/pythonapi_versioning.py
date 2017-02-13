'''
.. _snippets-pythonapi-versioning:

Python API: Versioning Data
===========================

This is the tested source code for the snippets used in
:ref:`pythonapi-versioning`. The config file we're using in this example
can be downloaded :download:`here <../examples/snippets/resources/datafs.yml>`.

SetUp
-----

.. code-block:: python

    >>> import datafs
    >>> from fs.tempfs import TempFS
    >>> import os

We test with the following setup:

.. code-block:: python

    >>> api = datafs.get_api(
    ...     config_file='examples/snippets/resources/datafs.yml')
    ...

This assumes that you have a config file at the above location. The config file
we're using in this example can be downloaded
:download:`here <../examples/snippets/resources/datafs.yml>`.

clean up any previous test failures

.. code-block:: python

    >>> try:
    ...     api.delete_archive('sample_archive')
    ... except (KeyError, OSError):
    ...     pass
    ...
    >>> try:
    ...     api.manager.delete_table('DataFiles')
    ... except KeyError:
    ...     pass
    ...

Add a fresh manager table:

.. code-block:: python

    >>> api.manager.create_archive_table('DataFiles')


Example 1
---------

.. EXAMPLE-BLOCK-1-START


.. code-block:: python

    >>> with open('sample_archive.txt', 'w+', ) as f:
    ...     f.write(u'this is a sample archive')
    ...
    >>> sample_archive = api.create(
    ...     'sample_archive',
    ...     metadata = {'description': 'metadata description'})
    ...
    >>> sample_archive.update('sample_archive.txt', prerelease='alpha')

.. EXAMPLE-BLOCK-1-END

cleanup:

.. code-block:: python

    >>> os.remove('sample_archive.txt')


Example 2
---------

.. EXAMPLE-BLOCK-2-START

.. code-block:: python

    >>> sample_archive.get_versions()
    [BumpableVersion ('0.0.1a1')]

.. EXAMPLE-BLOCK-2-END



Example 3
---------

.. EXAMPLE-BLOCK-3-START

.. code-block:: python

    >>> with open('sample_archive.txt', 'w+', ) as f:
    ...     f.write(u'Sample archive with more text so we can bumpversion')
    ...
    >>>
    >>> sample_archive.update('sample_archive.txt', bumpversion='minor')
    >>> sample_archive.get_versions()
    [BumpableVersion ('0.0.1a1'), BumpableVersion ('0.1')]

.. EXAMPLE-BLOCK-3-END

cleanup:

.. code-block:: python

    >>> os.remove('sample_archive.txt')


Example 4
---------

.. EXAMPLE-BLOCK-4-START

.. code-block:: python

    >>> sample_archive.get_latest_version()
    BumpableVersion ('0.1')

.. EXAMPLE-BLOCK-4-END


Example 5
---------

.. EXAMPLE-BLOCK-5-START

.. code-block:: python

    >>> sample_archive.get_latest_hash()
    u'510d0e2eadd19514788e8fdf91e3bd5c'

.. EXAMPLE-BLOCK-5-END


Example 6
---------

.. EXAMPLE-BLOCK-6-START

.. code-block:: python

    >>> sample_archive1 = api.get_archive(
    ...     'sample_archive',
    ...     default_version='0.0.1a1')
    ...
    >>> with sample_archive1.open('r') as f:
    ...    print(f.read())
    ...
    Sample archive with more text so we can bumpversion

.. EXAMPLE-BLOCK-6-END


Teardown
---------

.. code-block:: python

    >>> try:
    ...     api.delete_archive('sample_archive')
    ... except (KeyError, OSError):
    ...     pass
    ...

'''
