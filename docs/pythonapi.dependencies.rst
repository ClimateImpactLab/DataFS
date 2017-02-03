.. _pythonapi-dependencies:

==========================
Managing Data Dependencies
==========================

Dependency graphs can be tracked explicitly in datafs, and each version can have its own dependencies.

You specify dependencies from within python or using the :ref:`command line interface <cli-dependencies>`.

.. note::

    Dependencies are not currently validated in any way, so entering a dependency that is not a valid archive name or version will not raise an error.

View the source for the code samples on this page in :ref:`snippets-pythonapi-dependencies`.


Specifying Dependencies
-----------------------

On write
~~~~~~~~

Dependencies can be set when using the ``dependencies`` argument to :py:class:`~datafs.core.data_archive.DataArchive`'s :py:meth:`~datafs.core.data_archive.DataArchive.update`, :py:meth:`~datafs.core.data_archive.DataArchive.open`, or :py:meth:`~datafs.core.data_archive.DataArchive.get_local_path` methods.

``dependencies`` must be a dictionary containing archive names as keys and version numbers as values. A value of ``None`` is also a valid dependency specification, where the version is treated as unpinned and is always interpreted as the dependency's latest version.

For example:

.. include:: ../examples/snippets/pythonapi_dependencies.py
    :start-after: .. EXAMPLE-BLOCK-1-START
    :end-before: .. EXAMPLE-BLOCK-1-END


After write
~~~~~~~~~~~

Dependencies can also be added to the latest version of an archive using the :py:meth:`~datafs.core.data_archive.DataArchive.set_dependencies` method:

.. include:: ../examples/snippets/pythonapi_dependencies.py
    :start-after: .. EXAMPLE-BLOCK-2-START
    :end-before: .. EXAMPLE-BLOCK-2-END


Using a requirements file
~~~~~~~~~~~~~~~~~~~~~~~~~

If a requirements file is present at api creation, all archives written with that api object will have the specified dependencies by default.

For example, with the following requirements file as ``requirements_data.txt``:

.. include:: ../examples/snippets/pythonapi_dependencies.py
    :start-after: .. EXAMPLE-BLOCK-3-START
    :end-before: .. EXAMPLE-BLOCK-3-END


Archives written while in this working directory will have these requirements:

.. include:: ../examples/snippets/pythonapi_dependencies.py
    :start-after: .. EXAMPLE-BLOCK-4-START
    :end-before: .. EXAMPLE-BLOCK-4-END

Using Dependencies
------------------

Retrieve dependencies with :py:class:`~datafs.core.data_archive.DataArchive`'s :py:meth:`~datafs.core.data_archive.DataArchive.get_dependencies` method:

.. include:: ../examples/snippets/pythonapi_dependencies.py
    :start-after: .. EXAMPLE-BLOCK-5-START
    :end-before: .. EXAMPLE-BLOCK-5-END


Get dependencies for older versions using the ``version`` argument:

.. include:: ../examples/snippets/pythonapi_dependencies.py
    :start-after: .. EXAMPLE-BLOCK-6-START
    :end-before: .. EXAMPLE-BLOCK-6-END

