'''
.. _snippets-pythonapi-io:

Python API: Reading and Writing
===============================

This is the tested source code for the snippets used in
:ref:`pythonapi-io`. The config file we're using in this example
can be downloaded :download:`here <../examples/snippets/resources/datafs.yml>`.


Setup
-----

.. code-block:: python

    >>> import datafs
    >>> from fs.tempfs import TempFS

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

Displayed example 1 code:

.. EXAMPLE-BLOCK-1-START

.. code-block:: python

    >>> api.create(
    ...     'sample_archive',
    ...     metadata={'description': 'metadata for your archive'})
    ...
    <DataArchive local://sample_archive>

.. EXAMPLE-BLOCK-1-END



Example 2
---------

.. EXAMPLE-BLOCK-2-START

.. code-block:: python

    >>> with open('sample.txt', 'w+') as f:
    ...     f.write('this is a sample archive')
    ...

.. EXAMPLE-BLOCK-2-END


Example 3
---------

.. EXAMPLE-BLOCK-3-START

.. code-block:: python

    >>> sample_var = api.get_archive('sample_archive')
    >>> sample_var.update('sample.txt')

.. EXAMPLE-BLOCK-3-END



Example 4
---------

.. EXAMPLE-BLOCK-4-START

.. code-block:: python

    >>> with sample_var.open('r') as f:
    ...     print(f.read())
    ...
    this is a sample archive

.. EXAMPLE-BLOCK-4-END


Example 5
---------

.. EXAMPLE-BLOCK-5-START

.. code-block:: python

    >>> with open('sample.txt', 'w+') as f:
    ...     f.write('this is a sample archive with some more information')
    ...
    >>> sample_var.update('sample.txt')


.. EXAMPLE-BLOCK-5-END


Example 6
---------

.. EXAMPLE-BLOCK-6-START

.. code-block:: python

    >>> with sample_var.open('r') as f:
    ...     print(f.read())
    ...
    this is a sample archive with some more information


.. EXAMPLE-BLOCK-6-END


Example 7
---------

.. code-block:: python

    >>> import os
    >>> with open('sample.txt', 'w+') as f:
    ...        f.write(u'Local file to update to our FS')
    ...



.. EXAMPLE-BLOCK-7-START

.. code-block:: python

    >>> sample_var.update('sample.txt')

.. EXAMPLE-BLOCK-7-END


 Example 8
 ---------


.. EXAMPLE-BLOCK-8-START

.. code-block:: python

    >>> sample_archive_local = api.get_archive('sample_archive')
    >>> sample_archive_local.download('path_to_sample.txt', version='latest')

.. EXAMPLE-BLOCK-8-END


Example 9
---------

.. EXAMPLE-BLOCK-9-START

.. code-block:: python

    >>> with open('path_to_sample.txt', 'r') as f:
    ...     print(f.read())
    ...
    Local file to update to our FS

.. EXAMPLE-BLOCK-9-END


Teardown
---------

.. code-block:: python

    >>> try:
    ...     api.delete_archive('sample_archive')
    ... except (KeyError, OSError):
    ...     pass
    ...
    >>> os.remove('path_to_sample.txt')
    >>> os.remove('sample.txt')


.. EXAMPLE-BLOCK-10-START

.. code-block:: python

    >>> import numpy as np
    >>> import pandas as pd
    >>> import xarray as xr
    >>>
    >>> np.random.seed(123)
    >>>
    >>> times = pd.date_range('2000-01-01', '2001-12-31', name='time')
    >>> annual_cycle = np.sin(2 * np.pi * (times.dayofyear / 365.25 - 0.28))
    >>>
    >>> base = 10 + 15 * annual_cycle.reshape(-1, 1)
    >>> tmin_values = base + 3 * np.random.randn(annual_cycle.size, 3)
    >>> tmax_values = base + 10 + 3 * np.random.randn(annual_cycle.size, 3)
    >>>
    >>> ds = xr.Dataset({'tmin': (('time', 'location'), tmin_values),
    ...                  'tmax': (('time', 'location'), tmax_values)},
    ...                 {'time': times, 'location': ['IA', 'IN', 'IL']})
    >>>
    >>>
    >>>
    >>> streaming_archive = api.create(
    ...     'streaming_archive',
    ...     metadata={'description': 'metadata description for your archive'})
    ...
    >>> with streaming_archive.get_local_path() as f:
    ...        ds.to_netcdf(f)
    ...
    >>>
    >>>

.. EXAMPLE-BLOCK-10-END


.. EXAMPLE-BLOCK-11-START

.. code-block:: python

    >>> with streaming_archive.get_local_path() as f:
    ...     with xr.open_dataset(f) as ds:
    ...         print(ds) # doctest: +ELLIPSIS
    ...
    <xarray.Dataset>
    Dimensions:   (location: 3, time: 731)
    Coordinates:
      * location  (location) |S2 'IA' 'IN' 'IL'
      * time      (time) datetime64[ns] 2000-01-01 2000-01-02 2000-01-03 ...
    Data variables:
        tmax      (time, location) float64 12.98 3.31 6.779 0.4479 6.373 ...
        tmin      (time, location) float64 -8.037 -1.788 -3.932 -9.341 ...


.. EXAMPLE-BLOCK-11-END

'''
