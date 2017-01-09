.. _pythonapi-dependencies:

==========================
Managing Data Dependencies
==========================

Dependency graphs can be tracked explicitly in datafs, and each version can have its own dependencies.

You specify dependencies from within python or using the :ref:`command line interface <cli-dependencies>`.

.. note::

    Dependencies are not currently validated in any way, so entering a dependency that is not a valid archive name or version will not raise an error.


Specifying Dependencies
-----------------------

On write
~~~~~~~~

Dependencies can be set when using the ``dependencies`` argument to :py:class:`~datafs.core.data_archive.DataArchive`'s :py:meth:`~datafs.core.data_archive.DataArchive.update`, :py:meth:`~datafs.core.data_archive.DataArchive.open`, or :py:meth:`~datafs.core.data_archive.DataArchive.get_local_path` methods.

``dependencies`` must be a dictionary containing archive names as keys and version numbers as values. A value of ``None`` is also a valid dependency specification, where the version is treated as unpinned and is always interpreted as the dependency's latest version.

For example:

.. code-block:: python

    >>> my_archive = api.create('my_archive')
    >>> with my_archive.open('w+', 
    ...     dependencies={'archive2': '1.1', 'archive3': None}) as f:
    ...
    ...     f.write(u'contents depend on archive 2 v1.1')
    ...
    >>> archive.get_dependencies()
    {'archive2': '1.1', 'archive3': None}



After write
~~~~~~~~~~~

Dependencies can also be added to the latest version of an archive using the :py:meth:`~datafs.core.data_archive.DataArchive.set_dependencies` method:

.. code-block:: python

    >>> with my_archive.open('w+') as f:
    ...
    ...     f.write(u'contents depend on archive 2 v1.2')
    ...
    >>> my_archive.set_dependencies({'archive2': '1.2'})
    >>> my_archive.get_dependencies()
    {'archive2': '1.2'}


Using a requirements file
~~~~~~~~~~~~~~~~~~~~~~~~~

If a requirements file is present at api creation, all archives written with that api object will have the specified dependencies by default.

For example, with the following requirements file as ``requirements_data.txt``:

.. code-block:: text
    :linenos:

    dep1==1.0
    dep2==0.4.1a3

Archives written while in this working directory will have these requirements:

.. code-block:: python

    >>> api = datafs.get_api(
    ...     requirements_file='requirements_data.txt')
    >>>
    >>> archive = api.get_archive('my_archive')
    >>> with archive.open('w+') as f:
    ...     f.write(u'depends on dep1 and dep2')
    ...
    >>> archive.get_dependencies()
    {'dep1': '1.0', 'dep2': '0.4.1a3'}

Using Dependencies
------------------

Retrieve dependencies with :py:class:`~datafs.core.data_archive.DataArchive`'s :py:meth:`~datafs.core.data_archive.DataArchive.get_dependencies` method:

.. code-block:: python

    >>> archive.get_dependencies()
    {'dep1': '1.0', 'dep2': '0.4.1a3'}

Get dependencies for older versions using the ``version`` argument:

.. code-block:: python

    >>> archive.get_dependencies(version='0.0.1')
    {'archive2': '1.1', 'archive3': None}
