'''
.. _snippets-pythonapi-finding-archives:

Python API: Searching and Finding Archives
==========================================

This is the tested source code for the snippets used in
:ref:`pythonapi-finding-archives`. The config file we're using in this example
can be downloaded :download:`here <../examples/snippets/resources/datafs.yml>`.


Setup
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
    ...     api.delete_archive('my_archive')
    ...     api.delete_archive('streaming_archive')
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

Set up some archives to search

.. code-block:: python


	>>> with open('test.txt', 'w') as f:
	...		f.write('test test')
    >>> tas_archive = api.create('impactlab/climate/tas/tas_daily_us.csv')
    >>> tas_archive.update('test.txt')
    >>> precip_archive = api.create('impactlab/climate/pr/pr_daily_us.csv')
    >>> precip_archive.update('test.txt')
    >>> socio = api.create('impactlab/mortality/global/mortality_global_daily.csv')
    >>> socio.update('test.txt')
    >>> socio1 = api.create('impactlab/conflict/global/conflict_global_daily.csv')
    >>> socio1.update('test.txt')
    >>> socio2 = api.create('impactlab/labor/global/labor_global_daily.csv')
    >>> socio2.update('test.txt')


Example 1
---------

Displayed example 1 code

.. EXAMPLE-BLOCK-1-START

.. code-block:: python
	
	>>> api.listdir('')
	[u'impactlab', u'my_archive', u'sample_archive', u'streaming_archive']

.. EXAMPLE-BLOCK-1-END

Example 2
---------

Displayed example 2 code

.. EXAMPLE-BLOCK-2-START

.. code-block:: python
	
	>>> api.listdir('impactlab')
	[u'climate', u'conflict', u'labor', u'mortality']
	
.. EXAMPLE-BLOCK-2-END

Example 3
---------

Displayed example 3 code

.. EXAMPLE-BLOCK-3-START

.. code-block:: python
	
	>>> api.listdir('impactlab/conflict')
	[u'global']

.. EXAMPLE-BLOCK-3-END

Example 4
---------

Displayed example 4 code

.. EXAMPLE-BLOCK-4-START

.. code-block:: python
	
	>>> api.listdir('impactlab/conflict/global')
	[u'conflict_global_daily.csv']
	>>> api.listdir('impactlab/conflict/global/conflict_global_daily.csv')
	[u'0.0.1']

.. EXAMPLE-BLOCK-4-END


Teardown
--------

.. code-block:: python

    >>> try:
    ...     tas_archive.delete()
    ...     precip_archive.delete()
    ...     socio.delete()
    ...     socio1.delete()
    ...     socio2.delete()
    ...     os.remove('test.txt')
    ... except KeyError:
    ...     pass
    ...

    >>> api.manager.delete_table('DataFiles')

'''
