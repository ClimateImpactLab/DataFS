.. _pythonapi-finding-archives:


==============================
Searching and Finding Archives
==============================


DataFS allows you to search and locate archives with the following methods: 
:py:meth:`~datafs.DataAPI.listdir`, :py:meth:`~datafs.DataAPI.filter`, and :py:meth:`~datafs.DataAPI.search`. Let's look at each method to see how they work. 

Using :py:meth:`~datafs.DataAPI.listdir`
----------------------------------------

:py:meth:`~datafs.DataAPI.listdir` works just like typlical unix style ``ls`` in the sense that it returns all objects subordinate to the specified directory. If your team has used ``/`` to organize archive naming then you can explore the archive namespace just as you would explore a directory in a filesystem.

For example if we provide ``impactlab/conflict/global`` as an argument to ``listdir`` we get the following. 

.. include:: ../examples/snippets/pythonapi_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-1-START
    :end-before: .. EXAMPLE-BLOCK-1-END

Let's see what kind of archives we have in our system. 

.. include:: ../examples/snippets/pythonapi_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-2-START
    :end-before: .. EXAMPLE-BLOCK-2-END

Then if we use ``impactlab`` as an argument we see that we have several groupings below this. 

.. include:: ../examples/snippets/pythonapi_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-3-START
    :end-before: .. EXAMPLE-BLOCK-3-END

Let's explore ``conflict`` to see what kind of namespace groupings we have in there. 

.. include:: ../examples/snippets/pythonapi_finding_archives.py
	:start-after: .. EXAMPLE-BLOCK-4-START
	:end-before: .. EXAMPLE-BLOCK-4-END

OK. Just one. Now let's have a look inside the ``impactlab/conflict/global`` namespace. 

.. include:: ../examples/snippets/pythonapi_finding_archives.py
	:start-after: .. EXAMPLE-BLOCK-5-START
	:end-before: .. EXAMPLE-BLOCK-5-END

We see that if we give a full path with a file extension that we get version numbers of our archives. 

Using :py:meth:`~datafs.DataAPI.filter`
---------------------------------------

DataFS also lets you filter so you can limit the search space on archive names. With :py:meth:`~datafs.DataAPI.filter` you can use the ``prefix``, ``path``, ``str``, and ``regex`` pattern options to filter archives.
Let's look at using the prefix ``project1_variable1_`` which corresponds to the ``prefix`` option, the beginning string of a set of archive names. Let's also see how many archives we have in total by filtering without arguments. 

.. include:: ../examples/snippets/pythonapi_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-6-START
    :end-before: .. EXAMPLE-BLOCK-6-END

We see there are 125. By filtering with our prefix we can significantly reduce the number of archives we are looking at. 

We can also filter on ``path``. In this case we want to filter all NetCDF files that match a specific pattern. We need to set our ``engine`` value to ``path`` and put in our search pattern. 

.. include:: ../examples/snippets/pythonapi_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-7-START
    :end-before: .. EXAMPLE-BLOCK-7-END


We can also filter archives with archive names containing a specific string by setting ``engine`` to ``str``. In this
example we want all archives with the string ``variable2``. The filtering query returns 25 items. Let's look at the first few. 

.. include:: ../examples/snippets/pythonapi_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-8-START
    :end-before: .. EXAMPLE-BLOCK-8-END


Using :py:meth:`~datafs.DataAPI.search`
---------------------------------------


DataFS :py:meth:`~datafs.DataAPI.search` capabilites are enabled via tagging of archives. The arguments of the :py:meth:`~datafs.DataAPI.search` method are tags associated with a given archive. If archives are not tagged, they cannot be searched with the :py:meth:`~datafs.DataAPI.search` method. 

If we use :py:meth:`~datafs.DataAPI.search` without arguments, it is the same implementation as :py:meth:`~datafs.DataAPI.filter` without arguments. 

Let's see this in action. 


.. include:: ../examples/snippets/pythonapi_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-9-START
    :end-before: .. EXAMPLE-BLOCK-9-END

Our archives have been tagged with ``team1``, ``team2``, or ``team3`` Let's search for some archives with tag ``team3``.  

.. include:: ../examples/snippets/pythonapi_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-10-START
    :end-before: .. EXAMPLE-BLOCK-10-END

It brings back 41 archives. So we'll just look at a few


And lets look at the some of these archives to see what their tags are. We'll use
:py:meth:`~datafs.core.data_archive.DataArchive.get_tags`

.. include:: ../examples/snippets/pythonapi_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-12-START
    :end-before: .. EXAMPLE-BLOCK-12-END


And how about with tag ``team1``. We see that there are 42 archives with ``team1`` tag. 

.. include:: ../examples/snippets/pythonapi_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-12-START
    :end-before: .. EXAMPLE-BLOCK-12-END

And let's use :py:meth:`~datafs.core.data_archive.DataArchive.get_tags` to confirm the tags are ``team1``

.. include:: ../examples/snippets/pythonapi_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-13-START
    :end-before: .. EXAMPLE-BLOCK-13-END



If you have improvements or suggestions for the documentation please consider making contributions. 




