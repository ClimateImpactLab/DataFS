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
    >>> import itertools

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
	
	>>> api.listdir('impactlab/conflict/global')
	[u'conflict_global_daily.csv']

.. EXAMPLE-BLOCK-1-END

Example 2
---------

Displayed example 2 code

.. EXAMPLE-BLOCK-2-START

.. code-block:: python
	
	>>> api.listdir('')
	[u'impactlab']

.. EXAMPLE-BLOCK-2-END

Example 3
---------

Displayed example 3 code

.. EXAMPLE-BLOCK-3-START

.. code-block:: python
	
	>>> api.listdir('impactlab')
	[u'labor', u'climate', u'conflict', u'mortality']
	
.. EXAMPLE-BLOCK-3-END

Example 4
---------

Displayed example 4 code

.. EXAMPLE-BLOCK-4-START

.. code-block:: python
	
	>>> api.listdir('impactlab/conflict')
	[u'global']

.. EXAMPLE-BLOCK-4-END

Example 5
---------

Displayed example 5 code

.. EXAMPLE-BLOCK-5-START

.. code-block:: python
	
	>>> api.listdir('impactlab/conflict/global')
	[u'conflict_global_daily.csv']
	>>> api.listdir('impactlab/conflict/global/conflict_global_daily.csv')
	[u'0.0.1']

.. EXAMPLE-BLOCK-5-END

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



Filter example setup

.. code-block:: python

	>>> archive_names = []
    >>> for indices in itertools.product(*(range(1, 6) for _ in range(3))):
    ...		archive_name = ('project{}_variable{}_scenario{}.nc'.format(*indices))
    ... 	archive_names.append(archive_name)
    >>> for name in archive_names:
    ...		_ = api.create(name)
	





Example 6
---------

Displayed example 6 code

.. EXAMPLE-BLOCK-6-START

.. code-block:: python
>>> len(list(api.filter()))
125
>>> v1 = api.filter(prefix='project1_variable1_')
>>> list(v1)
[u'project1_variable1_scenario1.nc', u'project1_variable1_scenario2.nc', u'project1_variable1_scenario3.nc', u'project1_variable1_scenario4.nc', u'project1_variable1_scenario5.nc']
	
	
.. EXAMPLE-BLOCK-6-END


Example 7
---------

Displayed example 7 code

.. EXAMPLE-BLOCK-7-START

.. code-block:: python

>>> v2 = api.filter(pattern='*_variable4_scenario4.nc', engine='path')
>>> list(v2)
[u'project1_variable4_scenario4.nc', u'project2_variable4_scenario4.nc', u'project3_variable4_scenario4.nc', u'project4_variable4_scenario4.nc', u'project5_variable4_scenario4.nc']


.. EXAMPLE-BLOCK-7-END


Example 8
---------

Displayed example 8 code

.. EXAMPLE-BLOCK-8-START

.. code-block:: python

>>> v3 = list(api.filter(pattern='variable2', engine='str'))
>>> len(v3)
25
>>> v3[:4]
[u'project1_variable2_scenario1.nc', u'project1_variable2_scenario2.nc', u'project1_variable2_scenario3.nc', u'project1_variable2_scenario4.nc']


.. EXAMPLE-BLOCK-8-END


Example 9
---------

Displayed example 9 code

.. EXAMPLE-BLOCK-9-START

.. code-block:: python




.. EXAMPLE-BLOCK-9-END


Example 10
---------

Displayed example 10 code

.. EXAMPLE-BLOCK-10-START

.. code-block:: python

	>>> archives_search = list(api.search())
	>>> archives_filter = list(api.filter())
	>>> len(archives_search)
	125
	>>> len(archives_filter)
	125
.. EXAMPLE-BLOCK-10-END


Example 11
---------

Displayed example 11 code

.. EXAMPLE-BLOCK-11-START

.. code-block:: python




.. EXAMPLE-BLOCK-11-END





    >>> api.manager.delete_table('DataFiles')

'''
