.. _pythonapi-creating-archives:

======================
Creating Data Archives
======================

Archives are the basic unit of a DataFS filesystem. They are essentially files, metadata, history, versions, and dependencies wrapped into a single object.

You can create archives from within python or using the :ref:`command line interface <cli-creating-archives>`.

View the source for the code samples on this page in :ref:`snippets-pythonapi-creating-archives`.


Naming Archives
---------------

Archives can be named anything, as long as the data service you use can handle the name. If create an archive with a name illegal for the corresponding data service, you will receive an error on write (rather than on archive creation). Since this is an error specific to the storate service, we do not catch this error on creation.

Create an archive using the :py:meth:`datafs.DataAPI.create` command.

.. include:: ../examples/snippets/pythonapi_creating_archives.py
    :start-after: .. EXAMPLE-BLOCK-1-START
    :end-before: .. EXAMPLE-BLOCK-1-END


Specifying an Authority
-----------------------

If you have more than one authority, you will need to specify an authority on archive creation:

.. include:: ../examples/snippets/pythonapi_creating_archives.py
    :start-after: .. EXAMPLE-BLOCK-2-START
    :end-before: .. EXAMPLE-BLOCK-2-END

This can be done using the ``authority_name`` argument:

.. include:: ../examples/snippets/pythonapi_creating_archives.py
    :start-after: .. EXAMPLE-BLOCK-3-START
    :end-before: .. EXAMPLE-BLOCK-3-END

Alternatively, you can set the :py:attr:`~datafs.core.data_api.DataAPI.DefaultAuthorityName` attribute:

.. include:: ../examples/snippets/pythonapi_creating_archives.py
    :start-after: .. EXAMPLE-BLOCK-4-START
    :end-before: .. EXAMPLE-BLOCK-4-END


Adding Metadata
---------------

Arbitrary metadata can be added using the ``metadata`` dictionary argument:

.. include:: ../examples/snippets/pythonapi_creating_archives.py
    :start-after: .. EXAMPLE-BLOCK-5-START
    :end-before: .. EXAMPLE-BLOCK-5-END


Required Metadata
~~~~~~~~~~~~~~~~~

Administrators can set up metadata requirements using the manager's :ref:`admin` tools. If these required fields are not provided, an error will be raised on archive creation.

For example, when connected to a manager requiring the `'description'` field:

.. include:: ../examples/snippets/pythonapi_creating_archives.py
    :start-after: .. EXAMPLE-BLOCK-6-START
    :end-before: .. EXAMPLE-BLOCK-6-END

Trying again with a "description" field will work as expected.

Using the Helper
~~~~~~~~~~~~~~~~

Instead of providing all fields in the ``create`` call, you can optionally use the ``helper`` argument. Setting ``helper=True`` will start an interactive prompt, requesting each required item of metadata:

.. include:: ../examples/snippets/pythonapi_creating_archives.py
    :start-after: .. EXAMPLE-BLOCK-7-START
    :end-before: .. EXAMPLE-BLOCK-7-END


