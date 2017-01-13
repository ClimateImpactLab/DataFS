.. _pythonapi-versioning:

=================
Tracking Versions
=================

One of the main features of DataFS is its ability to manage versions of archives. In the :ref:`pythonapi-metadata` section we worked with Archive level metadata. In this section we will work with versioning and demonstrate some of its metadata properties. 



We'll assume you have an api created and configured with a manager and authority. On :py:meth:`~datafs.DataAPI.create`, versioning is true by default. Should you want to turn it off just set ``versioned=False``. 


Setting a Version
-----------------

Let's write to a file that we'll upload to our ``sample_archive`` and see how DataFS manages versioning. Once
we've created our arhive we'll use :py:meth:`~datafs.core.data_archive.DataArchive.update` to start tracking versions. This time we'll set our version as  ``prerelease`` and set it to ``alpha``. ``beta`` is also an option. 

.. code-block:: python

    >>> with open('sample_archive.txt', 'w+', ) as f:
    ...     f.write('this is a sample archive')
    >>>
    >>> sample_archive = api.create('sample_archive', metadata=dict(description='metadata description'))
    >>>
    >>> sample_archive.update('sample_archive.txt', prerelease='alpha')


Getting Versions
-----------------

Now let's use :py:meth:`~datafs.core.data_archive.DataArchive.get_versions` to see which versions we are tracking

.. code-block:: python

    >>> sample_archive.get_versions()
    >>> [BumpableVersion ('0.0.1a1')]


That's pretty cool. 


Bumping Versions
----------------

Now let's make some changes to our archive files. When we call :py:meth:`~datafs.core.data_archive.DataArchive.update` we'll specify ``bumpversion='minor'``. The ``bumpversion`` param takes values of ``major`` , ``minor`` or ``patch``.

.. code-block:: python

    >>> with open('sample_archive.txt', 'w+', ) as f:
    ...     f.write('Sample archive with more text so we can bumpversion')
    >>>
    >>> sample_archive.update('sample_archive.txt', bumpversion='minor')
    >>> sample_archive.get_versions()
    >>> [BumpableVersion ('0.0.1a1'), BumpableVersion ('0.1')]


Getting the latest version
--------------------------

What if I want to see what the latest version is? You can use the :py:meth:`~datafs.core.data_archive.DataArchive.get_latest_version`

.. code-block:: python
	
	>>> sample_archive.get_latest_version()
	>>> BumpableVersion ('0.1')



Getting the latest hash
~~~~~~~~~~~~~~~~~~~~~~~

So we can see that it will return the latest version which in this case is the ``minor`` bump that we just did. How does it know about this? DataFS hashes the file contents of every version and creates a unique hash for every file. Each time an update is made to the file contents a hash is made and saved. You can access this value with :py:meth:`~datafs.core.data_archive.DataArchive.get_latest_hash`

.. code-block:: python
	
	>>> sample_archive.get_latest_hash()
	>>> u'fe4509b806eb5a3480a10e1f1fe9cc62'



Getting a specific version
--------------------------

Let's say we want to get an older version. We can do this by specifying ``version`` in :py:meth:`~datafs.core.data_api.DataAPI.get_archive`


.. code-block:: python

	>>> sample_archive1 = = api.get_archive('sample_archive', default_version='0.0.1a1')
	>>> with sample_archive1.open('r') as f:
	... 	print(f.read())
	>>> this is a sample archive


We can see that this is our first version that saved as a prerelease alpha. 

To see more information on versioning check out :py:class:`~datafs.core.versions.BumpableVersion`. 








 
