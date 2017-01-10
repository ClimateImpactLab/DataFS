.. _pythonapi-io:

=========================
Reading and Writing Files
=========================


Writing Archive Files
---------------------

To write to a file in DataFS you'll first need to create the archive. We'll assume you've already set up your api with manager, and authorities. We'll use :py:meth:`~datafs.DataAPI.create`.


.. code-block:: python

    >>> api.create('sample_archive', metadata=dict(description='metadata for your archive'))
    >>> <DataArchive fs://sample_archive>



DataFS needs a file path in order to update files. So now that we have an archive on our manager, we can create a file and put it up in our filesystem. So let's first create a file called ``sample.txt``. 

.. code-block:: python

    >>> with open('sample.txt', 'w+') as f:
    ...     f.write('this is a sample archive')


Now that we have a file can we can use the ``update()`` method to upload our file. Depending on size of file and network speeds, there may be some latency when calling :py:meth:`~datafs.core.data_archive_DataArchive.update`. 


.. code-block:: python
	
	>>> sample_var = api.get_archive('sample_archive')
	>>> sample_var.update('sample.txt')


Now that our archive is up let's say we want to now pull it down and read it. Reading an archive file is 
an interface the python users will recognize. We initialize a context manager using the ``with`` statement. 
The actual call happens through :py:meth:`~datafs.core.data_archive.DataArchive.open`

.. code-block:: python
	
	>>> with sample_var.open('r') as f:
	... 	print(f.read())

	>>> this is a sample archive


This is really great. Let's see what happens when we want to make some updates to the file. 


.. code-block:: python

	>>> with open('sample.txt', 'w+') as f:
	... 	f.write('this is a sample archive with some more information')

	>>> sample_var.update('sample.txt')

Now let's read open and read to see. 

.. code-block:: python

	>>> with sample_var.open('r') as f:
	... 	print(f.read())

	>>> this is a sample archive with some more information

Looks good!


Since DataFS simply needs a filepath, you can simply provide a filepath and it will upload and write the file. If you have a file locally that you want managed by DataFS you can create an archive and put it on your filesystem. 


.. code-block:: python

	>>> sample_archive = api.create('sample_archive', metadata=dict(description='metadata for your archive'))
	>>> <DataArchive fs://sample_archive>
	>>> sample_archive.update('~/path/to/sample_archive.txt')




Downloading
-----------

If you want to download the latest version of an archive all you need to do is provide a path and set ``version='latest'``. This will download the latest version to the filepath specified. We'll use :py:meth:`~datafs.core.data_archive.DataArchive.get_archive` to get the archive and then use :py:meth:`~datafs.core.data_archive.DataArchive.download`


.. code-block:: python

	>>> sample_archive = api.get_archive('sample_archive')
	>>> sample_archive.download('~/path/to/local/data/directory/sample.txt', version='latest')

Let's just double check that we indeed have our file

.. code-block:: python

	>>> with open('~/path/to/local/data/directory/sample.txt', 'r') as f:
	... 	print(f.read())

	>>> this is a sample archive with some more information





Writing Streaming Objects
-------------------------


If you are working with certain packages like pandas, or xarray that need a filepath, the interaction is slightly modified from typical file objects. Let's first create the dataset we want to write to. The method we'll use for this operation is 
:py:meth:`datafs.core.DataArchive.get_local_path` and xarray's `open_dataset <http://xarray.pydata.org/en/stable/generated/xarray.open_dataset.html>`_ method


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
	>>>
	>>>
	>>> streaming_archive = api.create('streaming_archive', dict(metadata='metadata description for your archive'))
	>>> DataArchive fs://streaming_archive>
	>>>
	>>> with streaming_archive.get_local_path() as f:
	...		ds.to_netdcdf(f)
	

Downloading Streaming Objects
-----------------------------

Now reading a streaming object is similar a regular file object but generate a file path that is 
then passed to the package you are using for reading and writing. In this case we are using xarray so we'll use our 
:py:meth:`~datafs.core.data_archive.DataArchive.get_local_path` and xarray's `open_dataset <http://xarray.pydata.org/en/stable/generated/xarray.open_dataset.html>`_ method

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



Check out :ref:`examples` for more information on how to write and read files DataFS on different filesystems





