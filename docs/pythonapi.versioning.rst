.. _pythonapi-versioning:

=================
Tracking Versions
=================

One of the main features of DataFS is its ability to manage versions of archives. In the :ref:`pythonapi-metadata` section we worked with Archive level metadata. In this section we will work with versioning and demonstrate some of its metadata properties. 



We'll assume you have an api created and configured with a manager and authority. On :py:meth:`~datafs.DataAPI.create`, versioning is true by default. Should you want to turn it off just set ``versioned=False``.

View the source for the code samples on this page in :ref:`snippets-pythonapi-versioning`.

Setting a Version
-----------------

Let's write to a file that we'll upload to our ``sample_archive`` and see how DataFS manages versioning. Once
we've created our arhive we'll use :py:meth:`~datafs.core.data_archive.DataArchive.update` to start tracking versions. This time we'll set our version as  ``prerelease`` and set it to ``alpha``. ``beta`` is also an option. 

.. include:: ../examples/snippets/pythonapi_versioning.py
    :start-after: .. EXAMPLE-BLOCK-1-START
    :end-before: .. EXAMPLE-BLOCK-1-END


Getting Versions
-----------------

Now let's use :py:meth:`~datafs.core.data_archive.DataArchive.get_versions` to see which versions we are tracking

.. include:: ../examples/snippets/pythonapi_versioning.py
    :start-after: .. EXAMPLE-BLOCK-2-START
    :end-before: .. EXAMPLE-BLOCK-2-END


That's pretty cool. 


Bumping Versions
----------------

Now let's make some changes to our archive files. When we call :py:meth:`~datafs.core.data_archive.DataArchive.update` we'll specify ``bumpversion='minor'``. The ``bumpversion`` param takes values of ``major`` , ``minor`` or ``patch``.

.. include:: ../examples/snippets/pythonapi_versioning.py
    :start-after: .. EXAMPLE-BLOCK-3-START
    :end-before: .. EXAMPLE-BLOCK-3-END


Getting the latest version
--------------------------

What if I want to see what the latest version is? You can use the :py:meth:`~datafs.core.data_archive.DataArchive.get_latest_version`

.. include:: ../examples/snippets/pythonapi_versioning.py
    :start-after: .. EXAMPLE-BLOCK-4-START
    :end-before: .. EXAMPLE-BLOCK-4-END


Getting the latest hash
~~~~~~~~~~~~~~~~~~~~~~~

So we can see that it will return the latest version which in this case is the ``minor`` bump that we just did. How does it know about this? DataFS hashes the file contents of every version and creates a unique hash for every file. Each time an update is made to the file contents a hash is made and saved. You can access this value with :py:meth:`~datafs.core.data_archive.DataArchive.get_latest_hash`

.. include:: ../examples/snippets/pythonapi_versioning.py
    :start-after: .. EXAMPLE-BLOCK-5-START
    :end-before: .. EXAMPLE-BLOCK-5-END



Getting a specific version
--------------------------

Let's say we want to get an older version. We can do this by specifying ``version`` in :py:meth:`~datafs.core.data_api.DataAPI.get_archive`

.. include:: ../examples/snippets/pythonapi_versioning.py
    :start-after: .. EXAMPLE-BLOCK-6-START
    :end-before: .. EXAMPLE-BLOCK-6-END


We can see that this is our first version that saved as a prerelease alpha. 

To see more information on versioning check out :py:class:`~datafs.core.versions.BumpableVersion`. 


