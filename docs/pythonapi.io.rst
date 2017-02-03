.. _pythonapi-io:

=========================
Reading and Writing Files
=========================


View the source for the code samples on this page in :ref:`snippets-pythonapi-io`.

Writing Archive Files
---------------------

To write to a file in DataFS you'll first need to create the archive. We'll assume you've already set up your api with manager, and authorities. We'll use :py:meth:`~datafs.DataAPI.create`.


.. include:: ../examples/snippets/pythonapi_io.py
    :start-after: .. EXAMPLE-BLOCK-1-START
    :end-before: .. EXAMPLE-BLOCK-1-END



DataFS needs a file path in order to update files. So now that we have an archive on our manager, we can create a file and put it up in our filesystem. So let's first create a file called ``sample.txt``. 

.. include:: ../examples/snippets/pythonapi_io.py
    :start-after: .. EXAMPLE-BLOCK-2-START
    :end-before: .. EXAMPLE-BLOCK-2-END


Now that we have a file can we can use the ``update()`` method to upload our file. Depending on size of file and network speeds, there may be some latency when calling :py:meth:`~datafs.core.data_archive_DataArchive.update`. 


.. include:: ../examples/snippets/pythonapi_io.py
    :start-after: .. EXAMPLE-BLOCK-3-START
    :end-before: .. EXAMPLE-BLOCK-3-END


Now that our archive is up let's say we want to now pull it down and read it. Reading an archive file is 
an interface the python users will recognize. We initialize a context manager using the ``with`` statement. 
The actual call happens through :py:meth:`~datafs.core.data_archive.DataArchive.open`

.. include:: ../examples/snippets/pythonapi_io.py
    :start-after: .. EXAMPLE-BLOCK-4-START
    :end-before: .. EXAMPLE-BLOCK-4-END


This is really great. Let's see what happens when we want to make some updates to the file. 


.. include:: ../examples/snippets/pythonapi_io.py
    :start-after: .. EXAMPLE-BLOCK-5-START
    :end-before: .. EXAMPLE-BLOCK-5-END

Now let's open and read to see. 

.. include:: ../examples/snippets/pythonapi_io.py
    :start-after: .. EXAMPLE-BLOCK-6-START
    :end-before: .. EXAMPLE-BLOCK-6-END

Looks good!


Since DataFS simply needs a filepath, you can simply provide a filepath and it will upload and write the file. If you have a file locally that you want managed by DataFS you can create an archive and put it on your filesystem. 


.. include:: ../examples/snippets/pythonapi_io.py
    :start-after: .. EXAMPLE-BLOCK-7-START
    :end-before: .. EXAMPLE-BLOCK-7-END



Downloading
-----------

If you want to download the latest version of an archive all you need to do is provide a path and set ``version='latest'``. This will download the latest version to the filepath specified. We'll use :py:meth:`~datafs.core.data_archive.DataArchive.get_archive` to get the archive and then use :py:meth:`~datafs.core.data_archive.DataArchive.download`


.. include:: ../examples/snippets/pythonapi_io.py
    :start-after: .. EXAMPLE-BLOCK-8-START
    :end-before: .. EXAMPLE-BLOCK-8-END

Let's just double check that we indeed have our file

.. include:: ../examples/snippets/pythonapi_io.py
    :start-after: .. EXAMPLE-BLOCK-9-START
    :end-before: .. EXAMPLE-BLOCK-9-END





Writing Streaming Objects
-------------------------


If you are working with certain packages like pandas, or xarray that need a filepath, the interaction is slightly modified from typical file objects. Let's first create the dataset we want to write to. The method we'll use for this operation is 
:py:meth:`datafs.core.DataArchive.get_local_path` and xarray's `open_dataset <http://xarray.pydata.org/en/stable/generated/xarray.open_dataset.html>`_ method


.. include:: ../examples/snippets/pythonapi_io.py
    :start-after: .. EXAMPLE-BLOCK-10-START
    :end-before: .. EXAMPLE-BLOCK-10-END
	

Downloading Streaming Objects
-----------------------------

Now reading a streaming object is similar a regular file object but generate a file path that is 
then passed to the package you are using for reading and writing. In this case we are using xarray so we'll use our 
:py:meth:`~datafs.core.data_archive.DataArchive.get_local_path` and xarray's `open_dataset <http://xarray.pydata.org/en/stable/generated/xarray.open_dataset.html>`_ method


.. include:: ../examples/snippets/pythonapi_io.py
    :start-after: .. EXAMPLE-BLOCK-11-START
    :end-before: .. EXAMPLE-BLOCK-11-END

Check out :ref:`examples` for more information on how to write and read files DataFS on different filesystems





