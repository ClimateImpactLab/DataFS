.. _cli-creating-archives:

======================
Creating Data Archives
======================

Archives are the basic unit of a DataFS filesystem. They are essentially files, metadata, history, versions, and dependencies wrapped into a single object.

You can create archives from the command line interface or from :ref:`python <pythonapi-creating-archives>`.

Create an archive using the ``create`` command:

.. include:: ../../../tests/cli_snippets/test_cli_creating_archives.py
    :start-after: .. EXAMPLE-BLOCK-1-START
    :end-before: .. EXAMPLE-BLOCK-1-END

Naming Archives
---------------

Archives can be named anything, as long as the data service you use can handle the name.

For example, Amazon's S3 storage cannot handle underscores in object names. If you create an archive with underscores in the name, you will receive an error on write (rather than on archive creation). Since this is an error specific to the storage service, we do not catch this error on creation.


Specifying an Authority
-----------------------

If you have more than one authority, you will need to specify an authority on archive creation:

.. include:: ../../../tests/cli_snippets/test_cli_creating_archives.py
    :start-after: .. EXAMPLE-BLOCK-2-START
    :end-before: .. EXAMPLE-BLOCK-2-END

Adding Metadata
---------------

Arbitrary metadata can be added as keyword arguments:

.. include:: ../../../tests/cli_snippets/test_cli_creating_archives.py
    :start-after: .. EXAMPLE-BLOCK-3-START
    :end-before: .. EXAMPLE-BLOCK-3-END

Required Metadata
~~~~~~~~~~~~~~~~~

Administrators can set up metadata requirements using the manager's :ref:`admin` tools. If these required fields are not provided, an error will be raised on archive creation.

For example, when connected to a manager requiring the `'description'` field:

.. include:: ../../../tests/cli_snippets/test_cli_creating_archives.py
    :start-after: .. EXAMPLE-BLOCK-4-START
    :end-before: .. EXAMPLE-BLOCK-4-END

Trying again with a ``--description "[desc]"`` argument will work as expected.


Using the Helper
~~~~~~~~~~~~~~~~

Instead of providing all fields in the ``create`` call, you can optionally use the ``helper`` flag. Using the flag ``--helper`` will start an interactive prompt, requesting each required item of metadata:

.. include:: ../../../tests/cli_snippets/test_cli_creating_archives.py
    :start-after: .. EXAMPLE-BLOCK-5-START
    :end-before: .. EXAMPLE-BLOCK-5-END



