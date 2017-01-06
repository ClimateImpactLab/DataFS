'''

This tutorial demonstrates reading and writing files to remote archives using
on-disk I/O operations.

To demonstrate this, we make use of the :py:mod:`xarray` module, which cannot
read from a streaming object.

Set up the workspace
--------------------

.. code-block:: python

    >>> from datafs import DataAPI
    >>> from datafs.managers.manager_mongo import MongoDBManager
    >>> from fs.s3fs import S3FS

Initialize the API

.. code-block:: python

    >>> api = DataAPI(
    ...      username='My Name',
    ...      contact = 'my.email@example.com')
    >>>
    >>> manager = MongoDBManager(
    ...     database_name = 'MyDatabase',
    ...     table_name = 'DataFiles')
    >>>
    >>> manager.create_archive_table('DataFiles', raise_on_err=False)
    >>>
    >>> api.attach_manager(manager)


Attach a remote service
~~~~~~~~~~~~~~~~~~~~~~~

In this example we'll use a remote file system, in this case AWS S3. This
filesystem returns streaming objects returned by ``boto`` or ``request`` calls.


    >>> s3 = S3FS(
    ...     'test-bucket',
    ...     aws_access_key='MY_KEY',
    ...     aws_secret_key='MY_SECRET_KEY')
    >>>
    >>> api.attach_authority('aws', s3)
    >>>
    >>> var = api.create(
    ...     'streaming_archive',
    ...     metadata = dict(description = 'My test data archive'))
    >>>


Create sample data
~~~~~~~~~~~~~~~~~~


Create a sample dataset (from the
`xarray docs <http://xarray.pydata.org/en/stable/examples/weather-data.html>`_):

.. code-block:: python

    >>> import xarray as xr
    >>> import numpy as np
    >>> import pandas as pd
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
    >>> ds.attrs['version'] = 'version 1'

Upload the dataset to the archive

.. code-block:: python

    >>> with var.get_local_path() as f:
    ...     ds.to_netcdf(f)
    ...

Read and write to disk
----------------------

NetCDF files cannot be read from a streaming object:

.. code-block:: python

    >>> with var.open() as f:
    ...     print(type(f))
    ...
    <type '_io.TextIOWrapper'>

.. code-block:: python

    >>> with var.open() as f:           # doctest: +ELLIPSIS
    ...     with xr.open_dataset(f) as ds:
    ...         print(ds)
    Traceback (most recent call last):
    ...
    UnicodeDecodeError: 'utf8' codec can't decode byte 0x89 in position 0: invalid start byte


Instead, we can get a local path to open:

.. code-block:: python

    >>> with var.get_local_path() as f:
    ...     with xr.open_dataset(f) as ds:
    ...         print(ds)
    ...
    <xarray.Dataset>
    Dimensions:   (location: 3, time: 731)
    Coordinates:
      * location  (location) |S2 'IA' 'IN' 'IL'
      * time      (time) datetime64[ns] 2000-01-01 2000-01-02 2000-01-03 ...
    Data variables:
        tmax      (time, location) float64 12.98 3.31 6.779 0.4479 6.373 4.843 ...
        tmin      (time, location) float64 -8.037 -1.788 -3.932 -9.341 -6.558 ...
    Attributes:
        version: version 1

We can update file in the same way:

.. code-block:: python

    >>> with var.get_local_path() as f:
    ...     with xr.open_dataset(f) as ds:
    ...
    ...         # Load the dataset fully into memory and then close the file
    ...
    ...         dsmem = ds.load()
    ...         ds.close()
    ...
    ...     # Update the version and save the file
    ...
    ...     dsmem.attrs['version'] = 'version 2'
    ...     dsmem.to_netcdf(f)
    ...

Now let's open the file and see if our change was saved:

.. code-block:: python

    >>> # Acquire the file from the archive and print the version
    ... with var.get_local_path() as f:
    ...     with xr.open_dataset(f) as ds:
    ...         print(ds)
    ...
    <xarray.Dataset>
    Dimensions:   (location: 3, time: 731)
    Coordinates:
      * location  (location) |S2 'IA' 'IN' 'IL'
      * time      (time) datetime64[ns] 2000-01-01 2000-01-02 2000-01-03 ...
    Data variables:
        tmax      (time, location) float64 12.98 3.31 6.779 0.4479 6.373 4.843 ...
        tmin      (time, location) float64 -8.037 -1.788 -3.932 -9.341 -6.558 ...
    Attributes:
        version: version 2



Cleaning up
~~~~~~~~~~~

.. code-block:: python

    >>> var.delete()
    >>> api.manager.delete_table('DataFiles')

'''
