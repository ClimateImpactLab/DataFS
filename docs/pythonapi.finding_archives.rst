.. _pythonapi-finding-archives:


==============================
Searching and Finding Archives
==============================


DataFS allows you to search and locate archives with the following methods: 
:py:meth:`datafs.DataAPI.listdir`, :py:meth:`datafs.DataAPI.filter`, :py:meth:`datafs.DataAPI.search`. Let's look at each method to see how they work. 

Using `listdir`
---------------

:py:meth:`datafs.DataAPI.listdir` works just like typlical unix style `ls` in the sense that it returns all objects subordinate to the specified directory.

For example if we provide `impactlab/conflict/global` as an argument to `listdir` we get the following. 

.. include:: ../examples/snippets/pythonapi_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-1-START
    :end-before: .. EXAMPLE-BLOCK-1-END

If your team has used `/` to organize archive naming then you can explore the archive namespace just as you would explore a directory in a filesystem. Let's see what kind of archives we have in our system. 

.. include:: ../examples/snippets/pythonapi_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-2-START
    :end-before: .. EXAMPLE-BLOCK-2-END

Then if we use `impactlab` as an argument we see that we have several groupings below this. 

.. include:: ../examples/snippets/pythonapi_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-3-START
    :end-before: .. EXAMPLE-BLOCK-3-END

Let's explore `conflict` to see what kind of archives we have in there. 

.. include:: ../examples/snippets/pythonapi_finding_archives.py
	:start-after: .. EXAMPLE-BLOCK-4-START
	:end-before: .. EXAMPLE-BLOCK-4-END

OK. Just one. Now let's have a look at one is inside the `impactlab/conflict/global` namespace. 

.. include:: ../examples/snippets/pythonapi_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-5-START
    :end-before: .. EXAMPLE-BLOCK-5-END


 Using `filter`
 --------------

DataFS also lets you filter so you can limit the search space on archive names. With :py:meth:`datafs.DataAPI.filter` you can use the `prefix`, `path`, `str`, and `regex` pattern options to filter archives.
Let's look at using the prefix `project1_variable1_` which corresponds to the beginning of a set of archive names. Let's also see how many archives we have in total by filtering without arguments. We see there are 125. By filtering with our prefix we can significantly reduce the number of archives we are looking at. 

.. include:: ../examples/snippets/pythonapi_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-6-START
    :end-before: .. EXAMPLE-BLOCK-6-END

We can also filter on `path`. In this case we want to filter all NetCDF files that match a specific pattern. We need to set our `engine` value to `path` and put in our search pattern. 

.. include:: ../examples/snippets/pythonapi_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-7-START
    :end-before: .. EXAMPLE-BLOCK-7-END


We can also filter archives with archive names containing a specific string by setting `engine` to `str`. In this
example we want all archives with the string `variable2`. The filtering query returns 25 items. Let's look at the first few. 

.. include:: ../examples/snippets/pythonapi_finding_archives.py
    :start-after: .. EXAMPLE-BLOCK-8-START
    :end-before: .. EXAMPLE-BLOCK-8-END


Using `search`
--------------


DataFS `search` capabilites are enabled via tagging of archives. The arguments of the `search` method are tags associated with a given archive. Archives can be tagged. If archives are not tagged, they cannot be searched with the `search` method. 

